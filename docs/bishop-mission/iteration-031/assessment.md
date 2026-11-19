# Bishop 031 — compressed lower turning and a lower upper collar

The owner requested a shorter, fuller base and socket, closer in style to the
king and queen, and a lower upper collar while retaining the 54° reference fit.
The restored tall bishop 030 is archived as the rollback point.

## Accepted shape

The turning above the existing groove is compressed vertically by 12%.
The top socket control moves from height 1.42300 to 1.29424, about 9.0%
closer to the ground. The inner flare is 3.9% wider and the maximum foot
diameter is 0.7% wider. The upper collar crest is lowered by 0.05394 model
units and narrowed slightly so its front rim still registers in the reference.

The upper head moves down only 0.02052 units, and the button dome is refitted.
The first proposal flattened the button too far and was rejected after neutral
side inspection despite its good outline score. The accepted version retains
more rounding. Middle and lower collar controls remain unchanged.

The complete model is **0.72% shorter**: 4.59200668 → 4.55895996.
Its foot is 2.01302004 → 2.02697039 wide. The height-to-foot ratio is about
**1.4% lower**. These are actual saved-mesh dimensions. The local base change
is much larger than the whole-piece height change; a large overall shortening
is not claimed. The camera, scale and reference registration remain exact.

[Neutral before/after](geometry-side-comparison.png) ·
[Fixed reference comparison](comparison/comparison.png) ·
[Head/collar crop](comparison/head.png) ·
[Stem/socket crop](comparison/stem-socket.png)

## Reference fit

| Measured outline overlap | Bishop 030 | Bishop 031 |
| --- | ---: | ---: |
| Original white | 98.5534% | 99.1899% |
| Selected white candidate 3 | 97.0519% | 97.8091% |
| Original black | 97.9130% | 97.8139% |

The original white remains the primary reference. The opposite-color outline
has a small regression. These scores describe the outer mask, not complete
geometry, slit accuracy or finish.

The actual upper front collar rim moves from row 509.30 to 512.54 in the
1254px comparison, nearer the original's blurred edge around row 515.
Middle and lower front rims remain exact. The front base groove moves from
1054.52 to 1056.09, slightly farther below the original's dark line near 1053.
No source image, camera or alignment is changed to obtain these measurements.

The socket highlight and grain still differ from the reference. The inherited
material and light rig were not refitted, and their shading is not proof of
geometry. Neutral side and fixed views accompany the wood comparison.
This is an accepted shape iteration, not completion of the full visual-match
mission or a claim of exact recovered proportions.

## Reproduction

1. `python scripts/bishop/fit_compact_family.py` recreates the accepted
   `compact-family.json` proposal from archived 030. It fits a calibrated
   rotational-envelope approximation against the original outline; actual
   saved-model rendering governs acceptance.
2. `blender -b --python scripts/bishop/profile_shape_trial.py -- docs/bishop-mission/iteration-031/compact-family.json`
   builds `build/bishop-mission/187-compact-family-b`, regenerates render
   receivers, reopens the saved model and renders wood and neutral views.
3. `blender -b --python scripts/bishop/inspect_compact_family.py` measures the
   saved surfaces and renders both models with equal neutral side framing.
   `make_family_comparison.py --iteration 031` builds the side panel.
4. After promoting the checked trial to the current bishop paths, run
   `validate_checkpoint.py` and `render_diagnostics.py` in Blender.
   Refresh comparisons and pages with `compare.py` and `refresh_review.py`.
   The checkpoint collector's explicit `--bounds-evidence` option verifies
   the independently measured shorter/wider dimensions; its default
   unchanged-bounds checks still apply to ordinary local edits.
5. Update the bishop records in the existing set page with
   `refresh_set_entry.py`, and check the bishop viewer/review, shared lineup,
   board sizing and served assets.

The rejected flat-button configuration and images remain in
`rejected-flat-button`; they are not public viewer alternatives.
The accepted configuration changes only declared control positions.
Topology, UVs, cutter, packed textures, materials, lighting and the fixed
54° camera are independently checked against archived 030.
