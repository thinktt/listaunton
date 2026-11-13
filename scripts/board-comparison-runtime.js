(()=>{'use strict';
const byId=id=>document.getElementById(id);
const board=JSON.parse(byId('board-data').textContent);
const scaleData=JSON.parse(byId('side-scale-data').textContent);
const rows=Object.fromEntries(scaleData.pieces.map(item=>[item.piece,item]));
const layer=byId('board-model-layer'),pieces=byId('board-pieces'),shadows=byId('board-shadows');
const stage=byId('board-stage'),wipe=byId('board-wipe'),divider=byId('board-divider');
const elements={};let drag=null;
for(const item of board.pieces){
 const shadow=document.createElement('div');shadow.className='board-shadow';shadows.append(shadow);
 const img=document.createElement('img');img.src=item.file+'?v='+item.version;img.alt='';img.draggable=false;pieces.append(img);
 elements[item.piece]={img,shadow};
}
function layout(){
 const king=rows.king.height*Number(byId('side-scale-king').value);
 for(const item of board.pieces){
  const ratio=rows[item.piece].height*Number(byId('side-scale-'+item.piece).value)/king;
  // One uniform scale per model: its requested height relative to the king,
  // calibrated once from the king's base width in the original screenshot.
  const modelScale=board.kingHeight*ratio/item.modelHeight;
  const pixelsPerUnit=board.kingPixelsPerUnit*modelScale;
  const imageScale=pixelsPerUnit/item.pixelsPerUnit;
  const {img,shadow}=elements[item.piece];
  img.style.width=(item.width*imageScale/board.width*100)+'%';
  img.style.left=((item.centerX-item.footX*imageScale)/board.width*100)+'%';
  img.style.top=((board.groundY-item.footY*imageScale)/board.height*100)+'%';
  const width=item.baseWidth*pixelsPerUnit*1.20,height=width*.72;
  shadow.style.width=(width/board.width*100)+'%';shadow.style.height=(height/board.height*100)+'%';
  shadow.style.left=((item.centerX-width/2-2)/board.width*100)+'%';
  shadow.style.top=((board.groundY-height/2+3)/board.height*100)+'%';
 }
}
function paint(){
 const value=Math.max(0,Math.min(100,Number(wipe.value)||0));
 wipe.value=String(value);wipe.setAttribute('aria-valuetext',value+'% models, '+(100-value)+'% original');
 layer.style.clipPath='inset(0 '+(100-value)+'% 0 0)';
 divider.style.left=value+'%';divider.hidden=value===0||value===100;
 byId('board-status').textContent=value+'% models, '+(100-value)+'% original';
 for(const [id,point] of [['board-original',0],['board-half',50],['board-models',100]])byId(id).setAttribute('aria-pressed',String(value===point));
}
function move(clientX){const rect=stage.getBoundingClientRect();if(rect.width)wipe.value=String(Math.round(Math.max(0,Math.min(1,(clientX-rect.left)/rect.width))*100));paint();}
wipe.addEventListener('input',paint);
for(const [id,point] of [['board-original',0],['board-half',50],['board-models',100]])byId(id).addEventListener('click',()=>{wipe.value=String(point);paint();});
stage.addEventListener('pointerdown',event=>{
 if(event.isPrimary===false||event.button!==0)return;
 drag=event.pointerId;stage.setPointerCapture(event.pointerId);move(event.clientX);event.preventDefault();
});
stage.addEventListener('pointermove',event=>{if(drag===event.pointerId){move(event.clientX);event.preventDefault();}});
for(const type of ['pointerup','pointercancel','lostpointercapture'])stage.addEventListener(type,event=>{if(drag===event.pointerId)drag=null;});
for(const item of board.pieces){
 byId('side-scale-'+item.piece).addEventListener('input',layout);
 byId('side-reset-'+item.piece).addEventListener('click',layout);
}
layout();paint();
})();
