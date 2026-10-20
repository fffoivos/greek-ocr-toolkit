"""SS6 deterministic data adapter: saved judgments only, no readers or OCR."""
from __future__ import annotations
import collections as C
import hashlib
import json
import math
import re
import statistics as st
import sys
import unicodedata as U
from pathlib import Path

SS = Path(__file__).resolve().parents[1]
REVIEW = Path.home() / 'Projects/greek-ocr-toolkit-review'
ORDER = 'word caps_display abbrev_label marker roman_lower digits_letters number punctuation foreign_script handwriting watermark figure_ornament show_through noise cut_fragment multi_line part_of_line other'.split()
CLASSES = ['legit_text','printed_nonletter','non_text','out_of_scope_script','segmentation_fault','other']
LEGIT = set(ORDER[:7])
STRATA = ['opus','inside_by_source','mixed','rotated','border_outside','owner']

def load(p): return json.loads(p.read_text())
def jsonl(p): return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
def dump(p, v): p.write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def classify(typ, crop):
    if typ in LEGIT or typ == 'punctuation':
        if crop in {'clipped','extra'}: return 'segmentation_fault'
        if crop == 'ok': return 'legit_text' if typ in LEGIT else 'printed_nonletter'
        raise ValueError((typ,crop))
    if typ in {'noise','handwriting','figure_ornament','watermark','show_through'}: return 'non_text'
    if typ == 'foreign_script': return 'out_of_scope_script'
    if typ in {'cut_fragment','multi_line','part_of_line'}: return 'segmentation_fault'
    if typ == 'other': return 'other'
    raise ValueError(typ)

def final(sol, lead):
    return {k: lead[k] if lead and k in lead else sol[k] for k in ('type','text','crop')}

def control_calls(agreement):
    # Controls repeat in several contexts; preserve every actual amended observation.
    calls = C.defaultdict(list)
    for ctx, versions in agreement['controls'].items():
        version = 'amended' if 'amended' in versions else list(versions)[-1]
        for r in versions[version]['results']:
            calls[r['line_id']].append({'context':ctx,'version':version,**r['actual']})
    return calls

def make_rows():
    sample = jsonl(SS/'q3/sample.jsonl'); typed = {r['line_id']:r for r in jsonl(SS/'q3/typing.jsonl')}
    eye = load(SS/'q3/LEAD_EYE.json'); a=load(SS/'q3/AGREEMENT.json')
    controls = set(a['excluded_control_line_ids']); calls=control_calls(a)
    owners={r['line_id']:r for r in jsonl(SS/'q1/owner_joined.jsonl')}
    rows=[]
    for s in sample:
        lid=s['line_id']; is_control=lid in controls
        sol=typed.get(lid); lead=eye['corrections'].get(lid)
        # No single final Sol call exists for repeated controls excluded by SS5.
        if sol is None:
            variants={tuple(c[k] for k in ('type','text','crop','rotated')) for c in calls[lid]}
            sol=calls[lid][0] if len(variants)==1 else None
        f=final(sol,lead) if sol else None
        o=owners.get(lid,{})
        r={**s,'text':s['raw_text'],'width':s['width_px'],'height':s['height_px'],
           'class':s['primary_class'],'reason_category':o.get('category',s.get('reason_05')),
           'control':is_control,'sol':{k:sol[k] for k in ('type','text','crop','rotated','detail')} if sol else None,
           'lead':lead,'lead_checked':lid in eye['checked'], 'final_type':f['type'] if f else None,
           'final_text':f['text'] if f else None,'final_crop':f['crop'] if f else None,
           'final_class':classify(f['type'],f['crop']) if f else None,
           'label_ok':f['text'] in {'match','minor'} if f else None,
           'opus_type':typed.get(lid,{}).get('opus_type'),
           'owner_good':o.get('owner_good',False),'owner_bad':o.get('owner_bad',False),
           'owner_conflict':o.get('owner_conflict',False), 'owner_judgments':o.get('owner_judgments',[])}
        if is_control:
            r['control_observations']=calls[lid]
            r['control_note']='Excluded from bed; all amended context observations preserved. Final fields null when calls differ.'
        rows.append(r)
    assert len(rows)==437 and len({r['line_id'] for r in rows})==437
    assert {r['line_id'] for r in rows if not r['control']} == set(typed)
    return rows

