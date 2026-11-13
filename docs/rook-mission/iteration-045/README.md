# Rook iteration 045

2026-11-12. Useful intermediate: restrict pigment shift to perimeter, preserve center grain; reflection remains too cool.

The original black sprite and selected candidate 8 both support a thin curved floor boundary. Pixel-to-surface probes traced the spurious orange stripe to atlas V approximately 0.863–0.879 and showed that the model normal transition lay above the desired reference glint. Separate depth, pigment, lighting and registration tests distinguish these effects. Reference authority and registration were not changed.

## Assessment

Selected/original filled-silhouette IoU 97.30350% / 95.67335% (measured); interior/color/grain/lighting 80/75/66/60 (subjective). Working mean 75.66%; holistic 60-70%. The silhouette score cannot measure the altered recess. Remaining issues include hard/uneven rim arcs, bright notch pigment artifacts, reddish lower patches, stretched inside-wall grain, visible side-neck seams and inferred unseen form. No perfect-match claim.

## Reproduction and validation scope

See parameters.json and build/rook-mission for saved trial inputs. Builders: deeper_floor.py (039–040), repair_floor_pigment.py (041), floor_reflection.py (042–043), register_floor_grain.py (044), floor_annulus.py (045–046), bake_floor_atlas.py (047). Use render_saved_trial.py in a fresh Blender process for saved-render validation. Probe 038 is read-only. Earlier trials are rejected or superseded intermediates, not separately certified deliveries.

All rendered candidates have fixed-frame audits and saved receiver coverage checks. Full intentional-edit validation covers 040, 046 and 047; it proves only control rows 53–58 move downward, the camera and control UVs remain exact, and all five construction components are closed and positive. Material validation covers 041 and 046. Dedicated 047 finish checks preserve all previous packed source images, Principled finish parameters and old light properties/receiver tags; only one warm floor-linked glossy strip is added. Final geometry has 31,000 evaluated faces and six render partitions, while the viewer exports the closed union.

The shader pigment bake excludes current scene lights and restores Principled shading afterward. Inherited illumination artifacts in source-derived pigment remain; this is not recovered physical albedo. New pigment atlas is required for the viewer. The final live-to-baked foreground mean RGB difference is 0.01004/255, with identical alpha; see iteration-047/bake-comparison.json.

An initial same-process UV check failed. A repeated failure in a fresh process was measured at 1.1920928955e-7 (two float steps, 0.000366 texel at 3072px). The explicit receiver UV bound was changed from 1e-7 to 2e-7 (below 0.000615 texel). Exact face positions/coverage, normal bound, camera and image registration checks were not relaxed. Logs and diagnostic retained. Do not infer from the first fresh-process pass that stale cache was proven to be the sole cause.
