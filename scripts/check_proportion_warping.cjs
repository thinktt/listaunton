const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert'),crypto=require('crypto');
const root=path.resolve(process.argv[2]||path.join(__dirname,'..')),html=fs.readFileSync(path.join(root,'set-comparison.html'),'utf8');
function script(text,id){const m=text.match(new RegExp('<script id="'+id+'"[^>]*>([\\s\\S]*?)</script>'));assert(m,'Missing '+id);return m[1];}
const board=JSON.parse(script(html,'board-data')),scales=JSON.parse(script(html,'side-scale-data'));
const context={window:{}};vm.runInNewContext(script(html,'warp-math-runtime'),context);const math=context.window.ListauntonWarpMath;
const records=math.registrations(board),guide=math.guide(scales),squashed=math.preset('bishop',records,guide),chavet=math.preset('chavet',records,guide);
const matchedRecords=math.registrations({...board,pieces:board.pieces.map(({warpRuler,...item})=>item)});
assert.equal(squashed.bishop.height,88);assert.equal(squashed.bishop.width,100);
for(const [piece,r] of Object.entries(records)){
 assert.equal(squashed[piece].width,100);if(piece!=='bishop')assert.equal(squashed[piece].height,100);
 assert(Math.abs(r.ratio*chavet[piece].height/100-guide[piece])<.0006,piece+' Chavet height');
 let meta,buffer;
 if(piece==='queen'){
  const viewer=JSON.parse(script(fs.readFileSync(path.join(root,'review.html'),'utf8'),'viewer-document'));
  meta=JSON.parse(script(viewer,'mesh-metadata'));buffer=Buffer.from(script(viewer,'mesh-data').trim(),'base64');
 }else{meta=JSON.parse(fs.readFileSync(path.join(root,'assets',piece,'mesh.json'),'utf8'));buffer=fs.readFileSync(path.join(root,'assets',piece,'mesh.bin'));}
 assert.equal(meta.sourceSha256,r.sourceSha256);
 const data=buffer.buffer.slice(buffer.byteOffset,buffer.byteOffset+buffer.byteLength),model={meta,buffer:data};
 const digest=()=>crypto.createHash('sha256').update(Buffer.from(data)).digest('hex'),before=digest();
 const original=math.projectedBounds(model,{height:100,width:100},54,r);
 const changed=math.projectedBounds(model,squashed[piece],54,r);
 // With both a warp and a nonstandard camera, uniform scale must expand every
 // projected edge about the foot center, including the visible front of the sole.
 const shape = {height: 83, width: 112};
 const tilt = 47;
 const unscaled = math.projectedBounds(model, shape, tilt, r);
 for (const scale of [50, 125, 150]) {
  const dimensions = math.effectiveWarp({...shape, scale});
  const scaled = math.projectedBounds(model, dimensions, tilt, r);
  for (const edge of ['left','right','top','bottom']) {
   const anchor = edge === 'left' || edge === 'right' ? r.centerX : r.ground;
   const expected = anchor + (unscaled[edge] - anchor) * scale / 100;
   assert(Math.abs(scaled[edge] - expected) < 1e-6, piece+' '+edge+' must scale about the foot');
  }
 }
 // Alpha sampling and the low-res mesh export can shift the measured edge by
 // a pixel or two. Test the current mesh against its own render registration,
 // even when the lab deliberately retains an earlier physical ruler.
 const matched=math.projectedBounds(model,math.unwarped,54,matchedRecords[piece]);
 assert(Math.abs(matched.top-r.targetTop)<2,piece+' camera/top registration: '+(matched.top-r.targetTop));
 assert(Math.abs(matched.bottom-r.targetBottom)<2,piece+' camera/foot registration: '+(matched.bottom-r.targetBottom));
 if(piece==='bishop'){
  assert(changed.top-original.top>9,'Squash should visibly lower the bishop top');
  assert(Math.abs(changed.bottom-original.bottom)<.1,'Foot must stay anchored');
  assert(Math.abs((changed.right-changed.left)-(original.right-original.left))<.1,'Squash must preserve base width');
  console.log('Bishop −12%: top moves down '+(changed.top-original.top).toFixed(2)+' original pixels; foot moves '+(changed.bottom-original.bottom).toFixed(3)+' px.');
  const tilted=math.projectedBounds(model,squashed[piece],45,r);
  assert(Math.abs(tilted.top-changed.top)>10,'Tilt must update the actual reference projection');
  for(const angle of [20,45,80]){
   const basis=math.referenceBasis(meta,angle);
   for(let row=0;row<3;row++)for(let other=0;other<3;other++){
    const dot=basis[row*3]*basis[other*3]+basis[row*3+1]*basis[other*3+1]+basis[row*3+2]*basis[other*3+2];
    assert(Math.abs(dot-(row===other?1:0))<1e-6,'Camera tilt must rotate without stretching');
   }
  }
 }else for(const key of ['top','bottom','left','right'])assert.equal(changed[key],original[key],piece+' changed unexpectedly');
 assert.equal(digest(),before,'Source vertices must not be mutated');
 console.log(piece+': original registration top Δ '+(original.top-r.targetTop).toFixed(2)+'px, foot Δ '+(original.bottom-r.targetBottom).toFixed(2)+'px');
}
const restored=math.restore({angle:999,pieces:{bishop:{height:-20,width:999},king:{height:null,width:'bad'}}},records,guide);
assert.equal(restored.angle,80);assert.equal(restored.pieces.bishop.height,50);assert.equal(restored.pieces.bishop.width,130);assert.equal(restored.pieces.king.height,100);assert.equal(restored.pieces.king.width,100);
assert.equal(math.restore(null,records,guide).pieces.bishop.height,100,'Show the actual bishop on first load');
assert.equal(records.bishop.warpRuler.checkpoint,'025');
const resized=math.registrations({...board,pieces:board.pieces.map(item=>item.piece==='bishop'
 ? {...item,renderTop:item.renderTop+50,modelHeight:item.modelHeight*.9} : item)});
