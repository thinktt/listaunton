# Queen checkpoint 26 — restore the shelf-and-drop baseline

The owner judged the checkpoint-25 base/socket treatment to be a step away
from the intended form while retaining the compact collar treatment. This
checkpoint therefore restores the already validated checkpoint-24 base,
flare, socket, foot and stem while retaining its rounded lower collar and
thinner upper collar.

The raised socket again has its explicit horizontal shelf and steep inward
drop into the flare. It has not been smoothed into a taper. The crown, seated
egg, materials, lights, UVs, source references and fixed 54-degree
orthographic camera are unchanged from the stored checkpoint-24 model.

## Reference fit

At the unchanged registration and masks:

| Reference | Checkpoint 25 | Restored checkpoint 26 | Difference |
| --- | ---: | ---: | ---: |
| Original Lichess black sprite | 97.5207% | 97.7567% | +0.2360 points |
| Selected high-resolution detail | 98.0707% | 97.9356% | -0.1351 points |

The original is the master reference, so the restored profile is the active
working baseline. The 2% outer-shoulder study was fully rebuilt with its real
receiver-light setup but scored 97.4066% / 98.0125%; it is rejected and is not
included in the public review controls.

## Validation and synchronization

`side-shape-validation.json` freshly validates the stored source blend
(`a56b4f7e...`): a closed positive-volume mesh, zero boundary and
non-manifold edges, exact receiver/atlas-UV surface correspondence across six
receiver regions, all 82 checked receiver-light links, and a saved 54-degree
orthographic camera. `publish-side-shape.json` records the delivered active
model (`450314c8...`).

The fixed renders, side renders, embedded WebGL mesh and review-page camera
were regenerated from that same active model. The checkpoint publisher now
prefers scoped side-shape evidence, whose `model_sha256` identifies the actual
staged blend rather than a later repacked active file.
