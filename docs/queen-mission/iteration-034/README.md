# Socket study and shape-phase completion audit

November 12, 2026. The accepted model remains **checkpoint 33**, commit
`3980e37`, SHA-256
`243844939937d0b753df253810f0e60d67b86a664f14b86dd678e7e22d348a68`.
No new geometry, material or lighting is promoted in this iteration.

## Socket investigation

The source comparison places the model's brightest central socket band about
8 pixels below the original black image on the 1254-pixel canvas. The overall
median difference along the sampled crescent is only 2 pixels. These are
highlight observations, not recovered geometric edges: both grain and the
reflection rig affect which pixel is brightest. The original-white and selected
high-res images were also examined without changing their pixels or registration.

Two isolated interpretations lower the inner socket seat by 0.032 and 0.050
units. They broaden and flatten the shelf while leaving its outer wall, the
flare and foot unchanged. Coupled radius/height edits preserve the projected
front meridian at 54 degrees. Both actual neutral renders have exactly the
same exterior alpha mask as the diagnostic baseline. Nevertheless, the
stronger version looks too square and the moderate version loses the rounded
lip and much of the reference crescent in the existing wood/light rig.

Both are **rejected**. A good silhouette score does not validate the interior.
The real-wood trial is `269-flatter-socket-wood`; its five-category assessment
is recorded in [scores.json](scores.json). Neutral-only proposals do not receive
invented material scores. The actual wood render was made at 64 samples;
the accepted checkpoint's delivered renders remain at 256.

![Socket shelf bracket](neutral-shelf-comparison.png)

![Same sources and unchanged wood/light rig](socket-wood-comparison.png)

The remaining crescent discrepancy is retained as a finishing issue. This
test does not prove that every conceivable alternative socket is wrong, or
that the historical geometry/camera have been uniquely recovered. It does
show that the tested additional flattening is a worse explanation than the
accepted rounded shelf and steep drop.

## Completion audit against the existing mission

This audit uses the mission's **shape-phase** completion criteria, which
explicitly defer complete texture and lighting matching. The criteria have
not been changed. The phase comparison below starts at its documented
checkpoint-22 source; the goal resumed from checkpoint 24, where the collar
changes had already been accepted. These are cumulative results, not changes
all made in this final iteration.

![Whole-phase side comparison at equal physical scale](phase-audit/phase-side-before-after.png)

![Original-view comparison at unchanged registration](phase-audit/phase-fixed-comparison.png)

| Requirement | Authoritative evidence and assessment |
| --- | --- |
| Lower/shorter socket with its shelf and steep drop intact | Direct reads of the archived and current Blender controls show seat height 1.309390 → 1.230826, wall height 0.250000 → 0.235000, and wall radius 0.564500 → 0.529500. The shelf remains a separate rounded shoulder above a near-vertical wall. Fresh neutral side/fixed renders and both original colors show the construction. **Met.** |
| Lower collar rounded on both faces instead of a flaring shelf | The accepted bead rolls from radius 0.54 at both edges to 0.6744 at its crest. The equal-scale phase image visibly removes the former flared lower face. Checkpoint 31 also reduces the stem-to-bead join gap from 0.11530 to 0.03030. **Met.** |
| Smaller, thinner upper collar with closely stacked collars | Peak radius 0.481 → 0.452 (6.0% smaller); height 0.150 → 0.080 (46.7% thinner). The three-ring stack is retained and the upper ring reads as a fine turned line in the fresh profile. These are the accepted checkpoint-24 collars, preserved by the subsequent edits. **Met.** |
| Compact whole foot/flare/socket, with moderate and strong alternatives tested | The selected whole assembly is 6% shallower; the inner flare radius grows 0.680 → 0.727392 (7.0%), with the foot grounded. Checkpoint 33 replaces the extra lower inflection with one rounded turn. Checkpoint 31 records actual 6/10/16% trials and a wood render of the 10% case; checkpoint 32 records further arc-constrained compression and raised/broader shoulder proposals. More aggressive versions fail the original's socket relationship. The selected compact result visibly improves the side while retaining the source fit. **Met.** |
| Original image governs disputes; generated references remain supporting evidence | The stronger flattening and lower-camera proposals were rejected despite some generated-image gains. Black/white originals, selected high-res, imagined side and neutral renders were inspected. Source hashes and registration remain exact. **Met.** |
| Convincing original-view match, with numerical and visual before/after evidence | Final original IoU 97.7787%, selected high-res IoU 97.9770%. Across the entire phase the original loses 0.1404 percentage points from checkpoint 22, explicitly traded for the requested side form. The new independent neutral comparison agrees within sampling variation. No separate model registration or reference warping. **Met.** |
| Fixed 54° reference camera and preserved distinctive crown/egg | Actual saved camera is orthographic 54.0000007°. The direct phase audit proves identical camera matrix and scale and exact crown/bowl controls 86–107. Eight tips, flattened rim intervals and inverted bowl remain; the separately accepted compact egg is seated within them. **Met.** |
| Approved cross-piece proportions and other pieces preserved | The 83.4% queen/king gallery default and all reference selections retain their recorded hashes. No other piece's model or page changes. Current queen height/base ratio is 2.102978; the phase's small egg/foot changes are documented, not hidden by rescaling the gallery. **Met.** |
| Actual saved geometry, UVs, normals, receivers and material validated | Current-hash finish/model reports verify finite declared controls, closed positive-volume mesh, exact evaluated faces/UVs, six receivers, custom normals and 82 light links. The additional direct checkpoint-22-to-33 preservation check proves the material graph, packed image bytes, all 85 lights, camera and transform unchanged. **Met.** |
| Overlay, orbit model, side renders and download agree | Checkpoint-33 source hashes are embedded in the viewer and side metadata; camera regression error <0.000039 pixels. The review, site and model checks pass, and native-browser testing confirmed rendering, side/neutral controls and dragging. The repository and existing Windows preview were synchronized at acceptance and their current hashes are rechecked by this audit. **Met.** |
| Iteration evidence, scores, best-result preservation and commits | Each accepted checkpoint is archived and committed. This final study records the rejected variants without replacing the best model or adding public alternatives. All five current scores are retained. No push, watcher or subagent is used. **Met.** |

