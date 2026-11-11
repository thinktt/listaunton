# Queen checkpoint 20 — soften the lowest collar's underside

Four real mesh trials tested the lowest collar on November 11, 2026. Its
beveled underside made a flat shelf in profile. The accepted edit rounds the
lower quadrant, keeping the crest, upper surface, all heights and every other
part of the queen unchanged. Radial controls 51–54 are the only edited controls;
their maximum displacement is 0.05225 model units. The accepted camera remains
54 degrees. Gallery height defaults, source pixels and registration are exact.

The original Lichess collar is slightly broader than the generated upscale's.
Trial 189 improved the upscale at a small cost to the original. Trial 190 added
an unhelpful shoulder change. Trial 191 refitted the original, but broadened
the crest unnecessarily. Trial 192 retains the rounding and restores the
accepted crest. No source was moved or warped, and the promotion thresholds
were not relaxed to accept it.

Original IoU is **97.9191%**, versus
97.9177% before. High-res IoU is
**97.9683%**, versus 97.9701%.
The latter decreases 0.0018
percentage points: an explicitly accepted subpixel-scale tradeoff. These tiny
changes are not evidence of improved underlying reconstruction by themselves.
The side contour is subtly rounder. The draft's apparent color/shading gain
did **not** persist at 256 samples: the collar's blurred opaque-pixel RGB error
changes by +0.026% against the original
and +0.014% against the upscale, effectively
unchanged. Those are local color/shading statistics, not whole-piece fidelity
percentages. Acceptance is based on the side contour with the fixed view
preserved; no material or lighting improvement is claimed.

Visual ratings: form **85.5**, color **84**, grain **79**, lighting **76**.
The half-point form increase records a small visible improvement. Working
mean **84.4937%**, holistic **80–85%**. It remains incomplete.
The finial exposure, upright socket wall, base highlight breakup, bowl glints
and some wood-grain directions still differ. Next examine the finial/crown
relationship from the original and side profile before any larger proportion
change. Chavet/Lardy are guides to the whole-set ascending height relationship,
not evidence of authorship or a replacement for the Lichess silhouette.

All material nodes, packed texture bytes, 85 lights, camera and object transform
are unchanged. UVs and topology are unchanged. Six light receivers were
regenerated from the edited control, with their evaluated geometry, UVs, normals
and assignments checked. The saved mesh is closed and manifold. The model's
height/base diameter is unchanged at 2.14451368.

Reproduce from the protected checkpoint-19 archive:

```sh
blender -b --python scripts/queen/profile_study.py -- docs/queen-mission/iteration-020/profile.json --render --samples 256
blender -b --python scripts/queen/validate_finished_queen.py -- --blend build/queen-mission/192-preserved-crest/queen.blend --report-dir build/queen-mission/192-preserved-crest
blender -b --python scripts/queen/check_material_geometry.py -- --baseline history/queen-mission-019/queen-rebuilt.blend --current build/queen-mission/192-preserved-crest/queen.blend --allow-lower-collar --report-dir build/queen-mission/192-preserved-crest
blender -b --python scripts/queen/validate_profile_preservation.py -- build/queen-mission/192-preserved-crest/queen.blend --baseline history/queen-mission-019/queen-rebuilt.blend --out build/queen-mission/192-preserved-crest
```

The saved scene was reopened for 256-sample Cycles acceptance renders and
compared to the published fixed render. See `published-render-check.json`.
Fixed/side renders and the embedded interactive viewer share model `652bc91ad251ca5a4ea183256b45bae31c7cffe69121ba21582103d91617a63c`.
Camera, tab and overlay checks use the simulated DOM/WebGL harness; native
browser inspection was not performed. Browser lighting remains approximate.
The white original was also inspected for geometry; no white finish is claimed.
