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
