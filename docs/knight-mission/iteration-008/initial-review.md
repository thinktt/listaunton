# Checkpoint 008 · Starting model

The accepted scene for this reconstruction pass is the round 16A release, recorded in `67ea10d`. It opens on the 54° orthographic camera. The public fixed render, the saved file, and the evaluated viewer mesh agree on source SHA-256 `1a8c2b2384ac360766d3a3121671199f231df21b2ceea6caee22c9ebdb5e9766`. The previous entry in the main mission log, checkpoint 007, predates the sixteen improvement rounds. The four style notes and the mission’s five-category rubric govern this examination. [Prior carving decision](../../knight-improvement/round-016/verdict.md)

## What the pictures show

At board size the swept mane, brow and muzzle give a recognizable likeness. In the full registered view the chest reflection sits on a deeper, smoother channel than the dark central face and narrow edge seen in black candidate 2. The eye catches a longer lower line. The upper mane still has a bright patch at the forehead joint. The plain walnut across the pedestal has less mottling than the selected image. The overall color is close, while several local highlights differ in contrast and position. [Fixed pose](baseline/fixed.png) · [Mane](baseline/mane.png) · [Neck](baseline/neck.png) · [Model profile](baseline/side.png)

The source shows a narrow ledge between the neck and the rounded lip of the base. In profile, the current base rolls upward under the carving. On the exported mesh, the top stays within 0.002 model units of level out to a radius of 0.654. At that same height the neck extends to approximately 1.106 at the front and 1.021 at the back. The level part is covered for all 360 radial sections. That explains why an outline match can coexist with a visibly wrong joint. [Platform in the references](baseline/platform.png) · [Plan view at the seat](platform-parent.png) · [Surface measurements](platform-parent.json)

## Starting scores

| Selected outline | Interior form | Wood color | Grain and texture | Lighting | Equal-weight mean |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 97.73 | 88 | 89 | 79 | 74 | **85.55** |

Outline overlap with the original black sprite is 98.38%, and with the mirrored white sprite it is 97.25%. The outline uses the mission’s filled masks. The four remaining scores are visual assessments. The holistic estimate for the raised view is **83–88%**. On the common foreground the mean absolute RGB difference against black candidate 2 is 13.82 levels out of 255. Median two-pixel luma detail in the turned-base region is 1 level on the model and 3 in the reference. A high outline overlap or close average color does not resolve those interior differences. [Registered measurements](baseline/comparison.json)

Assess the platform, neck and mane in isolation, then inspect any combined result from both saved cameras and the top. Keep the original registration and source images fixed throughout.
