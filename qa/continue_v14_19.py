"""Continuation QA: fresh UI progression and checkpoint tests labelled separately.
No teleport, progression injection or clock acceleration in the fresh run.
Geometry is read for navigation; movement/actions use real input events.
On-demand original rendering avoids software-GPU saturation. No FPS claim.
"""
from pathlib import Path
import hashlib,json,math,subprocess,time,traceback,sys
from playwright.sync_api import sync_playwright
from apply_v14_19_r1 import build,EXPECTED
O=Path('qa-continuation');O.mkdir(exist_ok=True)
M=build(Path('index.html'),O/'candidate_r1')
R={'manifest':M,'rendering':'original renderer on demand; unmodified game tick, timing, shaders','cases':[],'milestones':[],'frames':[]}
INIT="""window.__qaErrors=[];addEventListener('error',e=>__qaErrors.push(e.message));addEventListener('unhandledrejection',e=>__qaErrors.push(String(e.reason)));Object.defineProperty(window,'__MEOWNURI9',{configurable:true,get(){return window.__qaGame},set(g){window.__qaGame=g;const draw=g.renderer.render.bind(g.renderer);g.renderer.render=()=>{};window.__qaDraw=()=>{g.updateUI();g.updateLabels();draw(g.scene,g.camera);return {...g.renderer.info.render}};}});"""
STATE="""()=>{let g=game;return {stage:g.stage,phase:g.storyPhase,day:g.dayNumber,mode:g.mode,ending:g.ending,cut:g.cut?{kind:g.cut.kind,scene:g.cut.scene,time:g.cut.time}:null,locked:g.storyLock,rest:g.homeResting,found:g.boxFound,meet:g.friendMeetPhase,bond:g.bondJourney?.phase,homeJourney:!!g.homeJourney,homeReady:g.homeReady,sunsetJourney:!!g.sunsetJourney,sunsetReady:g.sunsetReady,clueLead:g.clueLead?.kind,clueReady:g.clueLeadReady,player:{x:g.player.x,y:g.player.y,z:g.player.z},friend:{x:g.friend.x,z:g.friend.z,active:g.friend.active},bag:g.bag,placement:g.placement,action:g.action?{text:g.action.text,enabled:g.action.enabled}:null,quest:document.querySelector('#questText')?.textContent,modal:!document.querySelector('#modal').hidden,modalText:document.querySelector('#modalBody').innerText,errors:__qaErrors}}"""
server=subprocess.Popen(['python','-m','http.server','8776','--bind','127.0.0.1'],stdout=open(O/'server.log','w'),stderr=subprocess.STDOUT)
def persist(): (O/'results.json').write_text(json.dumps(R,ensure_ascii=False,indent=2))
def state(p):return p.evaluate(STATE)
def shot(p,name,method):
 p.evaluate('__qaDraw()');p.screenshot(path=str(O/(name+'.png')),timeout=40000)
 s=state(p);R['frames'].append({'name':name,'method':method,'state':s});persist();return s

def case(name,method,fn):
 t=time.time()
 try:d=fn();R['cases'].append({'name':name,'method':method,'status':'PASS','seconds':round(time.time()-t,1),'detail':d})
 except Exception as e:R['cases'].append({'name':name,'method':method,'status':'FAIL_OR_INCOMPLETE','seconds':round(time.time()-t,1),'error':str(e),'trace':traceback.format_exc()[-1800:]})
 print(json.dumps(R['cases'][-1],ensure_ascii=False),flush=True);persist()

def setup(b,candidate=True,mobile=False):
 c=b.new_context(viewport={'width':390 if mobile else 1280,'height':844 if mobile else 800},is_mobile=mobile,has_touch=mobile,device_scale_factor=1)
 c.add_init_script(INIT);p=c.new_page();p.set_default_timeout(15000)
 p.goto('http://127.0.0.1:8776/'+('qa-continuation/candidate_r1/' if candidate else ''),wait_until='load')
 p.wait_for_function('!!window.game && !!window.__meowAgency');p.wait_for_timeout(700);return c,p

