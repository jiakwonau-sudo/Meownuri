"""Review original game with renderer instrumentation, not game logic changes.
On-demand drawing avoids continuous software-GPU saturation. Original tick,
input, timers, shaders, lighting and scene objects remain unchanged. No FPS claim.
Natural UI play and injected chapter checkpoints are labelled separately.
"""
from pathlib import Path
import hashlib,json,math,subprocess,time,traceback,urllib.request
from playwright.sync_api import sync_playwright
O=Path('qa-focused');O.mkdir(exist_ok=True)
E='0269a3fde9f4c1dee0829abf4e8c19ff61b25701765d7e4fa1bcbfc893605161'
R={'source_sha256':hashlib.sha256(Path('index.html').read_bytes()).hexdigest(),'rendering':'on-demand original renderer; original game tick and timers remain active','cases':[],'frames':[]}
assert R['source_sha256']==E
server=subprocess.Popen(['python','-m','http.server','8775','--bind','127.0.0.1'],stdout=open(O/'server.log','w'),stderr=subprocess.STDOUT);time.sleep(.5)
INIT="""window.__qaErrors=[];addEventListener('error',e=>__qaErrors.push(e.message));addEventListener('unhandledrejection',e=>__qaErrors.push(String(e.reason)));Object.defineProperty(window,'__MEOWNURI9',{configurable:true,get(){return window.__qaGame},set(g){window.__qaGame=g;const draw=g.renderer.render.bind(g.renderer);g.renderer.render=()=>{};window.__qaDraw=()=>{g.updateUI();g.updateLabels();draw(g.scene,g.camera);return {...g.renderer.info.render}};}});"""
def save(): (O/'results.json').write_text(json.dumps(R,ensure_ascii=False,indent=2))
def state(p):
 return p.evaluate("""()=>{const g=game;return {title:document.title,h1:document.querySelector('h1')?.textContent,mode:g.mode,day:g.dayNumber,phase:g.storyPhase,cut:g.cut?{kind:g.cut.kind,scene:g.cut.scene,phase:g.cut.phase,time:g.cut.time}:null,ending:g.ending,homeJourney:!!g.homeJourney,homeReady:g.homeReady,sunsetJourney:!!g.sunsetJourney,bondJourney:g.bondJourney?.phase,player:{x:g.player.x,y:g.player.y,z:g.player.z},friend:{x:g.friend.x,z:g.friend.z,active:g.friend.active,visible:g.friend.mesh.visible},labels:g.labels.length,quest:document.querySelector('#questText')?.textContent,detail:document.querySelector('#questDetail')?.textContent,modal:document.querySelector('#modal').hidden?null:document.querySelector('#modalBody').innerText,subtitle:document.querySelector('#cinemaSubtitle').innerText,visibleLabels:Array.from(document.querySelectorAll('#worldLabels .label')).filter(x=>!x.hidden).map(x=>({text:x.textContent,x:x.getBoundingClientRect().x,y:x.getBoundingClientRect().y,w:x.getBoundingClientRect().width,h:x.getBoundingClientRect().height})),text:document.body.innerText,snapshot:g.snapshot(),errors:__qaErrors}}""")
def shot(p,name,method):
 info=p.evaluate('__qaDraw()');p.screenshot(path=str(O/(name+'.png')),timeout=45000);s=state(p);s.update(name=name,method=method,draw=info);R['frames'].append(s);save();return s

def setup(browser,mobile=False,url='http://127.0.0.1:8775/'):
 c=browser.new_context(viewport={'width':390 if mobile else 1280,'height':844 if mobile else 800},is_mobile=mobile,has_touch=mobile,device_scale_factor=1)
 c.add_init_script(INIT);p=c.new_page();p.set_default_timeout(25000);p.goto(url,wait_until='load');p.wait_for_function('!!window.game && !!window.__meowAgency');p.wait_for_timeout(800);return c,p

def case(name,fn):
 try:R['cases'].append({'name':name,'status':'EXECUTED','detail':fn()})
 except Exception as e:R['cases'].append({'name':name,'status':'INCOMPLETE','error':str(e),'trace':traceback.format_exc()[-2000:]})
 save()

def near_friend(p):
 for _ in range(20):
  s=p.evaluate('({d:game.dist(game.friend),x:game.friend.x-game.player.x,z:game.friend.z-game.player.z,yaw:game.yaw})')
  if s['d']<3.1:return True
  f=math.sin(s['yaw'])*s['x']+math.cos(s['yaw'])*s['z'];r=-math.cos(s['yaw'])*s['x']+math.sin(s['yaw'])*s['z']
  key=('w' if f>0 else 's') if abs(f)>=abs(r) else ('d' if r>0 else 'a')
  p.keyboard.down(key);p.wait_for_timeout(120);p.keyboard.up(key)
 return False

