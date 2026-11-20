# Repository layout

| Directory | Contents |
| --- | --- |
| `inputs/` | Original Lichess sprites, selected and alternate references, side studies, material source images, and their provenance. |
| `blender/` | Editable Blender files, active build scripts, historical checkpoints and scripts, and replay inputs and settings. |
| `page/` | The source HTML, CSS, and JavaScript. Large embedded images and mesh buffers are represented by content hashes. |
| `dist/` | Ignored renders, mesh exports, site payloads, the site build, and replay workspaces. |

`docs/` keeps the mission records, comparisons expressed as data, and
provenance notes. Paths quoted in historical notes refer to the original
checkout layout. The migration manifest records the original paths and
SHA-256 hashes of the generated files moved out of Git.

## View and package the site

```sh
python3 blender/project.py site
python3 -m http.server 8000 --directory dist/site
```

Open `http://localhost:8000`. The build assembles the old relative URLs
under `dist/site` and restores the payloads required by the existing
viewers and sandboxed queen frames. A fresh clone needs the matching site
output archive. That archive is built in the working checkout:

```sh
python3 blender/project.py pack
# The archive is dist/site-outputs.tar.gz.
python3 blender/project.py unpack /path/to/site-outputs.tar.gz
python3 blender/project.py site
```

GitHub Pages uses the workflow in `.github/workflows/pages.yml`. Set the
repository Actions variable `LISTAUNTON_SITE_OUTPUTS_URL` to a downloadable
HTTPS URL for the matching archive, such as a release asset. The workflow
checks archive hashes and deploys only `dist/site`.

## Render and replay

Render a saved camera and lighting setup straight from a native model:

```sh
python3 blender/project.py render blender/models/knight/knight-rebuilt.blend
```

The PNG goes under `dist/renders/`. In WSL, pass `--blender` with the
path to Blender's Windows executable if Blender is installed on Windows.
For alternate cameras, comparisons, and exports, use the corresponding
piece's scripts and mission log. Many of those scripts predate this
layout and resolve inputs relative to the script file. Prepare a copy
with the paths they expect:

```sh
python3 blender/project.py workspace
cd dist/workspace
python3 scripts/check_model_site.py
```

Stage settings, generation scripts, and native models still describe
the iterations they were saved with. Some older reports and previews
depend on caches, external inputs, or tool versions that the individual
recipe may not fully capture. Use the full pre-rewrite repository backup
for exact saved outputs and to resolve original commit IDs cited in notes:

```sh
python3 blender/project.py recover /path/to/pre-rewrite-backup ORIGINAL_COMMIT
```

The recovered snapshot goes to `dist/recovered/<original-commit>/`
with its original paths. Historical scripts can overwrite files in their
own workspace. Run them in that workspace when replaying an old study.

After a build in `dist/workspace`, copy intentional model or input
changes to the corresponding source folders. Use `capture` for specific
new or changed pages and generated files. This updates the page template
or writes the generated file under `dist` and records its hash for
packaging:

```sh
python3 blender/project.py capture assets/knight/render.png assets/knight/mesh.bin knight-model.html
python3 blender/project.py site
python3 blender/project.py pack
```
