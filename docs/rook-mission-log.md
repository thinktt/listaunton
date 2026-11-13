# Rook reconstruction mission log

## Mission-statement cleanup — 2026-11-12

The owner requested static goals with progress recorded separately. The
piece mission now preserves the original full visual-match objective and
five-category standard. This is a documentation migration, not a new model
iteration, fresh assessment, or change to the accepted model. The complete
pre-cleanup statement is available in Git at `fb75902169d17a993280dbd593f8d5163204e592:MISSION-ROOK.md`.

### Information moved out of the mission

Former drafting snapshot (historical, not the current accepted hash):

- Model SHA-256 at drafting: `23abce50f4a7bd6544f7844534e69a02e3a337a64ee7ce214e81acc353a26f2c`.

The former statement said full-material scores were unassessed. That was a
historical drafting statement, not a new assessment; use this log's actual
iteration evidence to establish the accepted state and current scores.

The statement also carried a snapshot saying the queen goal was paused.
Activation and pause state belong to the relevant goal, not this piece's mission.

Future checkpoints, scores, defect lists and phase completion belong in this
log and the iteration evidence. Change the static goal only at the owner's
direction. Apply [the shared mission standards](../MISSION-SET.md).

## Iteration 001 — 2026-11-12

Activated the full rook mission at the owner's direction. Inspected the original, selected black candidate 8 and accepted neutral model. Completed and rejected an initial procedural wood study for promotion: smeared horizontal grain, cloudy floor, insufficient red/orange color, and misplaced broad reflections. Saved/reopened NVIDIA render succeeded. Accepted model and public assets remain unchanged. See [the full examination and scores](rook-mission/iteration-001/README.md). Next: reference-informed pigment with separated illumination and continuous unseen-surface wood. Accepted iterations must update the review, local preview, rotating viewer and side views before further iteration; this operational requirement is separate from the goal objective.

## Iteration 002 — 2026-11-12

Reference-informed pigment restores recognisable floor fibers and exterior grain. Broad softbox reflections still wash out the right cavity. Low-confidence strips revert to the unrelated procedural material, especially the shaft and right rear merlon. Some target glints may remain weakly represented in pigment despite the confidence mask; this cannot be counted as a recovered highlight. Side view exposes material transitions and stretched detail. Reject for promotion.

Selected overlap 97.30350%; original 95.67335%; interior/color/grain/lighting 78/68/53/28 (subjective); working mean 64.86%. Saved geometry/camera/source/material validation passed. See [evidence and limitations](rook-mission/iteration-002/README.md). Goal remains active; accepted model and review remain unchanged.

## Iteration 003 — 2026-11-12

Making existing softboxes diffuse-only and adding three smaller real glossy sources removes the broad milky cavity reflection. Floor color and grain improve substantially; shaft coverage is more coherent. The small sources still create misplaced lower/central glints and fail to form the reference's bright thin rim, shoulder and foot crescents. Fallback grain transitions remain conspicuous in profile; rim-edge registration exposes the underlying shape mismatch. Keep as the best experimental starting point, not an accepted/public checkpoint.

Selected overlap 97.30350%; original 95.67335%; interior/color/grain/lighting 78/76/64/41 (subjective); working mean 71.26%. Saved geometry/camera/source/material validation passed. See [evidence and limitations](rook-mission/iteration-003/README.md). Goal remains active; accepted model and review remain unchanged.

## Iteration 004 — 2026-11-12 — accepted first wood checkpoint

Accepted model `9eaaaaadfd2195591508cda798d56c27aa263ee3baa9424ded8acf76d6e4349c` replaces the neutral material baseline; original controls/camera and owner-approved proportions are preserved. Prior neutral model archived under `history/rook-mission-000`. Packed pigment atlas, wood BSDF and smaller glossy sources substantially improve color and grain. Public rook model/review and the existing Windows preview now carry the same saved-model render, textured mesh and side comparison.

Selected/original IoU **97.30350% / 95.67335%**. Subjective interior/color/grain/lighting **78/76/66/41**; working mean **71.66%**; holistic **60–70%**. Model remains unfinished: weak/misplaced bright crescents, rim glints, inside-wall artifacts and side-neck pigment transitions. See [examination, reproduction and exact validation scope](rook-mission/iteration-004/README.md). Goal remains active. Next: fit the reflected edge highlights without disturbing the accepted pigment or geometry.

## Iterations 005–006 — 2026-11-12 — rejected reflection studies