try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(headless=True,args=['--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
  def natural():
   c,p=setup(b)
   try:
    shot(p,'01_title','original title, original rendering on demand')
    p.locator('#introStart').click();p.wait_for_timeout(8300);a=state(p)['player'];p.keyboard.down('w');p.keyboard.press('Space');p.wait_for_timeout(1500);p.keyboard.up('w');z=state(p)['player'];shot(p,'02_fresh_movement','fresh start; physical keyboard input, no state injection')
    return {'moved':math.hypot(a['x']-z['x'],a['z']-z['z'])>.2,'before':a,'after':z}
   finally:c.close()
  case('fresh start and keyboard movement',natural)
  def gift_wait_restore():
   c,p=setup(b)
   try:
    p.locator('#chapterStart').click();p.wait_for_timeout(800);assert near_friend(p),'Did not approach friend';p.keyboard.press('e');p.locator('[data-ag="0"]').wait_for(state='visible');shot(p,'03_gift_choice','built-in highlight plus natural approach and E')
    p.locator('[data-ag="0"]').click();p.wait_for_function('game.cut?.scene==="bond"');p.wait_for_timeout(2200);shot(p,'04_gift_exchange','natural choice button; original cutscene and all original text')
    p.wait_for_timeout(3500);shot(p,'05_gift_response','same original cutscene, later moment')
    p.wait_for_function('game.storyPhase===1 && !game.cut',timeout=60000);p.wait_for_timeout(10500);shot(p,'06_home_waiting','original home journey; player waits rather than follows')
    before=state(p);p.evaluate('game.save()');p.reload(wait_until='load');p.wait_for_function('!!window.game');p.wait_for_timeout(800);p.locator('#continueBtn').click();p.wait_for_timeout(4200);after=shot(p,'07_home_reload','normal Save and Continue UI; no state injection')
    return {'before':before,'after':after,'journey_lost':before['homeJourney'] and not after['homeJourney'],'quest_preserved':before['quest']==after['quest']}
   finally:c.close()
  case('gift, waiting and save restoration',gift_wait_restore)
  def sunset_wait():
   c,p=setup(b)
   try:
    p.locator('#chapterStart').click();p.wait_for_timeout(600)
    p.evaluate('game.storyPhase=2;game.prepareSunsetJourney()')
    p.wait_for_timeout(12500);shot(p,'08_sunset_waiting','injected start-of-sunset-journey checkpoint; original waiting behavior')
    p.wait_for_function('Array.from(document.querySelectorAll(".ag-balloon")).some(x=>!x.hidden&&x.textContent.includes("이쪽"))',timeout=20000)
    before=shot(p,'09_sunset_call','same checkpoint; original call speech and emoji coexist')
    p.wait_for_timeout(15000);after=state(p)
    return {'before':before,'after':after,'label_growth':after['labels']-before['labels']}
   finally:c.close()
  case('sunset waiting speech and label retention',sunset_wait)
  for outcome,button in [('sacrifice','#choiceSacrifice'),('resist','#choiceResist'),('third','#choiceThird')]:
   def ending(outcome=outcome,button=button):
    c,p=setup(b)
    try:
     p.locator('#chapterStart').click();p.wait_for_timeout(500)
     if outcome=='third':p.evaluate('game.memory.loops=1')
     p.evaluate('game.startDay2()');p.wait_for_timeout(1100);p.evaluate('game.storyPhase=5;game.clueLead=null;game.startBearEncounter()')
     p.wait_for_selector('#choiceSacrifice',state='visible',timeout=75000);shot(p,'10_'+outcome+'_choice','injected Day 2 checkpoint; original encounter and choice UI')
     p.locator(button).click();p.wait_for_function('game.ending',timeout=80000);before=state(p);shot(p,'11_'+outcome+'_ending','original outcome animation after choice; chapter checkpoint seeded')
     p.wait_for_timeout(5000);after=shot(p,'12_'+outcome+'_watchdog','same ending after >= one 4-second watchdog interval')
     return {'before':before,'after':after,'friend_should_live':outcome=='third','friend_actually_active':after['friend']['active']}
    finally:c.close()
   case('ending '+outcome,ending)
  def mobile():
   c,p=setup(b,True)
   try:
    shot(p,'13_mobile_title','390x844 mobile emulation; not physical Android')
    p.locator('#chapterStart').tap();p.wait_for_timeout(1200);shot(p,'14_mobile_world','built-in highlight; mobile emulation')
    a=state(p)['player'];r=p.locator('#joystick').bounding_box();p.mouse.move(r['x']+r['width']/2,r['y']+r['height']/2);p.mouse.down();p.mouse.move(r['x']+r['width']/2,r['y']+10);p.wait_for_timeout(1000);p.mouse.up();p.locator('#jump').tap();p.wait_for_timeout(250);z=shot(p,'15_mobile_controls','pointer joystick and touch jump, original game logic')
    return {'before':a,'after':z}
   finally:c.close()
  case('mobile emulation',mobile)
  def live():
   with urllib.request.urlopen('https://jiakwonau-sudo.github.io/Meownuri/',timeout=30) as u:raw=u.read();status=u.status
   d={'http':status,'sha256':hashlib.sha256(raw).hexdigest(),'matches_upload':hashlib.sha256(raw).hexdigest()==E};R['live_http']=d;save()
   c,p=setup(b,url='https://jiakwonau-sudo.github.io/Meownuri/')
   try:shot(p,'16_public_host','existing public HTTPS page with on-demand renderer instrumentation');return d
   finally:c.close()
  case('existing public hosting',live)
  b.close()
except Exception as e:R['fatal']=str(e);R['fatal_trace']=traceback.format_exc()
finally:server.terminate();save();print(json.dumps({'cases':[{k:v for k,v in x.items() if k!='detail'} for x in R['cases']],'frames':len(R['frames']),'live_http':R.get('live_http'),'fatal':R.get('fatal')},ensure_ascii=False))
