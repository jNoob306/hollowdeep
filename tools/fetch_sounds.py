#!/usr/bin/env python3
"""Find, audition and convert the CC0 sounds listed in docs/ASSETS.md.

Source: Freesound (freesound.org), CC0 licence only. Needs FREESOUND_KEY in a
.env file in the project folder, and ffmpeg on the PATH. Uses only the Python
standard library, so there is nothing to pip install.

Three steps:

  python tools/fetch_sounds.py shortlist
      Searches Freesound for each sound, downloads the top candidates as
      previews and writes tools/_audition/index.html. Open that page in a
      browser and listen.

  python tools/fetch_sounds.py pick sfx_bell_toll 432731
      Chooses a candidate by its Freesound id (shown on the audition page).
      Without a pick, the first candidate is used.

  python tools/fetch_sounds.py build
      Converts each chosen sound to mono OGG in assets/ (trimmed, faded,
      normalised) and records it in assets/CREDITS.md.

Add sound names after the command to limit it, e.g. "shortlist sfx_bell_toll".
"""
import html, json, os, re, shutil, subprocess, sys, time
import urllib.error, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'assets')
AUDITION = os.path.join(ROOT, 'tools', '_audition')
PICKS = os.path.join(ROOT, 'tools', 'sound_picks.json')
API = 'https://freesound.org/apiv2/search/text/'
UA = {'User-Agent': 'asset-fetch-script/1.0'}
CANDIDATES = 6

# name: (search words, shortest s, longest s of the source, length kept s, loop?, used for)
SOUNDS = {
    'sfx_bell_toll':   ('church bell toll single low',      2,   30, 8,   False, 'The Bellman, level start'),
    'sfx_bell_step':   ('bell clank metal dull single',     0.2, 4,  1.5, False, 'The Bellman, each step'),
    'sfx_bell_shake':  ('bell rattle shake fast',           0.5, 8,  2.5, False, 'The Bellman, grab wind-up'),
    'sfx_chain_drag':  ('heavy chain drag metal',           1,   15, 4,   False, 'The Bellman, moving'),
    'amb_drips':       ('cave water drips',                 8,   90, 20,  True,  'Cave ambience'),
    'amb_rumble':      ('distant low rumble earth',         3,   40, 9,   False, 'Cave ambience'),
    'amb_wind':        ('wind howling tunnel',              8,   90, 20,  True,  'Near exit shafts'),
    'amb_drone':       ('dark drone low ambient',           10,  120, 30, True,  'Music bed'),
    'amb_torch':       ('torch fire crackle',               6,   90, 15,  True,  "Player's torch"),
    'sfx_step_stone':  ('footstep stone single',            0.1, 2,  0.6, False, 'Player'),
    'sfx_step_gravel': ('footstep gravel single',           0.1, 2,  0.6, False, 'Player'),
    'sfx_mine':        ('pickaxe hit rock',                 0.2, 4,  1.2, False, 'Mining'),
    'sfx_swing':       ('sword swing whoosh',               0.1, 2,  0.7, False, 'Combat'),
    'sfx_hit':         ('sword hit flesh impact',           0.1, 3,  0.8, False, 'Combat'),
    'sfx_clang':       ('metal shield clang',               0.2, 4,  1.2, False, 'Blocking'),
    'sfx_groan':       ('zombie groan',                     0.5, 8,  3,   False, 'Feral Delver, Hollow Miner'),
    'sfx_screech':     ('monster screech wet',              0.5, 8,  3,   False, 'Spore Hermit, Pale Stalker'),
}


def load_key():
    key = os.environ.get('FREESOUND_KEY', '')
    path = os.path.join(ROOT, '.env')
    if not key and os.path.exists(path):
        for line in open(path, encoding='utf-8'):
            m = re.match(r'\s*FREESOUND_KEY\s*=\s*(.*)', line)
            if m:
                key = m.group(1).strip().strip('"\'')
    if not key:
        sys.exit('No Freesound key. Copy .env.example to .env and put your key after FREESOUND_KEY=')
    return key


def fetch(url, tries=3):
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                sys.exit(f'Freesound refused the request ({e.code}). Check FREESOUND_KEY in .env.')
            if e.code == 429:
                sys.exit('Freesound says too many requests. Wait a while and run the same command again.')
            if attempt == tries - 1:
                raise
        except urllib.error.URLError:
            if attempt == tries - 1:
                raise
        time.sleep(2 * (attempt + 1))


