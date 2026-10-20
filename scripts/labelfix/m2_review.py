"""Render native-pixel evidence panels for M2's deterministic visual queue."""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont
from scripts.labelfix.m2_run import OUT, rows, sha


def main():
    queue = rows(OUT/'M2_spotcheck_queue.jsonl')
    dest = OUT/'M2_visual'
    dest.mkdir(exist_ok=True)
    font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 16)
    panels = []
    manifest = []
    for r in queue:
        with Image.open(r['crop']) as source:
            original = source.convert('RGB')
        lo = max(0, math.floor(r['span'][0])-18)
        hi = min(original.width, math.ceil(r['span'][1])+18)
        crop = original.crop((lo, 0, hi, original.height))
        crop.save(dest/f"word_{r['review_id']:02d}_native.png")
        enlarged = crop.resize((crop.width*3, crop.height*3), Image.Resampling.NEAREST)
        # No smoothing, rethresholding or denoising in the evidence panel.
        panel = Image.new('RGB', (max(1200,enlarged.width+20), enlarged.height+90), 'white')
        d = ImageDraw.Draw(panel)
        d.text((10,8), f"{r['review_id']:02d} {r['id']} | {r['mode']} | 3x nearest native pixels", font=font,fill='black')
        d.text((10,30), f"Google: {r['google_word']}  ->  proposal: {r['proposed_word']}", font=font,fill='black')
        panel.paste(enlarged,(10,65))
        panels.append(panel)
        manifest.append(dict(review_id=r['review_id'], crop=r['crop'], crop_sha256=sha(r['crop']),
            native_window=[lo,0,hi,original.height], native_png=f"word_{r['review_id']:02d}_native.png"))
    for i in range(0,len(panels),5):
        group=panels[i:i+5]
        sheet=Image.new('RGB',(max(p.width for p in group),sum(p.height+8 for p in group)),'#c8c8c8')
        y=0
        for panel in group:
            sheet.paste(panel,(0,y));y+=panel.height+8
        sheet.save(dest/f'review_{i//5+1}.png')
    import json
    (dest/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':
    main()
