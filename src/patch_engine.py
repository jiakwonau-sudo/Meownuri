from pathlib import Path
import json,re,base64
DIR=Path('/mnt/data/meownuri_work')
original=Path('/mnt/data/E-01_meownuri_v15.7.html').read_text()
oldmap=re.search(r'<script type="importmap">(.*?)</script>',original,re.S)
imports=json.loads(oldmap.group(1))['imports']
code=base64.b64decode(imports['client'].split(',')[1]).decode()
fallback=r'''
/* v15.8 SOL-only: 2D safety renderer. WebGL remains primary whenever available.
 * This replaces the blank canvas with an interactive visual world on WebGL failure.
 * No changes to the existing game physics, story decisions, or saves. */
class SafetyCanvasRenderer {
 constructor(canvas,g,overlay=false){
  this.game=g; this.overlay=overlay;
  this.domElement=canvas;
  this.ctx=canvas.getContext('2d',{alpha:false});
  if(!this.ctx) {
   const replacement=document.createElement('canvas');replacement.id=canvas.id;
   canvas.replaceWith(replacement);this.domElement=replacement;
   this.ctx=replacement.getContext('2d',{alpha:false});
  }
  if(!this.ctx)throw new Error('Canvas 2D unavailable');
  this.shadowMap={enabled:false,type:0};this.info={render:{calls:0}};
  this.pixelRatio=1;this.w=innerWidth;this.h=innerHeight;this.setSize(this.w,this.h);
 }
 setPixelRatio(n){this.pixelRatio=Math.min(Number(n)||1,1.2);this.setSize(this.w,this.h)}
 setSize(w,h){this.w=Math.max(1,w);this.h=Math.max(1,h);const cv=this.domElement;cv.width=Math.max(1,Math.round(this.w*this.pixelRatio));cv.height=Math.max(1,Math.round(this.h*this.pixelRatio));cv.style.width=this.w+'px';cv.style.height=this.h+'px'}
 render(){
  const g=this.game,ctx=this.ctx,w=this.w,h=this.h;if(!g?.player||!ctx)return;
  this.info.render.calls++;
  const rw=this.domElement.width/w,rh=this.domElement.height/h;
  ctx.setTransform(rw,0,0,rh,0,0);
  const sky=ctx.createLinearGradient(0,0,0,h);
  sky.addColorStop(0,'#fae0bb');sky.addColorStop(.38,'#f7c8a1');sky.addColorStop(1,'#d99e79');
  ctx.fillStyle=sky;ctx.fillRect(0,0,w,h);
  const p=g.player,t=g.t||0;
  const scale=Math.max(7,Math.min(19,Math.min(w/27,h/42)));
  const focusX=w/2,focusY=h*.49;
  const pos=(x,z)=>({x:focusX+(x-p.x)*scale,y:focusY+(z-p.z)*scale*.70});
  const earth=ctx.createLinearGradient(0,h*.1,0,h);
  earth.addColorStop(0,'#b2cf8b');earth.addColorStop(.55,'#85b075');earth.addColorStop(1,'#648c55');
  ctx.fillStyle=earth;ctx.beginPath();ctx.ellipse(focusX,focusY+52,Math.max(w*.96,380),Math.max(h*.68,460),0,0,Math.PI*2);ctx.fill();
  // A readable playfield even without a GPU: winding trail, trees and wildflowers.
  ctx.save();ctx.strokeStyle='#c7b389';ctx.lineWidth=scale*.75;ctx.lineCap='round';ctx.beginPath();ctx.moveTo(-70,h*.48);
  ctx.bezierCurveTo(w*.32,h*.35,w*.65,h*.68,w+70,h*.51);ctx.stroke();ctx.restore();
  for(let i=0;i<33;i++){
    const xx=((i*19+7)%43-22)+Math.floor(p.x/7)*7,zz=((i*29+3)%49-24)+Math.floor(p.z/7)*7;
    const o=pos(xx,zz);if(o.x<-35||o.y<-30||o.x>w+35||o.y>h+35)continue;
    if(i%5===0){ctx.fillStyle='#406e48';ctx.beginPath();ctx.arc(o.x,o.y,scale*.75,0,Math.PI*2);ctx.fill();ctx.fillStyle='#6f9e5c';ctx.beginPath();ctx.arc(o.x-3,o.y-6,scale*.54,0,Math.PI*2);ctx.fill();}
    else {ctx.fillStyle=['#f3d97a','#f3a8b4','#d6eab4'][i%3];ctx.beginPath();ctx.arc(o.x,o.y,2.8,0,Math.PI*2);ctx.fill();}
  }
  if(g.box){const c=pos(g.box.x,g.box.z);ctx.save();ctx.translate(c.x,c.y);ctx.fillStyle='#7c4e2c';ctx.fillRect(-scale*1.7,-scale*1.8,scale*3.4,scale*2.8);ctx.fillStyle='#d6a56d';ctx.fillRect(-scale*1.2,-scale*1.4,scale*2.4,scale*2);ctx.fillStyle='#6e4936';ctx.font=`${Math.round(scale*2.3)}px system-ui`;ctx.textAlign='center';ctx.fillText('📦',0,5);ctx.restore();}
  const waypoint=g.storyProject?.target;
  if(waypoint){const q=pos(waypoint.x,waypoint.z);
   ctx.strokeStyle='#ffe58c';ctx.lineWidth=4;ctx.setLineDash([7,6]);ctx.beginPath();ctx.moveTo(focusX,focusY);ctx.lineTo(q.x,q.y);ctx.stroke();ctx.setLineDash([]);
   ctx.fillStyle='#ffe58c55';ctx.strokeStyle='#8d6232';ctx.lineWidth=2.5;ctx.beginPath();ctx.arc(q.x,q.y,scale*1.3,0,Math.PI*2);ctx.fill();ctx.stroke();
  }
  const extras=g.storyProject?.props||[];
  for(const it of extras){if(!it.visible)continue;const q=pos(it.x,it.z);if(q.x<-80||q.x>w+80||q.y<-80||q.y>h+80)continue;
   ctx.textAlign='center';ctx.font=`${Math.max(24,Math.round(scale*(it.size||2.6)))}px system-ui`;ctx.fillText(it.emoji||'🌲',q.x,q.y)}
  const all=[...(g.actors||[])];
  for(const a of all){if(a.active===false||!a.mesh?.visible)continue;const q=pos(a.x,a.z);if(q.x<-80||q.x>w+80||q.y<-80||q.y>h+80)continue;
   const emoji=a.id==='player'?'🐈':a.name==='까미'?'🐈‍⬛':a.name==='모카'?'🐈':a.name==='호박'?'🐈':a.name==='할미'?'🐈':a.name==='콩이'?'🐱':a.name==='레오'?'🦁':a.id==='bear'?'🐻':'🐈';
   ctx.fillStyle='#fdf2cfbb';ctx.beginPath();ctx.ellipse(q.x,q.y+4,scale*2,scale*.8,0,0,Math.PI*2);ctx.fill();ctx.textAlign='center';ctx.font=`${Math.max(27,scale*2.7)}px system-ui`;ctx.fillText(emoji,q.x,q.y+3);
   if(a.id!=='player'){ctx.fillStyle='#432a1b';ctx.textAlign='center';ctx.font='bold 11px system-ui';ctx.fillText(a.name,q.x,q.y+23)}
  }
  if(g.bear?.mesh?.visible){const q=pos(g.bear.x,g.bear.z);ctx.font='44px system-ui';ctx.textAlign='center';ctx.fillText('🐻',q.x,q.y)}
  ctx.textAlign='left';ctx.fillStyle='#3c342ac7';ctx.font='bold 11px system-ui';ctx.fillText('MEOWNURI · 2D 안전 모드',12,h-14);
 }
 dispose(){}
}
'''
code=code.replace('class Game{',fallback+'\nclass Game{',1)
old="this.renderer=new THREE.WebGLRenderer({canvas:$('#world'),antialias:true});"
new="""try { this.renderer=new THREE.WebGLRenderer({canvas:$('#world'),antialias:true});this.rendererMode='3d'; }
  catch(error){console.warn('[MEOWNURI] WebGL unavailable; activating 2D safe renderer',error.message);this.renderer=new SafetyCanvasRenderer($('#world'),this);this.rendererMode='2d';}"""
