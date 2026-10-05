"""Steer to a reachable interaction position, not a hard-coded occupied point.
Game bytes, collision, clocks, completion assertions and real input are unchanged.
The fixture preflight is separate; the subsequent full route starts empty.
"""
from pathlib import Path
import sys
assert sys.argv[1:]==['fresh']
bootstrap=Path('qa/retry_v15_2_fresh.py').read_text().split('try:\n    time.sleep(1)',1)[0]
exec(compile(bootstrap,'qa/retry_v15_2_fresh.py','exec'),globals())
R['retry_of']='37249942335: home restored and reached; driver targeted a point blocked by furniture/friend, outside the 4.5m interaction radius'
R['driver_revision']='Read-only reachable ring sampling for home interactions; actual keys, no actor/quest mutation'
previous_move_step=move_step
def move_step(p,goal,stop=2.1):
    resolved=p.evaluate('''()=>{const g=game,a=g.player;const home=g.stage===7&&((g.storyPhase===1&&g.homeReady)||(g.storyPhase===5&&g.clueLeadReady));if(!home||g.cut||g.ending)return null;const r=a.radius+.03,actors=g.otherActors(a),points=[];for(let i=0;i<32;i++){const ang=i*Math.PI/16,q={x:g.box.x+Math.sin(ang)*3.7,z:g.box.z+Math.cos(ang)*3.7};if(g.ground.safe(q.x,q.z,r,actors))points.push(q);}points.sort((a1,b1)=>Math.hypot(a1.x-a.x,a1.z-a.z)-Math.hypot(b1.x-a.x,b1.z-a.z));for(const q of points){if(Math.hypot(q.x-a.x,q.z-a.z)<.5||g.ground.path(a,q,r,actors).length)return q;}return null;}''')
    return previous_move_step(p,resolved if resolved else goal,.35 if resolved else stop)
def navigation_preflight(b):
    c,p=setup(b,True)
    try:
        saved=json.loads(Path('qa/natural_home_ready_37249942335.json').read_text())
        p.evaluate('(s)=>localStorage.setItem("meownuri:MEOWNURI9:story:v3-wide",JSON.stringify(s))',saved)
        p.reload(wait_until='load');p.wait_for_function('!!window.game && !!window.__meowAgency',timeout=60000);p.wait_for_timeout(700)
        click_visible(p,'#continueBtn');p.locator('#continueBtn').wait_for(state='hidden',timeout=60000)
        t=time.time();s=state(p)
        assert s['phase']==1 and s['homeReady']
        while time.time()-t<45:
            s=state(p)
            if s['action'] and '표지판' in s['action']['text']:
                p.keyboard.press('e')
                p.wait_for_function("game.cut && game.cut.scene==='home'",timeout=10000)
                result={'pass':True,'source':'unmodified natural snapshot from failed driver run 37249942335','seconds':round(time.time()-t,1),'actual_action':s['action'],'distance_to_box':p.evaluate('game.dist(game.box)'),'state':state(p)}
                assert not result['state']['errors'];return result
            move_step(p,{'x':13,'z':11},.7)
        raise AssertionError('No reachable home action within 45 seconds: '+json.dumps(state(p),ensure_ascii=False))
    finally:c.close()
try:
    time.sleep(1)
    with sync_playwright() as pw:
        b=pw.chromium.launch(headless=True,args=['--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
        R['navigation_preflight']=navigation_preflight(b);persist()
        print('NAVIGATION_PREFLIGHT '+json.dumps(R['navigation_preflight'],ensure_ascii=False),flush=True)
        case('v15.2-r1 fresh start through Day2 loss ending','separate empty browser; original clocks; real pointer and keyboard; two verified UI save/reloads; read-only geometry for navigation; no checkpoints, teleports or phase changes',lambda:continuous(b))
        b.close()
except Exception as e:R['fatal']=str(e);R['trace']=traceback.format_exc()
finally:
    server.terminate();persist()
    print('FINAL '+json.dumps({'cases':[{k:v for k,v in c.items() if k not in ('detail','trace')} for c in R['cases']],'fatal':R.get('fatal'),'capture_warnings':R['capture_warnings']},ensure_ascii=False),flush=True)
    if R.get('fatal') or len(R['cases'])!=1 or any(c['status']!='PASS' for c in R['cases']):sys.exit(1)
