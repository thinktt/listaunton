# The second line on the mane

The round-twelve carving puts the leading edge of the mane close to the dark hollow in the source. Farther back on the broad wooden face, a second dark arc still suggests another ridge. It is easiest to see near the middle of the neck.

I reopened the accepted 12B scene and isolated the material under the fixed camera. I rendered the current atlas as emission, then substituted the earlier 11B atlas on precisely the same mesh and UVs. A third exposure used one neutral base color with the actual surface normals and studio lights. In both unlit atlases a continuous dark mark follows the broad face. That mark disappears in the neutral-color exposure. The curved shadow at the inner edge of the mane survives under neutral color, as expected from its carved depth. [Registered crops of all five exposures](mane-pigment-origin.png)

| Along the extra arc, away from the inner edge | Relative darkness against the two adjacent samples |
| --- | ---: |
| Black candidate 2 | −3.7% |
| 12B complete walnut render | 26.8% |
| 12B unlit pigment | 33.6% |
| 11B unlit pigment on the 12B mesh | 27.7% |
| 12B neutral base color in studio light | −9.0% |

The line was located in the current pigment and then sampled at exactly the same pixels in every exposure. Positive values mean the center is darker than its two neighbors eight pixels away. These are rendered brightness measurements. They locate the apparent additional ridge in the color map. The final 12B stain increased its contrast. Its earlier physical origin is unknown.

Across the central face, black candidate 2 has short, mostly horizontal dark marks and finer pores. The parent’s upper-marking contrast is dominated by the long arc in its pigment. The original at playing resolution supports a broad face turning into a single shadow; it contains little directional evidence for individual pores. Black candidate 2 supplies an interpretation of that finer figure. [Wood figure on the registered and native sprite grids](mane-grain.png) · [Grain measurements](mane-grain.json)

A future material pass can work in the mane’s own surface coordinates. Recover the broad wood tone on the rear-facing plane, carry short stretches of walnut figure around both flanks and preserve the physical shade at the leading edge. Check the result in emission, studio light and at the rear quarters. A change in illumination alone would leave the false line in the texture when the knight is rotated.
