const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto');
const root=path.resolve(__dirname,'..'),output=path.join(root,'qa');
const report={testedAt:new Date().toISOString(),checks:[],errors:[],scope:'local Chromium; mobile emulation; GPU software / forced 2D; no physical device or audio listening'};
function check(name,value,detail){report.checks.push({name,pass:!!value,detail});console.log(value?'PASS':'FAIL',name);if(!value)throw Error(name)}
(async()=>{
 const html=fs.readFileSync(path.join(root,'preview.html'));const server=http.createServer((q,r)=>{r.setHeader('Content-Type','text/html;charset=utf-8');r.end(html)});await new Promise(r=>server.listen(0,'127.0.0.1',r));const url='http://127.0.0.1:'+server.address().port+'/preview.html?customize=1';
 let browser,page;
 try{
  const common=require('/tmp/meownuri-browser/node_modules/@sparticuz/chromium').args;
  for(const mode of['3d','2d']){
   browser=await chromium.launch({executablePath:process.env.QA_EXECUTABLE||'/tmp/chromium',headless:true,args:mode==='2d'?[...common,'--disable-webgl']:common});
   page=await browser.newPage({viewport:{width:390,height:844},isMobile:true,hasTouch:true,reducedMotion:'reduce'});page.on('pageerror',e=>report.errors.push(mode+': '+e.message));
   await page.goto(url);await page.waitForFunction(()=>window.MeownuriChoices?.state.open);if(fs.existsSync('/tmp/qa-fonts.css'))await page.addStyleTag({content:fs.readFileSync('/tmp/qa-fonts.css','utf8')+'#choiceStudio *{font-family:"Noto Sans KR","Noto Emoji",sans-serif!important}'});
   check(mode+' renderer',await page.evaluate(m=>MeownuriChoices.state.renderer===m,mode));
   const choose=async(step,name)=>{await page.locator('[data-step="'+step+'"]').click();await page.locator('#csOptions button').filter({hasText:name}).click()};
   await choose(0,'바닷가');await choose(1,'민트');await choose(2,'돌');
   check(mode+' visual draft not saved early',await page.evaluate(()=>{const s=MeownuriChoices.state;return s.draft.place==='coast'&&s.draft.color==='mint'&&s.draft.material==='stone'&&localStorage.getItem('meownuri:choice-studio:v1')===null}));
   await page.locator('#csClose').focus();await page.keyboard.press('Tab');check(mode+' Tab enters studio controls',await page.evaluate(()=>document.activeElement?.dataset.step==='0'&&document.querySelector('#modal').hidden));
   await page.screenshot({path:path.join(output,mode+'-coast-draft.png')});await page.locator('#csNext').tap();
   check(mode+' confirm creates persistent result',await page.evaluate(()=>{const s=MeownuriChoices.state,j=JSON.parse(localStorage.getItem('meownuri:choice-studio:v1'));return s.result&&j.value.place==='coast'&&j.value.color==='mint'&&j.value.material==='stone'}));
   await page.locator('#csActivity').tap();check(mode+' coast has fish interaction',await page.evaluate(()=>MeownuriChoices.state.activity==='fish'));
   await page.reload();await page.waitForFunction(()=>window.MeownuriChoices?.state.open);check(mode+' reload restores result',await page.evaluate(()=>MeownuriChoices.state.result&&MeownuriChoices.state.draft.material==='stone'));
   await page.locator('#csEdit').tap();await choose(0,'놀이터');await choose(1,'라벤더');await choose(2,'패브릭');await page.locator('#csNext').tap();
   check(mode+' second combination commits',await page.evaluate(()=>MeownuriChoices.state.committed.place==='play'&&MeownuriChoices.state.committed.material==='fabric'));
   await page.locator('#csActivity').tap();check(mode+' playground has play interaction',await page.evaluate(()=>MeownuriChoices.state.activity==='play'));
   await page.locator('#csUndo').tap();check(mode+' undo restores prior choice',await page.evaluate(()=>MeownuriChoices.state.committed.place==='coast'&&MeownuriChoices.state.committed.color==='mint'));
   await page.locator('#csEdit').tap();await choose(0,'풀밭');await page.locator('#csClose').tap();await page.locator('#cozyReviewStart').tap();await page.locator('#cozyOpenStudio').tap();check(mode+' cancel discards draft',await page.evaluate(()=>MeownuriChoices.state.draft.place==='coast'));
   await page.setViewportSize({width:375,height:667});check(mode+' narrow screen controls stay visible',await page.locator('#csEdit').isVisible());check(mode+' no horizontal overflow',await page.evaluate(()=>document.querySelector('#choiceStudio').scrollWidth<=innerWidth));
   await page.locator('#csEdit').tap();await choose(0,'풀밭');await page.locator('[data-step="2"]').click();await page.locator('#csNext').tap();await page.locator('#csActivity').tap();check(mode+' meadow grows flowers',await page.evaluate(()=>MeownuriChoices.state.activity==='bloom'));
   if(mode==='2d'){
    await page.locator('#csEdit').tap();const hashes=new Set();
    for(const place of['meadow','coast','play'])for(const color of['apricot','mint','lavender'])for(const material of['wood','stone','fabric']){
     await page.evaluate(({place,color,material})=>{for(const [i,value]of[[0,place],[1,color],[2,material]]){document.querySelector('[data-step="'+i+'"]').click();document.querySelector('[data-option="'+value+'"]').click()}},{place,color,material});
     await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));const data=await page.locator('#csCanvas').evaluate(c=>c.toDataURL());hashes.add(crypto.createHash('sha256').update(data).digest('hex'));
    }
    check('All 27 combinations produce distinct 2D images',hashes.size===27,hashes.size);
    await page.locator('#csNext').tap();await page.screenshot({path:path.join(output,'2d-play-result.png')});
    await page.reload();await page.waitForFunction(()=>window.MeownuriChoices?.state.open);check('All combination loop leaves valid saved result',await page.evaluate(()=>MeownuriChoices.state.result&&MeownuriChoices.state.draft.place==='play'));
   }
   await browser.close();browser=null;
  }
  check('No JavaScript errors',report.errors.length===0,report.errors);report.status='PASS';
 }catch(e){report.status='FAIL';report.failure=String(e);if(page)await page.screenshot({path:path.join(output,'failure.png')}).catch(()=>{});process.exitCode=1}
 finally{fs.writeFileSync(path.join(output,'choice-results.json'),JSON.stringify(report,null,2));if(browser)await browser.close();server.close()}
})();
