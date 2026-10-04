// Actual r2 wrapper + original Ground. Travel callback is a spy, not browser QA.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
// Use the exact embedded collision module, not a duplicate implementation.
const html=fs.readFileSync(process.argv[2] || new URL('../index.html',import.meta.url),'utf8');
const map=html.match(/<script type="importmap">([\s\S]*?)<\/script>/);
assert(map,'Embedded importmap missing');
const {Ground}=await import(JSON.parse(map[1]).imports.logic);
const py=fs.readFileSync(new URL('./apply_v14_19_r2.py',import.meta.url),'utf8');
const wrapper=py.split("WRAPPER='''")[1].split("'''")[0];
const results=[];
function fixture(){
 const ground=new Ground();
 ground.add({shape:'rect',x:10,z:8,hx:1.46,hz:1.34,owner:'box'});
 ground.add({shape:'rect',x:9,z:11,hx:1.325,hz:1.025,owner:'bed'});
 ground.add({shape:'circle',x:10.5,z:13.5,r:.82,owner:'bowl'});
 const friend={x:11.730285480204778,z:43.85629110100716,radius:.66*.82,active:true};
 const player={x:8.668627805100833,z:44.39201061306515,radius:.66,active:true};
 const calls=[];
 const g={ground,friend,player,storyPhase:5,clueLead:{kind:'home'},homeJourney:null,bearStarted:false,ending:false,
 otherActors(){return [player]},travel(a,t,dt,speed){calls.push({actor:a,target:t,dt,speed});return t}};
 vm.runInNewContext(wrapper,{g,WeakMap});return {g,calls,friend,ground};
}
function test(name,fn){try{fn();results.push({name,pass:true})}catch(e){results.push({name,pass:false,error:String(e)})}}
const blocked={x:10,z:11.5};
test('Exact natural furniture layout blocks original target and A*',()=>{const f=fixture();assert(f.ground.blocked(10,11.5,f.friend.radius+.06));assert.equal(f.ground.path(f.friend,blocked,f.friend.radius+.06,[f.g.player]).length,0)});
test('Occupied home target resolves to reachable free space',()=>{const f=fixture();const t=f.g.travel(f.friend,blocked,.016,2.5);assert(!f.ground.blocked(t.x,t.z,f.friend.radius+.06));assert(f.ground.path(f.friend,t,f.friend.radius+.06,[f.g.player]).length>0);assert(Math.hypot(t.x-10,t.z-11.5)<=4.5);assert.equal(f.calls[0].speed,2.5)});
test('Unobstructed target retains exact identity',()=>{const f=fixture(),t={x:20,z:20};assert.equal(f.g.travel(f.friend,t,.016,2.5),t)});
test('Actor positions and furniture colliders remain unchanged',()=>{const f=fixture();const before=JSON.stringify([f.friend,f.g.player,f.ground.colliders]);f.g.travel(f.friend,blocked,.016,2.5);assert.equal(JSON.stringify([f.friend,f.g.player,f.ground.colliders]),before)});
test('Non-companion actor is not redirected',()=>{const f=fixture();assert.equal(f.g.travel(f.g.player,blocked,.016,2.5),blocked)});
test('Non-home phase is not redirected',()=>{const f=fixture();f.g.storyPhase=4;f.g.clueLead.kind='fish';assert.equal(f.g.travel(f.friend,blocked,.016,2.5),blocked)});
test('Bear and ending phases are excluded',()=>{for(const k of ['bearStarted','ending']){const f=fixture();f.g[k]=true;assert.equal(f.g.travel(f.friend,blocked,.016,2.5),blocked)}});
test('Repeated calls keep a stable safe target',()=>{const f=fixture();const a=f.g.travel(f.friend,blocked,.016,2.5);assert.equal(f.g.travel(f.friend,{...blocked},.016,2.5),a)});
test('Changed obstacle invalidates cached target',()=>{const f=fixture();const a=f.g.travel(f.friend,blocked,.016,2.5);f.ground.add({shape:'circle',x:a.x,z:a.z,r:.3,owner:'newObstacle'});const b=f.g.travel(f.friend,blocked,.016,2.5);assert.notEqual(a,b);assert(!f.ground.blocked(b.x,b.z,f.friend.radius+.06))});
test('No available space retains normal blocked travel, never forced success',()=>{const f=fixture();f.ground.nearest=()=>null;assert.equal(f.g.travel(f.friend,blocked,.016,2.5),blocked)});
test('Day1 home journey uses same furniture-safe rule',()=>{const f=fixture();f.g.storyPhase=1;f.g.homeJourney={};f.g.clueLead=null;const t=f.g.travel(f.friend,blocked,.016,2.05);assert(!f.ground.blocked(t.x,t.z,f.friend.radius+.06))});
console.log(JSON.stringify({method:'Actual patch wrapper and original Ground; mocked travel callback, not browser',results},null,2));if(results.some(r=>!r.pass))process.exitCode=1;
