# Provenance of the Lichess Staunton pieces

This is a continuing investigation into the source images used by **listaunton**. It records what we can verify, separates interpretation from evidence, and leaves room for new findings. Updated **November 18, 2026**.

## What these pieces are

Our references are the twelve rendered sprites in Lichess’s **3D Staunton** set: king, queen, rook, bishop, knight and pawn, each in black and white. The exact source directory is `public/images/staunton/piece/Staunton` in the `lichess-org/lila` repository. The similarly named parent directory contains other sets; those should not be conflated with this specific set. The extra knight preview is not one of the twelve playing pieces.

The images depict wooden pieces, with grain, highlights and shadows baked into the renders. Our project is an independent reconstruction of their geometry and appearance, beginning with the queen. A sprite is not a recoverable 3D scene; unseen geometry and some proportions require interpretation.

## Where our copies came from

The active PNG references in [references/lichess-staunton-3d](references/lichess-staunton-3d/) were extracted verbatim from the local Lichess checkout on October 2, 2026, at commit `776e1ff6680182bfedaf17cd8500e1c3cc3defd0`. Their [manifest](references/lichess-staunton-3d/original-png-manifest.json) records hashes. Previously collected WebP copies remain in the same folder for history; they are not the original 2017 upload files.

For this investigation we separately extracted all twelve PNG blobs from the first import commit. We inspected their PNG chunks and decoded the embedded XMP rather than relying on filesystem dates. Raw XMP and a [manifest with original file hashes, identifiers and save histories](docs/provenance/2017-import/manifest.json) are preserved alongside this document. The first-import PNGs remain retrievable through the per-piece links below.

## Arrival in Lichess

