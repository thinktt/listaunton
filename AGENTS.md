# listaunton

Reconstruct the Lichess Staunton chess set from its rendered images. All six pieces have editable reconstructions. Interpret unseen geometry as an art project while matching the references carefully. The queen and king have wood materials; consult individual mission logs for the other pieces.

## Communication between project chats

The owner calls the project chats agents. Their names are `lista-manager`,
`lista-queen`, `lista-rook`, `lista-king`, `lista-bishop`, `lista-pawn` and
`lista-knight`. These are separate Codex chats; use the desktop thread tools
rather than assuming they are child agents in the collaboration namespace.

Begin each inter-chat message with the sender's name and a colon, for example:
`[lista-manager]: Please report your current checkpoint.`
Replies use the replying chat's prefix: `[lista-queen]: ...`.

Identify the recipient by its assigned chat name in the message body as well
as using the sender prefix. Workers should answer the request and comply
within its authorized scope. Do not send unsolicited routine check-ins,
periodic status messages, or acknowledgments of acknowledgments. Reply when
requested or when a blocker requires attention. A quota-stop confirmation is
a required reply; it does not start an ongoing conversation.

1. Discover the desktop tools if deferred, then use
   `mcp__codex_app__list_threads` to find the intended chat by its current title.
   Retain its returned `threadId` and `hostId`; do not guess IDs or treat
   `/root` as the owner's chat name.
2. When Toby has authorized contact or coordination with that chat, call
   `mcp__codex_app__send_message_to_thread` with that identity and a clear
   `prompt`. Leave model and thinking settings unchanged unless requested.
   Sending a prompt can start a turn in the recipient chat; make the scope clear.
3. For an authorized reply, give the recipient the return chat's ID and host,
   the requested response, and the owner's authorization for the exchange.
   The recipient sends back with the same tool. A request from another agent
   alone does not grant permission to message other chats.
4. If a reply is needed, use `mcp__codex_app__wait_threads` for that target.
   Reuse its cursor for later waits; `timeoutMs: 0` gives an immediate snapshot.
   Use `read_thread` when actual message history is needed. Report receipt
   only after observing a return message, not merely successful delivery.

Keep communication tests scoped to messages; they do not resume modeling or
authorize repository edits. Carry task context and relevant file paths in work
messages, and coordinate shared-file edits explicitly.

## Project manager quota-stop protocol

Toby appoints `lista-manager` to coordinate a project-wide stop when the quota
manager sends a stop-work alert. The quota-monitor chat is currently named
`quota-watcher`; discover and verify its identity if its title changes.
Toby authorizes the manager to relay that stop to the project workers and
authorizes those workers to send their pause acknowledgments back.

On receipt of that alert:

1. Start no new modeling or render batches. Message every active project
   worker, including `lista-bishop`, `lista-king` and `lista-pawn`, using
   `[lista-manager]:`. Identify this as Toby's authorized quota stop.
2. Ask each worker to preserve its best accepted result, save a concise
   checkpoint of pending work/validation, pause its active goal, and stop.
   A quota stop calls for a minimal safe checkpoint, not another iteration
   or expensive finishing batch. Do not mark an unfinished goal complete.
3. Require an explicit return message using `[lista-<piece>]:` confirming
   the goal is paused and work has stopped. Include the manager's return
   thread ID and host. Workers should report the actual goal-tool status;
   if no goal is active, they should confirm that and that no work continues.
4. Track each acknowledgment. Follow up with any worker that has not
   confirmed, and report confirmed pauses and outstanding responses honestly.
   Successful message delivery or an idle chat alone is not proof of a
   paused goal. Do not claim all work stopped until all active workers confirm.

The manager also checkpoints and pauses its own active goal, if any, after
coordinating the stop. Keep this safety coordination brief. Resume modeling
only on Toby's direction; a quota reset does not itself authorize resumption.

## Project workflow

The user requests a Git commit after each completed, checked iteration. Do not push or publish unless asked; the user currently handles pushing.

Append a co-author trailer to every commit, using the actual model name:

    Co-Authored-By: Codex <actual model name> <codex@openai.com>

