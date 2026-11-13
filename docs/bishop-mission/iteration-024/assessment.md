# Bishop checkpoint 024 — narrow the stem without adding a lower bulge

The accepted edit narrows only mid-stem radii **34–36**. Every control height
and every other radius remains exact from checkpoint 022. The root controls,
socket, base, foot, collars, head, button and slit are retained. Overall bounds,
saved orthographic 54-degree camera, source registration, material, atlas, UVs
and lights are unchanged. The editable model hash is
`2ac4f898f5c5a8b6f69edec478e8d380d23c4c3021122697b0a2973878a2b425`.

## What changed the interpretation

Actual first-hit contour probes show that the elevated outline below the
collars switches from the stem to the rear base. Treating the whole region as
stem in study 023 produced an unwanted lower-stem bulge. The new fit keeps
lower-stem controls 31–33 unchanged and narrows the middle conservatively.
Subdivision blends the edited surface into its neighboring controls; unchanged
control values do not mean every immediately adjacent evaluated point is exact.

A rotational-envelope calculation was independently tested against the actual
mesh before interpreting source slopes. Median radius and axis-coordinate
errors are about 0.042 and 0.068 original profile units on the tested continuous
segments. Source estimates around the blurred stem/base transition are unstable,
especially in the black sprite, and are not treated as precise dimensions.
The useful result is identifying which surface generates an edge, not claiming
to recover hidden geometry from a single image.

Two bounded stem/shoulder trials were rendered and inspected. The stronger
supported stem adjustment was chosen. A fitted rear-shoulder radius change of
only about 0.058 original profile units was omitted from the final model:
its projected effect is subpixel and does not justify changing that surface.
The final radii are approximately 18.50725, 16.86655 and 16.21114, reductions
of 1.08768, 0.48945 and 0.10877 original profile units respectively.

## Actual comparisons and tradeoffs

Against the registered original white, average edge error across the exposed
stem rows 592–615 falls from **3.646 to 1.229 pixels** in the 1254px comparison.
The crossover rows 616–635 worsen slightly, from **2.375 to 2.625 pixels**;
the rear-base region stays at 2.106 pixels. The first sampled base-generated
contour appears at row 624.5 instead of 626.5 because the narrowed stem reveals
it earlier. The base itself has not moved. This is a two-pixel sampling result,
not an exact recovered source transition.

Fixed wood/neutral crops and common-camera level views support the slimmer
taper. The pronounced lower swelling of rejected trial 176 is absent. Measured
radius increases monotonically from the actual waist toward the socket; the
maximum taper angle is about 16.58 degrees, between the previous 13.07 and
rejected trial's 19.68 degrees. Those angles describe the change, not a pass
threshold or proof of an original manufacturing profile.

Final outline IoUs are **98.7742% original white**, **97.0347% selected white 3**
and **97.8272% original black**, modest improvements over checkpoint 022.
The stable mask convention and unchanged registration are recorded with the
comparison outputs. Outline agreement still does not establish interior fit.

## Assessment across the mission metrics

- **Silhouette/placement:** the exposed stem is closer; the small crossover
  tradeoff remains. No global scale or camera compensation was used.
- **Interior form:** this is a supported local taper correction. Keep the
  broad subjective estimate at 82 rather than implying a whole-piece jump.
  Collar surface curvature, apparent head fullness and base transitions still
  need examination independently of photographic shading.
- **Wood color:** the inherited color remains uneven relative to the selected
  honey-colored reference. No color improvement is claimed; working score 83.
- **Grain/texture:** the atlas retains photographic shading and mismatched
  placement in places, including the turned bands. Working score remains 77.
- **Lighting:** finial highlights, socket reflection and base glints still
  differ from the selected image. Working score remains 72.

The five working scores are about **97.03 / 82 / 83 / 77 / 72**, mean 82.21,
with holistic resemblance still estimated around 70–80%. Only silhouette is
measured. Other percentages are subjective, uncertain working assessments.
This checkpoint does not resolve the owner's entire apparent-fullness concern
and does not complete the geometry or material/lighting mission.

## Validation and delivery

The final model was saved, reopened and rendered at 512 fixed samples, with
a separate neutral render. Independent scope validation proves the declared
three-radius edit, exact untouched controls, topology, UVs, cutter, packed
pigment, lights and saved camera. Actual anatomy checks pass for both closed
components, the full-depth open slit, solid floor and broad direct button/head
contact. The historical exposed-neck regression remains absent.

Both exact render receivers were regenerated and checked against evaluated
controls, including positions, normals, material slots and UVs. Export,
head/side/rear views, fixed wood/neutral images and both bishop pages were
rebuilt from the same saved model. Viewer and review runtime checks pass.
Native browser QA is not claimed. Checkpoint 022 remains the rollback source;
study 023 remains rejected evidence. Mission files, originals, registration,
candidate choices, other pieces and gallery defaults are preserved.

The geometry goal stays active. Continue feature-by-feature surface comparison;
do not hide remaining geometry questions with new pigment or reflector fitting.
No quota monitoring, subagents, push or external publication was used.
