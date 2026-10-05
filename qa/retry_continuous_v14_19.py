"""Retry unfinished continuous input QA; candidate game remains unchanged.
Driver fixes: reachable targets, physical modal clicks and companion clearance.
No progression injection, teleporting, accelerated clock or forced hidden click.
"""
from pathlib import Path
import json,sys,traceback
source=Path('qa/continue_v14_19.py').read_text()
prefix=source.split('try:\n time.sleep(1)\n with sync_playwright()',1)[0]
assert prefix!=source
prefix=prefix.replace("({x:g.box.x-2.9,z:g.box.z-2.9})'),1.4", "({x:g.box.x-2.4,z:g.box.z-1.6})'),.3")
prefix=prefix.replace("({x:g.box.x+3.5,z:g.box.z+3.5})'),1.0", "({x:g.box.x+2.4,z:g.box.z+2.4})'),.45")
prefix=prefix.replace("({x:g.box.x+3,z:g.box.z+3})'),.7", "({x:g.box.x+2.4,z:g.box.z+2.4})'),.45")
prefix=prefix.replace('ang=ring*.65;', 'ang=(ring+int((time.time()-last_change)/6))*.65;')
prefix=prefix.replace("s['cut']['kind'] if s['cut'] else None,s['cut'].get('scene') if s['cut'] else None)", "s['cut']['kind'] if s['cut'] else None,s['cut'].get('scene') if s['cut'] else None,tuple(s['bag'].values()))")
prefix=prefix.replace("R['milestones'].append({'elapsed':round(time.time()-t0,1),'state':s});persist();", "R['milestones'].append({'elapsed':round(time.time()-t0,1),'state':s});(O/'latest_natural_snapshot.json').write_text(json.dumps(p.evaluate('game.snapshot()'),ensure_ascii=False,indent=2));persist();")
old="if p.locator(sel).is_visible():p.locator(sel).click();handled=True;break"
assert prefix.count(old)==1
prefix=prefix.replace(old,"if p.locator(sel).is_visible():activate_modal(p,sel,s);handled=True;break")
prefix=prefix.replace("if not handled:raise AssertionError('Unhandled modal '+s['modalText'][:300])", "if not handled and state(p)['modal']:raise AssertionError('Unhandled modal '+state(p)['modalText'][:300])")
exec(compile(prefix,'qa/continue_v14_19.py','exec'),globals())
R['prior_runs']=['37238039338: original defects reproduced; r1 targeted fixes, ending animations and mobile checks passed','37238504715: fresh Day1, both UI reloads, Day2 reached; modal transition race','37239264528: player remained 1.5m in front of companion after sunset restore; navigation clearance added to driver, not game']
R['driver_revision']='4: visible pointer input and keyboard-only companion clearance; candidate unchanged'
R['driver_events']=[]
def activate_modal(p,sel,before):
 box=p.locator(sel).bounding_box()
 if not box:return
 x=box['x']+box['width']/2;y=box['y']+box['height']/2
 if y<0 or y>p.viewport_size['height']:
  try:p.locator(sel).scroll_into_view_if_needed(timeout=1200)
  except Exception:
   if not state(p)['modal']:return
   raise
  box=p.locator(sel).bounding_box()
  if not box:return
  x=box['x']+box['width']/2;y=box['y']+box['height']/2
 hit=p.evaluate('({sel,x,y})=>{let b=document.querySelector(sel),e=document.elementFromPoint(x,y);return !!b&&!!e&&b.contains(e)&&!b.disabled}',{'sel':sel,'x':x,'y':y})
 if not hit:p.wait_for_timeout(150);return
 p.mouse.click(x,y);p.wait_for_timeout(200)
 after=state(p)
 R['driver_events'].append({'selector':sel,'input':'physical pointer at visible hit-tested button','before_day':before['day'],'after_day':after['day'],'modal_after':after['modal'],'cut_after':after['cut']});persist()

def approach_friend(p,stop):
 # Do not park the player across the companion's collision/pathfinding start.
 # This is test input policy, not an actor-position or collision modification.
 s=state(p);f=s['friend'];a=s['player'];dx=a['x']-f['x'];dz=a['z']-f['z'];d=math.hypot(dx,dz)
 escape=getattr(p,'_qa_follow_escape',None)
 if stop>=5:
  if escape and d<4.3:
   if move_step(p,escape,.55):p._qa_follow_escape=None
   return
  if escape:p._qa_follow_escape=None
  if d<3.2:
   ux=dx/(d or 1);uz=dz/(d or 1)
   if d<.01:ux,uz=0,1
   escape={'x':f['x']+ux*4-uz*3,'z':f['z']+uz*4+ux*3}
   p._qa_follow_escape=escape
   R['driver_events'].append({'input':'keyboard sidestep to leave companion path clear','distance':d,'phase':s['phase'],'goal':escape});persist()
   move_step(p,escape,.55);return
 else:p._qa_follow_escape=None
 return move_step(p,{'x':f['x'],'z':f['z']},stop)
try:
 time.sleep(1)
 with sync_playwright() as pw:
  b=pw.chromium.launch(headless=True,args=['--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
  case('fresh start through Day2 loss ending','continuous keyboard/pointer gameplay with genuine UI save/reload; no injected checkpoint, teleport or accelerated clock',lambda:continuous(b))
  b.close()
except Exception as e:R['fatal']=str(e);R['trace']=traceback.format_exc()
finally:
 server.terminate();persist()
 print('FINAL '+json.dumps({'cases':[{k:v for k,v in c.items() if k not in ('detail','trace')} for c in R['cases']],'fatal':R.get('fatal'),'frames':len(R['frames'])},ensure_ascii=False),flush=True)
 if R.get('fatal') or any(c['status']!='PASS' for c in R['cases']):sys.exit(1)
