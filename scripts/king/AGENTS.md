# King reconstruction pipeline

Read the root AGENTS.md, MISSION-KING.md and latest docs/king-mission-log.md.
The current accepted scene has two closed editable controls and nine exact
derived body light receivers. Select editable meshes with
`render_regions.controls(scene)`, not by visibility. The body is intentionally
hidden from final rendering. Export the closed controls; do not export the
open derived receivers as replacement geometry.

After changing control geometry, UVs or float attributes, call
`render_regions.regenerate(scene)`. Use `assign_material` when a diagnostic
material must affect both a control and its receivers. Validate all receiver
faces, UVs, attributes, normals, shared material and light routes using
`validate_render_regions.check`. Current procedures and scoped geometry checks
are in docs/king-mission/iteration-005. Historical builders must not overwrite
the accepted model. At accepted checkpoints regenerate all king review assets,
sync the existing local preview, run relevant checks and commit as authorized.

Checkpoint 005 retains 004 closed geometry and pigment. Its exact flare receivers split at profile ring 17; `regenerate` preserves `king_split_flare`. Target `lower-flare` or `upper-flare` explicitly in new lights. Do not restore rejected foot edits or the zero-glossy-bounce diagnostic. Rebuild with `rebuild_checkpoint_005.py`; validate scope with `check_base_light_checkpoint.py --lower-relief --split-flare`. The viewer mesh remains byte-identical to 004; the accepted changes are local coat relief and lighting.

Checkpoint 006 retains the 005 geometry, UVs, relief, lighting and receiver split,
and uses king-pigment-atlas-v6.png. Inferred unlit wood completes hidden and
grazing surfaces; the central front and cross atlas are retained. Reproduce with
complete_hidden_pigment.py and iteration-006/reproduction-config.json; validate
scope with check_hidden_checkpoint.py. Temporary completion UVs/attributes are
removed before saving. Viewer mesh bytes remain identical to 005. The owner
paused after this checkpoint and resumed the king mission on 2026-11-12.


Checkpoint 007 changes foot profile controls 4–11, adds a local `Foot shoulder
satin` finish mask and a fitted area reflector. The camera, physical bounds,
v6 pigment and earlier material remain checked by `check_foot_shoulder.py`.
Reproduce from archived 006 with `rebuild_foot_checkpoint.py` and
`docs/king-mission/iteration-007/reproduction.json`. Preserve the four receiver
regions and regenerate after edits. The current source is the accepted seventh
model. Its review and local preview are synchronized. The whole-set test has a
documented pre-existing knight sizing metadata failure; keep that distinction
when reporting validation. Read the mission log for active status and next work.


Checkpoint 009 retains 007 geometry, material, packed images and fixed camera.
It splits socket from upper-body at interpolated profile ring 28, for five exact
receivers. `regenerate` preserves `king_split_socket` and existing routes.
`king_socket_broad_excluded` records that Front/Upper varnish omit the socket;
four `Socket ` glossy spotlights supply its local glints with shadows enabled.
Export the unchanged closed controls, never the open receivers. Reproduce
with socket_reflection_trial.py and iteration-009/reproduction.json from
archived 007. Check scope using check_socket_checkpoint.py; keep the exact
surface/UV/attribute/normal and light-route validators. The earlier four-region
pipeline remains supported. Read the mission log for remaining defects.


Checkpoint 010 retains 009 geometry, UVs, all float attributes, v6 material,
camera and old light settings. A sixth exact receiver isolates mean profile
ring [26.55, 27.25) for two new `Socket seam ` glossy area lights. Preserve
`king_split_socket_seam` and `king_socket_seam_lights_confined` during
regeneration. The four earlier `Socket ` lights cover socket plus socket-seam;
the two seam sources cover only socket-seam. Export the closed controls.
Reproduce with socket_seam_trial.py and iteration-010/reproduction.json from
archived 009; verify scope with check_socket_seam_checkpoint.py. The rejected
pigment and local-polish trials are not part of the accepted material. Keep
fixed/side/viewer assets synchronized and read the log for remaining defects.


