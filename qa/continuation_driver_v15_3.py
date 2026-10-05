"""Continue the archived Muse v15.3-r1 candidate. No public deployment.
Natural-save continuation and seeded ending checks are explicitly distinct.
Only real pointer/key events advance the natural-save case. The original
renderer is called on demand; the simulation clock/timers are not accelerated.
"""
from pathlib import Path
import hashlib,json,math,os,subprocess,time,traceback,sys
from playwright.sync_api import sync_playwright
O=Path('qa-resume');O.mkdir(exist_ok=True)
KEY='meownuri:MEOWNURI9:story:v3-wide'
EXPECTED='954d6d00e930e2e95b3595caa69e1515de0d71962dbeccb2d78549214d18011c'
assert hashlib.sha256(Path('index.html').read_bytes()).hexdigest()==EXPECTED
FIX=json.loads(Path('qa/natural_day2_save_37240016517.json').read_text())
R={'build':'Muse v15.3-r1','sha256':EXPECTED,'run_id':os.environ.get('GITHUB_RUN_ID'),'commit':os.environ.get('GITHUB_SHA'),'rendering':'original renderer on demand; normal game clocks','fresh_run_completed':False,'cases':[],'events':[],'frames':[],'observations':[]}
INIT="""window.__qaErrors=[];addEventListener('error',e=>__qaErrors.push(e.message));addEventListener('unhandledrejection',e=>__qaErrors.push(String(e.reason)));Object.defineProperty(window,'__MEOWNURI9',{configurable:true,get(){return window.__qaGame},set(g){window.__qaGame=g;const draw=g.renderer.render.bind(g.renderer);g.renderer.render=()=>{};window.__qaDraw=()=>{g.updateUI();g.updateLabels();draw(g.scene,g.camera);return {...g.renderer.info.render}};}});"""
STATE="""()=>{let g=game;return {t:g.t,day:g.dayNumber,stage:g.stage,phase:g.storyPhase,mode:g.mode,cut:g.cut?{kind:g.cut.kind,scene:g.cut.scene,phase:g.cut.phase,time:g.cut.time}:null,locked:g.storyLock,ending:g.ending,bear:g.bearStarted,rest:g.homeResting,home:!!g.homeJourney,homeReady:g.homeReady,clue:g.clueLead,clueReady:g.clueLeadReady,player:{x:g.player.x,y:g.player.y,z:g.player.z},friend:{x:g.friend.x,z:g.friend.z,active:g.friend.active},box:{x:g.box.x,z:g.box.z},action:g.action?{text:g.action.text,enabled:g.action.enabled}:null,modal:!document.querySelector('#modal').hidden,modalText:document.querySelector('#modalBody').innerText,quest:document.querySelector('#questText').innerText,day3:{button:!!document.querySelector('#agDay3Btn'),visible:!!document.querySelector('#agDay3Btn')?.getClientRects().length,active:!!window.__day3active,done:localStorage.getItem('meownuri:day3:done'),choice:localStorage.getItem('meownuri:day3')},errors:__qaErrors}}"""
def persist(): (O/'results.json').write_text(json.dumps(R,ensure_ascii=False,indent=2))
def state(p): return p.evaluate(STATE)
def event(p,label):
 s=state(p);R['events'].append({'label':label,'state':s});persist();print(label+' '+json.dumps(s,ensure_ascii=False),flush=True);return s

def shot(p,name):
 e={'name':name,'state':state(p)};R['frames'].append(e);persist()
 try:
  p.evaluate('__qaDraw()');p.screenshot(path=str(O/(name+'.jpg')),type='jpeg',quality=78,timeout=18000);e['capture']='CAPTURED'
 except Exception as x:e['capture']='FAILED';e['error']=str(x)
 persist()

def click(p,sel):
 p.locator(sel).wait_for(state='visible',timeout=10000)
 p.locator(sel).scroll_into_view_if_needed(timeout=4000)
 d=p.evaluate("""s=>{let e=document.querySelector(s),r=e.getBoundingClientRect(),x=r.x+r.width/2,y=r.y+r.height/2,h=document.elementFromPoint(x,y);return{x,y,hit:!!h&&(e===h||e.contains(h)),disabled:e.disabled}}""",sel)
 assert d['hit'] and not d.get('disabled'),(sel,d)
 p.mouse.click(d['x'],d['y']);p.wait_for_timeout(180)

def setup(b,mobile=False):
 c=b.new_context(viewport={'width':390 if mobile else 1280,'height':844 if mobile else 800},is_mobile=mobile,has_touch=mobile,device_scale_factor=1)
 c.add_init_script(INIT);p=c.new_page();p.set_default_timeout(15000)
 p.goto('http://127.0.0.1:8776/',wait_until='load');p.wait_for_function('!!window.game && !!window.__meowAgency');p.wait_for_timeout(700)
 return c,p

