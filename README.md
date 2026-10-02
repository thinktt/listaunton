# listauton

Recovering the Lichess **Staunton** chess set as editable 3D models from its static rendered images. We are starting with the queen. This is an independent art reconstruction, with interpretation where a single image cannot determine the geometry.

Open [the home page](index.html) to access:

- [Rotating queen](queen-3d.html): the current mesh, orbit controls, and the saved overlay camera.
- [Reference overlay](review.html): current/previous renders, opacity and blink comparison, and detail views.
- [Queen parts map](queen-parts.html): the names used to discuss the model.

The queen geometry includes a continuous splash-shaped crown, eight tips, a shallow bowl and seated egg-shaped finial. The neutral and brown materials are shape studies. Faithful wood grain is still to come.

## Files

- `models/queen/queen-rebuilt.blend`: current editable Blender model, with its reference packed inside.
- `assets/queen/`: the supplied high-resolution reference, renders, comparisons and validation reports.
- `references/lichess-staunton-3d/`: all twelve original Lichess piece images and source notes.
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
blender --background --python scripts/queen/validate_seamless_crown.py
node scripts/queen/check_viewer_camera.cjs
python scripts/check_site.py
```

Use an absolute Blender executable path if it is not on PATH. For Windows Blender with this repository in WSL, pass Windows/UNC versions of script paths (obtain them with `wslpath -w`), rather than Linux `/home/...` paths. Each script resolves repository paths from its own location. The saved model still contains its original render-output path until rebuilt; the external reference is already packed.

`validate_seamless_crown.py` checks the current crown revision against the preserved pre-seamless baseline. Its exact body/finial preservation checks are specific to that change; revise those expectations deliberately when future geometry changes are authorized.

The 3D viewer embeds its mesh and works without a server. The parts map keeps its original sandbox/CSP and uses external UI libraries from unpkg.com, so it needs internet access for those libraries.

## GitHub Pages

The repository is committed locally; pushing is left to the owner. Create a GitHub repository named `listauton`, add it as `origin`, and push `main`. In GitHub **Settings → Pages → Build and deployment → Source**, select **GitHub Actions**. Run **Publish site** from Actions if the initial push occurred before Pages was enabled.

The included workflow publishes on subsequent pushes to `main`. It packages the four root HTML pages, their assets and the Blender download; it does not deploy the historical working folders. If hosted under the `thinktt` account with the repository name `listauton`, the expected URL is `https://thinktt.github.io/listauton/`. It is not live until the owner pushes and Pages deployment succeeds.

To check the publishable bundle locally:

```sh
python3 scripts/package_site.py
python3 scripts/check_site.py _site
```

See [GitHub's custom Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## References and attribution

The twelve sprites came from Lichess's `public/images/staunton/piece/Staunton` directory. Specific authorship is unclear; see `references/lichess-staunton-3d/SOURCE.txt`. The high-resolution queen reference was supplied by the project owner after generating it with ChatGPT. It is an interpretation used for reconstruction, not recovered original geometry. No new license claim is made for these reference assets.
