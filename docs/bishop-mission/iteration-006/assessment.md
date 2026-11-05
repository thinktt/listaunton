# Bishop iteration 006 — a softer slit termination

Starting checkpoint: `361fb05`, preserved in `history/bishop-mission-005`.
The original white sprite remains authoritative and ungraded white candidate 3
remains the selected detail reference. This is a small geometry revision at
the existing 54-degree camera, with the accepted material and lighting retained.

## Examination and hypothesis

The prior render ended its mitre slit with an angular triangular facet. The
same facet was visible in neutral clay and the level head view, establishing
that it was a geometry issue. The high-resolution reference shows a softer,
rounded taper. The original white sprite supports that reading, though its
resolution cannot establish the exact cut profile. The darker original is
less conclusive. A rounded termination is an interpretation of this evidence,
not a recovered construction detail.

The trial replaces the flat bottom of the editable saw-cut volume with a
semicircle. Parallel sides, the original slit angle and width, and the cutter's
transform are retained. Its floor extends down by half the slit width. The
cut still passes through the full head thickness and stops above solid wood.
The head, button, collars, stem, socket and foot controls remain unchanged.
The change is confined to the slit region, with no adjustment to framing or
gallery proportions.

## Trials and scorecard

Scores below are silhouette / interior / color / texture / lighting.

| Trial | Scores | Decision |
| --- | --- | --- |
| 042 elongated rounded floor | 96.20 / 83 / 85 / 77 / 72 | Removes the angular floor; a little more extension than needed. |
| 043 circular floor, doubled bevel | 96.20 / 83 / 85 / 77 / 72 | No convincing benefit from the larger bevel; do not retain that extra edit. |
| 044 circular floor, original bevel | 96.20 / 83 / 85 / 77 / 72 | Chosen for the local shape improvement with the original edge treatment. |

| Metric | Previous | Current |
| --- | ---: | ---: |
| Outside silhouette and placement | 96.20 | 96.20 |
| Interior shapes and carved details | 81 | 83 |
| Wood color and tonal variation | 85 | 85 |
| Grain pattern and surface texture | 77 | 77 |
| Lighting and reflections | 72 | 72 |
| Equal-weight working mean | 82.24 | 82.64 |

Only silhouette is measured IoU. Other percentages are subjective visual
assessments; the mean is a progress indicator, not a probability of fidelity.
Holistic fixed-view appearance remains approximately **75–85%**. The localized
improvement merits a modest interior-shape increase, not an increase in the
unchanged material or lighting scores. At 96 samples the selected and both
original silhouette IoUs equal checkpoint 005 exactly. The silhouette mask
fills holes, so it does not measure this slit improvement.

There is a small tradeoff in the pixel diagnostic: shared-foreground mean RGB
error rises from 7.14 to 7.17 /255, and the head crop from 6.88 to 7.03 /255.
The newly rounded cut is still missing the reference's local reflected light.
The trial is retained for its more plausible, visibly smoother termination;
it is not presented as an improvement in every pixel or in lighting. The
unchanged base crop remains at 9.25 /255.

## Validation and delivery

The final trial is saved and reopened before its actual 96-sample, 1254-square
Cycles render, using the same Principled materials and Standard sRGB view.
The scope audit checks the exact cutter geometry against its declared profile,
closed positive-volume meshes, an open slit and solid floor, unchanged camera,
control meshes, UVs, materials, packed image data, world and lights. Evaluated
surface samples outside the local cut region are compared in both directions.
The existing anatomy checks still guard the continuous head and broad, gap-free
button contact. Exact results and hashes are recorded in `checkpoint.json`.

The persistent mission validator explicitly recognizes the declared slit
revision and runs the additional scope audit. It continues to reject other
control, topology or modifier changes. Later intentional material work can
use the geometry-only audit; this checkpoint receives the full material and
lighting preservation check as well.

Fresh neutral, level and rear diagnostics, exported mesh and review controls
must be synchronized before acceptance is committed. The bishop main page and
the existing local preview receive the same accepted checkpoint. UI verification
uses the simulated DOM/WebGL harness; no native-browser inspection is claimed.

## Remaining discrepancies and next step

- The small bright glint and detailed edge reflection at the slit tip are still
  absent. The reconstructed opening remains too uniform in tone.
- The narrow golden collar and foot reflections differ from the broader,
  broken cream reflections in the selected image.
- Some head and button grain/reflection detail is too smooth. Fine relief does
  not yet follow the color grain closely enough.
- The stem/socket retains a stray reflection. The rear pigment boundary is
  still conspicuous; this geometry change does not solve it.

Next, examine the slit-tip and cut-edge lighting separately from this accepted
shape. A measured reflection response can test whether a small localized
highlight can be added without reintroducing glare on the head or lower piece.
Continue the wider material and lighting work afterward. The mission remains
incomplete, and the queen and other pieces are unchanged by this work.
