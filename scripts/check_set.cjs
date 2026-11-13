const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync(process.argv[2],'utf8');
const presentationOnly=process.argv.includes('--presentation-only');
assert(html.includes('id="models-reference"')&&html.includes('>54°</button>'),'Reference-angle control is missing');
class E{constructor(tag){this.tag=tag;this.children=[];this.style={};this.attrs={};this.events={};this.value='';}append(...els){this.children.push(...els)}replaceChildren(){this.children=[]}setAttribute(k,v){this.attrs[k]=v}addEventListener(k,f){this.events[k]=f}}
const ids=Object.fromEntries(['set-data','grid','black','white','background'].map(k=>[k,new E(k)]));ids['set-data'].textContent=html.match(/id="set-data"[^>]*>(.*?)<\/script>/s)[1];
const doc={getElementById:id=>ids[id],createElement:t=>new E(t),documentElement:{style:{setProperty(){}}}};
vm.runInNewContext(html.match(/<script>\s*([\s\S]*?)<\/script>/)[1],{document:doc});
function cards(){assert.equal(ids.grid.children.length,6);return ids.grid.children;}
assert.equal(cards()[0].children[1].value,'candidate-1');assert.equal(cards()[2].children[1].value,'candidate-8');
ids.white.events.click();assert.equal(cards()[3].children[1].value,'white-candidate-3');
for(const color of ['black','white']){ids[color].events.click();for(const card of cards()){const sel=card.children[1];if(sel.disabled)continue;for(const opt of sel.children){sel.value=opt.value;sel.events.change();const im=card.children[2].children[0].children[0].children[0];assert(im.src);assert(Number.isFinite(parseFloat(im.style.width)));}}}
ids.white.events.click();assert(cards()[1].children[1].disabled);ids.black.events.click();assert.equal(cards()[2].children[1].value,'candidate-8');
console.log('PASS: six pairs, both colors, all candidate options, retained selections, missing white queen, finite placement.');

