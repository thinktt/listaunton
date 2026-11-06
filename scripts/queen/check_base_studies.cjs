// Browser regression for the base study. Requires Playwright and a local site server.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');

const root = path.resolve(__dirname, '../..');
const build = path.join(root, 'build/queen-base-studies');
const endpoint = process.argv[2] || 'http://localhost:8080/';
const ids = ['socket','compressed'];
const sum = bytes => {
  let h = 2166136261;
  for (const byte of bytes) h = Math.imul(h ^ byte,16777619);
  return h>>>0;
};
const expected = Object.fromEntries(ids.map(id=>[id,sum(fs.readFileSync(path.join(build,id,'mesh.bin')))]));

async function gpuSnapshot(canvas) {
  return canvas.evaluate(async el => {
    await new Promise(done=>requestAnimationFrame(()=>requestAnimationFrame(done)));
    const gl=el.getContext('webgl2');
    const program=gl.getParameter(gl.CURRENT_PROGRAM);
    const prior=gl.getParameter(gl.ARRAY_BUFFER_BINDING);
    const vertex=gl.getVertexAttrib(0,gl.VERTEX_ATTRIB_ARRAY_BUFFER_BINDING);
    gl.bindBuffer(gl.ARRAY_BUFFER,vertex);
    let h=2166136261;
    for (const target of [gl.ARRAY_BUFFER,gl.ELEMENT_ARRAY_BUFFER]) {
      const bytes=new Uint8Array(gl.getBufferParameter(target,gl.BUFFER_SIZE));
      gl.getBufferSubData(target,0,bytes);
      for (const byte of bytes) h=Math.imul(h^byte,16777619);
    }
    gl.bindBuffer(gl.ARRAY_BUFFER,prior);
    const pose={};
    for(const name of ['uRotation','uProjection','uPan','uDistance','uCenter']) {
      const val=gl.getUniform(program,gl.getUniformLocation(program,name));
      pose[name]=typeof val==='number'?val:Array.from(val);
    }
    return {id:document.documentElement.dataset.baseStudy,checksum:h>>>0,pose};
  });
}

async function main() {
  const launch={headless:true,args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']};
  if(process.env.BASE_STUDY_BROWSER) launch.executablePath=process.env.BASE_STUDY_BROWSER;
  const browser=await chromium.launch(launch);
  try {
    const page=await browser.newPage({viewport:{width:1440,height:960}});
    const errors=[];
    page.on('pageerror',error=>errors.push(error.message));
    const url=new URL('review.html',endpoint);
    url.searchParams.set('study',Date.now().toString());
    url.hash='bases';
    await page.goto(url.href,{waitUntil:'domcontentloaded'});
    const pane=page.frameLocator('#bases-frame');
    const profiles=pane.locator('#profiles');
    await profiles.waitFor();
    await profiles.locator('img').evaluateAll(ims=>Promise.all(ims.map(im=>im.decode())));
    assert.equal(await profiles.locator('img').count(),2);
    assert.equal(await page.locator('[data-workspace="bases"]').getAttribute('aria-pressed'),'true');
    await profiles.screenshot({path:path.join(build,'browser-side.png')});
    await pane.getByRole('button',{name:'Neutral',exact:true}).click();
    const sources=await profiles.locator('img').evaluateAll(ims=>ims.map(im=>im.getAttribute('src')));
    assert.deepEqual(sources,ids.map(id=>'assets/queen-base-studies/'+id+'/side-neutral.png'));
    await pane.getByRole('button',{name:'Whole piece',exact:true}).click();
    assert.match(await profiles.getAttribute('class'),/whole/);
    await pane.getByRole('button',{name:'54° overlay'}).click();
    await pane.getByRole('button',{name:'12% compressed',exact:true}).click();
    await pane.getByRole('button',{name:'50 / 50',exact:true}).click();
    assert.equal(await pane.locator('#model-image').getAttribute('href'),'assets/queen-base-studies/compressed/fixed-neutral.png');
    assert.equal(await pane.locator('#model-image').evaluate(el=>el.style.opacity),'0.5');
    assert.equal(await pane.locator('#ref-image').getAttribute('href'),'references/lichess-staunton-3d/Black-Queen.png');
    await pane.getByRole('button',{name:'Selected high-res',exact:true}).click();
    assert.equal(await pane.locator('#ref-image').getAttribute('href'),'assets/queen/reference.png');
    await pane.getByRole('button',{name:'Wood',exact:true}).click();
    await pane.getByRole('button',{name:'Rotate model',exact:true}).click();
    const orbit=pane.frameLocator('#orbit-frame');
    await orbit.locator('html[data-base-study="compressed"]').waitFor({timeout:90000});
    const canvas=orbit.locator('canvas');
    const initial=await gpuSnapshot(canvas);
    assert.equal(initial.checksum,expected.compressed);
    const rect=await canvas.boundingBox();
    await page.mouse.move(rect.x+rect.width*.48,rect.y+rect.height*.5);
    await page.mouse.down();
    await page.mouse.move(rect.x+rect.width*.48+68,rect.y+rect.height*.5+45,{steps:4});
    await page.mouse.up();
    const rotated=await gpuSnapshot(canvas);
    assert.notDeepEqual(rotated.pose.uRotation,initial.pose.uRotation);
    const uploads={};
    for(const [id,label] of [['socket','Raised socket'],['compressed','12% compressed']]) {
      await pane.getByRole('button',{name:label,exact:true}).click();
      await orbit.locator('html[data-base-study="'+id+'"]').waitFor();
      const actual=await gpuSnapshot(canvas);
      assert.equal(actual.checksum,expected[id],id+' GPU geometry');
      assert.deepEqual(actual.pose,rotated.pose,id+' camera moved');
      assert.equal(await orbit.locator('#viewer-model-file').getAttribute('href'),'../../models/queen-base-studies/'+id+'.blend');
      uploads[id]=actual.checksum;
    }
    await page.locator('[data-workspace="overlay"]').click();
    await page.locator('[data-workspace="bases"]').click();
    assert.deepEqual((await gpuSnapshot(canvas)).pose,rotated.pose);
    assert.equal(await pane.locator('#download').getAttribute('href'),'models/queen-base-studies/compressed.blend');
    assert.deepEqual(errors,[]);
    const report={passed:true,source_meshes_match_gpu:uploads,pose_survives_model_and_tab_changes:true,
                  registered_original_and_selected_reference:true,wood_and_neutral:true,page_errors:errors};
    fs.writeFileSync(path.join(build,'browser-check.json'),JSON.stringify(report,null,2)+'\n');
    console.log('PASS',JSON.stringify(report));
  } finally { await browser.close(); }
}
main().catch(error=>{console.error(error);process.exitCode=1;});
