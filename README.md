# listaunton

Recovering the Lichess **Staunton** chess set as editable 3D models from its static rendered images. All six pieces now have editable reconstructions. This is an independent art reconstruction, with interpretation where a single image cannot determine the geometry.

[The home page](index.html) displays all twelve original reference pieces. Choose either queen to open [the queen review](review.html). The king, rook, bishop, knight and pawn each open their own page with **Reference candidates** and **Model** tabs. All five have model comparisons.

The queen review has four tabs: **Reference overlay**, **3D model**, **Parts map**, and **Projection variants**. Use the tabs to switch; dragging the reference only pans it. The viewer retains its rotation when switching tabs. The current model and parts map are embedded; the projection study loads in its own frame on first use.

The queen geometry includes a continuous splash-shaped crown, eight tips, a shallow bowl and seated egg-shaped finial. Its three thin collars now sit closely stacked, with roughly 44% less center spacing and narrow grooves in place of the tall spacers. The neutral and brown materials are shape studies. Faithful wood grain is still to come.

The king uses the original Lichess sprite as the authority for proportions, with selected black candidate 1 supporting detail interpretation. Its closed revolved body and separate beveled cross intersect but are not boolean-fused. This is a geometry study of roughly 68,500 triangles in neutral clay; matching wood grain and finish come later.

[King projection variants](king-projections.html) compare six refitted models at assumed elevations of 48°, 52°, 54°, 56°, 60° and 64°. Inspect profiles at one physical scale, rotate while retaining the view, or compare each fitted render against either reference. They also appear in the king review’s **Projection variants** tab. The current king is preserved; see [the experiment notes](docs/king-projections.md).

[Queen](queen-projections.html) and [rook](rook-projections.html) have corresponding proportion studies, including **54°**, reachable from their review tabs and the home and set pages. Each study preserves its current model and uses one base diameter, ground level and profile camera across its alternatives. The queen also includes its current 51.5° interpretation. These are geometry alternatives fitted under different camera assumptions; silhouette agreement alone does not establish the historical camera. See [queen notes](docs/queen-projections.md) and [rook notes](docs/rook-projections.md).