Fitted 18 glossy spot reflectors, then constrained them to exact-position/UV edge receivers. The first spills glare into the cavity; the second removes much of that spill but misses the continuous bright crescents and exposes red/orange shoulder patches. Both rejected. Scores and scope are in iteration-005 and iteration-006. Receiver normal-encoding deviations are recorded explicitly; this diagnostic is not an accepted mesh replacement. Checkpoint 004 and synchronized web assets remain current. Next: inspect curved edge geometry and finish response before another lighting fit. Goal remains active.

## Iterations 007–011 — 2026-11-12 — finish ablations and strip illumination

Tested stronger polish, removing bump, and two real extended strip-light elevations on accepted checkpoint 004. Polish and microrelief changes do not solve the misplaced crescents. The high strip makes continuous arcs but exposes a double shoulder band; the low strip produces extra broad bands. All rejected for public promotion. Full saved geometry/material validation covers representative 008 and 010; individual evidence describes scope. Selected/original IoU remains 97.30350% / 95.67335%. Best diagnostic 010 has subjective interior/color/grain/lighting 78/74/65/44, working mean 71.66%; it is not a new accepted model. Next: inspect shoulder/foot profile and normals under extended illumination. Goal remains active; public checkpoint 004 preserved.

## Iterations 012–014 and diagnostics 015–016 — 2026-11-12

Rejected three shallower shoulder/foot groove experiments under identical strip illumination. They do not fix the double band; saved/reopened fixed and side comparisons are retained. The decisive new evidence is the pure-pigment diagnostic: bright shoulder/foot bands and dark red patches remain with illumination removed. The accepted atlas contains significant baked lighting contamination. Further geometry compensation alone is not supported. Next: separate or regularize pigment before another reflection fit; preserve recognizable grain and check the side view. Accepted checkpoint 004 and web assets remain unchanged. Goal remains active.

## Iterations 017–020 — 2026-11-12 — pigment repair and directed strips

Adjacent wood resampling removes some baked brightness but stretches grain and changes regional color. Strip illumination still produces two real reflections, correcting the earlier inference: baked pigment is a contributing cause, not the sole cause. Actual-normal strip placement reaches target edges but spills broad glare. Reduced, edge-linked strips remove the spill yet remain too weak/uneven and retain poor repaired grain. All rejected. Full saved validation passed for 017; receiver checks cover 020. Empirical source-pixel comparison rules out the suspected byte-image transfer error. Next: narrower pigment repair and independent edge intensity/receiver calibration. Checkpoint 004 remains public; goal active.

## Iteration 021 — 2026-11-12 — accepted foot reflector

Accepted a 40W foot-linked glossy strip while retaining checkpoint 004 wood, editable geometry, camera and existing lighting. Stronger variants rejected. Current model SHA-256 3f09283860474bec2297ff8cdd5ff2bec9a10833d02e4e53fd0290f361babb05. Previous state archived in history/rook-mission-004. Fixed/profile/rear renders, rotating mesh, root review and Windows preview synchronized and checked. See iteration-021 for exact preservation scope, measured receiver UV/normal rounding, saved-scene reproduction and site checks. Selected/original IoU 97.30350% / 95.67335%; subjective interior/color/grain/lighting 78/76/66/45; working mean 72.46%, holistic still 60-70%. Goal active; next address shoulder highlight placement without broad pigment replacement.

## Iterations 022–026 — 2026-11-12 — accepted lighting checkpoint 025

Shoulder-only light strength tests reduced regional error but retained old glare. Checkpoint 025 restricts the old upper/rim sources to the turret and disables the old front crescent, removing the misplaced shoulder patch and cavity streak. Geometry/camera/pigment unchanged, foot reflector preserved. Narrow pigment repair 026 rejected for grain distortion. Accepted model SHA-256 082b79a1712cd07eaab76af0f945688ff04281ba9678e568ac1077698ad7b8a2. Prior checkpoint 021 archived; fixed/profile/rear, viewer and Windows preview synchronized and checked. Selected/original IoU 97.30350% / 95.67335%; subjective interior/color/grain/lighting 78/74/66/53; working mean 73.66%, holistic 60-70%. Color declines slightly because removal of glare exposes baked reddish patches. See iteration-025 for validation and tradeoffs. Next: improve turret/inner-rim reflections and local pigment contamination. Goal remains active.

## Iterations 027–029 — 2026-11-12 — rejected turret strip studies

