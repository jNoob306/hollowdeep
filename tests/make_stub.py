"""Build a test copy of the game with Three.js replaced by a no-op stub.

Lets the game logic run in headless Chrome without a GPU or network.
Output: tests/build/index.html + tests/build/three-stub.mjs
Usage: python3 tests/make_stub.py
"""
import os, re
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, '..', 'index.html')).read()
js = src.split('<script type="module">')[1].split('</script>')[0]
names = sorted(set(re.findall(r'THREE\.(\w+)', js)))
stub = '''const H={get(t,k){if(k===Symbol.toPrimitive)return()=>0;if(k==='then'||k===Symbol.iterator)return undefined;if(k==='length')return 0;return mk();},apply(){return mk();},construct(){return mk();},set(){return true;}};
function mk(){return new Proxy(function(){},H);}
'''
for n in names:
    stub += ('export const MathUtils={degToRad:d=>d*Math.PI/180};\n' if n == 'MathUtils' else f'export const {n}=mk();\n')
out = os.path.join(here, 'build'); os.makedirs(out, exist_ok=True)
open(os.path.join(out, 'three-stub.mjs'), 'w').write(stub)
html = re.sub(r'https://cdn\.jsdelivr\.net/npm/three@[^"]+/build/three\.module\.js', './three-stub.mjs', src)
# The add-ons (model loader, skinned clone) are stubbed too. The stub loader always fails,
# so the tests run on the primitive fallback models.
html = re.sub(r'https://cdn\.jsdelivr\.net/npm/three@[^"]+/examples/jsm/', './addons/', html)
for rel, code in (('loaders/GLTFLoader.js', 'export class GLTFLoader{load(u,ok,prog,err){if(err)setTimeout(()=>err(new Error("stub")),0);}}\n'),
                  ('utils/SkeletonUtils.js', 'export function clone(o){return o;}\n')):
    path = os.path.join(out, 'addons', rel); os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w').write(code)
open(os.path.join(out, 'index.html'), 'w').write(html)
open(os.path.join(out, 'game.mjs'), 'w').write(js)
print('stub build ready:', out)