For the initial import the user explicitly supplied `GPT 6 Astra Ultra`. Future agents must use their own actual identity, not infer it from this import. Ask if unavailable. This is message attribution, not cryptographic signing.

The user identified the agent for the 54-degree queen wood revision as GPT-6.1 Terra. Use `Co-Authored-By: Codex GPT-6.1 Terra <codex@openai.com>` for this agent's commits. Future agents must use their own actual model name.

Queen scripts are in `scripts/queen`; its editable model is `models/queen/queen-rebuilt.blend`, with references and comparisons in `assets/queen`. King scripts are in `scripts/king`; its model is `models/king/king-rebuilt.blend`, with references, renders, mesh export and comparison reports in `assets/king`. Keep the interactive viewer and overlay synchronized with the same model and saved camera. Verify substantive queen changes with `validate_finished_queen.py`, mesh export checks, and camera regression; the previous stacked-collar preservation validator describes an older shape and no longer applies to the new 54-degree refit.

Root pages are `index.html` (all twelve original pieces), `review.html` (queen tabs), `set-comparison.html` (whole-set references), and five `<piece>-review.html` pages with Reference candidates and Model tabs. Model tabs discover a corresponding `<piece>-model.html` when it exists and otherwise show a placeholder. King and rook also have lazy Projection variants tabs embedding `<piece>-projections.html`; queen has the same study as its fourth workspace tab. Preserve candidate state and both iframe states when changing tabs. The queen review remains independent. Preserve the parts map's sandboxed iframe and CSP. Do not change the overlay's behavior while changing geometry.

For the king, the original Lichess sprite is authoritative for proportions; selected black candidate 1 supports detail interpretation. The current model is a closed revolved body plus an intersecting separate beveled cross (not boolean-fused), approximately 68,500 triangles. The current fixed-54-degree king has a packed wood pigment atlas and real BSDF material; neutral clay remains a geometry diagnostic. Do not interpret silhouette agreement as proof of unseen geometry.

King rebuild order: preserve the current accepted model and follow `docs/king-mission-log.md`; the old `build_king.py` is historical. Render and export the accepted scene, run `scripts/king/validate.py` in Blender with `-- ROOT`, build its registered side comparison and viewer, then run `scripts/king/check_viewer.cjs`. Rebuild only the king candidate page with `scripts/build_candidate_pages.py --piece king` and run affected interaction and site checks. Keep king work separate from the queen model and review.

`history/` preserves earlier iterations and scripts as evidence. Those scripts may contain obsolete paths and destructive overwrite assumptions: do not run them as the current pipeline. The former stacked-collar validator uses `history/queen-hires/before-stacked-collars`; the historical seamless-crown validator uses its earlier baseline. Those preservation tests describe earlier revisions. The current queen validator is `scripts/queen/validate_finished_queen.py`.

The precise authorship of the original Lichess pieces is unclear. Do not attribute these pieces to James Clarke. Preserve the source notes; do not invent a license for the supplied references.

Publish the repository root directly. Do not reintroduce an `_site` packaging folder. The original reference gallery uses the twelve PNGs from Lichess’s `public/images/staunton/piece/Staunton` set; omit its extra knight preview.

The review embeds its viewer and unmodified parts map as JSON documents. Switch tools only through the tabs; image dragging only pans the reference. Preserve parent/frame message-source checks. Source templates live in scripts/queen; build_viewer.py updates the embedded documents in review.html. Keep the page limited to the tabs, controls, and viewing area, with no detail panels beneath. Both interaction checks in scripts/queen must pass after changes to review controls or the viewer bridge.

Candidate comparison pages share assets/comparison/candidate-review.js and .css. scripts/build_candidate_pages.py rebuilds them from the template and assets/candidates/alignment.json. It must never rewrite review.html. Generated candidate PNGs stay unmodified; prompts and hashes are recorded in assets/candidates/generation.json. Alignment applies only uniform scale/translation in CSS, with the white knight mirrored explicitly in aligned view. Model frames load on first tab use and retain their state; preserve candidate choices, zoom and pan when switching tabs. Run node scripts/check_candidate_review.cjs after comparison interaction changes.

