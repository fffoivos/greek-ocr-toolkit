"""Indexed original/enhanced native audit panels; no runtime importer."""
import json
from pathlib import Path
import cv2,numpy as np
from .r8_ink02_i2 import ROOT,O,I,FL,dump,sha,clean,own,roi,bbox,crop_mask

def enhance(raw):
    lo,hi=np.percentile(raw,[1,99]);return np.rint(np.clip((raw.astype(float)-lo)/max(hi-lo,1)*255,0,255)).astype(np.uint8)
def bar(width,text):
    out=np.full((30,width,3),255,np.uint8);cv2.putText(out,text[:220],(5,20),cv2.FONT_HERSHEY_SIMPLEX,.43,(0,0,0),1);return out
def label_image(raw,label,zoom=2):
    image=cv2.resize(raw,None,fx=zoom,fy=zoom,interpolation=cv2.INTER_NEAREST)
    if image.ndim==2:image=cv2.cvtColor(image,cv2.COLOR_GRAY2BGR)
    return np.vstack([bar(image.shape[1],label),image])
def stack(images):
    w=max(im.shape[1] for im in images);result=[]
    for im in images:
        p=np.full((im.shape[0],w,3),255,np.uint8);p[:,:im.shape[1]]=im;result.append(p)
    return np.vstack(result)

