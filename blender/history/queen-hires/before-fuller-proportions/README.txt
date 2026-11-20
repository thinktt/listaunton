QUEEN RECONSTRUCTION FROM THE HIGH-RESOLUTION REFERENCE

CURRENT REFINEMENT
The bottom of the flare curves downward into a small outward roll above the
foot. The groove is narrower and about half as deep, creating a subtle line
instead of a broad channel. The shortened lower assembly, wider socket and
flat, coin-like foot retain their overall dimensions.
The three evenly spaced collars and the tapered crown body are unchanged.

Open queen-3d.html for free rotation, zoom, and top/underside views.
It starts with the same orthographic camera and framing as the overlay render.
Overlay camera or Reset restores that exact view after rotating or zooming.
Orthographic/Perspective changes the projection; the mesh itself is identical.
The interactive viewer uses simpler lighting than the Blender renders.
Open queen-parts.html for the interactive reference diagram and part names.

This pass follows the requested changes to the parts named in the diagram:
- The crown body (upper neck) has a continuous, gently widening taper.
- All three collars are thin shelves with small edge roundovers and even spacing.
- The stem has a stronger taper and a narrower waist.
- The raised socket rises with a straight side, then rounds inward to meet the
  stem. Its separate flared lip has been removed.
- The foot has a flat, coin-like outer edge with small rounded corners.
- The flare ends in a gentle rolled curve and a shallow groove above the foot.

The approved finial, crown tips, crown rim and inner bowl are unchanged. The
matching camera and original reference framing are retained. This pass follows
the requested shapes rather than preserving every earlier ring edge position.
The Previous previews show the sharper flare edge and deeper base groove.

Open queen-rebuilt.blend for the editable model.
Open review.html for the reference overlay, blink comparison, zoom, and detail views.
The reference image is also packed into the Blender file and installed as a 50% camera background.

USING THE LOCAL COMPARISON VIEWER
Keep review.html beside the PNG images and open it in a browser. It needs no internet connection.
Choose Current for the rounded base edge and shallow groove or Previous for the sharper edge and deeper groove. Both revisions support Neutral and Brown preview materials and use the same image coordinates. The previous neutral and brown images are queen-previous.png and queen-previous-brown.png.
Choose Neutral or Brown preview to change the rendered model material. Brown preview is plain, untextured gloss: it helps compare shape under similar color and reflections, but it is not the final wood material.
Use the opacity slider to mix the selected model render over the reference. Reference and Model show either image alone. Blink alternates them without changing their position. Hold the reference button or the Space key to see the reference temporarily.
Fit shows the whole image. The 1x and 2x buttons allow closer inspection; drag or scroll to pan.
Contours show the current revision only and automatically select Current. Selecting Previous while viewing contours returns to the overlay, so the current contour is never presented as a previous contour. Fixed detail comparison panels and the second-angle image show the current revision; the panels use the neutral render.
queen-three-quarter.png shows the reconstructed geometry from a second angle and is also displayed below the detail panels. queen-brown.png is the matching-camera plain brown preview; queen-matched.png is the neutral matching-camera render.

This rebuild uses reference.png (the supplied hi-res-queen.png), not the earlier low-resolution sprite profiles.
The source camera estimate is 55.32 degrees above horizontal. Both reference and matching render retain their original 1254 x 1254 pixel coordinates. Comparison images are not warped to improve their fit.

Geometry is editable: a turned body profile and a crown with a continuous bowl and central egg-shaped finial. Subdivision modifiers remain unapplied. The model uses arbitrary units.

The neutral and plain brown materials are for checking geometry. Wood grain and the final surface finish have not been recreated in this pass.

build_queen.py rebuilds the model and renders through Blender Python.
profile-landmarks.json records the projected circular features used to check internal details.