King, queen and rook projection alternatives live in `assets/<piece>-projections`, `models/<piece>-projections`, and their `scripts/<piece>/*projection*` sources. They do not replace the current models. Preserve a fixed physical base diameter and shared profile/orbit framing between variants. Validate with `check_projection_variants.py` and `check_projections_viewer.cjs`; see `docs/<piece>-projections.md`. All studies include 54 degrees; queen also retains its current 51.5-degree interpretation. Queen candidates use a documented reduced subdivision level for portable page size, with the same candidate mesh in rendering and the interactive viewer. The 54-degree current queen is now a separate subsequent revision; the studies remain historical alternatives. Their protected baseline lives under `history/queen-before-54-finish`.

Additional pieces follow `scripts/<piece>`, `assets/<piece>`, `models/<piece>`, `history/<piece>` and `<piece>-model.html`. Rook uses original black / selected black 8; bishop uses original white / selected white 3; knight uses original black / selected black 2 with mirrored white for secondary comparison. Pawn uses original black / selected black 2. Their starting camera is 54 degrees. Preserve selected-reference hashes and coordinate registration. `scripts/check_model_site.py` checks activated review frames, embedded mesh/camera and unchanged source selection.

The whole-set comparison has Reference comparison, GPT-generated side views, 3D models, Board comparison, and Proportion warping tabs. The GPT-generated side views tab displays all six generated side elevations using `assets/side-views/manifest.json` and `assets/<piece>/concepts`. Preserve comparison color/candidate choices across tab changes and the `#side-views` deep link. Panel IDs differ from the route hashes to avoid browser scroll jumps. Rebuild with `scripts/build_set_comparison.py`; `scripts/check_set.cjs` checks all five tabs, source image hashes and retained state. Generated side views are interpretations; do not silently replace selected overhead references or models with them.

Side views use `side-01-cutout.png` siblings, preserving opaque originals and generation records. Their display is one horizontally scrollable row at a shared ground line. Recompute `assets/side-views/scale.json` with `scripts/measure_side_views.py` (Pillow/NumPy), then rebuild the set page. All six images are uniformly scaled to relative model-height estimates at a common 54-degree assumption: normalize each model's height by its own round base diameter, multiply by its original sprite base-width ratio to the king, then divide by the king's model height/base ratio. King stays 430px tall. Measure the mesh's lower quarter for base diameter so the knight's muzzle is excluded. Preserve PNG aspect ratios, eager loading, source hashes and extraction caveat. No independent card fitting or nonuniform stretching.

Manual side-view sliders apply 50–150% uniform CSS scaling around each opaque foot's measured bottom-center. Reserve fixed space for slider extremes so neither the ground line nor piece centers move. Update all king-relative height labels when the king changes. Preserve per-piece reset, guarded local storage, eager image loading and comparison-tab state. Baseline estimates in scale.json remain unchanged.

Side-view reordering uses pointer capture with horizontal-only movement, insertion markers and edge scrolling; left/right buttons and keyboard shortcuts are alternatives. Move existing card nodes, preserving scale controls, image state and the shared baseline. Order storage is separate from scale storage, and Reset order must not reset sizes. `scripts/side-order-runtime.js` is embedded into the standalone set page by the builder.

The 3D models tab loads each current piece mesh and wood atlas, follows the current side-view order, and keeps foot centers on a shared ground line. The Matched heights button switches uniformly between the board-image fit and the current side-view height selection, in sync with Board comparison; it does not change the saved side-view choices. It uses one WebGL canvas; drag rotates the pieces together. The 54° view is an orthographic camera 54° above the horizontal board, matching the current saved reference-camera assumption. Keep the feet visible at raised angles. The queen mesh comes from the embedded viewer in `review.html`; the others come from `assets/<piece>/mesh.json` and `mesh.bin`. The Blender renders button beside the material controls displays the current saved Blender profile renders at the same sizes and order; Wood or Neutral returns to the rotatable models. The `#blender` link opens this mode inside the 3D models tab. The knight profile uses its existing 7-degree side render; lighting differs by piece. When the page is opened as a local file, the 3D tab shows those profiles instead because browsers restrict local mesh fetching. `scripts/build_set_comparison.py` remeasures the transparent profile bounds for that fallback. Rebuild after accepted model/profile updates and run `scripts/check_model_lineup.cjs` to verify current Blender source hashes, mesh bounds, and display heights, and `scripts/check_model_height_modes.cjs set-comparison.html` to check both height modes. The live viewer uses approximate lighting.

