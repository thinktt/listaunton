(()=>{'use strict';
function registrations(board){
 const entries=board.pieces.map(item=>{
  // Reuse the physical scale at which an accepted modeling target was chosen.
  const ruler = item.warpRuler ?? item;
  const imageScale = (item.targetBottom - item.targetTop) / (ruler.renderBottom - ruler.renderTop);
  const pixels = imageScale * ruler.pixelsPerUnit;
  return [item.piece, {...item, pixels,
   ground: item.targetTop + (ruler.footY - ruler.renderTop) * imageScale,
   physicalHeight: pixels * item.modelHeight}];
 });
 const result=Object.fromEntries(entries);
 for(const item of Object.values(result))item.ratio=item.physicalHeight/result.king.physicalHeight;
 return result;
}
function guide(scales){
 const king=scales.pieces.find(item=>item.piece==='king');
 return Object.fromEntries(scales.pieces.map(item=>[item.piece,Math.round(1000*item.height*item.defaultScale/(king.height*king.defaultScale))/1000]));
}
function bounded(value,fallback,min,max){return typeof value==='number'&&Number.isFinite(value)?Math.max(min,Math.min(max,Math.round(value*10)/10)):fallback;}
const scaleRange = {min: 50, max: 150};
const unwarped = Object.freeze({height: 100, width: 100, scale: 100});

function effectiveWarp({height, width, scale = 100}) {
 const factor = scale / 100;
 return {height: height * factor, width: width * factor};
}

function preset(name,records,targets){
 const pieces = {};
 for (const piece of Object.keys(records)) {
  const shape = {...unwarped};
  if (name === 'chavet') shape.height = bounded(100 * targets[piece] / records[piece].ratio, 100, 50, 150);
  if (name === 'bishop' && piece === 'bishop') shape.height = 88;
  pieces[piece] = shape;
 }
 return pieces;
}
function restore(saved,records,targets){
 const state={angle:54,tilts:Object.fromEntries(Object.keys(records).map(piece=>[piece,null])),pieces:preset('unwarped',records,targets)};
 if(!saved||typeof saved!=='object'||Array.isArray(saved))return state;
 state.angle=bounded(saved.angle,54,20,80);
 for(const [piece,value] of Object.entries(state.pieces)){
  state.tilts[piece]=bounded(saved.tilts&&saved.tilts[piece],null,20,80);
  const item=saved.pieces&&saved.pieces[piece];if(!item||typeof item!=='object')continue;
  value.height=bounded(item.height,value.height,50,150);value.width=bounded(item.width,100,70,130);
  value.scale=bounded(item.scale,100,scaleRange.min,scaleRange.max);
 }
 return state;
}
function angleForPiece(state,piece){return bounded(state.tilts&&state.tilts[piece],state.angle,20,80);}
function setAllTilts(state,angle){
 state.angle=bounded(angle,state.angle,20,80);
 for(const piece of Object.keys(state.pieces))state.tilts[piece]=null;
}
function referenceBasis(meta,angle){
 const m=meta.referenceCamera.worldToCamera,d=(angle-(meta.referenceCamera.elevationDegrees||54))*Math.PI/180,c=Math.cos(d),s=Math.sin(d);
 return [m[0],m[1],m[2],c*m[4]-s*m[8],c*m[5]-s*m[9],c*m[6]-s*m[10],s*m[4]+c*m[8],s*m[5]+c*m[9],s*m[6]+c*m[10]];
}
function orbitBasis(yaw,pitch){const c=Math.cos(yaw),s=Math.sin(yaw),a=Math.cos(pitch),b=Math.sin(pitch);return [c,-s,0,b*s,b*c,a,-a*s,-a*c,b];}
function columnMajor(m){return [m[0],m[3],m[6],m[1],m[4],m[7],m[2],m[5],m[8]];}
function projectedBounds(model,warp,angle,registration){
 const vertices=new Float32Array(model.buffer,0,model.meta.vertexByteLength/4),m=referenceBasis(model.meta,angle);
 const zmin=model.meta.bounds.min[2],w=warp.width/100,h=warp.height/100,pixels=registration.pixels;
 let left=Infinity,right=-Infinity,top=Infinity,bottom=-Infinity;
 for(let i=0;i<vertices.length;i+=8){
  const x=vertices[i]*w,y=vertices[i+1]*w,z=(vertices[i+2]-zmin)*h;
  const px=registration.centerX+(m[0]*x+m[1]*y+m[2]*z)*pixels;
  const py=registration.ground-(m[3]*x+m[4]*y+m[5]*z)*pixels;
  left=Math.min(left,px);right=Math.max(right,px);top=Math.min(top,py);bottom=Math.max(bottom,py);
 }
 return {left,right,top,bottom};
}
window.ListauntonWarpMath={registrations,guide,bounded,scaleRange,unwarped,effectiveWarp,preset,restore,angleForPiece,setAllTilts,referenceBasis,orbitBasis,columnMajor,projectedBounds};
})();
