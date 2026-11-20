# Round 13 · Candidate A

I chose A for the line of its upper lid. It begins beneath the swept ear, crosses the eye and tapers into the bridge of the nose. At the board angle the two small surfaces inside the eye catch the light separately. A longer reflection rolls across the cheek underneath. In profile the eye looks open and sits farther into the head. The parent’s dark perimeter gives it a seed-like appearance when the knight turns.

B has the smoothest transition out of the lower lid. It performs particularly well in the three-quarter clay views, and the pattern of light across the eye agrees more closely with the small original at board size. At 54° its pale reflection spreads across much of the lower cheek and the smaller crescent inside the eye is difficult to distinguish. A gives the more convincing overall reading of the selected walnut knight. [Fixed-camera eyes](eye-detail.png) · [The three candidates at playing size](eye-native-grid.png) · [Oblique views in clay](eye-turns-clay.png) · [Oblique views in walnut](eye-turns-walnut.png)

| Knight | Fixed 54° · 45% | Side · 35% | Form · 15% | Finish · 5% | Weighted / 100 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Parent, round 12B | 95.5 | 94 | 93 | 88 | 94.23 |
| A | 96.5 | 95 | 94 | 89 | 95.23 |
| B | 95.5 | 95.5 | 94.5 | 88 | 94.98 |

These are my visual grades. The two side views of each eye and three-quarter turns use the actual geometry under the same lights. All three models have identical outer silhouettes in both registered views. The overlap against the original black sprite is 98.38%. The overlap against black candidate 2 is 97.73%.

Blender also confirms that both eyes physically meet the skull. Each has about a thousand exposed vertices and roughly seven thousand beneath the surface. The release check now tests the actual carved faces, so the eye can move away from its original object center during sculpting. The near eye reaches 0.055 model units above the head and the far eye reaches 0.055.

## What the two black references agree on

The reflection under the eye occupies a longer arc in both references than it does in the parent. In the table, the endpoints enclose the central 80% of brightness above the nearby cheek. The cropped original uses the fixed registration of the Lichess PNG.

| Under the lower lid | Original black | Black 2 | Parent | A | B |
| --- | ---: | ---: | ---: | ---: | ---: |
| Span on the 1,254 px comparison | 42 px | 42 px | 18 px | 38 px | 31 px |
| Left and right endpoints | 483–525 | 483–525 | 493–511 | 481–519 | 486–517 |
| Position of brightest contrast | 498 | 495 | 504 | 496 | 495 |
| Peak contrast, 0–255 | 52 | 120 | 111 | 52 | 92 |

A follows the original’s subdued peak and nearly reaches the photographed length. Its reflection still dies out six pixels early toward the nose. B places the brightest part well, although the glazed cheek underneath is conspicuous. Both candidates recover light on the nose side inside the eye. That region accounts for 54% of the original’s brighter interior, 32% in black candidate 2, 10% in the parent, 47% in A and 37% in B. [Lower reflection](lower-lid-light.png) · [Inner reflection](inner-eye-light.png) · [Upper lid continuing onto the nose](brow-to-nose.png)

The original is coarser and darker than the selected enlargement. At a 100-pixel playing size, B’s light pattern has the highest correlation with the original (.884, against .784 for A and .755 for the parent), while its mean luminance error is higher (15.49, against 11.72 and 11.53). These differences show up as an especially bright patch under B’s eye. In the selected high-resolution eye interior A’s pattern correlation rises from .401 to .519, while B scores .388. B has the lower brightness error specifically in the lower lid and cheek. The source evidence favors different aspects of each candidate.

## What the carving contributes

On the 39 native sections where all three upper margins can be measured with the same chord, the near-side median recess measures .0415 model units on the parent, .0193 on A and .0243 on B. Across all 65 matched lower sections it measures .0201, .0219 and .0090 respectively. On the opposite side these results agree to within .0011 model units for each model. A relieves the abrupt notch at the top. B gives the lower edge the gentler exit into the cheek. The photographs show the line and its reflection. Their exact depths are artistic choices. [Native eye sections](socket-sections.png) · [Near and far eyes](eye-portraits.png) · [Source landmarks on the actual sides](brow-side.png)

A’s two exposed openings overlap by 99.5% across the shared local eye coordinates; B’s overlap by 98.9%. At 54° the visible insert areas are 976 pixels for the parent, 1,090 for A and 1,250 for B. The mane and pedestal retain their established shape. In A the long mane region changes by 0.008 intensity levels per color channel on average. The other persistent weakness on the mane comes from its wood map. [Pigment and lighting investigation](mane-surface.md)

I also re-rendered every eye under the parent studio, including its per-object light links and ray visibility. The duplicate parent control reproduced the same crop exactly. With all lights held equal, the parent has the smallest mean RGB error against black 2 over the eye crop (16.86, compared with 18.68 for A and 18.45 for B). Both new carvings improve when lit for their changed surfaces. Under their own studios the errors are 16.99, 16.68 and 16.79 respectively. The common clay turns show the physical change independently. [Common and saved studios](eye-studio-comparison.png) · [Pigment and neutral polish](eye-finish.png)

## Reproduction and validation

Start from the round-twelve Blender model at `9c3152c`, with its packed `wood-atlas-improvement-012-B.png`. The A and B folders include their sculpting, lighting, export and validation scripts and describe the staging layout. A retains the packed atlas. B uses a new atlas carrying adjacent wood into its eye islands. Its UV audit records a small interpolation discontinuity affecting 0.14% of the exposed near eye and 1.33% of the exposed far eye.

Two triangles in an earlier A mesh collapsed at the boundary of the local refinement. The sculptor repaired the topology before judging. The repair preserved the native vertex positions. All registered renders and three-way checks use the repaired A scene, SHA-256 `cd5de4ca41bf7061e04caf14843f399f49f7a82df8376bb966890d11edada20b`. The shipped A mesh has 288,430 triangles. I checked the actual WebGL position, normal, UV and index streams for all three models. No triangle in any of the seven visible parts fell below the doubled-area threshold of 10⁻¹⁰ in world coordinates. The gallery renders come from reopening the accepted scene at 144 samples. [Round fingerprints](decision.json) · [Mesh repair](A/repair.json) · [Final exported faces](exported-faces-A.json)
