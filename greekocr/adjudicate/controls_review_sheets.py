"""Private CQ1 control contact sheets, with expected forms beside enlarged pixels."""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from ._files import dump, hashes

__all__ = ['controls_review_sheets']


def controls_review_sheets(controls: list[dict], output: str | Path, *, per_sheet: int = 12, font_path: str | Path | None = None) -> dict:
    """Emit ≤12 controls per PNG, word zoom + optional letter zoom + expected form.

    Records require id, word_image, expected_form; letter_image/expected_tuple
    are optional. Output is private, outside every blind reader folder. Index
    stores the full text even when a long expected form wraps on the sheet.
    """
    if type(per_sheet) is not int or not 1 <= per_sheet <= 12 or not controls:
        raise ValueError('nonempty controls and 1..12 per sheet required')
    if len({c['id'] for c in controls}) != len(controls):
        raise ValueError('duplicate control identity')
    font = ImageFont.truetype(str(font_path or '/System/Library/Fonts/Supplemental/Arial.ttf'), 22)
    root = Path(output)
    root.mkdir(parents=True, exist_ok=False)
    index = []
    for offset in range(0,len(controls),per_sheet):
        group = controls[offset:offset+per_sheet]
        canvas = Image.new('RGB',(1600,320*((len(group)+1)//2)), 'white')
        draw = ImageDraw.Draw(canvas)
        for i,c in enumerate(group):
            x, y = (i%2)*800, (i//2)*320
            draw.rectangle((x,y,x+799,y+319),outline='#aaaaaa')
            draw.text((x+12,y+8),str(c['id']),font=font,fill='black')
            for field,left,width in [('word_image',12,580),('letter_image',610,178)]:
                if not c.get(field):
                    continue
                with Image.open(c[field]) as opened:
                    image = opened.convert('RGB')
                scale = min(3 if field=='word_image' else 8, width/image.width, 180/image.height)
                image = image.resize((max(1,round(image.width*scale)),max(1,round(image.height*scale))),Image.Resampling.NEAREST)
                canvas.paste(image,(x+left,y+42))
            text = 'Expected: '+c['expected_form']
            # Keep glyphs within a cell; full unabridged form also lives in index.
            lines, current = [], ''
            for char in text:
                if draw.textlength(current+char,font=font)>770:
                    lines.append(current); current=''
                current += char
            lines.append(current)
            if len(lines)>2:
                raise ValueError('expected form exceeds two contact-sheet lines')
            for j,line in enumerate(lines):
                draw.text((x+12,y+230+j*27),line,font=font,fill='black')
            if 'expected_tuple' in c:
                draw.text((x+12,y+290),str(c['expected_tuple']),font=font,fill='black')
            index.append(dict(id=c['id'], sheet=f'controls_{offset//per_sheet:03d}.png',
                              cell=i, expected_form=c['expected_form'], expected_tuple=c.get('expected_tuple')))
        canvas.save(root/f'controls_{offset//per_sheet:03d}.png')
    dump(root/'index.json',index)
    return dict(controls=len(controls), sheets=(len(controls)+per_sheet-1)//per_sheet, files=hashes(root))
