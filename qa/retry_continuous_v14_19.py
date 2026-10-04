"""Retry the unfinished continuous-input case, not already-passed checkpoints.
Driver fixes only: reachable interaction targets, finite furniture search and
progress snapshots. Candidate game bytes are identical to the first run.
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
# Save natural stage-1 completion to make a later diagnostic resume explicit.
prefix=prefix.replace("R['milestones'].append({'elapsed':round(time.time()-t0,1),'state':s});persist();", "R['milestones'].append({'elapsed':round(time.time()-t0,1),'state':s});(O/'latest_natural_snapshot.json').write_text(json.dumps(p.evaluate('game.snapshot()'),ensure_ascii=False,indent=2));persist();")
exec(compile(prefix,'qa/continue_v14_19.py','exec'),globals())
R['prior_run']='37238039338: both original defects reproduced, r1 fixes, resist/third animations and mobile checks passed; fresh driver stopped too far from box'
R['driver_revision']='2: stop within actual interaction range; original candidate unchanged'
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
