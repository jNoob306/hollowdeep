#!/usr/bin/env python3
"""Generate concept images (and later 3D models) for the assets in docs/ASSETS.md.

Uses free Hugging Face ZeroGPU Spaces through gradio_client. It never calls the
paid "Inference Providers" API, so it cannot run up a bill: when the free GPU
quota is used up the Space refuses the request and this script stops.

  python3 tools/generate_models.py list
  python3 tools/generate_models.py image player            # one image, seed 1
  python3 tools/generate_models.py image player --seed 7   # try another
  python3 tools/generate_models.py image player --back     # back view

Images are saved to art/src/<name>[_back]_s<seed>.png. Nothing is turned into
3D until the image has been approved, because that step costs far more quota.

Optional: HF_TOKEN in the environment or .env makes the Space count usage
against your own account's quota instead of the small anonymous one.
"""
import os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'art', 'src')
FLUX_SPACE = 'black-forest-labs/FLUX.1-schnell'
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
    names = [a for i, a in enumerate(args) if not a.startswith('--') and (i == 0 or args[i - 1] != '--seed')]
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
        if back:
            prompt = prompt.replace('front view', 'back view, seen from behind')
        dst = os.path.join(OUT, f'{name}{"_back" if back else ""}_s{seed}.png')
        try:
            result, _ = client.predict(prompt=prompt, seed=seed, randomize_seed=False, width=1024, height=1024,
                                       num_inference_steps=4, api_name='/infer')
        except Exception as e:  # quota or queue errors: stop, never retry in a loop
            sys.exit(f'{name}: the Space refused or failed, stopping here.\n  {e}')
        src = result['path'] if isinstance(result, dict) else result
        shutil.copy(src, dst)
        print(f'{name}: saved {os.path.relpath(dst, ROOT)}')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'list':
        print('\n'.join(CHARACTERS))
    elif len(sys.argv) > 1 and sys.argv[1] == 'image':
        cmd_image(sys.argv[2:])
    else:
        sys.exit(__doc__)
