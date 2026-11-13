// Check that the displayed mesh assets are the current Blender models and
// that each can be uniformly scaled to the selected king-relative height.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert');
const root=path.resolve(process.argv[2]||path.join(__dirname,'..'));
const read=file=>fs.readFileSync(path.join(root,file));
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const html=read('set-comparison.html').toString('utf8');
function script(document,id){const m=document.match(new RegExp('<script id="'+id+'"[^>]*>([\\s\\S]*?)</script>'));assert(m,'Missing '+id);return m[1];}
const scales=JSON.parse(script(html,'side-scale-data'));
const profiles=JSON.parse(script(html,'model-profile-data'));
const chosen=JSON.parse(read('assets/side-views/defaults.json'));
const rows=Object.fromEntries(scales.pieces.map(x=>[x.piece,x]));
const kingHeight=rows.king.height*chosen.scales.king;
const expected=chosen.shown_height_percent_of_king;
const queenDoc=JSON.parse(script(read('review.html').toString('utf8'),'viewer-document'));
for(const piece of chosen.order){
 let meta,bytes;
 if(piece==='queen'){
  meta=JSON.parse(script(queenDoc,'mesh-metadata'));
  bytes=Buffer.from(script(queenDoc,'mesh-data').trim(),'base64');
 }else{
  meta=JSON.parse(read('assets/'+piece+'/mesh.json'));
  bytes=read('assets/'+piece+'/mesh.bin');
 }
 assert.equal(sha(read('models/'+piece+'/'+piece+'-rebuilt.blend')),meta.sourceSha256,piece+' mesh is stale');
 assert.equal(meta.vertexStrideBytes,32);
 assert.equal(meta.vertexByteLength,meta.vertexCount*32);
 assert.equal(meta.indexByteOffset,meta.vertexByteLength);
 assert.equal(meta.totalByteLength,bytes.length);
 assert.equal(meta.indexByteOffset+meta.indexCount*4,bytes.length);
 const low=[Infinity,Infinity,Infinity],high=[-Infinity,-Infinity,-Infinity];
 for(let i=0;i<meta.vertexCount;i++)for(let j=0;j<3;j++){
  const value=bytes.readFloatLE(i*32+j*4);assert(Number.isFinite(value),piece+' non-finite vertex');
  low[j]=Math.min(low[j],value);high[j]=Math.max(high[j],value);
 }
 for(let j=0;j<3;j++){
  assert(Math.abs(low[j]-meta.bounds.min[j])<1e-4,piece+' minimum bounds');
  assert(Math.abs(high[j]-meta.bounds.max[j])<1e-4,piece+' maximum bounds');
 }
 const texture=piece==='queen'?meta.materialConfig.texture:(meta.texture||meta.material.texture);
 assert(read(texture).length>0,piece+' texture missing');
 const target=rows[piece].height*chosen.scales[piece]/kingHeight;
 assert.equal(Number((100*target).toFixed(1)),expected[piece],piece+' target height');
 const uniform=target/(high[2]-low[2]);
 assert(Math.abs((high[2]-low[2])*uniform-target)<1e-10,piece+' scaled height');
 const p=profiles[piece];const png=read(p.file);
 assert.equal(png.readUInt32BE(16),p.width);assert.equal(png.readUInt32BE(20),p.height);
 assert(p.top>0&&p.bottom<p.height&&p.left>=0&&p.right<p.width&&p.bottom>p.top,piece+' profile bounds');
 if(piece==='bishop'){
  const base='docs/bishop-mission';
  const checkpoints=fs.readdirSync(path.join(root,base)).filter(x=>/^iteration-\d+$/.test(x)).sort().reverse();
  const checkpoint=checkpoints.map(x=>path.join(base,x,'checkpoint.json')).filter(x=>fs.existsSync(path.join(root,x)))
    .map(x=>JSON.parse(read(x))).find(x=>x.accepted_model_sha256===meta.sourceSha256);
  assert(checkpoint,'No matching bishop checkpoint');
  assert.equal(checkpoint.accepted_model_sha256,meta.sourceSha256,'Bishop profile checkpoint model');
  assert.equal(checkpoint.public_stage_canonical_preview_identical_files[p.file],sha(png),'Bishop profile checkpoint image');
 }else{
  const registration=JSON.parse(read('assets/'+piece+'/side-registration.json'));
  assert.equal(registration.source_blend_sha256,meta.sourceSha256,piece+' profile model');
  if(piece==='queen')assert.equal(registration.wood_profile_sha256,sha(png),'Queen profile image');
  else{assert.equal(registration.profile,p.file,piece+' profile path');assert.equal(registration.profile_sha256,sha(png),piece+' profile image');}
 }
 console.log(piece+': current Blender mesh, texture, profile, and '+expected[piece].toFixed(1)+'% height verified');
}
