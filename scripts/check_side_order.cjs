const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync(process.argv[2],'utf8');
const data=JSON.parse(html.match(/<script id="side-scale-data"[^>]*>(.*?)<\/script>/s)[1]);
const script=id=>html.match(new RegExp('<script id="'+id+'">([\\s\\S]*?)<\\/script>'))[1];
const defaults=data.defaultOrder,orderKey='listaunton.side-view-order.'+data.defaultsRevision;

function fixture(saved=new Map(),blocked=false){
 let focused=null,nextFrame=0;const frames=new Map(),els={},docEvents={},winEvents={};
 class Element{
  constructor(id){this.id=id;this.children=[];this.parentNode=null;this.style={};this.attrs={};this.events={};this.value='';this.disabled=false;this.textContent='';this.captures=new Set();
   const classes=new Set();this.classList={add:(...a)=>a.forEach(v=>classes.add(v)),remove:(...a)=>a.forEach(v=>classes.delete(v)),contains:v=>classes.has(v)};
  }
  appendChild(child){if(child.parentNode){const siblings=child.parentNode.children;siblings.splice(siblings.indexOf(child),1);}this.children.push(child);child.parentNode=this;return child;}
  addEventListener(type,fn){(this.events[type]??=[]).push(fn);}
  setAttribute(key,value){this.attrs[key]=value;}
  focus(){focused=this;}
  setPointerCapture(id){this.captures.add(id);}
  hasPointerCapture(id){return this.captures.has(id);}
  releasePointerCapture(id){this.captures.delete(id);this.fire('lostpointercapture',{pointerId:id});}
  fire(type,values={}){const event={target:this,currentTarget:this,preventDefault(){this.prevented=true;},...values};for(const fn of this.events[type]||[])fn(event);return event;}
  getBoundingClientRect(){
   if(this.id==='side-scroll')return {left:100,right:100+this.clientWidth,width:this.clientWidth,top:80};
   const index=els['side-lineup'].children.indexOf(this),delta=Number((this.style.transform||'').match(/translateX\(([-.\d]+)px\)/)?.[1]||0);
   const left=100+index*332-els['side-scroll'].scrollLeft+delta;
   return {left,right:left+320,width:320,top:80};
  }
 }
 for(const match of html.matchAll(/\bid="([^"]+)"/g))els[match[1]]=new Element(match[1]);
 els['side-scale-data'].textContent=JSON.stringify(data);
 const lineup=els['side-lineup'],scroller=els['side-scroll'];scroller.scrollLeft=0;scroller.scrollWidth=1980;scroller.clientWidth=2200;
 for(const piece of defaults){
  const card=els['side-card-'+piece];lineup.appendChild(card);
  for(const prefix of ['side-left-','side-right-','side-drag-','side-scale-','side-reset-','side-scale-value-','side-ratio-'])card.appendChild(els[prefix+piece]);
  els['side-drag-'+piece].appendChild(els['side-picture-'+piece]);
 }
 const storage={getItem:key=>{if(blocked)throw Error('blocked');return saved.get(key)||null;},setItem:(key,value)=>{if(blocked)throw Error('blocked');saved.set(key,value);}};
 const window={localStorage:storage,addEventListener:(type,fn)=>(winEvents[type]??=[]).push(fn),
  requestAnimationFrame:fn=>{frames.set(++nextFrame,fn);return nextFrame;},cancelAnimationFrame:id=>frames.delete(id)};
 const document={getElementById:id=>els[id],addEventListener:(type,fn)=>(docEvents[type]??=[]).push(fn)};
 vm.runInNewContext(script('side-scales-runtime'),{document,window});
 vm.runInNewContext(script('side-order-runtime'),{document,window});
 return {els,saved,scroller,frames,
  order:()=>lineup.children.map(el=>el.id.replace('side-card-','')),
  emitDoc:(type,event)=>{for(const fn of docEvents[type]||[])fn({preventDefault(){},...event});},
  emitWindow:type=>{for(const fn of winEvents[type]||[])fn();},
  tick:count=>{for(let i=0;i<count;i++){const scheduled=[...frames];frames.clear();for(const [,fn] of scheduled)fn();}},
  focus:()=>focused,
 };
}
const pointer=(x,y=200)=>({pointerId:1,button:0,isPrimary:true,clientX:x,clientY:y});
function resize(f,piece,value){const el=f.els['side-scale-'+piece];el.value=String(value);el.fire('input');}
function drag(f,piece,x){const el=f.els['side-drag-'+piece],box=f.els['side-card-'+piece].getBoundingClientRect();el.fire('pointerdown',pointer(box.left+160));el.fire('pointermove',pointer(x));return el;}
function noDrag(f){assert.equal(f.frames.size,0);for(const piece of defaults){assert(!f.els['side-card-'+piece].classList.contains('is-dragging'));assert(!f.els['side-card-'+piece].style.transform);}}