def save_reload(p):
 if not p.locator('#menuBtn').is_visible():click(p,'[data-hud-toggle="utilityPanel"]')
 click(p,'#menuBtn');click(p,'#saveNow')
 before=p.evaluate('game.snapshot()');saved=p.evaluate('(k)=>JSON.parse(localStorage.getItem(k))',KEY)
 assert saved.get('agencyProgress')==before.get('agencyProgress'),'Save progression mismatch'
 p.reload(wait_until='load');p.wait_for_function('!!window.game && !!window.__meowAgency');p.wait_for_timeout(700)
 assert p.locator('#continueBtn').is_visible(),{'error':'Continue unavailable','saved':p.evaluate('(k)=>localStorage.getItem(k)',KEY),'state':state(p)}
 click(p,'#continueBtn');p.wait_for_function("document.querySelector('#start').hidden");p.wait_for_timeout(250)
 return before,state(p)

# The steering vector is applied through the actual on-screen joystick. This
# avoids the previous driver's eight-direction overshoot near furniture.
def move_step(p,goal,stop=1.0):
 d=p.evaluate("""({goal,stop})=>{let g=game,a=g.player,dist=Math.hypot(a.x-goal.x,a.z-goal.z);if(dist<stop)return{done:true};let actors=g.otherActors(a),end=g.ground.nearest(goal.x,goal.z,a.radius+.03,actors);if(!end)return{blocked:true};let path=g.ground.path(a,end,a.radius+.03,actors);let w=path.find(q=>Math.hypot(q.x-a.x,q.z-a.z)>.18)||end;return{dx:w.x-a.x,dz:w.z-a.z,yaw:g.yaw,path:path.length,jump:g.ground.height(w.x,w.z)>a.y+.10,dist};}""",{'goal':goal,'stop':stop})
 if d.get('done'):p.wait_for_timeout(100);return True
 if d.get('blocked'):p.wait_for_timeout(100);return False
 f=math.sin(d['yaw'])*d['dx']+math.cos(d['yaw'])*d['dz'];r=-math.cos(d['yaw'])*d['dx']+math.sin(d['yaw'])*d['dz'];m=math.hypot(f,r) or 1
 rect=p.locator('#joystick').bounding_box();assert rect,'Missing movement control'
 cx=rect['x']+rect['width']/2;cy=rect['y']+rect['height']/2
 p.mouse.move(cx,cy);p.mouse.down();p.mouse.move(cx+r/m*35,cy-f/m*35)
 if d['jump']:p.keyboard.press('Space')
 p.wait_for_timeout(max(35,min(130,m/4.4*600)));p.mouse.up()
 return False

def wait_state(p,predicate,seconds,label):
 start=time.monotonic();last=None;lastlog=0
 while time.monotonic()-start<seconds:
  s=state(p);assert not s['errors'],s['errors']
  sig=(s['day'],s['phase'],str(s['cut']),s['ending'],s['modal'])
  if sig!=last and time.monotonic()-lastlog>4:event(p,label);last=sig;lastlog=time.monotonic()
  if predicate(s):return s
  p.wait_for_timeout(200)
 event(p,label+'_TIMEOUT');shot(p,label+'_timeout');raise TimeoutError(label+' '+json.dumps(state(p),ensure_ascii=False))

