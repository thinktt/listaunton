# Pawn reconstruction

`pawn-rebuilt.blend` contains a single connected editable lathe, its subdivision modifier, the saved 54-degree orthographic camera, diagnostic clay material, lights, and all three unchanged reference images packed into the file. The camera opens in the saved comparison view. The render output path is relative to the project.

Original Lichess Black-Pawn.png controls shape; White-Pawn.png is a second original check. Selected Black candidate 2 supplies secondary detail interpretation. The editable `scripts/pawn/profile.json` stores meridian radii and projected ring-axis heights in the original 300px black sprite frame. The build script applies the existing candidate alignment once, then exports the exact evaluated mesh and saved camera for the self-contained `pawn-model.html` viewer.

Four passes are archived in `history/pawn`: initial proportions, base/head correction, collar/shoulder correction, and deeper base groove. Final silhouette IoU is 0.96174 against original black, 0.95899 against registered original white, and 0.93224 against selected Black 2. Mean original-black boundary error is 4.13px at 1254px output, about 0.99 original pixels. These metrics concern silhouette, not material or unseen surfaces. Internal head/collar/stem/base details were inspected in all three sources; `assets/pawn/comparison-contact-sheet.png` records the final visual comparison.

Validation finds one connected closed component, zero nonmanifold edges, positive volume, Euler characteristic 2 and no crossing meridian segments. The exported mesh has 57,984 triangles. Source SHA-256 and unchanged references are checked in `assets/pawn/validation.json`. The Node viewer check exercises actual JavaScript with a mocked WebGL context: its projection agrees with Blender within 0.000011px, with 40 repeated redraws, resize/reset, overlay controls, orbit persistence, pan and zoom checked. This is runtime verification, not a browser screenshot test.

Rebuild from the repository root with Blender and Python containing Pillow/NumPy:

```sh
blender -b --python scripts/pawn/build_pawn.py
blender -b --python scripts/pawn/validate.py -- .
python scripts/pawn/compare.py
python scripts/pawn/contact_sheet.py
python scripts/pawn/build_viewer.py
node scripts/pawn/check_viewer.cjs .
```

The single source view does not determine unseen geometry or exact dimensions. The underside is inferred as closed and flat. Clay and the viewer's optional brown material are inspection surfaces, not recovered wood textures.

## Seated head revision

Owner side-view feedback identified an exposed neck between the ball and collar. The ball is lowered by four original-image pixels into a broader inner seat. The outside collar and all lower-body meridian points are unchanged. The head and seat remain one closed continuous surface. `assets/pawn/side-seating.png` records the level view; `scripts/pawn/check_seating.py` checks preserved geometry and regenerates that view. The stronger seating reduces the original silhouette score from 98.07% to 96.17%; this is an intentional interpretation of the three-dimensional join, not a claim of a closer projected silhouette. The preceding shape is preserved in `history/pawn/04-before-seated-head`.
