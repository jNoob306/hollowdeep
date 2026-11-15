#!/usr/bin/env python3
"""Download the CC0 textures listed in docs/ASSETS.md into assets/.

Sources: Poly Haven (api.polyhaven.com) and ambientCG (ambientcg.com). Both are
CC0 and need no key. Each texture is saved at 1K as
assets/tex_<name>_color.jpg, _normal.jpg (OpenGL convention) and _rough.jpg,
and logged in assets/CREDITS.md.

Usage:
  python3 tools/fetch_textures.py                 # fetch everything missing
  python3 tools/fetch_textures.py rock moss       # only these
  python3 tools/fetch_textures.py --force         # re-download
  python3 tools/fetch_textures.py rock=ph:rock_06 # override a pick

Change a pick by editing PICKS below or with name=source:id on the command line.
"""
import hashlib, io, os, shutil, subprocess, sys, zipfile
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'assets')
UA = {'User-Agent': 'asset-fetch-script/1.0'}
JPEG_Q = '4'  # ffmpeg -q:v, 2 (best) to 31; 4 is visually clean and about a third of the size

# name -> (source, asset id).  ph = Poly Haven, acg = ambientCG.
PICKS = {
    'rock':    ('ph', 'rock_face_03'),
    'floor':   ('ph', 'rocks_ground_02'),
    'wetrock': ('ph', 'dry_riverbed_rock'),
    'crystal': ('acg', 'Ice003'),
    'wood':    ('ph', 'weathered_brown_planks'),
    'rust':    ('ph', 'rusty_metal_02'),
    'moss':    ('ph', 'mossy_rock'),
}
MAPS = ('color', 'normal', 'rough')


def get(url):
    r = requests.get(url, headers=UA, timeout=120)
    r.raise_for_status()
    return r


def from_polyhaven(asset):
    files = get(f'https://api.polyhaven.com/files/{asset}').json()
    out = {}
    for ours, theirs in (('color', 'Diffuse'), ('normal', 'nor_gl'), ('rough', 'Rough')):
        f = files[theirs]['1k']['jpg']
        data = get(f['url']).content
        if hashlib.md5(data).hexdigest() != f['md5']:
            raise RuntimeError(f'{asset} {theirs}: checksum mismatch')
        out[ours] = data
    return out, f'https://polyhaven.com/a/{asset}', 'Poly Haven'


def from_ambientcg(asset):
    z = zipfile.ZipFile(io.BytesIO(get(f'https://ambientcg.com/get?file={asset}_1K-JPG.zip').content))
    out = {}
    for ours, suffix in (('color', '_Color.jpg'), ('normal', '_NormalGL.jpg'), ('rough', '_Roughness.jpg')):
        name = next(n for n in z.namelist() if n.endswith(suffix))
        out[ours] = z.read(name)
    return out, f'https://ambientcg.com/a/{asset}', 'ambientCG'


def save_jpeg(data, path):
    """Write the JPEG, re-encoded smaller when ffmpeg is available."""
    tmp = path + '.src.jpg'
    with open(tmp, 'wb') as f:
        f.write(data)
    if shutil.which('ffmpeg'):
        r = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-vf', 'scale=1024:1024',
                            '-q:v', JPEG_Q, path])
        if r.returncode == 0:
            os.remove(tmp)
            return
    os.replace(tmp, path)


def update_credits(rows):
    """Rewrite the Textures section of assets/CREDITS.md, keeping other sections."""
    path = os.path.join(ASSETS, 'CREDITS.md')
    text = open(path).read() if os.path.exists(path) else '# Asset credits\n\nEvery file here is CC0 (public domain) or generated for this project.\n'
    head, _, rest = text.partition('\n## Textures\n')
    tail = ''
    if '\n## ' in rest:
        tail = '\n## ' + rest.split('\n## ', 1)[1]
    old = {}
    for line in rest.split('\n## ', 1)[0].splitlines():
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) == 4 and cells[0].startswith('`tex_'):
            old[cells[0]] = cells
    for name, (site, url) in rows.items():
        key = f'`tex_{name}_*.jpg`'
        old[key] = [key, site, url, 'CC0']
    body = '\n## Textures\n\n| Files | Source | Page | License |\n| --- | --- | --- | --- |\n'
    body += ''.join('| ' + ' | '.join(old[k]) + ' |\n' for k in sorted(old))
    with open(path, 'w') as f:
        f.write(head.rstrip('\n') + '\n' + body + tail)


def main(argv):
    force = '--force' in argv
    picks = dict(PICKS)
    names = []
    for a in argv:
        if a.startswith('--'):
            continue
        if '=' in a:
            name, spec = a.split('=', 1)
            picks[name] = tuple(spec.split(':', 1))
            a = name
        if a not in picks:
            sys.exit(f'unknown texture "{a}". Known: {", ".join(picks)}')
        names.append(a)
    os.makedirs(ASSETS, exist_ok=True)
    rows, failed = {}, []
    for name in names or list(picks):
        source, asset = picks[name]
        paths = {m: os.path.join(ASSETS, f'tex_{name}_{m}.jpg') for m in MAPS}
        if not force and all(os.path.exists(p) for p in paths.values()) and name not in names:
            print(f'{name}: already present, skipping')
            continue
        try:
            maps, url, site = (from_polyhaven if source == 'ph' else from_ambientcg)(asset)
        except Exception as e:  # keep going so one bad pick doesn't block the rest
            print(f'{name}: FAILED ({asset}): {e}')
            failed.append(name)
            continue
        for m, data in maps.items():
            save_jpeg(data, paths[m])
        rows[name] = (site, url)
        print(f'{name}: {asset} from {site}, ' + ', '.join(f'{os.path.getsize(p) // 1024} KB' for p in paths.values()))
    if rows:
        update_credits(rows)
    if failed:
        sys.exit(f'failed: {", ".join(failed)}')


if __name__ == '__main__':
    main(sys.argv[1:])
