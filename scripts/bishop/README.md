# Bishop reconstruction

The original Lichess white bishop is the proportion reference. The original black bishop is available as a second overlay. White candidate 3 supplies readable detail; candidate 4 was not used. Reference images remain byte-for-byte copies.

The model uses a continuous closed turned body, a separate intersecting rounded finial, and an editable Boolean saw cut through the full mitre thickness. The cut stops above the collars, leaving a solid floor. This is an editable visual reconstruction, not a manufacturing solid. The saved orthographic camera is 54 degrees above the board. Neutral clay remains diagnostic; grain is future work.

Run from the repository root:

1. Blender: `--background --python scripts/bishop/build_bishop.py`
2. Python with Pillow and NumPy: `scripts/bishop/compare.py`
3. Blender: `--background --python scripts/bishop/validate.py -- ROOT`
4. Python: `scripts/bishop/build_viewer.py`
5. Node: `scripts/bishop/check_viewer.cjs`
6. Optional Blender cavity view: `--background --python scripts/bishop/render_diagnostics.py`

`profile.json` stores radius and projected axis-center heights in the 300px original white image coordinates. The exporter maps those measurements into the selected-candidate frame using `original-alignment.json`. This registration is composed from candidate-to-black and original-white-to-black registrations, rather than applying the black registration directly to white. The browser uses the same inverse affine placement as the image comparisons. No reference pixels are warped or rewritten.

Silhouette agreement measures only the visible boundary. Four geometry passes also checked the finial, the narrow mitre neck, slit direction and floor, three collar steps, concave stem, socket lip, bell-shaped base and foot groove. Hidden surfaces and absolute dimensions remain interpretations of the rendered sources.
