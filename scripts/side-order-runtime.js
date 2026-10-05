// Included inline by the set-page builder so the gallery also works from file://.
(()=>{'use strict';
const byId=id=>document.getElementById(id),data=JSON.parse(byId('side-scale-data').textContent);
const defaults=data.pieces.map(item=>item.piece),names=Object.fromEntries(data.pieces.map(item=>[item.piece,item.name]));
const lineup=byId('side-lineup'),scroller=byId('side-scroll'),key='listaunton.side-view-order.v1';
const cards=Object.fromEntries(defaults.map(piece=>[piece,byId('side-card-'+piece)]));
let order=[...defaults],drag=null,frame=0;
try{const saved=JSON.parse(window.localStorage.getItem(key)||'null');
 if(Array.isArray(saved)&&saved.length===defaults.length&&new Set(saved).size===defaults.length&&saved.every(piece=>defaults.includes(piece)))order=saved;
}catch{}

function paint(){
 // Move existing nodes: image scale, input state and event handlers stay intact.
 for(const [index,piece] of order.entries()){
  lineup.appendChild(cards[piece]);
  byId('side-left-'+piece).disabled=index===0;
  byId('side-right-'+piece).disabled=index===order.length-1;
 }
}
function save(){try{window.localStorage.setItem(key,JSON.stringify(order));}catch{}}
function commit(next,piece){
 order=next;paint();save();
 if(piece){
  byId('side-order-status').textContent=names[piece]+' moved to position '+(order.indexOf(piece)+1)+' of '+order.length+'.';
  const box=cards[piece].getBoundingClientRect(),view=scroller.getBoundingClientRect();
  const shift=box.left<view.left?box.left-view.left:box.right>view.right?box.right-view.right:0;
  scroller.scrollLeft=Math.max(0,Math.min(scroller.scrollWidth-scroller.clientWidth,scroller.scrollLeft+shift));
  byId('side-drag-'+piece).focus({preventScroll:true});
 }
}
function move(piece,index){
 if(drag)finish(true);
 const at=Math.max(0,Math.min(order.length-1,index));
 if(order.indexOf(piece)===at)return;
 const next=order.filter(item=>item!==piece);next.splice(at,0,piece);commit(next,piece);
}
function clearMarkers(){for(const card of Object.values(cards)){card.classList.remove('drop-before','drop-after');}}
function updateDrag(){
 if(!drag||!drag.active)return;
 const card=cards[drag.piece],slotLeft=card.getBoundingClientRect().left-drag.translation;
 drag.translation=drag.startLeft+drag.x-drag.startX-slotLeft;
 card.style.transform='translateX('+drag.translation+'px)';
 const remaining=order.filter(piece=>piece!==drag.piece);
 let at=remaining.findIndex(piece=>{const box=cards[piece].getBoundingClientRect();return drag.x<box.left+box.width/2;});
 if(at<0)at=remaining.length;
 drag.proposal=[...remaining];drag.proposal.splice(at,0,drag.piece);
 clearMarkers();
 if(drag.proposal.join(',')!==order.join(',')){
  if(at<remaining.length)cards[remaining[at]].classList.add('drop-before');
  else cards[remaining[remaining.length-1]].classList.add('drop-after');
 }
}
function scrollTick(){
 frame=0;if(!drag||!drag.active)return;
 const box=scroller.getBoundingClientRect(),edge=56;
 let speed=0;
 if(drag.x<box.left+edge)speed=-Math.min(18,(box.left+edge-drag.x)/3);
 else if(drag.x>box.right-edge)speed=Math.min(18,(drag.x-box.right+edge)/3);
 if(speed){
  const old=scroller.scrollLeft,max=Math.max(0,scroller.scrollWidth-scroller.clientWidth);
  scroller.scrollLeft=Math.max(0,Math.min(max,old+speed));
  if(scroller.scrollLeft!==old)updateDrag();
 }
 frame=window.requestAnimationFrame(scrollTick);
}
function finish(cancelled){
 if(!drag)return;
 const ended=drag;drag=null;
 if(frame){window.cancelAnimationFrame(frame);frame=0;}
 cards[ended.piece].style.transform='';cards[ended.piece].classList.remove('is-dragging');
 scroller.classList.remove('is-reordering');clearMarkers();
 if(ended.surface.hasPointerCapture(ended.pointerId))ended.surface.releasePointerCapture(ended.pointerId);
 if(ended.active&&!cancelled)commit(ended.proposal,ended.piece);
}
for(const piece of defaults){
 const surface=byId('side-drag-'+piece);
 byId('side-left-'+piece).addEventListener('click',()=>move(piece,order.indexOf(piece)-1));
 byId('side-right-'+piece).addEventListener('click',()=>move(piece,order.indexOf(piece)+1));
 surface.addEventListener('keydown',event=>{
  let target;
  if(event.key==='ArrowLeft')target=order.indexOf(piece)-1;
  else if(event.key==='ArrowRight')target=order.indexOf(piece)+1;
  else if(event.key==='Home')target=0;
  else if(event.key==='End')target=order.length-1;
  else return;
  event.preventDefault();move(piece,target);
 });
 surface.addEventListener('pointerdown',event=>{
  if(drag||event.isPrimary===false||event.button!==0)return;
  drag={piece,surface,pointerId:event.pointerId,startX:event.clientX,startY:event.clientY,
        x:event.clientX,startLeft:cards[piece].getBoundingClientRect().left,translation:0,
        active:false,proposal:[...order]};
  surface.setPointerCapture(event.pointerId);
 });
 surface.addEventListener('pointermove',event=>{
  if(!drag||drag.pointerId!==event.pointerId)return;
  drag.x=event.clientX;
  if(!drag.active){
   const dx=Math.abs(event.clientX-drag.startX),dy=Math.abs(event.clientY-drag.startY);
   if(dx<6||dx<dy)return;
   drag.active=true;cards[piece].classList.add('is-dragging');scroller.classList.add('is-reordering');
   frame=window.requestAnimationFrame(scrollTick);
  }
  event.preventDefault();updateDrag();
 });
 surface.addEventListener('pointerup',event=>{
  if(!drag||drag.pointerId!==event.pointerId)return;
  drag.x=event.clientX;updateDrag();finish(false);
 });
 surface.addEventListener('pointercancel',event=>{if(drag&&drag.pointerId===event.pointerId)finish(true);});
 surface.addEventListener('lostpointercapture',event=>{if(drag&&drag.pointerId===event.pointerId)finish(true);});
 surface.addEventListener('dragstart',event=>event.preventDefault());
}
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&drag){event.preventDefault();finish(true);}});
for(const id of ['tab-comparison','tab-side-views'])byId(id).addEventListener('click',()=>finish(true));
window.addEventListener('hashchange',()=>finish(true));
window.addEventListener('blur',()=>finish(true));
byId('side-reset-order').addEventListener('click',()=>{finish(true);commit([...defaults]);byId('side-order-status').textContent='Original piece order restored.';});
paint();
})();
