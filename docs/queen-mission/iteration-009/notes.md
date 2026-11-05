# Ninth queen mission iteration — owner pause

Start from accepted commit 7d7d55a, model
c32bccbf33e5e137d982bdeafd881a783b006f62e644dbd5db2df57d02801004.
Keep 54 degrees, both original references, v4 pigment and accepted proportions.
The eighth model and four actual views are preserved in history/queen-mission-008.
Weekly reading at 2026-11-05 14:01:29 UTC: 24% used / 76% remaining,
reset 2026-11-11 13:19:47 UTC. Luna continues five-minute monitoring.

## Relief isolation

090 changes only the relief's color input from the first atlas to current v4.
The visible difference is too small to justify a change: 97.9612 / 80 / 80 /
77 / 64, mean 79.7922%. Reject as no convincing improvement.

091 removes all bump while retaining roughness, color and the accepted rig.
The bowl and base reflections become smooth and artificial while coarse
color markings remain. Scores 97.9612 / 80 / 80 / 74 / 61, mean 78.5922%.
Reject. 092 removes only procedural pores while keeping pigment relief.
It makes some highlights scratchier without fixing the coarse color pattern:
97.9612 / 80 / 80 / 76 / 62, mean 79.1922%. Reject. Both silhouette IoUs
are exactly unchanged in all three trials.

These repeat useful isolation checks under the newer rig, but corroborate the
fifth iteration's finding: the coarse appearance is not solely bump or pores.
Do not keep revisiting that hypothesis without new evidence.

## Color/coverage diagnosis and 093

Actual emission passes inspect material color and the stored projection
coverage. They are diagnostic data only, never beauty renders. Mean coverage
is 0.961 in the sampled bowl, 0.813 on the rim, 0.962 on the finial, 0.667 on
the crown body and 0.985 on the base. Thus broad missing coverage does not
explain the bowl/base appearance. Oblique rim/body regions retain some fallback.

093 reconnects the full-resolution packed inferred pigment and accepted
regional grade, bypassing the v3/v4 atlas bakes. The actual render is visually
near-identical to the accepted material; no score increase is justified.
Scores remain 97.9612 / 80 / 80 / 77 / 64, mean 79.7922%; reject as no gain.
The filtering steps are not the primary problem. References and geometry
remain untouched. 094 tests only stronger bounded fine-grain contrast,
raising the exponent from 1.5 to 2.1 while retaining its 3-pixel filter,
broad pigment, highlight suppression, original relief and accepted lights.


094 exaggerates dark/light grain and looks more etched. Scores 97.9612 / 80 /
79 / 74 / 64, mean 78.9922%; reject. 095 lowers the exponent to 0.85. It
softens fine detail but leaves broad invented markings, rather than matching
the reference's finer natural surface. Scores 97.9612 / 80 / 80 / 76 / 64,
mean 79.5922%; reject. All six actual renders preserve both reference outlines.

The owner requests a pause after finishing the current task. No further model
or render batch is started. The current public model and preview remain the
eighth checkpoint, working score 79.7922%, holistic 75–80%, visibly incomplete.
All completed trials are scored and preserved as evidence; none enters public
controls. A start/reference/current comparison is saved as mission-progress.png.
There is no pending trial validation or promotion. New scripts are parsed,
Git whitespace is checked, and delivery hashes are verified unchanged.

Final Luna reading, 2026-11-05 14:16:40 UTC: weekly 25% used / 75% remaining,
reset 2026-11-11 13:19:48 UTC. Luna has stopped monitoring at the owner's request.
The next step on resume is geometric inspection of bowl/rim and collar curves,
not another repetition of the unsuccessful pore or grain-gain experiments.
