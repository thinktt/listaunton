# listauton

Reconstruct the Lichess Staunton chess set from its rendered images, beginning with the queen. Interpret unseen geometry as an art project while matching the references carefully. Wood grain is planned; current materials are diagnostic.

The user requests a Git commit after each completed, checked iteration. Do not push or publish unless asked; the user currently handles pushing.

Append a co-author trailer to every commit, using the actual model name:

    Co-Authored-By: Codex <actual model name> <codex@openai.com>

For the initial import the user explicitly supplied `GPT 6 Astra Ultra`. Future agents must use their own actual identity, not infer it from this import. Ask if unavailable. This is message attribution, not cryptographic signing.

Active scripts are in `scripts/queen`. The editable model is `models/queen/queen-rebuilt.blend`; rendered references and comparisons are in `assets/queen`. Keep the interactive viewer and overlay synchronized with the same model and saved camera. Verify substantive geometry changes with the model validator, mesh export checks, and camera regression.

The root pages are `index.html`, `queen-3d.html`, `review.html`, and `queen-parts.html`. Preserve the parts map's sandboxed iframe and CSP. Do not change the overlay's behavior while changing geometry.

`history/` preserves earlier iterations and scripts as evidence. Those scripts may contain obsolete paths and destructive overwrite assumptions: do not run them as the current pipeline. The seamless-crown validator uses the specific baseline under `history/queen-hires/before-seamless-crown`.

The precise authorship of the original Lichess pieces is unclear. Do not attribute these pieces to James Clarke. Preserve the source notes; do not invent a license for the supplied references.
