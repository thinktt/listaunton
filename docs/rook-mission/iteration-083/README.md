# Foot reflection studies 079–083

Checkpoint 078 remains accepted and public. All four rendered alternatives are rejected for promotion. The goal remains unfinished.

## Evidence and judgment

079 measured the reference foot crescent: its center is dimmer, right flank brighter, and its fine glint is broken by surface detail. The accepted broad strip over-brightens the center and under-lights the right.

080 replaces the foot strip with measured left/right area lights at 25/100 W. 081 uses 50/200 W. Both use 0.75 by 0.14 area lights. They restore the dim center but over-brighten the left and leave the right too dim. 082 uses 10/400 W: closer asymmetric brightness but an excessively broad, smooth right patch. 083 narrows the light height to 0.04 and uses 3/115 W (approximately preserving radiance). It does not recover the thin irregular reference glint. These results do not establish that further lighting fitting cannot help; they rule out accepting these particular power/size settings.

Full fixed-frame and foot crops were inspected; 083 also has saved-model fixed/profile/rear views. Its side view remains a real shaded object, with inherited pigment illumination and broad foot bands still evident. Geometry, wood color and grain are unchanged, and no general fidelity increase is awarded. All five category ratings are recorded for each trial. Camera stays orthographic 54 degrees; owner proportions and source pixels remain unchanged.

## Validation and reproduction

Run foot_flanks.py for 080/081, foot_flanks_refined.py for 082, and foot_flanks_narrow.py for 083 with Blender background Python. Each requires the exact accepted 078 source SHA and writes isolated build/rook-mission directories. Render through render_saved_trial.py; compare with compare_foot_flanks.py and audit_mission.py. render_trial_views.py produces 083 side views without saving the camera changes.

Full saved geometry/material/receiver and lighting-scope validation covers 081, 082 and 083; 080 has saved receiver validation and the same guarded builder. The checks verify real Principled materials, packed image preservation, unchanged control/evaluated geometry, source hashes, camera and original light rig apart from disabling the foot strip and adding two linked glossy area lights. They do not certify visual fidelity. This batch has no new neutral render because the validated geometry and material are unchanged; accepted checkpoint 078 neutral evidence remains applicable. Public viewer/site assets are unchanged, so no public delivery rebuild is claimed.

Next: isolate foot roughness and bump response under the better asymmetric lighting, checking highlight width and fine breakup. Preserve the reference color/grain and do not alter the geometry merely to compensate for material/lighting differences. Current accepted model SHA: bfc8e7c5aca140363d67c379532f57412e0bac8206c0bd617591e0e993d94914.