All six GPT-generated side elevations live in the [Side views tab](set-comparison.html#side-views) of the whole-set page. Transparent images share a ground line and are uniformly scaled to model-based height estimates, with the king as 100%. The models use a common 54° camera assumption; original sprite base widths establish cross-piece scale despite arbitrary model units. Each piece has a 50–150% slider anchored at its foot, a Reset button, and browser-local saved adjustments. The chosen default sizes and order are recorded in `assets/side-views/defaults.json`; Reset restores those selections. Labels update to show current heights relative to the king. Drag pieces sideways or use their arrow buttons to reorder the lineup; order is saved separately from sizes. Generated image proportions remain unchanged, so base widths need not match exactly. Cards link to cutouts, untouched side images, piece reviews and prompts. The AI extraction altered some wood detail. See [scale and extraction notes](docs/side-view-scale.md). The original comparison retains its color and candidate choices when switching tabs. Gallery records are in `assets/side-views/manifest.json`; images and provenance files are in `assets/<piece>/concepts`.

See [the continuing provenance investigation](PROVENANCE.md) for the original set’s sources, per-piece metadata, known history and unresolved authorship.

[The shared camera study](camera-study.html) compares circular features across all six original pieces. Its working estimate is about 54° above the board, with substantial uncertainty; existing models and review pages remain unchanged.

## Files

- `models/queen/queen-rebuilt.blend`: current editable Blender model, with its reference packed inside.
- `assets/queen/`: the supplied high-resolution reference, renders, comparisons and validation reports.
- `models/king/king-rebuilt.blend`: current editable king model.
- `assets/king/`: king references, renders, exported mesh and comparison reports.
- `references/lichess-staunton-3d/`: all twelve original PNG sprites, their provenance and hashes, plus the previously collected WebP versions.
- `scripts/queen/` and `scripts/king/`: current generation, export and checking pipelines.
- `history/`: previous models, scripts, experiments and working notes preserved from the original project.
- `docs/import-manifest.json`: source-to-repository mapping and hashes for imported files.
- `build/`: ignored, regenerable mesh export and camera-check files.

The original Windows project was copied, not deleted, so existing open browser tabs continue to work. New work belongs in this repository. Historical scripts are archival and may retain their original machine-specific paths.

## Rebuild the queen

Use Blender 5.2 (the current model was built with 5.2.2), Python 3.10+ with the requirements below, and Node.js for the camera regression. Blender supplies `bpy`, `bmesh` and its NumPy runtime; do not install `bpy` into ordinary Python.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r scripts/queen/requirements.txt
blender --background --python scripts/queen/build_queen.py
blender --background --python scripts/queen/export_viewer_mesh.py
blender --background --python scripts/queen/inspect_viewer_camera.py
python scripts/queen/build_viewer.py
python scripts/queen/overlay_qa.py --reference-mask max-channel
blender --background --python scripts/queen/validate_stacked_collars.py
node scripts/queen/check_viewer_camera.cjs
node scripts/queen/check_review_reference.cjs
python scripts/check_site.py
```

Use an absolute Blender executable path if it is not on PATH. For Windows Blender with this repository in WSL, pass Windows/UNC versions of script paths (obtain them with `wslpath -w`), rather than Linux `/home/...` paths. Each script resolves repository paths from its own location. The saved model still contains its original render-output path until rebuilt; the external reference is already packed.

`validate_stacked_collars.py` checks the current revision against `history/queen-hires/before-stacked-collars`: a closed connected mesh, materially closer collar centers, narrow exposed spacers, and unchanged base/socket/lower stem and crown/bowl/finial. The earlier `validate_seamless_crown.py` remains available for its historical revision. Preservation checks must be revised deliberately when a future change authorizes those regions.

The 3D viewer embeds its mesh and works without a server. The parts map keeps its original sandbox/CSP and uses external UI libraries from unpkg.com, so it needs internet access for those libraries.

## Rebuild the king

See [the king reconstruction notes](docs/king-reconstruction.md) for measured features, iteration history and remaining uncertainty.

Use Blender for model construction and validation, ordinary Python with Pillow and NumPy for comparison analysis, and Node.js for viewer checks. Run from the repository root:

```sh
blender --background --python scripts/king/build_king.py
python scripts/king/compare.py
blender --background --python scripts/king/validate.py -- "$PWD"
python scripts/king/build_viewer.py
node scripts/king/check_viewer.cjs
python scripts/build_candidate_pages.py
node scripts/check_candidate_review.cjs
python scripts/check_site.py
```

The validator's argument after `--` is the repository root. When using Windows Blender against WSL files, supply its Windows/UNC path along with the Windows/UNC script path. Rebuild `king-model.html` after changing the model, then rebuild the candidate pages to activate its Model tab. The page embeds the model and references, uses the saved reference camera for its overlay, and retains rotation between tab visits. Image overlap is evidence for the visible silhouette, not proof of hidden geometry or a perfect reconstruction.

## Other piece models

The rook, bishop, knight and pawn use the shared working camera estimate of 54°. Each **Model** tab provides a source overlay and freely rotatable geometry, with the exact saved Blender camera for returning to the reference. Geometry materials are neutral; wood grain remains future work.

- [Rook build notes](scripts/rook/README.md): thin uniform crenellated wall, shallow cavity and turned base, guided by original black/white sprites and selected black candidate 8.
- [Bishop build notes](scripts/bishop/README.md): continuous curved head with a directly seated button and full-depth open mitre slit, guided by original white and selected white candidate 3.
- [Knight build notes](scripts/knight/README.md): continuous horse head with a tapered muzzle, joined mane, paired ears and turned pedestal, guided by both originals and selected black candidate 2.
- [Pawn build notes](scripts/pawn/README.md): one connected turned surface with round head seated directly in its shallow collar, curved stem and broad base rolls, guided by both originals and selected black candidate 2.

Builders, validators and viewer generators live under `scripts/<piece>/`; editable scenes under `models/<piece>/`; references, exported meshes and comparisons under `assets/<piece>/`. Earlier rendered iterations are under `history/<piece>/`. Run `python scripts/build_candidate_pages.py` after a new standalone `<piece>-model.html` is available, then `node scripts/check_candidate_review.cjs`, `python scripts/check_model_site.py`, and `python scripts/check_site.py`. This activates the existing Model tab while retaining candidate controls and lazy loading.

## GitHub Pages

The repository is committed locally; pushing is left to the owner. Create a GitHub repository named `listaunton`, add it as `origin`, and push `main`. In GitHub **Settings → Pages → Build and deployment → Source**, select **GitHub Actions**. Run **Publish site** from Actions if the initial push occurred before Pages was enabled.

The included workflow publishes the repository root directly on pushes to `main`. There is no `_site` folder or packaging step. All HTML pages live at the root and use relative asset links. If hosted under `thinktt/listaunton`, the expected URL is `https://thinktt.github.io/listaunton/`; it is not live until pushed and deployed.

Alternatively, choose **Deploy from a branch**, select **main / (root)**, and disable the custom Publish site workflow so only one deployment method is used. The root `.nojekyll` file allows plain static publishing.

Check the site locally with `python3 scripts/check_site.py`.

See [GitHub's custom Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## References and attribution

The twelve sprites came from Lichess's `public/images/staunton/piece/Staunton` directory. Specific authorship is unclear; see `references/lichess-staunton-3d/SOURCE.txt`. The high-resolution queen reference was supplied by the project owner after generating it with ChatGPT. It is an interpretation used for reconstruction, not recovered original geometry. No new license claim is made for these reference assets.

## Comparing the two queen references

In `review.html`, **Selected high-res** uses the ChatGPT-generated candidate chosen by the owner. **Original Lichess** uses the untouched 300 × 300 `Black-Queen.png` from the original 3D Staunton set. The model render stays in exactly the same place when switching references.

**Compare references** places the selected high-res image over the original sprite, with the same opacity, hold and blink controls. While comparing sources, model revision/material controls are paused. Contours remain explicitly high-res comparisons.

The original sprite is positioned by uniform scaling and translation fitted to the high-res silhouette, independently of the reconstructed model. No anisotropic stretching or warping is applied. The recorded scale is about 4.218×; the original and high-res outlines overlap by about 98.5% at the quarter-resolution fit. This describes silhouettes, not matching internal geometry or recovered detail. The browser smooths the enlarged source image.

`assets/queen/original-reference-alignment.json` records placement, source hashes and fitting method. Run `python scripts/queen/align_original_reference.py` to recompute the alignment and update the page's embedded metadata if the references change. `node scripts/queen/check_review_reference.cjs` checks the page's actual control logic, alignment hashes, zoom/pan stability, hold/blink behavior and contour guards.

## Review implementation

`scripts/queen/build_viewer.py` embeds the generated mesh viewer and the preserved `parts-template.html` into `review.html`. The parts map retains its sandbox and CSP. Both frames initialize on first use. Only messages from the corresponding parent/frame are accepted.

`check_review_reference.cjs` covers tab-only switching, image panning, reference selection and comparison controls. `check_viewer_camera.cjs` checks the exact Blender camera projection, native orbit, zoom and pan, and preservation of the view when changing tabs. `check_site.py` validates local links, the twelve source PNG hashes, embedded model provenance and the preserved parts map.

## Reference candidates

Each non-queen piece has high-resolution PNG candidate enlargements of each original color, made with the built-in image-generation tool. Additional color grades are identified in the candidate labels and records. Original black and white 300 × 300 sprites remain available in both selectors. These are interpretations for review; generated grain and carving details are not recovered source geometry.

Choose images A and B, then use Blend or Wipe and the A–B slider. A only/B only show exact endpoints; Swap exchanges the sources. Fit/1×/2× and drag-to-pan inspect details. Background choices help inspect transparent edges. Align to original applies measured uniform scale and translation without warping. The white knight is mirrored in aligned view to match the black knight; disable alignment to see its original orientation and framing. Downloads always return the untouched image files.

`assets/candidates/generation.json` records exact prompts, source hashes and output hashes. `assets/candidates/alignment.json` records browser placement and approximate silhouette overlap. `scripts/analyze_candidates.py` measures images using Pillow and NumPy without writing image pixels; `scripts/build_candidate_pages.py` builds the five HTML pages. Neither script modifies the queen review.

```sh
python scripts/analyze_candidates.py
python scripts/build_candidate_pages.py
node scripts/check_candidate_review.cjs
python scripts/check_site.py
```

The king comparison applies a common 5% display inset to provide headroom. The original king sprites themselves have clipped cross tips; display padding cannot restore them (see PROVENANCE.md). Bishop candidate revision 2 replaces the initial shallow engravings with a deep open mitre slit, generated again from the black original. Rejected bishop images are removed from the current tree (earlier versions remain in Git history).

The initial white candidates were generated directly from the white originals; later replacements and color grades keep their revision numbers. White bishop prompts use the same plain upscale instructions as the other pieces, with no mitre or slit guidance. Queen candidates were explicitly excluded. White knight candidates preserve their original facing direction in the files and are mirrored with the white original only when alignment is enabled.

Candidate comparisons open in Wipe mode. Drag the middle arrow or use the toolbar slider; the handle stays reachable at either endpoint and follows the visible area when zoomed. The focused handle also supports arrow keys (Shift for larger steps), Home and End. Dragging elsewhere still pans.

Candidate alignment now refines the whole-outline fit with the visible lower rings. `scripts/refine_foot_alignment.py` compares smoothed vertical brightness gradients against the same-color original and applies a small vertical translation only (less than four pixels in the original 300px canvas). Scale and horizontal placement stay fixed; weak or tied matches stay unchanged. `analyze_candidates.py` runs this step automatically. The saved `silhouette_y` makes repeated refinement idempotent. `assets/candidates/foot-alignment-report.json` records each correction and before/after agreement. This reduces registration error without warping away differences in generated ring thickness or curvature.

Rook candidates were replaced after turret review: black and white candidates 4–6 are the thin-rim versions, with additional black color grades 7 and 8. Earlier candidates 1–3 remain only in Git history. Generation records identify the historical input revision for edited candidates. Both original Lichess sprites remain available.

The [set comparison](set-comparison.html) shows all six pieces as candidate/original pairs at matched scale up to 300 pixels per image. Switch black/white and choose candidates independently. White queen remains unavailable. Rebuild with `python3 scripts/build_set_comparison.py` after changing candidate placements.