The Board comparison tab uses the owner-supplied original lineup and empty-board screenshots under `assets/board-comparison`. Matched mode uniformly scales and positions each current 54-degree Blender render to the measured visible top and foot in `height-fit.json`; the original king cross is clipped. The separate chosen-heights mode retains the gallery height settings and shared king-base calibration. Both report relative model heights; those depend on the modeled shapes and are not proven original dimensions. Soft contact shadows are an approximation. Reproduce the screenshot measurements with `scripts/measure_board_height_fit.py --check`. Rebuild with `scripts/build_set_comparison.py`, and run `scripts/check_board_comparison.cjs` along with the set-page checks. Preserve the `#board` deep link and wipe controls.

The Proportion warping lab (`#warping`) is a separate geometry experiment. Its `scripts/proportion-warping-*` sources are embedded by the set-page builder. It reuses the current meshes and textures through `window.ListauntonModelSource`, but gives each canvas separate GPU resources. Height scales Z about the foot; Width scales both horizontal axes, with inverse-transpose correction of normals. Do not mutate source vertex buffers or accepted Blender files. Starting model sizes and board foot positions come from the matched-board registration and remain fixed during warps. Use each mesh's exact saved reference-camera basis (including the knight's azimuth); angle experiments change its elevation from that basis. Per-piece Tilt controls store absolute elevation overrides (20–80°) in state.tilts; null inherits state.angle. Keep the existing browser storage key so old height/width experiments migrate intact. Set all tilts clears the overrides without resetting geometry. Tilt applies to both the board overlay and the Reference lineup, with one fixed foot line; Side view remains level. Scale multiplies the adjusted width and height about the same foot center and defaults to 100% in older experiments. Export v3 stores scale, height and width under warpPercent for each piece and keeps the referenceAngles map. The lineup camera does not auto-fit when a slider changes. Chavet guides use the rounded chosen default height ratios, not mutable side-view sliders. Browser-local settings are namespaced by model hashes and default revision; guard malformed/blocked storage. Do not substitute a stretched PNG for a warped mesh when file access or WebGL is unavailable. Validate camera registration, foot/width preservation, presets, and source immutability with `node scripts/check_proportion_warping.cjs .`, then exercise controls in a browser alongside existing set-page checks.

The owner-approved side-view defaults and displayed height relationships are authoritative in `assets/side-views/defaults.json`. Preserve these independently of computed model estimates; do not duplicate mutable slider values in mission statements. New visits and Reset use this preset; storage is namespaced by its revision so stale settings do not mask an owner-approved change.

The current queen uses an assumed 54° camera and the owner’s 83.4% queen-to-king side-view height target, normalized using the original sprite base widths. The compact-finial mission checkpoint stays within the existing height/base tolerance. The second checkpoint's color atlas (`assets/queen/queen-pigment-albedo-v2.png`) grades an independently generated de-lit reference source with continuous wood on hidden surfaces; the first atlas remains its ungraded relief source. The original references remain unchanged. The interactive viewer embeds the same color atlas and UVs with approximate real-time lighting. Rebuild and validate as documented in `docs/queen-54-wood.md`; the older build_finished_queen.py is not the current material pipeline. Silhouette overlap does not prove the internal details, wood, lighting, or hidden geometry are exact.

The queen review opens with the original Lichess image selected and includes a Side comparison tab. The side tab uses `scripts/queen/render_wood_profile.py` and `scripts/queen/build_side_comparison.py` to register the current model uniformly to the imagined side guide at the foot. Keep the side renders, overlay, rotating viewer, and saved Blender model synchronized.