def reload_ui(p):
 if not p.locator('#menuBtn').is_visible():p.locator('[data-hud-toggle="utilityPanel"]').click()
 p.locator('#menuBtn').click();p.locator('#saveNow').click()
 before=p.evaluate('game.snapshot()');p.reload(wait_until='load');p.wait_for_function('!!window.game && !!window.__meowAgency');p.wait_for_timeout(500)
 p.locator('#continueBtn').click();p.wait_for_timeout(350);return before,state(p)

def move_step(p,goal,stop=2.1):
 d=p.evaluate("""({goal,stop})=>{let g=game,a=g.player,t=goal;let d=Math.hypot(a.x-t.x,a.z-t.z);if(d<=stop)return {done:true};let actors=g.otherActors(a);let end=g.ground.nearest(t.x,t.z,a.radius+.03,actors);if(!end)return {blocked:true};let path=g.ground.path(a,end,a.radius+.03,actors);let w=path.find(q=>Math.hypot(q.x-a.x,q.z-a.z)>.38)||end;return {d,dx:w.x-a.x,dz:w.z-a.z,yaw:g.yaw,noPath:!path.length,jump:g.ground.height(w.x,w.z)>a.y+.08};}""",{'goal':goal,'stop':stop})
 if d.get('done'):p.wait_for_timeout(120);return True
 if d.get('blocked'):p.wait_for_timeout(150);return False
 f=math.sin(d['yaw'])*d['dx']+math.cos(d['yaw'])*d['dz'];r=-math.cos(d['yaw'])*d['dx']+math.sin(d['yaw'])*d['dz'];m=math.hypot(f,r) or 1
 keys=[]
 if abs(f)/m>.28:keys.append('w' if f>0 else 's')
 if abs(r)/m>.28:keys.append('d' if r>0 else 'a')
 for k in keys:p.keyboard.down(k)
 if d.get('jump'):p.keyboard.press('Space')
 p.wait_for_timeout(140)
 for k in keys:p.keyboard.up(k)
 return False

def target(p,expr):return p.evaluate('()=>{const g=game;const q='+expr+';return {x:q.x,z:q.z}}')
def approach_friend(p,stop):return move_step(p,target(p,'g.friend'),stop)

def baseline(b,candidate):
 c,p=setup(b,candidate)
 try:
  p.locator('#chapterStart').click();p.wait_for_timeout(400)
  p.evaluate('game.storyPhase=1;game.prepareHomeJourney()')
  before,after=reload_ui(p)
  assert bool(before.get('agencyProgress',{}).get('homeJourney'))==candidate
  assert after['homeJourney']==candidate,after
  if candidate:
   p.wait_for_timeout(450);before2,after2=reload_ui(p)
   assert before2['quest']['text']==before['quest']['text'],'Quest cache regressed on repeated save'
  shot(p,('r1' if candidate else 'original')+'_restore','injected home-journey checkpoint; UI save/reload')
  p.evaluate("game.dayNumber=2;game.storyPhase=5;game.friend.active=false;game.friend.mesh.visible=false;game.showEnding('sacrifice')")
  p.wait_for_timeout(5200);a=shot(p,('r1' if candidate else 'original')+'_ending_watchdog','injected terminal checkpoint; original watchdog timer runs normally')
  assert a['friend']['active']==(not candidate),a
  return {'home_journey_restored':after['homeJourney'],'friend_active_after_loss':a['friend']['active'],'errors':a['errors']}
 finally:c.close()

