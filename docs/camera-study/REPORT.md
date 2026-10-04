# Shared camera study

4 October 2026. Asked whether independent clues from all six Lichess Staunton pieces can constrain a shared viewing angle.

**A shared elevation around 54 degrees above the board fits the measured original-image features.** The numerical joint optimum is 53.75 degrees on a quarter-degree search grid, but that decimal precision is not physically justified. A practical working bracket is roughly 50–58 degrees. This is a judgment about systematic uncertainty, not a statistical confidence interval or recovered camera metadata.

The rook supplies most of the useful angle information. The other pieces are compatible with this angle, but their partly hidden circles do not narrow it much. The current queen camera (51.5 degrees) and king camera (52 degrees) remain plausible. Their half-degree difference does not explain a substantial difference in their modeled proportions. Neither model was changed for this study.

Open [the illustrated study](../../camera-study.html) to switch between common-angle and independent ellipses. Dashed ellipse portions behind the pieces are extrapolation, not observed edges.

## Evidence and assumptions

Only the untouched original 300 × 300 Lichess PNGs were used for these measurements. White sprites generally show clearer edges and supply one selected trace per piece for the pooled calculation. Black versions were examined as correlated cross-checks. The generated high-resolution candidates and reconstructed meshes did not determine this estimate.

A horizontal circle has projected minor/major axis ratio `q = sin(elevation)` under orthographic projection. This is also an approximation under weak perspective. We assume upright pieces, circular horizontal rings and negligible image roll. Significant perspective, tilted pieces or nonplanar edges would require a more complete camera/geometry model.

For each trace, its ellipse center and radius are free parameters. The combined fit shares only the axis ratio, hence elevation. Points and original-file SHA-256 hashes are recorded in `measurements.json`; `fits.json` contains the resulting ellipses, residual profiles and weighting sensitivity.

## Independent fits

All figures below use the same approximate orthogonal-distance fitting method for comparability. They are best fits of selected visible arcs, **not six independently established camera angles**.

| Piece | Measured feature | Independent optimum | Confidence in angle |
|---|---|---:|---|
| King | Front groove between flare and foot | 59.7° | Low: hidden center and rear arc |
| Queen | Front inter-collar edge | 62.1° | Low: short arc and bevel/shadow ambiguity |
| Bishop | Front inter-collar edge | 55.9° | Low: hidden center and rear arc |
| Knight | Collar beneath horse | 52.5° | Low: partial arc and edge-selection sensitivity |
| Rook | Top rim crest on several battlements | 53.8° | Moderate: separated front and rear sectors |
| Pawn | Front groove between flare and foot | 56.8° | Low: hidden center and rear arc |

The king's entry is a **new original-only base-groove check**, distinct from the earlier 52-degree modeling estimate based on upper-ring interpretation and the selected upscale. It does not establish that the king should use a 60-degree camera.

The ambiguity is measurable. At 52 degrees, the queen's visible-edge RMS residual is 0.312 original pixels; at its independent 62.1-degree optimum, it is 0.288 pixels. A difference of **0.024 pixels** is far below reliable interpretation of the blurred sprite and the physical bevel. Similar small improvements occur for the other incomplete arcs. Their hidden ellipse halves differ much more than the observed fronts.

Exploratory fits based on vertical residuals rather than approximate normal distances return slightly different optima, particularly for the knight and queen. That is additional evidence of weak identification, not competing camera discoveries. The `*-details.json` files preserve these trials and their limitations.

## Combining the clues

The loss is the weighted mean of each trace's mean squared approximate orthogonal edge residual. The rook has weight 1; each incomplete front arc has weight 0.25. These are engineering reliability choices, not inverse statistical variances. Black and white copies of a feature are not counted twice.

The joint optimum is 53.75 degrees. Varying every partial-arc weight from zero to one moves it only from 53.75 to 54.0 degrees. This stability largely reflects the rook's stronger constraint; it does not mean that six equally strong measurements independently converged.

For the rook alone, changing the measured feature from the bevel crest to its outer boundary moves the estimate from 53.8 to 55.9 degrees. Perturbing crest landmarks by 0.75 pixels produces approximately 51.8–55.8 degrees over the central 90% of trials. That trial interval covers landmark jitter only. Bevel geometry and lighting add systematic uncertainty, hence the broader practical 50–58-degree bracket.

Rounded outer collar silhouettes were excluded from the joint fit. On the queen and bishop they suggest apparent elevations around 57–60 degrees, but they are envelopes of a curved surface rather than a single planar circle. Some short-arc fits wander to 70–80 degrees with little change in visible-edge error. Those are failure modes of the inference, not evidence for different cameras.

## Implication for modeling

Use about 54 degrees as a shared camera **hypothesis to test**, while preserving the existing fitted models. The evidence is not strong enough to assert that 52 degrees was wrong, or to justify changing queen proportions solely by changing its camera. A joint render comparison with shared camera settings would need to refit geometry as well, because profile height and camera elevation can compensate for one another.

The earlier explanation of 52 degrees should therefore be read as a useful modeling estimate, not a uniquely measured historical camera angle.

## Reproduce

With Python, Pillow and NumPy, run from the repository root:

```sh
python scripts/camera-study/analyze.py
```

The script verifies original hashes, refits selected source points, regenerates both annotation figures and the residual plot, and rebuilds `camera-study.html`. It does not write source PNGs, models or existing review pages. Source points remain inspectable so future investigators can change edge selection deliberately rather than fitting a desired angle.

Figures were visually inspected. File links, source hashes and output consistency were checked; the local browser automation policy prevents direct file-URL UI inspection.