def sort_key(r): return (ORDER.index(r['final_type']),not r['inside'],r['source'],r['line_id'])
def summary(rows, key, categories):
    out=[]
    for value in categories:
        rs=[r for r in rows if r[key]==value];n=len(rs)
        out.append({'value':value,'n':n,'share':n/len(rows) if rows else None,
            'examples':[r['line_id'] for r in rs[:3]],
            'median_width':st.median(r['width'] for r in rs) if n else None,
            'median_height':st.median(r['height'] for r in rs) if n else None,
            'median_chars':st.median(r['chars'] for r in rs) if n else None,
            'median_A':st.median(r['A'] for r in rs) if n else None,
            'label_ok_n':sum(r['label_ok'] for r in rs),
            'label_ok_share':sum(r['label_ok'] for r in rs)/n if n else None})
    return out

def wilson(k,n):
    z=1.959963984540054;p=k/n;d=1+z*z/n
    mid=(p+z*z/(2*n))/d;rad=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [mid-rad,mid+rad]

def text_profile(text):
    # Ignore whitespace and Unicode combining marks for shape classification.
    cs=[c for c in U.normalize('NFD',text) if not c.isspace() and not U.category(c).startswith('M')]
    letters=[c for c in cs if c.isalpha()];digits=[c for c in cs if c.isdigit()]
    return {'letters_only':bool(cs) and all(c.isalpha() for c in cs),
        'digits_letters':bool(letters and digits),
        'punctuation_only':bool(cs) and all(U.category(c).startswith('P') for c in cs),
        'other_script':any(c.isalpha() and not any(s in U.name(c,'') for s in ('GREEK','LATIN','CYRILLIC')) for c in cs),
        'empty':not text.strip()}

def tables(rows):
    bed=[r for r in rows if not r['control']];inside=[r for r in bed if r['stratum']=='inside_by_source']
    pool=load(SS/'q3/SS3_RECEIPT.json')['pools']['inside_by_source'];sources=pool['by_source'];total=pool['total']
    assert len(inside)==150 and all(r['chars']<=8 and r['A']<=6 and r['inside'] for r in inside)
    t7={}
    for name,rs in [('overall',bed)]+[(s,[r for r in bed if r['stratum']==s]) for s in STRATA]:
        t7[name]={'n':len(rs),'final_type':summary(rs,'final_type',ORDER),'class':summary(rs,'final_class',CLASSES)}
    t8={}
    for key,cats in [('final_class',CLASSES),('final_type',ORDER)]:
        t8[key]=[]
        for v in cats:
            n=sum(r[key]==v for r in inside)
            p=sum(size/total * sum(r[key]==v for r in inside if r['source']==s)/sum(r['source']==s for r in inside) for s,size in sources.items())
            t8[key].append({'value':v,'n':n,'weighted_share':p,'estimated_pool_rows':p*total,'unweighted_share':n/150,'wilson95_unweighted':wilson(n,150)})
    t9={s:{'n':sum(r['source']==s for r in inside),'pool_n':size,'pool_weight':size/total,
        'classes':summary([r for r in inside if r['source']==s],'final_class',CLASSES)} for s,size in sources.items()}
    t10=[]
    for cl in CLASSES:
        rs=[r for r in bed if r['final_class']==cl];n=len(rs);profiles=[text_profile(r['text']) for r in rs]
        t10.append({'class':cl,'n':n,**{k:sum(p[k] for p in profiles)/n if n else None for k in text_profile('')},'label_ok_share':sum(r['label_ok'] for r in rs)/n if n else None})
    mixed=[r for r in bed if r['stratum']=='mixed']
    t12=[]
    for cl in CLASSES:
        rs=[r for r in bed if r['final_class']==cl and r['owner_judgments']]
        t12.append({'class':cl,'n':len(rs),'good_only':sum(r['owner_good'] and not r['owner_bad'] for r in rs),
            'bad_only':sum(r['owner_bad'] and not r['owner_good'] for r in rs),'conflict':sum(r['owner_good'] and r['owner_bad'] for r in rs),
            'neither':sum(not r['owner_good'] and not r['owner_bad'] for r in rs)})
    eye=load(SS/'q3/LEAD_EYE.json');checked=[r for r in bed if r['lead_checked']]
    def changed(r):return any(r['sol'][k]!=r['lead'][k] for k in ('type','text','crop')) if r['lead'] else False
    t13={'checked':len(checked),'corrections':len(eye['corrections']),'changed':sum(changed(r) for r in checked),'by_sol_type':[], 'observations':eye['observations']}
    for typ in ORDER:
        rs=[r for r in checked if r['sol']['type']==typ]
        t13['by_sol_type'].append({'sol_type':typ,'checked':len(rs),'changed':sum(changed(r) for r in rs),'type_changed':sum(r['final_type']!=typ for r in rs),'text_changed':sum(r['final_text']!=r['sol']['text'] for r in rs),'crop_changed':sum(r['final_crop']!=r['sol']['crop'] for r in rs)})
    return {'scope':{'sample':437,'bed':len(bed),'controls':20,'T8_n':150,'T8_pool':total,'T8_pool_note':pool['excludes']},
        'T7':t7,'T8':t8,'T9':t9,'T10':t10,'lexicon':{'status':'No local spellcheck lexicon data found; skipped.','searched':['greekocr/ (including ignored files)','artifacts/ (directory absent)'],'code_only':['greekocr/labelfix/lexicon.py','greekocr/labelfix/build_lexicon.py']},
        'T11':{'n':len(mixed),'final_type':summary(mixed,'final_type',ORDER),'class':summary(mixed,'final_class',CLASSES)},'T12':t12,'T13':t13}

