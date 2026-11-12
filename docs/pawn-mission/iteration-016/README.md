# Pawn checkpoint 016

The foot reflections are warmer and less pale. Trial 100 changes the color
and power of five existing foot lights, preserving the dedicated front light
because its earlier hue was closer to the authoritative original. Geometry,
the 54-degree camera, pigment, normal/finish maps and the groove-polish mask
are unchanged. The mission remains incomplete.

## Evidence and rejected approaches

Study 090 isolates all 44 lamps, the world and secondary glossy paths in
the lower band. Study 091 removes the three relief layers individually and
together. Removing relief worsens the largest foot patch: RGB error rises
from 14.32 to 22.72 levels with all relief disabled. The accepted finish
retains every layer. These cropped diagnostic values differ slightly from
full-frame values because adaptive sampling and denoising see different crops.

The geometric rays in `baseline-rays.json` show that the missing inner
groove line reflects close to the horizon. Existing foot sources are above
that direction. The material also reduces polish inside the recess. These
observations motivate tests; they do not establish the original lighting or
prove that the inferred groove profile is correct.

Trial 093 adds a low ribbon reflector, and trial 094 refines its aim/size.
Both create a second outer-foot glint. Study 095 tests stronger polish on
two existing groove-ramp knots, with full, quarter and zero ribbon energy.
Trial 096 uses a closer, narrower-spread ribbon plus that polish adjustment.
It partially restores the inner line, but retains an unsupported second
outer glint and worsens the overall base/foot error. All three full models
are rejected. The public model has no extra lamp or altered groove mask.
The actual sampling comparison also verifies that this was not a changed
seed, adaptive threshold or denoiser masquerading as a lighting result.

Trial 097 measures separate RGB-power responses for six existing foot
sources and makes bounded color adjustments. Trial 098 takes a smaller
second step. Both preserve the reflected grain while reducing the pale
cast. Original and selected right/left highlights support warmer color.
The original front arc was closer to its previous hue, so trial 100 starts
from checkpoint 015 and applies only the other five final color changes.
The source positions, dimensions, directions and visibility are unchanged;
the other 39 lamps, including the front-foot source, are exact.

## Comparison and tradeoffs

| Measurement | Checkpoint 015 | Checkpoint 016 |
| --- | ---: | ---: |
| Base/foot common-foreground RGB error, 0-255 | 2.724 | 2.640 |
| Right-foot patch RGB error | 8.790 | 7.011 |
| Left-foot patch RGB error | 7.579 | 6.642 |
| Largest groove/foot patch RGB error | 14.126 | 12.524 |
| Foot-line fine-pattern correlation | 0.9294 | 0.9295 |
| Foot-line fine contrast | 25.64 | 25.76 |

The selected foot-line contrast is 30.45, so its fine structure remains
too soft. Right-arc bright-pixel RGB/luma changes from approximately
[1.181, 0.979, 0.859] to [1.323, 0.961, 0.753], against the selected image's
[1.329, 0.969, 0.727]. Its original-sprite color is warmer still. The left
arc moves toward both sources but remains too pale. These are descriptive
display-color measurements, not linear reflectance or recovered lamp colors.

Preserving the front source brings that patch's RGB/luma back toward the
original: from trial 098's [1.825, 0.907, 0.352] to trial 100's
[1.775, 0.904, 0.412], versus original [1.719, 0.916, 0.443]. It gives up
some selected-image accuracy there. Other foot sources still contribute,
so retaining one lamp does not make the entire front patch identical.

Native original RGB error rises from 16.63 to 16.69; the selected enlargement
itself measures 15.74. This small error increase accompanies the visibly
closer right/left hue and is recorded rather than hidden. The inner groove
line remains missing, with its patch error slightly worse at 13.36 versus
13.30. Head/contact profile error stays 3.45; its dark core stays 6.64 against
4.19 in the selected image. Upper finish and geometry remain unchanged.

| Category | Checkpoint 015 | Checkpoint 016 |
| --- | ---: | ---: |
| Selected silhouette IoU | 96.81% | 96.81% |
| Interior form | 91 | 91 |
| Wood color | 93 | 93 |
| Grain and surface | 94 | 94 |
| Lighting | 92 | 92 |
| Equal-weight working mean | 93.36% | 93.36% |

The four visual ratings are judgments; the holistic range remains 90-95%.
Original black/white IoU remain 98.499%/98.135%. The local color gain is not
enough to raise the whole-piece ratings. The groove line, extra edge under
the flare, fragmented stem highlight, collar gaps and inferred rear grain
remain unresolved.

Next inspect the groove and outer-foot meridian together. The low-reflector
tests produce two glints where only one is wanted; compare the surface
normals at those locations and the original profiles before considering a
bounded turning change. Preserve the accepted overall dimensions, source
registration, head/collar/stem finish and camera. Do not adopt the rejected
extra-light or groove-polish variants as current models.

## Reproduction and validation

From the repository root with Blender 5.2.2:

```sh
blender -b --python-exit-code 1 --python scripts/pawn/rebuild_collar_finish.py -- docs/pawn-mission/iteration-016/reproduction.json
blender -b --python-exit-code 1 --python scripts/pawn/validate_local_surface.py -- docs/pawn-mission/iteration-016/reproduction.json models/pawn/pawn-rebuilt.blend docs/pawn-mission/iteration-016/surface-validation.json
blender -b --python-exit-code 1 --python scripts/pawn/validate.py -- .
```

The independent replay starts from archived checkpoint 015, reloads the
unchanged packed maps and applies the five explicit lamp-color rows.
`checkpoint.json` records actual saved-file/replay comparisons. The extended
scope check verifies all surface-map pixels, the complete live shader graph,
mesh/normals/UVs, sampling and denoiser settings, world, ray depth and every
lamp. The previous localized-map checkpoint also passes the extended check.

Fixed wood/clay renders, the foot-registered side view and rotating assets
are rebuilt from the same saved model. Four-angle studio and neutral-light
renders are recorded in `orbit-check.json`; page checks are in
`site-checks.json`. Sources, selections and gallery defaults are unchanged.
The whole-set model check stops on an unrelated king model/page hash
mismatch in the working tree. The unchanged pawn section passes separately;
`check_pawn_model_site.py` records exactly that narrower scope. The full-set
failure is retained in the report rather than reported as a pass.
Native browser GPU appearance remains unverified after the earlier local-file
policy rejection; no alternate route was attempted. Browser lighting remains
an approximation of the actual Cycles rig.
