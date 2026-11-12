# Bishop iteration 011 — finish studies, accepted model preserved

November 12, 2026. The owner resumed the mission and explicitly confirmed that
no pause was requested. The goal is active; this research checkpoint does not
pause or complete it. Checkpoint 010 remains the accepted model and public
review. No candidate in this study earns a replacement.

## What was examined

The socket crescent is too thin and glittery. Four unsaved material isolations
test whether its width is controlled by coat normals, relief strength or coat
roughness. Removing coat bump, reducing all relief, removing relief entirely,
and smoothing/roughening the coat do not recover the broad cream band.
Their socket errors are close to the control (8.09–8.22 versus 8.19 /255),
and the visible narrow strip remains. These are cropped diagnostics, not
whole-piece candidates or substitute beauty renders.

![Material isolations](finish-probe/comparison.png)

Four further unsaved tests enlarge the 17 existing socket emitters. Larger
sources soften the speckles without materially broadening the band. Increasing
the beam to 1.4 degrees creates an unwanted second arc above the socket and a
bright, uniform stripe. Its lower numerical crop error does not justify that
visible regression. No lights or material settings from these probes are kept.

![Emitter studies](emitter-probe/comparison.png)

The next tests address the surface pattern. The accepted material's color uses
the refined packed pigment atlas, but its pigment-related bump still reads the
earlier projected material. This difference is an observation about the shader,
not proof that simply sharing the color texture produces correct surface height.

Five full, saved-and-reopened 256-sample beauty renders explore that question:

- **089:** Reducing pore scale from 180 to 60 makes the finish smoother. The
  pore features grow, but their slopes weaken. Rejected.
- **090:** Compensating pore amplitude while preserving the pigment-height
  coefficient produces a coarse, pebbled finish and additional stray glints.
  Rejected.
- **091:** Using the accepted pigment atlas for pigment-related relief makes
  only a slight visual difference. There is no convincing overall improvement.
  Retained as research, not installed as the current model.
- **092:** Fourfold pigment-related height, with the fine-pore coefficient
  preserved, still does not reproduce the reference's varnish pattern. It also
  worsens the foot and socket. Rejected.
- **093:** Sixteenfold pigment-related height breaks up the base glint, but
  overemphasizes pigment markings as raised relief. The foot becomes visibly
  embossed, and the socket is less faithful. Rejected.

![Reference, accepted model, moderate and strong relief trials](finish-details.png)

The unchanged 54-degree camera, reference registration, source pixels, geometry,
UVs, lighting, pigment pixels and render paths are checked independently in the
saved material trials. Only their declared scalar inputs and shader link may
differ. The material-scope validator resolves Blender socket aliases to their
actual display names; the first audit of 090 exposed that naming issue, which
was fixed before rerunning the audit. No validation failure was ignored.

## Evaluation

The accepted scores stay **96.11 / 84 / 84 / 77 / 76**, with an equal-weight
mean of **83.42%** and a holistic estimate of **75–85%**. Only silhouette IoU
is measured. The remaining percentages are subjective working estimates.
`scores.json` assesses all five categories for each full candidate; the cropped
isolation renders are diagnostic probes and receive no whole-model score.

The shared-foreground RGB error is 7.72 /255 for the accepted image. It is
approximately 7.82, 8.05, 7.71, 7.77 and 8.28 for 089–093 respectively. The tiny
091 difference is insufficient evidence of an improvement, especially because
the screening renders use 256 samples versus the accepted render's 512.
The strong 093 trial increases foot error from 6.54 to 9.68. These numbers
describe registered images, not material fidelity percentages. The full metric
files and source hashes are preserved alongside the images.

The accepted silhouette and interior form are retained. Grain flow, small-scale
relief, collar/base reflections, slit-edge finish and the side/rear pigment
boundary remain visibly imperfect. No perfect-match claim is made.

Fresh head-side, full-profile and rear-oblique renders of 093 preserve the
geometry but expose the existing pigment boundary clearly. Stronger color-driven
relief is not a solution to that boundary. The files are in `trial-093/views`;
they are diagnostic camera views and do not modify the saved 54-degree camera.

## Continuation

Do not repeat these broad beam/roughness changes or promote a candidate merely
because one crop loss improves. Preserve checkpoint 010, now archived under
`history/bishop-mission-010`.

The next lighting study should inspect the actual surface-normal field around
the socket and the unwanted upper arc. A broader, genuinely confined reflection
may require an exact socket light receiver, with unchanged evaluated geometry,
normals and UVs, as used in the queen work. Such a change needs the bishop's
export and validation pipeline to distinguish editable controls from derived
receivers. Do not silently split the model or render stale derived geometry.

For texture, pigment intensity alone is not a reliable height map. Any further
relief study should separate broad color/illumination from fine grain and retain
the accepted color atlas. The side/rear pigment transition also remains a
separate, significant usability defect.

The canonical model, review pages and preview assets remain checkpoint 010;
there is no new accepted model to synchronize. Source selections, gallery
defaults, the queen and the other pieces are unchanged. No quota monitoring,
watchers, subagents, publishing or pushing is part of this iteration.