Tested rear, front and overhead glossy strip lights linked only to the rim. Rear lighting turns flat top faces white; front and overhead variants do not recover the thin reference arcs. All rejected. Saved/reopened renders and fixed-frame audits cover all three; representative 027 receives full saved geometry/material/camera/receiver validation. Accepted checkpoint 025 and synchronized public assets remain unchanged. Next inspect bevel geometry and shading normals before further rim-light fitting. Goal remains active; no claim of complete match.

## Iterations 030–037 — 2026-11-12 — accepted bevel reflection checkpoint 037

Measured existing bevel normals, tested lower/upper reflection targets and power, then confined two 1500W strips to upper rounded bevel faces. This strengthens thin rim arcs without white vertical notch streaks. Geometry, camera, pigment and original lights preserved. Model SHA-256 a667b97122b3c188d93040279660ef947d91ba12b442442a71b4ba97a133e484. Checkpoint 025 archived; saved fixed/profile/rear, exact mesh/viewer and Windows preview synchronized and validated. Selected/original IoU 97.30350% / 95.67335%; subjective interior/color/grain/lighting 78/74/66/57; mean 74.46%, holistic 60–70%. The recessed-floor highlight, baked pigment artifacts and side texture seams remain unresolved. Next address the floor-edge stripe and reflection, with a geometry/texture distinction rather than more global lights. Goal active.

## Iterations 038–047 — 2026-11-12 — accepted recessed-floor checkpoint 047

Traced the orange stripe and floor transition, rejected standalone depth edits and a whole-floor polar warp, then combined six-profile-pixel recess lowering, narrow pigment repair, perimeter-only grain registration and a warm floor-only strip. Pigment atlas v2 reproduces the live shader (mean RGB difference 0.01004/255, alpha identical). Model SHA-256 77221a063a8dbdd5f01545312c98e5bf31d4f86f3d6cbe0ea169ff198060a33e. Checkpoint 037 archived; fixed/profile/rear, closed viewer mesh, new atlas and Windows preview synchronized. Outer control geometry, merlons, camera, original lights and source images preserved. Selected/original IoU 97.30350% / 95.67335%; subjective interior/color/grain/lighting 80/75/66/61; mean 75.86%, holistic still 60–70%. UV receiver tolerance explicitly adjusted to 2e-7 after measuring two-float-step Boolean rounding; exact positional coverage remains required. Lower reddish pigment patches and severe side-neck seams remain, as do overly hard highlights. Next address lower-body pigment contamination without stretching grain. Goal active and full match incomplete.

## Iterations 048�053 � 2026-11-12 � rejected lower-body color clamps

Tested three hue floors followed by three saturation ceilings in the lower-body pigment shader. Hue correction reduces red but introduces orange/yellow patches; desaturation makes surrounding wood pink before removing dark bands. All six rejected. Fresh headless NVIDIA renders, per-scene receiver checks, fixed-frame audits and representative saved-model validation (048 and 052) completed. Accepted checkpoint 047 and synchronized public assets remain unchanged. See iteration-048 through iteration-053 for scores and evidence. Next isolate inherited brightness/chroma artifacts spatially instead of broadly grading the entire band. Full match remains incomplete; goal active.

## Iterations 054�058 � 2026-11-12 � local pigment repair diagnostics

Traced lower-body pixels to real UVs, confirming nearly clipped blue pigment and baked dark/red bands. Four localized difference-of-Gaussian repairs tested two neighborhood radii and strengths without UV warping. Upper patch improves slightly, but lower brightness overshoots and strong corrections create blobs/muddy grain; all rejected. Fixed saved renders, per-scene receiver audits and representative full validation (055) completed. Unmasked atlas pixels remain exact. Current accepted checkpoint 047 and public assets unchanged. Next distinguish upper brightness from lower chroma defects rather than applying one correction to all three patches. Goal active and full match incomplete.

## Iterations 059�060 � 2026-11-12 � upper-patch pigment lift

Isolated the upper patch with a compact UV/excess-red mask. Two additive color lifts improve brown hue without changing lower bands, but the patch remains flat and lacks grain. Rejected for promotion despite a small color score gain. Saved NVIDIA renders, per-scene receiver checks, representative material/geometry/camera validation (059) and fixed comparisons recorded. Accepted checkpoint 047 remains unchanged. Next restore missing local grain through reference-to-surface correspondence rather than further grading a detail-poor patch. Goal active.
