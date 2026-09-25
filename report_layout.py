"""Compile readable Korean reports for UQM's fixed 40x12, six-pixel cells.

Source translations remain plain Unicode with their original paragraph rows.
Only the packaged report bodies acquire display spacers and page padding.
"""
from pathlib import Path
import re
from PIL import Image, ImageDraw, ImageFont

COLUMNS = 40
ROWS = 12
CELL = 6
LINES_PER_PAGE = 5
BODY_ROWS = ROWS - 1  # Last row belongs to the engine's MORE prompt.
FONT_TARGET = 'ko/fonts/lander.fon/'


def wide(char):
    return ord(char) > 127


def cells(text):
    return sum(2 if wide(c) else 1 for c in text)


def spaced(text):
    return ''.join(c + (' ' if wide(c) else '') for c in text)


def logical_lines(text):
    """Wrap without dropping words; blank source rows remain paragraph breaks."""
    result = []
    for source_line in text.splitlines():
        words = source_line.split()
        if not words:
            result.append('')
            continue
        line = ''
        for word in words:
            if line and cells(line + ' ' + word) > COLUMNS:
                result.append(line)
                line = ''
            if line:
                line += ' '
            for char in word:
                if cells(line + char) > COLUMNS:
                    result.append(line)
                    line = ''
                line += char
        result.append(line)
    return result


def compile_body(text):
    lines = logical_lines(text)
    rows = []
    for start in range(0, len(lines), LINES_PER_PAGE):
        group = lines[start:start + LINES_PER_PAGE]
        rows.append('')  # First baseline is too high for 9px ink; reserve it.
        for line in group:
            rows.extend([spaced(line), ''])
        if start + LINES_PER_PAGE < len(lines):
            rows.extend([''] * (BODY_ROWS - 1 - len(group) * 2))
    return '\n'.join(rows).rstrip('\n')


def compile_table(text, translations):
    """Headers and untranslated records are byte-identical to input text."""
    chunks = re.split(r'(?m)(^#\(([^\r\n)]*)\)[^\r\n]*\r?\n)', text)
    newline = '\r\n' if '\r\n' in text else '\n'
    for i in range(1, len(chunks), 3):
        key, body = chunks[i+1:i+3]
        chunks[i+1] = ''
        if key in translations:
            old = body.rstrip('\r\n')
            chunks[i+2] = compile_body(translations[key]).replace('\n', newline) + body[len(old):]
    return ''.join(chunks)


def font_assets(archive, texts, root):
    """Keep original Latin glyphs and add binary 10x9 ink in two-cell slots."""
    prefix = 'base/fonts/lander.fon/'
    entries = {FONT_TARGET + n.removeprefix(prefix): archive.read(n)
               for n in archive.namelist() if n.startswith(prefix) and n.endswith('.png')}
    face = ImageFont.truetype(str(Path(root)/'vendor/galmuri/Galmuri9.ttf'), 10)
    chars = sorted({c for text in texts for c in text if wide(c)})
    for char in chars:
        box = face.getbbox(char)
        if (box[2]-box[0], box[3]-box[1]) != (10, 9):
            raise ValueError(f'Unexpected report glyph: {char!r}: {box}')
        mask = Image.new('L', (10, 9))
        ImageDraw.Draw(mask).text((-box[0], -box[1]), char, font=face, fill=255)
        mask = mask.point(lambda value: 255 if value >= 128 else 0)
        if not mask.getbbox():
            raise ValueError(f'Empty report glyph: {char!r}')
        # UQM hotspot for a 12px PNG is h-3=9. With ink at y=0 and
        # first content baseline y=12, ink starts at y=3. Row zero is blank.
        glyph = Image.new('RGBA', (10, 12), (255,255,255,0))
        glyph.paste(Image.new('RGBA', mask.size, (255,255,255,255)), (0,0), mask)
        import io
        output = io.BytesIO()
        glyph.save(output, format='PNG')
        entries[FONT_TARGET + f'{ord(char):05x}.png'] = output.getvalue()
    return entries