// Exercise the actual tab code with the already-populated comparison DOM.
for(const id of ['tab-comparison','tab-side-views','tab-models','tab-board','tab-warping','panel-comparison','panel-side-views','panel-models','panel-board','panel-warping','comparison-tools','view-note'])ids[id]=new E(id);
for(const el of Object.values(ids))el.focus=function(){this.focused=true;};
const events={},window={location:{hash:'#side-views'},addEventListener:(name,fn)=>events[name]=fn};
const comparisonCards=ids.grid.children;
const script=html.match(/<script id="set-tabs-runtime">([\s\S]*?)<\/script>/)[1];
vm.runInNewContext(script,{document:doc,window});
assert.equal(ids['panel-side-views'].hidden,false);
assert.equal(ids['panel-comparison'].hidden,true);
assert.equal(ids['comparison-tools'].hidden,true);
assert.equal(ids['tab-side-views'].attrs['aria-selected'],'true');
assert.equal(ids['tab-side-views'].tabIndex,0);
ids['tab-comparison'].events.click();
assert.equal(window.location.hash,'comparison');
assert.equal(ids['panel-side-views'].hidden,true);
assert.equal(ids['comparison-tools'].hidden,false);
assert.equal(ids.grid.children,comparisonCards,'Tab switches must not rebuild or reset comparisons');
assert.equal(cards()[2].children[1].value,'candidate-8');
ids.white.events.click();
const whiteCards=ids.grid.children,savedWhiteBishop=cards()[3].children[1].value;
const queenCard=whiteCards[1];assert(queenCard.children[1].disabled);
ids['tab-comparison'].events.keydown({key:'ArrowRight',preventDefault(){}});
assert.equal(ids['panel-side-views'].hidden,false);assert(ids['tab-side-views'].focused);
ids['tab-side-views'].events.keydown({key:'ArrowRight',preventDefault(){}});
assert.equal(ids['panel-models'].hidden,false);assert(ids['tab-models'].focused);
assert.equal(ids['panel-side-views'].hidden,true);
ids['tab-models'].events.keydown({key:'ArrowRight',preventDefault(){}});
assert.equal(ids['panel-board'].hidden,false);assert(ids['tab-board'].focused);
ids['tab-board'].events.keydown({key:'ArrowRight',preventDefault(){}});
assert.equal(ids['panel-warping'].hidden,false);assert(ids['tab-warping'].focused);
ids['tab-warping'].events.keydown({key:'ArrowRight',preventDefault(){}});
assert.equal(ids['panel-comparison'].hidden,false);assert(ids['tab-comparison'].focused);
ids['tab-side-views'].events.keydown({key:'Home',preventDefault(){}});
assert.equal(ids.grid.children,whiteCards);assert.equal(cards()[1],queenCard);
assert.equal(ids.white.attrs['aria-pressed'],'true');
assert.equal(cards()[3].children[1].value,savedWhiteBishop);
window.location.hash='#side-views';events.hashchange();assert.equal(ids['panel-side-views'].hidden,false);
window.location.hash='#models';events.hashchange();assert.equal(ids['panel-models'].hidden,false);
window.location.hash='#board';events.hashchange();assert.equal(ids['panel-board'].hidden,false);
window.location.hash='#warping';events.hashchange();assert.equal(ids['panel-warping'].hidden,false);
window.location.hash='#blender';events.hashchange();assert.equal(ids['panel-models'].hidden,false);
window.location.hash='#unknown';events.hashchange();assert.equal(ids['panel-comparison'].hidden,false);
assert.equal(ids.grid.children,whiteCards);
const path=require('path'),crypto=require('crypto'),root=path.dirname(path.resolve(process.argv[2]));
const manifest=JSON.parse(fs.readFileSync(path.join(root,'assets/side-views/manifest.json'),'utf8'));
assert.deepEqual(manifest.pieces.map(x=>x.piece),['king','queen','rook','bishop','knight','pawn']);
for(const item of manifest.pieces){
 assert(html.includes('data-side-piece="'+item.piece+'"'));
 assert(html.includes('src="'+item.file+'"'));assert(html.includes('href="'+item.review+'"'));
 const bytes=fs.readFileSync(path.join(root,item.file));assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),item.sha256);
 assert.equal(bytes.readUInt32BE(16),item.width);assert.equal(bytes.readUInt32BE(20),item.height);
 const record=JSON.parse(fs.readFileSync(path.join(root,item.generation),'utf8'));assert(record.prompt);assert(record.tool.toLowerCase().includes('image'));
}
console.log('PASS: side-view deep link, keyboard tabs, retained comparison/color state, six images, dimensions, hashes and prompt records.');