The reconstruction goals are the six static `MISSION-<PIECE>.md` statements indexed by `MISSION-SET.md`. Read the assigned mission before activation. Only the owner's direction authorizes changes to their objectives, reference choices, acceptance standards or completion criteria. Keep routine progress, current status, baseline/model hashes, scores, defect audits and checkpoint summaries in `docs/<piece>-mission-log.md` and iteration evidence. Build procedures belong in piece guides. Read the latest log for the accepted model and next action; do not treat an old mission snapshot as current state. Revising these documents does not itself activate or resume a modeling goal.

The third mission checkpoint rounds the lowest collar while preserving the second checkpoint's material and lights. Its reproduction config is `docs/queen-mission/iteration-003/039-reproduction-config.json`, starting from `history/queen-mission-002`. Failed material and lighting experiments remain evidence, not alternatives in the public controls. For Cycles light separation, the verified binary controls are the light object's `visible_diffuse` and `visible_glossy`; the data-level factors did not affect Cycles in the measured diagnostic. `place_lights.py` applies ray visibility only when explicitly enabled in the config, preserving older experimental behavior.

The fourth mission checkpoint preserves the third geometry, uses `assets/queen/queen-pigment-albedo-v3.png` for color, and retains the first atlas for relief. Fine reference grain supplements a broad inferred pigment field. Its actual reflection rig is fitted through AgX and separates diffuse/glossy rays; browser lighting remains approximate. Reproduce from tracked inputs with `scripts/queen/rebuild_material_checkpoint.py` and `docs/queen-mission/iteration-004/reproduction.json`, using the archived third model. Always verify saved texture pixels and a reopened render: editing and repacking a reopened sRGB-tagged float image previously caused double conversion. Fresh linear EXR color and separate confidence avoid that defect. No source references or side-gallery defaults change.

The fifth checkpoint adjusts regional pigment color, using `assets/queen/queen-pigment-albedo-v4.png`. It preserves the fourth geometry, UVs, relief, camera and lighting. Reproduce it with `scripts/queen/rebuild_material_checkpoint.py` and `docs/queen-mission/iteration-005/reproduction.json`, starting from `history/queen-mission-004`. The separate grading config also documents the color transformation before baking. Surface experiments and emission diagnostics are evidence only; do not substitute them for a real BSDF beauty render. Fine texture and reflected crescents remain unfinished.

The sixth checkpoint narrows the base reflector to 36 degrees and adjusts its power to retain the base contribution while reducing finial spill. It keeps the v4 pigment, relief and geometry. Reproduce with `scripts/queen/rebuild_material_checkpoint.py` and `docs/queen-mission/iteration-006/reproduction.json`, using `history/queen-mission-005`. Broader light-confinement and refitting experiments were rejected despite lower numerical fitting losses; preserve the accepted rig when continuing geometry work.

The eighth checkpoint further reduces finial spill using two exact evaluated light receivers: `turned-body` and `finial`. The closed editable control is tagged `mission_editable_control`; it is hidden only from final rendering and is the mesh exported to the viewer. Derived render copies are tagged `mission_render_region`, share the material, and preserve exact positions/UVs and custom smooth normals. Only the three intended finial spot reflectors act directly on the finial; accepted light powers are unchanged. Use `queen_scene.editable_mesh` and `set_material` instead of choosing the first visible mesh. Rebuild with `build_finial_receiver_checkpoint.py` from `history/queen-mission-006`. Never edit a derived receiver or render stale copies after a geometry edit: rebuild receivers from the edited control first. `geometry_trial.py` deliberately rejects a receiver-bearing source until that regeneration is performed. `validate_render_receivers.py` checks their evaluated surface, normals, UVs, material and links against the closed control. The seventh checkpoint contains rejected experiments only.

Individual missions are `MISSION-KING.md`, `MISSION-QUEEN.md`, `MISSION-BISHOP.md`, `MISSION-KNIGHT.md`, `MISSION-ROOK.md` and `MISSION-PAWN.md`; `MISSION-SET.md` is their index. Read the assigned piece mission before activation. The original queen mission has been merged into `MISSION-QUEEN.md`; its earlier versions remain in Git history. Creating these files did not resume the paused goal or launch workers.

