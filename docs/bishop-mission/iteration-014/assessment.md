# Bishop iteration 014 — collar and fine-relief investigations

The goal remains active. The owner confirmed that no pause is requested.
Checkpoint 013 remains the accepted model and public review. None of the
experiments below produces a convincing overall improvement, so no replacement
is promoted. Checkpoint 013 is now also preserved in `history/bishop-mission-013`.

## Findings

Six fixed-view isolation crops show that much of the collar's broad bright
pattern remains when the head and collar reflectors are disabled. Removing
bump does not recover the reference's narrow, irregular cream arcs. Doubling
the existing collar lamp changes crop RGB error from 5.898 to 5.950 /255.
This supports treating the inherited pigment and the actual reflections as
separate problems; it does not prove the collar geometry is exact.

Twelve measured surface points supply both evaluated geometric normals and
actual shader normals, including bump. Five placements and widths of the
existing collar area light were measured with real BSDF response passes.
Power fits across four warm/neutral tints, then two cooler tints, fail to beat
the accepted crop. The old placement remains the best prediction. These are
response predictions, not accepted beauty renders or fidelity scores.

Twelve localized warm-white spot responses were then measured without changing
any accepted lamp. The constrained fit retains only three nonzero additions.
Trial 112's full 128-sample beauty shows no worthwhile visible improvement:
the front collar remains too smooth and subdued. Its foreground RGB error is
7.1968 versus the accepted 512-sample result's 7.1865; collar error is 6.0215
versus 6.0016. These small differences include sample/denoising variation and
do not establish a meaningful regression or improvement. An independent
reopened audit proves that only the three declared lamps were added.

Trials 114 and 115 replace only the pigment-derived bump input with a 16-bit
height map made from small-scale linear-luminance variation in the current
color atlas. Broad variation is removed from that height input; the color
atlas itself, procedural pores, coat, bump distance and all lights remain
unchanged. The two gains are 2 and 4. Both scenes are saved, reopened and
rendered at 256 fixed samples. Independent audits verify the exact material
node/link scope, packed height pixels and preservation of the remaining scene.

The gentler map slightly breaks up the base glint, but does not reproduce the
reference's fine irregular grain. Collar, stem, socket and foot differences
increase. The stronger map exaggerates local relief without recovering the
missing grain pattern. The broad side/rear color patch persists in both;
fine relief cannot repair that pigment discontinuity. Full images, enlarged
fixed-coordinate crops and actual head/side/rear views were inspected. The
accepted neutral render was also inspected; geometry was not changed.

## Scores and decisions

The fixed camera stays at 54 degrees. Original white remains authoritative,
original black is a secondary shape check, and ungraded white candidate 3
remains the selected detail reference. No source pixel or registration changed.

| Result | Silhouette / placement | Interior form | Wood color | Grain / surface | Lighting | Decision |
|---|---:|---:|---:|---:|---:|---|
| Accepted 013 | 96.11 | 84 | 85 | 77 | 77 | Preserve |
| 112, localized collar lamps | 96.11 | 84 | 85 | 77 | 77 | Reject; no visible gain worth the extra lights |
| 114, fine relief gain 2 | 96.11 | 84 | 85 | 77 | 77 | Reject; local tradeoffs, no clear overall gain |
| 115, fine relief gain 4 | 96.11 | 84 | 85 | 76 | 76 | Reject; exaggerated finish, missing pattern unchanged |

Silhouette entries are rounded measured overlap; the other scores are visual
judgments. Raw masks and original-color overlaps are retained per trial in
`trials.json`. Tiny mask changes at differing samples are not geometry edits.
The accepted working mean remains **83.82%**, with a holistic fixed-view range
of **75–85%**. Neither value establishes an exact reconstruction.

| Diagnostic RGB MAE, /255 | Accepted 013 | 112 lamps | 114 fine relief | 115 stronger relief |
|---|---:|---:|---:|---:|
| Shared opaque foreground | 7.1865 | 7.1968 | 7.1640 | 7.1961 |
| Collars | 6.0016 | 6.0215 | 6.0231 | 6.0452 |
| Socket | 5.7880 | 5.7608 | 5.8273 | 5.8748 |
| Base | 11.0853 | 11.1174 | 10.9779 | 11.0237 |
| Foot | 6.5423 | 6.5282 | 6.5771 | 6.6609 |

Lower fitting loss alone does not justify accepting 114. Its material seam and
the characteristic reflected texture remain visibly wrong. See `details.png`
and each trial's `comparison/` and `views/` evidence.

## Next investigation

Address broad pigment continuity before adding more collar lights. The prior
flat-color trial 100 lost too much regional wood tone; the visibility-protected
fill 104 could not repair a transition that is mostly visible. A different
supported hypothesis is to preserve smooth **height-dependent** wood color
while extending it continuously around each turned ring, retaining bounded
fine observed grain. Compare that against 013 from the fixed and side cameras;
do not silently revive the rejected flat-color or hidden-only fills.

For fine finish, the current generated pigment source lacks some of the chosen
reference's grain. Consider extracting bounded, non-highlight detail from the
authoritative/selected source rather than amplifying a weak atlas. Residual
lighting must not be treated as measured pigment or surface height. Any such
trial still needs actual BSDF renders, reference checks and the five-category
assessment before promotion.

The collar crescents, slit-edge finish, base/button glints and side/rear pigment
boundary remain unresolved. The mission is incomplete. No quota checks, new
agents, publication or push occurred.
