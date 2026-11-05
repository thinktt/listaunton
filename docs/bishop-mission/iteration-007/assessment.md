# Bishop iteration 007 — a localized reflection at the slit tip

Starting checkpoint: `953d3a9`, preserved in `history/bishop-mission-006`.
The original white Lichess bishop remains authoritative; ungraded white
candidate 3 is the selected detail reference. This is a small lighting
improvement at the unchanged 54-degree orthographic camera.

## Examination and change

Both the selected image and the original white sprite have a small cream
reflection where the slit ends. The previous model has a dark rounded
termination without that glint. A new glossy-only spot light places a small
reflection on the actual head surface. It uses the existing body receiver;
the button does not receive it. Its position was guided by measured surface
normals, followed by a small positional correction against the actual render.

The original lights, environment, geometry, UVs, pigment, relief, material
nodes, dimensions and camera are preserved. Exported positions, normals and
indices are exact; evaluated UV interpolation differs by at most 0.0000000596
(less than 0.00013 texel in the atlas), while control UVs remain exact.
This is a real Principled-BSDF render, with no
reference photograph or composited highlight substituted for the surface.
The invented lighting arrangement is an artistic reconstruction, not a
recovery of the original scene.

## Trials and limitations

Small area lights initially produced attractive low-sample previews, but their
brightness and extent changed drastically as sampling increased. Those trials
were rejected. Their fitted powers and diagnostic predictions are not reliable
accepted lighting measurements. The useful failure is preserved in the
convergence evidence rather than offered as a public model alternative.

A point spot kept the reflection localized but was too broad and speckled.
Moving the source closer narrowed its footprint; a small source radius softened
it. A power adjustment restored the cream center, and a 0.0115-unit horizontal
translation corrected the observed leftward bias. The final configuration uses
an explicit one-degree spot angle. Blender had clamped the earlier requested
0.6-degree angle to one degree; effective values are now recorded and checked.

The final full image uses **512 fixed samples**, compared with checkpoint 006's
96-sample adaptive image. A separate 512-sample render of the unchanged baseline
isolates the actual light change. In that equal-quality comparison:

- Mean RGB error in the 555-pixel tip region decreases from **20.68 to 16.40 /255**.
- Error on the reference's 25 brightest core pixels decreases from
  **67.71 to 19.71 /255**.
- The shared foreground error changes only slightly: **7.498 to 7.491 /255**.
- Outside the tip context, mean absolute change is **0.137 /255**, with a
  99th-percentile channel change of **2 /255**. This includes sampling noise.

The glint remains localized at 512 and 2,048 fixed samples. It is not perfectly
converged: mean tip-region difference between those renders is 4.11 /255,
with a 99th-percentile channel difference of 63 /255 from fine highlight noise.
The reference error is 16.49 and 16.82 /255 respectively in those cropped
checks. This supports the local improvement, not an exact or noise-free match.
The final reopened full render is the accepted image; response predictions
and cropped renders do not replace it.

| Actual full-render trial | Silhouette | Interior | Color | Texture | Lighting | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 047–049 area-light attempts | about 96.20 | 83 | 85 | 77 | 72 | Rejected after sample dependence became apparent. |
| 052 distant point spot | about 96.20 | 83 | 85 | 77 | 73 | Local improvement, but too broad and speckled. |
| 053 closer soft spot | about 96.20 | 83 | 85 | 77 | 73 | More confined, but the core remains too dim. |
| 055 brighter soft spot | about 96.20 | 83 | 85 | 77 | 73 | Brighter core with a small leftward bias. |
| 056, finalized as 057 | 96.20 | 83 | 85 | 77 | 73 | Retained after alignment, full render and validation. |

Response-only fits 045, 046, 050 and 051 are diagnostics, not fully assessed
model candidates. They receive no invented whole-piece scores.

A separate pigment trial (054) measured the original projection confidence
and extended the surrounding color field. Its rear diagnostic still showed
the conspicuous patch boundary. It was rejected before full fixed-view
assessment, and the accepted atlas remains unchanged. Another hidden-only
fill is unlikely to solve shading already embedded inside protected pigment.

## Accepted scorecard

| Metric | Previous | Current |
| --- | ---: | ---: |
| Outside silhouette and placement | 96.20 | 96.20 |
| Interior shapes and carved details | 83 | 83 |
| Wood color and tonal variation | 85 | 85 |
| Grain pattern and surface texture | 77 | 77 |
| Lighting and reflections | 72 | 73 |
| Equal-weight working mean | 82.64 | 82.84 |

Only silhouette is measured IoU. Other scores are subjective visual estimates;
the mean is a progress indicator, not a probability of fidelity. Holistic
fixed-view appearance remains approximately **75–85%**. This small missing
reflection earns a modest lighting increase, not a claim that the overall
material is finished.

Selected-reference IoU is **96.1987%**, original-white IoU **97.8785%**, and
original-black IoU **96.7523%**. Tiny differences from checkpoint 006 arise
with render sampling; the evaluated positions and normals are unchanged, with
only the negligible UV rounding described above. Filled silhouette masks do
not assess the slit reflection.

## Validation and review delivery

The scene is saved, reopened and rendered at 1254 × 1254 with Standard sRGB.
Packed pigment pixels match the unchanged atlas exactly. A dedicated scope
audit compares the archived source against the final saved model and checks
the one declared added light, including its receiver, angle and source radius.
The existing anatomy, closed-mesh, rounded-cut, button-contact, fixed-camera,
UV and provenance checks remain required. The slit validator now records
properties appropriate to area and spot lights; its geometry checks are intact.

Neutral, level, rear and full-profile renders, exact viewer mesh and both bishop
pages are refreshed from this same checkpoint. The main page opens the
reference overlay and retains the rotation and candidate tabs. The canonical
repository and the owner's existing local preview are synchronized before the
checkpoint commit. Actual check results and hashes are in `checkpoint.json`.
UI validation uses the simulated DOM/WebGL harness; native browser inspection
is not claimed. Browser lighting remains approximate, while the overlay shows
the actual Cycles render.

## Remaining work

The glint is still too simple, the cut is too uniform in tone, and the head's
fine reflected grain differs. Collar and foot reflections remain narrower and
more golden than the cream reference. The socket has a stray bright line; the
base reflection is too compact. The rear pigment boundary remains conspicuous.

The next material hypothesis must address residual shading inside the visible
pigment, rather than applying another protected hidden-only fill. Test a
continuous broad pigment field with preserved fine grain and refit illumination
in an isolated trial; reject it if the fixed original/reference match regresses
materially. Preserve this checkpoint while pursuing that larger improvement.
The mission remains incomplete. Other pieces and gallery defaults are unchanged.
