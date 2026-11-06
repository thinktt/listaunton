# Queen checkpoint 18 — raised flare and compact socket

The Lichess queen has a fuller inner flare that climbs around the stem socket. The previous turning left a broad cylinder standing above it. This edit changes meridian rings 24 through 34. The rounded shoulder now meets the stem at its previous height, while the flare rises from below to shorten the exposed socket.

| Control-profile measurement | Previous | Revised |
| --- | ---: | ---: |
| Height where the inner flare meets the straight wall | 0.8547 | 0.9440 |
| Socket diameter | 1.1935 | 1.1290 |
| Exposed socket height from flare to stem seat | 0.4547 | 0.3654 |
| Straight section of that wall | 0.2435 | 0.1470 |

The measurements use Blender units on the editable profile. The diameter decreased 5.4%, the overall exposed height decreased 19.6% and its straight section shortened 39.6%.

The stronger test curve revealed the old lighting split as a line across the flare. The accepted build carries that boundary with the same surface faces. It verifies their atlas coordinates in each of the six light groups. The new surface slope required a softer base reflection and right socket glint. The long base light runs at 42% of its former power and the existing right socket spot at 20%. The packed walnut atlas is v9.

The camera stayed at the assumed 54° elevation throughout fitting. At identical registration, outline overlap measures 97.9122% for the original and 97.9657% for the selected high-res. Against checkpoint 17, lower-body RGB mean squared error fell 8.2% for the original and 4.7% for the high-res. See `socket-image-check.json` for the crop and blur settings. The shape and material remain interpretations from a single elevated view. The right-hand strip on the flare is smoother and more continuous than the broken highlight in the references.

Visual estimates are 84 for interior form, 84 for color, 79 for grain and 76 for lighting, on a 100-point scale. The previous form estimate was 82. `scores.json` includes the rejected rendered trials. `original-socket.png`, `high-res-socket.png` and `socket-side.png` show the comparisons.

Run the following from the project root to recreate the trial and reproduce the comparisons.

```sh
blender -b --python scripts/queen/refine_socket_flare.py -- docs/queen-mission/iteration-018/profile.json
blender -b --python scripts/queen/render_saved_trial.py -- 183-raised-flare-short-socket
python scripts/queen/compare_socket_flare.py --out build/queen-mission/junction-comparison
```

The closed control, the six render surfaces, camera, UVs, packed wood, permitted light changes, site and interactive camera checks passed. Current and Previous on the review page show checkpoints 18 and 17. The rotating viewer uses the accepted geometry with its browser material preview.
