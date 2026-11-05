# Tenth iteration: lower, smaller finial

Owner correction: both the original and selected high-resolution reference show
a smaller egg seated farther inside the crown. Fixed camera remains 54 degrees.

Trial 096 compresses the finial height above ring 106 by 15%, with 4% radial
reduction blended over its first two rings. Trial 097 uses 10% height reduction
and the same radial reduction. Neither changes rings 0-106, camera, UVs, wood
material or light powers. Render receivers are regenerated from the edited
closed control before rendering; their light links are restored.

097 is the preferred visual direction: the tip aligns more closely with the
high-resolution reference than 096 while reducing the overly tall exposed egg.
Both move closer to the original sprite. The 15% version sinks a little too far.

The old height check correctly flags the intentional lowering: the finial is
the highest point. Do not stretch the body to hide that change. The refined
check retains its original tolerance after subtracting the specified 0.0467
world-unit lowering from the height target; a non-finial vertex checksum guards
against unintended body changes. Side-gallery defaults remain unchanged.

Provisional five-category visual assessment for 097: outline 97.9583% measured,
form 81%, color 80%, grain 77%, lighting 64%; working mean 79.9917%.
Original silhouette IoU 97.9123%. Differences in silhouette from the previous
checkpoint are at rasterization/AA scale; this is an interior-form correction.
The modest form increase does not claim the whole crown is correct. Both trials
retain coarse bowl grain, broad pale rear-bowl reflections, mismatched finial
glints and imperfect collar/socket crescents. Holistic assessment remains
75-80%. 096 receives form 80%, other categories unchanged.

Reproduction trial 098 passed and is accepted. Its render differs from 097 by
mean 0.00000397 byte levels, maximum one byte level; alpha is identical. The
delivered model passes mesh, receiver and 54-degree camera checks. Viewer
camera regression error is 0.0000424 pixels. Both interaction harnesses, all
eight pages/55 links, source hashes, model tabs and protected projection checks
pass. Windows Git ownership prevented one check from reading history over UNC;
the same site check passed under WSL. No native browser GPU check is claimed.
No model completion is claimed.
