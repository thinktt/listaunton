# Queen checkpoint 25 — restrained lower-body compression and fuller flare

This checkpoint follows the owner’s side-profile request without sacrificing
the queen’s defining raised socket. It starts from checkpoint 24
(`fdfb52bc…`), which had restored the checkpoint-22 socket shelf and steep
flare drop while retaining the accepted rounded lower collar and finer upper
collar.

## Accepted geometry

- The entire foot-through-socket assembly is compressed **4%** in height from
  the floor through ring 38, then eased back to the unchanged lower-collar
  entry at ring 50. The floor and full model height remain unchanged.
- The socket’s horizontal wall remains horizontal: its straight exposed wall
  changes only from **0.14700** to **0.14112** units. Its radius stays exactly
  **0.56450**.
- The lower flare is given a restrained, continuous swell before the shelf:
  its five profile radii change from
  `0.7940 / 0.6800 / 0.6220 / 0.5990 / 0.5750` to
  `0.8067 / 0.7018 / 0.6469 / 0.6182 / 0.5842`.
  The flare still drops inward continuously into the unchanged shelf.
- The foot, crown, bowl, seated egg, UVs, wood material, lighting, fixed
  orthographic 54-degree camera, and accepted collar refinements are retained.

The goal is a subtly shorter, fuller side silhouette—not a smoothed or
separately tapered socket. The candidate is an interpretation where the
single elevated source view leaves genuine ambiguity.

## Reference fit and tradeoff

At the fixed, unchanged registration:

| Reference | Checkpoint 24 | Checkpoint 25 | Difference |
| --- | ---: | ---: | ---: |
| Original Lichess black sprite | 97.7567% | 97.5207% | -0.2360 points |
| Selected high-resolution detail reference | 97.9356% | 98.0707% | +0.1351 points |

The original Lichess sprite remains the master reference. This change is
accepted only as a small owner-directed side-profile interpretation while
preserving a strong original fit; the source conflict is recorded rather than
hidden. The stronger 6% and 10% whole-assembly compressions were rejected:
the 10% proposal visibly became squat and lost both reference fits.

## Validation

The saved candidate was validated against frozen checkpoint 22 plus the
documented checkpoint-24 collar offsets. It has a closed positive-volume mesh,
no boundary or non-manifold edges, unchanged undeclared control rings, exact
surface/atlas-UV correspondence across six render receivers, and all 82
light-receiver links. The camera remains orthographic at 54 degrees.

`profile.json`, `metrics.json`, `scores.json`, and the generated validation
report record the reproducible shape and its tradeoff. The review assets and
interactive viewer are synchronized from this same accepted model.

The pre-publication candidate digest is
`feca27a170ddf692d516c594a6bff2b9684c0d6a302387471f57319068a033f5`.
The publisher records the delivered active-model digest
`cae7d51be3faf3743a7a1180daa719477b01ba892c216de6e1e4cf8cdd03d5a3`
in `publish-side-shape.json`; `viewer-camera-check.json` independently verifies
the embedded viewer against that delivered model’s saved camera.
