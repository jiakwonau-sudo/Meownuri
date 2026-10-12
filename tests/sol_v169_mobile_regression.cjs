'use strict';
const {chromium}=require('playwright');
const fs=require('node:fs');
const http=require('node:http');
const path=require('node:path');
const crypto=require('node:crypto');
const {execFileSync}=require('node:child_process');
const baseline=process.argv.includes('--baseline');
const root=path.resolve(__dirname,'..');
const html=baseline?execFileSync('git',['show','b5a6b590f77f6511cf5f65e9a9c29fb4e09ced8b:index.html'],{cwd:root,maxBuffer:4e6}):fs.readFileSync(path.join(root,'index.html'));
const output=process.env.QA_OUTPUT||path.join(root,'qa-output',baseline?'baseline':'fixed');
fs.mkdirSync(output,{recursive:true});
const result={baseline,testedAt:new Date().toISOString(),sourceSha256:crypto.createHash('sha256').update(html).digest('hex'),checks:[],pageErrors:[]};
const check=(name,ok,detail)=>{result.checks.push({name,ok,detail});console.log(ok?'PASS':'FAIL',name,JSON.stringify(detail));if(!ok)throw Error(name);};
(async()=>{
  const server=http.createServer((req,res)=>{if(req.url==='/favicon.ico'){res.writeHead(204);return res.end();}res.setHeader('Content-Type','text/html; charset=utf-8');res.end(html);});
  let browser,page;
  try{
    await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
    result.url='http://127.0.0.1:'+server.address().port+'/';
    const args=['--no-sandbox',...(process.env.QA_2D?['--disable-webgl']:['--enable-webgl','--use-angle=swiftshader','--enable-unsafe-swiftshader'])];
    browser=await chromium.launch({headless:true,args,...(process.env.QA_CHROME?{channel:'chrome'}:{})});
    result.browser=browser.version();
    page=await browser.newPage({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
    page.on('pageerror',e=>result.pageErrors.push(String(e)));
    await page.goto(result.url,{waitUntil:'domcontentloaded'});
    await page.waitForFunction(()=>window.__SOL_MISSION_HUD_V169__?.buttonsEnabled);
    await page.locator('#solStartDay4').click();
    await page.waitForFunction(()=>MeownuriStory.getCurrent().day===4);
    const state=()=>page.evaluate(()=>{
      const p=document.querySelector('#solStoryPanel'),s=MeownuriStory.getCurrent(),style=getComputedStyle(p);
      return {day:s.day,beat:s.beat,finished:s.finished,visibility:style.visibility,opacity:style.opacity,pointerEvents:style.pointerEvents,classes:p.className,transition:style.transition,cta:document.querySelector('#solMissionDoV169').textContent,dockHidden:document.querySelector('#solMissionDockV169').hidden,renderer:game.rendererMode,events:__SOL_MISSION_HUD_V169__.events.slice(-6)};
    });
    const waitHidden=()=>page.waitForFunction(()=>getComputedStyle(document.querySelector('#solStoryPanel')).visibility==='hidden',null,{timeout:1500});
    await page.waitForFunction(()=>!document.querySelector('#solMissionDockV169').hidden);
    let s=await state();result.renderer=s.renderer;
    check('Day4 compact by default',s.day===4&&s.beat===0&&s.visibility==='hidden'&&!s.dockHidden,s);
    await page.locator('#solMissionMoreV169').click();
    s=await state();check('Open guide',s.visibility==='visible',s);
    await page.locator('#solGuideCloseV169').click();
    s=await state();
    if(baseline){
      check('Original Close failed reproduced',s.visibility==='visible'&&s.classes.includes('sol-guide-dismissed')&&s.events.at(-1)==='collapse',s);
      await waitHidden().catch(()=>{});s=await state();
      result.baselineAfterTransition=s;
      console.log('BASELINE visibility after transition observation',JSON.stringify(s));
    }else{
      check('Close immediately hides guide',s.visibility==='hidden'&&s.opacity==='0'&&s.pointerEvents==='none',s);
      await page.waitForTimeout(250);s=await state();check('Guide stays closed across HUD update',s.visibility==='hidden',s);
      await page.locator('#solMissionMoreV169').tap();s=await state();check('Reopen with touch',s.visibility==='visible',s);
      await page.locator('#solGuideCloseV169').tap();s=await state();check('Close with touch',s.visibility==='hidden',s);
      await page.locator('#solMissionMoreV169').click();await page.keyboard.press('Escape');
      s=await state();check('Escape closes guide',s.visibility==='hidden',s);
      const go=async()=>{
        await page.waitForFunction(()=>{
          const s=MeownuriStory.getCurrent();
          return __SOL_MISSION_HUD_V169__.beat===s.beat&&document.querySelector('#solMissionDoV169').textContent.startsWith(`${s.beat+1}/`);
        });
        let r=await state();const before=r.beat;
        if(r.cta.includes('이동')){
          await page.locator('#solMissionDoV169').tap();
          await page.waitForFunction(()=>document.querySelector('#solMissionDoV169').textContent.includes('행동'),null,{timeout:25000});
          r=await state();
        }
        check('Walk enables action at beat '+before,r.cta.includes('행동'),r);
        await page.locator('#solMissionDoV169').tap();
        await page.waitForFunction(b=>MeownuriStory.getCurrent().beat!==b||MeownuriStory.getCurrent().finished,before);
        await waitHidden();
      };
      await go();await go();
      await page.waitForFunction(()=>__SOL_MISSION_HUD_V169__.beat===2);
      s=await state();check('Day4 reaches 3/5 with guide hidden',s.beat===2&&s.visibility==='hidden',s);
      await page.screenshot({path:path.join(output,'day4-3of5.png')});
      await page.locator('#solMissionQuietV169').tap();check('Quiet hides action',!await page.locator('#solMissionDoV169').isVisible());
      await page.locator('#solMissionMoreV169').tap();check('Restore shows action',await page.locator('#solMissionDoV169').isVisible());
      await go();await go();await go();
      await page.waitForFunction(()=>document.querySelector('#solMissionDoV169').textContent.includes('DAY 5'));
      s=await state();check('Day4 completes all five beats',s.finished&&s.cta.includes('DAY 5'),s);
      await page.locator('#solMissionDoV169').tap();
      await page.waitForFunction(()=>MeownuriStory.getCurrent().day===5);
      await page.waitForFunction(()=>__SOL_MISSION_HUD_V169__.day===5);
      await waitHidden();s=await state();check('Day5 transition',s.day===5&&!s.finished&&s.beat===0&&s.visibility==='hidden',s);
      await page.screenshot({path:path.join(output,'day5-start.png')});
    }
    check('No JavaScript page errors',result.pageErrors.length===0,result.pageErrors);
    result.status='PASS';
  }catch(e){result.status='FAIL';result.error=String(e);if(page)await page.screenshot({path:path.join(output,'failure.png'),timeout:5000}).catch(()=>{});throw e;}
  finally{fs.writeFileSync(path.join(output,'results.json'),JSON.stringify(result,null,2)+'\n');if(browser)await browser.close();server.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
