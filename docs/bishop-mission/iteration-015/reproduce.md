# Reproduce the bishop pigment checkpoint

Work in an isolated copy with Blender 5.2.2 and Python/NumPy/Pillow. Preserve
the archived checkpoint-013 model and atlas. The exact accepted construction
commands and expected atlas hash are in `reproduction.json`; its bytes are
part of the saved scene's declaration and must remain unchanged.

The pipeline captures the unchanged surface and actual visibility, makes a
smooth fallback, measures the accepted BSDF, estimates visible pigment while
retaining uncertain existing detail, then limits the new atlas to the lower
body. The final shaded material is a Principled BSDF, never the diagnostic
emission used to measure pigment/position. Source reference pixels stay exact.

After the final saved/reopened render has been inspected, stage its
`125-final/bishop.blend`, `125-final/wood.png` and the
`125-turned-body-pigment/albedo.png` into the model, render and atlas locations
in the isolated copy. Run these checks from the repository root:

```text
blender --background --python-exit-code 1 --python scripts/bishop/validate_checkpoint.py
blender --background --python-exit-code 1 --python scripts/bishop/render_diagnostics.py
blender --background --python-exit-code 1 --python scripts/bishop/render_clay.py
python scripts/bishop/compare_export_checkpoint.py --baseline history/bishop-mission-013 --out docs/bishop-mission/iteration-015/export-comparison.json
python scripts/bishop/compare.py
python scripts/bishop/mission_compare.py --render assets/bishop/render.png --previous history/bishop-mission-013/render.png --out build/bishop-mission/125-final/comparison
python scripts/bishop/refresh_review.py
node scripts/bishop/check_viewer.cjs
node scripts/bishop/check_review.cjs
```

The historical validation checks the strict receiver change on checkpoint 012,
then the atlas change 012→013, then 013→015. Archived atlas paths are resolved
by their declared hashes beside the archived models when the public path has
changed. The current scene still receives its own geometry, anatomy, receiver,
camera and export checks. No tolerance was relaxed for this material change.

`trials.json` contains the eight assessments and model/render hashes. Each
trial folder includes the actual beauty, comparison, scope audit and available
side/rear views. To regenerate earlier investigations, use
`height_continuous_pigment.py` with default, `--amount .5`, or
`--angular --clean-boundary-detail`; then use `infer_visible_pigment.py` with
the saved response/fallback and flags recorded in each `pigment.json`.
Trial 122 measures trial 120 again and supplies its independent `--scope-audit`.
All research scenes were reopened before rendering at 256 fixed samples;
the accepted final uses 512. The generators now use the immutable checkpoint-013
scope evidence, so later public materials cannot silently change their lineage.

Collect the completed evidence with `collect_continuous_checkpoint.py` after
all validators finish. `sync_continuous_checkpoint.py` is a one-time delivery
guard for this checkpoint: it refuses a canonical repo whose bishop has moved
past checkpoint 013 and copies only the named bishop artifacts. It does not
change shared gallery sizing, stage Git files, commit, push or publish.

The browser's lighting remains approximate. The saved Cycles beauty is the
reference comparison. The goal remains incomplete; see `assessment.md` for
residual color seams, grain and reflection defects.
