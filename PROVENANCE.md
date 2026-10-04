# Provenance of the Lichess Staunton pieces

This is a continuing investigation into the source images used by **listaunton**. It records what we can verify, separates interpretation from evidence, and leaves room for new findings. Last updated: **October 4, 2026**.

## What these pieces are

Our references are the twelve rendered sprites in Lichess’s **3D Staunton** set: king, queen, rook, bishop, knight and pawn, each in black and white. The exact source directory is `public/images/staunton/piece/Staunton` in the `lichess-org/lila` repository. The similarly named parent directory contains other sets; those should not be conflated with this specific set. The extra knight preview is not one of the twelve playing pieces.

The images depict wooden pieces, with grain, highlights and shadows baked into the renders. Our project is an independent reconstruction of their geometry and appearance, beginning with the queen. A sprite is not a recoverable 3D scene; unseen geometry and some proportions require interpretation.

## Where our copies came from

The active PNG references in [references/lichess-staunton-3d](references/lichess-staunton-3d/) were extracted verbatim from the local Lichess checkout on October 2, 2026, at commit `776e1ff6680182bfedaf17cd8500e1c3cc3defd0`. Their [manifest](references/lichess-staunton-3d/original-png-manifest.json) records hashes. Previously collected WebP copies remain in the same folder for history; they are not the original 2017 upload files.

For this investigation we separately extracted all twelve PNG blobs from the first import commit. We inspected their PNG chunks and decoded the embedded XMP rather than relying on filesystem dates. Raw XMP and a [manifest with original file hashes, identifiers and save histories](docs/provenance/2017-import/manifest.json) are preserved alongside this document. The first-import PNGs remain retrievable through the per-piece links below.

## Arrival in Lichess

