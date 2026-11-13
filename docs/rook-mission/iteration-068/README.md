# Rook neck trial 068: rejected

Hidden-only edit does not remove the front neck arc.

Nearby lower-neck grain is shifted upward 369 atlas pixels, darkened by 0.65 in encoded RGB, and feathered into the neck. The mask excludes every triangle classified reference-visible, with erosion and feathering. This is inferred wood, not recovered unseen texture. No geometry, camera or light edits. Actual real-material fixed/profile/rear renders are saved; model files are hash-checked unchanged during rendering.

Representative full geometry/camera/material/receiver validations cover 068 and 070; 070 also has exact shader-input/link, light and UV checks. Every trial has a fresh saved-file render, fixed mask audit and side views. The alpha/silhouette stays unchanged. Scores retain unchanged interior and lighting categories, and explicitly account for the fixed-view color tradeoff against side-grain improvement. Original source pixels and registration remain untouched. Neutral geometry remains the validated checkpoint-066 geometry; no new neutral render was required for this pigment-only rejected/intermediate study.

Reproduce neck_visibility.py, repair_hidden_neck.py, apply_hidden_neck.py, then render_trial_views.py -- 068-neck-wood and audit_mission.py 068-neck-wood --render build/rook-mission/068-neck-wood/render.png. Use compare_neck_trials.py for side and fixed-difference evidence. Start from the pinned accepted checkpoint 066.

No public assets changed. Next tone prediction is 0.56309 from the measured .65/.85 response; it is only a least-squares display-space prediction and must be rendered. The full mission remains incomplete.
