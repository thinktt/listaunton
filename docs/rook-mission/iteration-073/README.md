# Rook shoulder reflection trial 073

Rejected: wider strip brightens the already excessive center.

Geometry, camera and pigment are unchanged from checkpoint 072. Trials 073–075 alter only broad shoulder-strip height/power. Trials 076–078 disable that strip and add two real white rectangular area lights aimed along measured reflection directions at the shoulder flanks. New sources are glossy-only, shadowed and linked only to the existing shoulder receiver. These are artistic studio lights, not recovered historical lighting. No emission or reference compositing replaces shading.

Saved scenes were reopened for rendering. All have receiver validation and fixed-frame mask audits. Full geometry/material preservation is representative for 073 and 077 and repeated for accepted 078. Exact shader/packed-image/world/light scope validators cover those same trials. The five-category scores separate measured overlap from subjective ratings; lighting changes do not earn geometry or pigment score gains. Profile measurements are sampled evidence, not proof of a full match. Remaining highlights, cavity contrast and inherited pigment illumination are unresolved.

Reproduce shoulder_width.py for 073–075, shoulder_flanks.py for 076–077, or shoulder_flanks_refined.py for 078 against archived checkpoint 072. Then render_saved_trial.py -- 073-shoulder-width, audit_mission.py, and the corresponding compare_shoulder script. Use an absolute --baseline path to the archive with material and lighting validators after promotion. Earlier trials are not public alternatives.