def run():
    cases=json.loads((O/'OBSERVATION_COMPARISON.json').read_text());pages={};index=[]
    for page in sorted({r['page'] for r in cases}):
        data=json.loads((O/'audit'/(page+'.json')).read_text());row=data['input'];assert sha(row['path'])==row['sha256'];gray=cv2.imread(row['path'],0);gray.flags.writeable=False
        for call in data['calls']:
            records=[r for r in cases if r['originating_call']==call['id']]
            if not records:continue
            # Record metadata from the same one-build offline invocation as its scores.
            factory=own.glyph_atlas;atlas=[]
            def prepare(raw):
                snapshot=factory(raw);atlas.append(dict(exemplars=[dict(bbox=list(e.bbox),line=e.line) for e in snapshot.exemplars],vectors_sha256=__import__('hashlib').sha256(snapshot.vectors.tobytes()).hexdigest(),aspects_sha256=__import__('hashlib').sha256(snapshot.aspects.tobytes()).hexdigest(),vectors_dtype=str(snapshot.vectors.dtype),aspects_dtype=str(snapshot.aspects.dtype)));return snapshot
            own.glyph_atlas=prepare
            try:result=own.analyze(gray,call['pool'],regions=[bbox(r['actual_item']) for r in records],detail=True)
            finally:own.glyph_atlas=factory
            assert result['regions']==call['offline_B5']['regions'];call['offline_atlas']=atlas[0] if atlas else None
            for r in records:r['offline_atlas']=call['offline_atlas']
        dump(O/'audit'/(page+'.json'),data)
        overview=cv2.cvtColor(cv2.resize(gray,None,fx=min(1,900/gray.shape[1]),fy=min(1,900/gray.shape[1])),cv2.COLOR_GRAY2BGR);scale=overview.shape[1]/gray.shape[1]
        for r in cases:
            if r['page']!=page:continue
            n=cases.index(r)+1;q=r['actual_item'];a,b,c,d=r['geometry']['roi'];raw=gray[b:d,a:c];m=crop_mask(raw.shape,q,(a,b));enh=enhance(raw)
            target=cv2.cvtColor(raw,cv2.COLOR_GRAY2BGR);cv2.drawContours(target,cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[0],-1,(0,0,255),1)
            fields=r['fast_region'];b5=r['offline_B5'];clipped=sum(g['clipped'] for g in fields['components']);strong=sum(not g['faint'] and not g['edge_fragment'] for g in fields['components'])
            description=f"{n:03} {page} {r['id']} source={q.get('source_ids')} ROI={a},{b},{c},{d}"
            diagnostic=f"M35 pool={r['pool_index']} bodies={fields['bodies']} normal={fields['normal']} strong={strong} clipped={clipped} run={fields['normal_run']} short={fields['short_ambiguous']} isolated={fields['isolated_normal_ink']} | B5 {b5['ownership']} F{b5['front_votes']}/B{b5['back_votes']}"
            images=[bar(max(900,raw.shape[1]*2),description),bar(max(900,raw.shape[1]*2),diagnostic),label_image(raw,'ORIGINAL native ROI, 2x nearest; original pixels determine findings'),label_image(enh,'ENHANCED 1/99 percentile display only; ordinary orientation'),label_image(enh[:,::-1],'ENHANCED REFLECTED display only; not an automatic source label')]
            review=stack(images);dest=O/'review'/f'{n:03}.png';dest.parent.mkdir(exist_ok=True);cv2.imwrite(str(dest),review)
            x,y,z,w=r['context_roi'];context=gray[y:w,x:z];cm=crop_mask(context.shape,q,(x,y));overlay=cv2.cvtColor(context,cv2.COLOR_GRAY2BGR);cv2.drawContours(overlay,cv2.findContours(cm,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[0],-1,(0,0,255),1)
            components=overlay.copy()
            for g in fields['components']:
                x0,y0,x1,y1=np.rint(np.asarray(g['bbox'])-[x,y,x,y]).astype(int);cv2.rectangle(components,(x0,y0),(x1,y1),(230,100,0) if g['faint'] else (0,160,0),1)
            contextimage=stack([bar(max(900,context.shape[1]),description),label_image(context,'ORIGINAL native surrounding rows, 1x',1),label_image(overlay,'REMOVED mask outline (red); no bbox substituted',1),label_image(cm*255,'ACTUAL crop_mask selected pixels',1),label_image(components,'M35 faint components blue / normal green, eligibility remains empirical',1)])
            contextpath=O/'panels'/f'{n:03}.png';contextpath.parent.mkdir(exist_ok=True);cv2.imwrite(str(contextpath),contextimage)
            witnesses=[]
            if r.get('offline_atlas') and b5.get('matches'):
                chosen=[]
                for orientation in ['direct','reflected']:
                    match=max(b5['matches'],key=lambda m:m[orientation]);ex=r['offline_atlas']['exemplars'][match[orientation+'_id']];parts=[]
                    for box in [match['bbox'],ex['bbox']]:
                        aa,bb,cc,dd=map(int,box);parts.append(label_image(gray[bb:dd,aa:cc],f"{orientation} {'query' if not parts else 'actual scored exemplar'} native 4x",4))
                    pair=stack(parts);path=O/'witnesses'/f'{n:03}.{orientation}.png';path.parent.mkdir(exist_ok=True);cv2.imwrite(str(path),pair);witnesses.append(dict(file=str(path.relative_to(O)),orientation=orientation,match=match,exemplar=ex,qualified_vote=match[orientation]>=.80 and (match['margin']<=-.08 if orientation=='direct' else match['margin']>=.08)))
            r.update(panel_index=n,review_file=str(dest.relative_to(O)),context_file=str(contextpath.relative_to(O)),witness_files=witnesses)
            index.append(dict(index=n,id=r['id'],page=page,review=r['review_file'],context=r['context_file'],witnesses=witnesses,original_roi=r['geometry']['roi'],missing_selected_pixels=r['coverage']['missing_mask_pixels']))
            cv2.polylines(overview,[np.rint(np.asarray(q['polygon'])*scale).astype(np.int32)],True,(0,0,255),1);cv2.putText(overview,str(n),(round(a*scale),round(b*scale)),0,.35,(255,0,0),1)
        path=O/'page_locations'/f'{page}.png';path.parent.mkdir(exist_ok=True);cv2.imwrite(str(path),overview)
    dump(O/'OBSERVATION_COMPARISON.json',cases);dump(O/'PANEL_INDEX.json',index)
    text=['# Native M35 removal panels','','153 indexed records. Review contains original native pixels plus labelled enhanced/reflect display aids; context contains surrounding rows, actual removed mask and component boxes. Page locations and exact call/calibration metadata are linked in JSON. Source adjudication is separate from generation.']
    for r in index:text.append(f"- {r['index']:03} {r['id']} {r['page']}: [native/enhanced](review/{r['index']:03}.png), [context/mask](panels/{r['index']:03}.png), [page location](page_locations/{r['page']}.png)")
    (O/'PANEL_INDEX.md').write_text('\n'.join(text)+'\n');print('panels',len(index))
if __name__=='__main__':run()
