# Rook 036 — rejected rim reflection study

2026-11-12. 4500W exaggerates notch-end streaks and produces excessively hard arcs. Rejected.

Original control geometry, evaluated surface, fixed orthographic 54-degree camera, material/pigment and original light properties are unchanged. Targets were selected from actual bevel corner normals near reference highlight pixels; reflectors are real glossy-only area lights. The implied studio arrangement is an artistic fit, not recovered historical metadata. Candidate 037 partitions the existing rim receiver, without moving faces, so added lights affect only upper rounded bevels.

## Scores and unresolved defects

Selected/original silhouette 97.30350% / 95.67335% (measured with unchanged masks). Interior/color/grain/lighting 78/74/66/54 (subjective); equal-weight mean 73.86%; holistic 60–70%. Filled silhouettes do not establish cavity fidelity. Missing recessed-floor glint, too-hard/uneven rim reflections, baked orange floor-edge stripe, reddish lower patches, stretched inside-wall pigment and severe side-neck texture transitions remain. No claim of perfect match.

## Evidence and scope

Fixed-frame comparisons and saved models exist for every trial. Full saved geometry/material/camera/receiver validation covers 037; its dedicated light validator checks packed image bytes, shader nodes/links, world, original lights and new receiver links. Earlier trials are rejected experiments, not independently certified deliveries. 035–037 were reopened before rendering; 031–034 were saved then rendered in the same process. Accepted 037 was staged and reopened again for fixed/profile/rear renders, exact closed-mesh export and viewer checks. Browser lighting remains approximate; the automated viewer harness is not native GPU browser visual QA.

See parameters.json for reproduction inputs and source hashes. Scripts are measured_rim.py (031–032), upper_bevel_rim.py (033–034), rim_strength.py (035–036) and rim_bevel_only.py (037). Checkpoint 025 is archived in history/rook-mission-025. The normal probe is iteration-030. All reference images and owner-approved proportions remain unchanged.
