/* MEOWNURI SOL 5.6 LINEAGE · DAY 04–10 / v16.0
 * Source of truth: 냥누리 기획서 (2026-10-05), parts 2–4.
 * Wordless by design: no cat dialogue, no emotional narration; clear action labels only.
 * Does not modify ASTRA or the legacy v15.7 save format.
 */
import 'client';
import * as THREE from 'three';
(() => {
  'use strict';
  const g=window.game||window.__MEOWNURI9;
  if (!g || window.MeownuriStory) return;
  const $=s=>document.querySelector(s);
  const KEY='meownuri:sol:day04-10:v1';
  const D3_KEY='meownuri:day3';
  const read=(k,defaultValue)=>{try{return JSON.parse(localStorage.getItem(k))??defaultValue}catch(_){return defaultValue}};
  const put=(k,x)=>{try{localStorage.setItem(k,JSON.stringify(x))}catch(e){console.warn('Story save unavailable',e)}};
  const d3=()=>read(D3_KEY,{});
  const PLANS={
    4:{name:'길 위에서',place:'path',beats:[
      {id:'departure',label:'옛집을 돌아보고 길을 나서기',focus:'오래된 HOME 간판',emoji:'🏠',cast:['까미','모카'],scene:'farewell'},
      {id:'meet',label:'언덕 위의 두 고양이에게 다가가기',focus:'수풀',emoji:'🐈',cast:['호박','할미'],scene:'meeting'},
      {id:'roles',label:'모닥불 주변에 역할 표시 놓기',focus:'모닥불',emoji:'🔥',cast:['까미','모카','호박','할미'],scene:'roles'},
      {id:'gather',label:'낚시와 약초 수집 돕기',focus:'낚시터',emoji:'🐟',cast:['모카','호박','할미'],scene:'work'},
      {id:'night',label:'모닥불 옆에 앉기',focus:'모닥불',emoji:'🔥',cast:['까미','모카','호박','할미'],scene:'camp'}
    ]},
    5:{name:'밥그릇',place:'village',beats:[
      {id:'empty',label:'빈 밥그릇 조사하기',focus:'빈 밥그릇',emoji:'🥣',scene:'empty'},
      {id:'conflict',label:'모카와 호박 사이에 다가가기',focus:'모카와 호박',emoji:'🐈',scene:'conflict'},
      {id:'kitten',label:'작은 고양이에게 다가가기',focus:'콩이',emoji:'🐱',scene:'kitten'},
      {id:'share',label:'먹이를 어떻게 나눌지 선택',focus:'큰 밥그릇',emoji:'🥣',scene:'choice',choice:['모두 조금씩 나눈다','내 몫을 호박에게 준다','모카와 낚시를 간다'],choiceKey:'day5_share_choice'},
      {id:'together',label:'밥그릇을 가운데로 옮기기',focus:'큰 밥그릇',emoji:'🥣',scene:'share'}
    ]},
    6:{name:'그것이 돌아왔다',place:'village',beats:[
      {id:'warning',label:'까미가 가리키는 숲 살펴보기',focus:'숲',emoji:'🐾',scene:'warning'},
      {id:'plan',label:'여섯 고양이의 역할 확인하기',focus:'작전 지도',emoji:'🗺️',scene:'plan'},
      {id:'trap',label:'큰 밥그릇 작전 실행하기',focus:'경보줄',emoji:'🔔',scene:'trap'},
      {id:'rescue',label:'모카를 향해 달리기',focus:'모카',emoji:'🐟',scene:'rescue'},
      {id:'recovery',label:'쓰러진 호박 곁에 앉기',focus:'호박',emoji:'🐈',scene:'recovery'}
    ]},
    7:{name:'마을의 이름',place:'village',beats:[
      {id:'sign',label:'마을 간판 세우고 이름 정하기',focus:'빈 간판',emoji:'🪧',scene:'sign',choice:['냥누리 마을','모닥불 마을','발자국 마을'],choiceKey:'village_name'},
      {id:'everyone',label:'고양이들의 발자국 남기기',focus:'마을 간판',emoji:'🐾',scene:'everyone'},
      {id:'festival',label:'모닥불 축제 시작하기',focus:'모닥불',emoji:'🔥',scene:'festival'},
      {id:'consequence',label:'옛 선택의 흔적 확인하기',focus:'마을 입구',emoji:'🐾',scene:'consequence'},
      {id:'messenger',label:'왕국의 전령을 맞이하기',focus:'마을 입구',emoji:'📜',scene:'messenger'},
      {id:'villageEnd',label:'별이 뜬 마을 바라보기',focus:'언덕',emoji:'🌟',scene:'villageEnd'}
    ]},
    8:{name:'초대',place:'road',beats:[
      {id:'travel',label:'바람을 따라 먼 길 걷기',focus:'왕국으로 향하는 길',emoji:'🐾',scene:'travel'},
      {id:'gate',label:'대리석 성문 가까이 가기',focus:'성문',emoji:'🏰',scene:'gate'},
      {id:'memory',label:'까미가 멈춘 문 앞에 서기',focus:'작은 문',emoji:'🚪',scene:'memory'},
      {id:'king',label:'왕 레오를 향해 다가가기',focus:'왕좌',emoji:'👑',scene:'king'}
    ]},
    9:{name:'왕의 제안',place:'castle',beats:[
      {id:'offer',label:'레오가 가리키는 왕좌 살펴보기',focus:'왕좌',emoji:'👑',scene:'offer'},
      {id:'oldroom',label:'까미의 작은 방 살펴보기',focus:'작은 침대',emoji:'🧸',scene:'oldroom'},
      {id:'reunion',label:'레오와 까미의 재회 지켜보기',focus:'작은 방',emoji:'🐈‍⬛',scene:'reunion'},
      {id:'decision',label:'삼색이의 길 선택하기',focus:'세 갈래 길',emoji:'🛤️',scene:'decision',choice:['왕국에 남는다','마을로 돌아간다','두 누리를 잇는다'],choiceKey:'day9_kingdom_choice'}
    ]},
    10:{name:'어떤 세상',place:'castle',beats:[
      {id:'decisionResult',label:'선택한 길에 첫 발 내딛기',focus:'첫 걸음',emoji:'🐾',scene:'decisionResult'},
      {id:'worldChange',label:'새로운 세상의 모습 만들기',focus:'변화',emoji:'🌱',scene:'worldChange'},
      {id:'together',label:'친구들과 마지막 장면 만들기',focus:'친구들',emoji:'🐈',scene:'together'},
      {id:'footprints',label:'열흘간 남긴 발자국 돌아보기',focus:'발자국 지도',emoji:'🗺️',scene:'footprints'}
    ]}
  };
  const saved=read(KEY,null);
  const st=saved&&saved.schema===1&&saved.day>=4&&saved.day<=10 ? saved :
    {schema:1,day:0,beat:0,unlocked:4,finished:false,choices:{},visited:[],updated:new Date().toISOString()};
  const coord={path:{x:8,z:17},village:{x:23,z:5},road:{x:-25,z:26},castle:{x:-41,z:35}};
  const actors={};
  let currentProps=[],worldReady=false,blocked=false,interval=null;
  const props=[];
  g.storyProject={props, target:null, day:0};
  const actorTraits={
    '모카':{id:'sol-moka',coat:'gray',scale:.80},'호박':{id:'sol-hobak',coat:'orange',scale:1.11},
    '할미':{id:'sol-halmi',coat:'white',scale:.87},'콩이':{id:'sol-kongi',coat:'orange',scale:.54},
    '바람':{id:'sol-baram',coat:'gray',scale:.75},'레오':{id:'sol-leo',coat:'orange',scale:1.28}
  };
  function save(){st.updated=new Date().toISOString();put(KEY,st)}
  function getActor(n){if(n==='삼색이')return g.player;if(n==='까미')return g.friend;
    if(actors[n])return actors[n];
    const p=actorTraits[n];if(!p)return null;
    const a=g.actor(p.id,n,p.coat,coord.village.x,coord.village.z,p.scale);
    actors[n]=a;a.active=false;a.mesh.visible=false;return a;
  }
  function position(n,x,z,visible=true){const a=getActor(n);if(!a)return null;
    const y=g.ground.height(x,z);a.x=x;a.z=z;a.y=y;a.active=visible;a.mesh.visible=visible;
    a.mesh.position.set(x,y,z);return a;
  }
  function point(x,z,size=1,emoji=''){return {x,z,size,emoji,visible:true}}
  function meshBox(gr,x,y,z,w,h,d,color){const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),new THREE.MeshStandardMaterial({color,roughness:.82}));m.position.set(x,y,z);gr.add(m);return m}
  function ball(gr,x,y,z,r,color){const m=new THREE.Mesh(new THREE.SphereGeometry(r,10,8),new THREE.MeshStandardMaterial({color,roughness:.8}));m.position.set(x,y,z);gr.add(m);return m}
  function addProp(x,z,emoji,kind='marker',size=3){
    let nx=x,nz=z;if(!g.ground.inside(nx,nz)){nx=Math.max(-55,Math.min(55,nx));nz=Math.max(-55,Math.min(55,nz));}
    const group=new THREE.Group();group.position.set(nx,g.ground.height(nx,nz),nz);
    const wood=0x855332,stone=0xe6d7bf,soft=0xf5dc9a;
    if(kind==='fire'){
      for(let i=0;i<5;i++){const t=i*Math.PI*2/5;meshBox(group,Math.cos(t)*.4,.17,Math.sin(t)*.4,1.5,.23,.25,wood).rotation.y=t;}
      const flame=ball(group,0,.9,0,.55,0xffad38);flame.material.emissive=new THREE.Color(0xff5818);flame.material.emissiveIntensity=1.7;group.userData.flame=flame;
      const lamp=new THREE.PointLight(0xffa44e,2.4,13);lamp.position.y=1.4;group.add(lamp);
    }else if(kind==='sign'){
      meshBox(group,0,1.4,0,.2,2.8,.25,wood);
      meshBox(group,0,2.65,0,3.8,1.25,.28,soft);
      for(const dx of[-1.55,1.55])meshBox(group,dx,2.65,.18,.09,.9,.1,wood);
    }else if(kind==='bowl'){
      const m=new THREE.Mesh(new THREE.CylinderGeometry(1.25,.95,.5,24),new THREE.MeshStandardMaterial({color:0xb77954,roughness:.6}));m.position.y=.3;group.add(m);ball(group,0,.57,0,.85,0xe6b482);
    }else if(kind==='fish'){
      ball(group,0,.46,0,.65,0x6bb9d0);meshBox(group,.63,.45,0,.36,.26,.5,0x5e97b4);
    }else if(kind==='garden'){
      for(let i=0;i<9;i++){const t=i*Math.PI*2/9;ball(group,Math.cos(t)*1.3,.4,Math.sin(t)*1.3,.32,[0xe7b1b8,0xf6d77a,0xc3bedf][i%3]);}
    }else if(kind==='gate'){
      for(const dx of[-3,3])meshBox(group,dx,3.2,0,1.1,6.4,1.4,stone);
      meshBox(group,0,6.5,0,7.6,1.25,1.5,stone);
      for(const dx of[-3.4,3.4])ball(group,dx,7.2,0,.7,0xf2d7a0);
    }else if(kind==='throne'){
      meshBox(group,0,.45,0,2.4,.8,1.5,0xe8bd6b);meshBox(group,0,1.7,-.6,2.45,2.7,.5,0xd9ae5a);
    }else if(kind==='door'){
      meshBox(group,0,2.3,0,2.1,4.6,.4,0x8a5c44);
      ball(group,.72,2.2,.25,.1,soft);
    }else if(kind==='bed'){
      meshBox(group,0,.22,0,2.6,.35,1.6,0x8f6544);meshBox(group,0,.48,0,2.4,.24,1.4,0xffe9c9);
      ball(group,-.7,.7,-.5,.38,0xf3e0b5);
    }else if(kind==='tree'){
      meshBox(group,0,1,0,.55,2.2,.55,wood);
      ball(group,0,3,0,1.5,0x669758);ball(group,.6,2.8,.2,.9,0x77a962);
    }else{
      ball(group,0,.38,0,.45,[0xffd28f,0x8aab74,0xd1ab92][Math.abs(Math.floor(nx+nz))%3]);
    }
    g.scene.add(group);const entry={x:nx,z:nz,emoji,kind,size,visible:true,group};props.push(entry);currentProps.push(entry);return entry;
  }
  function removeProps(){for(const obj of currentProps){obj.visible=false;g.scene.remove(obj.group);obj.group.traverse(o=>{if(o.geometry)o.geometry.dispose();if(o.material)o.material.dispose()})}currentProps=[];props.length=0}
  function landmark(b){
    const p=coord[currentPlace(st.day)];
    const points={departure:[-4,0],meet:[3,1],roles:[2,-3],gather:[6,4],night:[0,-2],empty:[0,1],conflict:[3,0],kitten:[-1,-3],share:[0,1],together:[0,1],warning:[3,5],plan:[0,0],trap:[7,3],rescue:[5,2],recovery:[0,1],sign:[-2,1],everyone:[-2,1],festival:[1,0],consequence:[6,-1],messenger:[7,-2],villageEnd:[-3,-2],travel:[-2,2],gate:[4,0],memory:[3,-4],king:[0,-3],offer:[0,-3],oldroom:[3,-4],reunion:[3,-4],decision:[0,-3],decisionResult:[0,-3],worldChange:[0,0],footprints:[0,0]};
    const delta=points[b.id]||[0,0];return {x:p.x+delta[0],z:p.z+delta[1]};
  }
  function placeAt(x,z,offset=4){
    const q=g.ground.nearest(x-offset,z+offset,.66,g.actors.filter(a=>a!==g.player))||{x,z};
    g.player.x=q.x;g.player.z=q.z;g.player.y=g.ground.height(q.x,q.z);
    g.player.mesh.position.set(q.x,g.player.y,q.z);
    g.distance=g.mobile?14:12;g.pitch=.64;g.yaw=.42;
    g.camera.position.set(q.x-7,g.player.y+9,q.z-9);g.camera.lookAt(q.x,g.player.y,q.z);
  }
  const currentPlace=day=>day===10?(st.choices.day9_kingdom_choice===1?'village':st.choices.day9_kingdom_choice===2?'road':'castle'):PLANS[day].place;
  function createWorld(day){
    removeProps(); const p=coord[currentPlace(day)];
    if(day===4){
      addProp(p.x,p.z,'🔥','fire');addProp(p.x+6,p.z+4,'🐟','fish');addProp(p.x-4,p.z,'🪧','sign');
      addProp(p.x+8,p.z-7,'🌳','tree');
    }else if(day>=5&&day<=7){
      addProp(p.x+1,p.z,'🔥','fire');addProp(p.x-2,p.z+1,'🥣','bowl');
      addProp(p.x+6,p.z+3,'🪧','sign');addProp(p.x-6,p.z-4,'🌳','tree');
      if(day>=7)addProp(p.x+5,p.z-5,'🌼','garden');
    }else if(day===10 && st.choices.day9_kingdom_choice===1){
      addProp(p.x,p.z,'🏘️','sign');addProp(p.x+3,p.z,'🔥','fire');addProp(p.x-3,p.z-2,'🎏','marker');
    }else if(day===10 && st.choices.day9_kingdom_choice===2){
      addProp(p.x,p.z,'🌈','garden');addProp(p.x+7,p.z,'🏰','gate');addProp(p.x-5,p.z-2,'🪧','sign');
    }else{
      addProp(coord.road.x+2,coord.road.z,'🏰','gate',4);
      addProp(coord.castle.x+4,coord.castle.z+1,'🏰','gate',4);
      addProp(coord.castle.x,coord.castle.z-3,'👑','throne',4);
      addProp(coord.castle.x+3,coord.castle.z-4,'🚪','door');
      addProp(coord.castle.x+5,coord.castle.z-6,'🧸','bed');
      if(day===10)addProp(coord.castle.x,coord.castle.z,'🌱','garden',4);
    }
    worldReady=true;
  }
  function cast(day){
    const base=coord[currentPlace(day)];const names=day===4?['까미','모카','호박','할미']:
        day>=5&&day<=7?['까미','모카','호박','할미','콩이']:
        ['까미','모카','호박','할미','콩이','바람','레오'];
    g.friend.active=true;g.friend.mesh.visible=true;
    for(let i=0;i<names.length;i++){const nm=names[i],t=i/Math.max(1,names.length)*Math.PI*2;
      position(nm,base.x+Math.cos(t)*3,base.z+Math.sin(t)*3,true);
    }
    for(const [name,a]of Object.entries(actors))if(!names.includes(name)){a.active=false;a.mesh.visible=false;}
  }
  function gesture(name,kind='happy',duration=1.8){const a=getActor(name);if(a&&a.active)g.gesture(a,kind,duration)}
  function objective(b){
    const spot=landmark(b),dist=Math.hypot(g.player.x-spot.x,g.player.z-spot.z);
    return {spot,dist,near:dist<2.8};
  }
  function actionUI(){
    const node=$('#solStoryAction');if(!node||!st.day||st.finished)return;
    const plan=PLANS[st.day],b=plan.beats[st.beat];if(!b)return;
    const s=objective(b);node.disabled=!s.near||blocked;
    node.textContent=s.near?(b.choice?'✦ 선택하기':'🐾 '+b.label):'🐾 표시된 곳으로 이동 ('+Math.ceil(s.dist)+'m)';
    $('#solStoryProgress').textContent=`DAY ${st.day} · ${st.beat+1}/${plan.beats.length}`;
    $('#solStoryLabel').textContent=b.emoji+' '+plan.name;
  }
  function applyBeatVisual(b){
    const m=landmark(b),p=coord[currentPlace(st.day)];
    const spread=st.day>=8?4.5:5.3;
    const active=Object.values(actors).filter(x=>x.active);
    const cats=[g.friend,...active];
    cats.forEach((a,i)=>{const t=2*Math.PI*i/Math.max(1,cats.length);a.x=m.x+Math.cos(t)*spread;a.z=m.z+Math.sin(t)*spread;a.y=g.ground.height(a.x,a.z);a.mesh.position.set(a.x,a.y,a.z)});
    // End-of-day tableau composition: everyone sees the same symbolic place, no speaking.
    if(['night','together','recovery','villageEnd','king','reunion','footprints'].includes(b.id)){
      const a=g.friend; if(a)g.gesture(a,'shy',2.5);
    }
    if(['meet','night','kitten','everyone','festival','villageEnd','gate','reunion','together'].includes(b.id)){
      for(const n of ['호박','콩이'])if(getActor(n)?.active)gesture(n,'happy',1.6);
    }
    if(b.id==='conflict'){gesture('모카','shy');gesture('호박','upset');}
    if(b.id==='together'){
      const ch=st.choices.day5_share_choice??0;
      if(ch===0){gesture('모카','happy',2);gesture('호박','happy',2);}
      else if(ch===1){gesture('호박','shy',3);gesture('까미','happy',2);}
      else{gesture('모카','happy',2);addProp(m.x+1,m.z+1,'🐟','fish',2.4);}
    }
    if(b.id==='warning'){
      const ch=st.choices.day5_share_choice;
      if(ch===0){gesture('모카','happy',1);gesture('호박','happy',1);}
      if(ch===1)gesture('호박','shy',2.7);
      if(ch===2)addProp(m.x+1,m.z-1,'🐟','fish',2.4);
    }
    if(b.id==='sign'&&st.choices.day3_departure==='stay')addProp(m.x-2,m.z+1,'🏠','sign',2.3);
    if(b.id==='rescue'){gesture('호박','jump',2.4);gesture('모카','alert',2);}
    if(b.id==='oldroom'){gesture('까미','shy',3);}
    if(b.id==='reunion'){
      position('까미',m.x-.53,m.z+.3);position('레오',m.x+.53,m.z+.3);
      getActor('까미').mesh.rotation.y=Math.PI/2;
      getActor('레오').mesh.rotation.y=-Math.PI/2;
    }
    if(b.id==='departure'){
      const stayed=st.choices.day3_departure==='stay';
      if(stayed){addProp(m.x-3,m.z-2,'🪧','sign',2.5);gesture('까미','shy',2.6);}
      else{gesture('까미','shy',3.3);gesture('모카','happy',1.6);}
    }
    if(b.id==='meet'){gesture('호박','shy',3);gesture('할미','shy',2);} 
    if(b.id==='roles'){
      st.choices.day4_roles={'모카':'낚시','호박':'약초','까미':'정찰','할미':'치료'};
      for(const name of ['모카','호박','까미','할미'])gesture(name,'happy',1.4);
    }
    if(b.id==='recovery'){gesture('호박','happy',3);gesture('할미','shy',3);}
    if(st.day===6){
      g.bear.active=b.id!=='recovery';g.bear.mesh.visible=g.bear.active;
      g.bear.x=p.x+9;g.bear.z=p.z+7;g.bear.y=g.ground.height(g.bear.x,g.bear.z);
      if(b.id==='trap')addProp(m.x,m.z,'🔔','marker',2);
    }
    if(b.id==='decision'){gesture('까미','shy',2.8);}
    if(b.id==='messenger'){gesture('까미','alert',2.8);}
    if(b.id==='warning'){gesture('까미','alert',2.5);}
    if(b.id==='consequence'){
      const c=st.choices.day3_bear_choice;
      if(c==='help'){
        addProp(m.x+2,m.z+2,'🐻','marker');addProp(m.x+3,m.z+2,'🐻','marker',2);
      }else if(c==='fight')addProp(m.x,m.z,'🐾','marker');
      else addProp(m.x,m.z,'🕳️','marker');
    }
    if(b.id==='decisionResult'||b.id==='worldChange'){
      if(st.day===10 && st.choices.day9_kingdom_choice===2 && st.choices.day3_bear_choice==='help'){
        g.bear.active=true;g.bear.x=p.x+9;g.bear.z=p.z+8;g.bear.y=g.ground.height(g.bear.x,g.bear.z);
        addProp(p.x+8,p.z+8,'🐻','marker',2);
      }
      const choice=st.choices.day9_kingdom_choice??2;
      if(choice===0){addProp(p.x+3,p.z,'🌱','garden');gesture('레오','happy');}
      if(choice===1){addProp(p.x-3,p.z,'🪧','sign');gesture('까미','happy');}
      if(choice===2){addProp(p.x+2,p.z,'🌈','garden');gesture('바람','happy');}
    }
    if(b.id==='footprints'){
      for(let i=0;i<10;i++){addProp(p.x+(i-5)*.8,p.z+Math.sin(i*.9)*.8,'🐾','marker',1.5)}
    }
  }
  function displayBeat(){
    const plan=PLANS[st.day],b=plan?.beats?.[st.beat];if(!b)return;
    applyBeatVisual(b);
    g.storyProject.day=st.day;
    g.storyProject.target=landmark(b);
    if(!g.storyProject.marker){
      const marker=new THREE.Mesh(new THREE.RingGeometry(1.05,1.26,32),new THREE.MeshBasicMaterial({color:0xffe57c,side:THREE.DoubleSide,transparent:true,opacity:.85,depthWrite:false}));
      marker.rotation.x=-Math.PI/2;g.scene.add(marker);g.storyProject.marker=marker;
    }
    const q=g.storyProject.target;
    g.storyProject.marker.position.set(q.x,g.ground.height(q.x,q.z)+.12,q.z);
    g.storyProject.marker.visible=true;
    g.setQuest(`DAY ${st.day} · ${b.focus}`,b.label);
    $('#stageText').textContent=`DAY ${st.day} · ${plan.name}`;
    g.dayNumber=st.day;
    $('#solStoryPanel').hidden=false;
    actionUI();save();
  }
  function startDay(day,force=false){
    if(!PLANS[day]||(!force&&day>st.unlocked))return false;
    if(window.__day3active && !force)return false;
    g.cut=null;g.storyLock=false;g.bearStarted=false;g.bearFreeCamera=false;g.ending=false;g.bear.active=false;g.bear.mesh.visible=false;
    g.mode='play';g.stage=8;g.storyPhase=0;
    const title=$('#start');if(title)title.hidden=true;
    if(!$('#modal').hidden)g.closeModal(true);
    document.body.classList.remove('cinematic','choice-lock');
    st.day=day;st.beat=0;st.finished=false;blocked=false;
    // Stop the old Day 3 invitation watchdog from re-appearing over Day 4–10 scenes.
    // A normal player can only open Day 4 after finishing Day 3.
    try{localStorage.setItem('meownuri:day3:done','1')}catch(e){}
    const staleDay3=$('#agDay3Btn');if(staleDay3)staleDay3.remove();
    const nextBtn=$('#solStoryNext');if(nextBtn)nextBtn.hidden=true;const actBtn=$('#solStoryAction');if(actBtn)actBtn.hidden=false;
    const back=d3();st.choices.day3_bear_choice=back.bear_choice||st.choices.day3_bear_choice||'help';
    st.choices.day3_departure=back.departure||st.choices.day3_departure||'leave';
    if(day>st.unlocked)st.unlocked=day;
    createWorld(day);cast(day);
    const spot=landmark(PLANS[day].beats[0]);placeAt(spot.x,spot.z,4);
    g.setDay(day,day>=8?'KINGDOM':'VILLAGE');
    try{g.storyCard('DAY '+day,planTitle(day), '',2600)}catch(e){console.warn(e)}
    displayBeat();save();
    return true;
  }
  function planTitle(day){return {4:'길 위에서.',5:'밥그릇.',6:'그것이 돌아왔다.',7:'마을의 이름.',8:'먼 길.',9:'왕의 제안.',10:'어떤 세상.'}[day]}
  function choose(i){
    const b=PLANS[st.day].beats[st.beat];if(!b?.choice||i<0||i>=b.choice.length)return false;
    const val=b.choiceKey==='village_name'?b.choice[i]:i;
    st.choices[b.choiceKey]=val;save();advance();return true;
  }
  function presentChoice(b){
    blocked=true;
    const box=$('#solStoryChoice');box.hidden=false;
    const heading=box.querySelector('strong');heading.textContent=b.label;
    const area=box.querySelector('.solChoiceItems');area.replaceChildren();
    b.choice.forEach((opt,i)=>{const btn=document.createElement('button');btn.type='button';btn.textContent=opt;
      btn.addEventListener('click',()=>{box.hidden=true;blocked=false;choose(i)});area.appendChild(btn)});
  }
  function perform(force=false){
    if(!st.day||st.finished||blocked)return false;
    const plan=PLANS[st.day],b=plan.beats[st.beat];if(!b)return false;
    if(!force&&!objective(b).near){actionUI();return false;}
    if(b.choice){presentChoice(b);return true;}
    // Action choreography. No text/dialogue balloons.
    const primary=['모카','호박','할미','콩이','바람','레오'][st.beat%6];
    if(getActor(primary)?.active)gesture(primary,st.beat%2?'happy':'jump',1.5);
    if(b.id==='recovery'){gesture('호박','happy',3);gesture('할미','shy',2);}
    if(b.id==='oldroom'){gesture('까미','shy',3);gesture('레오','shy',3);}
    if(b.id==='consequence'&&st.choices.day3_bear_choice==='help')gesture('까미','shy',4);
    if(['night','together','festival','villageEnd','reunion','together','footprints'].includes(b.id)){
      try{g.audio.play('complete')}catch(e){}
    }
    advance();return true;
  }
  function advance(){
    if(!st.day||st.finished)return;
    const plan=PLANS[st.day];st.visited.push(`${st.day}:${plan.beats[st.beat].id}`);st.beat++;
    if(st.beat<plan.beats.length){
      const spot=landmark(plan.beats[st.beat]);
      if(Math.hypot(g.player.x-spot.x,g.player.z-spot.z)>11)placeAt(spot.x,spot.z,5);
      displayBeat();
    }else completeDay();
  }
  function completeDay(){
    st.finished=true;st.unlocked=Math.max(st.unlocked,Math.min(10,st.day+1));save();
    const plan=PLANS[st.day];
    if(g.storyProject?.marker)g.storyProject.marker.visible=false;
    $('#solStoryAction').hidden=true;$('#solStoryProgress').textContent=`DAY ${st.day} ✓`;
    const final=st.day===10;
    const summary=final?([ '🌱 함께 만드는 왕국','🏘️ 우리의 마을','🌈 이어진 누리'][st.choices.day9_kingdom_choice??2]):`DAY ${st.day} COMPLETE`;
    try{g.storyCard(final?'제3누리 COMPLETE':'DAY '+st.day,final?summary:plan.name+'.','',3200)}catch(e){}
    const next=$('#solStoryNext');next.hidden=final;next.textContent=final?'':'▶ DAY '+(st.day+1)+' 시작';
    $('#solStoryEnding').hidden=!final;
    $('#solStoryEnding').textContent=final?`${summary} · 10일의 발자국`:' ';
    if(final){for(const a of Object.values(actors))if(a.active)gesture(a.name,'happy',2)}
  }
  function resume(){if(st.day<4||st.day>10)return false;
    const d=st.day,index=st.beat,done=st.finished;
    if(!startDay(d,true))return false;
    st.beat=Math.max(0,Math.min(index,PLANS[d].beats.length-1));
    displayBeat();if(done)completeDay();return true;
  }
  function initUI(){
    const style=document.createElement('style');style.textContent=`
      /* Existing Day 1–3 dialogue bubbles are hidden; functional instructions remain. */
      .ag-balloon{display:none!important}
      #solStoryPanel{position:fixed;z-index:36;bottom:calc(max(220px,env(safe-area-inset-bottom) + 220px));left:50%;transform:translateX(-50%);
       pointer-events:auto;max-width:min(90vw,410px);width:max-content;border:2px solid #795638;border-radius:17px;
       background:linear-gradient(135deg,#fff2d7e9,#f3d3a0e9);color:#4c3628;padding:7px 10px;text-align:center;
       box-shadow:0 4px 0 #5635213a;font:700 13px system-ui}
      #solStoryPanel[hidden],#solStoryChoice[hidden]{display:none!important}
      #solStoryAction{min-height:42px;max-width:min(82vw,350px);font-size:12px;padding:6px 10px;background:#85d0ad}
      #solStoryProgress{font-size:11px;color:#735338;display:block}
      #solStoryLabel{font-size:13px;display:block;margin:2px 0 5px}
      #solStoryNext{background:#ffd36e;width:100%}
      #solStoryChoice{position:fixed;z-index:90;inset:0;display:flex;align-items:center;justify-content:center;background:#22170e90;pointer-events:auto;padding:16px}
      .solChoiceCard{background:#f9ebd0;color:#513827;border:3px solid #7b573c;border-radius:22px;max-width:420px;width:95%;padding:19px;box-shadow:0 13px 45px #26190c80}
      .solChoiceItems{display:grid;gap:10px;margin-top:14px}.solChoiceItems button{background:#b0dcc5;text-align:left}
      #solChapter{position:fixed;z-index:36;right:10px;bottom:calc(168px + env(safe-area-inset-bottom));width:43px;min-width:43px;min-height:43px;padding:0;background:#e8d2a6;font-size:22px;pointer-events:auto}
      @media(max-width:760px){#solStoryPanel{bottom:calc(235px + env(safe-area-inset-bottom))}#solChapter{right:8px;bottom:calc(212px + env(safe-area-inset-bottom))}}
    `;document.head.appendChild(style);
    const wrap=document.createElement('div');wrap.innerHTML=`
      <section id="solStoryPanel" hidden aria-live="polite"><small id="solStoryProgress"></small><strong id="solStoryLabel"></strong>
        <button id="solStoryAction" type="button">🐾 다가가기</button><button id="solStoryNext" type="button" hidden>다음 날</button>
        <small id="solStoryEnding" hidden></small></section>
      <div id="solStoryChoice" hidden><section class="solChoiceCard" role="dialog" aria-modal="true"><strong></strong><div class="solChoiceItems"></div></section></div>
      <button id="solChapter" type="button" aria-label="다음 이야기" title="이어지는 이야기">📖</button>`;
    while(wrap.firstElementChild)document.body.appendChild(wrap.firstElementChild);
    $('#solStoryAction').onclick=()=>perform();
    $('#solStoryNext').onclick=()=>startDay(st.day+1);
    $('#solChapter').onclick=()=>{
      if(st.day>=4){if(st.finished&&st.day<10)startDay(st.day+1);else g.tell(`DAY ${st.day} · 화면의 목표를 따라 움직이세요`);return}
      if(localStorage.getItem('meownuri:day3:done')==='1'||st.unlocked>4)startDay(4);
      else g.tell('DAY 3 마지막 아침을 마치면 제2누리가 열립니다.');
    };
  }
  function tick(){if(!st.day||st.finished)return;
    if(g.mode!=='play')return;
    if(g.stage!==8)g.stage=8;
    const plan=PLANS[st.day],b=plan.beats[st.beat];
    if(!b)return;
    $('#stageText').textContent=`DAY ${st.day} · ${plan.name}`;
    const a=$('#action');if(a)a.hidden=true;
    if(g.storyProject?.marker)g.storyProject.marker.scale.setScalar(1+Math.sin(g.t*3)*.08);
    actionUI();
    const c=props.find(p=>p.kind==='fire');if(c?.group?.userData?.flame)c.group.userData.flame.scale.setScalar(1+Math.sin(g.t*7)*.09);
  }
  initUI();
  // Late wrapper after the original v15.7 agency initializers; no overwrite of core save.
  const priorTick=g.tick.bind(g);
  g.tick=function(dt){priorTick(dt);tick();};
  // Keep operational text, suppress all spoken dialogue from Day 1–3.
  const oldStoryLine=g.storyLine?.bind(g);
  if(oldStoryLine)g.storyLine=function(speaker,line,duration){
    if(['까미','삼색이','모카','호박','할미','콩이','레오','바람'].includes(speaker))return;
    return oldStoryLine(speaker,line,duration);
  };
  // All uses of existing localStorage day 3 choice are read, not reset.
  window.MeownuriStory={
    plans:PLANS,state:st,choices:st.choices,perform,choose,startDay,resume,
    getCurrent:()=>({day:st.day,beat:st.beat,total:PLANS[st.day]?.beats.length||0,finished:st.finished,unlocked:st.unlocked,choices:st.choices,characters:Object.entries(actors).filter(([n,a])=>a.active).map(([n])=>n),props:props.map(p=>p.kind)}),
    qaAdvance:()=>{const b=PLANS[st.day]?.beats[st.beat];if(!b)return false;if(b.choice)return choose(b.choiceKey==='village_name'?0:2);return perform(true);}
  };
  if(saved&&saved.day>=4 && !window.__day3active){setTimeout(()=>{if(g.mode==='title'){const next=$('#continueBtn');if(next){const b=document.createElement('button');b.className='primary';b.textContent='🐾 이어서 DAY '+saved.day;b.onclick=()=>resume();next.parentNode?.appendChild(b)}}},800)}
})();