def search(key, words, shortest, longest):
    q = urllib.parse.urlencode({
        'query': words,
        'filter': f'license:"Creative Commons 0" duration:[{shortest} TO {longest}]',
        'fields': 'id,name,username,license,duration,previews,url,avg_rating,num_downloads',
        'sort': 'score', 'page_size': 30, 'token': key,
    })
    results = json.loads(fetch(f'{API}?{q}'))['results']
    # Belt and braces: keep CC0 only, whatever the filter returned.
    results = [r for r in results if 'publicdomain/zero' in r.get('license', '')]
    # Favour well-rated, well-used sounds among the relevant ones.
    results.sort(key=lambda r: (r.get('avg_rating') or 0) * 2 + min(r.get('num_downloads') or 0, 2000) / 500,
                 reverse=True)
    return results[:CANDIDATES]


def read_json(path, default):
    return json.load(open(path, encoding='utf-8')) if os.path.exists(path) else default


def names_from(args):
    bad = [a for a in args if a not in SOUNDS]
    if bad:
        sys.exit(f'Unknown sound: {", ".join(bad)}. Known: {", ".join(SOUNDS)}')
    return args or list(SOUNDS)


def cmd_shortlist(args):
    key = load_key()
    os.makedirs(AUDITION, exist_ok=True)
    index_path = os.path.join(AUDITION, 'candidates.json')
    index = read_json(index_path, {})
    for name in names_from(args):
        words, shortest, longest = SOUNDS[name][:3]
        found = search(key, words, shortest, longest)
        folder = os.path.join(AUDITION, name)
        shutil.rmtree(folder, ignore_errors=True)
        os.makedirs(folder)
        index[name] = []
        for r in found:
            with open(os.path.join(folder, f'{r["id"]}.mp3'), 'wb') as f:
                f.write(fetch(r['previews']['preview-hq-mp3']))
            index[name].append({k: r[k] for k in ('id', 'name', 'username', 'duration', 'url')})
        print(f'{name}: {len(found)} candidates' + ('' if found else '  <-- none found, try other search words'))
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=1)
    write_audition_page(index)
    print(f'\nOpen this file in your browser to listen:\n  {os.path.join(AUDITION, "index.html")}')


def write_audition_page(index):
    picks = read_json(PICKS, {})
    e = html.escape
    out = ['<!doctype html><meta charset="utf-8"><title>Sound audition</title>',
           '<style>body{font:15px system-ui;max-width:900px;margin:2em auto;padding:0 1em;background:#16130f;color:#e6dcc8}'
           'h2{margin-top:2em;border-bottom:1px solid #554}small{color:#a99}.c{margin:.6em 0;padding:.5em;background:#221d17}'
           '.p{outline:2px solid #c90}code{background:#000;padding:.15em .4em;user-select:all}a{color:#dc9}audio{width:100%}</style>',
           '<h1>Sound audition</h1><p>Listen, then copy the command under the one you like and run it in the project folder. '
           'The highlighted one is the current choice. When you are done, run <code>python tools/fetch_sounds.py build</code>.</p>']
    for name in SOUNDS:
        if name not in index:
            continue
        out.append(f'<h2>{e(name)}.ogg <small>{e(SOUNDS[name][5])}</small></h2>')
        chosen = picks.get(name, index[name][0]['id'] if index[name] else None)
        for c in index[name]:
            out.append(f'<div class="c{" p" if c["id"] == chosen else ""}"><b>{e(c["name"])}</b> '
                       f'<small>{c["duration"]:.1f} s, by {e(c["username"])}, <a href="{e(c["url"])}">page</a></small>'
                       f'<audio controls preload="none" src="{e(name)}/{c["id"]}.mp3"></audio>'
                       f'<code>python tools/fetch_sounds.py pick {e(name)} {c["id"]}</code></div>')
    with open(os.path.join(AUDITION, 'index.html'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))


