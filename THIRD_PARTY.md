# Third-party resources

## Galmuri

Author: Lee Minseo (quiple). SIL Open Font License 1.1.
Source: https://github.com/quiple/galmuri
Files: vendor/galmuri/Galmuri7.ttf, Galmuri9.ttf, Galmuri11.ttf, OFL.txt.
Downloaded 2026-09-25 from the upstream main branch; exact SHA-256 values are recorded in vendor/galmuri/SHA256.json.
Fonts are unmodified. Build-generated PNG glyphs derive from Galmuri; retain its notice and license.

## The Ur-Quan Masters

Game assets are read from the user's installed Steam game during build; they are not included in this repository.
Public source inspected for resource format documentation: https://github.com/intgr/uqm-wasm/tree/main/sc2/src
The local installation's Manual.txt documents --addon and .rmp resource maps.
This is an unofficial fan project, not affiliated with the original developers.

## Font provenance and usage policy

Official webfont/documentation: https://github.com/quiple/galmuri#use-as-web-fonts
Official license: https://github.com/quiple/galmuri/blob/main/ofl.md
Local license: [OFL.txt](vendor/galmuri/OFL.txt). License: SIL OFL 1.1.

| File | Official download | Raster size | Current use |
|---|---|---|---|
| Galmuri7.ttf | https://raw.githubusercontent.com/quiple/galmuri/main/dist/Galmuri7.ttf | 8px (7px ink) | Compact UI and log/tiny glyphs |
| Galmuri9.ttf | https://raw.githubusercontent.com/quiple/galmuri/main/dist/Galmuri9.ttf | 10px (9px ink) | Player choices, commander/Ur-Quan subtitle trial; larger UI trial |
| Galmuri11.ttf | https://raw.githubusercontent.com/quiple/galmuri/main/dist/Galmuri11.ttf | 12px (11px ink), 24px | Micro font and start-menu artwork |

The official project offers web fonts too. This patch uses vendored TTFs to generate PNGs locally;
playing does not require a CDN or network connection. Never shrink a larger pixel face to an
unsupported size. Galmuri7 has limited Hangul syllable coverage; check each newly translated glyph.

Exact downloaded bytes are pinned by [SHA256.json](vendor/galmuri/SHA256.json), not by a claimed
upstream commit. The URLs above point to a moving branch. Recheck hashes and coverage on updates.

Whenever adding/replacing an external font or other asset, update this source section in the same
change with author, official source/download, license, local license file, file hash, usage and any
modifications. Free download alone is not a redistribution license. Keep font attribution/licenses
with generated assets. Record modifications explicitly; do not claim a modified font is original.

Race/dialogue assignments are tracked in [FONTS.md](translations/FONTS.md) and [fonts.ko.json](translations/fonts.ko.json). Proposed assignments do not mean those fonts have been applied in game. No additional external font files were introduced by this mapping.

## Race-font selection specimens (2026-09-25)

Added unmodified Galmuri11-Bold.ttf and Galmuri11-Condensed.ttf by Lee Minseo (quiple), SIL OFL 1.1.
Official downloads:
- https://raw.githubusercontent.com/quiple/galmuri/main/dist/Galmuri11-Bold.ttf
- https://raw.githubusercontent.com/quiple/galmuri/main/dist/Galmuri11-Condensed.ttf

Local files: vendor/galmuri/. License: vendor/galmuri/OFL.txt.
Hashes: vendor/galmuri/SHA256.json and translations/fonts.ko.json.
Render at 12px (11px ink). These are design specimens, not yet installed race-font replacements.
The earlier Galmuri specimen has been superseded by the independent-family specimen described below; the current image uses no game artwork.
Generator: tools/render_font_selection.py. No font outlines were modified.

Also researched but not bundled or applied: NeoDunggeunmo by Eunbin Jeong (Dalgona),
https://github.com/neodgm/neodgm (SIL OFL 1.1). It is not a selected font for this trial.

## Independent-family candidates (2026-09-25)

These four fonts are downloaded for specimens and future dialogue trials only. They are **not yet
included in generated game addons**. Fonts are unmodified. docs/font-selection.png now renders these
candidates and the existing Galmuri9 baseline; see each license and attribution below.
On future game integration, ship the relevant complete license/credit files with the addon too.

| Font/version | Author | Official source/download | License / local notices |
|---|---|---|---|
| Mona10 / 2026.08.16 | Monad ABXY | https://github.com/MonadABXY/mona-font ; https://github.com/MonadABXY/mona-font/releases/download/2026.08.16/MonaFont-ttf.zip | OFL 1.1; vendor/mona/LICENSE/ (all upstream bundled notices) |
| Mulmaru / v1.0 | Mushsooni | https://github.com/mushsooni/mulmaru ; https://github.com/mushsooni/mulmaru/releases/download/v1.0/Mulmaru.zip | OFL 1.1; vendor/mulmaru/LICENSE.txt |
| x10y12pxDenkiChipHangul / v1.213 | Lee Minseo; hicc and x8y12pxDenkiChip Project Authors | https://github.com/quiple/x10y12pxDenkiChipHangul ; https://raw.githubusercontent.com/quiple/x10y12pxDenkiChipHangul/v1.213/fonts/ttf/x10y12pxDenkiChipHangul.ttf | OFL 1.1; vendor/denkichip/OFL.txt and AUTHORS.txt |
| Dalmoori / v0.200 | RanolP and contributors | https://github.com/RanolP/dalmoori-font ; https://github.com/RanolP/dalmoori-font/releases/download/v0.200/dalmoori-font.zip | Apache 2.0; vendor/dalmoori/LICENSE |