assert.equal(resized.bishop.pixels,records.bishop.pixels,'A shorter bishop must keep the same measuring scale');
assert.equal(resized.bishop.ground,records.bishop.ground);
assert(Math.abs(resized.bishop.ratio/records.bishop.ratio-.9)<1e-9);
assert.equal(math.restore({angle:49.5,pieces:{bishop:{height:80,width:101}}},records,guide).pieces.bishop.height,80);
const legacy=math.restore({angle:49.5,pieces:{bishop:{height:84.4,width:105},queen:{height:87.7,width:112.7}}},records,guide);
for(const shape of Object.values(legacy.pieces))assert.equal(shape.scale,100,'Existing experiments retain their original size');
const sized=math.restore({pieces:{pawn:{scale:121.3},king:{scale:999},queen:{scale:'invalid'}}},records,guide);
assert.equal(sized.pieces.pawn.scale,121.3);assert.equal(sized.pieces.king.scale,150);assert.equal(sized.pieces.queen.scale,100);
for(const piece of Object.keys(records))assert.equal(math.angleForPiece(legacy,piece),49.5,'Old saved experiment must retain its reference angle');
assert.equal(legacy.pieces.queen.height,87.7);assert.equal(legacy.pieces.queen.width,112.7);
const independent=math.restore({...legacy,tilts:{bishop:45,queen:60,rook:'invalid',pawn:999}},records,guide);
assert.equal(math.angleForPiece(independent,'bishop'),45);assert.equal(math.angleForPiece(independent,'queen'),60);assert.equal(math.angleForPiece(independent,'king'),49.5);assert.equal(math.angleForPiece(independent,'rook'),49.5);assert.equal(math.angleForPiece(independent,'pawn'),80);
const shapes=JSON.stringify(independent.pieces);math.setAllTilts(independent,42.5);
assert.equal(JSON.stringify(independent.pieces),shapes,'All-tilts control must preserve height and width');
for(const piece of Object.keys(records))assert.equal(math.angleForPiece(independent,piece),42.5);
console.log('PASS: exact saved cameras, fixed foot/width under compression, Chavet preset, source preservation, independent tilts, and migration of saved experiments.');
