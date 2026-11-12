# Bishop checkpoint 012 — confined socket reflections

November 12, 2026. The goal remains active. This is a small accepted lighting
improvement from checkpoint 010, preserved in `history/bishop-mission-010`.

The socket crescent is slightly broader and less fragmented. Its 17 existing
spot reflectors now affect only the socket region; their source radii increase
to .024 units and cones to two degrees. Positions, colors and powers are exact.
The collar reflector excludes the socket, reducing the unwanted lower gold
glint. Other lighting, the wood material, closed geometry and 54-degree camera
remain unchanged. No photograph or emission pass substitutes for the beauty.

![Reference, previous checkpoint and current socket](socket/socket-comparison.png)

## Examination and scores

| Category | Previous | Current | Finding |
| --- | ---: | ---: | --- |
| Silhouette and placement | 96.11% | 96.11% | Same selected-reference IoU; original white 97.79%, original black 96.66%. |
| Interior form | 84% | 84% | Continuous head, deep slit, seated button and accepted turned profile are preserved. |
| Wood color | 84% | 84% | Same pigment. The reduced lower glint leaves a small local darkening tradeoff. |
| Grain and surface texture | 77% | 77% | The fine grain/relief mismatch and severe side/rear pigment boundary remain. |
| Lighting and reflections | 76% | 77% | Slightly broader cream band and less stray reflection, without the upper-stem arc. The reference band remains broader and less sparkly. |

Equal-weight working mean: **83.42% → 83.62%**. Holistic fixed-view estimate
remains **75–85%**. Only silhouette overlap is measured accuracy; the other
ratings are subjective progress estimates. This does not establish a perfect
match or an acceptable finished material from every angle.

At the unchanged 246-pixel reference cream core, RGB error decreases from
45.20 to 35.03 /255. Whole-socket crop error improves 8.12 → 7.97; lip crop
13.43 → 12.85. The model has 225 cream pixels in that lip crop, previously 138.
These diagnostics support the visible improvement but do not measure complete
fidelity. The bright lower streak diminishes, yet that crop's overall RGB
error worsens **8.38 → 8.72** because the surrounding socket becomes too dark.
Whole-piece shared-foreground RGB error improves slightly, **7.72 → 7.69**.

The actual saved scene is reopened and rendered with 512 fixed samples,
Standard/None display and four glossy bounces. All final silhouette values
match checkpoint 010 exactly, using the unchanged mission mask convention.
Raw and cleaned model masks differ by zero pixels.

## What the studies established

The earlier wider-beam trial illuminated the upper stem. Exact derived socket
receivers confine that illumination while retaining the full closed editable
body. A 1.4-degree cone gives less improvement than two degrees; further
source enlargement adds no convincing gain. Measured light-response passes
identify the collar reflector as the main remaining source of the lower glint.
Also excluding the head reflector adds no useful improvement, so it stays intact.

An initial saved trial exposed a Blender persistence bug in our implementation:
temporary evaluated material pointers rendered correctly in memory but became
empty slots on reopening. That invalid render is rejected. The fixed builder
uses the original persistent material slots and verifies them after reopening.
The independent audit checks actual packed texture pixels and the shader graph.

The body splits into two render-only surface regions by evaluated face-center
height, .99 ≤ z < 1.38 for the socket. Every evaluated face appears once, with
exact positions, topology, material indices and relevant scalar attributes.
Materials are shared with the original closed control. Custom-normal component
error is below .000044. Re-evaluating the Boolean after reopening introduces
at most **5.96e-8** UV rounding; the validator reports this explicitly under a
1e-7 bound (under .0005 texel at 4096px). Original control UVs are byte-identical.
No image scoring convention or prior geometry tolerance was changed.

The exported mesh still contains the two closed intersecting components and
135,128 triangles. Its positions, normals, indices, bounds and component list
are exactly unchanged; only the same one-float-ULP evaluated UV rounding changes
the binary hash. The viewer uses that export and the unchanged saved camera.
The original two closed components are not boolean-fused for manufacture.

## Validation and remaining work

Reopened receiver/material/light scope, closed-component volume/manifold checks,
slit depth/floor probes, continuous head/button contact, the declared earlier
base/slit edits, export and saved camera checks pass. The final side, rear,
head-side and neutral views are regenerated from the same saved model. The
bishop viewer and workspace interaction harnesses pass. Canonical/preview
synchronization and final site-check results are recorded in `checkpoint.json`.

The side/rear pigment boundary remains a serious defect, already present in
checkpoint 010; the new side/rear views do not resolve it. The base highlight
is still too compact and sharp; collar crescents, slit-edge finish, fine relief
and overall tonal distribution remain imperfect. The socket band still needs
greater breadth and its characteristic irregular lower streaks.

Next inspect pigment continuity in isolation, using the saved side/rear views
and the previously rejected material studies. Preserve this socket result and
the fixed-view fit while testing a genuinely continuous three-dimensional wood
finish. Further socket-light additions need measured support, not indiscriminate
brightening. The full mission remains incomplete; no quota monitoring occurred.
