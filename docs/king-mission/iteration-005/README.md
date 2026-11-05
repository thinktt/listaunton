# King checkpoint 005: isolate and reshape the lower base reflection

The lower shine is smaller and closer to the selected reference's position.
The previous broad vertical white wash is reduced. This is a modest lighting
refinement; the geometry, UVs, physical dimensions, framing, 54-degree camera
and every packed pigment pixel are unchanged from checkpoint 004.

## Accepted changes

Three diagonal glossy spot lights replace the three former lower-base lights.
Their centers are fitted through AgX using measured colored BSDF responses.
Local fine coat-relief strength is 0.02, fading in over profile rings 10–12
and out over 18–22. Base pigment, base-normal microrelief and the remaining
material graph are preserved. The old upper reflector retains its aim, power,
cone and color; the accepted foot lighting is retained.

The exact evaluated flare is split at profile ring 17 into lower-flare and
upper-flare receivers. Along with foot and upper-body, there are now four
derived render surfaces. They retain every evaluated face, UV, float attribute,
corner normal and shared material. The continuous closed body remains the
editable and exported geometry, plus the separate intersecting closed cross.
The upper reflector acts only on upper-flare; the new lower lights act only
on lower-flare. Other light routes retain their original surface coverage.
This is an artistic light-routing choice, not a recovered original studio rig.

## What the unsuccessful trials established

Trials 040–056 altered the foot/flare profile, verified reflected-ray visibility,
changed foot polish and tried larger area sources. They did not recover the
reference's broad grain-broken crescent. Their thin white knife edge was a
regression. None of those geometry or foot-light changes is in this checkpoint.

The later trials isolated a misplaced lower glint contributed by the old
upper-base reflector. Disabling only that light removed the patch. Suppressing
secondary glossy bounces did not: this was direct spill, unlike the recent
queen case. Narrowing the beam also weakened its desired upper glint. Exact
receiver separation kept the original upper beam while excluding the spill.
The accepted scene retains its original four glossy bounces.

The power fitter cannot remove an unwanted contribution held in its fixed
basis. Inspect isolated-light responses and the fixed response before changing
geometry or making more fitting passes. Small numerical loss reductions in
earlier trials were not accepted automatically. Every trial's five scores and
decision are in scores.json; contact sheets retain the actual rendered evidence.

## Assessment

| Metric | Checkpoint 004 | Checkpoint 005 |
| --- | ---: | ---: |
| High-res silhouette IoU | 97.820% | 97.820% |
| Interior form | 83% | 83% |
| Wood color | 82% | 82% |
| Grain and surface texture | 78% | 78% |
| Lighting and reflections | 58% | 60% |
| Equal-weight working mean | 79.764% | 80.164% |

Original-sprite IoU is unchanged at 96.833%. Only IoU is measured; other ratings
are subjective. The holistic range remains 73–82%. These values do not establish
a complete visual match. The original is authoritative; selected black 1 supplies
detail. Its pixels and registration remain unchanged.

In the declared lower-glint crop, the bright-pixel centroid moves from
(600.94,945.03) to(607.52,952.49), versus reference(606.62,952.82).
Thresholded bright area falls from 3772 to 1661 pixels; reference 2284. This confirms
better placement but also a remaining undersized reflection. Its diagonal shape
and grain breakup still differ. The threshold statistic is diagnostic, not a
replacement for the full image, crops, original overlay and other-angle review.

The foot crescent remains weak, narrow and low. The upper base glint remains
too small, and upper-body/cross reflections remain pale and regular. Cross
seating, shelf-like collars and cavity contrast still differ. Side and rear
inspection still reveal the strong orange-to-dark pigment transition into
inferred horizontal grain. The light-receiver boundary can make an illumination
cutoff visible in the clay diagnostic; exact-surface checks rule out a mesh seam.
It is a remaining lighting limitation, not a hidden geometry fix.

## Validation and reproduction

Run Blender with `--background --python-exit-code 1 --python
scripts/king/rebuild_checkpoint_005.py -- FRESH_LABEL`. It starts from the exact
archived 004 model and executes configs 067, 068, 069, 074 and 075 in a fresh build
directory. It never overwrites the accepted model or reference images.

The complete chain was executed. Reopened and reproduced beauty renders have
identical alpha and maximum channel difference 1/255. Reproduction mean foreground
RGB error is 0.000045/255. All packed pigment pixels are exact; the exported
mesh bytes are identical to 004. The source/control scope, material exception,
light settings/routes and exact derived surfaces passed validation. The model
still exports 70,364 triangles from two closed positive-volume components.

Keep the four-region split when regenerating after edits. Use
`render_regions.controls` and `regenerate`, then `validate_render_regions.check`.
New targeted reflectors should name `lower-flare` or `upper-flare` explicitly.
Use `check_base_light_checkpoint.py --lower-relief --split-flare` against 004
for this specific scope; the five-height foot validator describes checkpoint 004.
The separate regeneration check verifies preservation of all light routes.

The king review opens Reconstruction and embeds the same accepted fixed render,
closed mesh, pigment and registered side view. Browser lighting is approximate;
Cycles alone is used for the reference-lighting assessment. Page interactions
use the actual HTML's DOM/WebGL harness, not native browser screenshot inspection.
Repository and local preview interaction checks, site/model consistency, candidate
controls, whole-set defaults and historical projection preservation all pass.
All 32 king preview files were hash-verified. See checkpoint.json, checks/ and
preview-sync.json for the recorded results.

Next priority: repair the conspicuous hidden-surface wood transition while
preserving the selected-view pigment and fit. Then revisit the foot crescent
using isolated-light evidence before further geometry edits. Mission incomplete.
