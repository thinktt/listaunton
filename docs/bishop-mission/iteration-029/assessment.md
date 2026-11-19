# A stockier bishop at the original 54° view

The owner asked for a shorter, stockier bishop that still lines up with the Lichess original. The starting shape is the restored bishop 024. The original white sprite sets the outline and feature positions. Selected white candidate 3 supplies finer surface detail.

The waist measures **0.594** units across, up **9.8%**. The socket-to-collar span measures **1.241** units, down **12.5%**. The stem broadens into the underside of the lower collar while its outer edge still reads as a thin turned plate. Both level views use the same floor and scale. [Level profiles and colored outlines](side-comparison.png)

| Measurement | Restored bishop | Stockier bishop |
| --- | ---: | ---: |
| Overall height, model units | 4.5920 | 4.5610 |
| Foot diameter, model units | 2.0130 | 2.0130 |
| Height relative to king, fixed board ruler | 82.69% | 82.14% |
| Minimum evaluated stem diameter | 0.5412 | 0.5939 |
| Span between socket and lower collar controls | 1.4182 | 1.2413 |
| Original white silhouette overlap | 98.774% | 99.111% |
| Original black silhouette overlap | 97.827% | 98.058% |
| Selected white 3 silhouette overlap | 97.035% | 97.469% |
| Slit centerline mean error, native image pixels | 5.86 | 1.14 |
| Visible slit end, pixel x × y | 506 × 428 | 512 × 421 |
| Mean error across three front collar arcs, pixels | 3.24 | 0.04 |
| Front groove row, optical source near 1053 | 1046.4 | 1053.5 |

The entire piece is **0.68%** shorter. The waist and the transition into the collar account for most of the visible difference in profile. At 54°, the lower collar hides much of the upper shaft. Rings near the lower exposed waist still determine a short stretch of the original outline. Fitting that stretch separately made it possible to widen the stem in profile. The measurements use the reopened Blender mesh, including the cut surface. The original camera matrix, orthographic scale, sprite registration, sole and maximum diameter are identical to the restored fit. [Original, enlargement and both models](fixed-comparison.png) · [Native measurements](measurements.json)

## What the image constrains

At the former 74.5%-of-king height, even a centered, perfectly flat circular button would need to be at least 284 pixels wide in the saved frame to reach the top of the original. The source button is about 134 pixels wide. This bound follows from the fixed camera, sole and scale. The earlier shorter model left its button 68 native pixels below the original top. The accepted model places its first visible button pixel at row 160 against the antialiased original silhouette starting around row 156. Its front boundary ends at row 270. [Button comparison](button-comparison.png)

## Finish and remaining differences

The wood uses the restored material and atlas. The two real specular lights linked to the button were refitted because lowering its dome changed its reflections. The model's slit is still harder edged than the sprite. The warm socket and foot highlights and the grain spacing also differ. On a 0–255 scale, mean absolute RGB error over the body against original white was 19.1 before and 20.8 after. The button went from 14.6 to 16.3. These color measurements compare the model at the original sprite's sampling scale. The outline percentages measure shape alone.

## Reproducing the accepted model

Run Blender in background mode with `scripts/bishop/profile_shape_trial.py`, passing `docs/bishop-mission/iteration-029/profile-fit.json` after `--`. The file pins the source blend hash and enumerates the actual turning, saw placement and finial reflectors. The renderer saves and reopens the new blend before producing both wood and neutral images. The contour comparison, first-hit slit and button labels, level measurements and serving checks provide independent verification. [Saved fit](profile-fit.json) · [Stem studies](stem-proposals.json) · [Measurement detail](validation/served.json)
