import json,sys
from PIL import Image, ImageDraw, ImageFont
d=json.load(open(sys.argv[1])); out=sys.argv[2]
W=1500
try: font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf',26)
except: font=ImageFont.load_default()
def fit(im,maxw):
    if im.width>maxw:
        im=im.resize((maxw,int(im.height*maxw/im.width)),Image.LANCZOS)
    return im
for g in range(0,len(d),3):
    parts=[]
    for x in d[g:g+3]:
        z=Image.open(x['img']).convert('RGB'); l=Image.open(x['line_img']).convert('RGB')
        z=fit(z,W); l=fit(l,W)
        hdr=Image.new('RGB',(W,40),'yellow'); dr=ImageDraw.Draw(hdr)
        t=x['id']+'   A='+x['A']+'   B='+x['B']+('   C='+x['C'] if 'C' in x else '')
        dr.text((5,5),t,fill='black',font=font)
        parts+= [hdr,z,Image.new('RGB',(W,8),'red'),l,Image.new('RGB',(W,20),'blue')]
    H=sum(p.height for p in parts); c=Image.new('RGB',(W,H),'white'); y=0
    for p in parts: c.paste(p,(0,y)); y+=p.height
    c.save(f'{out}/g{g//3:03d}.png')
print('ok')
