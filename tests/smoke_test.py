import asyncio, json, os
PORT=int(os.environ.get('PORT','8765'))
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(**({'executable_path':os.environ['CHROME']} if os.environ.get('CHROME') else {}),args=['--no-sandbox','--use-gl=swiftshader','--enable-unsafe-swiftshader'])
        pg=await b.new_page(viewport={'width':900,'height':600})
        errs=[]
        pg.on('pageerror',lambda e:errs.append('PAGEERR '+str(e)))
        pg.on('console',lambda m:errs.append('CONSOLE '+m.text) if m.type=='error' else None)
        await pg.goto(f'http://localhost:{PORT}/index.html')
        await pg.wait_for_timeout(500)
        print('state',await pg.evaluate('window.__hd&&__hd.state'))
        # generation stats over seeds
        r=await pg.evaluate('''()=>{const out=[];for(let s=1;s<=40;s++)for(let d=1;d<=4;d++){const t=performance.now();const L=__hd.generateLevel(s*7919,d);
          out.push({d,open:L.openCount,ex:L.exits.length,nodes:L.nodes.length,sp:L.spawns.length,ch:L.chests.length,ms:performance.now()-t,
            exReach:L.exits.every(e=>L.exitDist[e.i]===0), desc:!!L.descent, boss:!!L.boss,
            det:JSON.stringify(__hd.generateLevel(s*7919,d).exits)===JSON.stringify(L.exits)});}
          const agg={};for(const o of out){const a=agg[o.d]=agg[o.d]||{n:0,open:0,exMin:9,exMax:0,nodes:0,sp:0,ms:0,det:true,bad:0};a.n++;a.open+=o.open;a.exMin=Math.min(a.exMin,o.ex);a.exMax=Math.max(a.exMax,o.ex);a.nodes+=o.nodes;a.sp+=o.sp;a.ms=Math.max(a.ms,o.ms);a.det=a.det&&o.det;if(!o.exReach||(o.d<4&&!o.desc)||(o.d==4&&!o.boss))a.bad++;}
          return agg;}''')
        print(json.dumps(r))
        await pg.click('#enter'); await pg.wait_for_timeout(800)
        print('after enter',await pg.evaluate('({s:__hd.state,x:__hd.player.x,z:__hd.player.z,en:__hd.enemies.length,ex:__hd.L.exits.length,fl:__hd.player.flasks})'))
        # walk forward
        await pg.keyboard.down('KeyW'); await pg.wait_for_timeout(1500); await pg.keyboard.up('KeyW')
        print('walked',await pg.evaluate('({x:__hd.player.x,z:__hd.player.z,st:__hd.player.state})'))
        # roll, attack
        await pg.keyboard.press('Space'); await pg.wait_for_timeout(100)
        print('roll',await pg.evaluate('__hd.player.state'))
        await pg.wait_for_timeout(700); await pg.keyboard.press('KeyJ'); await pg.wait_for_timeout(100)
        print('atk',await pg.evaluate('__hd.player.state+" stam "+__hd.player.stam.toFixed(0)'))
        await pg.wait_for_timeout(800)
        # teleport next to an enemy and fight
        r=await pg.evaluate('''()=>{const e=__hd.enemies.find(e=>e.type==='crawler')||__hd.enemies[0];const p=__hd.player;p.x=e.x;p.z=e.z-1.6;p.facing=0;__hd.cam.yaw=0;return e.type+' hp '+e.hp;}''')
        print('target',r)
        for i in range(8):
            await pg.keyboard.press('KeyJ'); await pg.wait_for_timeout(450)
        print('fight',await pg.evaluate('''({hp:__hd.player.hp,kills:__hd.run.kills,pack:JSON.stringify(__hd.player.pack),st:__hd.player.state,estates:__hd.enemies.filter(e=>e.alive&&Math.hypot(e.x-__hd.player.x,e.z-__hd.player.z)<12).map(e=>e.type+':'+e.state+':'+e.hp)})'''))
        # lock on
        await pg.keyboard.press('KeyQ'); await pg.wait_for_timeout(100)
        print('lock',await pg.evaluate('__hd.lock&&__hd.lock.type'))
        await pg.keyboard.press('KeyQ')
        # mine a node
        await pg.evaluate('''()=>{const n=__hd.L.nodes[0];const p=__hd.player;p.hp=100;for(const e of __hd.enemies)e.alive=false;p.x=n.x;p.z=n.z;const c=[Math.floor(n.x/3),Math.floor(n.z/3)];p.x=(c[0]+.5)*3;p.z=(c[1]+.5)*3;}''')
        await pg.wait_for_timeout(600)
        print('prompt',await pg.evaluate('document.getElementById("prompt").textContent+"|"+document.getElementById("prompt").className'))
        await pg.keyboard.press('KeyE'); await pg.wait_for_timeout(1800)
        print('mined',await pg.evaluate('JSON.stringify(__hd.player.pack)'))
        # descend
        await pg.evaluate('''()=>{const d=__hd.L.descent;const p=__hd.player;p.x=d.x;p.z=d.z;}''')
        await pg.wait_for_timeout(400); await pg.keyboard.press('KeyE'); await pg.wait_for_timeout(1700)
        print('depth',await pg.evaluate('__hd.L.depth+" en "+__hd.enemies.length'))
        # go to exit and extract
        await pg.evaluate('''()=>{for(const e of __hd.enemies)e.alive=false;const d=__hd.L.exits[0];const p=__hd.player;p.x=d.x;p.z=d.z;}''')
        await pg.wait_for_timeout(400); print('prompt',await pg.evaluate('document.getElementById("prompt").textContent'))
        await pg.keyboard.press('KeyE'); await pg.wait_for_timeout(3500)
        print('extract',await pg.evaluate('({s:__hd.state,stash:JSON.stringify(__hd.save.stash),t:document.getElementById("sumTitle").textContent})'))
        await pg.click('#sumBtn'); await pg.wait_for_timeout(300)
        await pg.evaluate('''()=>{Object.assign(__hd.save.stash,{iron:20,stone:20,fungus:20,bone:20,hide:20})}''')
        await pg.click('button[data-tab="gear"]'); await pg.click('button[data-tab="craft"]')
        await pg.click('button[data-k="w:iron"]'); await pg.click('button[data-k="u:flask"]'); await pg.click('button[data-k="a:hide"]')
        print('craft',await pg.evaluate('JSON.stringify([__hd.save.owned,__hd.save.equip,__hd.save.upg,__hd.save.stash, localStorage.getItem("hollowdeep_save").length])'))
        # death run on boss level with gamepad mock
        await pg.evaluate('''()=>{window.__gp={connected:true,axes:[0,0,0,0],buttons:Array.from({length:17},()=>({pressed:false,value:0}))};navigator.getGamepads=()=>[window.__gp];}''')
        await pg.wait_for_timeout(200)
        # gamepad: Start enters cave
        await pg.evaluate('__gp.buttons[9].pressed=true'); await pg.wait_for_timeout(120); await pg.evaluate('__gp.buttons[9].pressed=false'); await pg.wait_for_timeout(500)
        print('pad start',await pg.evaluate('({s:__hd.state,fl:__hd.player.flasks})'))
        z0=await pg.evaluate('__hd.player.z')
        await pg.evaluate('__gp.axes[1]=-1'); await pg.wait_for_timeout(800); await pg.evaluate('__gp.axes[1]=0')
        print('pad move dz',await pg.evaluate('__hd.player.z')-z0)
        await pg.evaluate('__gp.buttons[5].pressed=true'); await pg.wait_for_timeout(80); print('pad RB',await pg.evaluate('__hd.player.state')); await pg.evaluate('__gp.buttons[5].pressed=false'); await pg.wait_for_timeout(700)
        await pg.evaluate('__gp.buttons[1].pressed=true'); await pg.wait_for_timeout(80); print('pad B',await pg.evaluate('__hd.player.state')); await pg.evaluate('__gp.buttons[1].pressed=false'); await pg.wait_for_timeout(700)
        y0=await pg.evaluate('__hd.cam.yaw'); await pg.evaluate('__gp.axes[2]=1'); await pg.wait_for_timeout(300); await pg.evaluate('__gp.axes[2]=0'); print('pad look dyaw',await pg.evaluate('__hd.cam.yaw')-y0)
        await pg.evaluate('__gp.buttons[9].pressed=true'); await pg.wait_for_timeout(120); await pg.evaluate('__gp.buttons[9].pressed=false'); await pg.wait_for_timeout(200)
        print('pad pause',await pg.evaluate('__hd.state'))
        await pg.evaluate('__gp.buttons[1].pressed=true'); await pg.wait_for_timeout(120); await pg.evaluate('__gp.buttons[1].pressed=false'); await pg.wait_for_timeout(200)
        print('pad resume',await pg.evaluate('__hd.state'))
        # boss level
        await pg.evaluate('''()=>{__hd.loadLevel(4);const b=__hd.enemies.find(e=>e.type==='boss');const p=__hd.player;p.x=b.x;p.z=b.z-8;}''')
        seen=set()
        for i in range(60):
            await pg.wait_for_timeout(250)
            st=await pg.evaluate('''(()=>{const b=__hd.enemies.find(e=>e.type==='boss');__hd.player.hp=Math.max(__hd.player.hp,60);return b.state+':'+(b.atk?b.atk.kind:'-')+':'+b.phase2})()''')
            seen.add(st)
            if i==30: await pg.evaluate('''()=>{const b=__hd.enemies.find(e=>e.type==='boss');__hd.damageEnemy(b,330,true)}''')
        print('boss states',sorted(seen))
        await pg.evaluate('''()=>{const b=__hd.enemies.find(e=>e.type==='boss');__hd.damageEnemy(b,9999,true)}'''); await pg.wait_for_timeout(1500)
        print('boss dead pack',await pg.evaluate('JSON.stringify(__hd.player.pack)+" boss="+__hd.run.boss'))
        await pg.evaluate('__hd.damagePlayer(9999,0,0,true)'); await pg.wait_for_timeout(2500)
        print('death',await pg.evaluate('({s:__hd.state,t:document.getElementById("sumTitle").textContent,stats:JSON.stringify(__hd.save.stats)})'))
        print('ERRORS',errs[:15])
        await b.close()
asyncio.run(main())
