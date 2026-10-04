// Runtime checks use the actual page scripts and recorded WebGL uniforms.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=process.argv[2]||path.resolve(__dirname,'../..');
const html=fs.readFileSync(path.join(root,'king-projections.html'),'utf8');
const contents=id=>html.match(new RegExp(`<script id="${id}"[^>]*>([\\s\\S]*?)</script>`))[1];
const config=JSON.parse(contents('projection-data'));
const source=html.match(/<script>\s*([\s\S]*?)<\/script>/)[1];
function harness(noWebGL=false){
 const nodes=new Map(),queue=[],listeners={},uniforms={},windowListeners={};let resize,draws=0,indexCount;
 const node=id=>{if(!nodes.has(id))nodes.set(id,{id,tagName:'DIV',attrs:{},hidden:false,style:{},dataset:{},events:{},value:'',
  setAttribute(k,v){this.attrs[k]=v;},remove(){},addEventListener(k,v){this.events[k]=v;},textContent:''});return nodes.get(id);};
 const views=[...html.matchAll(/<button[^>]*data-view="([^"]+)"[^>]*>/g)].map(m=>Object.assign(node('view-'+m[1]),{tagName:'BUTTON',dataset:{view:m[1]}}));
 const variants=[...html.matchAll(/<(button|img)[^>]*data-variant="([^"]+)"[^>]*>/g)].map((m,i)=>Object.assign(node('variant-'+i),{tagName:m[1].toUpperCase(),dataset:{variant:m[2]},isRender:m[0].includes('render-layer')}));
 const renders=variants.filter(n=>n.isRender);
 node('projection-data').textContent=contents('projection-data');
 for(const variant of config.variants)node('mesh-'+variant.id).textContent=contents('mesh-'+variant.id);
 node('model-opacity').value='50';node('stage').dataset.mode='profiles';node('stage').clientWidth=1254;node('stage').clientHeight=1254;
 const gl=new Proxy({NO_ERROR:0,getError:()=>0,getShaderParameter:()=>true,getProgramParameter:()=>true,
  getUniformLocation:(_,name)=>name,drawElements:(_,count)=>{draws++;indexCount=count;},
  uniformMatrix4fv:(name,_,v)=>uniforms[name]=Array.from(v,Math.fround),uniformMatrix3fv:(name,_,v)=>uniforms[name]=Array.from(v,Math.fround),
  uniform3fv:(name,v)=>uniforms[name]=Array.from(v,Math.fround),uniform2fv:(name,v)=>uniforms[name]=Array.from(v,Math.fround),
  uniform1f:(name,v)=>uniforms[name]=Math.fround(v),uniform1i:(name,v)=>uniforms[name]=v
 },{get:(target,key)=>key in target?target[key]:(...args)=>({})});
 const canvas=Object.assign(node('viewer'),{clientWidth:1254,clientHeight:1254,width:1254,height:1254,
  getContext:()=>noWebGL?null:gl,addEventListener:(name,fn)=>listeners[name]=fn,
  getBoundingClientRect:()=>({left:0,top:0,width:canvas.clientWidth,height:canvas.clientHeight}),
  focus(){},setPointerCapture(){},classList:{add(){},remove(){}}});
 const context={console,Float32Array,Uint32Array,Uint8Array,Math,JSON,
  document:{getElementById:node,querySelectorAll:s=>s==='[data-view]'?views:s==='.render-layer'?renders:s==='button[data-variant]'?variants.filter(n=>n.tagName==='BUTTON'):variants},
  window:{devicePixelRatio:1,parent:{postMessage(){}},addEventListener(name,fn){windowListeners[name]=fn;}},
  requestAnimationFrame:cb=>queue.push(cb),setTimeout:cb=>queue.push(cb),atob:s=>Buffer.from(s,'base64').toString('binary'),
  ResizeObserver:class{constructor(cb){resize=cb;}observe(){}}
 };
 vm.runInNewContext(source,context,{filename:'king-projections-runtime.js'});
 function flush(){let n=0;while(queue.length){assert(n++<30);queue.shift()();}}
 function select(id){variants.find(n=>n.tagName==='BUTTON'&&n.dataset.variant===id).onclick();flush();}
 return {nodes,node,canvas,views,variants,renders,listeners,uniforms,flush,select,get indexCount(){return indexCount;},get draws(){return draws;},resize:()=>resize()};
}
const h=harness();h.flush();assert(h.draws>0);assert.equal(h.node('stage').dataset.mode,'profiles');
const state=()=>JSON.stringify([h.uniforms.uCenter,h.uniforms.uRotation,h.uniforms.uPan,h.uniforms.uDistance,h.uniforms.uProjection]);
const baselineState=state();
h.node('rotate-tab').onclick();h.flush();assert.equal(state(),baselineState);
for(const variant of config.variants){h.select(variant.id);assert.equal(state(),baselineState,'Switching variants changed shared framing');assert.equal(h.indexCount,variant.meta.indexCount);assert.equal(h.node('model-download').href,variant.model);}
h.listeners.pointerdown({button:0,pointerId:1,clientX:620,clientY:620,shiftKey:false,preventDefault(){}});
h.listeners.pointermove({pointerId:1,clientX:820,clientY:840,shiftKey:false,preventDefault(){}});h.listeners.pointerup({pointerId:1});h.flush();
h.listeners.wheel({deltaMode:0,deltaY:100,preventDefault(){}});h.flush();
h.listeners.pointerdown({button:2,pointerId:2,clientX:600,clientY:600,shiftKey:false,preventDefault(){}});
h.listeners.pointermove({pointerId:2,clientX:630,clientY:570,shiftKey:false,preventDefault(){}});h.listeners.pointerup({pointerId:2});h.flush();
const manualState=state();
for(const variant of config.variants){h.select(variant.id);assert.equal(state(),manualState,'Switching variants moved manual camera');}
h.node('compare-tab').onclick();h.flush();h.node('profiles-tab').onclick();h.flush();h.node('rotate-tab').onclick();h.flush();assert.equal(state(),manualState,'Switching tabs changed orbit');
h.node('reset').onclick();h.flush();assert.equal(state(),baselineState,'Reset did not restore shared front camera');
const matvec=(m,v)=>[0,1,2,3].map(i=>v.reduce((a,x,j)=>a+x*m[i*4+j],0));
function pixel(world){const u=h.uniforms,c=u.uCenter,r=u.uRotation,p=u.uProjection,b=[world[0]-c[0],world[2]-c[2],-(world[1]-c[1])];
 const v=[r[0]*b[0]+r[3]*b[1]+r[6]*b[2]+u.uPan[0],r[1]*b[0]+r[4]*b[1]+r[7]*b[2]+u.uPan[1],r[2]*b[0]+r[5]*b[1]+r[8]*b[2]-u.uDistance,1];
 const clip=[0,1,2,3].map(i=>p[i]*v[0]+p[i+4]*v[1]+p[i+8]*v[2]+p[i+12]);return [(clip[0]/clip[3]+1)*h.canvas.width/2,(1-clip[1]/clip[3])*h.canvas.height/2];}
