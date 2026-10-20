"""Offline S6 evaluation: immutable legacy slots plus explicit character/zone truth.

Only read_ink sees pixels, recogniser text and cached alignment. Print/owner
truth is used below for scoring, never to assign runtime regions or marks.
"""
import os
for k in ('VECLIB_MAXIMUM_THREADS','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS'):os.environ[k]='1'
import json,time,hashlib,gzip
from pathlib import Path
from collections import Counter
import numpy as np
from PIL import Image
from greekocr.labelfix import ink as I,markshape as M
from greekocr.labelfix.reading import read_ink
from greekocr.labelfix.validate import load_three_way
from greekocr.labelfix.sheet import load_alignments,crop_key
from greekocr.labelfix.linemetric import mark_set,score_slots,pooled,printed_words,summary,KINDS
from greekocr.labelfix.candidates import pair_tokens
from greekocr.labelfix.text import clusters,nfd,tokenize
from scripts.labelfix.s5_validate import read,write,metric
R=Path(__file__).resolve().parents[2];O=R/'docs/labelfix/spellcheck'


def detected(rs):
    if not rs:return []
    ev=rs.get('evidence',{});parts='+'.join(rs.get('parts',[]))
    ds=mark_set(parts)
    if ev.get('clipped_bottom'):ds={x for x in ds if x[0]!='subscript'}
    if rs.get('unnamed'):ds.add(('accent','unclassified'))
    if rs.get('apostrophe'):ds.add(('apostrophe','apostrophe'))
    return sorted(ds)


def zones(ms):
    if ms is None:return None
    return sorted({'below' if k=='subscript' else 'apostrophe' if k=='apostrophe' else 'above' for k,v in ms})


def physical(rs):
    if not rs:return []
    ev=rs.get('evidence',{})
    return sorted(k for k,v in [('above',ev.get('above')),('below',ev.get('below')),('apostrophe',rs.get('apostrophe'))] if v)


def char_truth(line,truth,*,reasons=None):
    out={};pw=printed_words(line,truth)
    for g,m in pair_tokens(line['google'],line['model']):
        if m is None:continue
        mc=clusters(m.core);pc=clusters(pw[g.index]) if pw.get(g.index) is not None else []
        if len(mc)!=len(pc) or any(a.base!=b.base for a,b in zip(mc,pc)):continue
        key=f"{line['line_id']}|{g.index}"
        if key in truth:
            pt=tokenize(nfd(truth[key]['printed'] or ''));trail=pt[0].trail if len(pt)==1 else ''
        else:
            ht=next((h for gg,h in pair_tokens(line['google'],line['human']) if gg.index==g.index),None)
            trail=ht.trail if ht else ''
        from greekocr.labelfix.markshape import mark_class
        for j,(a,b) in enumerate(zip(mc,pc)):
            if not a.base.isalpha():continue
            cls=mark_class(b.marks)
            if cls is None:
                start=m.core_start+a.start
                out[start]=None
                if reasons is not None:
                    reasons[start]=dict(reason='unsupported_printed_marks',printed=b.base+b.marks,
                        provenance='print_adjudication' if key in truth else 'agreement_proxy')
                continue
            ms=mark_set(cls)
            if j==len(mc)-1 and any(c in trail for c in "'’ʼ᾽"):ms.add(('apostrophe','apostrophe'))
            out[m.core_start+a.start]=sorted(ms)
    return out


def presence(rows,key,zone=None):
    c=Counter()
    for s in rows:
        if s['truth_zones'] is None:c['unknown_slots']+=1;continue
        c['known_slots']+=1
        t=set(s['truth_zones']);d=set(s['presence'][key])
        if zone:t&={zone};d&={zone}
        c['tp']+=len(t&d);c['fp']+=len(d-t);c['fn']+=len(t-d)
    return summary(c)


