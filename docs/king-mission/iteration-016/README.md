# King 016 · Queen turning and Chavet head

The king now shares the queen’s short socket, rounded shoulder, curved base and stack of thin collars. The head widens from its neck to its rim and has one shallow seat beneath the cross. The Chavet study informed the side profile. The original black Lichess sprite determined the fit at the saved 54° camera. [Chavet photographs](../../../queen-study.html) · [King review](../../../king-review.html)

![Queen, previous king and revised king in profile, registered to equal foot width](profile-comparison.png)

The side plate uses one uniform scale per piece and aligns the feet. This makes the turnings comparable across the two pieces. The gallery retains the owner's chosen set heights.

| Evaluated side-profile measurement | Previous king | Revised king |
| --- | ---: | ---: |
| Socket height, lower wall through stem join | 0.435 | 0.321 |
| Socket diameter at the wall | 1.093 | 1.096 |
| Height between lower and upper collar crests | 0.409 | 0.322 |
| Upper collar height, including its return to the neck | 0.199 | 0.103 |
| Head radius at the neck | 0.459 | 0.417 |
| Head radius at the rim | 0.606 | 0.607 |
| Raised rings beneath the cross | 2 | 1 |

Lengths are in Blender model units. The socket is 26.1% shorter, its diameter changes by 0.3%, and the three collars occupy 21.3% less height between the outer crests. The edited surface and its landmark definitions are recorded in the [measurements](profile-measurements.json).

## Comparison at 54°

![Black Lichess king, selected candidate and revised model in the same registered view](fixed-comparison.png)

| Silhouette intersection over union | Previous king | Revised king |
| --- | ---: | ---: |
| Original black sprite | 96.85% | 96.89% |
| Selected black candidate 1 | 97.83% | 97.56% |

The first transfer put the lowest collar too high and the foot too low, giving 95.58% overlap with the sprite. Adjusting the foot bevel and collar heights recovered the registration. The third pass removed the second seat under the cross. Both final silhouettes include the portion of the cross visible in the source frame.

On the project's visual rubric I rate interior form **86/100**, wood color **82/100**, grain and surface **80/100**, and lighting **69/100**. The collars and cross seat read more clearly from the side. In the registered view, the upper face reflects a broader pale patch than the selected image, the fine reflections around the collar edges are weaker, and the lower-right flare shows a concentrated glint. The stem and foot also have less distinct turned grain. The estimated equal-weight score including selected-image silhouette is **82.9/100**.

## Reproduction and verification

Run Blender 5.2 with `scripts/king/turn_chavet_profile.py` and pass [reproduction.json](reproduction.json) after `--`. It reads the archived king from 014 and the pinned queen from 033. If the queen has advanced, point `queen_source` in a copy of the configuration to the archived file with the recorded hash. The recipe samples the queen’s actual turning, registers individual heights and radii to the king, and saves a new editable scene under `build/king-mission/180-queen-turning-chavet`.

The scope check rebuilt and matched every control vertex at Blender storage precision. The evaluated meridian has no crossings. Two closed components have positive volume. Nine lighting regions match the editable surface, including every corner normal across the socket–stem boundary, before and after regeneration. Two fresh beauty renders have identical alpha and differ by at most one 8-bit RGB level. The exported camera and saved pigment match the source checkpoint. [Validation and reference hashes](checkpoint.json)

Both local viewers passed the rotation, material, side and overlay controls. The whole-set model, height, board and tilt checks passed, and the local server delivered the new mesh, profile and fixed render. The historical height audit still points to older knight files. Its three mismatching paths are recorded with the [delivery checks](delivery.json).
