# Rook 037 — accepted rim reflection study

2026-11-12. Two 1500W strips restricted to rounded upper bevels strengthen the thin rim arcs while removing the unwanted vertical notch-end streaks. Accepted incremental lighting improvement; recessed-floor arc remains missing.

Original control geometry, evaluated surface, fixed orthographic 54-degree camera, material/pigment and original light properties are unchanged. Targets were selected from actual bevel corner normals near reference highlight pixels; reflectors are real glossy-only area lights. The implied studio arrangement is an artistic fit, not recovered historical metadata. Candidate 037 partitions the existing rim receiver, without moving faces, so added lights affect only upper rounded bevels.

## Scores and unresolved defects

Selected/original silhouette 97.30350% / 95.67335% (measured with unchanged masks). Interior/color/grain/lighting 78/74/66/57 (subjective); equal-weight mean 74.46%; holistic 60–70%. Filled silhouettes do not establish cavity fidelity. Missing recessed-floor glint, too-hard/uneven rim reflections, baked orange floor-edge stripe, reddish lower patches, stretched inside-wall pigment and severe side-neck texture transitions remain. No claim of perfect match.

## Evidence and scope

Fixed-frame comparisons and saved models exist for every trial. Full saved geometry/material/camera/receiver validation covers 037; its dedicated light validator checks packed image bytes, shader nodes/links, world, original lights and new receiver links. Earlier trials are rejected experiments, not independently certified deliveries. 035–037 were reopened before rendering; 031–034 were saved then rendered in the same process. Accepted 037 was staged and reopened again for fixed/profile/rear renders, exact closed-mesh export and viewer checks. Browser lighting remains approximate; the automated viewer harness is not native GPU browser visual QA.

See parameters.json for reproduction inputs and source hashes. Scripts are measured_rim.py (031–032), upper_bevel_rim.py (033–034), rim_strength.py (035–036) and rim_bevel_only.py (037). Checkpoint 025 is archived in history/rook-mission-025. The normal probe is iteration-030. All reference images and owner-approved proportions remain unchanged.

Neutral diagnostic confirms unchanged form independently of pigment. Surface partition validation covers all 30,832 faces exactly once across five receivers. Maximum custom-normal component deviation is 0.0004726648 and Boolean UV interpolation deviation is 5.96e-8; neither is claimed byte-exact. Closed-viewer export still has 62,522 triangles; corner deduplication count changes slightly with Boolean UV float rounding. Automated public site and viewer checks pass; source and preview hashes match.
