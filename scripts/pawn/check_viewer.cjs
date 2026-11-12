// Exercise the actual pawn page's WebGL uniforms and controls without a browser.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=process.argv[2]||path.resolve(__dirname,'../..');
const html=fs.readFileSync(path.join(root,'pawn-model.html'),'utf8');
const text=id=>html.match(new RegExp(`<script id="${id}"[^>]*>([\\s\\S]*?)</script>`))[1];
const meta=JSON.parse(text('mesh-metadata')),mesh=Buffer.from(text('mesh-data'),'base64');
const source=html.match(/<script>\s*([\s\S]*?)<\/script>/)[1],uniforms={},queue=[],listeners={},nodes=new Map();
let resize,draws=0;const windowListeners={},parentMessages=[];
const parentFrame={postMessage(m){parentMessages.push(m);}};
const node=id=>{if(!nodes.has(id))nodes.set(id,{id,attrs:{},hidden:false,style:{},dataset:{},events:{},value:'',
 setAttribute(k,v){this.attrs[k]=v;},remove(){},addEventListener(k,v){this.events[k]=v;},textContent:''});return nodes.get(id);};
const views=[...html.matchAll(/data-view="([^"]+)"/g)].map(m=>Object.assign(node('view-'+m[1]),{dataset:{view:m[1]}}));
node('mesh-metadata').textContent=text('mesh-metadata');node('mesh-data').textContent=text('mesh-data');node('original-alignment').textContent=text('original-alignment');
node('side-registration').textContent=text('side-registration');node('side-opacity').value='50';
node('wood-texture').textContent=text('wood-texture');
assert.equal(require('node:crypto').createHash('sha256').update(Buffer.from(text('wood-texture'),'base64')).digest('hex'),meta.textureSha256);
for(const key of ['varnish','slope']){
 if(!meta[key])continue;
 const id=key+'-texture',bytes=Buffer.from(text(id),'base64');
 node(id).textContent=text(id);
 assert.equal(require('node:crypto').createHash('sha256').update(bytes).digest('hex'),meta[key].sha256);
 assert.deepEqual(bytes,fs.readFileSync(path.join(root,meta[key].file)));
}
assert.equal(meta.vertexStrideBytes,32);
node('model-opacity').value='50';node('stage').dataset.mode='compare';
node('stage').clientWidth=1254;node('stage').clientHeight=1254;
const gl=new Proxy({NO_ERROR:0,getError:()=>0,getShaderParameter:()=>true,getProgramParameter:()=>true,
 getUniformLocation:(_,name)=>name,drawElements:()=>draws++,
 uniformMatrix4fv:(name,_,v)=>uniforms[name]=Array.from(v,Math.fround),uniformMatrix3fv:(name,_,v)=>uniforms[name]=Array.from(v,Math.fround),
 uniform3fv:(name,v)=>uniforms[name]=Array.from(v,Math.fround),uniform2fv:(name,v)=>uniforms[name]=Array.from(v,Math.fround),
 uniform1f:(name,v)=>uniforms[name]=Math.fround(v),uniform1i:(name,v)=>uniforms[name]=v
},{get:(target,key)=>key in target?target[key]:(...args)=>({})});
const canvas=Object.assign(node('viewer'),{clientWidth:1254,clientHeight:1254,width:1254,height:1254,
 getContext:()=>gl,addEventListener:(name,fn)=>listeners[name]=fn,
 getBoundingClientRect:()=>({left:0,top:0,width:canvas.clientWidth,height:canvas.clientHeight}),
 focus(){},setPointerCapture(){},classList:{add(){},remove(){}}});
