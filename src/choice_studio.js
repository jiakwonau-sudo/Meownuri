/* SOL v16.11 · visual choices, original SOL meshes, committed local results. */
import 'client';
import {THREE,materials as M,building,cat} from 'art';
(() => {
 const g=window.game;if(!g||window.MeownuriChoices)return;
 const KEY='meownuri:choice-studio:v1', $=s=>document.querySelector(s);
 const places={meadow:{name:'풀밭',sub:'꽃과 나무가 있는 쉼터',ground:0x90ae74,sky:0xe5eddd},coast:{name:'바닷가',sub:'모래와 물결이 있는 쉼터',ground:0xead6aa,sky:0xdcecf0},play:{name:'놀이터',sub:'그네와 장난감이 있는 쉼터',ground:0xd1bda0,sky:0xf0e7dd}};
 const colors={apricot:{name:'살구',hex:0xcb8669,css:'#cb8669'},mint:{name:'민트',hex:0x729c89,css:'#729c89'},lavender:{name:'라벤더',hex:0x9383a7,css:'#9383a7'}};
 const surfaces={wood:{name:'나무',sub:'결이 보이는 따뜻한 판자'},stone:{name:'돌',sub:'작은 돌을 쌓은 단단한 벽'},fabric:{name:'패브릭',sub:'촘촘하게 짜인 부드러운 벽'}};
 const valid=v=>v&&places[v.place]&&colors[v.color]&&surfaces[v.material];
 const initial={place:'meadow',color:'apricot',material:'wood'};
 let saved=null;try{const s=JSON.parse(localStorage.getItem(KEY));if(s?.schema===1&&valid(s.value))saved=s.value}catch{}
 const state={committed:saved?{...saved}:null,draft:{...(saved||initial)},step:0,open:false,result:false,revision:0,renderer:'pending',storage:'unknown',activity:null};
 const history=[];let oldMode='title',sceneGroup=null,renderer=null,ctx=null,frame=0,previousFocus=null,animationStart=0,startedAt=0,liveUntil=0;
 const textures=new Map(),reduced=matchMedia('(prefers-reduced-motion: reduce)');
 const css=document.createElement('style');css.textContent=`
 #choiceStudio{position:fixed;inset:0;z-index:250;background:#f4f0e7;color:#3c443a;overflow:auto;overscroll-behavior:contain;font-family:system-ui,sans-serif;touch-action:pan-y}
 #choiceStudio[hidden]{display:none!important}#choiceStudio *{box-sizing:border-box}#choiceStudio button{font-family:inherit;color:inherit;margin:0;min-height:46px;border-radius:15px;border:1px solid #c8c9ba;background:#fbfaf5;box-shadow:none;cursor:pointer;letter-spacing:0}
 #choiceStudio button:focus-visible{outline:3px solid #4f796b;outline-offset:2px}#choiceStudio button:disabled{opacity:.4;cursor:default}
 .csShell{width:min(100%,760px);margin:auto;padding:14px 18px max(14px,env(safe-area-inset-bottom));min-height:100dvh;display:flex;flex-direction:column;gap:12px}
 .csHead{display:flex;align-items:center;justify-content:space-between;gap:12px}.csHead p{margin:0;font-size:12px;color:#6a7467}.csHead h1{font-size:23px;margin:2px 0;line-height:1.3}.csHead button{min-width:46px;font-size:23px}
 .csView{position:relative;overflow:hidden;border-radius:24px;background:#e5eddd;min-height:195px;height:clamp(220px,40dvh,350px);border:1px solid #d6d9cb}.csView canvas{width:100%;height:100%;display:block}.csCaption{position:absolute;left:12px;top:10px;padding:5px 9px;border-radius:20px;font-size:12px;background:#fbfaf5e8;pointer-events:none}
 .csSteps{display:flex;gap:7px}.csSteps button{flex:1;padding:8px 3px;font-size:13px;font-weight:650}.csSteps button[aria-selected=true]{background:#506f60!important;color:#fffaf0!important;border-color:#506f60!important}
 .csQuestion h2{font-size:18px;margin:2px 0 3px}.csQuestion p{font-size:12px;color:#6a7467;margin:0;line-height:1.5}
 .csOptions{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px}.csOptions button{display:flex;align-items:center;flex-direction:column;justify-content:center;padding:9px 4px;min-height:102px!important;border:2px solid transparent!important;background:#fffdf7!important;position:relative}.csOptions button[aria-pressed=true]{border-color:#507361!important;background:#edf2e8!important}.csOptions button[aria-pressed=true]:after{content:'✓';position:absolute;top:4px;right:7px;color:#507361;font-size:13px}.csOptions svg{width:80px;max-width:100%;height:50px;margin:0 0 5px}.csOptions strong{font-size:14px}.csOptions small{font-size:10px;margin-top:3px;color:#6a7467}
 .csFoot{margin-top:auto;display:flex;flex-direction:column;gap:8px;padding-top:3px}.csActions{display:flex;gap:9px}.csActions button{flex:1;padding:10px;font-size:14px;font-weight:700}.csActions button.csPrimary{background:#506f60!important;border-color:#506f60!important;color:#fffaf0!important;flex:2}.csSave{min-height:18px;font-size:11px;color:#6a7467;margin:0;text-align:center}.csResultTitle{font-size:20px;margin:0;text-align:center}.csResultSub{margin:0;text-align:center;color:#6a7467;font-size:13px;line-height:1.6}
 #choiceStudio.csResult .csView{height:clamp(260px,55dvh,470px)}#choiceStudio.csResult .csEditor{display:none}.csResultOnly{display:none}#choiceStudio.csResult .csResultOnly{display:block}.csEditOnly{display:block}.csActions.csEditOnly{display:flex}#choiceStudio.csResult .csActions.csResultOnly{display:flex}#choiceStudio.csResult .csEditOnly{display:none}
 #cozyOpenStudio{font-size:13px!important;min-width:70px!important}body.cs-active #cozyCare,body.cs-active #cozyReviewDock{visibility:hidden!important}
 @media(max-width:400px){.csShell{padding:11px 13px max(11px,env(safe-area-inset-bottom));gap:9px}.csView{height:clamp(190px,38dvh,330px);min-height:190px}.csHead h1{font-size:21px}.csOptions button{min-height:94px!important}.csOptions svg{height:44px}.csQuestion h2{font-size:16px}}
 @media(prefers-reduced-motion:reduce){#choiceStudio *{animation:none!important;transition:none!important}}
 `;document.head.append(css);
 const el=document.createElement('section');el.id='choiceStudio';el.hidden=true;el.setAttribute('role','dialog');el.setAttribute('aria-modal','true');el.setAttribute('aria-labelledby','csTitle');
 el.innerHTML=`<div class="csShell"><header class="csHead"><div><p>냥누리 · 내가 고른 풍경</p><h1 id="csTitle">내 공간 꾸미기</h1></div><button id="csClose" aria-label="꾸미기 닫기">×</button></header><div class="csView"><canvas id="csCanvas" aria-label="선택한 장소·색상·재질의 미리보기"></canvas><span class="csCaption" id="csCaption"></span></div><div class="csEditor"><nav class="csSteps" role="tablist" aria-label="꾸미기 단계"><button role="tab" data-step="0">1 장소</button><button role="tab" data-step="1">2 색상</button><button role="tab" data-step="2">3 재질</button></nav><div class="csQuestion"><h2 id="csQuestion"></h2><p id="csHint">그림을 누르면 위의 풍경이 바로 바뀌어요.</p></div><div class="csOptions" id="csOptions" role="group"></div></div><h2 class="csResultOnly csResultTitle" id="csResultTitle"></h2><p class="csResultOnly csResultSub" id="csResultSub"></p><footer class="csFoot"><div class="csActions csEditOnly"><button id="csBack">이전</button><button id="csNext" class="csPrimary">다음: 색 고르기</button></div><div class="csActions csResultOnly"><button id="csUndo">이전 모습</button><button id="csEdit" class="csPrimary">다시 꾸미기</button></div><p class="csSave" id="csSave" role="status" aria-live="polite">마지막에 ‘내 공간 만들기’를 누르면 저장돼요.</p></footer></div>`;
 document.body.append(el);let canvas=$('#csCanvas');
 const activityButton=document.createElement('button');activityButton.id='csActivity';activityButton.className='csResultOnly';activityButton.style.cssText='width:100%;font-size:15px;font-weight:700';el.querySelector('.csFoot').prepend(activityButton);
 function icon(kind,id){
  let body='';
  if(kind==='place'){
   const ground=id==='meadow'?'#94af77':id==='coast'?'#ead6aa':'#d4bfa4';body=`<ellipse cx="40" cy="38" rx="36" ry="12" fill="${ground}"/>`;
   if(id==='meadow')body+='<path d="M22 33V17M59 33V20" stroke="#806b4e" stroke-width="4"/><circle cx="22" cy="16" r="10" fill="#678967"/><circle cx="59" cy="18" r="8" fill="#91a77d"/><path d="M40 39v-7M49 40v-7" stroke="#678967"/><circle cx="40" cy="31" r="3" fill="#f1d47b"/><circle cx="49" cy="32" r="3" fill="#d8a5ad"/>';
   if(id==='coast')body+='<path d="M7 36Q20 27 34 35T73 35V44Q40 53 8 43Z" fill="#78b9c2"/><path d="M12 37q10-7 19 0t18 0" fill="none" stroke="#eef8ef" stroke-width="2"/><path d="M56 33V17M45 19Q56 4 67 19Z" fill="#c58b75" stroke="#8b7153" stroke-width="2"/>';
   if(id==='play')body+='<path d="M17 39L23 12H60L67 39M23 12L31 39" fill="none" stroke="#8b7153" stroke-width="3"/><path d="M37 14v17M51 14v17" stroke="#776854"/><path d="M34 32h21" stroke="#729c89" stroke-width="5"/><circle cx="15" cy="39" r="5" fill="#d49a76"/>';
  }else if(kind==='color'){const c=colors[id].css;body=`<path d="M18 23H62V47H18Z" fill="#e1cbb0"/><path d="M10 25L40 4L70 25Z" fill="${c}"/><path d="M34 47V33H46V47" fill="#7b6751"/><path d="M24 30h7v7h-7M50 30h7v7h-7" fill="#fff1b8"/>`}
  else{body='<rect x="8" y="6" width="64" height="40" rx="5" fill="#d2bda0"/>';
   if(id==='wood')body+='<path d="M8 18h64M8 32h64M24 6v12M56 18v14M33 32v14M13 12q17-6 34 0M28 26q16-5 35 0" fill="none" stroke="#8d7153" stroke-width="1.5"/>';
   if(id==='stone')body+='<path d="M8 19h64M8 32h64M28 6v13M52 6v13M17 19v13M43 19v13M63 19v13M28 32v14M53 32v14" stroke="#8f8c80" stroke-width="3"/>';
   if(id==='fabric')body+='<path d="M8 14h64M8 22h64M8 30h64M8 38h64M18 6v40M28 6v40M38 6v40M48 6v40M58 6v40M68 6v40" stroke="#a99883" opacity=".75"/>';
  }return `<svg viewBox="0 0 80 52" aria-hidden="true">${body}</svg>`;
 }
 function renderControls(){
  el.classList.toggle('csResult',state.result);$('#csTitle').textContent=state.result?'내가 만든 공간':'내 공간 꾸미기';
  const p=state.draft,key=['place','color','material'][state.step],data=[places,colors,surfaces][state.step];
  $('#csQuestion').textContent=['어디에서 지낼까요?','어떤 빛깔이 좋을까요?','무엇으로 지을까요?'][state.step];
  $('#csOptions').setAttribute('aria-label',['장소 선택','색상 선택','재질 선택'][state.step]);
  $('#csOptions').innerHTML=Object.entries(data).map(([id,v])=>`<button type="button" data-option="${id}" aria-label="${v.name}" aria-pressed="${p[key]===id}">${icon(key,id)}<strong>${v.name}</strong>${key==='material'?`<small>${id==='wood'?'따뜻한 결':id==='stone'?'단단한 돌':'부드러운 짜임'}</small>`:''}</button>`).join('');
  el.querySelectorAll('[data-step]').forEach(b=>b.setAttribute('aria-selected',+b.dataset.step===state.step?'true':'false'));
  $('#csBack').disabled=state.step===0;$('#csNext').textContent=['다음: 색 고르기','다음: 재질 고르기','내 공간 만들기'][state.step];
  $('#csCaption').textContent=`${places[p.place].name} · ${colors[p.color].name} · ${surfaces[p.material].name}`;
  $('#csResultTitle').textContent=`${colors[p.color].name}빛 ${places[p.place].name}`;
  $('#csResultSub').textContent=`${surfaces[p.material].name} 집과 고양이가 있는, 내가 고른 풍경.\n다시 꾸미면 새로운 모습이 만들어져요.`;
  $('#csUndo').disabled=history.length===0;
  activityButton.textContent={meadow:'🌼 꽃 피우기',coast:'🐟 물고기 만나기',play:'🧶 같이 놀기'}[p.place];
 }
 function texture(kind){
  if(textures.has(kind))return textures.get(kind);
  const c=document.createElement('canvas');c.width=c.height=128;const x=c.getContext('2d');x.fillStyle=kind==='stone'?'#d6d3c6':kind==='fabric'?'#dbcebb':'#d4b489';x.fillRect(0,0,128,128);
  x.strokeStyle=kind==='stone'?'#aaa99e':kind==='fabric'?'#b0a28e':'#a27d54';x.lineWidth=kind==='stone'?4:1;
  const step=kind==='fabric'?6:32;
  for(let y=0;y<128;y+=step){x.beginPath();x.moveTo(0,y);x.lineTo(128,y);x.stroke();if(kind==='wood'){x.lineWidth=.6;for(let d=7;d<24;d+=7){x.beginPath();x.moveTo(0,y+d);x.bezierCurveTo(30,y+d-3,75,y+d+3,128,y+d);x.stroke()}}}
  if(kind==='stone')for(let y=0;y<128;y+=32)for(let z=(y/32)%2?24:0;z<128;z+=48){x.beginPath();x.moveTo(z,y);x.lineTo(z,y+32);x.stroke()}
  if(kind==='fabric')for(let z=0;z<128;z+=6){x.beginPath();x.moveTo(z,0);x.lineTo(z,128);x.stroke()}
  const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.wrapS=t.wrapT=THREE.RepeatWrapping;textures.set(kind,t);return t;
 }
 const scene=new THREE.Scene();scene.add(new THREE.HemisphereLight(0xfff5df,0x8eaa8a,2.5));const sun=new THREE.DirectionalLight(0xffedc7,3.1);sun.position.set(-8,15,12);scene.add(sun);
 const camera=new THREE.OrthographicCamera(-9,9,6,-6,.1,100);camera.position.set(13,12,17);camera.lookAt(0,1,0);
 function box(parent,x,y,z,w,h,d,color,map=null){const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),new THREE.MeshStandardMaterial({color,map,roughness:state.draft.material==='stone'?1:.78}));m.position.set(x,y,z);parent.add(m);return m}
 function sphere(parent,x,y,z,r,color){const m=new THREE.Mesh(new THREE.SphereGeometry(r,12,8),new THREE.MeshStandardMaterial({color,roughness:.85}));m.position.set(x,y,z);parent.add(m);return m}
 function cloneOwnMaterials(root,p){root.traverse(o=>{if(!o.isMesh)return;const old=o.material;o.geometry=o.geometry.clone();o.material=old.clone();if(old===M.roof)o.material.color.setHex(colors[p.color].hex);if(old===M.wood2){o.material.color.setHex(0xffffff);o.material.map=texture(p.material);o.material.roughness=p.material==='stone'?1:p.material==='fabric'?.95:.7}})}
 function build(){
  if(sceneGroup){scene.remove(sceneGroup);sceneGroup.traverse(o=>{o.geometry?.dispose();if(o.material)o.material.dispose()})}
  const p=state.draft,env=places[p.place],color=colors[p.color].hex;scene.background=new THREE.Color(env.sky);sceneGroup=new THREE.Group();scene.add(sceneGroup);
  box(sceneGroup,0,-.38,0,11,.65,8.5,0xb1a18a);box(sceneGroup,0,-.02,0,11,.12,8.5,env.ground);
  box(sceneGroup,1.55,.12,.1,4.8,.13,5.2,0xffffff,texture(p.material));
  const house=building('house');cloneOwnMaterials(house,p);house.position.set(1.55,.2,-.6);house.scale.setScalar(.85);sceneGroup.add(house);
  const kitty=cat('calico');cloneOwnMaterials(kitty,p);kitty.position.set(1.2,.15,2.85);kitty.scale.setScalar(.56);kitty.rotation.y=-.25;sceneGroup.add(kitty);sceneGroup.userData.kitty=kitty;
  for(let i=0;i<4;i++)box(sceneGroup,-.5+i*.6,.12,3.1,.5,.12,.65,0xf0e4c9);
  if(p.place==='meadow'){
   for(const [x,z,r]of[[-3,-2,1.1],[-4,1,.8],[4,-3,.7]]){box(sceneGroup,x,.9,z,.26,1.9,.26,0x8b7050);sphere(sceneGroup,x,2.2,z,r,0x6c9569);sphere(sceneGroup,x+.3,2.6,z-.1,r*.7,0x8ca879)}
   for(let i=0;i<22;i++){const x=-4.6+(i%6)*.66,z=-2.7+Math.floor(i/6)*1.6;box(sceneGroup,x,.2,z,.045,.32,.045,0x68885d);sphere(sceneGroup,x,.4,z,.13,[0xebc67d,0xd5a7b0,0xf0ebd2][i%3])}
  }else if(p.place==='coast'){
   box(sceneGroup,-3.5,.09,0,3.5,.16,8.4,0x7cb9c2);for(let i=0;i<7;i++)box(sceneGroup,-3.6+(i%2)*.22,.19,-3.4+i*1.05,2.1,.035,.055,0xeaf6ee);
   box(sceneGroup,-1.7,.7,-2.8,.09,1.5,.09,0x8b7050);const umbrella=new THREE.Mesh(new THREE.ConeGeometry(.95,.45,12),new THREE.MeshStandardMaterial({color}));umbrella.position.set(-1.7,1.65,-2.8);sceneGroup.add(umbrella);
   for(let i=0;i<5;i++)sphere(sceneGroup,-1.6,.15,1.8+i*.4,.15,0xf3ead1);
  }else{
   for(const x of[-4,-1.4]){const beam=box(sceneGroup,x,1.5,-1,.18,3,.18,0x8b7050);beam.rotation.z=x<-2?-.15:.15}
   box(sceneGroup,-2.7,3.0,-1,3.1,.2,.22,color);for(const x of[-3.2,-2.2])box(sceneGroup,x,1.9,-1,.035,2.1,.035,0x645947);
   const seat=box(sceneGroup,-2.7,.9,-1,1.4,.14,.8,color);sceneGroup.userData.seat=seat;
   const seesaw=box(sceneGroup,-3.2,.53,2,3,.15,.65,color);seesaw.rotation.z=.12;box(sceneGroup,-3.2,.23,2,.5,.5,.6,0x8b7050);sphere(sceneGroup,-1,.43,2.7,.38,0xe4b478);
  }
  state.activity=null;state.revision++;resize();
 }
 function initRenderer(){
  if(renderer||ctx)return;
  try{renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:false});renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.5));renderer.outputColorSpace=THREE.SRGBColorSpace;state.renderer='3d'}catch{
   const next=canvas.cloneNode();canvas.replaceWith(next);canvas=next;ctx=canvas.getContext('2d');state.renderer='2d';
  }
 }
 function resize(){if(!state.open)return;const r=canvas.parentElement.getBoundingClientRect(),w=Math.max(1,r.width),h=Math.max(1,r.height);if(renderer){renderer.setSize(w,h,false);camera.left=-8.2;camera.right=8.2;camera.top=8.2*h/w;camera.bottom=-8.2*h/w;camera.updateProjectionMatrix()}else if(ctx){canvas.width=Math.round(w*1.3);canvas.height=Math.round(h*1.3)}}
 function draw2D(t){
  const p=state.draft,w=canvas.width,h=canvas.height,x=ctx,s=Math.min(w/470,h/270);x.setTransform(1,0,0,1,0,0);x.fillStyle='#'+places[p.place].sky.toString(16);x.fillRect(0,0,w,h);x.translate(w/2,h*.55);x.scale(s,s);
  const poly=(points,fill)=>{x.fillStyle=fill;x.beginPath();points.forEach((q,i)=>i?x.lineTo(...q):x.moveTo(...q));x.closePath();x.fill()};
  poly([[-208,-14],[-38,-88],[208,-5],[40,88]],'#'+places[p.place].ground.toString(16));poly([[-208,-14],[40,88],[40,99],[-208,-3]],'#a6967f');poly([[40,88],[208,-5],[208,6],[40,99]],'#b9a48a');
  if(p.place==='coast'){poly([[-208,-14],[-132,-47],[-17,38],[40,88]],'#79b8c2');x.strokeStyle='#e6f5ef';x.lineWidth=3;for(let i=0;i<4;i++){x.beginPath();x.moveTo(-187+i*38,-11+i*22);x.quadraticCurveTo(-170+i*38,-23+i*22,-148+i*38,2+i*22);x.stroke()}}
  if(p.place==='meadow'){for(const [a,b]of[[-142,-34],[-96,-64]]){x.fillStyle='#8b7050';x.fillRect(a-4,b-31,8,38);x.fillStyle='#6c9569';x.beginPath();x.arc(a,b-45,26,0,Math.PI*2);x.fill()}for(let i=0;i<15;i++){x.fillStyle=['#edcc7f','#d9acb3','#f8eedb'][i%3];x.beginPath();x.arc(-177+(i%5)*28,10+Math.floor(i/5)*14,3,0,Math.PI*2);x.fill()}}
  if(p.place==='play'){x.strokeStyle='#806a50';x.lineWidth=6;x.beginPath();x.moveTo(-165,24);x.lineTo(-145,-67);x.lineTo(-55,-40);x.lineTo(-40,47);x.moveTo(-145,-67);x.lineTo(-120,37);x.stroke();x.lineWidth=2;for(const a of[-124,-85]){x.beginPath();x.moveTo(a,-48);x.lineTo(a,-1);x.stroke()}x.fillStyle=colors[p.color].css;x.fillRect(-130,-1,50,9);x.beginPath();x.arc(-102,50,12,0,Math.PI*2);x.fill()}
  const pat=x.createPattern(texture(p.material).image,'repeat');poly([[-14,-38],[77,-10],[77,58],[-14,27]],pat);poly([[77,-10],[139,-48],[139,22],[77,58]],'#baa88d');poly([[-29,-42],[40,-104],[156,-53],[83,4]],colors[p.color].css);
  x.fillStyle='#6d5a49';x.fillRect(17,-1,23,38);x.fillStyle='#fff0b8';x.fillRect(50,-2,15,18);x.strokeStyle='#f4e5c6';x.lineWidth=2;x.strokeRect(50,-2,15,18);
  // Wordless original calico silhouette, matching the SOL cat's angular form.
  x.save();x.translate(111,58+(reduced.matches?0:Math.sin(t*.002)*1.5));x.fillStyle='#f0e5ce';x.fillRect(-13,-15,24,15);x.fillRect(-11,-33,24,22);poly([[-11,-32],[-11,-44],[-1,-34]],'#f0e5ce');poly([[4,-34],[13,-44],[13,-31]],'#c98449');x.fillStyle='#c98449';x.fillRect(-11,-29,10,10);x.fillStyle='#463d34';x.fillRect(5,-27,8,12);x.fillStyle='#354b34';x.fillRect(-7,-23,3,4);x.fillRect(4,-23,3,4);x.restore();
  if(state.result&&t<liveUntil){x.fillStyle='#a96665';x.font='22px system-ui';x.fillText('♡',102,14)}
  if(state.activity==='bloom'){for(let i=0;i<5;i++){x.fillStyle='#ebc67d';x.beginPath();x.arc(-140+i*21,12+(i%2)*14,7,0,Math.PI*2);x.fill();x.fillStyle='#fff3ce';x.beginPath();x.arc(-140+i*21,12+(i%2)*14,2,0,Math.PI*2);x.fill()}}
  if(state.activity==='fish'&&t<liveUntil){x.fillStyle='#f8e8bd';x.beginPath();x.ellipse(-95,12-Math.abs(Math.sin((liveUntil-t)*.003))*22,14,7,0,0,Math.PI*2);x.fill()}
  if(state.activity==='play'&&t<liveUntil){x.fillStyle=colors[p.color].css;x.beginPath();x.arc(-102+Math.sin(t*.003)*22,49,12,0,Math.PI*2);x.fill()}
 }
 function animate(t){if(!state.open)return;const ratio=reduced.matches?1:Math.min(1,(t-animationStart)/450);if(sceneGroup){sceneGroup.scale.setScalar(.94+.06*ratio);const seat=sceneGroup.userData.seat;if(seat&&!reduced.matches)seat.rotation.x=Math.sin(t*.0014)*(state.activity==='play'&&t<liveUntil?.35:.08);const kitty=sceneGroup.userData.kitty;if(kitty)kitty.position.y=.15+(state.activity&&t<liveUntil&&!reduced.matches?Math.abs(Math.sin(t*.006))*.25:0);const fish=sceneGroup.userData.fish;if(fish)fish.position.y=.3+(reduced.matches?.45:Math.abs(Math.sin(t*.003))*1.1)}if(renderer)renderer.render(scene,camera);else draw2D(t);frame=requestAnimationFrame(animate)}
 const originalRender=g.renderer.render.bind(g.renderer);g.renderer.render=(...args)=>{if(!state.open)return originalRender(...args)};
 function open(result=false){if(g.cut||g.storyLock)return;previousFocus=document.activeElement;oldMode=g.mode;state.open=true;state.result=!!(result&&state.committed);state.draft={...(state.committed||initial)};state.step=0;g.mode='customizing';window.MeownuriCozy?.cancel();document.body.classList.add('cs-active');el.hidden=false;initRenderer();build();renderControls();$('#csSave').textContent=state.result?'이 브라우저에 저장된 나의 공간이에요.':'마지막에 ‘내 공간 만들기’를 누르면 저장돼요.';animationStart=performance.now();frame=requestAnimationFrame(animate);$('#csClose').focus()}
 function close(){state.open=false;cancelAnimationFrame(frame);el.hidden=true;document.body.classList.remove('cs-active');g.mode=oldMode;previousFocus?.focus?.()}
 function commit(){if(!valid(state.draft))return;if(state.committed)history.push({...state.committed});state.committed={...state.draft};state.result=true;state.storage='saved';try{localStorage.setItem(KEY,JSON.stringify({schema:1,value:state.committed}))}catch{state.storage='failed'}animationStart=performance.now();liveUntil=animationStart+1800;g.audio.unlock();g.audio.play('complete');renderControls();$('#csSave').textContent=state.storage==='saved'?'✓ 이 브라우저에 내 공간이 저장됐어요.':'화면에 반영했어요. 브라우저 저장은 사용할 수 없어요.';$('#csEdit').focus()}
 $('#csOptions').onclick=e=>{const b=e.target.closest('[data-option]');if(!b)return;const key=['place','color','material'][state.step];state.draft[key]=b.dataset.option;animationStart=performance.now();build();renderControls()};
 el.querySelectorAll('[data-step]').forEach(b=>b.onclick=()=>{state.step=+b.dataset.step;renderControls()});
 $('#csNext').onclick=()=>{if(state.step<2){state.step++;renderControls()}else commit()};$('#csBack').onclick=()=>{state.step=Math.max(0,state.step-1);renderControls()};
 $('#csClose').onclick=close;$('#csEdit').onclick=()=>{state.result=false;state.step=0;renderControls();$('#csSave').textContent='새로 만들기 전까지 저장된 모습은 그대로예요.'};
 $('#csUndo').onclick=()=>{if(!history.length)return;state.draft=history.pop();state.committed={...state.draft};try{localStorage.setItem(KEY,JSON.stringify({schema:1,value:state.committed}));state.storage='saved'}catch{state.storage='failed'}build();renderControls();$('#csSave').textContent=state.storage==='saved'?'✓ 이전 모습으로 돌아왔어요.':'이전 모습으로 돌아왔어요. 저장은 사용할 수 없어요.'};
 activityButton.onclick=()=>{if(!state.result)return;liveUntil=performance.now()+2500;g.audio.unlock();
  if(state.draft.place==='meadow'){state.activity='bloom';if(!sceneGroup.userData.bloom){for(let i=0;i<5;i++){const x=-4+i*.6;box(sceneGroup,x,.28,2,.04,.5,.04,0x6c9569);sphere(sceneGroup,x,.6,2,.22,0xebc67d)}sceneGroup.userData.bloom=true}g.audio.play('gather')}
  else if(state.draft.place==='coast'){state.activity='fish';if(!sceneGroup.userData.fish){const f=new THREE.Group();const body=sphere(f,0,0,0,.28,0xf4e4b4);body.scale.set(1.6,.6,.6);box(f,-.45,0,0,.2,.2,.06,0xc58b75);f.position.set(-3,.5,1.7);sceneGroup.add(f);sceneGroup.userData.fish=f}g.audio.play('fish')}
  else{state.activity='play';g.audio.play('home')}
 };
 canvas.onclick=()=>{if(state.result)activityButton.click()};
 el.addEventListener('keydown',e=>{e.stopPropagation();if(e.key==='Escape'){e.preventDefault();close()}if(e.key==='Tab'){const focusable=[...el.querySelectorAll('button:not(:disabled)')].filter(x=>x.getClientRects().length);if(e.shiftKey&&document.activeElement===focusable[0]){e.preventDefault();focusable.at(-1).focus()}else if(!e.shiftKey&&document.activeElement===focusable.at(-1)){e.preventDefault();focusable[0].focus()}}});
 new ResizeObserver(()=>resize()).observe(canvas.parentElement);
 const launcher=document.createElement('button');launcher.id='cozyOpenStudio';launcher.textContent='🎨 꾸미기';launcher.onclick=()=>open(!!state.committed);$('#cozyReviewDock')?.prepend(launcher);
 window.MeownuriChoices={state,open,close,commit,places,colors,surfaces};
 if(new URLSearchParams(location.search).get('customize')==='1')open(!!state.committed);
})();
