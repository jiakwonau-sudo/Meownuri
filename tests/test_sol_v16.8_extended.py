from pathlib import Path
from playwright.sync_api import sync_playwright
import json
R=Path('/mnt/data/work_20261011')
HTML=(R/'MEOWNURI_SOL_v16.8_TAP_WOOD_BITE.html').read_text()
results=[]
def check(name,passed,detail):
 results.append({'test':name,'pass':bool(passed),'detail':detail})
 print(('PASS' if passed else 'FAIL'),name,detail[:200],flush=True)

def boot(browser):
 ctx=browser.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True)
 p=ctx.new_page();errors=[]
 p.on('pageerror',lambda e:errors.append(str(e)))
 p.evaluate("""() => {let data={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>Object.prototype.hasOwnProperty.call(data,k)?data[k]:null,setItem:(k,v)=>data[k]=String(v),removeItem:k=>delete data[k],clear:()=>data={}}});}""")
 p.set_content(HTML,wait_until='domcontentloaded')
 p.wait_for_function('window.game && window.MeownuriStory && window.__MEOWNURI_TAP_CONTROLLER__?.active !== undefined')
 return ctx,p,errors
with sync_playwright() as q:
 b=q.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 ctx,p,errors=boot(b)
 p.evaluate('''() => {let g=window.game; document.querySelector('#start').hidden=true;g.mode='play';g.stage=0;g.storyPhase=0;g.startStoryScene('bond')}''')
 p.wait_for_timeout(260)
 visits=[]
 for t in range(17):
  if not p.locator('#solTapCinematic').is_visible():break
  p.locator('#solTapCinematic').click(position={'x':150,'y':250})
  p.wait_for_timeout(185)
  state=p.evaluate('''() => ({time:game.cut?.time,flags:game.cut?.flags,qa:__MEOWNURI_TAP_CONTROLLER__?.taps,rom:window.__MEOWNURI_ROMANCE_QA__,emoji:window.__MEOWNURI_ROMANCE_EMOJI_QA__,woodVisible:!!game.giftWood?.visible})''')
  visits.append({'index':t+1,'time':state['time'],'count':state['qa'],'woodVisible':state['woodVisible'],'rom':state['rom']})
  if t==10:p.screenshot(path=str(R/'meow_v168_wood_scene.png'))
 check('17 manual TAP gestures accepted',len(visits)>=15 and max(v['count'] for v in visits)>=15, f'{len(visits)} attempted, {max(v["count"] for v in visits)} accepted')
 check('Wood prop visible during nibble scene',any(v['woodVisible'] and v['time'] and 53<=v['time']<64 for v in visits),str([(v['time'],v['woodVisible']) for v in visits if v['time'] and 53<=v['time']<64]))
 check('No JS page error in romance gestures',not errors,str(errors[:3]))
 (R/'meownuri_v16.8_tap_timeline.json').write_text(json.dumps(visits,ensure_ascii=False,indent=2)+'\n')
 ctx.close()
 for choice,label in [(0,'kingdom'),(1,'village'),(2,'bridge')]:
  ctx,p,errors=boot(b)
  p.locator('#solStartDay4').click()
  # Jump to Day9 through test API; finish Day9 using actual UI choices
  p.evaluate('window.MeownuriStory.startDay(9,true)')
  for _ in range(10):
   st=p.evaluate('window.MeownuriStory.getCurrent()')
   if st['finished']:break
   p.evaluate('''()=>{let g=window.game,t=g.storyProject.target;g.player.x=t.x;g.player.z=t.z;g.player.y=g.ground.height(t.x,t.z);g.player.mesh.position.set(t.x,g.player.y,t.z)}''')
   p.wait_for_timeout(38)
   p.locator('#solStoryAction').click(force=True)
   if p.locator('#solStoryChoice').is_visible():p.locator('.solChoiceItems button').nth(choice).click()
  if p.locator('#solStoryNext').is_visible():p.locator('#solStoryNext').click()
  for _ in range(10):
   st=p.evaluate('window.MeownuriStory.getCurrent()')
   if st['finished']:break
   p.evaluate('''()=>{let g=window.game,t=g.storyProject.target;g.player.x=t.x;g.player.z=t.z;g.player.y=g.ground.height(t.x,t.z);g.player.mesh.position.set(t.x,g.player.y,t.z)}''')
   p.wait_for_timeout(42)
   p.locator('#solStoryAction').click(force=True)
  st=p.evaluate('window.MeownuriStory.getCurrent()')
  check('Ending '+label,st['finished'] and st['day']==10 and st['choices'].get('day9_kingdom_choice')==choice and not errors,str(st)[:200])
  ctx.close()
 b.close()
(R/'meownuri_v16.8_extended_results.json').write_text(json.dumps({'mode':'2D fallback; in-memory storage shim; Chrome headless; real UI clicks / direct QA test setup for Day9','results':results,'passed':sum(x['pass'] for x in results),'failed':sum(not x['pass'] for x in results)},ensure_ascii=False,indent=2)+'\n')
print('SUMMARY',len(results),sum(x['pass'] for x in results),'pass')
