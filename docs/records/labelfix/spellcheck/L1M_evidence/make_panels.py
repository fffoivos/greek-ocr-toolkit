"""Native crop/component witnesses. Colour overlays are annotations, not masks."""
import gzip
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

HERE=Path(__file__).resolve().parent
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'


def load(path):return list(map(json.loads,gzip.open(path,'rt')))


def render(suite='borders'):
    lines=[]; details={};flags=[]
    for sample in ('200','vouli'):
        root=HERE/sample
        if not (root/'receipt.json').exists():continue
        lines.extend(load(root/'lines.jsonl.gz'))
        details.update({r['id']:r for r in load(root/'details.jsonl.gz')})
        flags.extend(load(root/'border_flags.jsonl.gz'))
    byline={r['id']:r for r in lines}
    chosen=[];used=set()
    # Six verdict flips, then six persistent flags. All attribution stays
    # undecidable without ownership maps; no semantic class is invented.
    for category in (('verdict_flip',) if suite=='flips' else ('verdict_flip','persistent_border')):
        candidates=[]
        for f in flags:
            r=byline[f['id']]
            d=details[f['id']]
            original_slot=next(s for s in d['modes']['original']['ENSEMBLE_AB']['slots'] if s['start']==f['start'])
            active='detector_clipped_'+f['edge']
            if active not in original_slot.get('hold_reasons',[]):continue
            flip=r['status']['original']['ENSEMBLE_AB']=='hold' and r['status']['masked']['ENSEMBLE_AB']!='hold'
            if category=='verdict_flip' and flip and not f['persists']:candidates.append(f)
            after_slot=next(s for s in d['modes']['masked']['ENSEMBLE_AB']['slots'] if s['start']==f['start'])
            if category=='persistent_border' and f['persists'] and active in after_slot.get('hold_reasons',[]):candidates.append(f)
        # Wave/edge balance first, then stable slot order.
        for wave in ('round1','round2','mixed'):
            for edge in ('top','bottom'):
                options=[f for f in candidates if byline[f['id']]['wave']==wave and f['edge']==edge and f['id'] not in used]
                taken=0
                for f in options:
                    if f['id'] in used:continue
                    chosen.append(dict(f,category=category));used.add(f['id']);taken+=1
                    if taken>=(2 if suite=='flips' else 1):break
        for f in candidates:
            if sum(c['category']==category for c in chosen)>=(12 if suite=='flips' else 6):break
            if f['id'] not in used:chosen.append(dict(f,category=category));used.add(f['id'])
    chosen=chosen[:12]
    assert len(chosen)==12 and len({f['id'] for f in chosen})==12
    directory='flip_panels' if suite=='flips' else 'panels'
    output=HERE/directory;output.mkdir(exist_ok=True)
    font=ImageFont.truetype(FONT,18);small=ImageFont.truetype(FONT,15)
    for number,f in enumerate(chosen,1):
        r=byline[f['id']];detail=details[r['id']]
        root=Path('/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/v2_masked')/('l1e_sample_r3' if r['sample']=='200' else 'l1e_sample_vouli')
        images=[]
        for p in (Path(r['source']['original_path']),root/r['source']['masked_path']):
            with Image.open(p) as im:images.append(im.convert('RGB'))
        x0,x1=f['window'];mid=(x0+x1)/2
        focus=(max(0,int(mid-55)),0,min(images[0].width,int(mid+75)),images[0].height)
        canvas=Image.new('RGB',(1600,660),'white');draw=ImageDraw.Draw(canvas)
        status=' / '.join(f"{m}: {r['status']['original'][m]} -> {r['status']['masked'][m]}" for m in ('ENSEMBLE_AB','PRESENCE'))
        draw.text((15,8),f"{number:02d}  {r['wave']}  {r['id']}",font=font,fill='black')
        draw.text((15,35),status,font=small,fill='black')
        draw.text((15,60),f"{f['category']}; target start {f['start']} {f['base']}, {f['edge']}; ownership UNDECIDABLE",font=font,fill='black')
        draw.text((15,86),f"foreign audit removed {r['source'].get('foreign_pixels_removed')}; own pixels lost {r['source'].get('own_pixels_lost')}; audit {r['source']['audit_status']}",font=small,fill='black')
        for i,(variant,im) in enumerate(zip(('original','masked'),images)):
            y=115+i*255
            draw.text((15,y),variant.upper()+' native crop (scaled to fit)',font=small,fill='black')
            fitted=im.copy();fitted.thumbnail((1540,80),Image.Resampling.NEAREST)
            canvas.paste(fitted,(20,y+22))
            # Highlight the focus window on the complete line for context.
            scale=fitted.width/im.width
            draw.rectangle((20+focus[0]*scale,y+22,20+focus[2]*scale,y+22+fitted.height),outline=(230,100,0),width=2)
            zoom=im.crop(focus);factor=min(6,680/max(1,zoom.width),125/max(1,zoom.height))
            zoom=zoom.resize((int(zoom.width*factor),int(zoom.height*factor)),Image.Resampling.NEAREST)
            canvas.paste(zoom,(20,y+112))
            labels=np.load(HERE/r['sample']/'pixels'/f"{r['id']}.npz")[variant+'_labels']
            overlay_array=np.array(im.crop(focus))
            for s in detail['detector'][variant]['slots']:
                box=s.get('bbox')
                if not box or not s.get('component_ids') or box[2]<=focus[0] or box[0]>=focus[2]:continue
                # Exact native labels within the letter partition, rather than
                # colouring the entire fused connected component.
                mask=np.isin(labels[:,focus[0]:focus[2]],s['component_ids'])
                yy,xx=np.indices(mask.shape)
                mask &= (xx+focus[0]>=box[0]) & (xx+focus[0]<box[2]) & (yy>=box[1]) & (yy<box[3])
                tint=np.array((200,0,160) if s['start']==f['start'] else (0,120,190))
                overlay_array[mask]=(.50*overlay_array[mask]+.50*tint).astype(np.uint8)
            overlay=Image.fromarray(overlay_array);od=ImageDraw.Draw(overlay)
            for s in detail['detector'][variant]['slots']:
                box=s.get('bbox')
                if not box or box[2]<=focus[0] or box[0]>=focus[2]:continue
                colour=(200,0,160) if s['start']==f['start'] else (0,120,190)
                od.rectangle((box[0]-focus[0],box[1],box[2]-focus[0]-1,box[3]-1),outline=colour,width=1)
            yedge=0 if f['edge']=='top' else im.height-1
            od.line((max(0,x0-focus[0]),yedge,min(overlay.width-1,x1-focus[0]-1),yedge),fill=(230,0,0),width=1)
            overlay=overlay.resize(zoom.size,Image.Resampling.NEAREST)
            canvas.paste(overlay,(800,y+112))
            draw.text((800,y+93),'Detector letter regions: blue; target magenta; clipping window red',font=small,fill='black')
        draw.text((15,635),'Nearest-neighbour zoom; native label IDs, full masks and border pixel coordinates are preserved in evidence.',font=small,fill='black')
        canvas.save(output/f'{number:02d}.png')
        f.update(panel=number,path=f'{directory}/{number:02d}.png',focus=list(focus),id=r['id'],wave=r['wave'])
    (HERE/('flip_visual_selection.json' if suite=='flips' else 'visual_selection.json')).write_text(json.dumps(chosen,ensure_ascii=False,indent=2)+'\n')
    for group in range(4):
        sheet=Image.new('RGB',(1600,1980),'white')
        for row in range(3):
            n=group*3+row+1
            if n<=len(chosen):
                with Image.open(output/f'{n:02d}.png') as panel:sheet.paste(panel,(0,row*660))
        sheet.save(output/f'sheet_{group+1}.png')
    print('Rendered',len(chosen),suite,'composite panels')


if __name__=='__main__':render()
