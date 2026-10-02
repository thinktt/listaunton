// Numerical regression check of the actual viewer's uniforms and event handlers.
// No browser, network request, or HTML rendering; Blender supplies expected pixels.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const path=require('node:path'),root=path.resolve(__dirname,'../..');
const html=fs.readFileSync(path.join(root,'queen-3d.html'),'utf8');
const truth=JSON.parse(fs.readFileSync(path.join(root,'build/queen/viewer-camera.json'),'utf8'));
const text=id=>html.match(new RegExp(`<script id="${id}"[^>]*>([\\s\\S]*?)</script>`))[1];
const source=html.match(/<script>\s*([\s\S]*?)<\/script>/)[1],uniforms={},queue=[],listeners={},nodes=new Map();
let resize,draws=0;const parentMessages=[],windowListeners={};const parentFrame={postMessage(message){parentMessages.push(message);}};
const node=id=>{if(!nodes.has(id))nodes.set(id,{id,attrs:{},hidden:false,setAttribute(k,v){this.attrs[k]=v;},remove(){},textContent:''});return nodes.get(id);};
const views=[...html.matchAll(/data-view="([^"]+)"/g)].map(m=>Object.assign(node('view-'+m[1]),{dataset:{view:m[1]}}));
node('mesh-metadata').textContent=text('mesh-metadata');node('mesh-data').textContent=text('mesh-data');
const gl=new Proxy({NO_ERROR:0,getError:()=>0,getShaderParameter:()=>true,getProgramParameter:()=>true,
 getUniformLocation:(_,name)=>name,drawElements:()=>draws++,
 uniformMatrix4fv:(name,_,v)=>uniforms[name]=Array.from(v,Math.fround),
 uniformMatrix3fv:(name,_,v)=>uniforms[name]=Array.from(v,Math.fround),
 uniform3fv:(name,v)=>uniforms[name]=Array.from(v,Math.fround),
 uniform2fv:(name,v)=>uniforms[name]=Array.from(v,Math.fround),
 uniform1f:(name,v)=>uniforms[name]=Math.fround(v),uniform1i:(name,v)=>uniforms[name]=v
},{get:(target,key)=>key in target?target[key]:(...args)=>({})});
const canvas=Object.assign(node('viewer'),{clientWidth:1254,clientHeight:1254,width:1254,height:1254,
 getContext:()=>gl,addEventListener:(name,fn)=>listeners[name]=fn,
 getBoundingClientRect:()=>({left:0,top:0,width:canvas.clientWidth,height:canvas.clientHeight}),
 focus(){},setPointerCapture(){},classList:{add(){},remove(){}}});
