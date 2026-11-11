# Queen checkpoint 23 — compact socket and stacked collars

This checkpoint addresses the owner’s side-profile concerns while retaining the
fixed Lichess view as the master reference. It starts from frozen checkpoint 22
(f390b7d…) and changes only the declared socket/flare rings 24–39 and
collar rings 50–62 and 74–85. The crown, bowl, egg, foot, material, UVs,
lights, source images, gallery defaults, and 54-degree orthographic camera
are retained.

The source images are treated as already-rendered orthographic sprites placed
intact on the 2D board: this checkpoint does not use CSS stretching, reference
warping, perspective substitution, or a separate viewer-only shape.

## Accepted shape changes

- The raised socket seat moves from **1.30939** to **1.27000** (3.01% lower).
- Its straight upper-wall height reduces from **0.14700** to **0.12000**
  (18.37% shorter), and its upper-wall radius reduces from **0.56450** to
  **0.54500**.
- The flare rises into that smaller socket through a continuous sequence rather
  than ending as a swollen drum.
- The lowest collar is a true rounded bead: its radius rolls from **0.54000**
  at either edge to a **0.67440** peak, giving both the upper and lower faces
  continuous curvature.
- The upper collar is deliberately finer: peak radius is **0.45200** instead
  of **0.48100**, and its height is **0.08000** instead of **0.15000**.

The height and base diameter remain 4.40727 and 2.07287 respectively. The
physical full side silhouette is an interpretation; it is judged alongside,
but never substituted for, the elevated Lichess sprite.

## Camera test and source-fit decision

The original source is orthographic and remains at the established 54-degree
camera in this accepted checkpoint. More compact physical proposals were
tested with lower orthographic elevations:

| Trial | Camera | Original black IoU | Selected high-res IoU | Decision |
| --- | ---: | ---: | ---: | --- |
| 217 socket flow + collars | 54° | 97.6997% | 97.9304% | Accepted |
| 220 shorter stem | 52.5° | 96.4807% | 96.7925% | Rejected |
| 218 compact profile | 50° | 92.7003% | 93.0933% | Rejected |
| 219 compact profile | 48° | 90.9264% | 91.3062% | Rejected |

Candidate 217 loses 0.219 percentage points against the original black
silhouette and 0.038 points against selected high-res, while the opposite
white original improves from 93.4067% to 93.5715%. That tradeoff is accepted
because it visibly corrects the requested local form while retaining a strong
fixed-view fit. The larger camera/proportion shifts do not.

## Validation and delivery

validate_finished_queen.py recognizes the explicit side_shape_study feature
and delegates only that documented geometry scope to
validate_side_shape_iteration.py; it does not relax the older frozen-profile
validators. The checkpoint passed:

- a closed, manifold control mesh check;
- exact declared-ring reconstruction from frozen checkpoint 22;
- unchanged controls outside the declared rings;
- 54° orthographic camera and identity object scale;
- exact receiver-face/atlas-UV correspondence, custom normals, materials,
  transforms, and 82 light receiver links;
- active viewer mesh export and saved-camera regression;
- regenerated fixed and side views from the promoted blend.

The rotating viewer, overlay render, and side comparison are synchronized from
the same active blend. The reference images and their registrations remain
unchanged.