const context={Image:class{set src(value){this._src=value;queue.push(()=>this.onload());}},console,Float32Array,Uint32Array,Uint8Array,Math,JSON,
 document:{getElementById:node,querySelectorAll:()=>views},window:{devicePixelRatio:1,parent:parentFrame,addEventListener(name,fn){windowListeners[name]=fn;}},
 requestAnimationFrame:cb=>queue.push(cb),setTimeout:cb=>queue.push(cb),atob:s=>Buffer.from(s,'base64').toString('binary'),
 ResizeObserver:class{constructor(cb){resize=cb;}observe(){}}
};
vm.runInNewContext(source,context,{filename:'pawn-model-runtime.js'});
function flush(){let n=0;while(queue.length){assert(n++<20);queue.shift()();}}
flush();assert(draws>0);assert(node('status').hidden);assert.equal(canvas.tabIndex,-1);assert.equal(node('model-image').style.opacity,.5);
if(meta.varnish){
 assert.equal(uniforms.uVarnish,1);
 assert.deepEqual(uniforms.uVarnishRange,Array.from(meta.varnish.gain,Math.fround));
 assert.deepEqual(uniforms.uPolishRange,Array.from(meta.varnish.polishGain||[1,1],Math.fround));
}
if(meta.slope){
 assert.equal(uniforms.uSlope,2);
 assert.equal(uniforms.uSlopeLimit,Math.fround(meta.slope.limit));
}
if(meta.matteBand){
 assert.deepEqual(uniforms.uMatteRise,Array.from(meta.matteBand.rise,Math.fround));
 assert.deepEqual(uniforms.uMatteFall,Array.from(meta.matteBand.fall,Math.fround));
 assert.equal(uniforms.uMatteFraction,Math.fround(meta.matteBand.fraction));
 assert(source.includes('polish*=1.0-matte;'));
}
assert(html.includes('<option value="original">Original black</option><option value="selected">Black candidate 2</option>'),'Original must be default reference.');
const alignment=JSON.parse(text('original-alignment'));
assert.equal(parseFloat(node('original-image').style.width),100/alignment.scale);
assert.equal(parseFloat(node('original-image').style.left),-alignment.x/alignment.scale);
assert.equal(parseFloat(node('original-image').style.top),-alignment.y/alignment.scale);
node('reference-choice').events.change({target:{value:'selected'}});assert(node('original-image').hidden);assert(!node('reference-image').hidden);
node('reference-choice').events.change({target:{value:'original'}});assert(!node('original-image').hidden);assert(node('reference-image').hidden);
function pixel(world){
 const c=uniforms.uCenter,r=uniforms.uRotation,p=uniforms.uProjection,b=[world[0]-c[0],world[2]-c[2],-(world[1]-c[1])];
 const v=[r[0]*b[0]+r[3]*b[1]+r[6]*b[2]+uniforms.uPan[0],r[1]*b[0]+r[4]*b[1]+r[7]*b[2]+uniforms.uPan[1],r[2]*b[0]+r[5]*b[1]+r[8]*b[2]-uniforms.uDistance,1];
 const clip=[0,1,2,3].map(i=>p[i]*v[0]+p[i+4]*v[1]+p[i+8]*v[2]+p[i+12]);
 return [(clip[0]/clip[3]+1)*canvas.width/2,(1-clip[1]/clip[3])*canvas.height/2];
}
const matvec=(m,v)=>[0,1,2,3].map(i=>v.reduce((a,x,j)=>a+x*m[i*4+j],0));
const ref=meta.referenceCamera,points=[];
for(let i=0;i<meta.vertexCount;i+=Math.max(1,Math.floor(meta.vertexCount/500))){const off=i*meta.vertexStrideBytes;points.push([mesh.readFloatLE(off),mesh.readFloatLE(off+4),mesh.readFloatLE(off+8)]);}
let maxError=0;
function compare(){
 assert.equal(uniforms.uOrthographic,1);const scale=Math.min(canvas.width/ref.width,canvas.height/ref.height);
 for(const point of points){const clip=matvec(ref.projectionMatrix.flat(),matvec(ref.worldToCamera.flat(),[...point,1]));
  const px=(clip[0]/clip[3]+1)*ref.width/2,py=(1-clip[1]/clip[3])*ref.height/2;
  const expected=[(canvas.width-ref.width*scale)/2+px*scale,(canvas.height-ref.height*scale)/2+py*scale],actual=pixel(point);
  const error=Math.hypot(actual[0]-expected[0],actual[1]-expected[1]);maxError=Math.max(maxError,error);assert(error<.001,`${error}px camera error`);
 }
}
compare();for(const [w,h] of [[1600,850],[390,700],[1254,1254]]){canvas.clientWidth=w;canvas.clientHeight=h;resize();flush();compare();}
node('rotate-tab').onclick();flush();assert.equal(node('stage').dataset.mode,'rotate');assert.equal(canvas.tabIndex,0);assert(node('comparison-controls').hidden);assert(!node('rotation-controls').hidden);compare();
node('perspective').onclick();flush();assert.equal(uniforms.uOrthographic,0);
listeners.pointerdown({button:0,pointerId:1,clientX:620,clientY:620,shiftKey:false,preventDefault(){}});
listeners.pointermove({pointerId:1,clientX:820,clientY:840,shiftKey:false,preventDefault(){}});listeners.pointerup({pointerId:1});flush();
listeners.wheel({deltaMode:0,deltaY:120,preventDefault(){}});flush();
const orbit=JSON.stringify([uniforms.uRotation,uniforms.uPan,uniforms.uProjection]);
node('compare-tab').onclick();flush();node('rotate-tab').onclick();flush();assert.equal(JSON.stringify([uniforms.uRotation,uniforms.uPan,uniforms.uProjection]),orbit,'Tabs changed orbit');
node('reset').onclick();flush();compare();
const before=pixel([0,0,2]);
listeners.pointerdown({button:2,pointerId:2,clientX:600,clientY:600,shiftKey:false,preventDefault(){}});
listeners.pointermove({pointerId:2,clientX:650,clientY:570,shiftKey:false,preventDefault(){}});listeners.pointerup({pointerId:2});flush();
const after=pixel([0,0,2]);assert(Math.abs(after[0]-before[0]-50)<.001);assert(Math.abs(after[1]-before[1]+30)<.001);
node('reset').onclick();flush();compare();
node('compare-tab').onclick();flush();
for(const [id,value] of [['reference-only',0],['model-only',1],['half-overlay',.5]]){node(id).onclick();assert.equal(node('model-image').style.opacity,value);}
node('model-opacity').value='73';node('model-opacity').events.input();assert.equal(node('model-image').style.opacity,.73);
assert(html.includes('#model-image{opacity:.5;background:#000}'),'Model-only image must have an opaque backing.');
assert(parentMessages.some(m=>m.channel==='listaunton-review'&&m.event==='viewer-ready'));
node('neutral').onclick();flush();assert.equal(uniforms.uUseWood,0);
windowListeners.message({source:{},data:{channel:'listaunton-review',action:'activate',material:'brown'}});flush();assert.notEqual(node('brown').attrs['aria-pressed'],'true');
node('brown').onclick();flush();assert.equal(uniforms.uUseWood,1);
const beforeSide=JSON.stringify([uniforms.uRotation,uniforms.uPan,uniforms.uProjection]);
node('side-tab').onclick();flush();assert.equal(node('stage').dataset.mode,'side');assert(!node('side-controls').hidden);assert(node('comparison-controls').hidden);
for(const [id,amount] of [['side-guide-only',0],['side-model-only',1],['side-half',.5]]){node(id).onclick();assert.equal(node('side-model').style.opacity,amount);}
const sr=JSON.parse(text('side-registration'));assert.equal(sr.source_blend_sha256,meta.sourceSha256);
const sidePng=fs.readFileSync(path.join(root,sr.profile));
assert.deepEqual(sr.profile_dimensions,[sidePng.readUInt32BE(16),sidePng.readUInt32BE(20)]);
assert.equal(parseFloat(node('side-model').style.width),sr.profile_dimensions[0]*sr.scale/sr.canvas[0]*100);
assert.equal(parseFloat(node('side-model').style.height),sr.profile_dimensions[1]*sr.scale/sr.canvas[1]*100);
node('rotate-tab').onclick();flush();assert.equal(JSON.stringify([uniforms.uRotation,uniforms.uPan,uniforms.uProjection]),beforeSide,'Side comparison changed orbit');
console.log(JSON.stringify({passed:true,pigmentAtlasHashMatches:true,varnishAtlasChecked:!!meta.varnish,slopeAtlasChecked:!!meta.slope,woodAndClayToggle:true,sideComparisonAndFootRegistration:true,sampledVertices:points.length,maxCameraErrorPixels:maxError,overlayEndpoints:true,tabOrbitPersistence:true,rotationPanZoom:true,cameraReset:true,sourceSha256:meta.sourceSha256},null,2));
