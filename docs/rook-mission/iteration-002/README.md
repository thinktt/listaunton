# Rook material study 002 — 2026-11-12

Reference-informed pigment restores recognisable floor fibers and exterior grain. Broad softbox reflections still wash out the right cavity. Low-confidence strips revert to the unrelated procedural material, especially the shaft and right rear merlon. Some target glints may remain weakly represented in pigment despite the confidence mask; this cannot be counted as a recovered highlight. Side view exposes material transitions and stretched detail. Reject for promotion.

## Comparison and scores

Fixed orthographic 54-degree camera; full-resolution 1254-square render. Both source colors and selected black candidate 8 are preserved. The canonical accepted model is still the original neutral model, SHA `23abce50f4a7bd6544f7844534e69a02e3a337a64ee7ce214e81acc353a26f2c`. No public page or model has been replaced.

Selected IoU: 97.30350%; original IoU: 95.67335%. These use max reference RGB >12 and alpha >127, largest component, holes filled; model alpha >127. This consistently establishes a new mission baseline: accepted neutral selected IoU 97.30484%, original 95.67668%. The older README used a different unfilled mask. Its figures remain historical and must not be interpreted as model improvement. Tiny trial/neutral differences are antialiasing/sampling, not geometry changes.

Visual judgments: interior form 78%, color 68%, grain/surface 53%, lighting 28%. Equal-weight working mean 64.86%; holistic range 55–65%. Scores are subjective except measured overlap; none proves exact reconstruction. The neutral baseline's material categories were effectively absent.

## What was verified

Saved trial was reopened before the actual shaded render. Exact evaluated positions and triangle indices, positive closed component volumes, object visibility/transforms, reference camera and dimensions match the accepted model. Both float texture images are finite and packed. The material output connects to Principled BSDF with zero emission. Source image hashes match. No rendering from a composite photograph substitutes for the model. The diagnostic side camera is not saved.

The pigment estimate inverts the scene's black/white BSDF response through AgX, then bounds it with reliability, alpha and highlight masks. A fixed object-space affine projection attaches it to real geometry; actual lights/BSDF create reflections. The invisible/grazing regions blend to procedural wood. This is an approximate one-view inverse problem, not recovery of unique historical albedo. Some residual lighting contamination and projection stretching remain; the side images demonstrate the limitations.

## Reproduction and next action

Run scripts/rook/wood_trial.py to prepare isolated 001. Then run scripts/rook/inverse_pigment_trial.py. Run scripts/rook/validate_material_trial.py -- 002-inverse-pigment in Blender and scripts/rook/audit_mission.py 002-inverse-pigment with Pillow/NumPy. All paths are rooted in the repository and outputs remain under build/rook-mission. The scripts use the existing king GPU/material helper without modifying king assets.

Next: improve texture continuity into unseen/grazing surfaces and eliminate sharp confidence boundaries, then fit the narrow reflected crescents. Bake pigment alone to portable UVs and validate a reopened beauty/side comparison before any accepted model, viewer and local-preview update. Keep the exact editable construction. No changes to static missions, gallery proportions, source registration or other pieces.
