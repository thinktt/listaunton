# Fifth queen mission checkpoint

The accepted change corrects regional wood color. The bowl is less orange,
the base and collars are slightly darker, and small channel adjustments bring
the socket, stem and foot closer to the reference. Geometry, the 54-degree
camera, UVs, relief and lights stay the same as checkpoint four.

The v4 atlas contains pigment only. It is baked using the existing UV layout
and rendered through the actual material and lights. The original images and
approved side-gallery proportions are unchanged. `reproduction.json` rebuilds
the material from the archived fourth model and tracked texture;
`063-reproduction-config.json` also records the pre-bake grading operation.

| Trial | Silhouette | Interior form | Color | Grain | Lighting | Working mean | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Fourth checkpoint | 97.961 | 80 | 75 | 77 | 59 | 77.79 | Baseline |
| 061 regional tones | 97.961 | 80 | 79 | 77 | 59 | 78.59 | Bowl too red; refine |
| 062 atlas relief | 97.961 | 80 | 75 | 77 | 58 | 77.59 | Reject |
| 063 refined tones | 97.961 | 80 | 80 | 77 | 59 | 78.79 | Accept after baking/checks |
| 064 smoother broad pigment | 97.961 | 80 | 75 | 77 | 59 | 77.79 | No convincing gain |
| 065 combined fine surface | 97.961 | 80 | 75 | 77 | 58 | 77.59 | Reject |
| 066 sharper varnish | 97.961 | 80 | 80 | 77 | 58 | 78.59 | Reject |
| 067 no relief | 97.961 | 80 | 80 | 74 | 54 | 77.19 | Diagnostic; reject |
| 068 v4 pigment bake | 97.961 | 80 | 80 | 77 | 59 | 78.79 | Delivery candidate |

Only silhouette overlap is a measured match percentage. Other scores are
consistent visual judgments; their mean is a working progress indicator.
Holistic assessment remains approximately 75–80%, visibly short of the
mission's indistinguishable-match criterion. Original-sprite overlap is
97.9109%; high-resolution overlap is 97.9612%, both unchanged.

Eight fixed non-highlight regional RGB medians agree within one byte level
per channel. This does not mean the full color field matches: broad tonal
variation and reflection placement remain wrong. The bake changes foreground
RGB by a mean 0.1391/255 relative to trial 063, with identical alpha.

Separate emission diagnostics reveal that coarse grain is largely in the
pigment, rather than being only a bump effect. Projection coverage is broad;
high-pass grain correlation in four sampled regions is 0.82–0.95, but fine
detail softens and coarse prior patterns remain. The diagnostic emission
images are not model beauty renders and are not exposed in public controls.

Remaining defects include elongated finial highlights, weak thin reflections
around the crown and collars, an incomplete socket crescent, coarse or overly
contrasty grain in places, and collar/socket curvature that differs from the
reference. Side views retain stretched inferred grain and an over-polished
socket. The next iteration should address these specific mismatches rather
than increasing scores because diagnostics look numerically favorable.

Validation and hashes are recorded in the adjacent JSON reports. Native
browser GPU inspection was unavailable; simulated DOM/WebGL interaction
checks are identified as such. The browser uses the saved mesh, camera and
atlas with approximate real-time lighting, while the fixed images use Cycles.

Weekly allowance at 2026-11-05 11:39:57 UTC was 18% used / 82% remaining,
resetting 2026-11-11 13:19:47 UTC. Luna continues the five-minute guard. The
mission remains active and incomplete.
