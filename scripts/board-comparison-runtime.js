(()=>{'use strict';
const byId=id=>document.getElementById(id);
const board=JSON.parse(byId('board-data').textContent);
const scaleData=JSON.parse(byId('side-scale-data').textContent);
const rows=Object.fromEntries(scaleData.pieces.map(item=>[item.piece,item]));
const layer=byId('board-model-layer'),pieces=byId('board-pieces'),shadows=byId('board-shadows');
const stage=byId('board-stage'),wipe=byId('board-wipe'),divider=byId('board-divider');
const elements={};let drag=null,heightMode='matched';
for(const item of board.pieces){
 const shadow=document.createElement('div');shadow.className='board-shadow';shadows.append(shadow);
 const img=document.createElement('img');img.src=item.file+'?v='+item.version;img.alt='';img.draggable=false;pieces.append(img);
 elements[item.piece]={img,shadow};
}
function layout(){
 const king=rows.king.height*Number(byId('side-scale-king').value);
 const modelHeights={};
 for(const item of board.pieces){
  const ratio=rows[item.piece].height*Number(byId('side-scale-'+item.piece).value)/king;
  let imageScale,groundY,top;
  if(heightMode==='matched'){
   // Fit the visible top and bottom of each render to the original screenshot.
   imageScale=(item.targetBottom-item.targetTop)/(item.renderBottom-item.renderTop);
   top=item.targetTop-item.renderTop*imageScale;
   groundY=top+item.footY*imageScale;
  }else{
   // Keep the owner's chosen relative heights and the common king-base scale.
   const modelScale=board.kingHeight*ratio/item.modelHeight;
   imageScale=board.kingPixelsPerUnit*modelScale/item.pixelsPerUnit;
   groundY=board.groundY;top=groundY-item.footY*imageScale;
  }
  const pixelsPerUnit=imageScale*item.pixelsPerUnit;
  modelHeights[item.piece]=pixelsPerUnit*item.modelHeight;
  const {img,shadow}=elements[item.piece];
  img.style.width=(item.width*imageScale/board.width*100)+'%';
  img.style.left=((item.centerX-item.footX*imageScale)/board.width*100)+'%';
  img.style.top=(top/board.height*100)+'%';
  const width=item.baseWidth*pixelsPerUnit*1.20,height=width*.72;
  shadow.style.width=(width/board.width*100)+'%';shadow.style.height=(height/board.height*100)+'%';
  shadow.style.left=((item.centerX-width/2-2)/board.width*100)+'%';
  shadow.style.top=((groundY-height/2+3)/board.height*100)+'%';
 }
 const labels={king:'K',queen:'Q',bishop:'B',knight:'N',rook:'R',pawn:'P'};
 byId('board-height-summary').textContent='Approx. model heights vs king: '+board.pieces.map(item=>labels[item.piece]+' '+(100*modelHeights[item.piece]/modelHeights.king).toFixed(1)+'%').join(' · ');
}
function setHeightMode(mode){
 heightMode=mode;
 byId('board-height-matched').setAttribute('aria-pressed',String(mode==='matched'));
 byId('board-height-chosen').setAttribute('aria-pressed',String(mode==='chosen'));
 byId('board-fit-note').textContent=mode==='matched'?"Matched to each visible top and foot. The original king's cross is clipped. Shadows approximated.":'Chosen side-view heights; king base aligned to the original. Shadows approximated.';
 layout();
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
byId('board-height-matched').addEventListener('click',()=>setHeightMode('matched'));
byId('board-height-chosen').addEventListener('click',()=>setHeightMode('chosen'));
setHeightMode('matched');paint();
})();
