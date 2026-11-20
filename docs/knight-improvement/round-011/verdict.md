# Round 11 · Candidate B

I chose B for the way its eye sits under the brow when the knight turns. The old eye resembles a glossy seed with a rim around it. B has two distinct carved surfaces. The broad upper part rolls down to a crescent that grows thinner toward the nose. The two curves are visible in neutral clay and the walnut carries fine grain through the corner of the eye. A gives the cheek a broader reflection and fits several image measurements better. In profile, its steep front corner forms a pointed teardrop. B gives the horse the cleaner expression.

| Knight | Fixed 54° · 45% | Side · 35% | All-around · 15% | Finish · 5% | Weighted / 100 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Parent, round 10B | 94 | 91 | 91 | 86 | 92.10 |
| A | 94.5 | 91 | 91.5 | 86 | 92.40 |
| B | 94.5 | 92.5 | 92 | 87.5 | 93.08 |

These grades express my visual judgment. Black candidate 2 supplies the fine carving detail. I also sampled the original black sprite directly on its 300-pixel grid and at a 100-pixel playing size. From that distance the upper and lower reflections blend. Their position under the brow matters more than the small cuts between them.

## What changed in the eye

In black candidate 2 the two surfaces inside the eye reflect light separately. Across columns 508–516 in the 1,254-pixel reference they peak around rows 481 and 489. B places them at 479 and 488, with a dark interval in between. In A, the two highlights nearer the rear corner land close to the reference at rows 470 and 473. A’s lower cheek follows the source more closely. B’s cheek glint is too concentrated and the nose-side corner is still darker than the reference.

| Measured in the same registered window | Parent | A | B |
| --- | ---: | ---: | ---: |
| Inner eye luminance error against black 2, 0–255 | 15.63 | 14.94 | 13.96 |
| Lower lid and cheek luminance error against black 2, 0–255 | 27.23 | 20.79 | 25.85 |
| Pattern correlation against original at 100 px | .730 | .775 | .755 |
| Luminance error against original at 100 px, 0–255 | 10.96 | 13.35 | 11.51 |
| Exposed inner eye area at 54°, pixels | 1,036 | 1,128 | 976 |

I rendered all three carvings under the released parent’s studio as well as each candidate’s saved lamps. Reinstalling the parent’s studio in a separate copy reproduced the control eye crop exactly. B’s relief stayed visible under a common light. Its saved eye lights produce the stronger pair of reflections at 54°. In A, the lower lid and cheek account for more of the improvement across the whole crop. The common-light mean RGB errors there were 17.25 for the parent, 16.77 for A and 17.76 for B. Both challengers improve with their own studio. The clay and side views show why B won the three-way comparison.

B’s inserts use a gently raised inner surface and a smaller crescent within a matching pair of sockets. The mirrored visible openings overlap by 99.51% in the head’s local coordinates. The evaluated inserts and head each pass their native self-intersection checks. A’s openings overlap by 99.34%. Both candidates produce exactly the parent’s fixed and side silhouette masks. The registered black original outline overlap remains 98.37% and black candidate 2 remains 97.70%. These figures measure outlines.

B adds adjacent cheek grain to both eye UV islands. The change covers 8,032 texels including edge bleed in a 3,072-square atlas. In motion the two eyes reflect the light differently as their surfaces turn. The walnut remains continuous across both flanks. The original silhouette, the centered upper mane and the outside of the muzzle carry through from the parent.

## Next carving

Below the ear, the original has a long dark hollow that separates the mane from the neck. Both black references locate this hollow to within a few pixels. The widest disagreement with our physical join is in the middle, where it lies about 54–55 reference pixels farther into the neck. Some of the current mane has no neck directly behind it. I would reshape both parts together, keeping the sharp upper mane and the outer silhouette. [Mane measurements and native ray sections](mane-to-neck.md)

[Fixed view](fixed.png) · [Side view](side.png) · [Eye in the source and all three models](eye-detail.png) · [Playing-size comparison](eye-native-grid.png) · [Three-quarter views in clay](eye-turns-clay.png) · [Both walnut flanks](paired-walnut.png) · [Studio control](eye-studio-comparison.png) · [Decision fingerprints](decision.json)

## Reproduction

Start from the round-ten Blender scene at commit `3c14cc3`. The A folder contains its sculpt and parent-studio comparison. The B folder contains the sculpt, source measurements, pigment generation, light placement, and a reproduction script. Use the staging layout described in their reports. The parent pigment is `assets/knight/wood-atlas-improvement-008-A.png`. The new packed pigment hashes to `beee98c4ee1af2c55823485a4c0149dea5332c7eaeaa07e06d82ae7022918fe7`. The two gallery images come from reopening the promoted model at 144 samples.