Checkpoint 011 retains 010 closed geometry, all attributes, v6 material and 54°
camera. Nine exact receivers now include lower/middle/upper collars using
COLLAR_RANGES in render_regions.py: [34.5,45.5), [45.5,53.5), [53.5,61.5).
Preserve king_split_collars and king_collar_broad_excluded during regeneration.
Front/Upper varnish omit collars; each new Collar source links only to its named
collar. All accepted sources retain shadows; the middle-left source fits to zero.
Reproduce from archived 010 with collar_reflection_trial.py and
iteration-011/reproduction.json; validate with check_collar_checkpoint.py.
Always use a fresh saved-file beauty after fitting: this study records a tiny
transient socket-glint mismatch and a passing independent fresh reproduction.
Keep the original failed checks as evidence. Do not promote rejected close-light
or shadow-omission trials. Export closed controls and synchronize all review
assets before another accepted iteration; consult the mission log for status.


Checkpoint 012 changes only profile controls 45–50 and the two existing middle
collar area lights. The full evaluated lathe section has no detected crossings;
the previous hidden collar overlap is repaired. Reproduce with
refine_collar_turning.py and iteration-012/reproduction.json from archived 011.
Validate using check_collar_turning.py and diagnose_full_profile.py, preserving
all nine receiver regions and current light routing. v6 pigment/material, all UVs
and float attributes, physical bounds and the 54-degree camera remain unchanged.
Use render_fixed_diagnostics.py --beauty-only for the canonical saved-file image;
its repeat and independent rebuild agree within 1/255. Alternate renderer entry
points can change a tiny socket glint; this remains a documented limitation.
Fixed 256 samples and removing denoising did not fix it and are not accepted.
Keep the accepted 128 adaptive/denoised settings and synchronize all king views.
The rejected color repairs and over-bright light fits must not become current.


Checkpoint 013 changes only heights of controls 58–60 by +.010, +.007 and
+.003, plus the two existing upper-collar area lights. Every radius, the 012
middle join, other controls, material/packed pixels, UVs and attributes,
physical bounds and 54-degree camera are preserved. Reproduce with
refine_collar_turning.py and iteration-013/reproduction.json from archived 012.
verify_collar_candidate.py runs scoped checks, receiver regeneration, saved
views, export and independent reconstruction before publication. Preserve all
nine receivers and routes; never promote the rejected brighter or larger-curve
tests. Use the canonical fresh renderer and synchronize fixed, side and viewer
assets. Read the mission log for current limitations and next work.


Checkpoint 014 preserves 013 geometry, all original UVs/attributes, packed v6
pigment and lights. `Collar varnish texture 014` changes only Fine varnish relief
strength to .60, fading over rings 34–37 and 60–63; cross values are zero.
Keep this model-space field and regenerate all nine receivers after edits.
Reproduce with local_finish_trial.py and iteration-014/reproduction.json from
archived 013. check_local_finish.py validates the exact scope; the finish
verification helper reopens, exports and independently reconstructs candidates.
The canonical repeat exposed the old tiny socket-glint instability again.
use_light_tree=False now restores the tested repeat/independent agreement within
1/255. Retain 128 adaptive/denoised samples, the explicit sampling toggle and
fixed 54-degree camera. The failed tree-enabled checks remain in iteration-014;
do not promote rejected pigment, roughness or stronger-relief experiments.
Synchronize fixed, side and viewer assets, and consult the mission log before work.

Checkpoint 016 fits the king's lower turning to the accepted queen and uses
a continuously flared Chavet-style head with one cross seat. Reproduce using
turn_chavet_profile.py and docs/king-mission/iteration-016/reproduction.json.
Preserve king_free_receiver_normals during regeneration. On Blender 5.2 it
stores the evaluated control's exact corner vectors in the receiver meshes.
The archived earlier checkpoints use their original encoding. Validate with
validate_chavet_profile.py, the receiver regeneration check and the full profile
intersection check before updating fixed, side, rotating and set views.

Checkpoint 017 uses all of queen 033's base loops plus a stem support with
the king's original angular resolution. Reproduce from archived king 016 with
match_queen_base.py and docs/king-mission/iteration-017/reproduction.json.
On this cage King profile ring is a logical, fractional coordinate. Use that
attribute to locate anatomical features. Regeneration preserves it when
king_mapped_profile_rings is set. Keep the Queen base varnish 017 field and
the four lower-region reflector routes. Validate the donor match and scope
with validate_queen_base.py as well as the standard export and receiver checks.
