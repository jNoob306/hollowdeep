import asyncio, json, os
PORT=int(os.environ.get('PORT','8765'))
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(**({'executable_path':os.environ['CHROME']} if os.environ.get('CHROME') else {}),args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
        pg=await b.new_page(viewport={'width':900,'height':600})
        errs=[]
        pg.on('pageerror',lambda e:errs.append('PAGEERR '+str(e)))
        await pg.goto(f'http://localhost:{PORT}/index.html'); await pg.wait_for_timeout(400)
        r=await pg.evaluate('''()=>{const agg={};let fails=0;
          for(let s=1;s<=60;s++)for(let d=1;d<=4;d++){let L;try{L=__hd.generateLevel(s*7919+3,d);}catch(e){fails++;continue;}
            let corr=0,openC=0;for(let z=1;z<43;z++)for(let x=1;x<43;x++){const i=z*44+x;if(L.g[i])continue;openC++;let w=0;for(const[a,b]of[[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]])w+=L.g[(z+b)*44+x+a];if(w>=3)corr++;}
            const a=agg[d]=agg[d]||{n:0,open:0,corr:0,ex:[9,0],bell:0,det:true};a.n++;a.open+=L.openCount;a.corr+=corr/openC;a.ex[0]=Math.min(a.ex[0],L.exits.length);a.ex[1]=Math.max(a.ex[1],L.exits.length);
            if(L.spawns.some(q=>q.type==='bellman'))a.bell++;
            a.det=a.det&&JSON.stringify(__hd.generateLevel(s*7919+3,d).exits)===JSON.stringify(L.exits);}
          for(const k in agg){agg[k].open=Math.round(agg[k].open/agg[k].n);agg[k].corr=+(agg[k].corr/agg[k].n).toFixed(2);}return {agg,fails};}''')
        print(json.dumps(r))
        m=await pg.evaluate('''()=>{const L=__hd.generateLevel(12345,2);let o='';const bl=L.spawns.find(q=>q.type==='bellman');
          for(let z=0;z<44;z++){for(let x=0;x<44;x++){let c=L.g[z*44+x]?'#':' ';if(x===L.start.cx&&z===L.start.cz)c='S';if(L.exits.some(e=>e.cx===x&&e.cz===z))c='E';if(L.descent&&L.descent.cx===x&&L.descent.cz===z)c='D';if(bl&&Math.floor(bl.x/3)===x&&Math.floor(bl.z/3)===z)c='B';o+=c;}o+='\\n';}return o;}''')
        print(m[:900])
        await pg.click('#enter'); await pg.wait_for_timeout(500)
        await pg.evaluate('''()=>{__hd.loadLevel(2);for(const e of __hd.enemies)if(e.type!=='bellman')e.alive=false;}''')
        await pg.wait_for_timeout(3500)
        print('bell after load',await pg.evaluate('({st:__hd.bell.state,count:__hd.bellCount,toast:document.getElementById("toast").textContent})'))
        await pg.wait_for_timeout(4000)
        print('wander',await pg.evaluate('({st:__hd.bell.state,count:__hd.bellCount,x:__hd.bell.x.toFixed(1),z:__hd.bell.z.toFixed(1)})'))
        # noise: put player 20m away via BFS-reachable open cell, mine-noise
        r=await pg.evaluate('''()=>{const b=__hd.bell,L=__hd.L;let best=null;for(const i of L.open){const x=(i%44+.5)*3,z=(((i/44)|0)+.5)*3,d=Math.hypot(x-b.x,z-b.z);if(d>18&&d<24){best=[x,z];break;}}
          const p=__hd.player;p.x=best[0];p.z=best[1];b.state='listen';b.t=99;__hd.makeNoise(p.x,p.z,26);return b.state;}''')
        print('after noise',r)
        await pg.wait_for_timeout(3000)
        print('hunting',await pg.evaluate('({st:__hd.bell.state,d:Math.hypot(__hd.bell.x-__hd.player.x,__hd.bell.z-__hd.player.z).toFixed(1)})'))
        # stand still, let it catch & grab
        for i in range(90):
            await pg.wait_for_timeout(500)
            st=await pg.evaluate('({st:__hd.bell.state,d:Math.hypot(__hd.bell.x-__hd.player.x,__hd.bell.z-__hd.player.z).toFixed(1),ps:__hd.player.state,s:__hd.state})')
            if st['ps']=='dead' or st['s']!='run': break
        print('final',st)
        await pg.wait_for_timeout(2500)
        print('summary',await pg.evaluate('document.getElementById("sumTitle").textContent+" | "+document.getElementById("sumBody").innerText.split("\\n").filter(x=>x.includes("Taken")).join()'))
        # roll-dodge test
        await pg.click('#sumBtn'); await pg.wait_for_timeout(200); await pg.click('#enter'); await pg.wait_for_timeout(400)
        await pg.evaluate('''()=>{__hd.loadLevel(2);for(const e of __hd.enemies)if(e.type!=='bellman')e.alive=false;const b=__hd.bell,p=__hd.player;b.tollT=0;
           p.x=b.x;p.z=b.z;let ok=false;for(const[dx,dz]of[[0,1],[0,-1],[1,0],[-1,0]]){const x=b.x+dx*2.4,z=b.z+dz*2.4;p.x=x;p.z=z;ok=true;break;}
           b.facing=Math.atan2(p.x-b.x,p.z-b.z);b.state='chase';b.see=true;b.cd=0;b.losT=0;}''')
        for i in range(40):
            await pg.wait_for_timeout(50)
            st=await pg.evaluate('__hd.bell.state')
            if st=='windup': break
        await pg.wait_for_timeout(500)
        await pg.keyboard.press('Space')
        await pg.wait_for_timeout(1000)
        print('after roll',await pg.evaluate('({b:__hd.bell.state,ps:__hd.player.state,hp:__hd.player.hp})'))
        # heavy stagger
        await pg.evaluate('''()=>{const b=__hd.bell;b.state='chase';__hd.damageEnemy(b,50,true);}''')
        print('stagger',await pg.evaluate('__hd.bell.state+" hp "+__hd.bell.hp'))
        # outrun: chase and run away along open path
        r=await pg.evaluate('''()=>{const b=__hd.bell,p=__hd.player;b.state='chase';b.see=true;b.lost=0;b.cd=5;
          const ce=[Math.floor(b.x/3),Math.floor(b.z/3)];return [b.x,b.z,p.x,p.z];}''')
        # boss arena exclusion
        await pg.evaluate('''()=>{__hd.player.hp=100;__hd.player.state='idle';__hd.loadLevel(4);for(const e of __hd.enemies)if(e.type!=='bellman')e.alive=false;const L=__hd.L,b=__hd.bell,p=__hd.player;p.x=L.boss.x;p.z=L.boss.z;b.x=L.boss.x;b.z=L.boss.z+7*3+3;b.state='chase';b.see=true;}''')
        await pg.wait_for_timeout(3000)
        print('arena',await pg.evaluate('(()=>{const L=__hd.L,b=__hd.bell;return {st:b.state,dToBoss:Math.hypot(b.x-L.boss.x,b.z-L.boss.z).toFixed(1),ps:__hd.player.state}})()'))
        print('ERRORS',errs[:10])
        await b.close()
asyncio.run(main())