let maxError=0,samples=0;
for(const variant of config.variants){
 h.select(variant.id);h.node('view-overlay').onclick();h.flush();
 const ref=variant.meta.referenceCamera,buffer=Buffer.from(contents('mesh-'+variant.id),'base64');
 for(const [w,height] of [[1254,1254],[1600,850],[390,700]]){
  h.canvas.clientWidth=w;h.canvas.clientHeight=height;h.resize();h.flush();
  const scale=Math.min(w/ref.width,height/ref.height);
  for(let i=0;i<variant.meta.vertexCount;i+=Math.max(1,Math.floor(variant.meta.vertexCount/100))){
   const world=[0,1,2].map(j=>buffer.readFloatLE(i*24+j*4));
   const clip=matvec(ref.projectionMatrix.flat(),matvec(ref.worldToCamera.flat(),[...world,1]));
   const expected=[(w-ref.width*scale)/2+(clip[0]/clip[3]+1)*ref.width/2*scale,(height-ref.height*scale)/2+(1-clip[1]/clip[3])*ref.height/2*scale];
   const actual=pixel(world),error=Math.hypot(actual[0]-expected[0],actual[1]-expected[1]);maxError=Math.max(error,maxError);assert(error<.001,variant.id+' camera mismatch '+error);samples++;
  }
 }
 const cameraState=state();const next=config.variants.find(v=>v.id!==variant.id);
 h.select(next.id);assert.equal(state(),cameraState,'Switching variant abandoned chosen reference camera');
}
h.node('compare-tab').onclick();
for(const [id,value] of [['reference-only',0],['model-only',1],['half-overlay',.5]]){h.node(id).onclick();for(const image of h.renders)assert.equal(image.style.opacity,value);}
h.node('reference-choice').events.change({target:{value:'selected'}});assert(h.node('original-image').hidden);assert(!h.node('reference-image').hidden);
h.node('reference-choice').events.change({target:{value:'original'}});assert(!h.node('original-image').hidden);assert(h.node('reference-image').hidden);
const fallback=harness(true);assert(fallback.node('rotate-tab').disabled);fallback.select(config.variants.find(v=>v.id!==config.baseline).id);fallback.node('compare-tab').onclick();assert.equal(fallback.node('stage').dataset.mode,'compare');
console.log(JSON.stringify({passed:true,variants:config.variants.length,meshCameraSamples:samples,maxCameraErrorPx:maxError,sharedPhysicalScale:true,variantSwitchRetainsOrbitPanZoom:true,referenceCameraSwitchIsExplicit:true,overlaySourcesAndEndpoints:true,profilesRemainUsableWithoutWebGL:true},null,2));