- **January 29, 2017:** [6043adc — Add Staunton 3D piece set](https://github.com/lichess-org/lila/commit/6043adc1324b712e630d75e53338af377137b645). The commit adds all twelve images and enables the set. Its message explicitly gives the source as [Lichess pieces: 3D Staunton on Userstyles](https://userstyles.org/styles/134558/lichess-pieces-3d-staunton).
- **July 7, 2017:** [15b4a25 — lossy png compression for 3d pieces](https://github.com/lichess-org/lila/commit/15b4a256928b5a96417934c24009223f03952303).
- **February 27, 2019:** [463329a — Optimize images to reduce filesize](https://github.com/lichess-org/lila/commit/463329af9a4b75cb1daeb046f4dba0d0ab375aea).

The two later entries were found while following both king files through Git history. They explain why the current PNG bytes differ from the first import. The first commit was made by Thibault Duplessis (ornicar); committing the import does not establish authorship of the artwork. The Userstyles link is evidence of the immediate import source, not proof of the original modeller or renderer. We have not established the earlier chain of custody.

## Metadata shared by all twelve first-import PNGs

| Field | Recorded value |
| --- | --- |
| Dimensions | 300 × 300 pixels |
| Pixel format | 8-bit RGBA, including transparency |
| Creator tool | Adobe Photoshop CC 2014 (Windows) |
| XMP creation date | December 28, 2016, 14:23:42 +03:00 |
| Last modification date | January 19, 2017; individual times below |
| Color profile | sRGB IEC61966-2.1 |
| Resolution | XMP says 72 DPI; PNG physical resolution rounds to about 72.009 DPI |

The XMP records created/saved events, Photoshop document and instance identifiers, orientation, dimensions and color information. The identifiers are retained in the manifest; they are not artist names. No artist credit, artwork copyright, source URL or 3D rendering application was found in these embedded records. The Hewlett-Packard copyright inside the ICC profile applies to the color profile, not the chess artwork.

**Interpretation:** the consistent metadata supports a shared Photoshop preparation workflow. The identical creation timestamp could have been inherited from a common document or batch process. It does not prove that all models were created at that moment. The `+03:00` offset records a clock setting; it does not identify the creator’s country. Photoshop could have been used only to prepare existing renders. The metadata does not tell us which changes were made during each save.

## Per-piece records

All twelve have the common creation timestamp and software listed above. These are the **save events retained in their XMP**, not necessarily a complete edit history. All times below use the recorded **+03:00** offset. The final save in each row also matches its modification and metadata timestamps.

| Piece / first-import PNG | Recorded saves | Extracted metadata |
| --- | --- | --- |
| [Black Bishop](https://github.com/lichess-org/lila/blob/6043adc1324b712e630d75e53338af377137b645/public/images/staunton/piece/Staunton/Black-Bishop.png) | 2017-01-19 14:06:41 | [XMP](docs/provenance/2017-import/Black-Bishop.xmp) |
| [Black King](https://github.com/lichess-org/lila/blob/6043adc1324b712e630d75e53338af377137b645/public/images/staunton/piece/Staunton/Black-King.png) | 2017-01-19 13:52:53; 2017-01-19 14:47:43 | [XMP](docs/provenance/2017-import/Black-King.xmp) |
| [Black Knight](https://github.com/lichess-org/lila/blob/6043adc1324b712e630d75e53338af377137b645/public/images/staunton/piece/Staunton/Black-Knight.png) | 2017-01-19 14:22:52; 2017-01-19 14:31:41 | [XMP](docs/provenance/2017-import/Black-Knight.xmp) |
| [Black Pawn](https://github.com/lichess-org/lila/blob/6043adc1324b712e630d75e53338af377137b645/public/images/staunton/piece/Staunton/Black-Pawn.png) | 2017-01-19 13:26:35; 2017-01-19 14:34:18 | [XMP](docs/provenance/2017-import/Black-Pawn.xmp) |
| [Black Queen](https://github.com/lichess-org/lila/blob/6043adc1324b712e630d75e53338af377137b645/public/images/staunton/piece/Staunton/Black-Queen.png) | 2017-01-19 13:57:20; 2017-01-19 14:43:41 | [XMP](docs/provenance/2017-import/Black-Queen.xmp) |
| [Black Rook](https://github.com/lichess-org/lila/blob/6043adc1324b712e630d75e53338af377137b645/public/images/staunton/piece/Staunton/Black-Rook.png) | 2017-01-19 13:30:55; 2017-01-19 14:27:36 | [XMP](docs/provenance/2017-import/Black-Rook.xmp) |
| [White Bishop](https://github.com/lichess-org/lila/blob/6043adc1324b712e630d75e53338af377137b645/public/images/staunton/piece/Staunton/White-Bishop.png) | 2017-01-19 14:03:25; 2017-01-19 14:03:25 | [XMP](docs/provenance/2017-import/White-Bishop.xmp) |
| [White King](https://github.com/lichess-org/lila/blob/6043adc1324b712e630d75e53338af377137b645/public/images/staunton/piece/Staunton/White-King.png) | 2017-01-19 13:52:47; 2017-01-19 14:40:38 | [XMP](docs/provenance/2017-import/White-King.xmp) |
| [White Knight](https://github.com/lichess-org/lila/blob/6043adc1324b712e630d75e53338af377137b645/public/images/staunton/piece/Staunton/White-Knight.png) | 2017-01-19 14:12:06; 2017-01-19 14:12:06 | [XMP](docs/provenance/2017-import/White-Knight.xmp) |
| [White Pawn](https://github.com/lichess-org/lila/blob/6043adc1324b712e630d75e53338af377137b645/public/images/staunton/piece/Staunton/White-Pawn.png) | 2016-12-28 15:16:39; 2017-01-19 13:26:29 | [XMP](docs/provenance/2017-import/White-Pawn.xmp) |
| [White Queen](https://github.com/lichess-org/lila/blob/6043adc1324b712e630d75e53338af377137b645/public/images/staunton/piece/Staunton/White-Queen.png) | 2016-12-28 15:00:41; 2017-01-19 14:41:31 | [XMP](docs/provenance/2017-import/White-Queen.xmp) |
| [White Rook](https://github.com/lichess-org/lila/blob/6043adc1324b712e630d75e53338af377137b645/public/images/staunton/piece/Staunton/White-Rook.png) | 2017-01-19 13:29:14; 2017-01-19 14:39:06 | [XMP](docs/provenance/2017-import/White-Rook.xmp) |

## The kings’ clipped crosses

Both original king images already have their crosses cut by the top image boundary in the **January 29, 2017 import**. We extracted and visually inspected both earliest PNGs: each is 300 × 300 and has nontransparent pixels at row zero. The current PNGs and retained WebP copies also show the clipping. It therefore predates the later compression commits and is not caused by our review page.

This establishes that Lichess received the images in this condition. It does not establish whether the clipping happened during rendering, cropping, Photoshop preparation or an earlier step. Display padding cannot recover the missing pixels; any completed cross would be a reconstruction and should be labelled accordingly.

## Authorship and rights remain unresolved

We have not verified the artist, modeller, renderer, original model files or a license specifically covering this exact set. Do not attribute it to James Clarke on the basis of a broad directory credit or another set’s provenance. Earlier discussion in this project made that attribution and it was withdrawn as unsupported for these pieces. Neither this document nor the reconstruction grants a new license to the source artwork.

## Our generated references are separate works of interpretation

The queen’s high-resolution reference was generated through ChatGPT and selected by the project owner from multiple candidates. Other pieces have generated black and white enlargements for comparison. These may infer or alter grain, carving and geometry; they are not newly discovered historical renders. [Candidate generation records](assets/candidates/generation.json) preserve prompts and input/output hashes. The original sprites remain available for comparison. We are selecting working high-resolution references; selection does not change the provenance of the originals.

## Open questions and next evidence to seek

- Can the original Userstyles page or an archived version identify its uploader, image-host URLs or upstream source?
- Are there earlier, larger or uncropped versions of these exact renders?
- Can the embedded document identifiers be matched to other surviving files?
- Who created the underlying models and wood materials, in which application, and under what terms?
- At what step were the king crosses clipped?

## How to continue this record

Add dated findings with direct source links, commit IDs or file hashes. Preserve raw evidence when practical. Clearly mark observations, interpretations and unresolved claims. Do not replace an uncertain attribution with a confident one without supporting evidence. If a conclusion changes, retain a short correction explaining why.

### Investigation log

- **October 4, 2026:** traced both king PNGs to the January 2017 import; confirmed clipping in those original blobs; recovered the import’s Userstyles source link; extracted and inspected XMP from all twelve original PNGs. Saved per-piece metadata and original SHA-256 hashes. No verified artwork author or original 3D application found.