def cmd_pick(args):
    if len(args) != 2 or args[0] not in SOUNDS or not args[1].isdigit():
        sys.exit('Usage: python tools/fetch_sounds.py pick <sound name> <freesound id>')
    name, sid = args[0], int(args[1])
    index = read_json(os.path.join(AUDITION, 'candidates.json'), {})
    if sid not in [c['id'] for c in index.get(name, [])]:
        sys.exit(f'{sid} is not one of the shortlisted candidates for {name}.')
    picks = read_json(PICKS, {})
    picks[name] = sid
    with open(PICKS, 'w', encoding='utf-8') as f:
        json.dump(picks, f, indent=1, sort_keys=True)
    write_audition_page(index)
    print(f'{name}: picked {sid}')


def peak_db(path, filters):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', filters + ',volumedetect',
                        '-f', 'null', '-'], capture_output=True, text=True)
    m = re.search(r'max_volume:\s*(-?[\d.]+) dB', r.stderr)
    return float(m.group(1)) if m else 0.0


def convert(src, dst, keep, loop):
    """Trim leading silence, cut to length, fade the ends, bring the peak to -1.5 dB, save mono OGG."""
    fade_out = 0.03 if loop else min(0.25, keep / 4)
    trim = f'silenceremove=start_periods=1:start_threshold=-50dB,atrim=0:{keep},asetpts=N/SR/TB'
    gain = max(-20.0, min(20.0, -1.5 - peak_db(src, trim)))
    chain = (f'{trim},volume={gain:.1f}dB,afade=t=in:d=0.01,'
             f'areverse,afade=t=in:d={fade_out},areverse')
    r = subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', src, '-af', chain,
                        '-ac', '1', '-ar', '44100', '-c:a', 'libvorbis', '-q:a', '4', dst])
    if r.returncode != 0:
        sys.exit(f'ffmpeg failed on {src}')


def update_credits(rows):
    """Rewrite the Sounds section of assets/CREDITS.md, keeping other sections."""
    path = os.path.join(ASSETS, 'CREDITS.md')
    text = open(path, encoding='utf-8').read() if os.path.exists(path) else \
        '# Asset credits\n\nEvery file here is CC0 (public domain) or generated for this project.\n'
    head, _, rest = text.partition('\n## Sounds\n')
    tail = '\n## ' + rest.split('\n## ', 1)[1] if '\n## ' in rest else ''
    old = {}
    for line in rest.split('\n## ', 1)[0].splitlines():
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) == 5 and cells[0].startswith('`'):
            old[cells[0]] = cells
    old.update(rows)
    body = '\n## Sounds\n\n| File | Original name | Author | Page | License |\n| --- | --- | --- | --- | --- |\n'
    body += ''.join('| ' + ' | '.join(old[k]) + ' |\n' for k in sorted(old))
    with open(path, 'w', encoding='utf-8') as f:
        f.write(head.rstrip('\n') + '\n' + body + tail)


def cmd_build(args):
    if not shutil.which('ffmpeg'):
        sys.exit('ffmpeg was not found. Install it, open a new terminal window and try again.')
    index = read_json(os.path.join(AUDITION, 'candidates.json'), {})
    picks = read_json(PICKS, {})
    os.makedirs(ASSETS, exist_ok=True)
    rows, missing = {}, []
    for name in names_from(args):
        cands = index.get(name, [])
        if not cands:
            missing.append(name)
            continue
        c = next((x for x in cands if x['id'] == picks.get(name)), cands[0])
        dst = os.path.join(ASSETS, f'{name}.ogg')
        convert(os.path.join(AUDITION, name, f'{c["id"]}.mp3'), dst, SOUNDS[name][3], SOUNDS[name][4])
        clean = lambda s: str(s).replace('|', '/')
        rows[f'`{name}.ogg`'] = [f'`{name}.ogg`', clean(c['name']), clean(c['username']), c['url'], 'CC0']
        print(f'{name}.ogg: {os.path.getsize(dst) // 1024} KB from "{c["name"]}"')
    if rows:
        update_credits(rows)
    if missing:
        print(f'\nNo candidates yet for: {", ".join(missing)}. Run "shortlist" for them first.')


if __name__ == '__main__':
    cmds = {'shortlist': cmd_shortlist, 'pick': cmd_pick, 'build': cmd_build}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        sys.exit(__doc__)
    cmds[sys.argv[1]](sys.argv[2:])