// Validate the page's actual placements against source measurements, not card size.
const sizing=JSON.parse(fs.readFileSync(path.join(root,manifest.scale),'utf8'));
const sliderData=JSON.parse(html.match(/<script id="side-scale-data"[^>]*>(.*?)<\/script>/s)[1]);
const chosen=JSON.parse(fs.readFileSync(path.join(root,'assets/side-views/defaults.json'),'utf8'));
const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,file))).digest('hex');
const textSha=file=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,file),'utf8').replace(/\r\n/g,'\n')).digest('hex');
const near=(actual,expected,label)=>assert(Math.abs(actual-expected)<.001,`${label}: ${actual} != ${expected}`);
const king=sizing.pieces.find(row=>row.piece==='king');
near(king.display.visible_height_px,430,'King anchor height');
assert(html.includes('class="side-lineup"'));assert(html.includes('class="side-scroll"'));
assert(html.includes('grid-template-columns:repeat(6,minmax(320px,1fr))'),'One row must retain space for slider extremes');
assert(html.includes('height:auto'),'No independent vertical stretching');
for(const row of sizing.pieces){
 const item=manifest.pieces.find(item=>item.piece===row.piece),cut=row.cutout,d=row.display;
 assert.equal(sha(row.original.file),row.original.sha256,'Original width source changed');
 assert.equal(sha(cut.file),cut.sha256,'Cutout measured for a different image');
 const extraction=JSON.parse(fs.readFileSync(path.join(root,item.generation),'utf8'));
 assert.equal(sha(extraction.source.file),extraction.source.sha256,'Original generated guide changed');
 assert.equal(item.source_file,extraction.source.file);assert(extraction.transparent_background);
 assert.equal(extraction.output.sha256,item.sha256);assert(cut.fully_transparent_fraction>.5);
 near(row.base_ratio_to_king,row.original.base_width_px/king.original.base_width_px,'Original ratio');
 const check=row.height_check,model=row.model,correction=check.uniform_correction_factor;
 assert.equal(model.assumed_elevation_degrees,54);
 if(!presentationOnly){
 assert.equal(textSha(model.file),model.sha256,'Height-check model metadata changed');
 assert.equal(sha(model.binary),model.binary_sha256,'Height-check geometry changed');
 assert.equal(textSha(model.camera_file),model.camera_sha256,'Height-check camera assumption changed');
 }
 near(model.height_to_base,model.height/model.base_diameter,'Model dimensions');
 if(row.piece==='knight'){
  const meta=JSON.parse(fs.readFileSync(path.join(root,model.file),'utf8'));
  assert(model.base_diameter<meta.bounds.size[0]-.1,'Knight base must exclude its overhanging muzzle');
 }
 near(check.height_ratio_to_king,row.base_ratio_to_king*model.height_to_base/king.model.height_to_base,'Model height ratio');
 near(d.visible_height_px/king.display.visible_height_px,check.height_ratio_to_king,'Displayed height estimate');
 near(d.base_width_px/king.display.base_width_px,row.base_ratio_to_king*correction,'Displayed base ratio');
 const card=html.match(new RegExp('<article[^>]*data-side-piece="'+row.piece+'"[\\s\\S]*?</article>'))[0];
 const style=card.match(/<img[^>]*style="([^"]+)"/)[1];
 const width=Number(style.match(/width:([\d.]+)px/)[1]);
 const left=Number(style.match(/left:calc\(50% \+ (-?[\d.]+)px\)/)[1]);
 const top=Number(style.match(/top:(-?[\d.]+)px/)[1]);
 const origin=style.match(/transform-origin:([\d.]+)px ([\d.]+)px/).slice(1).map(Number);
 const s=width/item.width;
 near(s,d.scale,'Uniform scale in page');near(top+cut.ground_y_px*s,sliderData.ground,'Shared ground line');
 near(left+cut.base_center_x_px*s,0,'Base centering');
 assert(top+cut.bounds_px[1]*s>=0,'Head clipped at top');
 const half=sliderData.minSlotWidth/2;
 for(const factor of [.5,.79,1,1.37,1.5]){
  const tx=x=>left+origin[0]+(x*s-origin[0])*factor;
  const ty=y=>top+origin[1]+(y*s-origin[1])*factor;
  near(tx(cut.base_center_x_px),0,'Foot center must stay fixed while scaling');
  near(ty(cut.ground_y_px),sliderData.ground,'Foot bottom must stay fixed while scaling');
  assert(ty(cut.bounds_px[1])>=0,'Head clipped at slider extreme');
  assert(tx(cut.bounds_px[0])>=-half,'Left side clipped at slider extreme');
  assert(tx(cut.bounds_px[2])<=half,'Right side clipped at slider extreme');
 }
 assert(card.includes('href="'+item.source_file+'"'),'Untouched side view must remain accessible');
}
console.log(presentationOnly ? 'PASS: recorded sizing, uniform image scale, shared ground and bounds (current model hashes explicitly excluded for presentation-only check).' : 'PASS: six 54-degree model height estimates, true knight base, uniform image scale, shared ground, bounds and source hashes.');

