# Bishop geometry checkpoint 018

The prior goal turn made progress: checkpoint 017 corrected the shoulder,
stem and upper collar, and exposed neutral comparison in the review. This
iteration continues the same geometry goal without changing any mission.

The head-to-collar outline had an outward bulge where both the original white
and selected enlargement show an inward turn. An initial upper-collar-only
hypothesis produced no improvement: its one-parameter optimizer chose zero.
Actual first-hit surface rays identified the offending surface as the **middle
collar behind the head**, near control ring 54. Image position had suggested the
wrong anatomical part.

The accepted change narrows the middle collar by up to 1.275 original profile
units and lowers it by a coupled amount. The combination holds
`axis_y + radius * sin(54 degrees)` fixed along the front meridian. Only controls
49–56 change, with tapered weights at either end. The front surface stays in
place while the rear edge moves down behind the head. This is actual geometry,
not a changed camera, reference scale, pixel warp or pigment correction.

The first-hit mesh measurements confirm that the middle collar's front extent
moves less than 0.05 native comparison pixel (0.04694 measured). In image rows
325–447, the mean absolute edge discrepancy against the original falls from 2.992 to 1.585 pixels;
the maximum falls from 12 to 5. Original-white silhouette overlap increases
from 98.590% to about 98.694%, and selected-white-3 overlap from 96.814% to about
96.897%. `surface-evidence.json` and `comparison/metrics.json` hold exact values.
These measurements are local placement and outline evidence, not a percentage
of recovered 3D truth.

The direct level view retains a smooth, stacked collar form. The button, head,
slit, upper/lower collars, stem, socket, base and foot controls are unchanged.
The source is archived as `history/bishop-mission-017`; checkpoint 015 also
remains available. Overall bounds, owner-approved gallery proportions and the
saved orthographic 54-degree camera are unchanged.

A separate ray-projected slit mask labels the actual visible cut interior,
independent of material and lighting. It follows the selected reference much
more closely than the dark/glossy appearance initially suggested. The slit
therefore remains unchanged in this pass. Its last interior pixel in the
diagnostic crop is at row 428; the photographic edge is blurred and includes a
bright rim. A dark-pixel threshold would not be an equivalent physical boundary.
The opposite-color image is retained as a clue, not used to override the white
original's visible cut placement.

Working ratings are **96.90 / 87 / 83 / 77 / 72**, mean about **83.18%**, holistic
appearance **75–85%**. Only silhouette is measured; other ratings are subjective.
The local shape improvement raises the interior rating by one point. The wood
atlas, UV controls, materials, relief and lights remain inherited and unfinished.
Color, grain and lighting scores do not improve merely because geometry improved.
The retained atlas still contains photographic shading and visible side/rear
transitions. The validator now labels its old albedo metadata flag explicitly
as metadata, not evidence that the material is free of illumination.

The final 512-sample render comes from the saved and reopened file. Independent
scope checks validate every declared control and preserve all others, including
the button/cutter. Geometry, camera, lights, shader graph and packed pixels agree
with the checked 128-sample trial. Derived receiver UV hashes vary by ordinary
evaluated floating-point rounding; independent receiver checks remain within the
existing 1e-7 tolerance. This is not treated as a free pass for other differences.
The current anatomy, mesh/export, slit, button-contact and interaction checks
all pass. Fixed wood/neutral images, rotating mesh and level/rear views are
rebuilt together. No native browser visual QA is claimed.

The geometry goal is still incomplete. Remaining examination includes the
socket lip-to-stem transition, lower-collar underside, and the small button and
foot outline differences. Some residuals may be source sampling or generated
reference differences, but that needs evidence, not assumption. Preserve the
original as authority when the generated enlargement conflicts. No other piece,
source pixels, registration, shared gallery, mission or quota monitor is changed.
