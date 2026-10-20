"""Measured offline/C1 audit ledgers; physical judgments are left unfilled."""
from collections import Counter,defaultdict
from pathlib import Path
import re
from .common import write_json,write_rows,read_json
from .rules import boundary_hyphens,word_scripts


def reports(out,tranche,features,context=None):
    root=Path(out)/tranche/'audits';witnesses=boundary_hyphens(features,context)
    write_rows(root/'hyphen_witnesses.jsonl',witnesses)
    changed=[]
    for r in features:
        if not r.get('assembly_changed'):continue
        old=r.get('old_label','');fixed=r['fixed_label'];strata=[]
        if re.search(r'[^\w\s]',old):strata.append('punctuation')
        if re.search(r'\d|\b[IVXLCMDΙΧΜϹІХСМѴ]+\b',old):strata.append('numerals')
        if len({s for _,s in word_scripts(old) if s not in ('none',)})>1 or any(s=='Mixed' for _,s in word_scripts(old)):strata.append('mixed_scripts')
        changed.append(dict(id=r['id'],source=r['source'],primary_class=r['primary_class'],crop=r.get('crop'),old_label=old,fixed_label=fixed,rollback_label=r.get('rollback_label',old),token_drop_trace=r.get('token_drop_trace',[]),strata=strata or ['other_changed'],dropped_punctuation=sum(sum(not ch.isalnum() and not ch.isspace() for ch in d.get('dropped_text','')) for d in r.get('token_drop_trace',[])),dropped_digits=sum(sum(ch.isdigit() for ch in d.get('dropped_text','')) for d in r.get('token_drop_trace',[])),rollback_available=r.get('rollback_label',old)==old,collateral_verdict=None))
    write_rows(root/'changed_line_collateral.jsonl',changed)
    write_json(root/'changed_line_collateral_receipt.json',dict(changed_lines=len(changed),strata=dict(Counter(s for r in changed for s in r['strata'])),physical_judgments=0,status='witnesses emitted; physical collateral review pending'))
    groups=defaultdict(list)
    for r in features:groups[r['source'],r['primary_class']].append(r)
    duplicate=[]
    for (source,cls),rr in sorted(groups.items()):
        eligible=[r for r in rr if r.get('candidate_before_dedupe',r.get('candidate_usable',False))]
        lost=sum(r.get('duplicate_exact',False) for r in eligible)
        duplicate.append(dict(source=source,primary_class=cls,before=len(eligible),exact_duplicates=lost,after=len(eligible)-lost,loss_rate=lost/len(eligible) if eligible else None))
    write_json(root/'duplicate_loss.json',dict(scope='exact crop SHA256 + normalised label; loss measured on this output only, not a near-duplicate claim',groups=duplicate,before=sum(r['before'] for r in duplicate),lost=sum(r['exact_duplicates'] for r in duplicate)))
    spread=[]
    for population,rr in [('with_hold',[r for r in features if r.get('candidate_usable')]),('admitted',[r for r in features if r.get('usable_final')])]:
        byclass=defaultdict(list)
        for r in rr:byclass[r['primary_class']].append(r)
        for cls,pool in sorted(byclass.items()):
            counts=Counter((r['source'],r.get('item','unknown')) for r in pool)
            for (source,item),n in sorted(counts.items()):spread.append(dict(population=population,primary_class=cls,source=source,item=item,rows=n,class_rows=len(pool),share=n/len(pool),cap=.10,passed=n/len(pool)<=.10,kind='book_issue'))
            if cls=='modern_scanned':
                for year,n in sorted(Counter(r.get('year') for r in pool if r['source']=='gazette_modern').items(),key=lambda v:str(v[0])):spread.append(dict(population=population,primary_class=cls,year=year,rows=n,class_rows=len(pool),share=n/len(pool),cap=.20,passed=n/len(pool)<=.20,kind='gazette_year'))
    write_json(root/'spread_caps.json',dict(rows=spread,violations=sum(not r['passed'] for r in spread),stage='after_dedupe',per_class={cls:dict(rows=sum(1 for r in features if r.get('candidate_usable') and r['primary_class']==cls),violations=sum(not r['passed'] for r in spread if r['primary_class']==cls)) for cls in sorted({r['primary_class'] for r in features})},scope='measured new unique candidate rows by class; whole-run cap must pass before release'))
    gazette=[]
    for stratum in ('probe_1982_1985','measured_1986_1990'):
        pool=[r for r in features if r['source']=='gazette_modern' and r.get('gazette_stratum')==stratum]
        mono=sum(r['primary_class']=='modern_scanned' and not r.get('gazette_polytonic') for r in pool)
        page_ids={r['page_id'] for r in pool}
        for path in (Path(out)/tranche/'pages').glob('*.json'):
            page=read_json(path)
            if page.get('status')=='completed' and page.get('source')=='gazette_modern':
                year=int(page.get('year') or page.get('analysis_page',{}).get('year') or 0)
                if (1982<=year<=1985 and stratum=='probe_1982_1985') or (1986<=year<=1990 and stratum=='measured_1986_1990'):page_ids.add(page['id'])
        gazette.append(dict(stratum=stratum,pages=len(page_ids),classified_rows=len(pool),modern_scanned_rows=mono,monotonic_share=mono/len(pool) if pool else None,denominator='all classified lines, including headings/numerics/dialogue',polytonic_rows=sum(r.get('gazette_polytonic',False) for r in pool),classes=dict(Counter(r['primary_class'] for r in pool))))
    write_json(root/'gazette_strata.json',dict(strata=gazette,primary_class_required='modern_scanned',polytonic_admitted=False))
    write_json(root/'conventions.json',dict(observed_substitutions={'long_s':sum(r.get('long_s_label_count',0) for r in features),'emdash_to_hyphen':sum(r.get('emdash_to_hyphen_count',0) for r in features),'elstat_raised_dot':sum(r.get('elstat_raised_dot_count',0) for r in features),'roman_tokens':sum(len(r.get('roman_fixes',[])) for r in features)},lookalike_lines=dict(Counter(r.get('lookalike_rule') for r in features if r['source']=='ia_greek_latin')),crop_tight_page_rows=sum(r.get('crop_tight_page',False) for r in features),note='label-observed counts; printed glyph totals require physical judgments'))
    return witnesses
