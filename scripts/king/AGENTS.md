# King reconstruction pipeline

Read the root AGENTS.md, MISSION-KING.md and latest docs/king-mission-log.md.
The current accepted scene has two closed editable controls and four exact
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
paused after this checkpoint; do not restart the mission without a resume.
