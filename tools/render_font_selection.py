"""Render an attributed font specimen; no original game artwork is used."""
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import patcher

if __name__ == '__main__':
    registry = json.loads((ROOT/'translations/fonts.ko.json').read_text(encoding='utf-8'))
    fonts = registry['fonts']
    order = registry['specimen_order']
    canvas = Image.new('RGB', (1100, 155*len(order)+20), (13, 19, 30))
    draw = ImageDraw.Draw(canvas)
    for i, name in enumerate(order):
        y = 16 + i * 155
        draw.text((18, y), name + ' / ' + str(fonts[name]['raster_px']) + ' px native / 3x preview',
                  font=patcher.font('Galmuri11', 24), fill=(121, 197, 246))
        face = ImageFont.truetype(str(ROOT/fonts[name]['file']), fonts[name]['raster_px'])
        for offset, text, color in [(42, '우리는 너희의 응답을 기다린다.', (245, 243, 223)),
                                    (86, '함장, 교신을 계속할까요? 켬 / 끔', (96, 216, 205))]:
            mask = patcher.text_mask(text, face)
            mask = mask.resize((mask.width*3, mask.height*3), Image.Resampling.NEAREST)
            canvas.paste(color, (18, y+offset), mask)
    canvas.save(ROOT/'docs/font-selection.png')