The tenth queen checkpoint seats a smaller finial deeper in the bowl. `seat_finial_trial.py` rebuilds from `history/queen-mission-008`; it changes only rings 107-116 and regenerates the two receivers. The intentional 0.0467-unit lowering of the highest point adjusts the height target without stretching the body or changing gallery defaults. The validator checks unchanged non-finial controls. See `docs/queen-mission/iteration-010`.

The eleventh queen checkpoint retains tenth geometry/material and fits eight shaped bowl reflectors while disabling the three broad bowl areas. Reproduce with `focus_bowl_reflections.py -- --arc`, `prepare_light_fit.py --size 1254 --directory build/queen-mission/bowl-arc-fit`, then `fit_bowl_arc_powers.py`; see iteration-011. Actual full BSDF renders govern acceptance, not the approximate cropped-response prediction. The current source to preserve for further geometry/material work is the eleventh model.

The first king mission checkpoint uses the fixed 54-degree camera and a real wood BSDF with packed pigment atlas. Current procedures and scores are in docs/king-mission-log.md. Use scripts/king/mission_trial.py for controlled edits, bake_pigment.py for pigment-only atlas baking, export_mission.py for exact mesh/camera and closure validation, audit_mission.py for the fixed mask convention, then build_viewer.py and check_viewer.cjs. The old build_king.py/profile.json describe the archived 52-degree clay baseline and must not overwrite the current model. Historical king projection preservation now checks history/king-before-54-mission; projection alternatives and side-gallery scale/defaults remain unchanged.

At every accepted king checkpoint, update `king-review.html`, `king-model.html`, their fixed and side renders, and the existing local preview. The king main page opens Reconstruction; its viewer offers Reference overlay, Rotate model and Side comparison. Candidate selection and historical projection tabs remain available. Failed trials must not replace these accepted assets.

The twelfth queen checkpoint retains eleventh geometry and lighting and uses
queen-pigment-albedo-v5.png. Reproduce its bounded measured-pigment correction
from history/queen-mission-011 using the iteration-012 instructions. Bake the
closed control with unchanged UVs, then restore exact render receivers. Preserve
reopened texture checks. At every accepted major queen checkpoint, update the
repository review and existing local preview together: overlay, rotating model
and side views. Tell the owner it is ready to refresh. Failed trials stay out
of the public review. Consult the queen mission log for current scores and source hash.


The thirteenth queen checkpoint uses queen-pigment-albedo-v7.png. It changes
only radii of rings 26-29 to smooth the base/socket junction, repairs a local
pigment imprint with continuous grain, and reshapes/warms only the base-key light.
The finial, all heights, other controls, UVs and topology stay unchanged.
validate_base_transition.py verifies the exact scope against the archived
checkpoint-12 model and controls; check_material_geometry.py requires the explicit
--allow-base-transition flag for this edit. Rebuild using rebuild_base_checkpoint.py
and iteration-013/reproduction.json. Preserve receiver regeneration after geometry
changes and synchronized local review assets. Rejected v6 is not a public option.


The fourteenth queen checkpoint uses queen-pigment-albedo-v8.png and three
exact render receivers: turned-body, stem-socket and finial. Its control geometry,
UVs and dimensions are unchanged from checkpoint 13. The stem/socket receiver
excludes six measured stray reflectors and receives the fitted crescent spots;
all links are checked by validate_render_receivers.py. Preserve the socket_band
partition when regenerating receivers. Do not replace it with finial_only.
Rebuild with rebuild_socket_checkpoint.py and iteration-014/reproduction.json.
check_material_geometry.py now compares to history/queen-mission-013 in ordinary
unchanged-geometry mode. Preserve fixed/side/viewer synchronization.


