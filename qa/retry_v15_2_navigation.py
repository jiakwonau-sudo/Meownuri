"""Outer-house keyboard approach. Game bytes remain unchanged.
Natural-save UI preflight and fresh-empty full play use separate contexts.
"""
from pathlib import Path
import sys
assert sys.argv[1:]==['fresh']
bootstrap=Path('qa/retry_v15_2_fresh.py').read_text().split('try:\n    time.sleep(1)',1)[0]
exec(compile(bootstrap,'qa/retry_v15_2_fresh.py','exec'),globals())
R['retry_of']='Earlier fresh/preflight interruptions: capture, implicit click wait, tangent navigation; 37251133721 reached home action but expected cinematic before its required choice screen'
R['driver_revision']='Staged outer-house keyboard route; assert visible home choice before cinematic; no game-state mutation'
previous_move_step=move_step
route_pages={}
def move_step(p,goal,stop=2.1):
    s=state(p)
    home=s['stage']==7 and ((s['phase']==1 and s['homeReady']) or (s['phase']==5 and s['clueReady']))
    if not home or s['cut'] or s['ending']:return previous_move_step(p,goal,stop)
    routes=route_pages.setdefault(p,{})
    if s['phase'] not in routes:
        box=target(p,'g.box')
        routes[s['phase']]={'i':0,'waypoints':[{'x':box['x']+8,'z':box['z']+8},{'x':box['x']+8,'z':box['z']},{'x':box['x']+3.7,'z':box['z']}]}
        R.setdefault('driver_events',[]).append({'event':'OUTER_HOME_APPROACH','phase':s['phase'],'waypoints':routes[s['phase']]['waypoints']});persist()
    route=routes[s['phase']];i=route['i']
    done=previous_move_step(p,route['waypoints'][i],.85 if i<2 else .4)
    if done and i<2:route['i']+=1
    return done and i==2

def navigation_preflight(b):
    c,p=setup(b,True)
    try:
        saved=json.loads(Path('qa/natural_home_ready_37249942335.json').read_text())
        p.evaluate('(s)=>localStorage.setItem("meownuri:MEOWNURI9:story:v3-wide",JSON.stringify(s))',saved)
        p.reload(wait_until='load');p.wait_for_function('!!window.game && !!window.__meowAgency',timeout=60000);p.wait_for_timeout(700)
        click_visible(p,'#continueBtn');p.locator('#continueBtn').wait_for(state='hidden',timeout=60000)
        t=time.time();s=state(p);assert s['phase']==1 and s['homeReady']
        while time.time()-t<45:
            s=state(p)
            if s['action'] and '표지판' in s['action']['text']:
                p.keyboard.press('e')
                p.locator('[data-ag="0"]').wait_for(state='visible',timeout=10000)
                after=state(p)
                assert after['modal'] and '우리의 집' in after['modalText'] and not after['errors'],after
                return {'pass':True,'source':'unmodified natural snapshot from run 37249942335','seconds':round(time.time()-t,1),'actual_action':s['action'],'distance_to_box':p.evaluate('game.dist(game.box)'),'state':after,'meaning':'Real E interaction opened the home choice UI; cinematic requires another player choice'}
            move_step(p,{'x':13,'z':11},.7)
        raise AssertionError('No reachable home action within 45 seconds: '+json.dumps(state(p),ensure_ascii=False))
    finally:c.close()
try:
    time.sleep(1)
    with sync_playwright() as pw:
        b=pw.chromium.launch(headless=True,args=['--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
        R['navigation_preflight']=navigation_preflight(b);persist()
        print('NAVIGATION_PREFLIGHT '+json.dumps(R['navigation_preflight'],ensure_ascii=False),flush=True)
        case('v15.2-r1 fresh start through Day2 loss ending','separate empty browser; original clocks; real pointer and keyboard; two verified UI save/reloads; geometry-assisted navigation; no checkpoints, teleports or phase changes',lambda:continuous(b))
        b.close()
except Exception as e:R['fatal']=str(e);R['trace']=traceback.format_exc()
finally:
    server.terminate();persist()
    print('FINAL '+json.dumps({'cases':[{k:v for k,v in c.items() if k not in ('detail','trace')} for c in R['cases']],'fatal':R.get('fatal'),'capture_warnings':R['capture_warnings']},ensure_ascii=False),flush=True)
    if R.get('fatal') or len(R['cases'])!=1 or any(c['status']!='PASS' for c in R['cases']):sys.exit(1)
