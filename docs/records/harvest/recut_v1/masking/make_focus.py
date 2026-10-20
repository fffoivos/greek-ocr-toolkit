"""Five larger native contexts for the inspected IA component witnesses."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).resolve().parent


def main():
    records=[json.loads(s) for s in (OUT/'dev/records.jsonl').read_text().splitlines()]
    font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',12)
    for card,box in [('c001',(350,0,500,65)),('c023',(0,0,95,62)),('c040',(180,0,290,54)),
                     ('c019',(155,0,260,43)),('c015',(0,0,120,55))]:
        r=next(r for r in records if r['stratum']=='ia_greek_latin' and r['dev']['card_id']==card)
        images=[Image.open(OUT/r[a+'_path']).convert('RGB').crop(box) for a in ('original','masked')]
        w,h=images[0].size;sheet=Image.new('RGB',(max(1000,w*6+40),h*3+55),'#e3e3e3')
        ImageDraw.Draw(sheet).text((5,5),card+' original / masked: '+r['google_text'],fill='black',font=font)
        sheet.paste(images[0].resize((w*3,h*3)),(10,40))
        sheet.paste(images[1].resize((w*3,h*3)),(w*3+30,40))
        sheet.save(OUT/'dev/witnesses'/f'focus_ia_{card}.png')

if __name__=='__main__':main()
