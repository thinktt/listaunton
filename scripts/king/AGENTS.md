# King reconstruction pipeline

Read the root AGENTS.md, MISSION-KING.md and latest docs/king-mission-log.md.
The current accepted scene has two closed editable controls and three exact
derived body light receivers. Select editable meshes with
`render_regions.controls(scene)`, not by visibility. The body is intentionally
hidden from final rendering. Export the closed controls; do not export the
open derived receivers as replacement geometry.

After changing control geometry, UVs or float attributes, call
`render_regions.regenerate(scene)`. Use `assign_material` when a diagnostic
material must affect both a control and its receivers. Validate all receiver
faces, UVs, attributes, normals, shared material and light routes using
`validate_render_regions.check`. Current procedures and scoped geometry checks
are in docs/king-mission/iteration-004. Historical builders must not overwrite
the accepted model. At accepted checkpoints regenerate all king review assets,
sync the existing local preview, run relevant checks and commit as authorized.
