# Round 14 · Candidate B

I chose B. In both black references the light crosses one broad, carved face and falls into a narrow hollow where the mane meets the neck. The parent had a second dark arc partway across that face. B removes it and carries short walnut strokes from the neck across the mane. From the side the head reads as one piece of wood. [The two photographs and three knights at 54°](fixed.png) · [Actual side profiles](side.png) · [Mane close-ups](mane-surface-comparison.png)

A also resolves the doubled edge. Its grain runs almost horizontally at the board angle, very close to the selected photograph. Under the rear lights its dense end grain becomes evenly speckled across a large area. B keeps more of the longer figure down the middle of the back. Its bright rear shoulder turns more gradually into the inside face at 54°, which is visible even at playing size. The lower back of B still has a conspicuous change in grain direction. Its deepest shadow is also a little darker than the photograph. [Matched rear and quarter views](back-walnut.png) · [Walnut on both flanks](paired-walnut.png) · [Pigment under uniform emission](back-pigment.png)

| Knight | Fixed 54° · 45% | Side · 35% | Form · 15% | Finish · 5% | Weighted / 100 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Parent, 13A | 96.5 | 95 | 94 | 89 | 95.23 |
| A, new walnut field | 96.6 | 95.2 | 94 | 91 | 95.44 |
| B, grain from the neighboring neck | 97.1 | 95.7 | 94 | 93.5 | 95.97 |

These are artistic grades. The three knights have the same geometry, so their form scores are equal. The grain affects how clearly the shape reads from the side.

## What the photographs show

| Measure | Original black | Black candidate 2 | Parent | A | B |
| --- | ---: | ---: | ---: | ---: | ---: |
| Darkness of the extra arc against its neighbors | −8.4% | −3.7% | 26.8% | −6.3% | −4.8% |
| Brightness on the back third of the broad face | 31.4 | 39.3 | 23.4 | 39.7 | 39.2 |
| Brightness on the inner third | 21.3 | 24.9 | 29.4 | 30.0 | 25.7 |
| Strongest continuous dark marking within the broad face | 2.7% | 6.9% | 26.8% | 6.5% | 6.2% |

Brightness is on a 0–255 scale. A negative arc measurement means the sampled center is brighter than its neighbors. B also brings the average RGB error on the mane down from 8.72 to 6.55 on the original sprite grid and from 10.02 to 5.11 against black candidate 2 on that grid. A scores 9.21 and 7.30 respectively. The original is darker overall and supplies little information about individual pores. It does establish which side of the mane catches the light. [Native sprite and playing size](mane-native.png) · [Brightness across the carving](whole-mane.png) · [Grain detail](mane-grain.png)

The true hollow in B remains within a median of two pixels of the reference on the fixed camera. The median luminance at its deepest point is five, against eight in black candidate 2. The source grain runs about one degree from horizontal in the measured patch. A is within two degrees of that direction and B is within seven. In B the fine pores have approximately the same contrast as black candidate 2. [Registered sample measurements](mane-surface-comparison.json) · [Grain measurements](mane-grain.json)

## What survived the change

I reopened all three scenes and compared the actual vertices, normals, triangle indices, UV maps, varnish values, camera and studio lamps. Both candidates preserve them. Every pixel of both silhouettes matches the parent in the fixed and registered side views. The outline overlap is 98.38% with the original black sprite and 97.73% with selected candidate 2. I checked the material at 253 UV seams across the hanging mane. B’s median RGB step is 2.03 levels across a seam and 2.14 across an ordinary triangle edge. A does particularly well on the small number of seams with a strong color step. [Native geometry and seam checks](uv-continuity.json) · [Contour and neutral-render checks](unchanged-carving.json) · [Clay turn](carving-turns.png)

The accepted model starts at round 13A, commit `a859987`. The frozen B scene has SHA-256 `768e8da32b31736302b3b9b99a747d2a8116aee23887dc227eccd33c233d47fd` and its packed atlas has SHA-256 `f6e6b26fad1baf22bbf7dd0eb0427cb61b9064245af6acbd268d31068502f4c8`. A’s new walnut field and B’s restoration can each be rebuilt from the same parent. [A’s construction notes](A/assessment.md) · [B’s construction notes and reproduction steps](B/REPORT.md) · [Scenes and render hashes](decision.json)

The recipe’s six inputs and shared helpers come from the parent commit and the B folder. Several Windows text files, including the viewer template and original sprite alignment, use CRLF line endings. Converting their Git copies to CRLF reproduces the recorded digests.

The eye still has a break in the sweep of its upper lid. The central reflection sits lower than it does in either photograph. [Eye close-up and measurements](eye-corners-014.md)