// Exercise the actual controls, including refresh persistence and unavailable storage.
const scaleRuntime=html.match(/<script id="side-scales-runtime">([\s\S]*?)<\/script>/)[1];
const storageKey='listaunton.side-view-scales.'+sliderData.defaultsRevision;let stored=null;
const storage={getItem(){return stored;},setItem(key,value){assert.equal(key,storageKey);stored=value;}};
function scaleContext(storage){
 const elements={'side-scale-data':new E('script')};elements['side-scale-data'].textContent=JSON.stringify(sliderData);
 for(const item of sliderData.pieces)for(const prefix of ['side-picture-','side-scale-','side-scale-value-','side-ratio-','side-reset-'])elements[prefix+item.piece]=new E(prefix);
 vm.runInNewContext(scaleRuntime,{document:{getElementById:id=>elements[id]},window:{localStorage:storage}});
 return elements;
}
let controls=scaleContext(storage);
for(const item of sliderData.pieces)assert.equal(controls['side-picture-'+item.piece].style.transform,'scale('+(item.defaultScale/100)+')');
function move(piece,value){const input=controls['side-scale-'+piece];input.value=String(value);input.events.input({target:input});}
move('rook',137);assert.equal(controls['side-picture-rook'].style.transform,'scale(1.37)');
assert.equal(controls['side-scale-value-rook'].textContent,'137%');
assert.equal(controls['side-scale-rook'].attrs['aria-valuetext'],'137% of model estimate');
assert.equal(controls['side-picture-pawn'].style.transform,'scale('+(chosen.scales.pawn/100)+')');
move('king',120);const rookHeight=sliderData.pieces.find(item=>item.piece==='rook').height;
assert.equal(controls['side-ratio-rook'].textContent,'Height: '+(rookHeight*1.37/(430*1.2)*100).toFixed(1)+'% of king');
controls=scaleContext(storage);assert.equal(controls['side-scale-rook'].value,'137');assert.equal(controls['side-scale-king'].value,'120');
controls['side-reset-rook'].events.click();assert.equal(controls['side-scale-rook'].value,String(chosen.scales.rook));assert.equal(controls['side-scale-king'].value,'120');
move('pawn',10);assert.equal(controls['side-scale-pawn'].value,'50');
move('pawn',999);assert.equal(controls['side-scale-pawn'].value,'150');
stored='not json';controls=scaleContext(storage);assert.equal(controls['side-scale-king'].value,String(chosen.scales.king));
stored=JSON.stringify({king:130,pawn:'90',bishop:400});controls=scaleContext(storage);
assert.equal(controls['side-scale-king'].value,'130');assert.equal(controls['side-scale-pawn'].value,String(chosen.scales.pawn));assert.equal(controls['side-scale-bishop'].value,'150');
controls=scaleContext({getItem(){throw new Error('Storage disabled');},setItem(){throw new Error('Storage disabled');}});
move('knight',113);assert.equal(controls['side-picture-knight'].style.transform,'scale(1.13)');
console.log('PASS: fixed foot anchors and unclipped extremes, independent sliders, live king-relative labels, per-piece reset and safe storage restoration.');

assert.deepEqual(chosen.order,['king','queen','bishop','knight','rook','pawn']);
assert.deepEqual(chosen.scales,{king:105,queen:117,bishop:94,knight:116,rook:115,pawn:111});
assert.deepEqual(sliderData.defaultOrder,chosen.order);
assert.deepEqual([...html.matchAll(/data-side-piece="([^"]+)"/g)].map(match=>match[1]),chosen.order,'Static HTML should start in the chosen order');
for(const item of sliderData.pieces){
 assert.equal(item.defaultScale,chosen.scales[item.piece]);
 const height=Number((item.height*item.defaultScale/(430*chosen.scales.king)*100).toFixed(1));
 assert.equal(height,chosen.shown_height_percent_of_king[item.piece],'Chosen heights must match the saved guide');
 assert(html.includes('Height: '+height.toFixed(1)+'% of king'));
}
console.log('PASS: Chavet-based sizes/order, static defaults, default resets and matching displayed height ratios.');
