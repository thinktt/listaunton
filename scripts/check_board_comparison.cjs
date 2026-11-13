// Check board positioning from the actual camera data and exercise the wipe.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),vm=require('vm'),assert=require('assert');
const htmlPath=path.resolve(process.argv[2]),root=path.dirname(htmlPath),html=fs.readFileSync(htmlPath,'utf8');
function script(id){const match=html.match(new RegExp('<script id="'+id+'"[^>]*>([\\s\\S]*?)</script>'));assert(match,'Missing '+id);return match[1];}
const data=JSON.parse(script('board-data')),scales=JSON.parse(script('side-scale-data'));
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
for(const file of [data.original,data.empty]){
 const png=fs.readFileSync(path.join(root,file));assert.equal(png.readUInt32BE(16),data.width);assert.equal(png.readUInt32BE(20),data.height);
}
class Element{
 constructor(){this.children=[];this.style={};this.attrs={};this.events={};this.value='';this.hidden=false;}
 append(child){this.children.push(child)}
 addEventListener(name,fn){(this.events[name]??=[]).push(fn)}
 setAttribute(name,value){this.attrs[name]=value}
 fire(name,extra={}){for(const fn of this.events[name]||[])fn({target:this,preventDefault(){},...extra});}
 setPointerCapture(id){this.captured=id}
 getBoundingClientRect(){return {left:100,width:659}}
}
const ids={};for(const id of ['board-data','side-scale-data','board-model-layer','board-pieces','board-shadows','board-stage','board-wipe','board-divider','board-status','board-original','board-half','board-models','board-height-matched','board-height-chosen','board-height-summary','board-fit-note'])ids[id]=new Element();
ids['board-data'].textContent=JSON.stringify(data);ids['side-scale-data'].textContent=JSON.stringify(scales);ids['board-wipe'].value='50';
for(const item of scales.pieces){ids['side-scale-'+item.piece]=new Element();ids['side-scale-'+item.piece].value=String(item.defaultScale);ids['side-reset-'+item.piece]=new Element();}
const document={getElementById:id=>ids[id],createElement:()=>new Element()};
vm.runInNewContext(script('board-comparison-runtime'),{document});
assert.deepEqual(data.pieces.map(x=>x.piece),['king','queen','bishop','knight','rook','pawn']);
assert.equal(ids['board-pieces'].children.length,6);assert.equal(ids['board-shadows'].children.length,6);
assert.equal(ids['board-height-matched'].attrs['aria-pressed'],'true');
assert(ids['board-fit-note'].textContent.includes('clipped'));
const matchedWidths={};
for(const [index,item] of data.pieces.entries()){
 const img=ids['board-pieces'].children[index],scale=parseFloat(img.style.width)/100*data.width/item.width;
 const top=parseFloat(img.style.top)/100*data.height,left=parseFloat(img.style.left)/100*data.width;
 assert(Math.abs(top+item.renderTop*scale-item.targetTop)<1e-8,item.piece+' matched top');
 assert(Math.abs(top+item.renderBottom*scale-item.targetBottom)<1e-8,item.piece+' matched bottom');
 assert(Math.abs(left+item.footX*scale-item.centerX)<1e-8,item.piece+' matched foot center');
 matchedWidths[item.piece]=parseFloat(img.style.width);
}
ids['board-height-chosen'].fire('click');
assert.equal(ids['board-height-chosen'].attrs['aria-pressed'],'true');
const kingHeight=data.kingHeight*data.kingPixelsPerUnit,kingScale=scales.pieces.find(x=>x.piece==='king').defaultScale;
for(const [index,item] of data.pieces.entries()){
 const img=ids['board-pieces'].children[index],png=fs.readFileSync(path.join(root,item.file));
 assert(img.src.startsWith(item.file+'?v='));assert.equal(sha(png).slice(0,16),item.version);
 const imageScale=parseFloat(img.style.width)/100*data.width/item.width;
 const left=parseFloat(img.style.left)/100*data.width,top=parseFloat(img.style.top)/100*data.height;
 assert(Math.abs(left+item.footX*imageScale-item.centerX)<1e-8,item.piece+' foot x');
 assert(Math.abs(top+item.footY*imageScale-data.groundY)<1e-8,item.piece+' foot y');
 const expected=scales.pieces.find(x=>x.piece===item.piece);
 const relative=expected.height*expected.defaultScale/(scales.pieces.find(x=>x.piece==='king').height*kingScale);
 assert(Math.abs(item.modelHeight*item.pixelsPerUnit*imageScale/kingHeight-relative)<1e-8,item.piece+' relative height');
 if(item.piece==='king')assert(Math.abs(item.baseWidth*item.pixelsPerUnit*imageScale-data.kingBasePixels)<1e-8,'King base width');
}
assert.equal(ids['board-model-layer'].style.clipPath,'inset(0 50% 0 0)');
ids['board-models'].fire('click');assert.equal(ids['board-wipe'].value,'100');assert(ids['board-divider'].hidden);
ids['board-original'].fire('click');assert.equal(ids['board-wipe'].value,'0');assert(ids['board-divider'].hidden);
ids['board-half'].fire('click');assert.equal(ids['board-wipe'].value,'50');assert(!ids['board-divider'].hidden);
ids['board-stage'].fire('pointerdown',{isPrimary:true,button:0,pointerId:1,clientX:100+659*.7});
ids['board-stage'].fire('pointermove',{pointerId:1,clientX:100+659*.3});
ids['board-stage'].fire('pointerup',{pointerId:1});assert.equal(ids['board-wipe'].value,'30');
const queen=ids['board-pieces'].children[1],before=parseFloat(queen.style.width);
ids['side-scale-queen'].value='130';ids['side-scale-queen'].fire('input');
const old=scales.pieces.find(x=>x.piece==='queen').defaultScale;
assert(Math.abs(parseFloat(queen.style.width)/before-130/old)<1e-8,'Gallery size must update the board');
ids['board-height-matched'].fire('click');
assert(Math.abs(parseFloat(queen.style.width)-matchedWidths.queen)<1e-8,'Matched fit must not depend on chosen slider sizes');
console.log('PASS: original image height fits, chosen sizes, 54-degree render placement, wipe and live sizing.');
