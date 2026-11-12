# Pawn checkpoint 012

Trial 065 restores finer grain breaks in the flare and foot reflections.
The accepted model keeps checkpoint 011's geometry, pigment, contact setup,
44 lights and orthographic 54-degree camera. The full visual-match mission
remains incomplete.

## Changes and comparison

Nine actual roughness/polish responses and a second sampling seed establish
the finish adjustment. Seventeen actual tangent-normal responses establish
the smaller surface changes. Both studies use the accepted 512-sample,
seed-0, light-tree-disabled setup. The surface band comes from the saved
meridian and camera/depth projection, rather than an arbitrary image mask.
Only visible, supported measurements alter the maps. The finish changes
1.231% of its atlas and the normal map changes 1.206%. Both maps are byte
identical outside UV height 0.19–0.42; the head and collar maps remain intact.
The bounded normal range remains 0.135 (about 7.69 degrees).

The atlas's encoded roughness gain remains 0.30–2.40 and polish gain remains
0.38–1.85. The recovery report also records unconstrained fitted proposals;
values beyond those ranges are clamped when encoded. No new emission,
billboard or screen-space composite is used in the shaded model.

| Fine reflection | Pattern correlation, 011 | Pattern correlation, 012 |
| --- | ---: | ---: |
| Broad left flare | 0.884 | 0.938 |
| Thin flare line | 0.663 | 0.869 |
| Foot line | 0.861 | 0.929 |

Foot-line fine contrast increases from 21.4 to 25.6 against 30.4 in the
selected detail image. Thin-flare contrast increases from 22.9 to 24.3
against 29.4. The enlarged patches in `065-reflections.png` show both the
closer pattern and the remaining softness. Base/foot common-foreground RGB
error falls from 3.14 to 2.76 levels. Upper-head correlation stays 0.904;
the three collar patch correlations remain about 0.815 / 0.825 / 0.871.

Trial 066 warms and strengthens three existing foot reflectors. It brings
the selected highlight hue a little closer, but original-sprite color error
increases to 16.66 from 16.60 and foot-pattern correlation falls to 0.924.
That small selected-view gain does not justify altering the accepted rig;
the light experiment is rejected. Its configuration and comparisons remain
research evidence, not a public alternative.

## Assessment and limits

| Category | Checkpoint 011 | Checkpoint 012 |
| --- | ---: | ---: |
| Selected silhouette IoU | 96.81% | 96.81% |
| Interior form | 91 | 91 |
| Wood color | 93 | 93 |
| Grain and surface | 93 | 94 |
| Lighting | 92 | 92 |
| Equal-weight working mean | 93.16% | 93.36% |

The four visual ratings are judgments, with the holistic range held at
90–95%. The model retains the original's broader rear flare where the
generated detail reference disagrees. Original black and white silhouette
IoU stay 98.499% and 98.135%. Native original RGB error remains 16.60 at the
reported precision; the selected enlargement itself measures 15.74. The
head/contact brightness-profile error changes slightly from 3.44 to 3.48
levels, while its dark core stays 6.53 against the selected image's 4.19.

The collar still has coarse patches and an imperfect lower-head reflection.
Stem/socket highlight shape and the foot's highlight warmth remain short
of the selected image. Some fine contrast remains too soft, and the hidden
wood is inferred and broader. No score establishes recovered unseen form.
Next examine the stem/socket reflections and remaining collar residuals
while retaining the improved lower finish and accepted lighting.

## Reproduction and verification

From the repository root with Blender 5.2.2:

```sh
blender -b --python-exit-code 1 --python scripts/pawn/rebuild_collar_finish.py -- docs/pawn-mission/iteration-012/reproduction.json
blender -b --python-exit-code 1 --python scripts/pawn/validate_local_surface.py -- docs/pawn-mission/iteration-012/reproduction.json models/pawn/pawn-rebuilt.blend docs/pawn-mission/iteration-012/surface-validation.json
blender -b --python-exit-code 1 --python scripts/pawn/validate.py -- .
```

The replay starts independently from archived checkpoint 011 and tracked
maps. `checkpoint.json` records the saved model hash and actual reopened /
replayed image differences. The scope validator checks the complete live
BSDF graph, prior relief, pigment, map pixels and permitted surface band,
geometry/normals/UVs, all lights, world, ray depth and sampling. The source
images and side-gallery defaults remain unchanged.

Fixed wood/clay, side comparison and rotating mesh are regenerated from the
same saved model. Four angles under both the real rig and neutral inspection
light check the surface away from the fitted view. Repository and viewer
code checks are recorded in `site-checks.json`. Native browser GPU inspection
remains unverified after the earlier local-file URL policy rejection; no
alternate browser route was attempted. The browser uses matching maps with
approximate real-time lighting, rather than the full Cycles rig.