def continuous(b):
 c,p=setup(b,True);seen=set();restored=set();t0=time.time();last=None;last_change=time.time();ring=0
 try:
  shot(p,'fresh_00_title','candidate r1; fresh empty browser storage')
  p.locator('#introStart').click()
  while time.time()-t0<720:
   s=state(p)
   if s['errors']:raise AssertionError('Runtime errors: '+str(s['errors']))
   sig=(s['day'],s['stage'],s['phase'],s.get('meet'),s.get('bond'),s.get('homeReady'),s.get('sunsetReady'),s.get('clueReady'),s['cut']['kind'] if s['cut'] else None,s['cut'].get('scene') if s['cut'] else None)
   if sig!=last:
    last=sig;last_change=time.time();R['milestones'].append({'elapsed':round(time.time()-t0,1),'state':s});persist();print('PROGRESS '+json.dumps({'seconds':round(time.time()-t0,1),'sig':sig,'quest':s['quest']},ensure_ascii=False),flush=True)
   photo=(s['day'],s['stage'],s['phase'],s['cut'].get('scene') if s['cut'] else None)
   if photo not in seen and len(seen)<24:
    seen.add(photo);shot(p,'fresh_%02d'%len(seen),'fresh start, keyboard/pointer progression; no checkpoints, teleports or clock acceleration')
   if s['ending']:
    p.wait_for_timeout(5200);end=shot(p,'fresh_ending','continuous fresh game to actual choice outcome and watchdog interval')
    assert not end['friend']['active'],'Friend resurrected after sacrifice'
    return {'completed':True,'seconds':round(time.time()-t0,1),'ending':end,'ui_save_reload_stages':sorted(restored)}
   if s['modal']:
    handled=False
    for sel in ['#choiceSacrifice','#agGo','[data-ag="0"]']:
     if p.locator(sel).is_visible():p.locator(sel).click();handled=True;break
    if not handled:raise AssertionError('Unhandled modal '+s['modalText'][:300])
    p.wait_for_timeout(200);continue
   if s['cut']:p.wait_for_timeout(250);continue
   if s['rest']:p.keyboard.press('e');p.wait_for_timeout(200);continue
   if s['locked']:p.wait_for_timeout(200);continue
   a=s['action'] or {};text=a.get('text','')
   if s['stage']==0:
    if text and ('조사' in text or '첫 집' in text):p.keyboard.press('e')
    else:move_step(p,target(p,'({x:g.box.x-2.9,z:g.box.z-2.9})'),1.4)
   elif s['stage']==1:
    if '줍기' in text:p.keyboard.press('e')
    else:
     goal=p.evaluate("()=>{let g=game;let n=g.gather.filter(n=>n.active).sort((a,b)=>g.dist(a)-g.dist(b))[0];return n?{x:n.x,z:n.z}:null}")
     if not goal:raise AssertionError('No remaining gathering target')
     move_step(p,goal,1.8)
   elif s['stage'] in (2,4):
    if '만들기' in text:p.keyboard.press('e')
    else:move_step(p,target(p,'({x:g.box.x+3.5,z:g.box.z+3.5})'),1.0)
   elif s['stage'] in (3,5):
    if a.get('enabled') and '여기 놓기' in text:p.keyboard.press('e')
    else:
     ang=ring*.65;goal=target(p,'({x:g.box.x+Math.sin('+str(ang)+')*3.8,z:g.box.z+Math.cos('+str(ang)+')*3.8})')
     if move_step(p,goal,.65):ring+=1
   elif s['stage']==6:
    dist=math.hypot(s['player']['x']-s['friend']['x'],s['player']['z']-s['friend']['z'])
    if s['meet']==0:approach_friend(p,6.8)
    elif s['meet']==1 or dist<5.0:
     dx=s['player']['x']-s['friend']['x'];dz=s['player']['z']-s['friend']['z'];m=math.hypot(dx,dz) or 1
     move_step(p,{'x':s['friend']['x']+dx/m*13,'z':s['friend']['z']+dz/m*13},.7)
    elif dist>7.5:approach_friend(p,6.5)
    else:p.wait_for_timeout(180)
   elif s['stage']==7:
    ph=s['phase']
    if ph==0:
     if s.get('bond') in (1,3):
      if '물고기' in text:p.keyboard.press('e')
      else:approach_friend(p,2.5)
     else:approach_friend(p,6.0)
    elif ph==1:
     if 'home' not in restored and s['homeJourney']:
      before,after=reload_ui(p);assert after['homeJourney'],'Home journey lost';restored.add('home');continue
     if s['homeReady']:
      if '표지판' in text:p.keyboard.press('e')
      else:move_step(p,target(p,'({x:g.box.x+3,z:g.box.z+3})'),.7)
     else:approach_friend(p,5.6)
    elif ph==2:
     if 'sunset' not in restored and s['sunsetJourney'] and not s['sunsetReady']:
      before,after=reload_ui(p);assert after['sunsetJourney'],'Sunset journey lost';restored.add('sunset');continue
     if s['sunsetReady']:
      if '나란히' in text:p.keyboard.press('e')
      else:approach_friend(p,2.6)
     else:approach_friend(p,5.8)
    elif ph==3:
     if '발톱' in text:p.keyboard.press('e')
     else:move_step(p,target(p,'g.clawClue'),2.8)
    elif ph==4:
     if s['clueReady']:
      if '더미' in text:p.keyboard.press('e')
      else:move_step(p,target(p,'g.fishClue'),3.0)
     else:approach_friend(p,5.5)
    elif ph==5:
     if s['clueReady']:
      if '주변 듣기' in text:p.keyboard.press('e')
      else:move_step(p,target(p,'({x:g.box.x+3,z:g.box.z+3})'),.7)
     else:approach_friend(p,5.5)
   if time.time()-last_change>100:
    shot(p,'fresh_stalled','fresh run stopped by progress/driver stall; not claimed complete')
    raise AssertionError('No stage transition for 100s: '+json.dumps(s,ensure_ascii=False))
  shot(p,'fresh_deadline','continuous run deadline; incomplete, not success')
  raise TimeoutError('Continuous progression deadline. Last state '+json.dumps(state(p),ensure_ascii=False))
 finally:
  (O/'fresh_final_state.json').write_text(json.dumps(state(p),ensure_ascii=False,indent=2));c.close()