def home_to_ending(b):
 c,p=setup(b)
 try:
  p.evaluate('([k,s])=>localStorage.setItem(k,JSON.stringify(s))',[KEY,FIX]);p.reload(wait_until='load');p.wait_for_function('!!window.game && !!window.__meowAgency');p.wait_for_timeout(700);click(p,'#continueBtn')
  event(p,'natural_restore')
  for i in range(2):
   before,after=save_reload(p);assert after['clueReady'] or after['clue'],'Lost clue journey';event(p,'real_save_reload_'+str(i+1))
  start=time.monotonic();nextlog=0
  while time.monotonic()-start<85:
   s=state(p)
   if s['clueReady']:break
   move_step(p,s['friend'],5.0)
   if time.monotonic()>nextlog:event(p,'home_travel');nextlog=time.monotonic()+10
  assert state(p)['clueReady'],'Kkami did not arrive home'
  assert p.evaluate('game.snapshot().furniture')==FIX['furniture'],'Furniture altered'
  shot(p,'01_home_arrived');event(p,'home_arrival_verified')
  # Choose a reachable point in the actual interaction radius instead of the
  # old single hard-coded point. Geometry inspection is read-only.
  goal=p.evaluate("""()=>{let g=game,a=g.player,actors=g.otherActors(a),best=null;for(let r of[4.4,3.8,3.2])for(let t=0;t<Math.PI*2;t+=.24){let q={x:g.box.x+Math.sin(t)*r,z:g.box.z+Math.cos(t)*r};if(!g.ground.safe(q.x,q.z,a.radius+.08,actors))continue;let path=g.ground.path(a,q,a.radius+.03,actors);if(!path.length)continue;let len=0,last=a;for(let w of path){len+=Math.hypot(w.x-last.x,w.z-last.z);last=w}if(!best||len<best.len)best={...q,len}}return best}""")
  assert goal,'No reachable home interaction point';R['interaction_goal']=goal;persist()
  start=time.monotonic();nextlog=0
  while time.monotonic()-start<60:
   s=state(p)
   if s['cut']:break
   if s['action'] and '주변 듣기' in s['action']['text']:
    p.keyboard.press('e');p.wait_for_timeout(250)
   else:move_step(p,goal,.25)
   if time.monotonic()>nextlog:event(p,'approach_silence');nextlog=time.monotonic()+8
  assert state(p)['cut'],'Never entered silence; do not mislabel as bear timeout'
  event(p,'silence_entered')
  wait_state(p,lambda s:s['modal'] and p.locator('#choiceSacrifice').is_visible(),130,'actual_bear_sequence')
  shot(p,'02_bear_choice');click(p,'#choiceSacrifice')
  wait_state(p,lambda s:s['ending'],90,'actual_loss_sequence');p.wait_for_timeout(5500)
  s=event(p,'loss_ending_after_watchdog');shot(p,'03_loss_ending')
  assert not s['friend']['active'],'Lost friend resurrected';assert not s['errors']
  return {'home_arrived':True,'furniture_unchanged':True,'ui_save_reload_count':2,'ending':s,'method':'Unmodified recorded natural save; real joystick and E; no scene or clock injection'}
 finally:c.close()

def safe_ending_probe(b):
 c,p=setup(b)
 try:
  click(p,'#chapterStart');p.wait_for_timeout(500)
  # Explicit isolated checkpoint, NOT natural/fresh progression.
  p.evaluate("game.memory.loops=1;game.startDay2();game.storyPhase=5;game.clueLead=null")
  p.wait_for_timeout(1600);s=event(p,'day2_early_day3_entry');shot(p,'04_day2_entry_observed')
  R['observations'].append({'code':'D3_EARLY_ENTRY','observed':s['day3']['visible'],'detail':'Day3 entry shown before Day2 bear outcome; observation only, not silently fixed'});persist()
  p.evaluate('game.startBearEncounter()')
  wait_state(p,lambda s:s['modal'] and p.locator('#choiceThird').is_visible(),130,'safe_bear_choice');click(p,'#choiceThird')
  wait_state(p,lambda s:s['ending'],95,'safe_ending_sequence');p.wait_for_timeout(1600)
  s=event(p,'safe_ending_day3_entry');shot(p,'05_safe_ending')
  assert s['friend']['active'] and not s['errors']
  R['observations'].append({'code':'D3_SAFE_ENTRY_HIDDEN','observed':not s['day3']['visible'],'detail':'Day3 entry availability at earned safe ending'});persist()
  return {'friend_survives':True,'state':s,'method':'Seeded Day2 encounter; real choice click and full original ending animation'}
 finally:c.close()

def case(name,fn):
 t=time.monotonic()
 try:detail=fn();c={'name':name,'status':'PASS','detail':detail}
 except Exception as e:c={'name':name,'status':'FAIL_OR_INCOMPLETE','error':str(e),'trace':traceback.format_exc()}
 c['seconds']=round(time.monotonic()-t,1);R['cases'].append(c);persist();print('CASE '+json.dumps(c,ensure_ascii=False),flush=True)
server=subprocess.Popen([sys.executable,'-m','http.server','8776','--bind','127.0.0.1'],stdout=open(O/'server.log','w'),stderr=subprocess.STDOUT)
try:
 time.sleep(.8)
 with sync_playwright() as pw:
  b=pw.chromium.launch(headless=True,args=['--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
  case('Natural saved home journey through actual loss ending',lambda:home_to_ending(b))
  case('Safe ending and Day3 entry diagnostic',lambda:safe_ending_probe(b))
  b.close()
except Exception as e:R['fatal']=str(e);R['trace']=traceback.format_exc()
finally:
 server.terminate();persist()
 print('RESULT '+json.dumps({'cases':[{'name':c['name'],'status':c['status']} for c in R['cases']],'observations':R['observations'],'fatal':R.get('fatal')},ensure_ascii=False),flush=True)
 if R.get('fatal') or len(R['cases'])!=2 or any(c['status']!='PASS' for c in R['cases']):sys.exit(1)