let f=fixture();assert.deepEqual(f.order(),defaults);
resize(f,'king',120);resize(f,'rook',137);
const rookImage=f.els['side-picture-rook'],rookInput=f.els['side-scale-rook'];
f.els['side-right-king'].fire('click');assert.deepEqual(f.order(),['queen','king','bishop','knight','rook','pawn']);
f.els['side-drag-pawn'].fire('keydown',{key:'Home'});assert.deepEqual(f.order(),['pawn','queen','king','bishop','knight','rook']);
assert(f.els['side-left-pawn'].disabled);assert(f.els['side-right-rook'].disabled);
assert.equal(f.els['side-picture-rook'],rookImage);assert.equal(rookImage.style.transform,'scale(1.37)');assert.equal(f.els['side-scale-rook'],rookInput);
f.els['side-reset-order'].fire('click');assert.deepEqual(f.order(),defaults);assert.equal(rookInput.value,'137');assert.equal(f.els['side-scale-king'].value,'120');

const surface=drag(f,'rook',1100);assert.deepEqual(f.order(),defaults,'Drag must not rebuild the row before drop');
assert(f.els['side-card-rook'].style.transform.startsWith('translateX('));
assert(f.els['side-card-knight'].classList.contains('drop-before'));
assert.equal(f.els['side-card-rook'].getBoundingClientRect().top,80,'Horizontal drag must preserve the baseline');
surface.fire('pointerup',pointer(1100));assert.deepEqual(f.order(),['king','queen','bishop','rook','knight','pawn']);noDrag(f);
assert.equal(rookImage.style.transform,'scale(1.37)');assert.equal(f.focus(),surface);
let restored=fixture(f.saved);assert.deepEqual(restored.order(),f.order());assert.equal(restored.els['side-scale-rook'].value,'137');

for(const cancel of ['escape','pointercancel','lostpointercapture','tab','blur']){
 const before=f.order();const s=drag(f,'rook',260);
 if(cancel==='escape')f.emitDoc('keydown',{key:'Escape'});
 else if(cancel==='tab')f.els['tab-comparison'].fire('click');
 else if(cancel==='blur')f.emitWindow('blur');
 else s.fire(cancel,{pointerId:1});
 assert.deepEqual(f.order(),before,cancel+' must abandon reorder');noDrag(f);
}
f.els['side-scale-rook'].fire('pointerdown',pointer(260));resize(f,'rook',118);noDrag(f);assert.equal(f.els['side-picture-rook'].style.transform,'scale(1.18)');

// A short horizontal move is a click; a vertical gesture remains available for scrolling.
const still=f.order(),s=f.els['side-drag-rook'];s.fire('pointerdown',pointer(200));s.fire('pointermove',pointer(204,240));s.fire('pointerup',pointer(204,240));assert.deepEqual(f.order(),still);noDrag(f);

// Captured drag scrolls to reach the far end without moving the foot vertically.
f=fixture();f.scroller.clientWidth=720;
const edge=drag(f,'king',810);f.tick(100);assert(f.scroller.scrollLeft>1000);
assert.equal(f.els['side-card-king'].getBoundingClientRect().top,80);
edge.fire('pointerup',pointer(810));assert.equal(f.order().at(-1),'king');noDrag(f);
f.els['side-drag-king'].fire('keydown',{key:'Home'});assert.equal(f.order()[0],'king');assert.equal(f.scroller.scrollLeft,0,'Keyboard reordering reveals its new position without vertical scroll');

const bad=new Map([[orderKey,'["king","king","rook","bishop","knight","pawn"]']]);assert.deepEqual(fixture(bad).order(),defaults);
assert.deepEqual(fixture(new Map([[orderKey,'broken json']])).order(),defaults);
f=fixture(new Map(),true);f.els['side-right-king'].fire('click');assert.equal(f.order()[1],'king');
console.log('PASS: drag insertion, arrows/keyboard, horizontal-only motion, saved order, scale/DOM preservation, cancellation, edge scrolling and invalid/blocked storage.');

const legacy=new Map([['listaunton.side-view-order.v1',JSON.stringify([...defaults].reverse())],['listaunton.side-view-scales.v1',JSON.stringify({king:150,pawn:50})]]);
const upgraded=fixture(legacy);assert.deepEqual(upgraded.order(),defaults);assert.equal(upgraded.els['side-scale-king'].value,'99');assert.equal(upgraded.els['side-scale-pawn'].value,'97');
assert(legacy.has('listaunton.side-view-order.v1'),'Old preferences need not be deleted to apply a new default revision');
console.log('PASS: new default revision applies the chosen arrangement without stale settings overriding it.');
