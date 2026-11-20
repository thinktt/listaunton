# Checkpoint 008 · Knight carving and walnut finish

The accepted knight has a three-faced mane with lightly softened edges and a continuous sweep to the base. Three shallow faces now describe the front of the neck. The turned base supports the carving on a level platform. In the model profile, a narrow ledge is visible in front of and behind the neck. The fixed camera is 54° above the board with 12° yaw. The second view is the actual model rendered from 7° elevation. [Fixed camera](fixed.png) · [Side profiles](side.png) · [Registered comparisons](comparison.json)

| Measure | Earlier model (16A) | Accepted (043) |
| --- | ---: | ---: |
| Filled silhouette overlap with black candidate 2 | 97.73% | 97.87% |
| Interior form | 88 | 92 |
| Wood color | 89 | 89 |
| Grain and surface texture | 79 | 79 |
| Lighting and reflections | 74 | 74 |
| Equal-weight mean | 85.55 | 86.37 |

The selected silhouette is measured. The remaining four scores are visual assessments. The separate holistic estimate is 84–88%. Using the same camera and registration, original black sprite overlap rose from 98.38% to 98.54%. Mirrored white overlap slipped from 97.25% to 97.19%. The common-foreground mean absolute RGB error against black candidate 2 rose from 13.81 to 14.62 levels out of 255. The clearer carving and physical ledge are the reasons for accepting this checkpoint. [Starting assessment](initial-review.md) · [Scorecard and release verification](scorecard.json)

The level platform extends beyond the combined footprint of the mane and neck at all 360 sampled angles. At a vertical tolerance of 0.00001 model units, the smallest margin is 0.0534 units, with 0.0535 at the front and 0.1069 at the back. Native triangle checks confirm that both the mane and neck enter the platform. [Seating measurements](replay/native-seating.json)

The first combined carving caught a broad, pale patch on the mane and a second gold line on the platform. Trial 043 darkens the mane cap, picks out the forward bevel in warm light, and reduces the two collar-strip lights. Against candidate 2, the platform crop’s RGB error fell from 13.49 in trial 042 to 11.82. The turned base still looks smoother than the reference. The eye has a stronger lower edge, and the front neck lacks the clean, narrow highlight visible in both black references. Address the chest reflection next and recheck the grain through the full turn. [Mane](mane.png) · [Platform](platform.png) · [Chest](neck.png)
