"""Eight native label spot checks per source; independent blind pack unchanged."""
from f2lib import *
from PIL import ImageFont,ImageDraw
import textwrap
def main():
 font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',24)
 for folder in (BASE/'label_cards').iterdir():
  if not folder.is_dir():continue
  cards=rows(folder/'cards.jsonl')
  if not cards:continue
  selected=sorted(cards,key=lambda r:-len(r['text']))[:6]+sorted(cards,key=lambda r:len(r['text']))[:2]
  for j in range(2):
   canvas=Image.new('RGB',(1800,4*260),'white');d=ImageDraw.Draw(canvas)
   for i,r in enumerate(selected[j*4:(j+1)*4]):
    with Image.open(folder/r['crop']) as im:
     im=im.convert('RGB');im.thumbnail((1760,140));canvas.paste(im,(20,i*260+5))
    text=r['card']+' '+r['text'];lines=textwrap.wrap(text,125)
    for k,line in enumerate(lines[:3]):d.text((20,i*260+155+30*k),line,font=font,fill='black')
   dest=BASE/'bulk/local_review'/(folder.name+f'-{j+1}.jpg');dest.parent.mkdir(exist_ok=True);canvas.save(dest,quality=90)
  write(BASE/'receipts/local-review-selection'/(folder.name+'.json'),dict(cards=[r['card'] for r in selected],selection='six longest proposed cards and two shortest; local unblinded diagnostic only; not independent adjudication',label_card_manifest_sha256=sha(folder/'cards.jsonl')))
if __name__=='__main__':main()
