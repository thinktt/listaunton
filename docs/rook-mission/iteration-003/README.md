# Rook material study 003 — 2026-11-12

Making existing softboxes diffuse-only and adding three smaller real glossy sources removes the broad milky cavity reflection. Floor color and grain improve substantially; shaft coverage is more coherent. The small sources still create misplaced lower/central glints and fail to form the reference's bright thin rim, shoulder and foot crescents. Fallback grain transitions remain conspicuous in profile; rim-edge registration exposes the underlying shape mismatch. Keep as the best experimental starting point, not an accepted/public checkpoint.

## Comparison and scores

Fixed orthographic 54-degree camera; full-resolution 1254-square render. Both source colors and selected black candidate 8 are preserved. The canonical accepted model is still the original neutral model, SHA `23abce50f4a7bd6544f7844534e69a02e3a337a64ee7ce214e81acc353a26f2c`. No public page or model has been replaced.

Selected IoU: 97.30350%; original IoU: 95.67335%. These use max reference RGB >12 and alpha >127, largest component, holes filled; model alpha >127. This consistently establishes a new mission baseline: accepted neutral selected IoU 97.30484%, original 95.67668%. The older README used a different unfilled mask. Its figures remain historical and must not be interpreted as model improvement. Tiny trial/neutral differences are antialiasing/sampling, not geometry changes.

Visual judgments: interior form 78%, color 76%, grain/surface 64%, lighting 41%. Equal-weight working mean 71.26%; holistic range 60–70%. Scores are subjective except measured overlap; none proves exact reconstruction. The neutral baseline's material categories were effectively absent.

## What was verified

Saved trial was reopened before the actual shaded render. Exact evaluated positions and triangle indices, positive closed component volumes, object visibility/transforms, reference camera and dimensions match the accepted model. Both float texture images are finite and packed. The material output connects to Principled BSDF with zero emission. Source image hashes match. No rendering from a composite photograph substitutes for the model. The diagnostic side camera is not saved.

The pigment estimate inverts the scene's black/white BSDF response through AgX, then bounds it with reliability, alpha and highlight masks. A fixed object-space affine projection attaches it to real geometry; actual lights/BSDF create reflections. The invisible/grazing regions blend to procedural wood. This is an approximate one-view inverse problem, not recovery of unique historical albedo. Some residual lighting contamination and projection stretching remain; the side images demonstrate the limitations.

## Reproduction and next action

Run scripts/rook/wood_trial.py to prepare isolated 001. Then run scripts/rook/inverse_pigment_trial.py -- --separate-lights. Run scripts/rook/validate_material_trial.py -- 003-separated-light-pigment in Blender and scripts/rook/audit_mission.py 003-separated-light-pigment with Pillow/NumPy. All paths are rooted in the repository and outputs remain under build/rook-mission. The scripts use the existing king GPU/material helper without modifying king assets.

Next: improve texture continuity into unseen/grazing surfaces and eliminate sharp confidence boundaries, then fit the narrow reflected crescents. Bake pigment alone to portable UVs and validate a reopened beauty/side comparison before any accepted model, viewer and local-preview update. Keep the exact editable construction. No changes to static missions, gallery proportions, source registration or other pieces.
