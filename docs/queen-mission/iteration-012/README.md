# Twelfth queen checkpoint: measured pigment refinement

The accepted change refines the actual wood pigment, leaving the closed model,
54-degree camera, UVs, surface relief, roughness and lights unchanged. The
v5 color atlas is baked from pigment only; the final images use the real BSDF.
Hidden and uncertain surfaces retain the previous atlas through the existing
coverage mask. This remains an inferred material, with some residual shading.

## Findings and decisions

The 512-sample diagnostic did not remove the coarse wood pattern. Replacing
medium-scale detail with smoothed pigment lost valid reference detail; both
replacement trials were rejected. Independently smoother coat normals changed
reflections without solving the mismatch, and were rejected too.

Native-resolution black/white BSDF measurements estimate the current shading
response. Subtracting the black response from the reference and dividing by
the white-minus-black response gives a pigment estimate. Strong reflections,
weak responses and boundaries receive low or zero confidence. The first
bounded correction was too weak; wider bounds restored more base markings.

A rendered diagnostic then showed the white-response approximation made the
bowl about 15% darker than predicted because the actual material response is
not perfectly linear. One bounded correction from the actual BSDF render
improved the bowl tone. A small spatial blur prevents fitting isolated sampling
noise. Bright glints stay excluded. The corrected pigment is baked into the
unchanged 2048-square UV atlas, then all fixed and side images are rendered.

The visible improvement is better regional wood tone and more recognizable
base markings, with less coarse color mottling in the bowl. Reflections remain
misplaced and overly harsh. This is a modest accepted gain, not an exact match.

## Scores

Silhouette is measured IoU; all other scores are subjective estimates.

| Checkpoint | Silhouette | Interior form | Color | Grain | Lighting | Working mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Previous, iteration 11 | 97.9612 | 81 | 80 | 77 | 65 | 80.1922 |
| Accepted, trial 119 | 97.9612 | 81 | 82 | 79 | 65 | 80.9922 |

Original-sprite IoU stays 97.9109%. Holistic assessment: 76-81%. All nine
trial scorecards and decisions are in scores.json. Display RGB error decreases
in all four inspected regions; display-errors.json records the coordinates,
common-foreground mask and measurements. Those errors include lighting and
shape, and must not be described as independent fidelity percentages.

## Reproduction

Start from history/queen-mission-011/queen-rebuilt.blend. Its SHA-256 is
1eb382aa47117ded52c6bb32a576fb16c24980d8f68e2f923cf9d0bcc03f19ab.
Use ordinary Python for prepare_light_fit.py, and Blender's Python for the
other steps. Paths below are relative to the repository for scripts that
resolve ROOT themselves; validation --blend and --report-dir require absolute
paths when Blender runs from another directory.

```sh
python scripts/queen/prepare_light_fit.py --size 1254 --directory build/queen-mission/pigment-fit-011
blender -b --python scripts/queen/capture_material_response.py -- --source history/queen-mission-011/queen-rebuilt.blend --out build/queen-mission/pigment-fit-011 --samples 256
blender -b --python scripts/queen/refine_visible_pigment.py -- --source history/queen-mission-011/queen-rebuilt.blend --variant 117-expanded-pigment --lower .25 --upper 4 --weight 1
blender -b --python scripts/queen/capture_pigment_feedback.py -- 117-expanded-pigment
blender -b --python scripts/queen/refine_visible_pigment.py -- --source history/queen-mission-011/queen-rebuilt.blend --variant 118-feedback-pigment --lower .25 --upper 4 --weight 1 --feedback 117-expanded-pigment
blender -b --python scripts/queen/bake_pigment_atlas.py -- --source build/queen-mission/118-feedback-pigment/queen.blend --variant 119-measured-pigment-atlas --texture assets/queen/queen-pigment-albedo-v5.png --reuse-uv
blender -b --python scripts/queen/render_saved_trial.py -- 119-measured-pigment-atlas
```

The initial measured-response render uses 256 samples. Color trials use 128;
the baked, reopened, delivered and side renders use 64. Reference coordinates,
view transform and resolution stay fixed. Black/white and emission passes are
diagnostics; none is a delivered beauty image. Large diagnostic arrays remain
reproducible build outputs rather than additional public candidates.

## Validation and remaining work

The saved atlas was reopened and rendered: its fixed-view RGB difference from
the in-memory render is at most one byte, with a 99th percentile of zero; alpha
is identical. The control vertices, atlas UVs and topology match the prior
checkpoint exactly. The usual closed-mesh, 54-degree, sizing and exact receiver
checks pass. Fixed, side and original comparisons were inspected. The side view
keeps the existing geometry and remains a textured 3D model; inferred texture
and studio lighting still look less convincing from that angle than the guide.

Delivered validation, mesh/camera synchronization, interaction and site results
are recorded with this checkpoint. Browser interaction checks use the existing
simulated DOM/WebGL harness; no native GPU browser inspection is claimed.
At this and every accepted checkpoint, the repository review and existing
Windows local preview are updated together. Refresh review.html to see it.

Next: inspect the excessive relief within the right-base reflection and the
missing fine reflected grain now that pigment is closer. Compare the reference,
neutral geometry and new pigment separately before changing curvature. The
front bowl crescent, rim edges and collar/socket highlights also remain off.
The goal remains active and incomplete. No quota monitor is part of this work.
