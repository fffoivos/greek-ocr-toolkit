"""Contact sheets (aspect preserved, red frame = crop extent) for viewing the typology crops."""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw
SP = Path(sys.argv[1]); per = 10
rows = [json.loads(l) for l in open(SP / 'chosen.jsonl')]
rows = [r for r in rows if r['set'].startswith('typology')]
H = 56; MAXW = 1150; LAB = 60
(SP / 'sheets').mkdir(exist_ok=True)
for s in range(0, len(rows), per):
    chunk = rows[s:s + per]
    ims = []
    for r in chunk:
        im = Image.open(r['crop_path']).convert('L')
        k = H / im.height
        if im.width * k > MAXW:
            k = MAXW / im.width
        ims.append(im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS))
    sheet = Image.new('RGB', (MAXW + LAB + 10, sum(i.height + 14 for i in ims) + 4), (200, 215, 235))
    d = ImageDraw.Draw(sheet); y = 4
    for j, (r, im) in enumerate(zip(chunk, ims)):
        d.text((4, y + 4), f'#{s + j}', fill=(0, 0, 0))
        sheet.paste(im.convert('RGB'), (LAB, y + 2))
        d.rectangle([LAB - 1, y + 1, LAB + im.width, y + 2 + im.height], outline=(220, 0, 0))
        y += im.height + 14
    sheet.save(SP / 'sheets' / f'sheet_{s // per:02d}.png')
    for j, r in enumerate(chunk):
        print(f'#{s+j} [{r["set"][9:13]}/{r["population"]}] {r["width"]}x{r["height"]} c={r["chars"]} {r["source"]} {r["primary_class"]} v05={r["verdict_05"]} own={r["owner"]} :: {r["text"]!r}')