const context={console,Float32Array,Uint32Array,Uint8Array,Math,JSON,
 document:{getElementById:node,querySelectorAll:()=>views},window:{devicePixelRatio:1,parent:parentFrame,addEventListener(name,fn){windowListeners[name]=fn;}},
 requestAnimationFrame:cb=>queue.push(cb),setTimeout:cb=>queue.push(cb),
 atob:s=>Buffer.from(s,'base64').toString('binary'),
 ResizeObserver:class{constructor(cb){resize=cb;}observe(){}}
};
vm.runInNewContext(source,context,{filename:'queen-3d-runtime.js'});
function flush(){let n=0;while(queue.length){assert(n++<20);queue.shift()();}}
flush();assert(draws>0,'Viewer did not reach drawElements');assert(node('status').hidden,'Viewer failed initialization');
function pixel(world){
 const c=uniforms.uCenter,r=uniforms.uRotation,p=uniforms.uProjection;
 const b=[world[0]-c[0],world[2]-c[2],-(world[1]-c[1])];
 const v=[r[0]*b[0]+r[3]*b[1]+r[6]*b[2]+uniforms.uPan[0],r[1]*b[0]+r[4]*b[1]+r[7]*b[2]+uniforms.uPan[1],r[2]*b[0]+r[5]*b[1]+r[8]*b[2]-uniforms.uDistance,1];
 const clip=[0,1,2,3].map(i=>p[i]*v[0]+p[i+4]*v[1]+p[i+8]*v[2]+p[i+12]);
 return [(clip[0]/clip[3]+1)*canvas.width/2,(1-clip[1]/clip[3])*canvas.height/2];
}
let maxError=0;
function compare(){
 assert.equal(uniforms.uOrthographic,1);
 const {width,height}=truth.referenceCamera,scale=Math.min(canvas.width/width,canvas.height/height);
 for(const s of truth.samples){const actual=pixel(s.world),expected=[(canvas.width-width*scale)/2+s.pixel[0]*scale,(canvas.height-height*scale)/2+s.pixel[1]*scale];
  const error=Math.hypot(actual[0]-expected[0],actual[1]-expected[1]);maxError=Math.max(maxError,error);assert(error<.001,`${s.name}: ${error}px`);}
}
compare();
for(const [w,h] of [[1600,850],[390,700],[1254,1254]]){canvas.clientWidth=w;canvas.clientHeight=h;resize();flush();compare();}
node('perspective').onclick();flush();assert.equal(uniforms.uOrthographic,0);assert.equal(uniforms.uProjection[11],-1);
listeners.keydown({key:'ArrowRight',shiftKey:false,preventDefault(){}});flush();
listeners.wheel({deltaMode:0,deltaY:120,preventDefault(){}});flush();
node('reset').onclick();flush();compare();
listeners.pointerdown({button:0,pointerId:1,clientX:620,clientY:620,shiftKey:false,preventDefault(){}});
listeners.pointermove({pointerId:1,clientX:820,clientY:840,shiftKey:false,preventDefault(){}});listeners.pointerup({pointerId:1});flush();
assert.equal(uniforms.uOrthographic,1);assert.equal(node('view-overlay').attrs['aria-pressed'],'false');
const manualState=JSON.stringify([uniforms.uRotation,uniforms.uPan,uniforms.uDistance,uniforms.uProjection[5]]);
canvas.clientWidth=1400;resize();flush();
assert.equal(JSON.stringify([uniforms.uRotation,uniforms.uPan,uniforms.uDistance,uniforms.uProjection[5]]),manualState,'Resize changed manual orbit framing');
node('view-overlay').onclick();flush();compare();
const before=pixel([0,0,2]);
listeners.pointerdown({button:2,pointerId:2,clientX:600,clientY:600,shiftKey:false,preventDefault(){}});
listeners.pointermove({pointerId:2,clientX:650,clientY:570,shiftKey:false,preventDefault(){}});listeners.pointerup({pointerId:2});flush();
const after=pixel([0,0,2]);assert(Math.abs(after[0]-before[0]-50)<.001);assert(Math.abs(after[1]-before[1]+30)<.001);
node('reset').onclick();flush();compare();
const result={passed:true,blenderSampleCount:truth.samples.length,viewportShapes:5,maxPixelError:maxError,projectionSwitch:true,dragRotation:true,panPixelAccuracy:true,resetRestoresCamera:true,manualViewSurvivesResize:true,sourceSha256:truth.sourceSha256};
fs.writeFileSync(path.join(root,'build/queen/viewer-camera-check.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));

assert(parentMessages.some(message=>message.channel==='listaunton-review'&&message.event==='viewer-ready'));
const rotationBeforeBridge=JSON.stringify(uniforms.uRotation);
windowListeners.message({source:{},data:{channel:'listaunton-review',action:'orbit',dx:.1,dy:.1}});flush();
assert.equal(JSON.stringify(uniforms.uRotation),rotationBeforeBridge,'An unrelated window changed the model');
windowListeners.message({source:parentFrame,data:{channel:'listaunton-review',action:'orbit',dx:.1,dy:.1}});flush();
assert.notEqual(JSON.stringify(uniforms.uRotation),rotationBeforeBridge,'The handoff drag did not rotate the model');
windowListeners.message({source:parentFrame,data:{channel:'listaunton-review',action:'activate',reset:true,material:'brown'}});flush();compare();
assert.equal(node('brown').attrs['aria-pressed'],'true');
const beforeBridgePan=Array.from(uniforms.uPan);
windowListeners.message({source:parentFrame,data:{channel:'listaunton-review',action:'pan',dx:.1,dy:-.1}});flush();
assert.notDeepEqual(Array.from(uniforms.uPan),beforeBridgePan);
const rotationBeforeInvalid=JSON.stringify(uniforms.uRotation);
windowListeners.message({source:parentFrame,data:{channel:'listaunton-review',action:'orbit',dx:NaN,dy:Infinity}});flush();
assert.equal(JSON.stringify(uniforms.uRotation),rotationBeforeInvalid);
windowListeners.message({source:parentFrame,data:{channel:'listaunton-review',action:'activate',reset:true,material:'neutral'}});flush();compare();
console.log('PASS: embedded viewer readiness, parent-only gesture bridge, orbit, pan, material sync and exact camera reset.');
