const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync(process.argv[2],'utf8');
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
for(const id of ['tab-comparison','tab-side-views','panel-comparison','panel-side-views','comparison-tools','view-note'])ids[id]=new E(id);
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
ids['tab-side-views'].events.keydown({key:'Home',preventDefault(){}});
assert.equal(ids.grid.children,whiteCards);assert.equal(cards()[1],queenCard);
assert.equal(ids.white.attrs['aria-pressed'],'true');
assert.equal(cards()[3].children[1].value,savedWhiteBishop);
window.location.hash='#side-views';events.hashchange();assert.equal(ids['panel-side-views'].hidden,false);
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
const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,file))).digest('hex');
const near=(actual,expected,label)=>assert(Math.abs(actual-expected)<.001,`${label}: ${actual} != ${expected}`);
const king=sizing.pieces.find(row=>row.piece==='king');
near(king.display.visible_height_px,430,'King anchor height');
assert(html.includes('class="side-lineup"'));assert(html.includes('class="side-scroll"'));
assert(html.includes('grid-template-columns:repeat(6,minmax(220px,1fr))'),'One row must retain scale on narrow screens');
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
 near(d.base_width_px/king.display.base_width_px,row.base_ratio_to_king,'Displayed base ratio');
 const card=html.match(new RegExp('<article[^>]*data-side-piece="'+row.piece+'"[\\s\\S]*?</article>'))[0];
 const style=card.match(/<img[^>]*style="([^"]+)"/)[1];
 const width=Number(style.match(/width:([\d.]+)px/)[1]);
 const left=Number(style.match(/left:calc\(50% \+ (-?[\d.]+)px\)/)[1]);
 const top=Number(style.match(/top:(-?[\d.]+)px/)[1]);
 const s=width/item.width;
 near(s,d.scale,'Uniform scale in page');near(top+cut.ground_y_px*s,sizing.display.ground_y_px,'Shared ground line');
 near(left+cut.base_center_x_px*s,0,'Base centering');
 assert(top+cut.bounds_px[1]*s>=0,'Head clipped at top');
 const half=sizing.display.min_slot_width_px/2;
 assert(left+cut.bounds_px[0]*s>=-half,'Left side clipped');
 assert(left+cut.bounds_px[2]*s<=half,'Right side clipped');
 assert(card.includes('href="'+item.source_file+'"'),'Untouched side view must remain accessible');
}
console.log('PASS: uniform king-relative base scale, shared ground, no clipped pieces, original guide hashes and transparent cutout provenance.');
