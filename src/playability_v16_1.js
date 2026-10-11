/* MEOWNURI SOL v16.1: accessible start, assisted walking, day chapter index.
   Deployed as a tiny additive overlay. Never changes Astra or legacy saves. */
(() => {
  'use strict';
  const $ = selector => document.querySelector(selector);
  let booted = false, auto = false, pendingTarget = null;
  const introButtonId = 'solStartDay4';
  function init() {
    if (booted || !window.MeownuriStory || !window.game || !$('#introStart') || !$('#solStoryPanel')) return false;
    booted = true;
    const game = window.game, story = window.MeownuriStory;
    const style = document.createElement('style');
    style.textContent = `
      #solStartDay4{background:#89d0b2!important;color:#392d24!important;border-color:#5b6647!important}
      #solStoryAssist{min-height:40px;margin-top:5px;width:100%;background:#f3dd9f;color:#403023;border-color:#927344;padding:6px 10px;font-size:12px;pointer-events:auto}
      #solStoryAssist:disabled{opacity:.68;background:#e6d9b4}
      #solJumpMenu{position:fixed;inset:0;z-index:98;background:#1c170fa8;display:grid;place-items:center;padding:12px;pointer-events:auto}
      #solJumpMenu[hidden]{display:none!important}
      #solJumpMenu>section{width:min(94vw,420px);max-height:min(85dvh,690px);overflow:auto;border:3px solid #68462c;border-radius:20px;background:#fff1d1;padding:17px;color:#4b3524;box-shadow:0 13px 45px #15100a95}
      #solJumpMenu h2{font-size:19px;margin:0 0 8px}
      #solJumpMenu p{font-size:12px;line-height:1.4;margin:5px 0 12px}
      .solDayGrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
      .solDayGrid button{font-size:12px;padding:8px 7px;min-height:47px;text-align:center}
      .solDayGrid button.chosen{background:#9edebc}
      #solJumpClose{display:block;width:100%;margin-top:12px;background:#ffe1a5}
      @media(max-width:440px){#solStoryPanel{bottom:calc(224px + env(safe-area-inset-bottom))!important;max-width:86vw}#solStoryAssist{font-size:11px}}
    `;
    document.head.appendChild(style);
    const btn = document.createElement('button');
    btn.id = introButtonId;
    btn.className = 'primary';
    btn.type = 'button';
    btn.textContent = '🏘️ DAY 4–10 바로 플레이';
    btn.title = '기존 Day 1–3을 건너뛰고 마을 이야기부터 게임으로 진행';
    $('#introStart').before(btn);
    btn.addEventListener('click', () => {auto=false; story.startDay(4,true);});
    const hint = document.createElement('small');
    hint.style.cssText = 'display:block;margin:3px auto 8px;line-height:1.3;color:#66503b';
    hint.textContent = '조이스틱으로 이동 · 필요하면 목표로 걷기 버튼';
    btn.after(hint);
    const assist = document.createElement('button');
    assist.id = 'solStoryAssist';
    assist.type = 'button';
    assist.textContent = '🐾 목표로 걷기';
    $('#solStoryAction').after(assist);
    assist.addEventListener('click',()=>{
      const s=story.getCurrent();
      if(s.day<4||s.finished||!game.storyProject?.target)return;
      auto=!auto;
      if(auto) pendingTarget={...game.storyProject.target};
      assist.textContent=auto?'■ 걷기 중지':'🐾 목표로 걷기';
    });
    const menu = document.createElement('div');
    menu.id='solJumpMenu';menu.hidden=true;
    menu.innerHTML=`<section role="dialog" aria-modal="true" aria-label="냥누리 날짜 선택"><h2>🐾 냥누리 플레이</h2><p>처음부터 플레이하거나, 제작된 Day 4–10 중 하나를 선택해 체험합니다. 날짜 변경 시 현재 장면은 저장됩니다.</p><div class="solDayGrid"></div><button id="solJumpClose" type="button">닫기</button></section>`;
    document.body.append(menu);
    const chapter=$('#solChapter');
    chapter.title='날짜 선택 · 이어하기';
    chapter.setAttribute('aria-label','날짜 선택 · 이어하기');
    function renderMenu(){
      const grid=menu.querySelector('.solDayGrid');grid.replaceChildren();
      for(let day=4;day<=10;day++){
        const plan=story.plans[day],node=document.createElement('button');
        node.textContent=`DAY ${day} · ${plan.name}`;node.type='button';
        if(story.getCurrent().day===day)node.className='chosen';
        node.addEventListener('click',()=>{auto=false;menu.hidden=true;story.startDay(day,true)});
        grid.append(node);
      }
    }
    chapter.onclick=()=>{renderMenu();menu.hidden=false;};
    $('#solJumpClose').onclick=()=>{menu.hidden=true;};
    menu.addEventListener('click',ev=>{if(ev.target===menu)menu.hidden=true;});
    document.addEventListener('keydown',ev=>{if(ev.key==='Escape'&&!menu.hidden)menu.hidden=true;});
    const originalTick = game.tick.bind(game);
    game.tick = function(dt){
      originalTick(dt);
      if(!$('#solStoryPanel') || $('#solStoryPanel').hidden) return;
      const s=story.getCurrent();
      if(s.day<4||s.finished){auto=false;assist.hidden=true;return;}
      assist.hidden=false;
      const target=game.storyProject?.target;
      if(!target)return;
      const distance=Math.hypot(game.player.x-target.x,game.player.z-target.z);
      if(auto && distance<2.2){auto=false;pendingTarget=null;}
      if(auto && pendingTarget && (Math.abs(target.x-pendingTarget.x)>0.1||Math.abs(target.z-pendingTarget.z)>0.1)){
        auto=false;pendingTarget=null;
      }
      if(auto && game.mode==='play' && distance>2.2){
        const step=Math.min(distance-2.05,Math.max(.02,dt)*7.2);
        game.player.x+=(target.x-game.player.x)/distance*step;
        game.player.z+=(target.z-game.player.z)/distance*step;
        game.player.y=game.ground.height(game.player.x,game.player.z);
        game.player.mesh.position.set(game.player.x,game.player.y,game.player.z);
        game.vy=0;
      }
      assist.disabled=!auto && distance<2.8;
      assist.textContent=auto?'■ 걷기 중지':distance<2.8?'✓ 목표 도착 · 행동 버튼 선택':'🐾 목표로 걷기';
    };
    window.MeownuriPlayable={version:'v16.1',startDay4:()=>story.startDay(4,true),openChapters:()=>chapter.click(),stopWalk:()=>{auto=false},isWalking:()=>auto};
    return true;
  }
  if(!init()){
    let count=0;
    const watch=setInterval(()=>{if(init()||++count>=300)clearInterval(watch);},100);
  }
})();
