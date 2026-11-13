# Bishop checkpoint 020 — shallower button with direct contact

The previous pass corrected the foot and reassessed the broader swollen
appearance. This pass finds a concrete internal shape error: at the saved
54-degree camera, the button's visible front boundary reached row 278, while
the selected reference suggests about row 270. The original white sprite also
supports a shallower edge. These are comparison-canvas coordinates, not pixels
in the original 300-pixel sprite.

First-hit rays label the actual button surface independently of the wood,
highlights and shadows. The accepted boundary reaches row 270 while retaining
the same projected width. `button-surface-evidence.json` records the complete
upper/lower column boundaries and several front-arc landmarks. The reference
landmarks are manually interpreted with approximately +/-3-pixel uncertainty;
they are not exact recovered ground truth. `button-boundaries.png` shows both
actual mesh boundaries over the unchanged original and selected reference.

The accepted button has a shallow convex top and a thin rounded underside.
Its radii and highest physical point remain fixed. The original thick underside
is reduced, rather than scaling the whole bishop or changing the camera.
The upper half of the head meridian extends smoothly inside the button, using
a cubic adjustment that starts with zero displacement, slope and curvature.
All body controls through ring 85 are exact, including the head's widest
region, collars, stem, socket, flare and current foot. All radial controls,
overall height, camera, source registration, UVs, packed pigment and lighting
are preserved.

The first rim-lifting trial matched the front boundary more closely but made
a cup-shaped underside and reduced the direct contact width to 77.45% of the
button width. It failed the existing 80% contact minimum and is rejected.
A shallow-lens trial fixes that failure; its broader head-tip extension is
not selected because it unnecessarily perturbs the upper-head outline.
The chosen localized extension retains that outline more closely. Both
alternatives and their decisions remain in the evidence, not in public choices.

Actual saved-surface checks confirm broad contact of approximately 85.15%,
one external head-to-button transition, no gap or exposed cylindrical neck,
and a continuously tapering exposed head. Button height/width falls from about
0.413 to 0.259. The deep slit and solid floor remain real geometry. The slit
cutter's dimensions and placement are exact; its intersection near the modified
tip naturally follows the new head surface.

The join probe now spans the actual higher junction instead of stopping at
the former fixed height. Its criteria are unchanged. The regression checks
the combined external surface of both components: the historical bad seat
belonged to the button object, so a head-only check would hide it. The rejected
fixture still exposes a long cylindrical run, while the current head does not.
Scope validation independently checks every changed and unchanged control in
both components, along with topology, modifiers, UVs, source pixels, packed
textures, lights, camera and regenerated exact render receivers.

The final saved/reopened 512-sample render overlaps the original white by
about 98.744%, selected white 3 by 97.005%, and original black by 97.785%.
These are exterior measurements only. The original-white upper-head row error
stays close to the prior model (about 2.06 comparison pixels); the internal
button-boundary evidence is the main reason for accepting this change.

Working ratings are **97.01 / 81 / 83 / 77 / 72**, mean about **82.00%**.
Only silhouette is measured; other scores are subjective, with overall
appearance still roughly **70-80%**. The retained wood and fitted lights are
unfinished and can exaggerate or disguise curvature. Neutral and unfitted
studio views remain essential. The button improvement does not resolve the
larger collar, head-fullness, socket and base-transition concerns.

The accepted scene, fixed wood/neutral renders, exported rotating mesh,
head/side/rear views and local review are synchronized after their checks.
The archived source is checkpoint 019. Mission files, other pieces, original
images and shared gallery settings are unchanged. Native browser QA is not
claimed. The geometry goal remains active and incomplete; no quota watcher,
subagent, push or external publication is involved.
