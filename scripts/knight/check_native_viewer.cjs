// Run the local review in Chromium and exercise its real WebGL 2 program.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { createHash } = require('node:crypto');
const { chromium } = require('playwright');

async function main() {
  const root = path.resolve(process.argv[2] || path.join(__dirname, '../..'));
  const output = path.resolve(process.argv[3] || path.join(root, 'build/knight-native'));
  fs.mkdirSync(output, {recursive: true});
  const browser = await chromium.launch({
    headless: true,
    executablePath: process.env.LISTAUNTON_CHROMIUM_BINARY || undefined,
    args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-background-networking']
  });
  try {
    const page = await browser.newPage({viewport: {width: 1000, height: 850}, deviceScaleFactor: 1});
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
    await page.route(/^https?:/, route => route.abort());
    await page.goto(pathToFileURL(path.join(root, 'knight-model.html')).href);
    await page.locator('#rotate-tab').click();
    await page.waitForFunction(() => document.querySelector('#stage').dataset.mode === 'rotate' && document.querySelector('#status').hidden);
    const canvas = page.locator('#viewer');
    const gpu = await canvas.evaluate(c => {
      const gl = c.getContext('webgl2');
      const program = gl.getParameter(gl.CURRENT_PROGRAM);
      const detail = gl.getExtension('WEBGL_debug_renderer_info');
      return {
        linked: Boolean(program && gl.getProgramParameter(program, gl.LINK_STATUS)),
        finishArray: gl.getVertexAttrib(3, gl.VERTEX_ATTRIB_ARRAY_ENABLED),
        error: gl.getError(),
        renderer: detail ? gl.getParameter(detail.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER)
      };
    });
    assert(gpu.linked && gpu.error === 0);
    const meta = await page.locator('#mesh-metadata').textContent().then(JSON.parse);
    if (meta.finish) assert(gpu.finishArray);
    const settle = () => page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
    async function capture(name) {
      await settle();
      const raw = await canvas.screenshot({path: path.join(output, name+'.png')});
      return createHash('sha256').update(raw).digest('hex');
    }
    const front = await capture('fixed-orbit');
    await page.locator('[data-view="side"]').click();
    const side = await capture('side-orbit');
    await page.locator('#neutral').click();
    const clay = await capture('side-clay');
    assert.equal(new Set([front, side, clay]).size, 3);
    await page.locator('#brown').click();
    const bounds = await canvas.boundingBox();
    const x = bounds.x+bounds.width*.5, y = bounds.y+bounds.height*.5;
    await page.mouse.move(x,y); await page.mouse.down();
    await page.mouse.move(x+110,y+38,{steps: 8}); await page.mouse.up();
    const rotated = await capture('drag-orbit');
    assert.notEqual(rotated, side);
    await page.locator('#side-tab').click();
    await page.locator('#side-model-only').click();
    assert.equal(await page.locator('#side-model').evaluate(el => Number(el.style.opacity)), 1);
    await page.locator('#compare-tab').click();
    await page.locator('#reference-choice').selectOption('selected');
    await page.locator('#model-only').click();
    assert.equal(await page.locator('#model-image').evaluate(el => Number(el.style.opacity)), 1);
    assert.deepEqual(errors, []);
    const report={source_sha256:meta.sourceSha256,browser:browser.version(),gpu,errors,wood_fixed:front,wood_side:side,neutral_side:clay,orbit_drag:rotated,side_and_fixed_tabs_passed:true};
    fs.writeFileSync(path.join(output,'native-qa.json'),JSON.stringify(report,null,2)+'\n');
    console.log('PASS: Chromium compiled and drew the knight shader, changed material and preset, orbited, and switched comparison tabs.', gpu.renderer);
  } finally {
    await browser.close();
  }
}

main().catch(error => { console.error(error); process.exitCode=1; });
