# Project conventions

- Do not modify the game executable. Keep saves, game assets and generated packages out of Git.
- Whenever adding or replacing third-party fonts/assets, update THIRD_PARTY.md in the same change:
  author, official source/download URL, license and local license file, hash, usage and modifications.
- Read translations/GLOSSARY.md and glossary.ko.json before translating proper nouns.
  Register new names separately; distinguish proposed, in_use, approved and preserve.
  Never label a proposal user-approved without evidence. Preserve dynamic player/ship names.
- Run python tools/check_glossary.py for terminology changes. This checks only explicit UI bindings;
  do not claim it verifies all dialogue terminology.
- Use native pixel-font raster sizes and verify glyph coverage. Fixed 8px rows cannot fit 9px ink.

- Keep translations/fonts.ko.json and FONTS.md aligned with glossary IDs and actual font assignments. Distinguish proposed fonts from applied trials; update attribution for new fonts.

- User decision (2026-09-25): no semitransparent Korean font glyphs, including small UI and dialogue. Use binary alpha (0/255). Retained AA tools/specimens are historical experiments, not approved deployment candidates.

- Full localization goal: before each dialogue batch, read translations/personas.ko.json and the relevant source conversation/context. Preserve state/speaker variants and keep player responses separate. Enforce translations/glossary.lock.json; add new terms explicitly without rewriting locked names. Never mark untranslated or unreviewed records complete.
