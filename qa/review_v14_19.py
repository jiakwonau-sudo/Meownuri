"""Read-only gameplay review. Original game files are never modified.
Natural UI interactions and injected chapter checkpoints are separately labelled.
"""
from pathlib import Path
import hashlib, json, math, subprocess, time, traceback, urllib.request
from playwright.sync_api import sync_playwright

OUT = Path('qa-results'); OUT.mkdir(exist_ok=True)
URL = 'http://127.0.0.1:8765/'
EXPECTED = '0269a3fde9f4c1dee0829abf4e8c19ff61b25701765d7e4fa1bcbfc893605161'
results = {'source_sha256': hashlib.sha256(Path('index.html').read_bytes()).hexdigest(), 'cases': [], 'frames': []}
assert results['source_sha256'] == EXPECTED, 'Source differs from uploaded v14.19'
server = subprocess.Popen(['python', '-m', 'http.server', '8765', '--bind', '127.0.0.1'], stdout=open(OUT/'server.log','w'), stderr=subprocess.STDOUT)
time.sleep(1)

def persist():
    (OUT/'results.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')

def state(p):
    return p.evaluate('''() => {const g=window.game;if(!g)return {game:false};return {
    game:true,title:document.title,h1:document.querySelector('h1')?.textContent,
    mode:g.mode,stage:g.stage,day:g.dayNumber,phase:g.storyPhase,
    cut:g.cut?{kind:g.cut.kind,scene:g.cut.scene,phase:g.cut.phase,time:g.cut.time}:null,
    player:{x:g.player.x,y:g.player.y,z:g.player.z},friend:{x:g.friend.x,z:g.friend.z,active:g.friend.active,visible:g.friend.mesh.visible},
    homeVisible:g.box.mesh.visible,ending:g.ending,bearStarted:g.bearStarted,
    homeJourney:!!g.homeJourney,homeReady:g.homeReady,bondJourney:g.bondJourney?{phase:g.bondJourney.phase}:null,
    sunsetJourney:!!g.sunsetJourney,sunsetReady:g.sunsetReady,
    quest:document.querySelector('#questText')?.textContent,detail:document.querySelector('#questDetail')?.textContent,
    action:document.querySelector('#action')?.textContent,
    modal:document.querySelector('#modal')?.hidden?null:document.querySelector('#modalBody')?.innerText,
    labels:g.labels.length,visibleLabels:Array.from(document.querySelectorAll('#worldLabels .label')).filter(x=>!x.hidden).map(x=>({text:x.textContent,x:x.getBoundingClientRect().x,y:x.getBoundingClientRect().y,w:x.getBoundingClientRect().width,h:x.getBoundingClientRect().height})),
    text:document.body.innerText,errors:window.__reviewErrors||[],
    storageKeys:Object.keys(localStorage),snapshot:g.snapshot(),
    beats:Array.from(document.querySelectorAll('.ag-beat')).map(x=>x.innerText)
    }}''')

def shot(p,name,label):
    p.screenshot(path=str(OUT/(name+'.png')),timeout=20000)
    s=state(p);s.update(name=name,method=label);results['frames'].append(s);persist();return s

def case(name,fn):
    try:
        detail=fn();results['cases'].append({'name':name,'status':'PASS','detail':detail})
    except Exception as e:
        results['cases'].append({'name':name,'status':'FAIL','error':str(e),'trace':traceback.format_exc()[-3000:]})
    persist()

def setup(c):
    p=c.new_page();p.set_default_timeout(15000)
    p.add_init_script("window.__reviewErrors=[];addEventListener('error',e=>__reviewErrors.push(e.message));addEventListener('unhandledrejection',e=>__reviewErrors.push(String(e.reason)));")
    p.goto(URL,wait_until='load');p.wait_for_function('!!window.game && !!window.__meowAgency && !!window.__meowBGM');p.wait_for_timeout(1000)
    return p