- **January 29, 2017:** [6043adc — Add Staunton 3D piece set](https://github.com/lichess-org/lila/commit/6043adc1324b712e630d75e53338af377137b645). The commit adds all twelve images and enables the set. Its message explicitly gives the source as [Lichess pieces: 3D Staunton on Userstyles](https://userstyles.org/styles/134558/lichess-pieces-3d-staunton).
- **February 1, 2017.** Lichess added a tentative credit to Eden Murs, linking to the same Userstyles record. [Credit commit d8357c4](https://github.com/lichess-org/lila/commit/d8357c4f0067722d50c4f6c5cc446f2c32e385d0).
- **July 7, 2017:** [15b4a25 — lossy png compression for 3d pieces](https://github.com/lichess-org/lila/commit/15b4a256928b5a96417934c24009223f03952303).
- **February 27, 2019:** [463329a — Optimize images to reduce filesize](https://github.com/lichess-org/lila/commit/463329af9a4b75cb1daeb046f4dba0d0ab375aea).

The two optimization commits were found while following both king files through Git history. They explain why the current PNG bytes differ from the first import. The first commit was made by Thibault Duplessis (ornicar); committing the import does not establish authorship of the artwork. The import commit identifies the immediate source. The evidence for the earlier part of the chain is below.

## Recovered Userstyles version

FreeStyler preserved the lost style as **Lichess Pieces: 3D Staunton**, mirror ID **147617**. Its preview shows the same wooden pieces on a Lichess board. The mirror credits **EdenMurs@userstyles**, account **367394**, and its related styles list the same account ID under **DenWalker@userstyles**. The preview shows the Lichess handle **EdenMurz**, which also links to the EdenMurs Userstyles collection in a first-person forum post. [FreeStyler record](https://freestyler.ws/style/147617/lichess-pieces-3d-staunton), [preserved board screenshot](https://freestyler.ws/images/styles_screenshot/5/295/147617/147617_after.jpeg?u=1490486760), [uploader’s Lichess thread](https://lichess.org/forum/general-chess-discussion/my-new-lichess-themes-and-pieces).

The style record gives **October 31, 2016** as its creation date and **February 6, 2017** as its update date. The screenshot and stylesheet survive from the mirrored version. The date the style record was created is insufficient to date its first use of these sprites. The same Userstyles ID was subsequently called *Chess.com Board: Fritz Wood 1* in a March 2018 export and is now *Chess.com pieces: Fritz*. The current CSS links to a different set of twelve images, all downloaded and checked against the import hashes. [March 2018 export](https://gitlab.com/heterosexual/archives/userstyles.org/-/blob/0b2d75b0c6a336e49ed027d58bd8f98dc90d126d/styles/134558.json), [current Userstyles record](https://userstyles.org/styles/134558.json), [current CSS](https://userstyles.org/styles/134558.css).

The mirror’s **Show Code** response gives twelve separate PNG URLs on the Russian image host Radikal. Each URL contains a `1701` path segment, consistent with January 2017 and the last Photoshop saves. The URLs establish where the mirrored style loaded the images. The CSS offers no credit for the renders or source link before Radikal. No successful Wayback capture was found for any of the twelve full-size URLs. The Black Queen URL now serves a website landing page in place of the PNG. ArchiveTeam reports that its separate 2022 rescue covered public gallery thumbnails. [Recovered stylesheet](https://freestyler.ws/api/v2/get_css.php?json=%5B%7B%22id%22%3A147617%2C%22params%22%3A%5B%5D%7D%5D), [ArchiveTeam Radikal project](https://wiki.archiveteam.org/index.php/Radikal).

<details>
<summary>Original Radikal URLs from the mirror</summary>

| Piece | URL |
| --- | --- |
| Black Bishop | `http://s018.radikal.ru/i507/1701/e6/775f65c09e20.png` |
| Black King | `http://s019.radikal.ru/i641/1701/e6/cbd23e33bd90.png` |
| Black Knight | `http://s09.radikal.ru/i182/1701/5f/fe7da5b70677.png` |
| Black Pawn | `http://s018.radikal.ru/i517/1701/25/b30441835799.png` |
| Black Queen | `http://s008.radikal.ru/i304/1701/6d/73acc9bbc877.png` |
| Black Rook | `http://s011.radikal.ru/i317/1701/45/5f9ba373c9e6.png` |
| White Bishop | `http://s019.radikal.ru/i625/1701/da/e494f84f0f6d.png` |
| White King | `http://s014.radikal.ru/i328/1701/48/6f25c419349a.png` |
| White Knight | `http://s018.radikal.ru/i515/1701/21/57c718ea333c.png` |
| White Pawn | `http://s06.radikal.ru/i179/1701/63/0a798d451e73.png` |
| White Queen | `http://s45.radikal.ru/i108/1701/63/831b5e582cc4.png` |
| White Rook | `http://s014.radikal.ru/i326/1701/e4/6b3a86a71483.png` |

The recovered screenshot has SHA-256 `1dc9b428f08a65f021591cb1e0b9b7a061909f47d75064c5dbe33ef978c5d686`.

</details>

## Search for an earlier copy

The twelve first-import PNGs were checked against their recorded SHA-256 values. Searches using original filenames, selected hashes, Git blob IDs, XMP identifiers and Radikal filenames found no earlier copies. Google Lens showed no exact matches for the first-import black queen or knight. These results cover the sources and indexes checked.

- **Lucas Chess, April 2015.** Version 9.03 introduced Marc Graziani’s *Staunton 3D*. The twelve embedded PNGs tested had different hashes, and the pictured rook, queen and knight have different shapes. [Release announcement](https://lucaschess.blogspot.com/2015/04/version-903-new-set-of-pieces-stauton.html), [2015 piece directory](https://github.com/lukasmonk/lucaschess/tree/9f9b17fd8d3bfca6d58af65a2a29689ca7334f7b/Pieces/Staunton%203D).
- **Chess.com.** The sampled *3D Staunton*, *Real 3D* and *3D Plastic* art share a different knight with a ribbed mane and a different rook with wide crenels and a domed interior. The *3D ChessKid* art is also distinct. [Chess.com Staunton knight](https://images.chesscomfiles.com/chess-themes/pieces/3d_staunton/150/bn.png), [Chess.com Staunton rook](https://images.chesscomfiles.com/chess-themes/pieces/3d_staunton/150/br.png).
- **Fritz.** The similarly named theme on the reused Userstyles ID is the flat Fritz set. The 2006 *Fritz die Zehnte* report shows separate Fritz 3D wood examples. The close-ups of Fritz 9 wood and Fritz 10 Tropical Wood have distinct rook and knight shapes. This leaves other Fritz themes unverified. [Fritz 10 report, figures 17–20](https://computerschach.de/Files/2006/Fritz%20die%20Zehnte.pdf#page=14).

The earliest dated evidence for these particular PNGs remains the December 28, 2016, Photoshop preparation recorded in the imported files. The earlier renders or models could predate that work. Their creator and source before the Userstyle remain unknown.

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

We have not verified the artist, modeller, renderer, original model files or a license specifically covering this exact set. The FreeStyler mirror labels the userstyle CC0. The rights to the underlying artwork remain unverified. Do not attribute it to James Clarke on the basis of a broad directory credit or another set’s provenance. Earlier discussion in this project made that attribution and it was withdrawn as unsupported for these pieces. Neither this document nor the reconstruction grants a new license to the source artwork.

## Our generated references are separate works of interpretation

The queen’s high-resolution reference was generated through ChatGPT and selected by the project owner from multiple candidates. Other pieces have generated black and white enlargements for comparison. These may infer or alter grain, carving and geometry; they are not newly discovered historical renders. [Candidate generation records](assets/candidates/generation.json) preserve prompts and input/output hashes. The original sprites remain available for comparison. We are selecting working high-resolution references; selection does not change the provenance of the originals.

## Open questions and next evidence to seek

- Can a pre-import copy of the style or a surviving Radikal file establish when the sprites were first published?
- Can an earlier asset pack, program, or firsthand source identify where EdenMurs obtained the renders?
- Are there earlier, larger or uncropped versions of these exact renders?
- Can the embedded document identifiers be matched to other surviving files?
- Who created the underlying models and wood materials, in which application, and under what terms?
- At what step were the king crosses clipped?

## How to continue this record

Add dated findings with direct source links, commit IDs or file hashes. Preserve raw evidence when practical. Clearly mark observations, interpretations and unresolved claims. Do not replace an uncertain attribution with a confident one without supporting evidence. If a conclusion changes, retain a short correction explaining why.

### Investigation log

- **October 4, 2026:** traced both king PNGs to the January 2017 import; confirmed clipping in those original blobs; recovered the import’s Userstyles source link; extracted and inspected XMP from all twelve original PNGs. Saved per-piece metadata and original SHA-256 hashes. No verified artwork author or original 3D application found.

- **November 6, 2026:** began a visual comparison with historical and modern Staunton families. [A Chavet set shown from the side](https://www.chess.com/forum/view/chess-equipment/finally-please-help-identify-these-pieces) and [another seen from above](https://www.chess.com/forum/view/chess-equipment/help-identifying-a-chavet-chess-set) share several features with the Lichess queen, including a low finial within a flared crown. The accompanying bishop and turned bases also provide useful comparisons, while the knights differ visibly. These are observations of resemblance, not evidence that a Chavet set was used as a reference, nor a new attribution of the Lichess artwork. The [queen study](queen-study.html) records the photograph sources and distinguishes historical examples from reproductions.

- **November 18, 2026.** Recovered the original Userstyle’s preview and image URLs from FreeStyler, tied the EdenMurs and DenWalker names to the same Userstyles account, and checked exact hashes and visual matches against other sets. The original modeller and any earlier publication remain unresolved.
