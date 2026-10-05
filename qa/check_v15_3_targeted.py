"""Latest v15.3 targeted regression. No claim of fresh completion or Day3 QA.
Use previous real-input regression driver; preserve game clocks and renderer.
"""
from pathlib import Path
import json,traceback,sys,hashlib,os
source=Path('qa/complete_v14_19_r2.py').read_text().split('try:\n time.sleep(1)\n with sync_playwright()',1)[0]
source=source.replace("'from apply_v14_19_r2 import'","'from apply_v15_3_r1 import'")
exec(compile(source,'qa/complete_v14_19_r2.py','exec'),globals())
assert M['candidate_sha256']=='954d6d00e930e2e95b3595caa69e1515de0d71962dbeccb2d78549214d18011c'
R.update(build_target='Muse v15.3-r1; new Day3 preserved verbatim',capture_warnings=[],source_run_id=os.environ.get('GITHUB_RUN_ID'),scope='Three targeted regression cases only; no fresh completion or Day3 play-through claim',prior_fresh_incomplete_runs=[37247951908,37249361919,37249942335,37250826122,37251133721,37251310548])
def shot(p,name,method):
 s=state(p);entry={'name':name,'method':method,'state':s,'capture_status':'STATE_RECORDED'};R['frames'].append(entry);persist()
 try:
  p.evaluate('__qaDraw()');p.screenshot(path=str(O/(name+'.jpg')),type='jpeg',quality=75,timeout=12000);entry['capture_status']='CAPTURED'
 except Exception as e:
  entry['capture_status']='CAPTURE_INCOMPLETE';R['capture_warnings'].append({'name':name,'error':str(e)})
 persist();return s

def click_visible(p,selector):
 p.locator(selector).wait_for(state='visible',timeout=10000)
 point=p.evaluate('''sel=>{let el=document.querySelector(sel);if(!el)return null;let r=el.getBoundingClientRect(),x=r.x+r.width/2,y=r.y+r.height/2,h=document.elementFromPoint(x,y);return {x,y,ok:!!h&&(h===el||el.contains(h))&&r.width>0&&r.height>0};}''',selector)
 assert point and point['ok'],{'selector':selector,'point':point}
 p.mouse.click(point['x'],point['y'])

def reload_ui(p):
 if not p.locator('#menuBtn').is_visible():click_visible(p,'[data-hud-toggle="utilityPanel"]')
 click_visible(p,'#menuBtn');click_visible(p,'#saveNow')
 before=p.evaluate('game.snapshot()')
 saved=p.evaluate('JSON.parse(localStorage.getItem("meownuri:MEOWNURI9:story:v3-wide"))')
 assert saved and saved.get('agencyProgress')==before.get('agencyProgress'),'UI save missing progression'
 p.reload(wait_until='load');p.wait_for_function('!!window.game && !!window.__meowAgency');p.wait_for_timeout(700)
 R.setdefault('reload_diagnostics',[]).append(p.evaluate('''()=>({url:location.href,saveLength:(localStorage.getItem('meownuri:MEOWNURI9:story:v3-wide')||'').length,continueHidden:document.querySelector('#continueBtn').hidden,mode:game.mode,errors:__qaErrors})'''));persist()
 click_visible(p,'#continueBtn');p.locator('#continueBtn').wait_for(state='hidden',timeout=10000);p.wait_for_timeout(350)
 return before,state(p)

def restore_fixture(b,candidate):
 c,p=setup(b,candidate)
 p.evaluate('(s)=>localStorage.setItem("meownuri:MEOWNURI9:story:v3-wide",JSON.stringify(s))',FIX)
 p.reload(wait_until='load');p.wait_for_function('!!window.game && !!window.__meowAgency');p.wait_for_timeout(700)
 click_visible(p,'#continueBtn');p.locator('#continueBtn').wait_for(state='hidden',timeout=10000);p.wait_for_timeout(700)
 return c,p
try:
 time.sleep(1)
 with sync_playwright() as pw:
  b=pw.chromium.launch(headless=True,args=['--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
  case('v15.3 R01 R02 targeted save and ending guard','seeded checkpoint, actual UI save/reload twice, original watchdog timer; not fresh play',lambda:baseline(b,True))
  case('v15.3 R03 natural save through actual ending','unaltered natural save and furniture, real keys/pointer and actual cinematics; no stage skipping',lambda:repaired_home_and_ending(b))
  case('v15.3 mobile controls','390x844 touch/pointer emulation, not physical Android or FPS',lambda:mobile(b))
  b.close()
except Exception as e:R['fatal']=str(e);R['trace']=traceback.format_exc()
finally:
 server.terminate();persist()
 print('FINAL '+json.dumps({'cases':[{k:v for k,v in c.items() if k not in ('detail','trace')} for c in R['cases']],'fatal':R.get('fatal'),'capture_warnings':R['capture_warnings']},ensure_ascii=False),flush=True)
 if R.get('fatal') or len(R['cases'])!=3 or any(c['status']!='PASS' for c in R['cases']):sys.exit(1)