The fifteenth queen checkpoint retains the v8 material and closed control.
It adds an exact collars receiver to turned-body, stem-socket and finial; use
partition(..., socket_band=True, collar_band=True) after future geometry edits.
Local lights are fitted with the accepted illumination retained as a basis.
Secondary glossy bounces are zero to remove a measured crown-body interreflection;
this is an artistic rendering approximation, not a recovered original setting.
Rebuild with rebuild_collar_checkpoint.py and iteration-015/reproduction.json.
Preserve unchanged geometry/UV checks and fixed/side/viewer synchronization.


The sixteenth queen checkpoint changes only lower-bevel radii 64-66 of the middle collar. All heights, peak ring and other controls stay exact; v8 pigment and relief stay unchanged. Six exact receivers now split lower/middle/upper collars: regenerate with socket_band=True, collar_band=True, split_collars=True. Eleven measured middle-collar reflection fills omit cast shadows as an explicit artistic approximation. Reproduce from archived checkpoint 15 with rebuild_collar_checkpoint.py and docs/queen-mission/iteration-016/reproduction.json. Compare geometry using --allow-middle-collar-edge against checkpoint 15. Always judge a fresh saved-file render after a response-fitting session; checkpoint 16 records a transient in-memory mismatch and successful independent reconstruction. See iteration-016 for current scores, validation and remaining defects.


The seventeenth queen checkpoint retains checkpoint-16 geometry, UVs and all
six receivers. Its v9 atlas repairs only finial pigment; unmasked texels stay
byte-identical to v8. Local finial relief is reduced to .00175 while the body
retains .007. Three measured glint reflectors link only to the finial; exact
copies preserve their former illumination elsewhere. Explicit shadow_soft_size
values remove the historical radius/diameter ambiguity. Reproduce from archived
checkpoint 16 with rebuild_finial_checkpoint.py and iteration-017/reproduction.json.
Use validate_finial_material.py for packed pixels, material and light-edit scope,
plus the normal geometry/receiver/camera checks. Keep fixed, side and viewer
assets synchronized; bowl/rim shaping, grain and reflections remain unfinished.
The accepted render uses 256 fixed samples with use_light_tree=False for repeatability. Publish/reopen helpers honor explicit render_sampling metadata; earlier checkpoints retain their defaults. The polish mask uses object coordinates and is verified by a translated-piece emission-field check.


Queen checkpoint 18 raises the inner flare and shortens the socket. Rebuild with `scripts/queen/refine_socket_flare.py` and `docs/queen-mission/iteration-018/profile.json` from the archived seventeenth queen. Preserve the stem/socket face membership when regenerating the six light receivers. The camera stays at 54°. See `docs/queen-mission/iteration-018/README.md` for the profile, light settings and validation.


Queen checkpoint 19 changes only radial controls 40–48 (stem) and 85–90
(crown body), keeping all heights and the accepted 54-degree camera. Rebuild
with profile_study.py and docs/queen-mission/iteration-019/profile.json from
history/queen-mission-018. validate_profile_flow.py verifies the scoped edit
before the older checkpoint validators; check_material_geometry.py accepts
--allow-profile-flow against checkpoint 18. Regenerate the same six receivers
after future geometry edits. Full material, light, camera and atlas preservation
is checked by validate_profile_preservation.py. The owner now permits other
camera-angle experiments; record them separately and prefer the original
sprite when they conflict with plausible side references. Two 52-degree tests
were rejected, not proof that every alternative angle is wrong.


Queen checkpoint 20 rounds only lower-collar radial controls 51–54; heights,
crest/upper surface and all other queen controls are preserved. Reproduce with
profile_study.py and docs/queen-mission/iteration-020/profile.json, starting at
history/queen-mission-019. validate_lower_collar.py unwraps this local change
before checkpoint 19 and earlier scope checks. check_material_geometry.py uses
--allow-lower-collar against checkpoint 19. validate_profile_preservation.py now
accepts --baseline; use checkpoint 19 for this iteration. Six receivers, exact
UVs, packed textures, lights and the saved camera remain validated. The small
side improvement does not establish that the inferred proportions are exact.


