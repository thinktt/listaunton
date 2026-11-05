# First bishop boxwood checkpoint — 2026-11-05

The former clay model now has a real boxwood material, a pigment-only texture
atlas, procedural wood on unseen and cut surfaces, fine relief and varnish,
and a physical studio light rig. The model is still editable, including its
full-depth Boolean slit. The camera remains the identical 54° orthographic
camera. The selected reference, both originals and registration are unchanged.

## Assessment

| Category | Initial clay | This checkpoint |
| --- | ---: | ---: |
| Outside silhouette and placement (selected IoU) | 94.88% | 94.88% |
| Interior geometry and carved details | 78% | 78% |
| Wood color and tonal variation | 0% | 70% |
| Grain pattern and surface texture | 0% | 64% |
| Lighting and reflections | 30% | 54% |
| Equal-weight working mean | 40.58% | **72.18%** |

The separate original-white IoU is **96.5827%**, and original-black IoU is
**95.9639%**. Only silhouette is measured; the other scores are visual judgments.
Holistic full-material resemblance is roughly **65–75%**. This is a first
material checkpoint, far from the mission's completion criteria.

Warm color, distinctive forked base markings, curved growth bands and small
flecks are now present. The button has two actual reflected glints. The slit
interior remains wood instead of becoming a black texture void. The view from
the side and the rear remains a real volumetric object with continuous fallback
wood; those views were rendered and inspected separately.

Remaining defects:

- The button is a little narrow/low. The head/slit termination and collar
  curves still differ. The base and foot need flatter, more precise profiles.
- The wood is too uniform and orange in places, with insufficient dark/light
  variation across the collar and socket. The original white sprite is warmer
  and blurrier than the chosen candidate; the candidate is not a recovered map.
- Fine grain is too coarse and marbled, and some pale streaks are invented.
  Surface relief and the transition to hidden procedural wood still need work.
- Reflections are too clean and plastic-like. The head streak, collar/socket
  crescents, base glint and foot highlights have the wrong breadth or location.
  The side-view stem reflection is too long. Some fitted collar reflectors are
  below the base plane, a sign that geometry and illumination remain unresolved.
- Opposite-color checks establish only shared geometry. A black finish has
  not been reconstructed by this checkpoint.

## Trials and decisions

`trials.json`, seven configs and the contact sheet retain all five scores for
every material/light trial. Trial 001 established wood. Trial 002 was too broadly
lit; 003 reduced spill but over-strong relief scattered glints; 004 sharpened the
finish. Trial 005 washed the color toward pink/tan and was rejected. Trial 006
used narrow area-light spread, which increased normalized energy and caused
blown highlights; it was rejected. Trial 007 balances fine relief with two
button glints and is the chosen appearance.

The first atlas exposed two integration defects, fixed before acceptance:

1. Boolean cut faces had degenerate lathe UVs and rendered black. Their own
   procedural boxwood material now handles all 400 cut polygons. The viewer
   marks these faces explicitly and uses a matching approximate wood color.
2. End-cap UVs extended outside the atlas. Four dedicated cap islands now
   keep all outer UVs inside the image, including the underside and button cap.

The corrected source is baked and rendered after reopening the saved blend.
The atlas contains pigment only, with no illumination baked into the beauty
render. Material outputs are Principled BSDFs. The inferred pigment source,
exact built-in image-generation prompt, and hashes are in
`assets/bishop/pigment-generation.json`; the original reference was never edited.

## Verification and provenance

- Two closed, positive-volume components; no nonmanifold edges. The continuous
  head and direct button contact pass the existing anatomy and junction checks.
- Control vertices and triangle indices are exactly unchanged. Blender's
  evaluated coordinates differ by at most 0.000002384 model units from the
  initial file, a subpixel numerical difference after adding UV data. The
  validator uses a documented 0.000005-unit tolerance rather than byte hashes.
  Height and base diameter remain exactly unchanged.
- The saved/reopened packed atlas agrees with the disk image pixel-for-pixel.
  A reproduction of the first corrected bake differed by only 0.000081 of an
  8-bit RGB level on average; the later cap layout was also baked, reopened,
  rendered and checked by the corrected pipeline.
- The evaluated viewer has 133,120 triangles and exact exported pigment UVs.
  Its camera/control harness tests references, tabs, rotation, pan, zoom, reset,
  embedded texture hashes and parent-message checks. The maximum measured
  camera error is below 0.00001 pixel. This is a DOM/WebGL harness, not a native
  browser visual inspection. Browser lighting remains approximate.
- Side and rear renders use the accepted model. Fixed wood/clay renders,
  comparison crops, Blender file and viewer are synchronized. The prior clay
  file and render remain in `history/bishop-mission-000`.
- The side gallery retains exactly the same heights, widths, defaults and
  order. Only its bishop mesh metadata/binary provenance hashes are refreshed.

See the machine-readable validation, score, metric and reproduction files in
this directory. Checkpoint source SHA and atlas SHA are recorded there rather
than conflating a low pixel loss with visual completion.

## Next hypothesis

Use the now-readable finish to refine geometry at the fixed registration:
measure the button and base against both originals and the selected candidate,
then test a small button-width/height adjustment and a flatter base/foot profile
in separate trials. Preserve the accepted deep slit and gap-free head/button
contact. Keep this first wood checkpoint until a candidate improves the fit.