def walk(p,target,stop=2.7,seconds=25):
    end=time.monotonic()+seconds;held=set();lastjump=0;initial=None
    try:
        while time.monotonic()<end:
            s=p.evaluate('({x:game.player.x,z:game.player.z,yaw:game.yaw,lock:game.storyLock,cut:!!game.cut})')
            if initial is None:initial=s
            dx,dz=target['x']-s['x'],target['z']-s['z']
            if math.hypot(dx,dz)<stop:return {'arrived':True,'start':initial,'end':s}
            if s['cut'] or s['lock']:break
            # Route selection reads world geometry; motion uses real keyboard input only.
            route=p.evaluate('(q)=>game.ground.path(game.player,q,game.player.radius)',target)
            q=next((q for q in route if math.hypot(q['x']-s['x'],q['z']-s['z'])>.8),target)
            dx,dz=q['x']-s['x'],q['z']-s['z'];dist=max(.001,math.hypot(dx,dz))
            f=(math.sin(s['yaw'])*dx+math.cos(s['yaw'])*dz)/dist
            r=(-math.cos(s['yaw'])*dx+math.sin(s['yaw'])*dz)/dist
            keys={'Shift'}
            if abs(f)>.28:keys.add('w' if f>0 else 's')
            if abs(r)>.28:keys.add('d' if r>0 else 'a')
            for k in held-keys:p.keyboard.up(k)
            for k in keys-held:p.keyboard.down(k)
            held=keys
            if time.monotonic()-lastjump>1.05:p.keyboard.press('Space');lastjump=time.monotonic()
            p.wait_for_timeout(180)
        return {'arrived':False,'state':state(p)}
    finally:
        for k in held:p.keyboard.up(k)

def isolated_checkpoint(p):
    # Test-only checkpoint. Not represented as a natural Day 1-to-Day 2 playthrough.
    p.locator('#chapterStart').click();p.wait_for_timeout(400)
    p.evaluate('game.startDay2()');p.wait_for_timeout(1300)
    p.evaluate('game.storyPhase=5;game.clueLead=null;game.clueLeadReady=true;game.startBearEncounter()')

