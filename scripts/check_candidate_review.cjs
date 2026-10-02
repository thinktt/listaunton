// Exercise the shared browser runtime, including async image loading and every source pair.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),source=fs.readFileSync(path.join(root,'assets/comparison/candidate-review.js'),'utf8');
const settle=()=>new Promise(resolve=>setImmediate(resolve));
async function check(piece){
 const html=fs.readFileSync(path.join(root,piece+'-review.html'),'utf8');
 const data=JSON.parse(html.match(/<script id="comparison-data"[^>]*>(.*?)<\/script>/s)[1]);
 assert.equal(data.images.length,8);
 for(const color of ['Black','White'])assert.equal(data.images.filter(item=>item.label.startsWith(color+' candidate')).length,3);
 const nodes=new Map(),failed=new Set();let errors=0;
 function node(id){if(!nodes.has(id))nodes.set(id,{id,style:{},attrs:{},listeners:{},value:'',checked:false,hidden:false,clientWidth:900,clientHeight:700,scrollLeft:0,scrollTop:0,offsetLeft:0,offsetTop:0,decode:()=>Promise.resolve(),setPointerCapture(){},focus(){},getBoundingClientRect(){return {left:-100,width:1000};},setAttribute(k,v){this.attrs[k]=v;},addEventListener(k,fn){this.listeners[k]=fn;},fire(k,event={}){return this.listeners[k]?.({target:this,preventDefault(){},stopPropagation(){},...event});}});return nodes.get(id);}
 const zooms=['fit','1','2'].map(value=>Object.assign(node('zoom-'+value),{dataset:{zoom:value}}));
 node('comparison-data').textContent=JSON.stringify(data);node('image-a').value='black';node('image-b').value='candidate-1';node('align').checked=true;node('mix').value='50';
 const doc={getElementById:node,querySelectorAll:()=>zooms,documentElement:{style:{setProperty(){}}}};
 class FakeImage{set src(value){queueMicrotask(()=>failed.has(value)?this.onerror():this.onload());}}
 vm.runInNewContext(source,{document:doc,window:{addEventListener(){}},ResizeObserver:class{observe(){}},Image:FakeImage,console:{error(){errors++;}},Map,Promise,JSON,Number,String,Math});
 await settle();
 assert.equal(node('stage').style.visibility,'visible');assert.equal(node('loading').hidden,true);
 assert.equal(node('wipe').attrs['aria-pressed'],'true');assert.equal(node('layer-b').style.clipPath,'inset(0 50% 0 0)');
 const h=node('wipe-handle');assert.equal(h.hidden,false);
 node('viewport').scrollLeft=70;node('viewport').scrollTop=80;
 h.fire('pointerdown',{button:0,pointerId:7,clientX:400});h.fire('pointermove',{pointerId:7,clientX:650});
 assert.equal(node('mix').value,'75');assert.equal(h.attrs['aria-valuenow'],'75');assert.equal(node('layer-b').style.clipPath,'inset(0 25% 0 0)');
 assert.equal(node('viewport').scrollLeft,70);assert.equal(node('viewport').scrollTop,80);
 h.fire('pointermove',{pointerId:8,clientX:200});assert.equal(node('mix').value,'75');
 h.fire('pointermove',{pointerId:7,clientX:1500});assert.equal(node('mix').value,'100');assert.equal(h.hidden,false);
 h.fire('pointermove',{pointerId:7,clientX:-500});assert.equal(node('mix').value,'0');assert.equal(h.hidden,false);
 h.fire('pointercancel',{pointerId:7});h.fire('pointermove',{pointerId:7,clientX:650});assert.equal(node('mix').value,'0');
 h.fire('keydown',{key:'ArrowRight',shiftKey:true});assert.equal(node('mix').value,'10');h.fire('keydown',{key:'End'});assert.equal(node('mix').value,'100');h.fire('keydown',{key:'Home'});assert.equal(node('mix').value,'0');
 node('blend').fire('click');assert.equal(h.hidden,true);

 for(const a of data.images)for(const b of data.images){
   node('image-a').value=a.id;node('image-b').value=b.id;node('image-b').fire('change');await settle();
   assert.equal(node('photo-a').src,a.file);assert.equal(node('photo-b').src,b.file);
   assert.equal(node('photo-a').style.transform,a.flip?'scaleX(-1)':'none');assert.equal(node('photo-b').style.transform,b.flip?'scaleX(-1)':'none');
   if(piece==='king')for(const id of ['photo-a','photo-b']){const style=node(id).style;assert(parseFloat(style.top)>=3,'King needs top headroom');assert(parseFloat(style.left)>=0);assert(parseFloat(style.top)+parseFloat(style.height)<=100);assert(parseFloat(style.left)+parseFloat(style.width)<=100);}
   assert.equal(node('download-a').href,a.file);assert.equal(node('download-b').href,b.file);
   node('only-a').fire('click');assert.equal(node('layer-b').style.opacity,'0');
   node('only-b').fire('click');assert.equal(node('layer-b').style.opacity,'1');
   node('half').fire('click');assert.equal(node('layer-b').style.opacity,'0.5');
 }
 node('wipe').fire('click');node('mix').value='25';node('mix').fire('input');
 assert.equal(node('layer-b').style.clipPath,'inset(0 75% 0 0)');assert.equal(node('divider').hidden,false);
 node('only-a').fire('click');assert.equal(node('layer-b').style.clipPath,'inset(0 100% 0 0)');assert.equal(node('divider').hidden,true);
 node('only-b').fire('click');assert.equal(node('layer-b').style.clipPath,'inset(0 0% 0 0)');
 node('blend').fire('click');assert.equal(node('layer-b').style.clipPath,'none');
 node('image-a').value='black';node('image-b').value='white';node('image-b').fire('change');await settle();
 assert.equal(node('photo-b').style.transform,piece==='knight'?'scaleX(-1)':'none');
 node('align').checked=false;node('align').fire('change');assert.equal(node('photo-b').style.transform,'none');assert.equal(node('photo-b').style.width,piece==='king'?'90%':'100%');
 node('mix').value='20';node('swap').fire('click');await settle();assert.equal(node('image-a').value,'white');assert.equal(node('image-b').value,'black');assert.equal(node('mix').value,'80');
 node('zoom-2').fire('click');assert.equal(node('stage').style.width,'2508px');
 node('viewport').scrollLeft=100;node('viewport').scrollTop=120;
 node('viewport').fire('pointerdown',{button:0,pointerId:1,clientX:100,clientY:100});node('viewport').fire('pointermove',{pointerId:1,clientX:140,clientY:120});node('viewport').fire('pointerup');
 assert.equal(node('viewport').scrollLeft,60);assert.equal(node('viewport').scrollTop,100);
 node('image-b').value='candidate-1';node('image-b').fire('change');node('image-b').value='candidate-3';node('image-b').fire('change');await settle();
 assert.equal(node('photo-b').src,data.images.find(x=>x.id==='candidate-3').file);assert.equal(node('viewport').scrollLeft,60);assert.equal(node('stage').style.width,'2508px');
 assert.equal(errors,0);
 console.log('PASS: '+piece+' — 64 source pairs, default wipe, draggable/keyboard divider, loading, blend/wipe endpoints, swap, alignment, downloads, pan/zoom and rapid switching.');
}
(async()=>{for(const piece of ['king','rook','bishop','knight','pawn'])await check(piece);})().catch(error=>{console.error(error);process.exitCode=1;});