assert old in code;code=code.replace(old,new,1)
old="let prev=performance.now();const loop=now=>{const dt=Math.min(.05,(now-prev)/1000);prev=now;this.tick(dt);this.renderer.render(this.scene,this.camera);requestAnimationFrame(loop)};requestAnimationFrame(loop);"
new="""let prev=performance.now();let fails=0;let blankSamples=0;let watchFrames=0;
  const loop=now=>{const dt=Math.min(.05,(now-prev)/1000);prev=now;
    try {this.tick(dt);this.renderer.render(this.scene,this.camera);fails=0;
      // A valid WebGL context can still render ONLY the clear colour. Check low-frequency
      // pixels AFTER render, and avoid flagging title, cinematic fades, or deliberate menus.
      if(this.rendererMode==='3d' && this.mode==='play' && !this.cut && !this.storyLock && (++watchFrames%90===0)){
        const gl=this.renderer.getContext(), w=gl.drawingBufferWidth,h=gl.drawingBufferHeight;
        if(w>90&&h>90){const samples=[],pixel=new Uint8Array(4);
          for(const [xx,yy] of [[.22,.30],[.50,.34],[.78,.36],[.35,.52],[.65,.58],[.48,.72]]){
            gl.readPixels(Math.floor(w*xx),Math.floor(h*yy),1,1,gl.RGBA,gl.UNSIGNED_BYTE,pixel);
            samples.push([pixel[0],pixel[1],pixel[2],pixel[3]]);
          }
          const first=samples[0],same=samples.every(c=>c.every((v,i)=>i===3 || Math.abs(v-first[i])<3));
          const blank=same&&first[3]>0;
          blankSamples=blank?blankSamples+1:0;
          if(blankSamples>=4)this.activateSafetyRenderer('four uniformly blank 3D frames');
        }
      }
    }catch(e){if(++fails<=3)console.error('[MEOWNURI] render/update error',e);if(this.rendererMode==='3d'){this.activateSafetyRenderer('render error');}}
    requestAnimationFrame(loop)};requestAnimationFrame(loop);
  if(this.rendererMode==='3d'){
    const cv=this.renderer.domElement;
    cv.addEventListener('webglcontextlost',event=>{event.preventDefault();this.activateSafetyRenderer('context lost')});
    cv.addEventListener('webglcontextrestored',()=>{console.info('[MEOWNURI] WebGL context restored; 3D ready on next load')});
  }"""
