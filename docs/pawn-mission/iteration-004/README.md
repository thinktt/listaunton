# Pawn checkpoint 004

Checkpoint 003 (`7374921`) seats the ball without a gap, but its stretched
lower hemisphere puts the darkest part of the front join around row 601.
The original black sprite puts it near row 592, the white near 589, and the
selected black enlargement near 590. These measurements use the center of
the collar at the same registered camera. The selected side guide has a
round cheek that enters a shallow, cushioned seat.

## Lower head and collar

Trial 017 changes the lower hemisphere to a circular arc with a contact
radius of 0.65 times the ball radius. Four collar controls roll up to that
contact. The upper hemisphere, highest point, overall height and foot stay
at their accepted positions. In clay the side shows a round ball seated
directly in the collar. The front shadow moves to approximately row 589.

## Dark studio and walnut

At the outer rim of the ball, the median blue from the black-material
reflection pass alone was 3.30 times the selected target's scene-linear blue.
With world strength reduced from 0.065 to 0.0125, the ratio is 0.64.
Median displayed rim RGB changes from (80, 47, 37) to (67, 28, 9), against
(66, 31, 10) in the reference. This ring measures radii 112–116 reference
pixels above row 544, on opaque, common foreground. The darker environment
also shifts the middle wood color, so trial 019 measures diffuse response
again and builds a fresh continuous walnut atlas. The existing foot pigment
is retained through the recessed cut, blending to the revised wood between
model Z 0.29 and 0.34.

Seven relatively distant collar reflectors in trial 020 give unwanted
head glints and conspicuous vertical bars in the side view. The accepted
setup uses four closer sources with narrower beams and a stronger penalty
for spill across the head. The collar now separates more clearly under the
ball. Its highlights still look like short parallel marks. The base highlights
remain too broad and the head's glints are smoother than the photograph.

## Reproduction

```sh
blender -b --python-exit-code 1 --python scripts/pawn/apply_wood.py -- docs/pawn-mission/iteration-004/reproduction.json
```

The configuration starts from archived checkpoint 003, applies the new head
controls and world strength, restores the four fitted emitters and packs the
new diffuse wood. Metrics, per-trial scorecards, side views and independent
replay comparisons are stored alongside this file.

Site links, reference hashes, all model pages and the candidate interaction
checks pass. The pawn's orbit and camera are checked in the DOM/WebGL harness.
The full-set check still stops at the independently changing knight height
metadata described in checkpoint 003.
