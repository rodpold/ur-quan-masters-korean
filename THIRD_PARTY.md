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
| Galmuri9.ttf | https://raw.githubusercontent.com/quiple/galmuri/main/dist/Galmuri9.ttf | 10px (9px ink) | Player choices, commander subtitles, historical larger UI trial, and fixed-cell lander reports |
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

## Distinct binary race-font candidates (2026-09-25)

Fifteen additional independent design families from official Google Fonts, unmodified TTF binaries. All SIL OFL 1.1; retain full bundled copyright/license notices. Upstream designer metadata is listed below; OFL files identify copyright holders. Every source is pinned to commit 23e54b51ddffbc7713c583748e3bd86f62b1fa4a. Used only in binary (alpha 0/255) font specimens; no game installation. Sunflower and Dongle use Bold files, but each is its own design family, not a reused family weight for another race.

| Family | Designer | Official source / download | License | Font SHA-256 |
|---|---|---|---|---|
| BlackHanSans | Zess Type | [source](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/blackhansans) / [TTF](https://raw.githubusercontent.com/google/fonts/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/blackhansans/BlackHanSans-Regular.ttf) | vendor/blackhansans/OFL.txt | `31960809284026681774a8e52dc19ebcad26cf69b0ad9d560f288296fbb52739` |
| Jua | Woowahan Brothers | [source](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/jua) / [TTF](https://raw.githubusercontent.com/google/fonts/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/jua/Jua-Regular.ttf) | vendor/jua/OFL.txt | `769677aef240bfc3b9965f2b50748075bff885e6c6992fc591a3fb268279f898` |
| Sunflower | JIKJISOFT | [source](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/sunflower) / [TTF](https://raw.githubusercontent.com/google/fonts/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/sunflower/Sunflower-Bold.ttf) | vendor/sunflower/OFL.txt | `6b033627817f6619433afe82028013dc45a78ff82406b1dbe5b16e1bbc370e0a` |
| Dokdo | FONTRIX | [source](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/dokdo) / [TTF](https://raw.githubusercontent.com/google/fonts/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/dokdo/Dokdo-Regular.ttf) | vendor/dokdo/OFL.txt | `5b3a3d8d28af31fa9adec3fc5da81a88b52e1ff39ed3930c1db787aa4e79c36d` |
| YeonSung | Woowahan brothers | [source](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/yeonsung) / [TTF](https://raw.githubusercontent.com/google/fonts/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/yeonsung/YeonSung-Regular.ttf) | vendor/yeonsung/OFL.txt | `49ac2a11009f5f58307d377911eb45d210cf4c1d379d9eca38fb4cdad5491ef6` |
| Stylish | AsiaSoft Inc | [source](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/stylish) / [TTF](https://raw.githubusercontent.com/google/fonts/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/stylish/Stylish-Regular.ttf) | vendor/stylish/OFL.txt | `3ea2e4c9d0183fdcc1362039305ef30fa8bb5154f030b303a029059a44a8516c` |
| PoorStory | Yoon Design | [source](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/poorstory) / [TTF](https://raw.githubusercontent.com/google/fonts/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/poorstory/PoorStory-Regular.ttf) | vendor/poorstory/OFL.txt | `831ab87f7b5463f9cd83ac249bf386816f3a478f1d226427c88cac907adb7ee2` |
| HiMelody | YoonDesign Inc | [source](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/himelody) / [TTF](https://raw.githubusercontent.com/google/fonts/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/himelody/HiMelody-Regular.ttf) | vendor/himelody/OFL.txt | `360d2c0a880918aa48328d1d9219f5390788d09a1c9353e12b471de018673ae6` |
| SingleDay | DXKorea Inc | [source](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/singleday) / [TTF](https://raw.githubusercontent.com/google/fonts/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/singleday/SingleDay-Regular.ttf) | vendor/singleday/OFL.txt | `716ff67a4b0675b35c26d60a4bb83173f7d153ab754474ed36c3369593ca1ca8` |
| GamjaFlower | YoonDesign Inc | [source](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/gamjaflower) / [TTF](https://raw.githubusercontent.com/google/fonts/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/gamjaflower/GamjaFlower-Regular.ttf) | vendor/gamjaflower/OFL.txt | `ece32819ed58536355a49a095b0cdfdd3b8ef9081c5ed9ca1cef8f5d999ae1ac` |
| CuteFont | TypoDesign Lab. Inc | [source](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/cutefont) / [TTF](https://raw.githubusercontent.com/google/fonts/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/cutefont/CuteFont-Regular.ttf) | vendor/cutefont/OFL.txt | `c403227fe6288a8c1423ca48e93fd7efc81e3b81053f7d17adcf659bd95fa4c3` |
| GowunBatang | Yanghee Ryu | [source](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/gowunbatang) / [TTF](https://raw.githubusercontent.com/google/fonts/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/gowunbatang/GowunBatang-Regular.ttf) | vendor/gowunbatang/OFL.txt | `466c593e7147412e748af4856d5ad14709b5a860bdf62b9c2546f2c5874e9849` |
| GowunDodum | Yanghee Ryu | [source](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/gowundodum) / [TTF](https://raw.githubusercontent.com/google/fonts/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/gowundodum/GowunDodum-Regular.ttf) | vendor/gowundodum/OFL.txt | `a6e457933227483a11758fd0947bc74422a106d46f0bf057fdaa5af94a30067d` |
| Dongle | Yanghee Ryu | [source](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/dongle) / [TTF](https://raw.githubusercontent.com/google/fonts/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/dongle/Dongle-Bold.ttf) | vendor/dongle/OFL.txt | `944c498c0d1a1832ab36f173b1b3aa5ae77b2a914e00c4d79e05338fae36472d` |
| BlackAndWhitePicture | AsiaSoft Inc. | [source](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/blackandwhitepicture) / [TTF](https://raw.githubusercontent.com/google/fonts/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/blackandwhitepicture/BlackAndWhitePicture-Regular.ttf) | vendor/blackandwhitepicture/OFL.txt | `4d72cd6de1f210b446c86f06b4e13d7641cbcfb1b375c6927341388aa8e08056` |

Local vendor directories also retain METADATA.pb and SHA256.json. No font outlines modified. docs/binary-race-fonts-*.png contain only new font renders, not game graphics. Original-English comparisons are generated under ignored artifacts/binary-font-review/. GowunDodum is retained as an alternate, not assigned in the unique-family proposal.

## Race fonts integrated into local addon

The 24 selected families listed in translations/fonts.ko.json are now rasterized as binary Hangul glyphs by race_fonts.py. Original font binaries are unmodified. The generated addon ships the relevant complete license notices, additional dependency notices and author files plus individual source/designer credits under ko/licenses/. Original English glyphs come from the user installation and remain excluded from Git.

Shared font references inspected in the public source port: https://github.com/intgr/uqm-wasm/blob/main/sc2/src/uqm/comm/spahome/spahome.c , https://github.com/intgr/uqm-wasm/blob/main/sc2/src/uqm/comm/starbas/starbas.c , https://github.com/intgr/uqm-wasm/blob/main/sc2/src/uqm/comm/rebel/rebel.c . These confirm Spathi, Commander and Yehat font sharing respectively.

## Report font and rendering audit

Lander reports use the existing Galmuri9.ttf by Lee Minseo (quiple), OFL-1.1, rasterized at 10px into binary 10x9 ink inside 10x12 PNGs. Display spacing occupies two original cells and alternate rows; TTF outlines are unchanged. Source, SHA-256, and license are listed above and in vendor/galmuri/SHA256.json. Original lander Latin glyphs are read only from the user's game and are not committed.

`tools/check_report_layout.py` adapts the pagination/control-flow of UQM's MakeReport and UniChar_isGraph for an offline audit. This tool is **GPL-2.0-or-later**, an exception to the repository's default MIT license. Original copyright: Paul Reiche, Fred Ford, 1992-2002; Python adaptation: 2026 ur-quan-masters-korean contributors. License: [LICENSES/UQM-GPL.txt](LICENSES/UQM-GPL.txt), SHA-256 `560aff43d87dd0a1c1281e48a72152d854001209f76962b2fbe47cc38b97c958`.

Inspected public source snapshot: [report.c](https://github.com/intgr/uqm-wasm/blob/daadbb540a8c46f09dcdb0080b4212fb33e6cb94/sc2/src/uqm/planets/report.c), [unicode.c](https://github.com/intgr/uqm-wasm/blob/daadbb540a8c46f09dcdb0080b4212fb33e6cb94/sc2/src/libs/strings/unicode.c), [gfxload.c](https://github.com/intgr/uqm-wasm/blob/daadbb540a8c46f09dcdb0080b4212fb33e6cb94/sc2/src/libs/graphics/gfxload.c), and [getstr.c](https://github.com/intgr/uqm-wasm/blob/daadbb540a8c46f09dcdb0080b4212fb33e6cb94/sc2/src/libs/strings/getstr.c). Full C source and game assets are not bundled. The audit excludes timing, input handling, and PC font effects; it does not establish executable equivalence or replace runtime testing.

## 조크-포트-피크 화자 연결 참고

- 출처: [UQM 공개 포트 zoqfotc.c](https://github.com/intgr/uqm-wasm/blob/daadbb540a8c46f09dcdb0080b4212fb33e6cb94/sc2/src/uqm/comm/zoqfot/zoqfotc.c), 고정 커밋 daadbb540a8c46f09dcdb0080b4212fb33e6cb94.
- 원 소스 저작권: Paul Reiche, Fred Ford (1992–2002). GPL-2.0-or-later, [라이선스 사본](licenses/UQM-GPL.txt).
- 용도: 발화 ID와 ZOQ/PIK 콜백의 사실적 대응을 추출해 translations/zoqfotpik-speakers.ko.json에 기록. 원문 파일 SHA-256은 해당 JSON 참조.
- 원본 C 코드·게임 대사·이미지·음성은 이 자료에 복제하지 않는다. 기존 게임 소스의 라이선스는 원 출처를 따른다. 신규 폰트나 폰트 수정은 없다.
- 설치 EXE와 공개 포트의 동일성 및 실제 자막·화자 타이밍은 별도 검토 대상이다.

소개 슬라이드 한글 추가 용도: 기존 Galmuri7/Galmuri9 파일과 라이선스·해시를 재사용한다. 새 외부 폰트는 없으며 Galmuri9의 기존 흑백 래스터를 slides 글꼴에도 배치한다. 원본 영문 슬라이드 글리프는 사용자 설치 패키지에서 빌드 시 복사하며 저장소에 배포하지 않는다. 원본 글리프와 음악·이미지는 변경하지 않는다.

최종 엔딩 슬라이드에도 위 소개와 동일한 Galmuri9 원본 파일·라이선스·해시와 흑백 변환을 재사용한다. 기존 slides 영문 글리프는 사용자 설치본에서만 복사하고 저장소에는 배포하지 않는다.

## 슬라이드·함선 소개 재생 경로 조사

UQM 공개 포트의 [intro.c](https://github.com/intgr/uqm-wasm/blob/daadbb540a8c46f09dcdb0080b4212fb33e6cb94/sc2/src/uqm/intro.c), [fmv.c](https://github.com/intgr/uqm-wasm/blob/daadbb540a8c46f09dcdb0080b4212fb33e6cb94/sc2/src/uqm/fmv.c), [shipyard.c](https://github.com/intgr/uqm-wasm/blob/daadbb540a8c46f09dcdb0080b4212fb33e6cb94/sc2/src/uqm/shipyard.c)를 참고했다. 원 저작권 Paul Reiche / Fred Ford, GPL-2.0-or-later([사본](licenses/UQM-GPL.txt)). 해시는 docs/shipspin-resource-audit.json 참조. 사용 목적은 리소스 이름·FONT 선택 동작·텍스트 버퍼 한도의 사실 확인이다. 원본 코드를 복제·배포하거나 설치 EXE를 수정하지 않았다.

성도 이름 처리 참고: [starmap.c](https://github.com/intgr/uqm-wasm/blob/daadbb540a8c46f09dcdb0080b4212fb33e6cb94/sc2/src/uqm/starmap.c), [planets/pstarmap.c](https://github.com/intgr/uqm-wasm/blob/daadbb540a8c46f09dcdb0080b4212fb33e6cb94/sc2/src/uqm/planets/pstarmap.c). Paul Reiche / Fred Ford, GPL-2.0-or-later([사본](licenses/UQM-GPL.txt)). 파일 해시는 docs/celestial-name-review.json에 기록했다. 이름 연결·UTF-8 검색·버퍼 크기를 확인했으며 원본 코드는 저장소에 포함하지 않는다. 새 폰트나 외부 이미지는 추가하지 않았다.

장치 목록 레이아웃 참고: [planets/devices.c](https://github.com/intgr/uqm-wasm/blob/daadbb540a8c46f09dcdb0080b4212fb33e6cb94/sc2/src/uqm/planets/devices.c), Paul Reiche / Fred Ford (1992–2002), GPL-2.0-or-later([사본](licenses/UQM-GPL.txt)). SHA-256과 용도는 translations/device-labels.ko.json 참조. 원본 코드는 배포하지 않으며 기존 Galmuri7 흑백 tiny 글리프를 재사용한다.

## 원소명 및 착륙정 텍스트 참고

- 원소 표기: [2022 개정 교육과정에 따른 교과용도서 개발을 위한 편수자료 III 기초과학·정보 편](https://www.goe.go.kr/resource/old/BBSMSTR_000000030136/BBS_202304060600195200.pdf), 경기교육청 공개본, 본문 213–214쪽. 원소명 사실 대조에만 사용했으며 문서·표 이미지는 배포하지 않는다. 일반 화학 명칭을 직접 입력했고 재배포 라이선스를 주장하지 않는다.
- 표시 방식: [planets/lander.c](https://github.com/intgr/uqm-wasm/blob/daadbb540a8c46f09dcdb0080b4212fb33e6cb94/sc2/src/uqm/planets/lander.c), Paul Reiche / Fred Ford, GPL-2.0-or-later([사본](licenses/UQM-GPL.txt)). pickupMineralNode와 DrawPlanetSide의 첫 공백 분리/7픽셀 간격을 확인했다. 원본 코드·그림은 배포하지 않는다. 기존 Galmuri7 흑백 폰트를 재사용한다.
