"""Fresh-route retry: replace only automatic navigation waits on UI clicks.
Actual visible hit-tested pointer events, storage reload, and game assertions
are retained. Game source and timing remain byte-identical to prior runs.
"""
from pathlib import Path
import sys
assert sys.argv[1:] == ['fresh']
bootstrap=Path('qa/retry_v15_2.py').read_text().split('try:\n    time.sleep(1)',1)[0]
exec(compile(bootstrap,'qa/retry_v15_2.py','exec'),globals())
R['retry_of']='37249361919 fresh: Locator.click completed but its automatic navigation wait timed out; recorded final state already restored the journey'
R['driver_revision']='physical hit-tested save/continue pointer, explicit visible state checks instead of implicit navigation waits'
def click_visible(p,selector):
    p.locator(selector).wait_for(state='visible',timeout=60000)
    point=p.evaluate('''sel=>{const el=document.querySelector(sel);if(!el)return null;const r=el.getBoundingClientRect();const x=r.x+r.width/2,y=r.y+r.height/2;const hit=document.elementFromPoint(x,y);return {x,y,ok:!!hit&&(hit===el||el.contains(hit))&&r.width>0&&r.height>0};}''',selector)
    assert point and point['ok'], {'selector':selector,'hit_test':point}
    p.mouse.click(point['x'],point['y'])
def reload_ui(p):
    if not p.locator('#menuBtn').is_visible():click_visible(p,'[data-hud-toggle="utilityPanel"]')
    click_visible(p,'#menuBtn');click_visible(p,'#saveNow')
    before=p.evaluate('game.snapshot()')
    saved=p.evaluate('JSON.parse(localStorage.getItem("meownuri:MEOWNURI9:story:v3-wide"))')
    assert saved and saved.get('agencyProgress')==before.get('agencyProgress'),'UI save did not persist current journey'
    p.reload(wait_until='load')
    p.wait_for_function('!!window.game && !!window.__meowAgency',timeout=60000)
    p.wait_for_timeout(700)
    click_visible(p,'#continueBtn')
    p.locator('#continueBtn').wait_for(state='hidden',timeout=60000)
    p.wait_for_function("game.mode==='play'",timeout=60000)
    p.wait_for_timeout(350)
    after=state(p)
    R.setdefault('driver_events',[]).append({'event':'UI_SAVE_RELOAD','day':before.get('dayNumber'),'phase':before.get('storyPhase'),'storage_verified':True,'home_restored':after['homeJourney'],'sunset_restored':after['sunsetJourney'],'errors':after['errors']})
    persist()
    return before,after
try:
    time.sleep(1)
    with sync_playwright() as pw:
        b=pw.chromium.launch(headless=True,args=['--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
        case('v15.2-r1 fresh start through Day2 loss ending','empty storage; original clocks; actual visible pointer and keyboard; two verified UI save/reloads; no checkpoint injection or teleport',lambda:continuous(b))
        b.close()
except Exception as e:
    R['fatal']=str(e);R['trace']=traceback.format_exc()
finally:
    server.terminate();persist()
    print('FINAL '+json.dumps({'cases':[{k:v for k,v in c.items() if k not in ('detail','trace')} for c in R['cases']],'fatal':R.get('fatal'),'capture_warnings':R['capture_warnings']},ensure_ascii=False),flush=True)
    if R.get('fatal') or len(R['cases'])!=1 or any(c['status']!='PASS' for c in R['cases']):sys.exit(1)