def ending_animation(b,outcome):
 c,p=setup(b,True)
 try:
  p.locator('#chapterStart').click();p.wait_for_timeout(300)
  p.evaluate("game.memory.loops=1;game.startDay2();game.storyPhase=5;game.clueLead=null;game.startBearEncounter()")
  p.locator('#choiceSacrifice').wait_for(state='visible',timeout=90000)
  p.locator({'sacrifice':'#choiceSacrifice','resist':'#choiceResist','third':'#choiceThird'}[outcome]).click()
  p.wait_for_function('game.ending',timeout=90000);p.wait_for_timeout(5200)
  s=shot(p,'r1_animated_'+outcome,'injected Day2 encounter checkpoint; real choice UI and full outcome animation')
  assert s['friend']['active']==(outcome=='third'),s
  assert not s['errors'],s['errors'];return s
 finally:c.close()

def mobile(b):
 c,p=setup(b,True,True)
 try:
  p.locator('#introStart').tap();p.wait_for_timeout(1800);a=state(p)['player']
  r=p.locator('#joystick').bounding_box();p.mouse.move(r['x']+r['width']/2,r['y']+r['height']/2);p.mouse.down();p.mouse.move(r['x']+r['width']/2,r['y']+8);p.wait_for_timeout(700);p.mouse.up()
  p.locator('#jump').tap();p.wait_for_timeout(180);s=shot(p,'r1_mobile','390x844 pointer/touch emulation; no physical-device FPS claim')
  assert math.hypot(a['x']-s['player']['x'],a['z']-s['player']['z'])>.1
  assert not s['errors'];return s
 finally:c.close()
try:
 time.sleep(1)
 with sync_playwright() as pw:
  b=pw.chromium.launch(headless=True,args=['--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
  case('original two defects reproduced','checkpoint injection + UI reload and original timer',lambda:baseline(b,False))
  case('candidate two defects corrected','same checkpoints and timing; repeated save/reload',lambda:baseline(b,True))
  case('fresh start through Day2 loss ending','continuous keyboard/pointer gameplay with two real save/reload interruptions; no checkpoint or teleport',lambda:continuous(b))
  for result in ('resist','third'):case('full outcome animation '+result,'explicitly seeded Day2 encounter, actual choice UI',lambda result=result:ending_animation(b,result))
  case('mobile controls','emulated mobile; not physical Android',lambda:mobile(b))
  b.close()
except Exception as e:R['fatal']=str(e);R['trace']=traceback.format_exc()
finally:
 server.terminate();persist();summary=[{k:v for k,v in c.items() if k not in ('detail','trace')} for c in R['cases']]
 print('FINAL '+json.dumps({'cases':summary,'fatal':R.get('fatal'),'frames':len(R['frames'])},ensure_ascii=False),flush=True)
 if R.get('fatal') or any(c['status']!='PASS' for c in R['cases']):sys.exit(1)
