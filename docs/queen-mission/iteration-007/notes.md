# Seventh queen mission iteration

Starting commit: `d1b806f` (sixth accepted checkpoint).
Starting model SHA-256:
`82100ad9047426b1be46e72d01d769189b4e9f667005fd8c8bcc5d743c16526e`.
Reference SHA-256 remains
`bc510a8f5fff0a1e51fd913f1cf4f4707849d68c5d4dabc8ce6df16cc2e1423a`.
The orthographic camera remains 54 degrees above the board. No source image,
gallery default, or other piece is changed.

Luna reading at 2026-11-05 12:30:48 UTC: weekly 20% used / 80% remaining;
reset 2026-11-11 13:19:48 UTC. Five-minute monitoring remains active.

## 077: socket shoulder — rejected

Raise the middle of the socket shoulder to roll toward a flatter upper
surface, retaining its radii, stem junction, material, and rig. The actual
wood and clay renders reveal a more abrupt upper shoulder and additional
back-edge exposure. The white curved highlight still does not match.

The high-res silhouette IoU falls from 97.9612% to 97.7217%; the original
falls from 97.9109% to 97.7050%. Scores (outline, form, color, grain,
lighting): **97.7217 / 79 / 80 / 77 / 60**, mean **78.7443%**, versus
accepted **97.9612 / 80 / 80 / 77 / 61**, mean **79.1922%**. This is a
regression. The trial is isolated and does not replace the accepted model.

## Distant reflected-light experiment — rejected

The current collars and socket are near the correct screen positions, but
their reflected crescents remain weak or misplaced. Several nearby lamps
spill onto the finial or stem. Test a different reflection rig before
forcing more geometry changes to compensate for those reflections.

Cluster mirror directions at bright, low-chroma reference pixels into 36
directions. For each, measure actual Cycles responses to 3-degree and
10-degree distant reflectors using the accepted material with black base
color. Fit nonnegative powers through the saved AgX display transform,
using a fresh actual diffuse baseline. Restore the full wood material and
render it for acceptance. Reference pixels guide physical light directions
and powers; they are never substituted for a beauty render.

The loss is only a fitting aid. Accept only after fixed-coordinate full,
detail, original-sprite, overlay, and side-view inspection. Preserve the
sixth checkpoint if the denser light-direction basis gives no clear gain.

078 has now been rendered and rejected. The fit reaches 0.0110438 display-space
loss, but broad stem/socket streaks and a bright back-left crown patch make
the image worse. Scores: **97.9612 / 80 / 77 / 76 / 55**, mean **77.1922%**.
Both silhouette IoUs are unchanged. Useful reflection directions alone do
not solve the current material response.

## 079 and fresh light fit — rejected

Reduce the existing relief's strength from 0.45 to 0.20 and distance from
0.007 to 0.003. Roughness changes from 0.19 to 0.16 and coat roughness from
0.075 to 0.06; pigment, geometry and camera remain unchanged. First render
with the accepted rig, then measure a fresh response basis and refit it.
Previous no-normal and lower-roughness trials retained old fitted lights;
this joint test checks whether exaggerated normal variation is limiting
reflection placement. Never reuse old response images with the new material.

At 2026-11-05 12:44:42 UTC, Luna reports weekly 21% used / 79% remaining;
reset remains 2026-11-11 13:19:48 UTC.

079 makes glints crisper but creates a harsh bowl arc and a sharper misplaced
base highlight. Scores: **97.9612 / 80 / 80 / 76 / 59**, mean **78.5922%**.
080 refits freshly measured responses of that material. It retains false
stem spots and adds shiny bands around the socket and collars. Scores:
**97.9612 / 80 / 77 / 75 / 54**, mean **76.7922%**. Reject both.

## 081: circumferential polish — rejected

An earlier anisotropy trial used packed-atlas tangents. This trial instead
uses the physical tangent `normalize(-y, x, 0)` with anisotropy 0.9 on the
turned body, fading to zero between z=3.8 and 4.0 so the bowl and finial
remain isotropic. It starts from the sixth checkpoint, preserving its relief,
roughness and lights. The actual render makes no convincing whole-image
gain. Scores remain **97.9612 / 80 / 80 / 77 / 61**, mean **79.1922%**;
reject the extra complexity. All material/light trials preserve both IoUs.

## Checkpoint

No experimental model is promoted. The sixth model, four delivery renders,
embedded viewer and preview remain unchanged. Trial scripts, input hashes,
comparison crops, overlays and scores are retained as evidence. Large raw
response arrays and failed Blender files stay in ignored build storage;
they do not appear in public review controls.

Next hypothesis: light linking can prevent a reflector intended for one
turned region from spilling onto another. First verify that render-only
mesh partitions preserve the accepted surface, UVs, normals and actual image
with all lights still global. Only then test linked real lights. Do not alter
the delivered mesh/viewer pipeline until a complete actual render demonstrates
a clear improvement. The mission remains incomplete.
