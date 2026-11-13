# Rook iteration 029: rim strip study — rejected

2026-11-12. Started from accepted checkpoint 025 at the unchanged orthographic 54-degree camera. Added one 300W glossy-only rectangular area source, 6 by 0.12 units, linked only to the existing rim receiver. Position and exact source/model hashes are in parameters.json. Saved and reopened the scene before rendering on NVIDIA OptiX at 64 samples.

Overhead strip gives no meaningful improvement to the missing rim highlights. The baked orange band above the floor remains conspicuous.

The physical interior geometry, pigment and lower lighting are unchanged. Shaft/base defects persist: reddish compensation patches, side-neck transitions, stretched inside-wall grain and weak lower crescents. No public model, viewer, reference, camera or gallery setting was replaced.

## Assessment

Selected silhouette 97.30350%; original 95.67335% (measured). Interior 78, color 74, grain 66, lighting 53 (subjective). Equal-weight working mean 73.66%; holistic 60-70%. Filled masks do not measure cavity or rim fidelity. Unseen form remains inferred.

## Validation scope

All three trials were reopened and rendered; fixed-frame audits cover each render. Full saved geometry, UV, packed material, camera and receiver validation is run on representative 027 only. Trials 028 and 029 use the same script, changing only light position; they are rejected without promotion, not certified deliverables. No browser or side-view acceptance check was performed because these fixed-view failures already disqualify them.

Reproduce with scripts/rook/rim_strip_study.py (guarded checkpoint-025 hash), then scripts/rook/audit_mission.py 029-rim-strip. Build models remain isolated under ignored build/rook-mission.

Next: inspect actual rim bevel shape and shading normals. Broad top-surface reflection is possible, but the tested source directions do not form the desired thin arcs. This does not by itself prove a geometry defect.
