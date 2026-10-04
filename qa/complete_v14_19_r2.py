"""Final r2 QA. Natural-save regression and fresh full play are separate cases."""
from pathlib import Path
import json,hashlib,sys,traceback
bootstrap=Path('qa/retry_continuous_v14_19.py').read_text().split('try:\n time.sleep(1)\n with sync_playwright()',1)[0]
anchor="exec(compile(prefix,'qa/continue_v14_19.py','exec'),globals())"
assert bootstrap.count(anchor)==1
bootstrap=bootstrap.replace(anchor,"prefix=prefix.replace('from apply_v14_19_r1 import','from apply_v14_19_r2 import').replace('candidate_r1','candidate_r2')\n"+anchor)
exec(compile(bootstrap,'qa/retry_continuous_v14_19.py','exec'),globals())
R['build_target']='v14.19-r2; original/main untouched'
R['natural_fixture_origin']='Unmodified game.snapshot() from natural fresh run 37240016517, at 469.4 seconds immediately after fish scene'
FIX=json.loads(Path('qa/natural_day2_save_37240016517.json').read_text())
R['natural_fixture_sha256_canonical']=hashlib.sha256(json.dumps(FIX,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def restore_fixture(b,candidate):
 c,p=setup(b,candidate)
 p.evaluate('(s)=>localStorage.setItem("meownuri:MEOWNURI9:story:v3-wide",JSON.stringify(s))',FIX)
 p.reload(wait_until='load');p.wait_for_function('!!window.game && !!window.__meowAgency');p.wait_for_timeout(700)
 p.locator('#continueBtn').click();p.wait_for_timeout(700)
 return c,p

def blocked_original(b):
 c,p=restore_fixture(b,False)
 try:
  diag=p.evaluate('()=>{let g=game,t={x:g.box.x,z:g.box.z+3.5},r=g.friend.radius+.06;return {target:t,blocked:g.ground.blocked(t.x,t.z,r),route_length:g.ground.path(g.friend,t,r,g.otherActors(g.friend)).length,furniture:g.snapshot().furniture}}')
  assert diag['blocked'] and diag['route_length']==0,diag
  start=state(p)['friend'];p.wait_for_timeout(3500);s=shot(p,'R03_original_blocked_home','Unmodified natural save loaded; no progression/position editing; original goal intersects bed')
  assert not s['clueReady'];assert math.hypot(start['x']-s['friend']['x'],start['z']-s['friend']['z'])<.5
  return {'diagnostic':diag,'state':s}
 finally:c.close()

def repaired_home_and_ending(b):
 c,p=restore_fixture(b,True)
 try:
  t=time.time()
  while time.time()-t<45 and not state(p)['clueReady']:
   approach_friend(p,5.5)
  s=shot(p,'R03_r2_home_arrived','Same natural save and furniture; ordinary travel to nearby free home position')
  assert s['clueReady'],s
  assert p.evaluate('JSON.stringify(game.snapshot().furniture)')==json.dumps(FIX['furniture'],ensure_ascii=False,separators=(',',':')),'Furniture changed'
  assert math.hypot(s['friend']['x']-10,s['friend']['z']-8)<8,s
  t=time.time()
  while time.time()-t<25:
   s=state(p)
   if s['cut']:break
   if s['action'] and '주변 듣기' in s['action']['text']:p.keyboard.press('e')
   else:move_step(p,{'x':12.4,'z':10.4},.45)
  p.locator('#choiceSacrifice').wait_for(state='visible',timeout=100000)
  shot(p,'R03_r2_bear_choice','Natural-save continuation; actual silence and bear cinematics, no scene skipping')
  for _ in range(12):
   s=state(p)
   if s['cut'] or s['ending']:break
   activate_modal(p,'#choiceSacrifice',s);p.wait_for_timeout(200)
  p.wait_for_function('game.ending',timeout=100000);p.wait_for_timeout(5200)
  end=shot(p,'R03_r2_loss_ending','Natural-save continuation through actual choice and loss animation; ending watchdog observed')
  assert not end['friend']['active'];assert not end['errors']
  return {'home_goal_arrived':True,'furniture_unchanged':True,'ending':end,'seconds':round(time.time()-t,1)}
 finally:c.close()
try:
 time.sleep(1)
 with sync_playwright() as pw:
  b=pw.chromium.launch(headless=True,args=['--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
  case('R03 original blocked destination reproduced','natural saved layout, original v14.19, collision and path evidence',lambda:blocked_original(b))
  case('R03 repaired home return through actual ending','same natural saved layout, r2, ordinary movement plus visible UI; explicitly not a fresh start',lambda:repaired_home_and_ending(b))
  case('R01 R02 retained in r2','seeded checkpoints and actual UI save/reload, distinct from fresh play',lambda:baseline(b,True))
  case('r2 fresh start through Day2 loss ending','fresh empty browser; actual keyboard/pointer; two UI saves/reloads; no injected checkpoint, teleport or clock acceleration',lambda:continuous(b))
  case('r2 mobile controls','390x844 touch/pointer emulation; not physical Android performance',lambda:mobile(b))
  b.close()
except Exception as e:R['fatal']=str(e);R['trace']=traceback.format_exc()
finally:
 server.terminate();persist()
 print('FINAL '+json.dumps({'cases':[{k:v for k,v in c.items() if k not in ('detail','trace')} for c in R['cases']],'fatal':R.get('fatal'),'frames':len(R['frames'])},ensure_ascii=False),flush=True)
 if R.get('fatal') or any(c['status']!='PASS' for c in R['cases']):sys.exit(1)