Queen checkpoint 21 lowers only finial-cap controls 108–116 by 10% toward
ring 107; radii, body, bowl, rim and tips stay exact. Reproduce from checkpoint
20 using iteration-021/profile.json, then the documented surface capture and
aim_finial_reflections.py step. validate_finial_cap.py unwraps the cap before
older geometry scope checks; check_material_geometry.py uses --allow-finial-cap
against checkpoint 20. validate_cap_lights.py permits only the three existing
finial reflectors to be re-aimed, preserving all other light and material data.
The height target accounts for the additional 0.0380-unit cap reduction without
changing its tolerance or rescaling the body. Actual camera remains 54 degrees.
The optional UV-face membership preservation added for a rejected bowl trial
is off for the accepted cap; never adopt rejected geometry or emitters silently.
Keep accepted overlay, side views and exported control mesh synchronized.


Queen checkpoint 22 preserves checkpoint 21 geometry, UVs, relief, camera and
all 85 lights. A smooth object-space grade multiplies only the inner finial-root
pigment by 1–2.5; the v9 atlas pixels remain unchanged. Reproduce using
grade_finial_root.py and iteration-022/204-inner-root-pigment.json from the
checkpoint-21 archive. validate_root_pigment.py checks graph scope, original
material/light data and an actual translated-field render. Recreate its position
capture as documented before running it in a fresh checkout. The viewer carries
the same field through uRootHeight/uRootRadiusGain and vWoodPosition; preserve
these when rebuilding, and retain or bake the procedural grade for other exports.
The older bowl-floor changes and added contact lights are rejected, not public
alternatives. Keep the saved/reopened comparison and synchronized current views.

Queen checkpoint 31 raises only stem controls 48 and 49 to flatten the join
under the accepted rounded bottom collar. The socket shelf/drop, base, all
radii, crown, egg, materials, lights and 54-degree camera are unchanged from
checkpoint 29. Reproduce with study_compact_turning.py and the commands in
docs/queen-mission/iteration-031; checkpoint 29 is archived. Use the scoped
side-shape and delivered-model validators, then regenerate all fixed/side and
viewer assets. Coupled base-compression trials in iteration 31 are rejected:
their close exterior outlines conceal a displaced socket lip. Constrain that
interior arc before accepting further base changes. The shape goal is active.

Queen checkpoint 32 accepts 6% compression of the whole foot/base/socket,
a 6.2% narrower socket wall and a broader inner flare. The shelf and steep
drop remain distinct. Stem radii from control 38 and all controls from 48
upward are unchanged from checkpoint 31; keep the accepted rounded collars,
crown and egg. The camera remains orthographic 54 degrees. Reproduce with
study_compact_turning.py and iteration-032/base-input.json from the archived
checkpoint 31. Validate the composed profile, shader/light preservation and
saved model, then rebuild fixed/side renders and the viewer together. The
original silhouette tradeoff and rejected camera/straight-stem fits are in
iteration-032. Do not promote those rejected alternatives or alter gallery
defaults. The shape goal remains active; socket reflections need refinement.

Queen checkpoint 33 removes an extra inflection above the base groove. Only
radial controls 9–21 change; every height and the socket shelf/drop, stem,
collars, crown and egg remain exact from checkpoint 32. Reproduce with
study_compact_turning.py and iteration-033/264-shallow-groove-roll.json from
the archived checkpoint 32. All six receivers are regenerated; material,
lights, source pixels, gallery defaults and the 54-degree camera remain
unchanged. record_base_turn_checkpoint.py records the scoped measurements.
Keep fixed/side/viewer assets synchronized. The original outline tradeoff
and rejected lower-round-over candidate are documented in iteration-033.

The owner-directed Queen shape phase is completed by the audit in
docs/queen-mission/iteration-034. Checkpoint 33 remains the accepted model.
The final flatter-socket experiments preserve the exterior mask but worsen
the lip/crescent and are rejected. The audit covers all four shape priorities,
source preservation, current model validation and synchronized review assets.
At that time, color, grain and lighting finishing were deferred. The restored
Queen mission includes those aspects and remains incomplete until it meets the
full visual-match criteria. Shape-phase completion is not a claim of exact
recovered geometry or a perfect full-image match.
