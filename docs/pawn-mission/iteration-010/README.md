# Pawn checkpoint 010

Accepted on 2026-11-12. Trial 056 improves the ball-to-collar contact while
preserving checkpoint 009's geometry, UVs, proportions and 54-degree camera.
The saved model is `27570c1205a59a26d8417d6b88ef32764d14fb664941a5d49bb7d35a212cd87e`.
The mission remains incomplete.

## What changed

Four existing collar reflectors have lower measured powers. A normal-map
refinement affects only the collar's UV band; the older grain relief stays
unchanged. Removing that relief did not solve the coarse reflection pattern.

A smooth band beneath the ball mixes 35% matte wood with the existing
varnished wood. Both are real BSDFs, sharing the same live pigment and final
surface normal. This reduces the unwanted reflected line without removing
secondary glossy light from the entire scene. The original four diffuse and
four glossy bounce depths remain in use.

The two front diffuse lights move down by three degrees around the contact.
This narrows the actual shadow cast by the ball. The camera stays at 54
degrees above the board. A new bounded pigment fit then balances the wood
under that illumination. Diagnostic black/gray renders measure both BSDFs;
they never enter the public beauty images.

## Comparison

| Measurement | Checkpoint 009 | Checkpoint 010 | Selected reference |
| --- | ---: | ---: | ---: |
| Contact brightness-profile RMSE | 7.16 | 3.03 | 0 |
| Darkest contact level | 6.13 | 6.72 | 4.19 |
| Head RGB error | 3.43 | 2.99 | 0 |
| Collar/stem RGB error | 3.65 | 2.98 | 0 |
| Base/foot RGB error | 4.00 | 3.46 | 0 |
| Native original RGB error | 16.40 | 16.50 | 15.74 |

Brightness and RGB errors use a 255-level scale. The contact profile samples
the same physical occlusion edge with unchanged registration. Its darkest
value is still too bright, and recovery six pixels below the edge is 33.60
against 29.09. The lower RMSE does not mean every point improved.

The three head-glint centers remain within 0.92 original sprite pixels.
The slight native-original color regression is an explicit tradeoff for
the closer contact and selected-reference color distribution. Original black
and white silhouette IoU remain 98.50% and 98.14%. The enlargement's narrower
rear flare conflicts with both originals; the model still follows the originals.

| Category | Checkpoint 009 | Checkpoint 010 |
| --- | ---: | ---: |
| Selected silhouette IoU | 96.81% | 96.81% |
| Interior form | 91 | 91 |
| Wood color | 93 | 93 |
| Grain and surface | 92 | 92 |
| Lighting | 91 | 92 |
| Equal-weight working mean | 92.76% | 92.96% |

The four visual ratings are judgments, with an unchanged holistic range of
90–95%. Small alpha-edge differences are sampling effects; exported geometry,
normals and UVs are byte-identical to checkpoint 009.

The collar's left highlight remains too coarse and patchy. A pale lower-head
reflection is still visible at enlarged scale. The stem and socket highlights
differ, and the flare's finest grain remains weaker than the reference.
Unseen wood uses broader inferred grain. Next target the collar's fine
reflection pattern while holding this improved contact and saved lighting.

## Trials and reproduction

`scorecard.json` records all eleven trials and all five scores. Trials 046–049
test diffuse fill and local roughness/polish; none replaces the accepted
result. Trial 051's reduced relief is also rejected. Trials 050, 052–055 form
the measured intermediate steps leading to 056. Rejected material maps are
not offered on the review page.

From the repository root with Blender 5.2.2:

```sh
blender -b --python-exit-code 1 --python scripts/pawn/rebuild_contact_checkpoint.py -- docs/pawn-mission/iteration-010/reproduction.json
blender -b --python-exit-code 1 --python scripts/pawn/validate_contact_checkpoint.py -- docs/pawn-mission/iteration-010/reproduction.json models/pawn/pawn-rebuilt.blend docs/pawn-mission/iteration-010/contact-material-validation.json
blender -b --python-exit-code 1 --python scripts/pawn/validate.py -- .
```

The first command reconstructs trial 057 from archived checkpoint 009 and
tracked inputs without replacing the accepted model. Reopened and independent
replay renders retain identical alpha and differ from the trial by at most
one RGB level. The scope validator checks the original shader graph, real
BSDF coverage, packed maps, collar-only normal edits, six permitted light
changes, unchanged world, ray depths, camera and geometry.

The fixed wood/clay, side views and rotating mesh come from the saved model.
Four-angle studio and neutral-light views are in `orbit-sheet.png`. The viewer
carries the same maps and matte band, with approximate lighting; it does not
duplicate the Cycles studio rig. Page checks exercise texture hashes, matte
uniforms, camera alignment, orbit, pan, zoom, tabs and reference controls.
Native browser GPU verification remains unavailable after the earlier browser
policy rejection of the local file URL; no alternate browser route was tried.
See `site-checks.json` for repository checks and any separate shared-site issues.
