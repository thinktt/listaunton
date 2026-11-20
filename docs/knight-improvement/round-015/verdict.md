# Round 15 · The eye beneath the swept ear

**Candidate A wins.** The upper lid describes one smooth arch from the back corner to the bridge of the nose. In profile the eye sits inside the head, and the line stays legible on both flanks under a moving softbox. B gives the closest fixed-camera reflection, but its exposed eye and lower lip form two parallel curves. That double edge grows more pronounced as the horse turns. [Both flanks in wood and clay](eye-portraits.png) · [Three angles in clay](eye-turns-clay.png)

| Model | Reference · 45% | Profile · 35% | Form · 15% | Finish · 5% | Weighted |
| --- | ---: | ---: | ---: | ---: | ---: |
| Parent 14B | 97.1 | 95.7 | 94.0 | 93.5 | 95.97 |
| **15A** | **96.9** | **96.7** | **94.5** | **93.4** | **96.30** |
| 15B | 97.4 | 95.3 | 94.1 | 93.6 | 95.98 |

These are visual judgments of the whole knight. The reference fixes the view at 54°. The profile images use the registered 7° camera. The microscope crops below use the same framing on every model. [Whole fixed view](fixed.png) · [Registered profiles](side.png) · [At board size](board-read.png)

## What changed in the eye

The parent has a small hook directly below the swept ear. At side angles this puts two corners above the rear of the eye. A pulls the underside of the ear back and lets the skull carry the entire middle section of the visible crease. That makes the eye quieter in profile. The visible opening covers 846 pixels in the fixed view, down from 1,090. On independent solid sections about 46% of each eye insert sits inside the head. The measured left and right openings overlap 99.39% after reflection. [Ear, skull and insert at 54°](upper-eye-surfaces.png) · [Native socket measurements](eye-socket-volumes.json) · [A under moving light](raking-eye-near.png)

B keeps the parent’s swept ear and brings the light to (506, 474), close to the peak at (504, 473) in black candidate 2. Its broader, smoother lower-cheek reflection also matches the target more closely. The original sprite’s eye pattern, sampled at 100 pixels for the whole piece, correlates best with B (0.798), followed by the parent (0.784) and A (0.728). B exposes 1,338 pixels of the insert at 54°. Its enlarged surface catches a second long crescent as the horse turns. [Studio comparison](eye-studio-comparison.png) · [Original sprite grid](eye-native-grid.png) · [Opposite flank under moving light](raking-eye-far.png)

A preserves the direction of light-to-dark transitions in 131 of the 164 neighboring original pixels where both references agree. B preserves 115, the parent 106. This measures local edge direction. The sprite correlation above also accounts for the distribution of brightness across the whole eye region. The two tests favor different candidates. In the fixed view A's nasal crease sits closer to the source, but the central glint is softer and the lower cut still shows more brightly than the photographed cheek. [Shared transitions](eye-shared-edges.png) · [Registered reference and model details](eye-detail.png)

A keeps the full 7° silhouette. Fourteen pixels at the far ear cross the opacity threshold in the 54° view after subdivision. The resulting outline overlap is 98.37% against the original and 97.73% against black candidate 2. Both submitted meshes export with seven parts and no degenerate triangles. The parent and both candidates share the studio during the common-light test. Reopening an identical scene gives zero measured difference in its control crop. [Outline check](registered-edge-detail.json) · [Native A verification](A/sculpt-check.json) · [Native B verification](B/verified.json) · [WebGL geometry check](exported-faces-A.json)

## Remaining mane work

The hanging mane retains the sharp geometry and walnut from round 14B. The upper blade above the ear still catches a wide, pale band across its middle. Both black references put a smaller, warmer reflection near its forward shoulder. Separating the studio lamps isolates the rear oval as the main source of the misplaced strip. The next pair should compare a finer physical bevel and a warmer, better placed reflection while checking how the edge holds up in profile and from behind. [The upper mane and its lighting](upper-mane-015.md)

## Reproducing the two carvings

Start in a disposable copy of the project at `108b391`, which contains the parent scene, atlas, studio helpers and both registered parent renders. For each letter, copy the contents of this round’s lettered evidence directory to `build/knight-mission/improvement-015-A` or `improvement-015-B` in that copy. Place these four files in each trial directory.

| Source at 108b391 | Trial filename |
| --- | --- |
| `models/knight/knight-rebuilt.blend` | `parent.blend` |
| `assets/knight/wood-atlas-improvement-014-B.png` | `pigment.png` |
| `assets/knight/render.png` | `parent-wood.png` |
| `assets/knight/guide-render.png` | `parent-side.png` |

A’s assessment lists its sculpt and render commands. B’s PowerShell recipe uses its recorded design number and checks the result in the browser. Both recipes use the original scene’s scale and studio. [A’s recipe](A/assessment.md) · [B’s recipe](B/reproduce.ps1) · [Source checksums](B/support.json)
