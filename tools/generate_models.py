#!/usr/bin/env python3
"""Generate concept images (and later 3D models) for the assets in docs/ASSETS.md.

Uses free Hugging Face ZeroGPU Spaces through gradio_client. It never calls the
paid "Inference Providers" API, so it cannot run up a bill: when the free GPU
quota is used up the Space refuses the request and this script stops.

  python3 tools/generate_models.py list
  python3 tools/generate_models.py image player            # one image, seed 1
  python3 tools/generate_models.py image player --seed 7   # try another
  python3 tools/generate_models.py image player --back     # back view
  python3 tools/generate_models.py image enemy_hermit --tag witch --subject "Gaunt spore witch, ..."
                                                           # try another design: replaces the description,
                                                           # keeps the pose wording, saves as <name>_<tag>_s<seed>.png
  python3 tools/generate_models.py model player 5          # approved image (seed 5) -> 3D

Images are saved to art/src/<name>[_back]_s<seed>.png. Nothing is turned into
3D until the image has been approved, because that step costs far more quota.
"model" makes exactly one model per command and saves the raw, unrigged mesh to
art/raw/<name>.glb (about 100,000 triangles; Blender reduces and rigs it later).

Optional: HF_TOKEN in the environment or .env makes the Space count usage
against your own account's quota instead of the small anonymous one.
"""
import os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'art', 'src')
FLUX_SPACE = 'black-forest-labs/FLUX.1-schnell'
TRELLIS_SPACE = 'microsoft/TRELLIS.2'
RAW = os.path.join(ROOT, 'art', 'raw')
MAX_PER_RUN = 4  # hard cap on generations in one command

# file name -> heading in docs/ASSETS.md whose ```text block is the prompt
CHARACTERS = {
    'player': 'Main character: The Delver',
    'enemy_feral': 'Feral Delver',
    'enemy_miner': 'Hollow Miner',
    'enemy_hermit': 'Spore Hermit',
    'enemy_jailer': 'Chain Jailer',
    'enemy_stalker': 'Pale Stalker',
    'stalker_bellman': 'The Bellman, the stalker',
    'boss_warden': 'The Crystal Warden',
    'boss_lantern': 'The Lantern Mother',
    'boss_ossuary': 'The Ossuary King',
}


def prompt_for(name):
    doc = open(os.path.join(ROOT, 'docs', 'ASSETS.md'), encoding='utf-8').read()
    h = re.search(r'^#+ ' + re.escape(CHARACTERS[name]) + r'[^\n]*\n', doc, re.M)
    section = re.split(r'^#+ ', doc[h.end():], maxsplit=1, flags=re.M)[0] if h else ''
    m = re.search(r'```text\n(.*?)\n```', section, re.S)
    if not m:
        sys.exit(f'No prompt found in docs/ASSETS.md under "{CHARACTERS[name]}"')
    return m.group(1).strip()


def hf_token():
    tok = os.environ.get('HF_TOKEN', '')
    path = os.path.join(ROOT, '.env')
    if not tok and os.path.exists(path):
        for line in open(path, encoding='utf-8'):
            m = re.match(r'\s*HF_TOKEN\s*=\s*(.*)', line)
            if m:
                tok = m.group(1).strip().strip('"\'')
    return tok or None


def cmd_image(args):
    seeds = [int(args[i + 1]) for i, a in enumerate(args) if a == '--seed']
    back = '--back' in args
    subject = next((args[i + 1] for i, a in enumerate(args) if a == '--subject'), None)
    tag = next((args[i + 1] for i, a in enumerate(args) if a == '--tag'), '')
    names = [a for i, a in enumerate(args)
             if not a.startswith('--') and (i == 0 or args[i - 1] not in ('--seed', '--subject', '--tag'))]
    bad = [n for n in names if n not in CHARACTERS]
    if bad or not names:
        sys.exit(f'Give one or more of: {", ".join(CHARACTERS)}')
    jobs = [(n, s) for n in names for s in (seeds or [1])]
    if len(jobs) > MAX_PER_RUN:
        sys.exit(f'{len(jobs)} images asked for; the cap is {MAX_PER_RUN} per run to protect the GPU quota.')
    from gradio_client import Client
    tok = hf_token()
    client = Client(FLUX_SPACE, verbose=False, **({'hf_token': tok} if tok else {}))
    os.makedirs(OUT, exist_ok=True)
    for name, seed in jobs:
        prompt = prompt_for(name)
        if subject:  # try a different design while keeping the standard pose wording
            prompt = subject.rstrip('. ') + '. ' + prompt[prompt.index('Full body, front view'):]
        if back:
            prompt = prompt.replace('front view', 'back view, seen from behind')
        dst = os.path.join(OUT, f'{name}{"_" + tag if tag else ""}{"_back" if back else ""}_s{seed}.png')
        try:
            result, _ = client.predict(prompt=prompt, seed=seed, randomize_seed=False, width=1024, height=1024,
                                       num_inference_steps=4, api_name='/infer')
        except Exception as e:  # quota or queue errors: stop, never retry in a loop
            sys.exit(f'{name}: the Space refused or failed, stopping here.\n  {e}')
        src = result['path'] if isinstance(result, dict) else result
        shutil.copy(src, dst)
        print(f'{name}: saved {os.path.relpath(dst, ROOT)}')


def cmd_model(args):
    if len(args) != 2 or args[0] not in CHARACTERS or not args[1].isdigit():
        sys.exit('Usage: python3 tools/generate_models.py model <name> <seed of the approved image>')
    name, seed = args
    src = os.path.join(OUT, f'{name}_s{seed}.png')
    if not os.path.exists(src):
        sys.exit(f'No image at {os.path.relpath(src, ROOT)}')
    from gradio_client import Client, handle_file
    tok = hf_token()
    client = Client(TRELLIS_SPACE, verbose=False, **({'hf_token': tok} if tok else {}))
    try:  # one pass, no retries: any refusal (quota, queue) stops here
        client.predict(api_name='/start_session')
        cut = client.predict(input=handle_file(src), api_name='/preprocess_image')
        cut = cut['path'] if isinstance(cut, dict) else cut
        client.predict(image=handle_file(cut), seed=0, resolution='1024', api_name='/image_to_3d')
        glb = client.predict(decimation_target=100000, texture_size=1024, api_name='/extract_glb')[0]
    except Exception as e:
        sys.exit(f'{name}: the Space refused or failed, stopping here.\n  {e}')
    os.makedirs(RAW, exist_ok=True)
    dst = os.path.join(RAW, f'{name}.glb')
    shutil.copy(glb, dst)
    shutil.copy(cut, os.path.join(RAW, f'{name}_cutout.png'))
    print(f'{name}: saved {os.path.relpath(dst, ROOT)} ({os.path.getsize(dst) // 1024} KB)')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'list':
        print('\n'.join(CHARACTERS))
    elif len(sys.argv) > 1 and sys.argv[1] == 'image':
        cmd_image(sys.argv[2:])
    elif len(sys.argv) > 1 and sys.argv[1] == 'model':
        cmd_model(sys.argv[2:])
    else:
        sys.exit(__doc__)