assert old in code;code=code.replace(old,new,1)
# Ensure loaded WebGL renderer fails over even when it loses GPU mid-play; preserve previous canvas to avoid context mismatch
inject="""
 activateSafetyRenderer(reason){
   if(this.rendererMode==='2d')return;
   console.warn('[MEOWNURI] switching to visible 2D fallback:',reason);
   const old=this.renderer?.domElement||document.querySelector('#world');
   const canvas=document.createElement('canvas');canvas.id='world';old?.replaceWith(canvas);
   try {this.renderer.dispose()}catch(e){}
   this.renderer=new SafetyCanvasRenderer(canvas,this);this.renderer.setPixelRatio(Math.min(devicePixelRatio,1.2));this.rendererMode='2d';
 }
"""
assert ' actor(id,name,coat,x,z,scale)' in code;code=code.replace(' actor(id,name,coat,x,z,scale)',inject+' actor(id,name,coat,x,z,scale)',1)
# tighten stale/invalid camera parameters, never allow huge far-plane/NaN screen
anchor="""
  if(!Number.isFinite(this.player.x)||!Number.isFinite(this.player.z)||!Number.isFinite(this.player.y)){
    console.warn('[MEOWNURI] invalid player position, restoring known safe location');
    this.player.x=this.boxFound?this.box.x-3:-38;this.player.z=this.boxFound?this.box.z+3:-32;
    this.player.y=this.ground.height(this.player.x,this.player.z);this.vy=0;
  }
  if(!Number.isFinite(this.yaw))this.yaw=.7;
  if(!Number.isFinite(this.pitch))this.pitch=.42;
  if(!Number.isFinite(this.distance)||this.distance>72||this.distance<3)this.distance=this.mobile?11.5:7.5;
"""
assert ' tick(dt){this.t+=dt;' in code;code=code.replace(' tick(dt){this.t+=dt;', ' tick(dt){'+anchor+'this.t+=dt;',1)
# remove redundant speech bubbles and emotional cat narration (not mechanical instructions)
# Existing inline agency script's bubbles stay, hide only speech class so HUD labels remain.
# do not break string-based BGM triggers until moved to structured event system.
imports['client']='data:text/javascript;base64,'+base64.b64encode(code.encode()).decode()
newmap=json.dumps({'imports':imports},ensure_ascii=False,separators=(',',':'))
patched=original[:oldmap.start()]+f'<script type="importmap">{newmap}</script>'+original[oldmap.end():]
# CSS to hide agency *speech* and show clear help without redundant bubble dialogue
patched=patched.replace('</style>','\n/* v15.8 wordless cats: retain objectives, hide spoken bubbles */\n.ag-balloon {display:none !important;}\n</style>',1)
patched=patched.replace('WIDE WORLD v15.7 · DAY 3','WIDE WORLD v15.8 · DISPLAY FIX · DAY 3').replace('>v15.7<','>v15.8<')
out=DIR/'MEOWNURI_SOL_v15.8_FIX.html';out.write_text(patched)
(DIR/'decoded/client_fixed.js').write_text(code)
print('saved',out,len(patched),'base source preserved',len(original))
