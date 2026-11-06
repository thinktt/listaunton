# Pawn checkpoint 008

The ordinary diffuse wood in checkpoint 007 (`a44fda5`) closely matches
the selected pawn. Inside its lower reflections, the grain has less contrast.
The original also shows a narrow reflection on the left edge of the stem,
a bright socket lip and a thin line below the main flare highlight.

## Reflectors and grain

Trial 037 is rejected. Several compact sources blew out when the optimizer
compared two saturated powers and discarded the dim range. Trial 038 brackets
the useful range with a log-spaced watt search and verifies that its measured
loss improves over zero added light. This recovers sensible energies. Its
highlights still spread over too much wood.

Trial 039 measures the actual material in eight UV tangent directions at two
small slopes. The fitted corrections combine with the existing relief in
one packed map. The median tilt is 0.65°, its 99th percentile is 3.01° and
its maximum is 7.69°. The upper head glint's fine contrast reaches 17.6
against 18.4 in the selected image. On the narrow flare line, correlation
of the fine brightness pattern moves from −0.35 at checkpoint 007 to +0.37.

Trial 040 refits reflector energies after the material change. The spatial
power fit weights the selected high-resolution pixels at 88% and the
registered original black sprite at 12%. All published comparisons still
use each original reference independently. At native resolution, RGB error
against the black sprite improves from 16.75 to 16.37 on a 255-level scale.
The three head glints fall within 0.86 original pixels of their source
centers. The relative geometry, camera and gallery display height are held.

On the left flare patch, fine contrast improves from 11.4 to 17.7 against
29.4 in the target. Fine-pattern correlation rises from 0.60 to 0.79.
The right lower arc and foot reflection are still too broad. The left edge
of the stem and lower socket retain shape differences in their highlights.

## Sampling and reproduction

Corresponding head and flare crops were rendered at 128, 512 and 768 samples,
including a second 768-sample seed and an unfiltered comparison. At 512
samples the flare's fine contrast increases from 12.3 to 13.8 against 16.1.
The unfiltered 768-sample crop has still more contrast but poorer correlation
with the reference. The accepted comparison uses 128 denoised samples,
consistent with the preceding checkpoints. Grain detail remains visible
across independent seeds.

```sh
blender -b --python-exit-code 1 --python scripts/pawn/fit_lighting.py -- docs/pawn-mission/iteration-008/reproduction.json
```

The replay starts from archived checkpoint 007, attaches the updated
directional grain and reconstructs the fitted emitters. The review uses the
same packed pigment, varnish and normal maps. Fine-pattern measurements,
native comparisons, sampling results and independent replay measurements
are recorded in this directory.

The closed 57,984-triangle mesh and UVs are byte-identical to checkpoint
007. Reopened and independent renders retain identical alpha and differ
from the trial by at most one RGB level. The synchronized DOM/WebGL viewer
checks the actual camera and all three maps. Site, model and candidate
checks pass. The full-set test still stops on the separate knight height
metadata hash; the archived pawn height source remains valid.
