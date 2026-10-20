"""N1-specific numbered decision boxes, using saved geometry only."""
from PIL import Image, ImageDraw, ImageFont
COLORS={'decided-changed':'#b83228','decided-unchanged':'#177944','unsure':'#946400'}


def detection_image(image, slots, *, opening_quotes=None, scale=2):
    if not isinstance(image,Image.Image):
        with Image.open(image) as im: image=im.copy()
    # Keep native pixels and add a number lane so labels cannot cover the ink.
    out=Image.new('RGB',(image.width*scale,image.height*scale+30),'white')
    base=image.convert('L').convert('RGB') if scale==1 else image.convert('RGB')
    out.paste(base.resize((image.width*scale,image.height*scale),Image.Resampling.NEAREST))
    draw=ImageDraw.Draw(out)
    try: font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',12 if scale==1 else 18)
    except OSError: font=None
    lane_right=[-1,-1]
    for s in slots:
        color=COLORS[s['style']]
        for r in s.get('evidence',{}).get('attached',[]):
            x0,y0,x1,y1=[round(v*scale) for v in r['bbox']]
            x0=max(0,min(out.width-1,x0));x1=max(x0,min(out.width-1,x1))
            y0=max(0,y0);y1=min(image.height*scale-1,y1)
            if s['style']=='unsure':
                for x in range(x0,x1+1,10):
                    draw.line((x,y0,min(x+5,x1),y0),fill=color,width=2)
                    draw.line((x,y1,min(x+5,x1),y1),fill=color,width=2)
                for y in range(y0,y1+1,10):
                    draw.line((x0,y,x0,min(y+5,y1)),fill=color,width=2)
                    draw.line((x1,y,x1,min(y+5,y1)),fill=color,width=2)
            else: draw.rectangle((x0,y0,x1,y1),outline=color,width=2 if s['style']=='decided-unchanged' else 3)
        if s.get('locator_span') is not None:
            x=max(0,min(out.width-25,round(s['locator_span'][0]*scale)))
            lane=0
            if scale==1 and x<lane_right[0]+2:lane=1
            label=str(s['number'])
            draw.text((x,image.height*scale+(1+14*lane if scale==1 else 3)),label,fill=color,font=font)
            lane_right[lane]=x+draw.textlength(label,font=font)
    return out
