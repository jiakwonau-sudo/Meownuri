const {chromium}=require('playwright');
const fs=require('fs'),http=require('http'),path=require('path');
const root=path.resolve(__dirname,'..'),out=path.join(root,'qa-reference');fs.mkdirSync(out,{recursive:true});
const results={checks:[],errors:[],scope:'Chromium mobile 390x844; software WebGL; fixture-based interaction tests, not full story playthrough'};
function check(name,ok,detail){results.checks.push({name,ok,detail});console.log(ok?'PASS':'FAIL',name);if(!ok)throw Error(name)}
(async()=>{
 const server=http.createServer((q,r)=>{r.setHeader('Content-Type','text/html; charset=utf-8');r.end(fs.readFileSync(path.join(root,'index.html')))});await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const args=process.env.QA_ARGS?JSON.parse(process.env.QA_ARGS):['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader'];
 const browser=await chromium.launch({headless:true,args,...(process.env.QA_EXECUTABLE?{executablePath:process.env.QA_EXECUTABLE}:{})});
 const p=await browser.newPage({viewport:{width:390,height:844},isMobile:true,hasTouch:true});p.on('pageerror',e=>results.errors.push(e.message));
 try{
  await p.goto('http://127.0.0.1:'+server.address().port);await p.waitForFunction(()=>window.MeownuriCozy);
  check('3D module boot',await p.evaluate(()=>game.rendererMode==='3d'));
  await p.locator('#introStart').click();
  // A free-play fixture isolates the added interactions from long authored cinematics.
  await p.evaluate(()=>{const g=game;g.stage=5;g.player.x=0;g.player.z=0;g.player.y=g.ground.height(0,0);g.friend.x=2;g.friend.z=0;g.friend.y=g.ground.height(2,0);g.friend.active=true;g.friend.mesh.visible=true;g.bag.fish=2;g.updateUI()});
  await p.locator('[data-care=pet]').tap();
  check('Pet causes cat heart',await p.evaluate(()=>MeownuriCozy.state.lastOutcome==='pet'&&game.bag.fish===2));
  check('Care tap cooldown',await p.evaluate(()=>!MeownuriCozy.care('feed')&&game.bag.fish===2));
  await p.evaluate(()=>MeownuriCozy.state.lastCare=game.t-3);await p.waitForTimeout(200);await p.locator('[data-care=feed]').tap();
  check('Feed consumes exactly one and saves',await p.evaluate(()=>game.bag.fish===1&&JSON.parse(localStorage.getItem('meownuri:MEOWNURI9:story:v3-wide')).bag.fish===1));
  await p.evaluate(()=>{game.bag.fish=0;game.updateUI()});check('No fish disables feed',await p.locator('[data-care=feed]').isDisabled());
  await p.screenshot({path:path.join(out,'care.png')});
  await p.evaluate(()=>{game.friend.active=false;game.friend.mesh.visible=false;game.updateUI()});check('Care hidden without nearby cat',await p.locator('#cozyCare').isHidden());
  check('Water target rejected',await p.evaluate(()=>!MeownuriCozy.moveTo({x:59,z:59})));
  check('Walk target accepted',await p.evaluate(()=>MeownuriCozy.moveTo({x:0,z:3})));
  await p.waitForFunction(()=>!MeownuriCozy.state.target);check('Walk reaches target',await p.evaluate(()=>Math.hypot(game.player.x,game.player.z-3)<.5));
  await p.evaluate(()=>MeownuriCozy.moveTo({x:0,z:7}));await p.keyboard.press('Escape');check('Manual input cancels walk',await p.evaluate(()=>!MeownuriCozy.state.target));
  // Use projected ground point for a real pointer tap, not only the controller method.
  const pt=await p.evaluate(()=>{let v=new __THREE.Vector3(-2,game.ground.height(-2,3),3).project(game.camera);return{x:(v.x*.5+.5)*innerWidth,y:(-v.y*.5+.5)*innerHeight}});
  await p.touchscreen.tap(pt.x,pt.y);await p.waitForTimeout(100);check('Ground touch starts walking',await p.evaluate(()=>!!MeownuriCozy.state.target));
  await p.evaluate(()=>MeownuriCozy.cancel());
  await p.mouse.move(200,400);await p.mouse.down();await p.mouse.move(250,410,{steps:5});await p.mouse.up();check('Camera drag does not walk',await p.evaluate(()=>!MeownuriCozy.state.target));
  await p.evaluate(()=>{game.storyLock=true});check('Story lock blocks walk and care',await p.evaluate(()=>!MeownuriCozy.moveTo({x:0,z:0})&&!MeownuriCozy.care('pet')));await p.evaluate(()=>game.storyLock=false);
  await p.evaluate(()=>{game.town.start();game.bag.wood=30;game.bag.fiber=10;game.town.buildMenu()});
  check('Three house options visible',await p.locator('.cozyStyles button').count()===3);
  await p.locator('[data-style=sage]').tap();check('Selected card state',await p.locator('[data-style=sage]').getAttribute('aria-pressed')==='true');
  await p.screenshot({path:path.join(out,'house-choices.png')});
  await p.locator('[data-build=house]').click();
  check('Blueprint retains style',await p.evaluate(()=>game.town.blueprint?.cozyStyle==='sage'));
  await p.evaluate(()=>{const g=game,b=g.town.blueprint;g.player.x=b.access.x;g.player.z=b.access.z;g.player.y=g.ground.height(g.player.x,g.player.z);g.town.beginConstruction();for(let i=0;i<8;i++)g.town.manualBuild(g.town.structures[0]);g.save()});
  check('Real construction preserves costs and style',await p.evaluate(()=>{const s=game.town.structures[0];return s.complete&&s.cozyStyle==='sage'&&game.bag.wood===18&&game.bag.fiber===6&&s.mesh.children.some(o=>o.userData.cozyRole==='roof'&&o.material.color.getHex()===0x648575)}));
  await p.screenshot({path:path.join(out,'built-house.png')});
  await p.reload();await p.waitForFunction(()=>window.MeownuriCozy);await p.locator('#continueBtn').click();
  check('Reload restores house appearance',await p.evaluate(()=>{const s=game.town.structures[0];return s.cozyStyle==='sage'&&s.mesh.children.some(o=>o.userData.cozyRole==='roof'&&o.material.color.getHex()===0x648575)}));
  check('No page errors',results.errors.length===0,results.errors);
  results.status='PASS';
 }catch(e){results.status='FAIL';results.failure=String(e);await p.screenshot({path:path.join(out,'failure.png')});process.exitCode=1}
 finally{fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(results,null,2));await browser.close();server.close()}
})();