try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=['--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
        desktop=browser.new_context(viewport={'width':1280,'height':800},device_scale_factor=1)
        p=setup(desktop)
        case('desktop title and WebGL boot',lambda:shot(p,'01_desktop_title','natural UI'))
        def intro():
            p.locator('#introStart').click();p.wait_for_timeout(8500)
            a=state(p)['player'];p.keyboard.down('w');p.keyboard.press('Space');p.wait_for_timeout(1600);p.keyboard.up('w');b=state(p)['player']
            assert math.hypot(a['x']-b['x'],a['z']-b['z'])>.2,'Keyboard movement did not change position'
            shot(p,'02_intro_movement','natural keyboard and jump')
            target=p.evaluate('({x:game.storyWorld.finalScrap.position.x,z:game.storyWorld.finalScrap.position.z})')
            route=walk(p,target,2.8,35)
            if route['arrived']:
                p.keyboard.press('e');p.wait_for_timeout(4000)
            shot(p,'03_intro_trail','natural keyboard route; no teleport')
            return {'movement_from':a,'movement_to':b,'route':route}
        case('fresh start, keyboard movement, paper-trail approach',intro)
        p.close()
        q=setup(desktop)
        def gift():
            q.locator('#chapterStart').click();q.wait_for_timeout(600)
            route=walk(q,q.evaluate('({x:game.friend.x,z:game.friend.z})'),2.6,12)
            q.keyboard.press('e');q.wait_for_timeout(1700);shot(q,'04_gift_early','built-in highlight entry plus natural input')
            q.wait_for_timeout(3300);shot(q,'05_gift_dialogue','actual animated gift scene')
            q.wait_for_function('game.storyPhase===1 && !game.cut',timeout=40000)
            q.wait_for_timeout(8500);shot(q,'06_kkami_waiting','natural NPC home journey; player intentionally waits')
            return {'route':route,'state':state(q)}
        case('gift exchange and Kkami waiting',gift)
        def save_restore():
            before=state(q);q.evaluate('game.save()');q.reload(wait_until='load');q.wait_for_function('!!window.game && !!window.__meowAgency');q.wait_for_timeout(800)
            q.locator('#continueBtn').click();q.wait_for_timeout(1600)
            after=shot(q,'07_restored_day1','normal save, page reload and Continue button')
            return {'before':before,'after':after,'home_journey_preserved':before['homeJourney']==after['homeJourney']}
        case('Day 1 save/continue state comparison',save_restore)
        q.close()
        for outcome,button in [('sacrifice','#choiceSacrifice'),('resist','#choiceResist'),('third','#choiceThird')]:
            def ending(outcome=outcome,button=button):
                c=browser.new_context(viewport={'width':1280,'height':800})
                r=setup(c)
                if outcome=='third':r.evaluate('game.memory.loops=1')
                isolated_checkpoint(r)
                r.wait_for_timeout(3000);shot(r,'08_'+outcome+'_bear','injected Day 2 checkpoint; actual encounter renderer')
                r.wait_for_selector('#choiceSacrifice',state='visible',timeout=70000)
                shot(r,'09_'+outcome+'_choice','actual choice UI; checkpoint-seeded encounter')
                r.locator(button).click()
                if outcome=='third':
                    for i in range(4):
                        r.wait_for_timeout(3000);shot(r,'10_third_plan_'+str(i),'actual third-route recall; loop count seeded')
                r.wait_for_function('game.ending',timeout=65000)
                immediate=state(r);shot(r,'11_'+outcome+'_ending','actual ending after UI selection')
                r.wait_for_timeout(3500);after=shot(r,'12_'+outcome+'_after_watchdog','post-ending state after watchdog interval')
                c.close()
                return {'immediate':immediate,'after_3500ms':after,'friend_should_survive':outcome=='third','friend_active_after':after['friend']['active']}
            case('Day 2 outcome: '+outcome,ending)
        def mobile():
            c=browser.new_context(viewport={'width':390,'height':844},device_scale_factor=1,is_mobile=True,has_touch=True)
            m=setup(c);shot(m,'13_mobile_title','mobile viewport emulation; not physical phone')
            m.locator('#chapterStart').tap();m.wait_for_timeout(1000)
            shot(m,'14_mobile_highlight','mobile viewport emulation')
            before=state(m)['player'];box=m.locator('#joystick').bounding_box()
            m.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2);m.mouse.down();m.mouse.move(box['x']+box['width']/2,box['y']+10);m.wait_for_timeout(1300);m.mouse.up()
            m.locator('#jump').tap();m.wait_for_timeout(200);after=shot(m,'15_mobile_controls','pointer joystick plus touch jump in mobile emulation')
            c.close();return {'before':before,'after':after}
        case('mobile portrait rendering and controls',mobile)
        def live():
            with urllib.request.urlopen('https://jiakwonau-sudo.github.io/Meownuri/',timeout=30) as res:
                data=res.read();status=res.status
            digest=hashlib.sha256(data).hexdigest();assert digest==EXPECTED,'Live Pages differs from archive'
            c=browser.new_context(viewport={'width':1280,'height':800});r=c.new_page();r.goto('https://jiakwonau-sudo.github.io/Meownuri/',wait_until='load');r.wait_for_function('!!window.game');r.wait_for_timeout(1200)
            shot(r,'16_live_pages','existing public HTTPS deployment; no new deployment')
            c.close();return {'http':status,'sha256':digest,'url':'https://jiakwonau-sudo.github.io/Meownuri/'}
        case('existing public hosting matches uploaded source',live)
        browser.close()
except Exception as e:
    results['fatal']=str(e);results['fatal_trace']=traceback.format_exc()
finally:
    server.terminate();persist();print(json.dumps({'cases':[{k:v for k,v in x.items() if k!='detail'} for x in results['cases']],'frames':len(results['frames']),'fatal':results.get('fatal')},ensure_ascii=False))
if results.get('fatal'):raise SystemExit(1)
