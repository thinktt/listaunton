# Queen checkpoint 27 — support the lower foot

A fixed-camera contour audit of checkpoint 26 isolated the remaining repeatable
outer-boundary difference to the lowest foot: at its bottom edge the model
closed inward slightly sooner than both registered source silhouettes. The
raised socket, its explicit horizontal shelf and steep inward flare drop were
not the cause and are preserved exactly.

The accepted adjustment is intentionally restrained. It broadens only control
rings 2–9 of the foot support, with a peak radial change of 0.009 Blender
units at ring 5. It produces a slightly flatter, better-supported rim without
adding a separate bulb. Ring 1, rings 10–11, and every ring from 12 upward
remain unchanged; the flare, socket, stem, collars, crown, seated egg,
material, lights, UVs, source registration and saved 54-degree orthographic
camera are retained.

The reproducible staging tool is `scripts/queen/study_foot_lip.py`. Its
accepted invocation was:

```sh
blender -b --python scripts/queen/study_foot_lip.py -- \
  --variant 235-foot-lip-half-strength --peak-delta 0.009 --samples 64
```

## Reference fit

The table uses the unchanged mask convention and the published, saved active
render. The original Lichess sprite remains the master reference.

| Reference | Checkpoint 26 | Checkpoint 27 | Difference |
| --- | ---: | ---: | ---: |
| Original Lichess black sprite | 97.7567% | 97.8523% | +0.0956 points |
| Selected high-resolution detail | 97.9356% | 97.9622% | +0.0267 points |

A stronger 0.018-unit version gave the original a larger improvement
NaN
NaN
NaN
0
NaN
0
NaN
NaN
NaN
NaN
NaN
0
NaN
NaN
NaN
NaN
NaN
