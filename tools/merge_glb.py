"""Merge the clips of an animation-only GLB into a skinned character GLB with the same bone names."""
import json, struct, sys
def read(p):
    b=open(p,'rb').read(); n=struct.unpack('<I',b[12:16])[0]; j=json.loads(b[20:20+n]); o=20+n
    m=struct.unpack('<I',b[o:o+4])[0]; return j, b[o+8:o+8+m]
def write(p,j,bin_):
    js=json.dumps(j,separators=(',',':')).encode(); js+=b' '*(-len(js)%4); bin_+=b'\0'*(-len(bin_)%4)
    open(p,'wb').write(b'glTF'+struct.pack('<II',2,12+8+len(js)+8+len(bin_))+struct.pack('<I',len(js))+b'JSON'+js+struct.pack('<I',len(bin_))+b'BIN\0'+bin_)
cj,cb=read(sys.argv[1]); aj,ab=read(sys.argv[2])
cb+=b'\0'*(-len(cb)%4); off=len(cb); bv0=len(cj['bufferViews']); ac0=len(cj['accessors'])
for v in aj['bufferViews']:
    v=dict(v); v['byteOffset']=v.get('byteOffset',0)+off; v['buffer']=0; cj['bufferViews'].append(v)
for a in aj['accessors']:
    a=dict(a); a['bufferView']+=bv0; cj['accessors'].append(a)
name2idx={n.get('name'):i for i,n in enumerate(cj['nodes'])}
cj['animations']=[]; missing=set()
for an in aj['animations']:
    ch=[]
    for c in an['channels']:
        nm=aj['nodes'][c['target']['node']].get('name')
        if nm not in name2idx: missing.add(nm); continue
        ch.append({'sampler':c['sampler'],'target':{'node':name2idx[nm],'path':c['target']['path']}})
    cj['animations'].append({'name':an['name'],'channels':ch,'samplers':[{**s,'input':s['input']+ac0,'output':s['output']+ac0} for s in an['samplers']]})
bin_=cb+ab; cj['buffers'][0]['byteLength']=len(bin_); write(sys.argv[3],cj,bin_)
print('merged',len(cj['animations']),'clips; unmatched bones:',missing)
