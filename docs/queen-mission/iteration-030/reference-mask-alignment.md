# Registered source-mask audit

This is a diagnostic comparison between the unmodified registered original
black Lichess sprite and the selected high-resolution reference.  It does not
alter, retouch, or re-register either image.  It asks a deliberately narrow
question: within each fixed crop, what integer translation in the range
`-5..+5` pixels would maximize the two existing silhouette masks' IoU?

| Crop | Baseline IoU | Best local IoU | Best local shift | Gain |
| --- | ---: | ---: | --- | ---: |
| Whole piece | 98.214% | 98.330% | +2 px X, 0 px Y | +0.116 pp |
| Crown | 98.316% | 98.429% | +1 px X, 0 px Y | +0.114 pp |
| Collars | 97.962% | 98.573% | +1 px X, +3 px Y | +0.612 pp |
| Socket / stem | 98.355% | 98.523% | +2 px X, -1 px Y | +0.168 pp |
| Base | 98.351% | 98.578% | +2 px X, 0 px Y | +0.227 pp |
| Foot | 96.943% | 97.261% | +2 px X, +1 px Y | +0.319 pp |

The selected image is extremely close to the original at the whole-piece
level, but it contains small local differences rather than a single uniform
translation.  In particular, the collar region's +3-pixel local vertical
preference means that a model change which helps the selected image there can
be a registration/style difference rather than recovered geometry.  The base
does not show that vertical preference, so its source conflict remains a real
shape interpretation issue rather than a simple vertical registration error.

This audit is explanatory only.  All reconstruction comparisons continue to
use the existing fixed registration and unchanged source pixels; the original
Lichess sprite remains the master geometry reference.
