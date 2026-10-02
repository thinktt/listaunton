
'use strict';
(() => {
const canvas=document.getElementById('viewer'), status=document.getElementById('status');
const meta=JSON.parse(document.getElementById('mesh-metadata').textContent);
const gl=canvas.getContext('webgl2',{antialias:true,alpha:true,powerPreference:'high-performance'});
if(!gl){status.textContent='This browser could not start 3D graphics. Try opening this page in Chrome or Edge, or open the Blender file below.';return;}
const vs=`#version 300 es
precision highp float;
layout(location=0) in vec3 aPosition;
layout(location=1) in vec3 aNormal;
uniform vec3 uCenter;
uniform mat3 uRotation;
uniform mat4 uProjection;
uniform vec2 uPan;
uniform float uDistance;
out vec3 vNormal;
out vec3 vPosition;
void main(){
 vec3 p=aPosition-uCenter;
 p=uRotation*vec3(p.x,p.z,-p.y);
 vPosition=p+vec3(uPan,-uDistance);
 vNormal=uRotation*vec3(aNormal.x,aNormal.z,-aNormal.y);
 gl_Position=uProjection*vec4(vPosition,1.0);
}`;
const fs=`#version 300 es
precision highp float;
in vec3 vNormal;
in vec3 vPosition;
uniform vec3 uColor;
uniform float uGloss;
out vec4 outColor;
vec3 light(vec3 n,vec3 v,vec3 l,vec3 color,float strength){
 float diffuse=max(dot(n,l),0.0);
 vec3 h=normalize(l+v);
 float spec=pow(max(dot(n,h),0.0),uGloss)*step(0.001,diffuse);
 return strength*color*(uColor*diffuse+vec3(spec*0.25));
}
void main(){
 vec3 n=normalize(vNormal),v=normalize(-vPosition);
 vec3 c=uColor*(0.19+0.06*n.y);
 c+=light(n,v,normalize(vec3(-0.65,0.9,1.25)),vec3(1.0,0.94,0.86),1.45);
 c+=light(n,v,normalize(vec3(0.85,0.2,0.9)),vec3(0.79,0.88,1.0),0.55);
 c+=light(n,v,normalize(vec3(0.45,0.75,-0.8)),vec3(0.9,0.95,1.0),0.8);
 c=clamp((c*(2.51*c+0.03))/(c*(2.43*c+0.59)+0.14),0.0,1.0);
 outColor=vec4(pow(c,vec3(1.0/2.2)),1.0);
}`;
let program,vao,uniforms,meshBytes,ready=false,lost=false,pending=false;
let q=[0,0,0,1],pan=[0,0],distance=9,material='neutral',autoFit=true;
const fov=40*Math.PI/180,tanHalf=Math.tan(fov/2);
const size=meta.bounds.size,radius=Math.hypot(...size)/2;
const clamp=(x,a,b)=>Math.min(b,Math.max(a,x));
const normalize=a=>{const l=Math.hypot(...a);return a.map(v=>v/l);};
const mul=(a,b)=>[
 a[3]*b[0]+a[0]*b[3]+a[1]*b[2]-a[2]*b[1],
 a[3]*b[1]-a[0]*b[2]+a[1]*b[3]+a[2]*b[0],
 a[3]*b[2]+a[0]*b[1]-a[1]*b[0]+a[2]*b[3],
 a[3]*b[3]-a[0]*b[0]-a[1]*b[1]-a[2]*b[2]
];
const axis=(x,y,z,a)=>[x*Math.sin(a/2),y*Math.sin(a/2),z*Math.sin(a/2),Math.cos(a/2)];
function rotation(){const [x,y,z,w]=q;return new Float32Array([
 1-2*(y*y+z*z),2*(x*y+z*w),2*(x*z-y*w),
 2*(x*y-z*w),1-2*(x*x+z*z),2*(y*z+x*w),
 2*(x*z+y*w),2*(y*z-x*w),1-2*(x*x+y*y)
]);}
function fit(){
 const m=rotation(),aspect=Math.max(.2,canvas.clientWidth/canvas.clientHeight);let d=0;
 for(const x of [-size[0]/2,size[0]/2])for(const y of [-size[2]/2,size[2]/2])for(const z of [-size[1]/2,size[1]/2]){
  const rx=m[0]*x+m[3]*y+m[6]*z,ry=m[1]*x+m[4]*y+m[7]*z,rz=m[2]*x+m[5]*y+m[8]*z;
  d=Math.max(d,Math.abs(rx)/(tanHalf*aspect)+rz,Math.abs(ry)/tanHalf+rz);
 }
 distance=d*1.22;pan=[0,0];
}
function unselectViews(){document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed','false'));}
function view(name){
 const views={perspective:mul(axis(1,0,0,25*Math.PI/180),axis(0,1,0,-25*Math.PI/180)),front:[0,0,0,1],side:axis(0,1,0,Math.PI/2),top:axis(1,0,0,Math.PI/2),bottom:axis(1,0,0,-Math.PI/2)};
 q=views[name]||views.perspective;autoFit=true;fit();
 document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===name)));
 schedule();
}
function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS)){const info=gl.getShaderInfoLog(s);gl.deleteShader(s);throw new Error(info);}return s;}
function initialize(){
 const vert=shader(gl.VERTEX_SHADER,vs),frag=shader(gl.FRAGMENT_SHADER,fs);
 program=gl.createProgram();gl.attachShader(program,vert);gl.attachShader(program,frag);gl.linkProgram(program);
 if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error(gl.getProgramInfoLog(program));
 gl.deleteShader(vert);gl.deleteShader(frag);
 vao=gl.createVertexArray();gl.bindVertexArray(vao);
 const vb=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,vb);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(meshBytes.buffer,0,meta.vertexByteLength/4),gl.STATIC_DRAW);
 for(let i=0;i<2;i++){gl.enableVertexAttribArray(i);gl.vertexAttribPointer(i,3,gl.FLOAT,false,meta.vertexStrideBytes,i*12);}
 const ib=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,ib);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,new Uint32Array(meshBytes.buffer,meta.indexByteOffset,meta.indexCount),gl.STATIC_DRAW);
 uniforms={};for(const name of ['uCenter','uRotation','uProjection','uPan','uDistance','uColor','uGloss'])uniforms[name]=gl.getUniformLocation(program,name);
 gl.enable(gl.DEPTH_TEST);gl.enable(gl.CULL_FACE);gl.cullFace(gl.BACK);gl.clearColor(0,0,0,0);
 const error=gl.getError();if(error!==gl.NO_ERROR)throw new Error('WebGL upload error '+error);
 ready=true;status.hidden=true;schedule();
}
function draw(){
 pending=false;if(!ready||lost)return;
 const dpr=Math.min(window.devicePixelRatio||1,2),w=Math.max(1,Math.round(canvas.clientWidth*dpr)),h=Math.max(1,Math.round(canvas.clientHeight*dpr));
 if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;}
 gl.viewport(0,0,w,h);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.useProgram(program);gl.bindVertexArray(vao);
 const f=1/tanHalf,n=radius*.01,far=radius*100;
 gl.uniformMatrix4fv(uniforms.uProjection,false,new Float32Array([f/(w/h),0,0,0,0,f,0,0,0,0,(far+n)/(n-far),-1,0,0,2*far*n/(n-far),0]));
 gl.uniformMatrix3fv(uniforms.uRotation,false,rotation());gl.uniform3fv(uniforms.uCenter,meta.bounds.center);
 gl.uniform2fv(uniforms.uPan,pan);gl.uniform1f(uniforms.uDistance,distance);
 gl.uniform3fv(uniforms.uColor,material==='brown'?[.12,.045,.018]:[.24,.26,.29]);gl.uniform1f(uniforms.uGloss,material==='brown'?90:55);
 gl.drawElements(gl.TRIANGLES,meta.indexCount,gl.UNSIGNED_INT,0);
}
function schedule(){if(!pending){pending=true;requestAnimationFrame(draw);}}
function zoom(factor){autoFit=false;distance=clamp(distance*factor,radius*.8,radius*20);schedule();}
function shift(dx,dy){autoFit=false;const scale=2*distance*tanHalf/canvas.clientHeight;pan[0]+=dx*scale;pan[1]-=dy*scale;schedule();}
function ball(x,y){const r=canvas.getBoundingClientRect(),scale=.45*Math.min(r.width,r.height);x=(x-r.left-r.width/2)/scale;y=(r.height/2-y+r.top)/scale;const s=x*x+y*y;return normalize([x,y,s<=.5?Math.sqrt(1-s):.5/Math.sqrt(s)]);}
function turn(a,b){
 const dot=clamp(a[0]*b[0]+a[1]*b[1]+a[2]*b[2],-1,1);
 let delta=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0],1+dot];
 if(dot<-.999999){const orth=Math.abs(a[0])<.9?[1,0,0]:[0,1,0];delta=[a[1]*orth[2]-a[2]*orth[1],a[2]*orth[0]-a[0]*orth[2],a[0]*orth[1]-a[1]*orth[0],0];}
 q=normalize(mul(normalize(delta),q));unselectViews();schedule();
}
const pointers=new Map();
function gesture(){const p=[...pointers.values()];return p.length<2?null:{x:(p[0].x+p[1].x)/2,y:(p[0].y+p[1].y)/2,d:Math.hypot(p[0].x-p[1].x,p[0].y-p[1].y)};}
canvas.addEventListener('pointerdown',e=>{if(e.button!==0&&e.button!==2)return;e.preventDefault();canvas.focus({preventScroll:true});canvas.setPointerCapture(e.pointerId);pointers.set(e.pointerId,{x:e.clientX,y:e.clientY,pan:e.button===2||e.shiftKey});canvas.classList.add('dragging');});
canvas.addEventListener('pointermove',e=>{
 const old=pointers.get(e.pointerId);if(!old)return;e.preventDefault();const before=gesture();
 pointers.set(e.pointerId,{...old,x:e.clientX,y:e.clientY});const after=gesture();
 if(before&&after){if(before.d>3&&after.d>3)zoom(before.d/after.d);shift(after.x-before.x,after.y-before.y);}
 else if(old.pan||e.shiftKey)shift(e.clientX-old.x,e.clientY-old.y);
 else turn(ball(old.x,old.y),ball(e.clientX,e.clientY));
});
function release(e){pointers.delete(e.pointerId);if(!pointers.size)canvas.classList.remove('dragging');}
for(const name of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(name,release);
canvas.addEventListener('contextmenu',e=>e.preventDefault());
canvas.addEventListener('wheel',e=>{e.preventDefault();const unit=e.deltaMode===1?16:e.deltaMode===2?canvas.clientHeight:1;zoom(Math.exp(clamp(e.deltaY*unit,-300,300)*.0012));},{passive:false});
canvas.addEventListener('dblclick',()=>view('perspective'));
canvas.addEventListener('keydown',e=>{
 const keys=['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','=','-','_','r','R'];if(!keys.includes(e.key))return;e.preventDefault();
 if(e.key.toLowerCase()==='r')view('perspective');else if(e.key==='+'||e.key==='=')zoom(.85);else if(e.key==='-'||e.key==='_')zoom(1/.85);
 else if(e.shiftKey)shift(e.key==='ArrowLeft'?-24:e.key==='ArrowRight'?24:0,e.key==='ArrowUp'?-24:e.key==='ArrowDown'?24:0);
 else{const angle=Math.PI/24;const d=e.key==='ArrowLeft'?axis(0,1,0,-angle):e.key==='ArrowRight'?axis(0,1,0,angle):e.key==='ArrowUp'?axis(1,0,0,-angle):axis(1,0,0,angle);q=normalize(mul(d,q));unselectViews();schedule();}
});
document.getElementById('reset').onclick=()=>view('perspective');
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>view(b.dataset.view));
document.getElementById('zoom-in').onclick=()=>zoom(.85);document.getElementById('zoom-out').onclick=()=>zoom(1/.85);
for(const name of ['neutral','brown'])document.getElementById(name).onclick=()=>{material=name;for(const id of ['neutral','brown'])document.getElementById(id).setAttribute('aria-pressed',String(id===name));document.getElementById('surface-note').textContent=name==='brown'?'Geometry study · plain brown, wood grain to come':'Geometry study · neutral surface';schedule();};
new ResizeObserver(()=>{if(autoFit)fit();schedule();}).observe(canvas);
canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();lost=true;ready=false;status.hidden=false;status.textContent='3D graphics paused. Restoring the view…';});
canvas.addEventListener('webglcontextrestored',()=>{lost=false;try{initialize();}catch(e){fail(e);}});
function fail(error){status.hidden=false;status.textContent='The 3D view could not load. You can still open the Blender file below.';console.error(error);}
view('perspective');
requestAnimationFrame(()=>setTimeout(()=>{try{
 const encoded=document.getElementById('mesh-data');const raw=atob(encoded.textContent.trim());meshBytes=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)meshBytes[i]=raw.charCodeAt(i);encoded.remove();
 if(meshBytes.byteLength!==meta.totalByteLength)throw new Error('Mesh size mismatch');initialize();
}catch(e){fail(e);}},0));
})();
