(()=>{'use strict';
const byId=id=>document.getElementById(id);
const data=JSON.parse(byId('side-scale-data').textContent);
let order=data.defaultOrder.slice();
// These profiles are rendered from the accepted models. Their alpha bounds are
// measured by the page builder for the Blender renders and offline fallback.
const profiles=JSON.parse(byId('model-profile-data').textContent);
const stage=byId('models-stage'),fallback=byId('models-fallback'),canvas=byId('models-canvas');
const panel=byId('panel-models'),status=byId('models-status');
const rows=Object.fromEntries(data.pieces.map(item=>[item.piece,item]));
const images={};
for(const piece of order){
 const img=document.createElement('img');img.src=profiles[piece].file+'?v='+profiles[piece].version;img.alt='';img.draggable=false;
 fallback.append(img);images[piece]=img;
}
let models=null,gl=null,program=null,uniforms=null,started=false,lost=false;
let showBlender=window.location.hash==='#blender',loadMessage='Loading current 3D models…';
let yaw=0,pitch=0,wood=true,pending=false,drag=null;
const ratio=piece=>rows[piece].height*Number(byId('side-scale-'+piece).value)/(rows.king.height*Number(byId('side-scale-king').value));
function ratios(){return Object.fromEntries(order.map(piece=>[piece,ratio(piece)]));}
function measure(currentStage=stage){
 const width=currentStage.clientWidth,height=currentStage.clientHeight,cell=width/order.length,relative=ratios();
 let maxHeight=1,maxWidth=0;
 for(const piece of order){
  const p=profiles[piece],r=relative[piece];maxHeight=Math.max(maxHeight,r);
  maxWidth=Math.max(maxWidth,r*(p.right-p.left)/(p.bottom-p.top));
 }
 const pixels=Math.min(440,(height-100)/maxHeight,cell*.87/Math.max(maxWidth,.01));
 return {width,height,cell,relative,pixels,ground:height-30};
}
function layout(){
 const selected=[...byId('side-lineup').children].map(card=>card.getAttribute('data-side-piece'));
 if(selected.length===order.length&&new Set(selected).size===order.length&&selected.every(piece=>rows[piece])){
  order=selected;
  for(const piece of order)byId('models-headings').append(byId('models-heading-'+piece));
 }
 const m=measure();
 order.forEach((piece,index)=>{
  byId('models-ratio-'+piece).textContent=(m.relative[piece]*100).toFixed(1)+'% of king';
  if(!m.width||!m.height)return;
  const p=profiles[piece],k=m.pixels*m.relative[piece]/(p.bottom-p.top),img=images[piece];
  img.style.width=(p.width*k)+'px';img.style.left=((index+.5)*m.cell-p.center*k)+'px';
  img.style.top=(m.ground-p.bottom*k)+'px';
 });
 schedule();
}
function selectButtons(){
 byId('models-side').setAttribute('aria-pressed',String(!showBlender&&yaw===0&&pitch===0));
 byId('models-threequarter').setAttribute('aria-pressed',String(!showBlender&&Math.abs(yaw+.43)<1e-6&&Math.abs(pitch-.35)<1e-6));
 byId('models-wood').setAttribute('aria-pressed',String(!showBlender&&wood));
 byId('models-neutral').setAttribute('aria-pressed',String(!showBlender&&!wood));
 byId('models-blender').setAttribute('aria-pressed',String(showBlender));
}
function schedule(){if(!models||!gl||lost||showBlender||panel.hidden||pending)return;pending=true;requestAnimationFrame(()=>{pending=false;draw();});}
function paintDisplay(){
 const ready=Boolean(models&&gl&&!lost),showImages=showBlender||!ready;
 fallback.hidden=!showImages;canvas.hidden=showImages;
 for(const id of ['models-wood','models-neutral'])byId(id).disabled=!ready;
 for(const id of ['models-side','models-threequarter'])byId(id).disabled=!ready||showBlender;
 status.textContent=showBlender?'Saved Blender side renders. The knight is viewed slightly above level; lighting varies between pieces.':ready?'Drag to rotate all pieces together. Lighting in this view is approximate.':loadMessage;
 selectButtons();if(!showImages)schedule();
}
function changeDisplay(blender){
 showBlender=blender;
 const hash=blender?'#blender':'#models';
 if(window.location.hash!==hash)window.location.hash=hash;
 paintDisplay();
}
for(const piece of order){
 byId('side-scale-'+piece).addEventListener('input',layout);
 byId('side-reset-'+piece).addEventListener('click',layout);
}
byId('models-side').addEventListener('click',()=>{yaw=0;pitch=0;selectButtons();schedule();});
byId('models-threequarter').addEventListener('click',()=>{yaw=-.43;pitch=.35;selectButtons();schedule();});
byId('models-wood').addEventListener('click',()=>{wood=true;changeDisplay(false);});
byId('models-neutral').addEventListener('click',()=>{wood=false;changeDisplay(false);});
byId('models-blender').addEventListener('click',()=>changeDisplay(!showBlender));
canvas.addEventListener('pointerdown',event=>{drag={x:event.clientX,y:event.clientY};canvas.setPointerCapture(event.pointerId);});
canvas.addEventListener('pointermove',event=>{if(!drag)return;yaw+=(event.clientX-drag.x)*.008;pitch=Math.max(-1.3,Math.min(1.3,pitch+(event.clientY-drag.y)*.008));drag={x:event.clientX,y:event.clientY};selectButtons();schedule();});
for(const type of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(type,()=>{drag=null;});
canvas.addEventListener('keydown',event=>{
 const step=.1;
 if(event.key==='ArrowLeft')yaw-=step;else if(event.key==='ArrowRight')yaw+=step;
 else if(event.key==='ArrowUp')pitch=Math.max(-1.3,pitch-step);else if(event.key==='ArrowDown')pitch=Math.min(1.3,pitch+step);
 else if(event.key==='Home'){yaw=0;pitch=0;}else return;
 event.preventDefault();selectButtons();schedule();
});
const vertex=`#version 300 es
precision highp float;
layout(location=0) in vec3 aPosition;
layout(location=1) in vec3 aNormal;
layout(location=2) in vec2 aUV;
uniform vec3 uBase;
uniform float uScale,uYaw,uPitch,uPixels,uX,uGround;
uniform vec2 uViewport;
out vec3 vNormal;out vec2 vUV;
vec3 rotatePoint(vec3 p){
 float c=cos(uYaw),s=sin(uYaw);p=vec3(c*p.x+s*p.z,p.y,-s*p.x+c*p.z);
 c=cos(uPitch);s=sin(uPitch);return vec3(p.x,c*p.y-s*p.z,s*p.y+c*p.z);
}
void main(){
 vec3 p=(aPosition-uBase)*uScale;
 p=vec3(p.x,p.z,-p.y);
 p=rotatePoint(p);
 vNormal=rotatePoint(vec3(aNormal.x,aNormal.z,-aNormal.y));vUV=aUV;
 vec2 pixel=vec2(uX+p.x*uPixels,uGround-p.y*uPixels);
 gl_Position=vec4(pixel.x/uViewport.x*2.0-1.0,1.0-pixel.y/uViewport.y*2.0,-p.z/6.0,1.0);
}`;
const fragment=`#version 300 es
precision highp float;
in vec3 vNormal;in vec2 vUV;out vec4 outColor;
uniform sampler2D uWood;uniform bool uUseWood,uBishop;
vec3 light(vec3 n,vec3 l,vec3 pigment,float strength){
 float d=max(dot(n,l),0.0);vec3 h=normalize(l+vec3(0.0,0.0,1.0));
 float spec=pow(max(dot(n,h),0.0),90.0)*step(.001,d)*.22;
 return strength*(pigment*d+vec3(spec));
}
void main(){
 vec3 n=normalize(vNormal);vec3 pigment=vec3(.24,.26,.29);
 if(uUseWood){pigment=uBishop&&vUV.x<0.0?vec3(.153,.076,.023):pow(texture(uWood,vUV).rgb,vec3(2.2));if(uBishop)pigment*=3.0;}
 vec3 c=pigment*(.19+.06*n.y);
 c+=light(n,normalize(vec3(-.65,.9,1.25)),pigment,1.35);
 c+=light(n,normalize(vec3(.85,.2,.9)),pigment,.48);
 c+=light(n,normalize(vec3(.45,.75,-.8)),pigment,.65);
 c=clamp((c*(2.51*c+.03))/(c*(2.43*c+.59)+.14),0.0,1.0);
 outColor=vec4(pow(c,vec3(1.0/2.2)),1.0);
}`;
function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;}
function image(path){return new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=()=>reject(Error('Cannot load '+path));im.src=path;});}
async function fetchOk(path,method){const r=await fetch(path,{cache:'no-cache'});if(!r.ok)throw Error('Cannot load '+path);return r[method]();}
async function queenMesh(){
 const page=new DOMParser().parseFromString(await fetchOk('review.html','text'),'text/html');
 const entry=page.getElementById('viewer-document');if(!entry)throw Error('Queen viewer is missing');
 const viewer=new DOMParser().parseFromString(JSON.parse(entry.textContent),'text/html');
 const meta=JSON.parse(viewer.getElementById('mesh-metadata').textContent);
 const raw=atob(viewer.getElementById('mesh-data').textContent.trim()),bytes=new Uint8Array(raw.length);
 for(let i=0;i<raw.length;i++)bytes[i]=raw.charCodeAt(i);
 return {meta,buffer:bytes.buffer,texture:meta.materialConfig.texture};
}
async function loadPiece(piece){
 let result;
 if(piece==='queen')result=await queenMesh();
 else{
  const [meta,buffer]=await Promise.all([fetchOk('assets/'+piece+'/mesh.json','json'),fetchOk('assets/'+piece+'/mesh.bin','arrayBuffer')]);
  result={meta,buffer,texture:meta.texture||(meta.material&&meta.material.texture)};
 }
 const {meta,buffer}=result;
 if(meta.vertexStrideBytes!==32||meta.vertexByteLength!==meta.vertexCount*32||meta.indexByteOffset!==meta.vertexByteLength||buffer.byteLength!==meta.totalByteLength||!result.texture)throw Error('Incomplete '+piece+' mesh');
 const vertices=new Float32Array(buffer,0,meta.vertexByteLength/4),min=meta.bounds.min,max=meta.bounds.max;
 // Center the round foot, excluding the knight's overhanging head.
 let xmin=Infinity,xmax=-Infinity,ymin=Infinity,ymax=-Infinity;const limit=min[2]+(max[2]-min[2])*.25;
 for(let i=0;i<vertices.length;i+=8)if(vertices[i+2]<=limit){xmin=Math.min(xmin,vertices[i]);xmax=Math.max(xmax,vertices[i]);ymin=Math.min(ymin,vertices[i+1]);ymax=Math.max(ymax,vertices[i+1]);}
 if(!Number.isFinite(xmin)||!Number.isFinite(ymin))throw Error('Invalid '+piece+' base');
 result.base=[(xmin+xmax)/2,(ymin+ymax)/2,min[2]];
 const textureVersion=meta.textureSha256||(meta.material&&meta.material.textureSha256)||meta.sourceSha256;
 result.image=await image(result.texture+'?v='+encodeURIComponent(textureVersion));
 return result;
}
function initialize(){
 const vs=shader(gl.VERTEX_SHADER,vertex),fs=shader(gl.FRAGMENT_SHADER,fragment);program=gl.createProgram();gl.attachShader(program,vs);gl.attachShader(program,fs);gl.linkProgram(program);
 if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(program));
 uniforms={};for(const name of ['uBase','uScale','uYaw','uPitch','uPixels','uX','uGround','uViewport','uWood','uUseWood','uBishop'])uniforms[name]=gl.getUniformLocation(program,name);
 for(const piece of order){
  const model=models[piece],meta=model.meta;model.vao=gl.createVertexArray();gl.bindVertexArray(model.vao);
  const vb=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,vb);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(model.buffer,0,meta.vertexByteLength/4),gl.STATIC_DRAW);
  for(let i=0;i<2;i++){gl.enableVertexAttribArray(i);gl.vertexAttribPointer(i,3,gl.FLOAT,false,32,i*12);}
  gl.enableVertexAttribArray(2);gl.vertexAttribPointer(2,2,gl.FLOAT,false,32,24);
  const ib=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,ib);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint32Array(model.buffer,meta.indexByteOffset,meta.indexCount),gl.STATIC_DRAW);
  model.wood=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,model.wood);gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,true);
  gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,model.image);gl.generateMipmap(gl.TEXTURE_2D);
  gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR_MIPMAP_LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
 }
 gl.bindVertexArray(null);gl.enable(gl.DEPTH_TEST);gl.depthFunc(gl.LEQUAL);
}
function draw(){
 if(!models||!gl||panel.hidden)return;
 const m=measure(),dpr=Math.min(window.devicePixelRatio||1,1.5);
 const width=Math.max(1,Math.round(m.width*dpr)),height=Math.max(1,Math.round(m.height*dpr));
 if(canvas.width!==width||canvas.height!==height){canvas.width=width;canvas.height=height;}
 gl.viewport(0,0,width,height);gl.clearColor(.125,.137,.122,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.useProgram(program);
 gl.uniform2f(uniforms.uViewport,m.width,m.height);gl.uniform1f(uniforms.uYaw,yaw);gl.uniform1f(uniforms.uPitch,pitch);
 gl.uniform1f(uniforms.uPixels,m.pixels);gl.uniform1f(uniforms.uGround,m.ground);gl.uniform1i(uniforms.uWood,0);gl.uniform1i(uniforms.uUseWood,wood?1:0);
 order.forEach((piece,index)=>{
  const model=models[piece],height=model.meta.bounds.size[2],target=m.relative[piece];
  gl.uniform3fv(uniforms.uBase,model.base);gl.uniform1f(uniforms.uScale,target/height);
  gl.uniform1f(uniforms.uX,(index+.5)*m.cell);gl.uniform1i(uniforms.uBishop,piece==='bishop'?1:0);
  gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,model.wood);gl.bindVertexArray(model.vao);
  gl.drawElements(gl.TRIANGLES,model.meta.indexCount,gl.UNSIGNED_INT,0);
 });
}
async function start(){
 layout();paintDisplay();if(started||panel.hidden)return;started=true;
 if(location.protocol==='file:'){loadMessage='Showing model profile renders. Open the local server for the rotatable 3D models.';paintDisplay();return;}
 gl=canvas.getContext('webgl2',{antialias:true,alpha:false});
 if(!gl){loadMessage='Showing model profile renders because 3D graphics are unavailable.';paintDisplay();return;}
 try{
  loadMessage='Loading current 3D models…';paintDisplay();
  const loaded=await Promise.all(order.map(async piece=>[piece,await loadPiece(piece)]));
  models=Object.fromEntries(loaded);initialize();paintDisplay();layout();
 }catch(error){console.error(error);models=null;loadMessage='Could not load all 3D models; showing the saved model profiles.';paintDisplay();}
}
canvas.addEventListener('webglcontextlost',event=>{event.preventDefault();lost=true;loadMessage='3D graphics paused; showing model profiles.';paintDisplay();});
canvas.addEventListener('webglcontextrestored',()=>{lost=false;try{initialize();paintDisplay();layout();}catch(error){console.error(error);models=null;loadMessage='Could not restore 3D graphics; showing model profiles.';paintDisplay();}});
byId('tab-models').addEventListener('click',start);
window.addEventListener('hashchange',()=>{
 if(window.location.hash==='#blender')showBlender=true;
 else if(window.location.hash==='#models')showBlender=false;
 if(!panel.hidden)start();
});
new ResizeObserver(()=>{if(!panel.hidden)layout();}).observe(stage);
paintDisplay();if(!panel.hidden)start();
})();