def fmt(x):
    if x is None:return '—'
    if isinstance(x,float):return f'{x:.4f}'
    return str(x).replace('|','\\|').replace('\n',' ')
def mdtable(head,rows):return '\n'.join(['| '+' | '.join(head)+' |','| '+' | '.join(['---']*len(head))+' |']+['| '+' | '.join(map(fmt,r))+' |' for r in rows])+'\n'
def write_markdown(q):
    out=['# Q3 final tables\n','417 bed rows; 20 controls excluded. Final type/text/crop use the lead correction where present, otherwise Sol. label_ok means final text code match or minor; it does not assert a usable crop. A = long/short side. Width and height medians are computed separately, in native orientation. Examples show up to three available rows; zero cells are retained.\n']
    out+=['## T7 — final typology\n']
    for s,g in q['T7'].items():
        out.append(f'### {s} (n={g["n"]})\n')
        for key in ['final_type','class']:
            out.append(mdtable([key,'n','share','median w×h px','median chars','median A','label_ok share','example line_ids'],[[r['value'],r['n'],r['share'],f"{fmt(r['median_width'])}×{fmt(r['median_height'])}",r['median_chars'],r['median_A'],r['label_ok_share'],', '.join(r['examples'])] for r in g[key]]))
    out+=['## T8 — source-weighted population estimate\n','A **150-row sample** of nonnumeric small rows (chars ≤ 8 and A ≤ 6), inside_by_source only. Source weights are SS3 pool counts / 19,377. This residual pool excludes earlier drawn strata (including Opus); estimates apply to that sampling frame, not an unbiased census of all small rows. Weighted estimate = Σ source pool share × within-source observed share. Estimated counts refer to that residual pool. The 95% Wilson intervals describe **unweighted** k/150 shares and are not confidence intervals for the weighted estimates. No interval accounts for prior selection or judgment uncertainty.\n']
    for key,rs in q['T8'].items():out.append(mdtable([key,'k/150','weighted share','estimated pool rows','unweighted share','Wilson 95% (unweighted)'],[[r['value'],r['n'],r['weighted_share'],r['estimated_pool_rows'],r['unweighted_share'],' – '.join(fmt(x) for x in r['wilson95_unweighted'])]for r in rs]))
    out+=['## T9 — inside_by_source class shares\n',mdtable(['source','n','pool n','pool weight']+CLASSES,[[s,v['n'],v['pool_n'],v['pool_weight']]+[r['share'] for r in v['classes']] for s,v in q['T9'].items()])]
    out+=['## T10 — Google text profiles by final class\n','All bed rows. Whitespace and combining marks ignored for shape tests; letters-only requires ≥1 letter and no other characters. Digits+letters requires both, permits punctuation, and can overlap other-script. Punctuation-only uses Unicode P categories (symbols such as % or + are not all punctuation). Other-script tests letters outside Greek/Latin/Cyrillic; punctuation resembling a foreign character is not a script letter. Empty means blank/whitespace. Categories need not sum to one.\n',mdtable(['class','n','letters only','digits+letters','punctuation only','other script','empty','label_ok'],[[r[k] for k in ['class','n','letters_only','digits_letters','punctuation_only','other_script','empty','label_ok_share']] for r in q['T10']]),q['lexicon']['status']+' Searched greekocr/ and artifacts/; artifacts/ is absent. Lexicon builder/loader code exists, but no word-list data was found.\n']
    out+=['## T11 — mixed stratum\n',f"n={q['T11']['n']}; selected by Google digits+letters, not by final ink type.\n"]
    for key in ['final_type','class']:out.append(mdtable([key,'n','examples'],[[r['value'],r['n'],', '.join(r['examples'])]for r in q['T11'][key]]))
    out+=['## T12 — final class vs owner good/bad\n','Join all bed rows against owner_joined.jsonl, across all strata (not just the owner stratum). Counts are per unique line; multiple judgments are collapsed to good-only / bad-only / conflicting / neither. Controls excluded. These are recorded judgments, not new owner decisions.\n',mdtable(['class','owner-judged n','good only','bad only','conflict','neither'],[[r[k]for k in ['class','n','good_only','bad_only','conflict','neither']] for r in q['T12']])]
    t=q['T13'];out+=['## T13 — lead eye vs Sol\n',f"Checked {t['checked']} rows; {t['changed']} rows changed type, text or crop ({t['corrections']} correction records). Note-only changes do not count. Per-Sol-type denominators are checked rows only.\n",mdtable(['Sol type','checked','changed','type changed','text changed','crop changed'],[[r[k]for k in ['sol_type','checked','changed','type_changed','text_changed','crop_changed']]for r in t['by_sol_type']]),'Lead observations (verbatim):\n']
    out+=['> '+v+'\n' for v in t['observations']]
    (SS/'q3/Q3_TABLES.md').write_text('\n'.join(out))

