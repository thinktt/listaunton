# listaunton

Recovering the Lichess **Staunton** chess set as editable 3D models from its static rendered images. We are starting with the queen. This is an independent art reconstruction, with interpretation where a single image cannot determine the geometry.

Open [the home page](index.html) to access:

- [Rotating queen](queen-3d.html): the current mesh, orbit controls, and the saved overlay camera.
- [Combined queen review](review.html): interactive 3D rotation and the high-res parts map alongside current/previous renders against either the selected high-res reference or original Lichess queen, direct comparison of both source images, opacity/blink controls, and detail views.
- [Queen parts map](queen-parts.html): the names used to discuss the model.
- [Original Staunton references](staunton-references.html): all twelve original PNG sprites from Lichess’s 3D Staunton set, paired by piece.

The queen geometry includes a continuous splash-shaped crown, eight tips, a shallow bowl and seated egg-shaped finial. Its three thin collars now sit closely stacked, with roughly 44% less center spacing and narrow grooves in place of the tall spacers. The neutral and brown materials are shape studies. Faithful wood grain is still to come.

## Files

- `models/queen/queen-rebuilt.blend`: current editable Blender model, with its reference packed inside.
- `assets/queen/`: the supplied high-resolution reference, renders, comparisons and validation reports.
- `references/lichess-staunton-3d/`: all twelve original PNG sprites, their provenance and hashes, plus the previously collected WebP versions.
- `scripts/queen/`: portable current generation, export and checking pipeline.
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

**Compare references** places the selected high-res image over the original sprite, with the same opacity, hold and blink controls. While comparing sources, model revision/material controls are paused. The fixed detail panels and contours remain explicitly high-res comparisons.

The original sprite is positioned by uniform scaling and translation fitted to the high-res silhouette, independently of the reconstructed model. No anisotropic stretching or warping is applied. The recorded scale is about 4.218×; the original and high-res outlines overlap by about 98.5% at the quarter-resolution fit. This describes silhouettes, not matching internal geometry or recovered detail. The browser smooths the enlarged source image.

`assets/queen/original-reference-alignment.json` records placement, source hashes and fitting method. Run `python scripts/queen/align_original_reference.py` to recompute the alignment and update the page's embedded metadata if the references change. `node scripts/queen/check_review_reference.cjs` checks the page's actual control logic, alignment hashes, zoom/pan stability, hold/blink behavior and contour guards.

## One-page queen review

`review.html` combines the existing comparison, 3D model, and parts map. Drag the comparison picture to switch into the current 3D model and continue rotating with that same drag. Short clicks do not trigger a switch. Shift-drag or right-drag pans the comparison image without leaving it.

The **3D model** button opens the same standalone viewer inside the review page, with its projection, material, camera-angle, zoom, reset, free orbit, and pan controls. Initial loading preserves the first drag by queuing movement until the viewer is ready. Returning via the button preserves its current orbit; beginning a fresh drag from the comparison starts at the matched overlay camera. The interactive 3D model is always the current revision.

**Parts map** shows the existing high-res diagram and fourteen-part name key. Its original file, sandbox, and content-security policies are unchanged. **Reference overlay** returns to the comparison, where the original black Lichess and generated high-res references remain available. The model and map frames load on first use; their standalone pages remain available too.

`check_review_reference.cjs` covers view switching, queued drag handoff, image panning, reference selection and the original comparison controls. `check_viewer_camera.cjs` checks the embedded gesture bridge as well as the exact Blender camera projection, orbit, zoom and pan math. Only messages from the corresponding parent/frame are accepted.
