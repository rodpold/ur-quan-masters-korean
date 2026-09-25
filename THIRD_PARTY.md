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
