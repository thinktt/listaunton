# Queen checkpoint 24 — restore the socket shelf

The owner preferred the compact, rounded collar treatment from checkpoint 23,
but rejected its altered base/socket silhouette.  This checkpoint therefore
starts from frozen checkpoint 22 and changes **only** the collar rings:
50–62 for the lower rounded bead and 74–85 for the thinner upper collar.

The base, flare, socket, foot, stem, crown, bowl, egg, materials, lights,
reference images, registration, and 54-degree orthographic camera are restored
from checkpoint 22.  In particular, the raised socket retains its clear shelf
and its steep drop into the flare; it has not been smoothed into a taper.

## Evidence

- The active model is at SHA-256
  `fdfb52bc279c836b326b79325cf772ff4f589f9f16675926a6b6e52108c2c9eb`.
- `side-shape-validation.json` proves every undeclared control ring matches
  frozen checkpoint 22 exactly.  The resulting closed render surface has no
  boundary or non-manifold edges, and all six render receivers retain exact
  surface/atlas correspondence.
- The updated fixed-view silhouette fit is **97.7567%** against original
  Lichess black and **97.9356%** against the selected high-resolution detail
  reference.  The candidate measurement in `metrics.json` is the same result
  within rasterization variation.
- The browser viewer, overlay, and side comparison share this active model and
  54-degree camera.  The viewer exports the source model's own editable
  control surface (44,924 triangles) rather than retaining an old mesh; it is
  not a separate viewer-only interpretation.

The source images remain unchanged and are treated as already-rendered
orthographic sprites placed intact on the board.  The side guide remains an
interpretive comparison only, not a replacement reference.
