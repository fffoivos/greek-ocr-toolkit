"""Build reproducible native crop/label sheets for sampled human inspection."""
import json
from pathlib import Path
import random
import sys
sys.dont_write_bytecode=True
from PIL import Image, ImageDraw, ImageFont
import harvest as h


def main():
    lines=[json.loads(x) for x in (h.OUT/'lines.jsonl').read_text().splitlines()]
    if (h.OUT/'qa/source_line_rejections.json').exists():
        lines.extend(r['record'] for r in h.load('qa/source_line_rejections.json')['rejections'])
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',25)
    small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',21)
    samples=[]
    for key in sorted({r['book_key'] for r in lines}):
        group=sorted([r for r in lines if r['book_key']==key],key=lambda r:r['line_id'])
        by_sim=sorted(group,key=lambda r:(r['alignment']['alignment_similarity'],r['line_id']))
        candidates=[('lowest_similarity',by_sim[0]),('median_similarity',by_sim[len(by_sim)//2]),
            ('longest_label',max(group,key=lambda r:len(r['label']))),
            ('seeded_random',random.Random('T7b-native-review:'+key).choice(group))]
        selected=[];seen=set()
        for reason,row in candidates:
            if row['line_id'] not in seen:selected.append((reason,row));seen.add(row['line_id'])
        width=max(1600,max(r['crop_size'][0] for _,r in selected)+40)
        height=sum(r['crop_size'][1]+150 for _,r in selected)+20
        sheet=Image.new('RGB',(width,height),'#ffffff');draw=ImageDraw.Draw(sheet);y=10
        for reason,r in selected:
            draw.text((20,y),f"{r['line_id']} | {reason} | similarity {r['alignment']['alignment_similarity']:.4f}",font=small,fill='#555555')
            y+=35
            with Image.open(h.ROOT/r['crop_path']) as crop:sheet.paste(crop,(20,y))
            y+=r['crop_size'][1]+10
            draw.text((20,y),r['human_label_literal'],font=font,fill='#111111')
            y+=105
            samples.append(dict(line_id=r['line_id'],book_key=key,selection=reason,crop_path=r['crop_path'],
                crop_sha256=r['crop_sha256'],label_literal=r['human_label_literal'],
                similarity=r['alignment']['alignment_similarity']))
        sheet_path=h.OUT/'qa'/('crop-sheet-'+key+'.png');sheet_path.parent.mkdir(exist_ok=True)
        sheet.save(sheet_path)
        for sample in samples:
            if sample['book_key']==key:sample.update(sheet=h.rel(sheet_path),sheet_sha256=h.sha(sheet_path))
    h.save('qa/crop_review_samples.json',dict(scope='Four deterministic samples per book where distinct: lowest and median alignment similarity, longest label, seeded random. Native crop pixels are pasted without resampling; human label is printed below. This is a sample, not exhaustive label verification.',samples=samples))
    print(f"Built {len(samples)} review pairs across five books")


if __name__=='__main__':main()