def sheet(rows):
    sys.path.insert(0,str(REVIEW))
    from greekocr.adjudicate import owner_sheet
    assert Path(owner_sheet.__file__).resolve().is_relative_to(REVIEW.resolve())
    descriptions=dict(re.findall(r'^- `([^`]+)`: (.+)$',(SS/'prompts/type.md').read_text(),re.M))
    bed=sorted([r for r in rows if not r['control']],key=sort_key)
    owners={r['line_id']:r for r in jsonl(SS/'q1/owner_joined.jsonl')}
    counts=C.Counter(r['final_type'] for r in bed);cards=[]; hashes={}
    for r in bed:
        p=Path(r['crop_path']);assert sha(p)==r['crop_sha256'];hashes[str(p)]=sha(p)
        sol=r['sol'];lead=r['lead'];o=owners.get(r['line_id'],{})
        versions=[{'name':'0.5','verdict':r['verdict_05'],'text':o.get('reason_05',r['reason_05'])}]
        if o.get('verdict_08'):versions.append({'name':'0.8','verdict':o['verdict_08'],'text':o['reason_08']})
        info=[{'name':'Google','text':r['text']},{'name':'Type (Sol / lead)','text':sol['type']+' / '+(lead['type'] if lead else 'no correction')+'; final '+r['final_type']+' → '+r['final_class']},
            {'name':'Text vs crop','text':f"Sol: text {sol['text']}; crop {sol['crop']}; rotated {sol['rotated']}; detail: {sol['detail'] or '—'}"+(f" | Lead: text {lead['text']}; crop {lead['crop']}; note: {lead['note']}" if lead else '')}]
        if r['opus_type']:info.append({'name':'Opus type','text':r['opus_type']})
        info.extend([{'name':'Size','text':f"{r['width']}×{r['height']} px; {r['chars']} chars; A={r['A']:.3f}; {'inside' if r['inside'] else 'outside'}"},{'name':'Source','text':f"{r['source']}; {r['book']}; {r['wave']}"}])
        cards.append({'line_id':r['line_id'],'group':r['final_type'],'image':p,'alt':r['line_id'], 'rows':info,'versions':versions,'tool_verdict':versions[-1]['verdict'],'tags':[{'text':r['stratum']},{'text':r['final_class']}]})
    proposed={t:classify(t,'ok') for t in ORDER}
    groups=[{'id':t,'heading':f"{t} — {counts[t]} — proposed class: {proposed[t]}",'gap':descriptions[t]+(' Legitimate/punctuation types with clipped/extra crops map to segmentation_fault.' if t in LEGIT|{'punctuation'} else '')} for t in ORDER]
    intro='\n'.join(['Q3 typology of non-numeric small segments; small = chars ≤ 8 and long/short side ≤ 6. Bed includes border/outside comparison rows and ink typed as numbers. 417 bed cards; 20 controls excluded.',
        'KEEP = this crop with its Google text is a usable training line; DROP = it is not.',
        'Outer frame = your mark: green KEEP, red DROP, neutral unmarked. Inner frame = latest available saved tool verdict: 0.8 where present, otherwise 0.5; green KEEP, red DROP, amber UNCERTAIN.',
        'Keys: ↑ ↓ move; SPACE toggles KEEP/DROP; z zooms; b toggles saved overlays (none supplied in these sample records); Esc leaves notes. Hover/click gives the lens. Marks and notes save only after your action; no writes on load.',
        'Groups: '+', '.join(f'{t} {counts[t]}' for t in ORDER)+'.',
        'Final lead-corrected types are proposed typology, not owner marks. Group headers use the ok-crop class; individual clipped/extra crops show segmentation_fault.'])
    html=owner_sheet.render(cards,{'title':'Q3 — small-segment typology owner review','intro':intro,'groups':groups,'sheet_prefix':'smallseg'})
    (SS/'sheet').mkdir(exist_ok=True)
    (SS/'sheet/small_segments_sheet.html').write_text(html)
    dump(SS/'sheet/card_manifest.json',[{'line_id':r['line_id'],'doc_id':'smallseg:'+r['line_id'],'group':r['final_type'],'inside':r['inside'],'source':r['source'],'crop_sha256':r['crop_sha256']} for r in bed])
    return dict(counts),hashes,str(owner_sheet.__file__)

