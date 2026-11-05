/* SOL reference-transfer candidate, 2026-11-05. Original meshes and story retained. */
import 'client';
import {THREE,materials as M} from 'art';
const g=window.game;
if(g && !window.MeownuriCozy){
 const $=s=>document.querySelector(s), town=g.town;
 const palettes={clay:{roof:0xa95245,wall:0xb0774c,label:'흙빛'},sage:{roof:0x648575,wall:0xd8c7a3,label:'풀빛'},lavender:{roof:0x897b9f,wall:0xdccbb8,label:'보랏빛'}};
 const state={version:'SOL v16.10-reference',target:null,selectedStyle:'clay',lastCare:-10,lastOutcome:null};
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 const style=document.createElement('style');style.textContent=`
 #cozyCare{position:fixed;left:50%;transform:translateX(-50%);bottom:max(142px,calc(env(safe-area-inset-bottom) + 132px));z-index:35;display:flex;gap:8px;padding:5px;border-radius:30px;background:#fff7e8ed;border:1px solid #b9a98d;box-shadow:0 4px 20px #231c1720}
 #cozyCare[hidden]{display:none}#cozyCare button{min-width:48px;min-height:48px;margin:0;border-radius:50%;font-size:23px;background:#fff9ee;color:#433b30;border:1px solid #c8b99e}#cozyCare button:disabled{opacity:.45}
 .cozyStyles{display:flex;gap:8px;margin:10px 0}.cozyStyles button{flex:1;min-width:0;min-height:82px;padding:8px 4px;border:2px solid transparent;background:#fff9ef;color:#433b30}.cozyStyles button[aria-pressed=true]{border-color:#5b7966;background:#edf3e8}.cozyStyles svg{display:block;width:64px;max-width:100%;height:48px;margin:auto}.cozyStyles small{display:block}.cozyStyles button:focus-visible,#cozyCare button:focus-visible{outline:3px solid #567965;outline-offset:3px}
 #cozyNav{position:fixed;left:50%;transform:translateX(-50%);top:65px;z-index:36;pointer-events:none;font-size:26px;background:#fff7e8e8;border-radius:50%;padding:7px;display:none}#cozyNav[data-show=true]{display:block}
 `;document.head.append(style);
 const dock=document.createElement('div');dock.id='cozyCare';dock.hidden=true;dock.setAttribute('role','group');dock.setAttribute('aria-label','가까운 고양이 돌보기');
 dock.innerHTML='<button type="button" data-care="pet" aria-label="쓰다듬기" title="쓰다듬기">♡</button><button type="button" data-care="feed" aria-label="물고기 나누기" title="물고기 나누기">🐟</button>';
 document.body.append(dock);
 const notice=document.createElement('div');notice.id='cozyNav';notice.setAttribute('role','status');document.body.append(notice);let noticeTimer;
 const notify=(icon,label)=>{notice.textContent=icon;notice.setAttribute('aria-label',label);notice.dataset.show='true';clearTimeout(noticeTimer);noticeTimer=setTimeout(()=>notice.dataset.show='false',1300)};
 const allowed=()=>g.mode==='play'&&!g.cut&&!g.storyLock&&!g.homeResting&&!g.bearStarted&&!g.selected&&!town.blueprint&&$('#modal').hidden&&(!window.MeownuriStory||MeownuriStory.getCurrent().day<4);
 const nearCat=()=>g.actors.filter(a=>a!==g.player&&a!==g.bear&&a.active&&a.mesh.visible&&g.dist(a)<3.2).sort((a,b)=>g.dist(a)-g.dist(b))[0];
 function cancel(){state.target=null;ring.visible=false;g.player.path=[];g.player.goal=null}
 function care(kind){
  const a=nearCat();if(!allowed()||!a||g.t-state.lastCare<2)return false;
  if(kind==='feed'&&g.bag.fish<1)return false;
  cancel();state.lastCare=g.t;
  if(kind==='feed'){g.bag.fish--;g.audio.play('fish')}else g.audio.play('home');
  a.mesh.rotation.y=Math.atan2(g.player.x-a.x,g.player.z-a.z);
  g.emotion(a,kind==='feed'?'🐟':'💛',2);g.gesture(a,reduced.matches?'shy':'happy',1.4);
  g.emotion(g.player,'♡',1.6);g.save();state.lastOutcome=kind;return true;
 }
 dock.addEventListener('click',e=>{const b=e.target.closest('[data-care]');if(b)care(b.dataset.care)});
 const ring=new THREE.Mesh(new THREE.RingGeometry(.48,.61,32),new THREE.MeshBasicMaterial({color:0xffe4a5,side:THREE.DoubleSide,transparent:true,opacity:.9,depthWrite:false}));ring.rotation.x=-Math.PI/2;ring.visible=false;g.scene.add(ring);
 function moveTo(p){
  if(!allowed()||!g.ground.dry(p.x,p.z))return false;
  const dest=g.ground.nearest(p.x,p.z,g.player.radius+.08,g.otherActors(g.player),1.5);
  if(!dest||!g.ground.path(g.player,dest,g.player.radius+.06,g.otherActors(g.player)).length){cancel();notify('⊘','이곳으로 걸어갈 수 없어요');return false}
  state.target={...dest};state.started=g.t;state.progressAt=g.t;state.lastDistance=g.dist(dest);
  ring.position.set(dest.x,g.ground.height(dest.x,dest.z)+.09,dest.z);ring.visible=g.rendererMode==='3d';g.audio.unlock();return true;
 }
 // A short single-pointer tap walks; drag and pinch retain the original camera controls.
 const canvas=$('#world'),ray=new THREE.Raycaster();let press=null,multi=false;const pointers=new Set();
 canvas.addEventListener('pointerdown',e=>{pointers.add(e.pointerId);if(pointers.size>1){multi=true;press=null;return}multi=false;press={id:e.pointerId,x:e.clientX,y:e.clientY,time:performance.now(),moved:false}});
 canvas.addEventListener('pointermove',e=>{if(press&&Math.hypot(e.clientX-press.x,e.clientY-press.y)>9)press.moved=true});
 canvas.addEventListener('pointerup',e=>{
  const p=press;pointers.delete(e.pointerId);press=null;
  if(!p||multi||p.id!==e.pointerId||p.moved||performance.now()-p.time>500||!allowed()||g.rendererMode!=='3d')return;
  const r=canvas.getBoundingClientRect();ray.setFromCamera(new THREE.Vector2((e.clientX-r.left)/r.width*2-1,1-(e.clientY-r.top)/r.height*2),g.camera);
  // March against the game's exact height field rather than an invented flat floor.
  let last=null;
  for(let t=.5;t<160;t+=.2){const q=ray.ray.at(t,new THREE.Vector3());if(!g.ground.inside(q.x,q.z))continue;const h=g.ground.height(q.x,q.z);if(q.y<=h&&last){moveTo(q);break}last=q;}
 });
 canvas.addEventListener('pointercancel',e=>{pointers.delete(e.pointerId);press=null});
 addEventListener('blur',()=>{press=null;pointers.clear();cancel()});
 document.addEventListener('visibilitychange',()=>{if(document.hidden)cancel()});
 addEventListener('keydown',e=>{if(['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Escape','Space'].includes(e.code))cancel()});
 $('#joystick').addEventListener('pointerdown',cancel);
 const update=g.updatePlayer.bind(g);g.updatePlayer=function(dt){
  if(state.target){
   if(!allowed()||Math.hypot(g.joy.x,g.joy.y)>.06){cancel()}
   else{const d=g.dist(state.target);if(d<state.lastDistance-.08){state.lastDistance=d;state.progressAt=g.t}
    if(g.travel(g.player,state.target,dt,3.4)){cancel();notify('✓','도착했어요')}
    else if(g.t-state.progressAt>2.5||g.t-state.started>30){cancel();notify('⊘','길이 막혔어요')}
   }
  }
  update(dt);
 };
 const ui=g.updateUI.bind(g);g.updateUI=function(){ui();const a=allowed()?nearCat():null;dock.hidden=!a;
  if(a){dock.setAttribute('aria-label',a.name+' 돌보기');dock.querySelector('[data-care=feed]').disabled=g.bag.fish<1||g.t-state.lastCare<2;dock.querySelector('[data-care=pet]').disabled=g.t-state.lastCare<2}
  if(!allowed()&&state.target)cancel();if(ring.visible)ring.scale.setScalar(reduced.matches?1:1+Math.sin(g.t*3)*.08);
 };
 function paint(s){if(s.type!=='house'||!palettes[s.cozyStyle])return;const p=palettes[s.cozyStyle];s.mesh.traverse(o=>{if(o.isMesh&&(o.material===M.roof||o.material===M.wood2)){const role=o.material===M.roof?'roof':'wall';o.material=o.material.clone();o.material.color.setHex(p[role]);o.userData.cozyRole=role}})}
 const add=town.addStructure.bind(town);town.addStructure=function(s){add(s);paint(s)};
 const select=town.selectBlueprint.bind(town);town.selectBlueprint=function(type){select(type);if(this.blueprint?.type==='house')this.blueprint.cozyStyle=state.selectedStyle};
 const snap=town.snapshot.bind(town);town.snapshot=function(){const s=snap();s.structures.forEach((b,i)=>{if(this.structures[i].cozyStyle)b.cozyStyle=this.structures[i].cozyStyle});return s};
 const menu=town.buildMenu.bind(town);town.buildMenu=function(){menu();const card=$('[data-build=house]')?.closest('.buildCard');if(!card)return;
  const row=document.createElement('div');row.className='cozyStyles';row.setAttribute('role','group');row.setAttribute('aria-label','집 외관 선택');
  row.innerHTML=Object.entries(palettes).map(([id,p])=>`<button type="button" data-style="${id}" aria-label="${p.label} 집" aria-pressed="${state.selectedStyle===id}"><svg viewBox="0 0 72 52" aria-hidden="true"><path d="M13 25H59V49H13Z" fill="#${p.wall.toString(16)}"/><path d="M6 26L36 4L66 26Z" fill="#${p.roof.toString(16)}"/><path d="M30 49V32H43V49" fill="#66513b"/><path d="M18 31H25V38H18ZM48 31H55V38H48Z" fill="#ffdfa1"/></svg><small>${p.label}</small></button>`).join('');
  row.onclick=e=>{const b=e.target.closest('[data-style]');if(!b)return;state.selectedStyle=b.dataset.style;row.querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed',x===b?'true':'false'))};card.insertBefore(row,card.querySelector('[data-build]'));
 };
 window.MeownuriCozy={state,moveTo,cancel,care,palettes};
}
