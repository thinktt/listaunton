# Pawn side-view quality

The owner requested a new side-view quality goal on 2026-11-18: study standard
Staunton pawns, make this pawn look convincing and finely finished from the
side, and preserve its already successful reference-view match. This is a
separate aesthetic assessment from the original fixed-view match score.

The starting accepted model is checkpoint 017, SHA-256
`0d0f9c2649fbd209eaf5817c4d51256ca1b49f4587adc278cee29744bab6a4a6`.
Checkpoint 018's rejected collar experiments are not the starting model.
The camera constraint remains orthographic, 54 degrees above the board.
Current gallery relationships come from `assets/side-views/defaults.json`;
do not restore obsolete slider values from earlier work.

## Side-quality rubric

These are visual judgments, not measurements or recovered historical facts.
Score at full-piece viewing size and in close detail, with neutral clay and
wood, using the same framing and a common lighting setup when comparing form.
Do not give geometry credit for lighting alone. Inspect several side/rear
azimuths before declaring the material complete.

| Criterion | Weight | What a high score requires | Starting score |
| --- | ---: | --- | ---: |
| Profile and proportions | 30% | Balanced head, collar and stem; a poised, recognizably Staunton outline | 68 |
| Turned details | 15% | Intentional edges and transitions; refined base and groove; no swollen or pinched bands | 60 |
| Wood continuity | 20% | Believable grain and color over the whole piece, without projected shadow stripes or abrupt patches | 48 |
| Surface finish | 15% | Crisp but restrained pores and varnish; polished wood rather than melted plastic | 62 |
| Lighting and form | 15% | Readable curvature, coherent highlights, open shadows and no unexplained bright spots | 52 |
| Seating and presentation | 5% | Ball seated in its collar; level, stable foot and useful framing | 75 |
| Weighted side-quality score | 100% | | **59.85 / 100** |

The starting holistic judgment is approximately 55–65/100. In particular,
the base has a deep pinched waist, the socket is a long cylindrical interruption,
and the reference-fitted material/light combination looks patchy and dark
from the side. The head/collar seating and overall dimensions are useful
foundations to retain. This does not reduce the separate fixed-view match
score recorded in checkpoint 017.

A practical finishing target is at least 90/100 overall, with no category
below 85 and no obvious defect at ordinary viewing size. Scores cannot be
rounded up to declare success. Final acceptance also requires the original
view to remain convincing and the model to remain usable from other angles.

## Reference-view guard

Compare every accepted change at unchanged registration against both original
Lichess colors and selected black candidate 2. Retain the original source
pixels and the established filled-silhouette mask convention. Record outline
overlap separately from full-color and feature comparisons. Do not silently
trade away a matched head, collar reflection, socket arc or foot line merely
because an average score remains high. The current geometry and 47-light
reference rig are the baseline; a side presentation studio is a separately
identified lighting setup on the same geometry and material.

## External visual research

The external pieces are style guides, not replacement ground truth or evidence
that the Lichess artist used a particular physical set.

- [British Chess Sets, early Jaques set entered No. 8](https://www.britishchesssets.com/chess/No8/index.html): its row of original boxwood pawns shows a thin foot, a comparatively low molded base, a clean concave stem and a distinct thin collar.
- [Dermot Rochford collection, early Jaques 3.5-inch set](https://www.chessantiquesonline.com/rochford_collection/secbig/Jaq1406.html): the pawn photograph shows the same restrained base transitions with small individual variations.
- [Chessbazaar Player Series](https://chessbazaar.com/products/the-player-series-staunton-chess-pieces-in-sheesham-wood-boxwood-3-0-king-extra-queens): the contemporary product photographs provide additional wood, turning and proportion examples. The published pawn dimensions are 40 mm tall and 23 mm across the base; these are not dimensions to impose on our piece.

The photographs were visually inspected locally after the web image fetcher
returned cache misses. Their URLs and hashes are recorded in the private
research cache. Third-party photographs are not incorporated into the public
model textures or reference gallery. The existing generated side guide remains
an interpretation, and the Lichess sprites settle conflicts.

## Current work

[Side checkpoint 001](iteration-001/README.md) accepts a separate saved side
studio and a 1254-pixel profile render. It retains checkpoint 017's exact
geometry, wood, finish, UVs and reference rig. The side-quality score improves
from 59.85 to 64.85/100 through lighting and presentation; no geometry or
material improvement is claimed. The reference render is visually unchanged.

Thinner-collar, compressed-base, shallower-groove, smoother-socket and hidden
wood experiments were rejected. The collar looked better from the side but
displaced its reference highlight. Local light fits failed to recover it.
Hidden grain completion did not solve the visible projected texture boundary.

The most useful finding is the difference between the front and rear under
the same studio: the unseen rear has continuous grain, while the front carries
patches and dark boundaries inherited from fitting the reference. A pigment-only
diagnostic confirms that some of these features are embedded in the color atlas.
The next step is to separate that broad illumination from the pigment while
retaining the reference's fine grain, then test a coherent real lighting fit.
Larger geometry changes need material transfer and reflection checks together.
Do not repeat the rejected profile edits alone or accept silhouette scores as
proof that the collar reflection has survived. The goal remains active.
