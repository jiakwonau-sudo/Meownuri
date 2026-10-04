"""Complete only the unfinished natural-save outcome test.
The fresh keyboard-input playthrough and both UI reloads already passed in
run 37241216746. Game bytes, simulation timing and collision are unchanged.
"""
from pathlib import Path
import json,sys,traceback
source=Path('qa/complete_v14_19_r2.py').read_text()
bootstrap=source.split('try:\n time.sleep(1)\n with sync_playwright()',1)[0]
assert bootstrap!=source
# Observed original silence + bear cinematics take about 124 real seconds.
# The previous 100-second selector wait was too short; no game time changes.
bootstrap=bootstrap.replace('timeout=100000','timeout=180000')
exec(compile(bootstrap,'qa/complete_v14_19_r2.py','exec'),globals())
R['prior_verified_run']='37241216746: original R03 reproduced; r2 home arrival verified; R01/R02, fresh start through ending with two actual UI reloads, and mobile all passed. Not repeated here.'
R['timeout_correction']='Only selector waiting budget increased from 100s to 180s; observed silence + bear sequences were about124s in the passing fresh run.'
try:
 time.sleep(1)
 with sync_playwright() as pw:
  b=pw.chromium.launch(headless=True,args=['--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
  case('R03 natural save through full loss ending','same unmodified natural save and furniture, normal movement and visible pointer/keyboard input; longer wait budget only',lambda:repaired_home_and_ending(b))
  b.close()
except Exception as e:R['fatal']=str(e);R['trace']=traceback.format_exc()
finally:
 server.terminate();persist()
 print('FINAL '+json.dumps({'cases':[{k:v for k,v in c.items() if k not in ('detail','trace')} for c in R['cases']],'fatal':R.get('fatal'),'frames':len(R['frames'])},ensure_ascii=False),flush=True)
 if R.get('fatal') or any(c['status']!='PASS' for c in R['cases']):sys.exit(1)