def aggregate(rows):
    held=[l for l in rows if not l['dev']];dev=[l for l in rows if l['dev']]
    result={'heldout_lines':len(held),'dev_lines':len(dev)}
    classes=sorted(M.load_model(R/'docs/labelfix/markshape_model_S4.json').classes)
    def atomic(ms):
        if ms is None:return None
        out=[]
        for kind,value in ms:
            if kind=='compound':out.extend(('accent' if p in ('acute','grave','circumflex') else 'breathing',p) for p in value.split('+'))
            else:out.append((kind,value))
        return out
    for split,ls in [('heldout',held),('dev',dev)]:
        result[split]={k:metric(ls,k) for k in ('S4','S5','detected')}
        result[split]['atomic']={k:pooled([score_slots([dict(s,truth=atomic(s['truth']),detected=atomic(s[k]),unknown_kinds=[]) for s in l['slots']]) for l in ls]) for k in ('S4','S5','detected')}
        chars=[s for l in ls for s in l['character_checks']]
        groups={'all':chars,'fused':[s for s in chars if s['fused']],
                'clean':[s for s in chars if not s['fused']],
                'merged_accent':[s for s in chars if s['merged_accent']],
                'breathing':[s for s in chars if s['truth'] and any(k=='breathing' for k,v in s['truth'])],
                'compound':[s for s in chars if s['truth'] and any(k=='compound' for k,v in s['truth'])]}
        result[split]['presence']={g:dict(n=len(ss),scores={k:presence(ss,k,'above' if g in ('merged_accent','breathing','compound') else None) for k in ('S4','S5','S6')}) for g,ss in groups.items()}
        result[split]['below_meanline']={k:sum(s['below_meanline'][k] for s in chars) for k in ('S4','S5','S6')}
        result[split]['below_font_meanline']={k:sum(s['below_font_meanline'][k] for s in chars) for k in ('S4','S5','S6')}
        result[split]['capital_side_boxes']={k:sum(s['capital_side_boxes'][k] for s in chars) for k in ('S4','S5','S6')}
        result[split]['fused_components']=sum(len({tuple(s['component_ids']) for s in l['character_checks'] if s['fused']}) for l in ls)
        result[split]['per_class']={}
        known=[s for l in ls for s in l['slots'] if s['truth'] is not None]
        for cls in classes:
            target=mark_set(cls);support=sum(set(map(tuple,s['truth']))==target for s in known)
            dd={}
            for k in ('S4','S5','detected'):
                tp=sum(set(map(tuple,s['truth']))==target and set(map(tuple,s[k]))==target for s in known)
                pred=sum(set(map(tuple,s[k]))==target for s in known)
                dd[k]=dict(support=support,tp=tp,predicted=pred,precision=tp/pred if pred else None,recall=tp/support if support else None)
            result[split]['per_class'][cls]=dd
        result[split]['per_book']={doc:{k:metric([l for l in ls if l['doc']==doc],k) for k in ('S4','S5','detected')} for doc in sorted({l['doc'] for l in ls})}
        asc=[s for l in ls for s in l['slots'] if s['truth']==[] and (s['base'] in 'δβλθφξζ' or s['base'].isupper())]
        result[split]['ascender']=dict(n=len(asc),counts={k:sum(bool(s.get(k+'_evidence',s['evidence']).get('above')) for s in asc) for k in ('S4','S5','S6')})
    return result