def main():
    rows=make_rows();(SS/'samples.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    q=tables(rows);dump(SS/'q3/q3.json',q);write_markdown(q)
    counts,hashes,module=sheet(rows)
    inputs=[SS/p for p in ['q3/typing.jsonl','q3/LEAD_EYE.json','q3/sample.jsonl','q1/owner_joined.jsonl','q3/AGREEMENT.json','q3/SS3_RECEIPT.json','prompts/type.md']]
    inputs += [REVIEW/p for p in ['docs/review/HUMAN_REVIEW_SHEETS.md','docs/review/reference_scratch/build_gate_sheet.py','greekocr/adjudicate/owner_sheet.py','greekocr/adjudicate/owner_sheet.css','greekocr/adjudicate/owner_sheet.js']]
    dump(SS/'q3/SS6_RECEIPT.json',{'status':'BUILT_PENDING_VALIDATION','inputs':{str(p):sha(p) for p in inputs},'crop_inputs':hashes,'owner_sheet_module':module,'card_counts_per_group':{t:counts.get(t,0) for t in ORDER},'sample_rows':len(rows),'bed_cards':sum(counts.values()),'controls':20,'render_check':None,'tests':None,'outputs':{}})
    print('Built',len(rows),'sample rows;',sum(counts.values()),'cards;',q['T13']['changed'],'lead changes')
if __name__=='__main__':main()