Exact chosen archive members, font SHA-256 and archive SHA-256 are recorded in translations/fonts.ko.json.
Each vendor/<family>/SHA256.json also pins all bundled font/license bytes. No upstream commit is inferred
from a download date. Mona retains all supplied notices for Ark Pixel, M+ Fonts, k8x12 and Noto Emoji
alongside its own OFL even though this trial renders only Korean text. DenkiChip is an extension of
x8y12pxDenkiChip, not a Galmuri weight variant. Mulmaru and Dalmoori list design references in their
upstream READMEs; distinct font projects do not imply every glyph has unrelated origins.

## Expressive outline candidates (2026-09-25)

Eight unmodified official Google Fonts TTF files are bundled for comparison only, not installed game replacements. All are SIL OFL 1.1; preserve their complete copyright and license notices on redistribution. Author below is the upstream designer metadata; copyright holders appear in each OFL.txt. Metadata and binaries are pinned to the same Git commit. No outlines were modified.

| Font | Designer | Official pinned source / download | Local license | SHA-256 |
|---|---|---|---|---|
| NanumPenScript | Sandoll Communication | [source](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/nanumpenscript) / [TTF](https://raw.githubusercontent.com/google/fonts/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/nanumpenscript/NanumPenScript-Regular.ttf) | vendor/nanumpenscript/OFL.txt | `6f0d1ab29c7894010dc88831fb7a0a51edb79136e450344183de5b1a8b52bd43` |
| NanumBrushScript | Sandoll Communication | [source](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/nanumbrushscript) / [TTF](https://raw.githubusercontent.com/google/fonts/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/nanumbrushscript/NanumBrushScript-Regular.ttf) | vendor/nanumbrushscript/OFL.txt | `27ceaf578c96f594cdf07fe0181b251790acbb746a164e45c1f6473f89911a31` |
| Gaegu | JIKJI SOFT | [source](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/gaegu) / [TTF](https://raw.githubusercontent.com/google/fonts/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/gaegu/Gaegu-Regular.ttf) | vendor/gaegu/OFL.txt | `aa52c98336f7c62e2896fc8b12b56a75d5b476d88a2f104b0980f4f7ce0adfc3` |
| EastSeaDokdo | YoonDesign Inc | [source](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/eastseadokdo) / [TTF](https://raw.githubusercontent.com/google/fonts/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/eastseadokdo/EastSeaDokdo-Regular.ttf) | vendor/eastseadokdo/OFL.txt | `8cebb39d375134fdbcedef9bf4ec4f6c3f02c39ed0aacd6e83f7a0f435e593b2` |
| KirangHaerang | Woowahan Brothers | [source](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/kiranghaerang) / [TTF](https://raw.githubusercontent.com/google/fonts/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/kiranghaerang/KirangHaerang-Regular.ttf) | vendor/kiranghaerang/OFL.txt | `d677d28d466989017c520f00a2a7794ea581ea3d9fa9a830fbb44f1015eac72d` |
| Gugi | TAE System & Typefaces Co. | [source](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/gugi) / [TTF](https://raw.githubusercontent.com/google/fonts/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/gugi/Gugi-Regular.ttf) | vendor/gugi/OFL.txt | `c0b1f979979cfc309fb2438fa9464f96173353e0c4842cc7a5919658184ed9d3` |
| SongMyung | JIKJI | [source](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/songmyung) / [TTF](https://raw.githubusercontent.com/google/fonts/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/songmyung/SongMyung-Regular.ttf) | vendor/songmyung/OFL.txt | `7f90ab20250911560212cc5819c7b205f9c6644bb96b65095d89fcae096bbf58` |
| DoHyeon | Woowahan Brothers | [source](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/dohyeon) / [TTF](https://raw.githubusercontent.com/google/fonts/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/dohyeon/DoHyeon-Regular.ttf) | vendor/dohyeon/OFL.txt | `35644be7f28e0a68a447b1f7af351dcde5674b870f24f7b5f43e26d00b4ab653` |

Each vendor directory includes METADATA.pb and SHA256.json for all downloaded bytes. docs/expressive-fonts.png contains only newly rendered font specimens. Original-game glyph comparisons are generated locally under ignored artifacts/font-review; they are not redistributed in Git.

## Commander alpha trial

`tools/trial_commander_font.py` rasterizes the already attributed, unmodified Do Hyeon at 12px for commander Hangul only. The generated local addon includes its complete OFL.txt and a source/designer credit under ko/licenses/dohyeon/. Alpha is retained or thresholded for an identical-metrics binary control. No outline modifications. Source, pinned version and original SHA-256 remain as listed above.

## Seven-pixel UI alpha trial

The existing Do Hyeon binary (same pinned source/hash/license above) is rasterized at 32px, then proportionally resampled to a 6x7px ink box within the original 8x8 UI glyph canvas. Only starcon/tiny Hangul is replaced. No font outlines modified. The generated addon includes OFL.txt and CREDIT.txt under ko/licenses/dohyeon/. This supersedes the local commander trial; default builds remain unchanged.
