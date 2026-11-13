# Rook shoulder reflection trial 078

Accepted: 650W per flank matches sampled side peaks and dimmer center more closely.

Geometry, camera and pigment are unchanged from checkpoint 072. Trials 073–075 alter only broad shoulder-strip height/power. Trials 076–078 disable that strip and add two real white rectangular area lights aimed along measured reflection directions at the shoulder flanks. New sources are glossy-only, shadowed and linked only to the existing shoulder receiver. These are artistic studio lights, not recovered historical lighting. No emission or reference compositing replaces shading.

Saved scenes were reopened for rendering. All have receiver validation and fixed-frame mask audits. Full geometry/material preservation is representative for 073 and 077 and repeated for accepted 078. Exact shader/packed-image/world/light scope validators cover those same trials. The five-category scores separate measured overlap from subjective ratings; lighting changes do not earn geometry or pigment score gains. Profile measurements are sampled evidence, not proof of a full match. Remaining highlights, cavity contrast and inherited pigment illumination are unresolved.

Reproduce shoulder_width.py for 073–075, shoulder_flanks.py for 076–077, or shoulder_flanks_refined.py for 078 against archived checkpoint 072. Then render_saved_trial.py -- 078-shoulder-flanks, audit_mission.py, and the corresponding compare_shoulder script. Use an absolute --baseline path to the archive with material and lighting validators after promotion. Earlier trials are not public alternatives.

## Accepted delivery

Two .75 by .14 unit area lights, 650W each, replace the old broad strip (retained but disabled). At x400/x560 their peak rows match reference y882/y888, with mean-RGB peaks 244/247 versus 251.7/248. At x483 the trial peak is 103 at y899 versus reference 105.7 at y898. Width and surrounding falloff remain imperfect. Full fixed, profile/rear and neutral views were examined. Exact material/light scope, closed mesh/normal/UV export, fixed 54-degree camera and six receiver coverage checks pass. Staged render rounding is measured in delivery-check.json. All source pixels and registration are preserved.

Fixed/profile/rear, exported mesh, root viewer and Windows preview are synchronized from the saved model. Viewer tests use mock GL; they are not native-browser GPU visual QA. Rotating-viewer lighting remains approximate. No push or publication; the full mission remains active.
