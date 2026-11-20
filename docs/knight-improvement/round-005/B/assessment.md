# Round 5, candidate B

The mane now has a broad planed flank and a narrow bevel that follows the crest and turns down both sides of the neck. A steeper undercut separates the lower blade from the neck. Eighty-eight longitudinal support edges carry the bevel through subdivision. Its strength fades toward the physical root accepted in round 4. Side clay shows the sweep clearly under broad lighting. In the rear quarter the broad flat gives the back a more angular profile.

The eye has a new surface and two different corners. The refaired cheek carries a deeper upper incision, a short lower bevel and a shallow tapered walnut inset. The orbital area has 6,097 additional vertices. The inset sits closely beneath the brow in side clay. In the fixed walnut view its discernible portion narrows from 228 to 130 samples on the same 2-pixel ray grid, with a small reflection across the exposed central facet. The parent’s existing upper-eye reflector was re-aimed at the new facet and reduced to 0.63 W. Its receivers remain the two eyes.

The new crest and eye read most clearly in side and rear-quarter views. At 54°, the noseward end of the inset is angular and the lower eyelid has a quieter reflection than the original and black candidate 2. The selected-reference silhouette overlap moves from 96.63% to 96.57%, and the original-sprite overlap moves from 97.22% to 96.99%.

## Evidence

- `flat-comparison.png` shows the parent and candidate in the same neutral material and soft light from the fixed and registered side cameras. `carving-study.png` compares the walnut eyes and both carvings against the registered original and black candidate 2. `contact.png` includes board-size, reverse, front, side and rear views. `clay-turn.webp` contains sixteen evenly lit views.
- `knight.blend` has SHA-256 `fddd00699d622e0ee02c7410b12c52bda8ea2e95c45a9ddcc50e2e9b243e8c3b`. The starting model has SHA-256 `65dac17941c4a06535e59ed0c63e0fc028979e5d60e8954046f4e92c5355b268`.
- The reopened 144-sample fixed render, `wood.png`, has SHA-256 `8b4d585bbae1a95d362ed59ffce95c3be1ac492d2799f6be4fbda6ea0418454d`. The reopened registered side render, `wood-side.png`, has SHA-256 `11deba6976322df3b8c2149dae6177e5a9b72920a1377af6820ba7209eee61a2`.
- `verified.json` records the repository’s viewer mesh export and native validation on an isolated copy. All nine components are closed, connected solids. Both insets pass the existing eye-seating test. The packed images, camera and other studio lights agree with the parent.
- `carve.py` implements the mane sections, orbital refairing, upper cut, lower bevel and inset on both sides. With the verified starting file at `parent.blend`, run Blender in background mode with `--python-exit-code 1 -P carve.py -- --parent-flat --final`. Run `verify.py` in Blender and `review.py` with Python, Pillow and NumPy. `parameters.json` and `metrics.json` record the final physical dimensions and measurements.
