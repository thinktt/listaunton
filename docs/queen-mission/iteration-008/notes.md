# Eighth queen mission iteration — in progress

Repository starting commit: `0390d4b`; accepted model remains the sixth
checkpoint, SHA-256
`82100ad9047426b1be46e72d01d769189b4e9f667005fd8c8bcc5d743c16526e`.
Fixed 54-degree camera, v4 pigment, original references and approved side
proportions remain unchanged.

At 2026-11-05 13:08:41 UTC, Luna reports weekly 22% used / 78% remaining,
reset 2026-11-11 13:19:47 UTC. Five-minute monitoring continues.

## 082: render-region equivalence

The first linked-lighting hypothesis requires separate receiver objects.
Before changing lights, partition a temporary evaluated copy into ten turned
regions, retaining every face, original position, UV layer and smooth corner
normal. Keep the closed editable control mesh unchanged, hidden only from
the test render. All accepted lights remain global in this diagnostic.

The actual 64-sample beauty render has identical alpha to the accepted image.
Foreground RGB mean absolute difference is **0.00357016/255**, 95th percentile
zero, maximum six. No seam or shape change is visible. Scores remain
97.9612 / 80 / 80 / 77 / 61, working mean 79.1922%. This is a technique
validation, not a new accepted model. A separate emission pass provides
region IDs for fitting; it is never used as a beauty image or viewer texture.

## 083: linked reflectors — rejected

Fit each region's reflected-light response separately, using the measured
distant-direction responses and previous area/spot responses. The fixed world
is already included in the fresh diffuse baseline and is excluded from the
regional emitter list. Each fitted emitter is a real Cycles light linked to
one receiver region. Diffuse lights remain global. The cached linear response
only guides the solve; actual light-linked rendering decides acceptance.

This is artistic light linking, not a claim about the original studio. It
retains the actual three-dimensional surface and wood BSDF. A successful
result will require side-view inspection and explicit integration/validation
of the editable-control/render-receiver distinction before any promotion.
The current public model, images, viewer and preview remain untouched.

The first implementation created a receiver collection per light and exceeded
Blender's 64-collection limit. That invalid render was not scored. Receivers
now share ten regional collections, verified before the valid rerender.

083 strengthens some collar/socket edges but adds a gray sheen across the
base and body. Scores: 97.9612 / 80 / 74 / 75 / 58, mean 76.9922%; reject.
084 restricts path depth to direct lighting. It changes too little to resolve
the sheen and receives the same scores. Both retain the accepted silhouette
IoUs exactly. Indirect reflections alone are not the explanation.

## Measurement checks and 085 — rejected

A black-BSDF single-light diagnostic confirms receiver isolation: a light
linked only to the finial gives zero signal on the foot, base, socket, stem
and collars, while some finial light reaches the bowl through reflection.
The masked fitting prediction differs from the actual render by roughly
2–11 RGB levels depending on region, with the crown body especially affected.

Capture all 322 current linked lights separately with the full colored wood
material, preserving their actual links and colors. Their total mean scene
linear energy agrees with an all-lights render within about 0.2%, but 64-sample
pixel errors are large. Increasing the small all-lights diagnostic to 4096
samples reduces mean linear disagreement from 0.05228 to 0.01276. Sampling
noise matters, but the high-sample image still has the wrong sheen.

085 fits the 88 measured area/spot responses, excluding distant emitters and
using the full RGB Jacobian through AgX. Render at 256 samples with adaptive
sampling disabled. Despite a simpler rig and a more faithful response model,
the actual image retains unwanted crown-body glints, weak collar crescents,
and a pale base. Scores: 97.9604 / 80 / 77 / 76 / 59, mean 77.9921%; reject.
Tiny silhouette changes are anti-aliasing/sample differences; geometry is
unchanged. Its original IoU is 97.9117%, versus accepted 97.9109%.

## 086–087: finial-only exclusion — in progress

Return to the sixth checkpoint's exact lights and powers. Restrict only their
finial reception: 086 allows the intended finial areas and spots; 087 allows
only the three finial spots. All other surfaces retain the accepted lighting.
This smaller experiment tests the already measured spill without substituting
a new whole-piece fitted rig.

At 2026-11-05 13:28:58 UTC, Luna reports weekly 22% used / 78% remaining,
reset 2026-11-11 13:19:48 UTC. The mission remains active and incomplete.


086 reduces the long finial streak, scoring 97.9612 / 80 / 80 / 77 / 63,
mean 79.5922%. 087 excludes the remaining area-reflector spill and retains
three more compact glints: lighting 64, mean 79.7922%. Other categories are
unchanged. The finial grain and the upper two glint shapes still differ from
the reference. This is a modest improvement, not a complete lighting match.

## 088: minimal receivers � accepted

Rebuild the selected lighting from the archived sixth model using only two
receivers, turned body and finial, instead of ten. All original light powers,
closed control geometry, UVs, pigment, relief and camera remain unchanged.
Foreground difference against 087 is 0.001747/255, p95 zero, maximum five;
alpha is identical. The distinction is implementation simplicity, not a new
visual score. Keep 97.9612 / 80 / 80 / 77 / 64, mean 79.7922%.

The receiver validator confirms exact evaluated surface faces and atlas UVs,
715,776 triangles, shared wood material and intended links. Maximum custom
normal component error is 0.00003234. The editable control remains closed
and manifold with eight crown tips and the accepted height/base ratio.
Side wood and clay renders show no new geometry or material regression.
A fresh build from the sixth checkpoint is compared with the trial, and the
four delivered views are regenerated from the accepted saved scene.

The delivered model SHA-256 is
`c32bccbf33e5e137d982bdeafd881a783b006f62e644dbd5db2df57d02801004`.
References and approved side-gallery defaults are unchanged. Current/best
scores remain provisional visual estimates except measured silhouette IoU.
Native browser GPU inspection is unavailable; DOM/WebGL harness checks are
reported separately from actual Blender renders.

At 2026-11-05 13:51:43 UTC Luna reports 23% used / 77% remaining, reset
2026-11-11 13:19:48 UTC. Continue five-minute monitoring. Next isolate the
coarse relief that makes bowl and rim grain look etched; the original atlas
still drives relief even though color uses v4.
