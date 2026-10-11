from pathlib import Path
from playwright.sync_api import sync_playwright,TimeoutError as PTimeout
import json,time
ROOT=Path('/mnt/data/work_20261011')
html=(ROOT/'MEOWNURI_SOL_v16.8_TAP_WOOD_BITE.html').read_text()
records=[]

def boot(browser,mobile=True):
  ctx=browser.new_context(viewport={'width':390 if mobile else 1120,'height':844 if mobile else 760},is_mobile=mobile,device_scale_factor=1,has_touch=mobile)
  p=ctx.new_page();errors=[]
  p.on('pageerror',lambda e:errors.append(str(e)))
  p.evaluate("""() => {let data={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>Object.prototype.hasOwnProperty.call(data,k)?data[k]:null,setItem:(k,v)=>data[k]=String(v),removeItem:k=>delete data[k],clear:()=>data={}}});}""")
  p.set_content(html,wait_until='domcontentloaded',timeout=22000)
  p.wait_for_function('window.game && window.MeownuriStory && window.__MEOWNURI_TAP_CONTROLLER__ && window.__MEOWNURI_TAP_CONTROLLER__.active !== undefined',timeout=10000)
  return ctx,p,errors

def record(case,ok,detail=''):
  records.append({'case':case,'ok':bool(ok),'detail':detail})
  print(('PASS' if ok else 'FAIL'),case,detail[:250],flush=True)
with sync_playwright() as q:
 browser=q.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 ctx,p,errors=boot(browser)
 record('Boot 390x844 2D fallback',p.evaluate('window.game.rendererMode')=='2d',str(p.title()))
 record('TAP init unique',p.evaluate("document.querySelectorAll('#solTapCinematic').length===1 && window.__MEOWNURI_TAP_CONTROLLER__.version==='SOL v16.8'"))
 p.locator('#solStartDay4').click()
 p.wait_for_timeout(500)
 record('Day4 start button',p.evaluate('window.MeownuriStory.getCurrent().day===4'),str(p.evaluate('window.MeownuriStory.getCurrent()')))
 # Real auto-walk UI through one waypoint
 p.locator('#solStoryAssist').click()
 try:p.wait_for_function("!document.querySelector('#solStoryAction').disabled",timeout=18000)
 except PTimeout:pass
 near=p.evaluate('''() => {const a=window.game.player,b=window.game.storyProject.target;return Math.hypot(a.x-b.x,a.z-b.z)}''')
 record('Auto-walk reaches first target',near<2.8,'distance %.2fm'%near)
 if near>=2.8:
  p.evaluate('''()=>{let g=window.game,q=g.storyProject.target;g.player.x=q.x;g.player.z=q.z;g.player.y=g.ground.height(q.x,q.z);g.player.mesh.position.set(q.x,g.player.y,q.z)}''')
 p.locator('#solStoryAction').click()
 record('Day4 first actual action click',p.evaluate('window.MeownuriStory.getCurrent().beat===1'),str(p.evaluate('window.MeownuriStory.getCurrent()')))
 p.screenshot(path=str(ROOT/'meow_v168_day4_mobile.png'))
 # Traverse remaining with real buttons and teleport to objective (not natural-play claim)
 seen=[]
 for day in range(4,11):
  for _ in range(15):
   st=p.evaluate('window.MeownuriStory.getCurrent()')
   if st['day']!=day or st['finished']:break
   p.evaluate('''()=>{let g=window.game,q=g.storyProject.target;g.player.x=q.x;g.player.z=q.z;g.player.y=g.ground.height(q.x,q.z);g.player.mesh.position.set(q.x,g.player.y,q.z)}''')
   p.wait_for_timeout(45)
   p.locator('#solStoryAction').click(force=True)
   if p.locator('#solStoryChoice').is_visible():
    opts=p.locator('.solChoiceItems button')
    idx=2 if day==9 else 0
    opts.nth(idx).click()
   seen.append(f'{day}:{st["beat"]}')
  st=p.evaluate('window.MeownuriStory.getCurrent()')
  record(f'Day{day} completion via UI',st['finished'] and st['day']==day, f'{len([x for x in seen if x.startswith(str(day)+":")])} beat clicks')
  if day!=10:
   try:p.locator('#solStoryNext').click(timeout=4000)
   except Exception as e:record('Next day click',False,str(e)[:100]);break
 st=p.evaluate('window.MeownuriStory.getCurrent()')
 record('Day10 ending Bridge path',st['day']==10 and st['finished'] and st['choices'].get('day9_kingdom_choice')==2,str(st))
 record('No pageerrors through Day10',len(errors)==0,str(errors[:5]))
 p.screenshot(path=str(ROOT/'meow_v168_day10_mobile.png'))
 ctx.close()
 # Actual gift cutscene manual tap smoke; isolate from day loop
 ctx,p,errors=boot(browser)
 prep=p.evaluate('''() => {let g=window.game;document.querySelector('#start').hidden=true;g.mode='play';g.stage=0;g.storyPhase=0;try{g.startStoryScene('bond');return {kind:g.cut?.kind,scene:g.cut?.scene,mode:g.mode,film:g.romanceFilm}}catch(e){return {error:String(e)}}}''')
 print('gift prep',prep)
 p.wait_for_timeout(380)
 active=p.evaluate('window.__MEOWNURI_TAP_CONTROLLER__.active')
 record('Gift cutscene TAP eligible',active,str(prep))
 prior=p.evaluate('window.game?.cut?.time||0')
 if active:
  p.locator('#solTapCinematic').click(position={'x':180,'y':300})
  p.wait_for_timeout(100)
  after=p.evaluate('window.game?.cut?.time||0')
  record('Tap advances story timer',after>prior+1,f'{prior:.2f} -> {after:.2f}')
  p.screenshot(path=str(ROOT/'meow_v168_gift_tap.png'))
  record('TAP no new pageerror',len(errors)==0,str(errors[:3]))
 ctx.close();browser.close()
(ROOT/'meownuri_v16.8_playwright_results.json').write_text(json.dumps({'tested_at':'2026-10-11','mode':'about:blank + set_content, Chromium 2D software fallback, mocked in-memory localStorage','results':records,'passed':sum(x['ok'] for x in records),'failed':sum(not x['ok'] for x in records)},ensure_ascii=False,indent=2)+'\n')
print('SUMMARY',len(records),sum(x['ok'] for x in records),'passed',sum(not x['ok'] for x in records),'failed')
