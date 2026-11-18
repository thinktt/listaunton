// Exercise the actual embedded model and board controls together, including
// the saved-profile fallback and the independent side-view slider values.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync(process.argv[2],'utf8');
function script(id){const m=html.match(new RegExp('<script id="'+id+'"[^>]*>([\\s\\S]*?)</script>'));assert(m,'Missing '+id);return m[1];}
const scales=JSON.parse(script('side-scale-data'));
const board=JSON.parse(script('board-data'));
const profiles=JSON.parse(script('model-profile-data'));
// The original board measurements are fixed. A model edit can change the
// visible footprint at 54 degrees and its inferred height in matched mode.
const fitFile=path.join(path.dirname(process.argv[2]),'assets/board-comparison/height-fit.json');
const {targets}=JSON.parse(fs.readFileSync(fitFile,'utf8'));
const expectedHeights={};
for(const piece of board.pieces){
 const target=targets[piece.piece];
 const imageScale=(target.bottom-target.top)/(piece.renderBottom-piece.renderTop);
 expectedHeights[piece.piece]=imageScale*piece.pixelsPerUnit*piece.modelHeight;
}
const matchedLabel=piece=>(100*expectedHeights[piece]/expectedHeights.king).toFixed(1)+'% of king';
class Element{
 constructor(){this.children=[];this.style={};this.attrs={};this.events={};this.value='';this.hidden=false;this.clientWidth=1320;this.clientHeight=620;this.classList={toggle(){}};}
 append(child){this.children.push(child)}
 addEventListener(name,fn){(this.events[name]??=[]).push(fn)}
 setAttribute(name,value){this.attrs[name]=value}
 getAttribute(name){return this.attrs[name]??null}
 fire(name,extra={}){for(const fn of this.events[name]||[])fn({target:this,preventDefault(){},...extra});}
 click(){this.fire('click')}
 setPointerCapture(){}
 getBoundingClientRect(){return {left:0,width:659}}
}
const ids={};
for(const id of ['side-scale-data','board-data','model-profile-data','models-stage','models-fallback','models-canvas','panel-models','models-status','models-height-note','models-heading','models-headings','side-lineup','models-side','models-threequarter','models-reference','models-height-matched','models-wood','models-neutral','models-blender','tab-models','board-model-layer','board-pieces','board-shadows','board-stage','board-wipe','board-divider','board-status','board-original','board-half','board-models','board-height-matched','board-height-chosen','board-height-summary','board-fit-note'])ids[id]=new Element();
ids['side-scale-data'].textContent=JSON.stringify(scales);
ids['board-data'].textContent=JSON.stringify(board);
ids['model-profile-data'].textContent=JSON.stringify(profiles);
ids['board-height-matched'].setAttribute('aria-pressed','true');
ids['board-wipe'].value='50';ids['panel-models'].hidden=true;
for(const item of scales.pieces){
 const piece=item.piece;
 ids['side-scale-'+piece]=new Element();ids['side-scale-'+piece].value=String(item.defaultScale);
 ids['side-reset-'+piece]=new Element();ids['models-heading-'+piece]=new Element();ids['models-ratio-'+piece]=new Element();
}
for(const piece of scales.defaultOrder){const card=new Element();card.setAttribute('data-side-piece',piece);ids['side-lineup'].append(card);}
const document={getElementById:id=>{assert(ids[id],'Missing fixture element '+id);return ids[id]},createElement:()=>new Element()};
const context={document,window:{location:{hash:''},addEventListener(){}},location:{protocol:'file:'},ResizeObserver:class{observe(){}},requestAnimationFrame(){}};
vm.runInNewContext(script('model-lineup-runtime'),context);
vm.runInNewContext(script('board-comparison-runtime'),context);
const label=piece=>ids['models-ratio-'+piece].textContent;
const image=piece=>ids['models-fallback'].children[scales.defaultOrder.indexOf(piece)];
function assertProfileRatios(){
 const displayed=piece=>parseFloat(image(piece).style.width)/profiles[piece].width*(profiles[piece].bottom-profiles[piece].top);
 for(const piece of scales.defaultOrder){
  const expected=Number(label(piece).split('%')[0])/100;
  assert(Math.abs(displayed(piece)/displayed('king')-expected)<.00051,piece+' fallback height');
 }
}
assert.equal(ids['models-height-matched'].attrs['aria-pressed'],'true');
for(const piece of scales.defaultOrder)assert.equal(label(piece),matchedLabel(piece),piece+' matched to the original board');
assert(ids['board-height-summary'].textContent.includes('Q '+matchedLabel('queen').split(' ')[0]));
assertProfileRatios();
ids['models-height-matched'].click();
assert.equal(ids['models-height-matched'].attrs['aria-pressed'],'false');
assert.equal(ids['board-height-chosen'].attrs['aria-pressed'],'true');
assert.equal(label('queen'),'85.2% of king');assert.equal(label('bishop'),'71.8% of king');
assert(ids['models-height-note'].textContent.includes('your chosen'));
assertProfileRatios();
ids['side-scale-pawn'].value='120';ids['side-scale-pawn'].fire('input');
assert.equal(label('pawn'),'57.4% of king');
ids['models-height-matched'].click();
assert.equal(ids['board-height-matched'].attrs['aria-pressed'],'true');
assert.equal(label('pawn'),matchedLabel('pawn'));
assert.equal(ids['side-scale-pawn'].value,'120','Matched mode must preserve chosen sizes');
assertProfileRatios();
ids['board-height-chosen'].click();assert.equal(ids['models-height-matched'].attrs['aria-pressed'],'false');assert.equal(label('pawn'),'57.4% of king');
ids['board-height-matched'].click();assert.equal(ids['models-height-matched'].attrs['aria-pressed'],'true');assert.equal(label('pawn'),matchedLabel('pawn'));
assert(!ids['models-height-matched'].disabled,'Height switch remains available for saved profiles');
console.log('PASS: matched and chosen heights stay synchronized in both directions, including saved profiles and chosen slider values.');