def main():
    raise RuntimeError('Historical validator is pinned to its saved artifacts; SF1 runtime has a new pixel/schema contract. Use sf1_rescore for saved-evidence truth/policy comparisons, or copy this validator to an explicitly versioned output workflow.')
    # A cache miss must fail closed, never invoke recognition or the network.
    import socket
    from greekocr.labelfix.ctc_align import Recognizer
    def forbidden(*args,**kwargs):raise RuntimeError('S6 is offline and cached-alignment-only')
    Recognizer.__init__=forbidden
    Recognizer.align_batch=forbidden
    socket.socket.connect=forbidden
    start=time.monotonic();s4={l['line_id']:l for l in read(O/'S4_lines.jsonl.gz')};s5={l['line_id']:l for l in read(O/'S5_lines.jsonl.gz')}
    als=load_alignments(R/'.cache/labelfix/align_s0.jsonl');model=M.load_model(R/'docs/labelfix/markshape_model_S4.json')
    truth=json.loads((O/'print_truth_s0.json').read_text());rows=[]
    for n,l in enumerate(load_three_way(0)):
        b4=s4[l['line_id']];b5=s5[l['line_id']]
        with Image.open(l['crop']) as im:ci=I.analyse(im)
        reading=read_ink(ci,l['model'],als[crop_key(l['crop'])],model,filtered=False)
        assert len(reading.slots)==sum(c.base.isalpha() for c in clusters(nfd(l['model'])))
        assert all(s['component'] is not None for s in reading.slots)
        original={c.index:c for c in ci.components}
        slot_of={tuple(s['bbox']):s['slot'] for s in b4['slots']}
        serial=[]
        for rs in reading.slots:
            c=rs['component'];d={k:v for k,v in rs.items() if k not in ('component','evidence','naming')}
            d.update(bbox=[c.x0,c.y0,c.x1,c.y1],evidence=rs['evidence'].to_record())
            d['component_slots']=[slot_of.get(tuple(getattr(original[i],v) for v in ('x0','y0','x1','y1'))) for i in rs['component_ids']]
            d['component_slot']=next((x for x in d['component_slots'] if x is not None),None)
            serial.append(d)
        slots=[]
        for a,b in zip(b4['slots'],b5['slots']):
            assert a['slot']==b['slot'] and a['truth']==b['truth'] and a['bbox']==b['bbox']
            ss=[s for s in serial if s['component_slot']==a['slot']]
            ds=sorted({tuple(x) for s in ss for x in detected(s)})
            ev=dict(a['evidence'],above=[],below=[],diagnostics=[],apostrophes=[])
            for field in ('above','below','diagnostics'):
                ev[field]=list({tuple(q['bbox']):q for s in ss for q in s['evidence'][field]}.values())
            if ss:ev.update({k:v for k,v in ss[0]['evidence'].items() if k not in ('above','below','diagnostics')})
            slots.append(dict(a,S4=a['detected'],S5=b['detected'],S4_evidence=a['evidence'],S5_evidence=b['evidence'],
                              detected=ds,evidence=ev,above=len(ev['above']),below=len(ev['below']),unknown_kinds=[],
                              unnamed=[i for s in ss for i in s['unnamed']],recogniser_children=[s['start'] for s in ss]))
        truth_reasons={};ct=char_truth(l,truth,reasons=truth_reasons);cs=[]
        maps={k:{s['start']:s for s in bl['recogniser_slots']} for k,bl in [('S4',b4),('S5',b5)]};maps['S6']={s['start']:s for s in serial}
        for s in serial:
            ms=ct.get(s['start']);top,baseline=ci.band(sum(s['region_bounds'])/2)
            # An immutable source CC spans body and a substantial upper lobe.
            merged=False
            for i in s['component_ids']:
                c=original[i];a,b=s['region_bounds']
                if c.y0<top-.15*ci.xh and c.y1>top+.6*ci.xh:
                    upper=ci.labels[max(0,c.y0):max(0,int(np.floor(top))),max(c.x0,a):min(c.x1,b)]==i
                    merged |= upper.sum()>=max(3,.012*ci.xh*ci.xh)
            cc=dict(start=s['start'],base=s['base'],truth=ms,truth_zones=zones(ms),truth_reason=truth_reasons.get(s['start']),
                    component_ids=s['component_ids'],component_slots=s['component_slots'],fused=s['fused'],
                    merged_accent=bool(merged and s['base'].lower() in 'αεηιουωρ'),
                    presence={},below_meanline={},below_font_meanline={},capital_side_boxes={})
            for k in maps:
                rs=maps[k].get(s['start']);cc['presence'][k]=physical(rs)
                ev=rs.get('evidence',{}) if rs else {};above=ev.get('above',[])
                # Side marks lie outside the capital body and use the S5 side
                # zone; report them separately, never call them body intrusions.
                cc['below_meanline'][k]=sum(b['source']!='preposed' and b['bbox'][3]>ev.get('meanline',top) for b in above)
                cc['below_font_meanline'][k]=sum(b['source']!='preposed' and b['bbox'][3]>top for b in above)
                cc['capital_side_boxes'][k]=sum(b['source']=='preposed' and b['bbox'][3]>top for b in above)
            cs.append(cc)
        rows.append(dict(line_id=l['line_id'],doc=l['doc'],dev=b4['dev'],crop=l['crop'],slots=slots,
                         recogniser_text=l['model'],reading=reading.text,S4_reading=b4['reading'],S5_reading=b5['reading'],
                         reading_flags=reading.unnamed,opening_quotes=reading.opening_quotes,
                         recogniser_slots=serial,character_checks=cs,font_fit=ci.font_fit,font_width=ci.font_width))
        if n%100==0:print('evaluated',n,round(time.monotonic()-start,1),flush=True)
    write(O/'S6_lines.jsonl.gz',rows)
    result=aggregate(rows)
    for label in ('S4','S5'):
        for split,key in [('heldout','after'),('dev','dev_after')]:
            frozen=json.loads((O/f'{label}_metrics.json').read_text())[key]
            for kind in ('total',)+KINDS:
                a=result[split][label]['total'] if kind=='total' else result[split][label]['by_kind'][kind]
                b=frozen['total'] if kind=='total' else frozen['by_kind'][kind]
                assert all(a.get(k,0)==b.get(k,0) for k in ('tp','fp','fn','known_slots','unknown_slots')),(label,split,kind)
    cap=[];by={l['line_id']:l for l in rows}
    for old in read(O/'S5_capital_truth.jsonl'):
        l=by[old['line_id']];s=next(s for s in l['slots'] if s['slot']==old['slot'])
        rs=next((r for r in l['recogniser_slots'] if r['component_slot']==s['slot']),None)
        e=s['S4_evidence'];box=s['bbox']
        cap.append(dict(old,S4_pixel=box[3]-box[1]>=1.25*e['xh'] and box[1]<e['meanline']-.2*e['xh'],
                        S6=rs['case_class']=='capital' if rs else False,S6_pixel=rs['pixel_class']=='capital' if rs else False))
    write(O/'S6_capital_truth.jsonl',cap)
    def binary(ss,key):
        return summary(Counter(tp=sum(s[key] and s['truth'] for s in ss),fp=sum(s[key] and not s['truth'] for s in ss),fn=sum(not s[key] and s['truth'] for s in ss),n=len(ss)))
    result['capitals']={k:binary(cap,k) for k in ('before','S4_pixel','after','pixel','S6','S6_pixel')}
    disagreement=[s for s in cap if s['case_disagreement']]
    result['capitals_disagreement']={k:binary(disagreement,k) for k in ('before','S4_pixel','after','pixel','S6','S6_pixel')}
    result['regressions']={}
    for label in ('S4','S5'):
        losses=[]
        for l in rows:
            for s in l['slots']:
                if s['truth'] is None:continue
                t,a,b=[set(map(tuple,x)) for x in (s['truth'],s['detected'],s[label])]
                if (t&b)-a or (a-t)-(b-t):losses.append(dict(line_id=l['line_id'],slot=s['slot'],truth=s['truth'],before=s[label],after=s['detected'],before_evidence=s[label+'_evidence'],after_evidence=s['evidence'],lost=sorted((t&b)-a),new_false=sorted((a-t)-(b-t))))
        write(O/f'S6_regressions_{label}.jsonl',losses);result['regressions'][label]=len(losses)
    result.update(elapsed_seconds=time.monotonic()-start,cpu_only=True,network=False,ctc_forward_passes=0,
                  model_sha256={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in ('docs/labelfix/markshape_model_S4.json','docs/labelfix/case_model_S5.json')})
    (O/'S6_metrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('capitals','capitals_disagreement','regressions','elapsed_seconds')},ensure_ascii=False),flush=True)
    print('presence',result['heldout']['presence'],flush=True)

if __name__=='__main__':main()
