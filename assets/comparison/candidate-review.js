(() => {
  'use strict';
  const $=id=>document.getElementById(id),data=JSON.parse($('comparison-data').textContent);
  const items=new Map(data.images.map(item=>[item.id,item]));
  const a=$('image-a'),b=$('image-b'),viewport=$('viewport'),stage=$('stage'),slider=$('mix');
  const imageA=$('photo-a'),imageB=$('photo-b'),layerB=$('layer-b'),divider=$('divider');
  let mode='wipe',zoom='fit',scale=1,drag=null,wipeDrag=null,version=0,ready=false;
  const handle=$('wipe-handle');
  const cache=new Map();
  function load(src){
    if(!cache.has(src))cache.set(src,new Promise((resolve,reject)=>{
      const image=new Image();image.onload=()=>resolve(image);image.onerror=()=>{cache.delete(src);reject(new Error('Could not load '+src));};image.src=src;
    }));
    return cache.get(src);
  }
  function place(image,item){
    const aligned=$('align').checked,s=aligned?item.scale:1;
    // A shared inset keeps the entire aligned king visible without changing relative geometry.
    const padding=data.viewPadding||0,frameScale=1-padding/50;
    image.style.width=s*frameScale*100+'%';image.style.height=s*frameScale*100+'%';
    image.style.left=(padding+(aligned?item.x:0)*frameScale)+'%';image.style.top=(padding+(aligned?item.y:0)*frameScale)+'%';
    image.style.transform=aligned&&item.flip?'scaleX(-1)':'none';
  }
  function positionHandle(){
    const height=1254*scale;
    handle.style.top=Math.max(22,Math.min(height-22,viewport.scrollTop+viewport.clientHeight/2-stage.offsetTop))+'px';
  }
  function paint(){
    const value=Number(slider.value),wipe=mode==='wipe';
    layerB.style.opacity=wipe?'1':String(value/100);
    layerB.style.clipPath=wipe?`inset(0 ${100-value}% 0 0)`:'none';
    divider.hidden=!wipe||value===0||value===100;divider.style.left=value+'%';
    handle.hidden=!wipe;handle.style.left=`clamp(22px, ${value}%, calc(100% - 22px))`;
    handle.setAttribute('aria-valuenow',String(value));handle.setAttribute('aria-valuetext',value+'% image B');
    positionHandle();
    $('mix-value').textContent=value+'% B';
    $('mix-label').textContent=wipe?'Wipe':'Blend';
    $('blend').setAttribute('aria-pressed',String(!wipe));$('wipe').setAttribute('aria-pressed',String(wipe));
    const ia=items.get(a.value),ib=items.get(b.value);
    place(imageA,ia);place(imageB,ib);
    $('status').textContent=`A: ${ia.label} · B: ${ib.label}`;
    $('alignment-status').textContent=$('align').checked?(ia.flip||ib.flip?'Aligned · white knight mirrored':'Aligned · uniform scale and position'):'Original framing';
    $('download-a').href=ia.file;$('download-b').href=ib.file;
  }
  async function pair(){
    wipeDrag=null;
    const request=++version,ia=items.get(a.value),ib=items.get(b.value);
    ready=false;stage.style.visibility='hidden';$('loading').hidden=false;$('loading').textContent='Loading images…';
    paint();
    try{
      await Promise.all([load(ia.file),load(ib.file)]);
      if(request!==version)return;
      imageA.src=ia.file;imageA.alt=data.piece+' — '+ia.label;imageB.src=ib.file;imageB.alt=data.piece+' — '+ib.label;
      await Promise.all([imageA.decode?.(),imageB.decode?.()]);
      if(request!==version)return;
      ready=true;paint();stage.style.visibility='visible';$('loading').hidden=true;
    }catch(error){if(request===version){$('loading').textContent='Image unavailable. Choose another image or reload the page.';console.error(error);}}
  }
  function resize(next,keepCenter=true){
    const cx=(viewport.scrollLeft+viewport.clientWidth/2-stage.offsetLeft)/scale;
    const cy=(viewport.scrollTop+viewport.clientHeight/2-stage.offsetTop)/scale;
    zoom=next;scale=next==='fit'?Math.min(viewport.clientWidth,viewport.clientHeight)/1254:Number(next);
    stage.style.width=1254*scale+'px';stage.style.height=1254*scale+'px';
    if(keepCenter&&next!=='fit'){viewport.scrollLeft=cx*scale+stage.offsetLeft-viewport.clientWidth/2;viewport.scrollTop=cy*scale+stage.offsetTop-viewport.clientHeight/2;}
    else{viewport.scrollLeft=0;viewport.scrollTop=0;}
    positionHandle();
    document.querySelectorAll('[data-zoom]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.zoom===zoom)));
  }
  a.addEventListener('change',pair);b.addEventListener('change',pair);
  slider.addEventListener('input',paint);$('align').addEventListener('change',paint);
  for(const value of ['blend','wipe'])$(value).addEventListener('click',()=>{mode=value;wipeDrag=null;paint();});
  for(const [id,value] of [['only-a',0],['half',50],['only-b',100]])$(id).addEventListener('click',()=>{slider.value=String(value);paint();});
  $('swap').addEventListener('click',()=>{const old=a.value;a.value=b.value;b.value=old;slider.value=String(100-Number(slider.value));pair();});
  $('background').addEventListener('change',()=>document.documentElement.style.setProperty('--canvas',$('background').value));
  document.querySelectorAll('[data-zoom]').forEach(button=>button.addEventListener('click',()=>resize(button.dataset.zoom)));
  handle.addEventListener('pointerdown',event=>{
    if(!ready||mode!=='wipe'||event.button!==0)return;
    event.preventDefault();event.stopPropagation();drag=null;
    handle.focus({preventScroll:true});handle.setPointerCapture(event.pointerId);
    const rect=stage.getBoundingClientRect();
    wipeDrag={id:event.pointerId,offset:event.clientX-rect.left-Number(slider.value)/100*rect.width};
  });
  handle.addEventListener('pointermove',event=>{
    if(!wipeDrag||event.pointerId!==wipeDrag.id)return;
    event.preventDefault();event.stopPropagation();
    const rect=stage.getBoundingClientRect();
    slider.value=String(Math.round(Math.max(0,Math.min(100,(event.clientX-rect.left-wipeDrag.offset)/rect.width*100))));
    paint();
  });
  const endWipe=event=>{if(wipeDrag&&event.pointerId===wipeDrag.id)wipeDrag=null;};
  for(const type of ['pointerup','pointercancel','lostpointercapture'])handle.addEventListener(type,endWipe);
  handle.addEventListener('keydown',event=>{
    const step=event.shiftKey?10:1,value=Number(slider.value);
    const next={ArrowLeft:value-step,ArrowDown:value-step,ArrowRight:value+step,ArrowUp:value+step,Home:0,End:100}[event.key];
    if(next===undefined)return;
    event.preventDefault();event.stopPropagation();slider.value=String(Math.max(0,Math.min(100,next)));paint();
  });
  viewport.addEventListener('scroll',positionHandle);
  viewport.addEventListener('pointerdown',event=>{
    if(!ready||wipeDrag||event.button!==0)return;
    event.preventDefault();viewport.setPointerCapture(event.pointerId);
    drag={id:event.pointerId,x:event.clientX,y:event.clientY,left:viewport.scrollLeft,top:viewport.scrollTop};
  });
  viewport.addEventListener('pointermove',event=>{
    if(!drag||event.pointerId!==drag.id)return;
    viewport.scrollLeft=drag.left-event.clientX+drag.x;viewport.scrollTop=drag.top-event.clientY+drag.y;
  });
  for(const type of ['pointerup','pointercancel','lostpointercapture'])viewport.addEventListener(type,()=>{drag=null;});
  window.addEventListener('blur',()=>{drag=null;wipeDrag=null;});
  new ResizeObserver(()=>{if(zoom==='fit')resize('fit',false);}).observe(viewport);
  resize('fit',false);pair();
})();
