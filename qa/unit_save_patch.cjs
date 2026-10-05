// Isolated tests of the actual extracted agency wrappers. Core/DOM mocked.
// Run after: python qa/apply_v14_19_r1.py index.html qa-r1
// Then: node qa/unit_save_patch.cjs qa-r1/agency.js
const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const src=fs.readFileSync(process.argv[2]||'qa-r1/agency.js','utf8');
const block=src.slice(src.indexOf('  /* ---------- 0.'),src.indexOf('  /* ---------- 1.'));
const KEY='meownuri:MEOWNURI9:story:v3-wide';let results=[];
function fixture(saved){
 let data=saved?JSON.stringify(saved):null,button=0;
 const dom={'#questText':{textContent:'fresh'},'#questDetail':{textContent:''}};
 const g={mode:'title',stage:0,storyPhase:0,dayNumber:1,friendMeetPhase:0,friend:{x:0,z:0},box:{x:10,z:8},storyWorld:{sunset:{x:45,z:-17}},giftFish:{visible:false},
 setQuest(t,d){dom['#questText'].textContent=t;dom['#questDetail'].textContent=d||''},
 snapshot(){return {line:'MEOWNURI9',schema:2,stage:this.stage,storyPhase:this.storyPhase,dayNumber:this.dayNumber,friend:{...this.friend}}},
 restore(){let s=JSON.parse(data);if(!s||s.line!=='MEOWNURI9'||s.schema!==2)return;this.mode='play';Object.assign(this,{stage:s.stage,storyPhase:s.storyPhase,dayNumber:s.dayNumber,friend:s.friend||{x:0,z:0}})},
 ensureStoryFish(){return this.floorFish||(this.floorFish={visible:true})},ensureGiftFish(){this.giftFish={visible:true}},
 showSunsetTrail(v){this.trail=v},clearIntroTrail(){this.trailCleared=true},beginClueLead(kind){this.clueLead={kind};this.clueLeadReady=false},showClue(){},storyCard(){}
 };
 vm.runInNewContext(block,{g,window:{},$:s=>dom[s]||null,localStorage:{getItem:k=>{assert.equal(k,KEY);return data}},setTimeout(){},showDay2Button(){button++},Math,Number,JSON});
 return {g,save(){data=JSON.stringify(g.snapshot());return JSON.parse(data)},get button(){return button}};
}
function test(name,fn){try{fn();results.push({name,pass:true})}catch(e){results.push({name,pass:false,error:e.stack})}}
const cases=[['fish detected',{storyPhase:0,bondJourney:{phase:1}}],['returning with gift',{storyPhase:0,bondJourney:{phase:2}}],['home follow',{storyPhase:1,homeJourney:{lookAt:893}}],['home arrived',{storyPhase:1,homeReady:true}],['sunset follow',{storyPhase:2,sunsetJourney:{phase:0,lookAt:250}}],['sunset arrived',{storyPhase:2,sunsetJourney:{phase:1},sunsetReady:true}],['night stay',{storyPhase:2,__day1Complete:true}],['Day2 fish lead',{storyPhase:4,dayNumber:2,clueLead:{kind:'fish',phase:0,lookAt:333}}],['Day2 home arrived',{storyPhase:5,dayNumber:2,clueLeadReady:true}],['friend meeting',{stage:6,friendMeetPhase:2}]];
for(const [name,vars] of cases)test('roundtrip '+name,()=>{
 const a=fixture();Object.assign(a.g,{mode:'play',stage:7},vars);a.g.setQuest('retained '+name,'details');const s=a.save(),b=fixture(s);b.g.restore();
 for(const key of ['homeReady','sunsetReady','clueLeadReady','__day1Complete'])assert.equal(!!b.g[key],!!a.g[key]);
 for(const key of ['bondJourney','homeJourney','sunsetJourney','clueLead'])if(vars[key]){assert(b.g[key],key);if(vars[key].phase!==undefined)assert.equal(b.g[key].phase,vars[key].phase)}
 assert.equal(b.g.__questText,'retained '+name);assert.equal(b.save().quest.text,s.quest.text);assert.equal(b.g.friendMeetPhase,a.g.friendMeetPhase);
 if(name==='night stay')assert.equal(b.button,1);
 if(name==='fish detected')assert.equal(b.g.floorFish.visible,true);
 if(name==='Day2 home arrived')assert.equal(b.g.clueLead,null);
});
for(const ph of [0,1,2])test('legacy save phase '+ph,()=>{let f=fixture({line:'MEOWNURI9',schema:2,stage:7,storyPhase:ph,dayNumber:1,friend:{x:0,z:0},quest:{text:'old quest',detail:'old'}});f.g.restore();assert.equal(f.g.__questText,'old quest');assert(ph===0?f.g.bondJourney:ph===1?f.g.homeJourney:f.g.sunsetJourney)});
test('legacy arrived home',()=>{let f=fixture({line:'MEOWNURI9',schema:2,stage:7,storyPhase:1,dayNumber:1,friend:{x:13.5,z:11.5}});f.g.restore();assert(f.g.homeReady);assert(!f.g.homeJourney)});
test('legacy night stay',()=>{let f=fixture({line:'MEOWNURI9',schema:2,stage:7,storyPhase:2,dayNumber:1,friend:{x:45,z:-17},quest:{text:'밤의 평화'}});f.g.restore();assert.equal(f.button,1);assert(f.g.__day1Complete)});
test('wrong schema rejected',()=>{let f=fixture({line:'other',schema:999,agencyProgress:{version:1,homeJourney:{}}});f.g.restore();assert.equal(f.g.mode,'title');assert.equal(f.g.homeJourney,undefined)});
console.log(JSON.stringify({method:'Actual save-wrapper code, mocked core/DOM; not browser QA',results},null,2));if(results.some(r=>!r.pass))process.exitCode=1;
