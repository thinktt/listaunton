# Queen checkpoint 19 — continuous stem and crown curves

The owner resumed the queen mission on November 11, 2026, allowing camera-angle
experiments and identifying Chavet/Lardy as the leading whole-set proportion
guides. The original Lichess image remains authoritative; these families are
visual analogies, not established attribution. The broad German Knight base is
a useful shape guide, but the tested base change did not improve this model.

The accepted change increases stem radii through rings 40–48 and eases crown-body
radii 85–90 inward. The narrowest stem radius increases about 11.4%; the largest
local crown-body reduction is about 5.9%. Every control height, foot, raised
socket, collar, crown rim/tip, bowl and finial remains unchanged. Total physical
height and base diameter are preserved. All wood pixels, material nodes, UVs,
lights and the saved camera are identical to checkpoint 18. Six regenerated
light receivers preserve the exact evaluated surface and smooth normals.

Both a simple and a bounded-refitted 52-degree camera were actually rendered.
The better of those fits reaches about 96.88% original silhouette IoU, compared
with 97.91% at the accepted baseline, and broadens the socket. It is not accepted.
This does not prove 54° is the original angle; it only rejects these specific
experiments. The accepted local shape improvement remains at **54°**.

Final measured IoU is **97.9177%** for the original and
**97.9701%** for the selected high-res. The tiny outline improvement is not
the reason for acceptance: the side profile is fuller and less straight-sided
without sacrificing the established fixed view. Visual ratings are form 85,
color 84, grain 79 and lighting 76; mean 84.3940%, holistic 80–85%.
The white sprite was inspected as a geometry cross-check; this is still only
the brown finish. It is **not a perfect reconstruction**.

The socket still has a rather upright wall, the lower collar's underside looks
shelf-like in a level side view, and the finial may remain too exposed. The
base highlight and bowl crescents differ from the original, and wood relief
and some grain directions remain approximate. The next useful test is the
lower collar underside and stem shoulder, under a fresh local shape study.

Reproduce from the protected checkpoint-18 archive:

```sh
blender -b --python scripts/queen/profile_study.py -- docs/queen-mission/iteration-019/profile.json --render --samples 256
blender -b --python scripts/queen/validate_finished_queen.py -- --blend build/queen-mission/188-stronger-flow/queen.blend --report-dir build/queen-mission/188-stronger-flow
blender -b --python scripts/queen/check_material_geometry.py -- --baseline history/queen-mission-018/queen-rebuilt.blend --current build/queen-mission/188-stronger-flow/queen.blend --allow-profile-flow --report-dir build/queen-mission/188-stronger-flow
```

Reopened 256-sample Cycles renders were checked against the promoted scene.
Topology, unchanged material/light/camera checks, exact receiver geometry and
UV checks, viewer camera regression and tab/overlay interaction checks passed.
The latter use a simulated DOM/WebGL harness. Fixed, side and interactive
assets all refer to model `d5882d44aa0dc3f2f72ea7449f353e530e59888fb3804ef32233544ce6feffb0`. Source references and gallery defaults remain
unchanged. Rejected trials remain evidence only, not new public model choices.
