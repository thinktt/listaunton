# Rook local pigment trial 057: rejected

Wider neighborhood still leaves sharp contaminated band edges and brightens the lower patch.

Small Gaussian UV masks cover the three measured defects. The repair adds a local difference between an 8px blur and a 100px surrounding blur, keeping original fine detail before clipping. Both low-frequency illumination contamination and genuine pigment can be altered: this is an artistic repair, not recovered albedo. Pixels outside the masks are byte-identical. Source atlas and accepted model are hash-pinned. No geometry, camera or light changes. The source-derived blue-channel clipping and hard band boundaries remain unresolved.

Saved scenes reopened and rendered with NVIDIA OptiX. Every trial has a saved receiver coverage check and fixed-reference audit. Full saved geometry/camera/material validation is representative in iteration-055. Full and shoulder comparisons are recorded; no new side export or public viewer was promoted. Existing side seams remain unresolved. Scores separately report measured overlap and subjective categories; lighting setup and interior form are unchanged. Grain ratings decrease where visible smoothing/gray halos damage the result. Whole-image fidelity remains incomplete.

Reproduce with scripts/rook/repair_local_pigment_wide.py using the pinned atlas, then apply_local_pigment_wide.py using accepted checkpoint 047, then render_saved_trial.py -- 057-local-pigment and audit_mission.py 057-local-pigment. Each builder creates two variants. The probe in iteration-054 supplies actual defect UV positions.

Accepted checkpoint 047, review, mesh and side images remain unchanged. Next separate the upper-patch brightness defect from lower-patch chroma contamination and preserve edge detail explicitly; broader blur alone is insufficient.
