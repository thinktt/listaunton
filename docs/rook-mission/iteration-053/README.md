# Rook trial 053: rejected local color correction

Strong pink desaturation is markedly less faithful. Accepted checkpoint 047 and all public assets are unchanged.

The saved scene was reopened and rendered headlessly with NVIDIA OptiX at the unchanged orthographic 54-degree camera. The shader changes Base Color only: smooth atlas-V mask between control rows 15 and 32, U below .76, no coordinate resampling. Trials 048-050 clamp linear-RGB HSV hue to .018/.026/.034. Trials 051-053 retain hue floor .018 and cap saturation at .94/.88/.82. Maximum RGB value is preserved; this does **not** preserve perceptual luminance. Neither method separates inherited illumination from pigment.

Full and shoulder comparisons and fixed-frame audits are included. Geometry/material/camera validation is representative: iteration 048 for hue and iteration 052 for saturation; every saved render has its own exact-position receiver coverage validation. No new side/viewer export was promoted. Existing side seams remain unresolved, and this experiment provides no evidence they improved. Unchanged geometry does not prove unseen form is recovered.

Scores in scores.json use measured silhouette overlap and subjective remaining categories. Interior/grain/lighting scores stay unchanged; color changes reflect visible tradeoffs, not merely regional pixel loss. The montage in the scratch workspace stretches crops for diagnosis; full-comparison.png preserves aspect ratio and is the presentation evidence.

Reproduce with scripts/rook/lower_chroma.py against the pinned checkpoint-047 model, then render_saved_trial.py -- 053-lower-chroma, and audit_mission.py 053-lower-chroma. The builders create all three isolated variants in their family. Do not replace the accepted model with these trials.

Next: identify the spatial extent of baked reddish/dark compensation bands and repair only contaminated pigment while preserving fine grain; avoid broad hue/saturation clamps.
