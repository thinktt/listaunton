(()=>{'use strict';
const byId=id=>document.getElementById(id),math=window.ListauntonWarpMath;
const board=JSON.parse(byId('board-data').textContent),scales=JSON.parse(byId('side-scale-data').textContent);
const records=math.registrations(board),targets=math.guide(scales),order=board.pieces.map(item=>item.piece);
const panel=byId('panel-warping'),stage=byId('warp-model-stage'),boardStage=byId('warp-board-stage');
const key='listaunton.warp-lab.v1.'+scales.defaultsRevision+'.'+board.pieces.map(item=>item.sourceSha256.slice(0,12)).join('.');
let saved=null;try{saved=JSON.parse(localStorage.getItem(key));}catch{}
let state=math.restore(saved,records,targets),before=false,wood=true,view='side',yaw=0,pitch=0,comparison='overlay';
let models=null,mainRenderer=null,boardRenderer=null,loading=false,failed=false,pending=false,drag=null;
const names=Object.fromEntries(scales.pieces.map(item=>[item.piece,item.name]));
for(const piece of order){
 const heading=document.createElement('div');heading.className='warp-heading';
 heading.innerHTML='<strong>'+names[piece]+'</strong><small id="warp-ratio-'+piece+'"></small><small>Chavet guide '+(targets[piece]*100).toFixed(1)+'%</small>';
 byId('warp-headings').append(heading);
 const card=document.createElement('div');card.className='warp-piece-control';
 card.innerHTML=['height','width'].map(axis=>{
  const label=axis==='height'?'Height':'Width',min=axis==='height'?50:70,max=axis==='height'?150:130,id='warp-'+piece+'-'+axis;
  return '<div class="warp-control-row"><label for="'+id+'">'+label+'</label><span><input id="'+id+'-number" type="number" min="'+min+'" max="'+max+'" step="0.1" aria-label="'+names[piece]+' '+axis+' percent">%</span></div><input id="'+id+'" type="range" min="'+min+'" max="'+max+'" step="0.1" aria-label="'+names[piece]+' '+axis+' percent">';
 }).join('')+'<p id="warp-gap-'+piece+'" class="warp-gap">Reference gap —</p><button id="warp-reset-'+piece+'" type="button" aria-label="Reset '+names[piece].toLowerCase()+' proportions">Reset</button>';
 byId('warp-piece-controls').append(card);
 for(const axis of ['height','width']){
  const id='warp-'+piece+'-'+axis;
  function change(value){state.pieces[piece][axis]=math.bounded(Number(value),state.pieces[piece][axis],axis==='height'?50:70,axis==='height'?150:130);changed();}
  byId(id).addEventListener('input',event=>change(event.target.value));
  byId(id+'-number').addEventListener('change',event=>change(event.target.value));
 }
 byId('warp-reset-'+piece).addEventListener('click',()=>{state.pieces[piece]={height:100,width:100};changed();});
}
function values(piece){return before?{height:100,width:100}:state.pieces[piece];}
function save(){try{localStorage.setItem(key,JSON.stringify(state));return true;}catch{return false;}}
function changed(){before=false;const stored=save();paint();schedule();byId('warp-status').textContent=stored?'Experiment saved in this browser.':'Experiment active for this visit. Use Save settings to keep a copy.';}
function paint(){
 const king=values('king').height/100;
 for(const piece of order){
  byId('warp-ratio-'+piece).textContent=(records[piece].ratio*values(piece).height/king).toFixed(1)+'% of king';
  for(const axis of ['height','width']){
   const id='warp-'+piece+'-'+axis,value=state.pieces[piece][axis];
   byId(id).value=String(value);byId(id+'-number').value=String(value);
   byId(id).setAttribute('aria-valuetext',value+'% of unwarped '+axis);
  }
 }
 for(const [id,name] of [['warp-bishop-preset','bishop'],['warp-chavet-preset','chavet'],['warp-reset','unwarped']]){
  const p=math.preset(name,records,targets);byId(id).setAttribute('aria-pressed',String(order.every(piece=>p[piece].height===state.pieces[piece].height&&p[piece].width===state.pieces[piece].width)));
 }
 byId('warp-before').setAttribute('aria-pressed',String(before));
 byId('warp-side').setAttribute('aria-pressed',String(view==='side'));
 byId('warp-reference').setAttribute('aria-pressed',String(view==='reference'));
 byId('warp-reference').textContent=state.angle+'° view';
 byId('warp-angle').value=String(state.angle);
 byId('warp-wood').setAttribute('aria-pressed',String(wood));byId('warp-neutral').setAttribute('aria-pressed',String(!wood));
 byId('warp-reference-title').textContent='Original view · '+state.angle+'°';
 for(const [id,name] of [['warp-original','original'],['warp-overlay','overlay'],['warp-model-only','model']])byId(id).setAttribute('aria-pressed',String(comparison===name));
 byId('warp-board-background').src=comparison==='model'?board.empty:board.original;
 byId('warp-board-canvas').style.opacity=comparison==='original'?'0':comparison==='overlay'?'.55':'1';
}
for(const [id,name] of [['warp-bishop-preset','bishop'],['warp-chavet-preset','chavet'],['warp-reset','unwarped']])byId(id).addEventListener('click',()=>{state.pieces=math.preset(name,records,targets);changed();});
byId('warp-before').addEventListener('click',()=>{before=!before;paint();schedule();byId('warp-status').textContent=before?'Showing unwarped shapes. Your experiment is preserved.':'Showing your warped shapes.';});
byId('warp-side').addEventListener('click',()=>{view='side';yaw=0;pitch=0;paint();schedule();});
byId('warp-reference').addEventListener('click',()=>{view='reference';paint();schedule();});
byId('warp-wood').addEventListener('click',()=>{wood=true;paint();schedule();});
byId('warp-neutral').addEventListener('click',()=>{wood=false;paint();schedule();});
byId('warp-angle').addEventListener('change',event=>{state.angle=math.bounded(Number(event.target.value),state.angle,35,70);changed();});
byId('warp-angle-reset').addEventListener('click',()=>{state.angle=54;changed();});
for(const [id,name] of [['warp-original','original'],['warp-overlay','overlay'],['warp-model-only','model']])byId(id).addEventListener('click',()=>{comparison=name;paint();});
byId('warp-export').addEventListener('click',()=>{
 const exported={schema:'listaunton-proportion-warping-v1',created:new Date().toISOString(),referenceAngle:state.angle,warpPercent:state.pieces,
  baseline:'Board-matched sizes, with model origin at the foot; width scales both horizontal axes.',
  models:Object.fromEntries(order.map(piece=>[piece,{sourceSha256:records[piece].sourceSha256,baselineHeightRatio:records[piece].ratio,chavetHeightRatio:targets[piece]}]))};
 const url=URL.createObjectURL(new Blob([JSON.stringify(exported,null,2)+'\n'],{type:'application/json'}));
 const a=document.createElement('a');a.href=url;a.download='listaunton-proportion-warping.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
});
const vertex=`#version 300 es
precision highp float;
layout(location=0) in vec3 aPosition;layout(location=1) in vec3 aNormal;layout(location=2) in vec2 aUV;
uniform vec3 uBase,uWarp;uniform mat3 uView;
uniform float uScale,uPixels,uX,uGround;uniform vec2 uViewport;
out vec3 vNormal;out vec2 vUV;
void main(){
 vec3 p=uView*((aPosition-uBase)*uWarp*uScale);
 vNormal=uView*(aNormal/uWarp);vUV=aUV;
 vec2 pixel=vec2(uX+p.x*uPixels,uGround-p.y*uPixels);
 gl_Position=vec4(pixel.x/uViewport.x*2.0-1.0,1.0-pixel.y/uViewport.y*2.0,-p.z/32.0,1.0);
}`;
class Renderer{
 constructor(canvas){
  this.canvas=canvas;const gl=this.gl=canvas.getContext('webgl2',{antialias:true,alpha:true});if(!gl)throw Error('WebGL 2 is unavailable.');
  const compile=(type,source)=>{const shader=gl.createShader(type);gl.shaderSource(shader,source);gl.compileShader(shader);if(!gl.getShaderParameter(shader,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(shader));return shader;};
  const program=this.program=gl.createProgram();gl.attachShader(program,compile(gl.VERTEX_SHADER,vertex));gl.attachShader(program,compile(gl.FRAGMENT_SHADER,window.ListauntonModelSource.fragmentShader));gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(program));
  this.uniforms={};for(const name of ['uBase','uWarp','uView','uScale','uPixels','uX','uGround','uViewport','uWood','uUseWood','uBishop'])this.uniforms[name]=gl.getUniformLocation(program,name);
  this.resources={};
  for(const piece of order){
   const source=models[piece],meta=source.meta,vao=gl.createVertexArray();gl.bindVertexArray(vao);
   const vb=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,vb);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(source.buffer,0,meta.vertexByteLength/4),gl.STATIC_DRAW);
   for(let i=0;i<2;i++){gl.enableVertexAttribArray(i);gl.vertexAttribPointer(i,3,gl.FLOAT,false,32,i*12);}
   gl.enableVertexAttribArray(2);gl.vertexAttribPointer(2,2,gl.FLOAT,false,32,24);
   const ib=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,ib);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint32Array(source.buffer,meta.indexByteOffset,meta.indexCount),gl.STATIC_DRAW);
   const texture=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,texture);gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,true);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,source.image);gl.generateMipmap(gl.TEXTURE_2D);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR_MIPMAP_LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
   this.resources[piece]={vao,texture};
  }
  gl.bindVertexArray(null);gl.enable(gl.DEPTH_TEST);gl.depthFunc(gl.LEQUAL);
  canvas.addEventListener('webglcontextlost',event=>{event.preventDefault();showError('3D graphics paused. Save your settings, then reload the page to continue.');});
 }
 frame(transparent){
  const {canvas,gl,uniforms:u}=this,dpr=Math.min(window.devicePixelRatio||1,1.5),w=canvas.clientWidth,h=canvas.clientHeight;
  const width=Math.max(1,Math.round(w*dpr)),height=Math.max(1,Math.round(h*dpr));if(canvas.width!==width||canvas.height!==height){canvas.width=width;canvas.height=height;}
  gl.viewport(0,0,width,height);gl.clearColor(transparent?0:.125,transparent?0:.137,transparent?0:.122,transparent?0:1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.useProgram(this.program);gl.uniform2f(u.uViewport,w,h);gl.uniform1i(u.uWood,0);gl.uniform1i(u.uUseWood,wood?1:0);
 }
 piece(piece,warp,basis,scale,pixels,x,ground){
  const {gl,uniforms:u}=this,model=models[piece],gpu=this.resources[piece];
  gl.uniform3f(u.uBase,0,0,model.meta.bounds.min[2]);gl.uniform3f(u.uWarp,warp.width/100,warp.width/100,warp.height/100);
  gl.uniformMatrix3fv(u.uView,false,math.columnMajor(basis));gl.uniform1f(u.uScale,scale);gl.uniform1f(u.uPixels,pixels);gl.uniform1f(u.uX,x);gl.uniform1f(u.uGround,ground);gl.uniform1i(u.uBishop,piece==='bishop'?1:0);
  gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,gpu.texture);gl.bindVertexArray(gpu.vao);gl.drawElements(gl.TRIANGLES,model.meta.indexCount,gl.UNSIGNED_INT,0);
 }
}
function schedule(){if(!models||failed||panel.hidden||pending)return;pending=true;requestAnimationFrame(()=>{pending=false;draw();});}
function draw(){
 if(!models||failed||panel.hidden)return;
 const width=stage.clientWidth,height=stage.clientHeight,cell=width/order.length;
 // Frame the entire allowed experiment range once, so moving a height slider
 // never causes an automatic zoom that conceals the geometry change.
 const maxWidth=Math.max(...order.map(piece=>Math.hypot(models[piece].meta.bounds.size[0],models[piece].meta.bounds.size[1])*records[piece].ratio/models[piece].meta.bounds.size[2]*1.3));
 const pixels=Math.min(300,(height-50)/1.55,cell*.87/maxWidth);
 const radius=Math.max(...order.map(piece=>models[piece].baseRadius*records[piece].ratio/models[piece].meta.bounds.size[2]*1.3));
 const angle=view==='reference'?state.angle*Math.PI/180:pitch,ground=height-16-radius*Math.abs(Math.sin(angle))*pixels;
 mainRenderer.frame(false);boardRenderer.frame(true);
 const boardScale=boardStage.clientWidth/board.width;
 for(const [index,piece] of order.entries()){
  const model=models[piece],warp=values(piece),record=records[piece],reference=math.referenceBasis(model.meta,state.angle);
  mainRenderer.piece(piece,warp,view==='reference'?reference:math.orbitBasis(yaw,pitch),record.ratio/model.meta.bounds.size[2],pixels,(index+.5)*cell,ground);
  boardRenderer.piece(piece,warp,reference,1,record.pixels*boardScale,record.centerX*boardScale,record.ground*boardScale);
  const bounds=math.projectedBounds(model,warp,state.angle,record),top=bounds.top-record.targetTop,bottom=bounds.bottom-record.targetBottom;
  const signed=value=>(value>=0?'+':'−')+Math.abs(value).toFixed(1);
  byId('warp-gap-'+piece).textContent='Top '+signed(top)+' px · foot '+signed(bottom)+' px';
 }
}
function showError(message){failed=true;comparison='original';paint();byId('warp-load-message').hidden=false;byId('warp-load-message').textContent=message;byId('warp-board-canvas').hidden=true;byId('warp-status').textContent='The original reference is available. Save settings downloads your experiment.';}
async function start(){
 if(panel.hidden)return;if(models){schedule();return;}if(loading||failed)return;loading=true;
 if(location.protocol==='file:'){showError('Open this lab through the local server at http://localhost:8080/set-comparison.html#warping to load the 3D geometry.');return;}
 try{
  const entries=await Promise.all(order.map(async piece=>{
   const model=await window.ListauntonModelSource.loadPiece(piece);if(model.meta.sourceSha256!==records[piece].sourceSha256)throw Error('The '+piece+' model changed. Rebuild the comparison page before using this lab.');return [piece,model];
  }));
  models=Object.fromEntries(entries);mainRenderer=new Renderer(byId('warp-model-canvas'));boardRenderer=new Renderer(byId('warp-board-canvas'));
  byId('warp-load-message').hidden=true;byId('warp-status').textContent='Drag the lineup to rotate. Height changes leave the base width unchanged; Width changes both horizontal axes.';paint();schedule();
 }catch(error){console.error(error);showError('Could not load the proportion lab. '+error.message);}
}
const canvas=byId('warp-model-canvas');
canvas.addEventListener('pointerdown',event=>{if(event.button!==0)return;drag={x:event.clientX,y:event.clientY};canvas.setPointerCapture(event.pointerId);});
canvas.addEventListener('pointermove',event=>{if(!drag)return;if(view==='reference'){pitch=state.angle*Math.PI/180;yaw=0;}view='orbit';yaw+=(event.clientX-drag.x)*.008;pitch=Math.max(-1.3,Math.min(1.3,pitch+(event.clientY-drag.y)*.008));drag={x:event.clientX,y:event.clientY};paint();schedule();});
for(const type of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(type,()=>{drag=null;});
canvas.addEventListener('keydown',event=>{if(view==='reference'){pitch=state.angle*Math.PI/180;yaw=0;}if(event.key==='ArrowLeft')yaw-=.1;else if(event.key==='ArrowRight')yaw+=.1;else if(event.key==='ArrowUp')pitch=Math.max(-1.3,pitch-.1);else if(event.key==='ArrowDown')pitch=Math.min(1.3,pitch+.1);else if(event.key==='Home'){view='side';yaw=0;pitch=0;}else return;if(event.key!=='Home')view='orbit';event.preventDefault();paint();schedule();});
byId('tab-warping').addEventListener('click',start);window.addEventListener('hashchange',()=>{if(!panel.hidden)start();});
new ResizeObserver(schedule).observe(stage);new ResizeObserver(schedule).observe(boardStage);
paint();if(!panel.hidden)start();
})();