The direct measurements and read-only assertions are in
[phase-measurements.json](phase-audit/phase-measurements.json),
[phase material/light preservation](phase-audit/profile-preservation.json),
and the final [delivery audit](completion-checks.json). The finish/model and
camera reports under `../iteration-033/` contain the accepted SHA-256.

The final delivery guard found that iteration 33's separate shape-scope
report described the pre-publication trial file (`5d00bbee…`), although its
finish/model and viewer reports described the accepted download. The shape
validator was rerun against the exact current `24384493…` Blender file; its
new report is [current-side-shape-validation.json](current-side-shape-validation.json).
The older report is retained as trial history, not relabeled as a current-file
check.

## Inspiration inspection

The existing study's actual photographs were opened and examined in the
native browser. The [German Knight queens](https://nl.chess-chivalry.com/cdn/shop/products/German-knight-queen-acacia-final.webp?v=1668756899&width=1946)
show a broad uninterrupted base slope, restrained lower rounding and a lower
collar curved on both faces. The [Chavet lineup](https://images.chesscomfiles.com/uploads/v1/images_users/tiny_mce/Walterbiensur/phpLW3HUH.jpg)
shows fine upper collar lines, a compact base and a low queen finial. Their
differences are retained as differences; neither is treated as the actual
Lichess source. No claim of documented design ancestry is made.

## Final scorecard and limits

The accepted scores stay **97.7787 / 90 / 85 / 79 / 76**, with working mean
**85.5557%** and holistic range **80–85%**. Only the silhouette is a measured
percentage; the other categories are visual assessments. There is no increase
for merely completing an audit or rejecting a trial.

The four requested shape changes have been tested, rendered, compared and
delivered, so this shape-focused mission is complete. The full visual-match
project remains unfinished: socket/crown reflections, grain/relief and regional
color still differ. White finish has not been matched. Browser lighting remains
an approximation of Cycles, and the viewer displays the editable control mesh
while Cycles renders its subdivision surface. Unknown side geometry and the
54-degree historical camera remain interpretations.

## Reproduction

`audit_shape_phase.py` reads the two Blender files without saving either:

```sh
blender -b --python scripts/queen/audit_shape_phase.py -- --before history/queen-mission-022/queen-rebuilt.blend --after models/queen/queen-rebuilt.blend --output build/queen-mission/shape-phase-audit
blender -b --python scripts/queen/render_neutral_shape_studies.py -- --source history/queen-mission-022/queen-rebuilt.blend --manifest docs/queen-mission/iteration-034/phase-before-manifest.json --variant baseline --output build/queen-mission/shape-phase-before
blender -b --python scripts/queen/render_neutral_shape_studies.py -- --source models/queen/queen-rebuilt.blend --manifest docs/queen-mission/iteration-034/socket-shelf-studies.json --output build/queen-mission/socket-shelf-studies
```

The guarded compact-turning builder can reproduce trial 269 using
`267-flatter-socket-seat-032.json` and source hash `24384493…`. Do not promote
it; the rejection above is visual, not a topology failure. Supporting Python
scripts, source controls, render snapshots and reports are kept alongside this
document. They use NumPy, SciPy and Pillow and do not modify source references.
