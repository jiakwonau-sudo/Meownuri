/* Explicit review entry. No story save is written in this page. */
import 'client';
const g=window.game;
if(g&&window.MeownuriCozy){
 const $=s=>document.querySelector(s);
 g.save=()=>{const el=$('#saveStatus');if(el)el.textContent='미리보기 · 저장하지 않음'};
 const css=document.createElement('style');css.textContent=`
 #cozyReviewDock{position:fixed;left:50%;transform:translateX(-50%);top:54px;z-index:40;display:flex;gap:7px;max-width:96vw;padding:5px;border-radius:22px;background:#fff7e8ed;border:1px solid #b9a98d}
 #cozyReviewDock[hidden]{display:none}#cozyReviewDock button{min-height:44px;min-width:72px;margin:0;padding:7px 12px;font-size:13px;background:#fff7e8;color:#433b30}
 body.cozy-review-play #statusPanel,body.cozy-review-play #questPanel{display:none!important}
 body.cozy-review-play #hint{bottom:235px;max-width:90vw}
 `;document.head.append(css);
 const panel=$('#start .panel');panel.innerHTML='<div class="ag-title-kicker">SOL v16.10 · PREVIEW</div><h1>냥누리</h1><h2>작은 마을의 일상</h2><p>고양이를 돌보고<br>세 가지 빛깔의 집을 지어보세요.</p><p class="note">새 기능 체험용 공간입니다.<br>진행 내용은 저장하지 않습니다.</p><button class="primary" id="cozyReviewStart">🐾 마을 둘러보기</button>';
 const dock=document.createElement('div');dock.id='cozyReviewDock';dock.hidden=true;dock.setAttribute('aria-label','새 기능 체험');dock.innerHTML='<button id="cozyReviewCare">♡ 고양이</button><button id="cozyReviewBuild">⌂ 집 짓기</button><button id="cozyReviewReset">↺ 다시</button>';document.body.append(dock);
 function carePlace(){
  MeownuriCozy.cancel();g.closeModal();
  const p=g.ground.nearest(0,3,g.player.radius+.1,[],4);g.player.x=p.x;g.player.z=p.z;g.player.y=g.ground.height(p.x,p.z);g.vy=0;
  const q=g.ground.nearest(p.x+2.2,p.z,g.friend.radius+.1,[g.player],4);Object.assign(g.friend,{x:q.x,z:q.z,y:g.ground.height(q.x,q.z),active:true});g.friend.mesh.visible=true;g.friend.idleTarget=null;
  g.bag.fish=Math.max(3,g.bag.fish);g.distance=g.mobile?14:11;g.pitch=.52;g.yaw=.7;g.camera.position.set(p.x-9,g.player.y+10,p.z-10);g.updateUI();
 }
 $('#cozyReviewStart').onclick=()=>{
  g.begin(false);g.town.start();g.stage=5;g.storyPhase=0;g.cut=null;g.storyLock=false;g.bag.wood=36;g.bag.fiber=12;g.bag.stone=12;g.bag.scrap=6;
  document.body.classList.add('cozy-review-play');dock.hidden=false;carePlace();g.tell('고양이 곁에서 ♡ · 🐟 버튼을 눌러보세요.');
 };
 $('#cozyReviewCare').onclick=carePlace;
 $('#cozyReviewBuild').onclick=()=>{MeownuriCozy.cancel();g.town.buildMenu()};
 $('#cozyReviewReset').onclick=()=>location.reload();
 window.MeownuriReview={mode:'isolated-reference-preview'};
}
