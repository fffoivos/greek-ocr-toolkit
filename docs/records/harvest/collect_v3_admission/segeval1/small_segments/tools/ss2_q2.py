"""SS2 descriptive analysis. Run with -B; writes only q2. Network unused."""
from pathlib import Path
import collections
import json
import re
import sys
import subprocess
import platform
import pandas as pd
import numpy as np
import ss1_q1 as ss1
from ss1_q1 import (chars, rotation, output_type, xheight, wave_group, reason_category,
    box_fail, sha, read_rows, crop_hash, owner_class, owner_bad_box, join_records,
    false_reject_counts, candidate_membership, pct, clean, write_json, md_table)
BASE = ss1.BASE
SMALL = ss1.SMALL
OUT = SMALL / 'q2'
INPUTS = ss1.INPUTS
TYPES = ['numeric', 'mixed', 'nonnumeric']
DEFINITIONS = {'D_rec': ('D_rec','C7',8,6), 'D_alt5': ('D_alt5','C7',5,4),
               'D_cells': ('D_cells','C5',None,None)}
EXTENSIONS = [(f'chars_le_{c}_A_le_{a}','C7',c,a) for c,a in
              [(10,6),(10,8),(12,8),(8,5),(8,8),(6,5)]]


def book_page(row_id):
    m = re.match(r'^(.*?)--(s[0-9]+)(?:-|$)', row_id)
    if m:
        return m[1], m[1]+'--'+m[2], 'double_dash_s'
    m = re.match(r'^(.*?)-p([0-9]+)-l[0-9]+$', row_id)
    if m:
        return m[1], m[1]+'-p'+m[2], 'collection_v2'
    book = re.sub(r'(?:--|-)l[0-9]+$', '', row_id)
    return book, book, 'fallback'


def concentration(counts):
    values = sorted((int(v) for v in counts if v > 0), reverse=True)
    total = sum(values)
    result = {'books_with_rows':len(values), 'rows':total}
    for target in [50,80,95]:
        cumulative = 0
        k = 0
        for v in values:
            if cumulative*100 >= total*target: break
            cumulative += v
            k += 1
        result[f'books_for_{target}pct'] = k
    for k in [1,5,10,20,50,100]:
        result[f'top_{k}_share_pct'] = pct(sum(values[:k]),total)
    return result


def ranked_books(books, field='small_rows', density=False):
    f = books[books.rows >= 50].copy() if density else books.copy()
    key = 'density_pct' if density else field
    return f.sort_values([key,'book'],ascending=[False,True]).head(40).to_dict('records')


def ratio_bucket(n, d, edges):
    for i, upper in enumerate(edges):
        if 100*n <= upper*d: return i
    raise ValueError((n,d))


def page_proxies(pages):
    return {'numeric_ge_50pct':pages.numeric_rows*2 >= pages.rows,
            'small_ge_50pct':pages.small_rows*2 >= pages.rows}


def type_counts(frame, keys):
    return pd.crosstab([frame[k] for k in keys],frame.output_type).reindex(columns=TYPES,fill_value=0)


def books_table(df, small):
    gb = df.groupby('book',sort=True)
    books = gb.size().rename('rows').to_frame()
    for field in ['source','wave','primary_class']:
        books[field] = gb[field].agg(lambda v: sorted(set(v)))
    books['pages'] = gb.page.nunique()
    books['small_rows'] = small.groupby('book').size()
    books['pages_with_small'] = small.groupby('book').page.nunique()
    for typ in TYPES:
        books[typ] = small[small.output_type.eq(typ)].groupby('book').size()
    for field in ['small_rows','pages_with_small']+TYPES:
        books[field] = books[field].fillna(0).astype(int)
    books['density_pct'] = 100*books.small_rows/books.rows
    return books.reset_index()[['book','source','wave','primary_class','rows','small_rows',
                                'density_pct']+TYPES+['pages','pages_with_small']]


def page_table(df, small):
    pages = df.groupby('page').size().rename('rows').to_frame()
    pages['book'] = df.groupby('page').book.first()
    pages['small_rows'] = small.groupby('page').size()
    pages['numeric_rows'] = df[df.output_type.eq('numeric')].groupby('page').size()
    for typ in TYPES:
        pages[typ] = small[small.output_type.eq(typ)].groupby('page').size()
    for field in ['small_rows','numeric_rows']+TYPES:
        pages[field] = pages[field].fillna(0).astype(int)
    return pages.reset_index()


def page_summary(pages):
    distributions = []
    labels = ['0–10%','(10–25%]','(25–50%]','(50–75%]','(75–90%]','(90–100%]']
    for share,field in [('small_share','small_rows'),('numeric_share','numeric_rows')]:
        buckets = [ratio_bucket(n,d,[10,25,50,75,90,100]) for n,d in zip(pages[field],pages.rows)]
        for i,label in enumerate(labels):
            f = pages[np.array(buckets)==i]
            distributions.append(dict(share=share,bucket=label,pages=len(f),small_rows=int(f.small_rows.sum()),
                share_of_all_small_pct=pct(f.small_rows.sum(),pages.small_rows.sum()),
                **{t:int(f[t].sum()) for t in TYPES}))
    proxies=[]
    for name,mask in page_proxies(pages).items():
        f=pages[mask]
        proxies.append(dict(proxy=name,pages=len(f),small_rows=int(f.small_rows.sum()),
            share_of_all_small_pct=pct(f.small_rows.sum(),pages.small_rows.sum()),
            **{t:int(f[t].sum()) for t in TYPES},
            **{t+'_share_of_type_pct':pct(f[t].sum(),pages[t].sum()) for t in TYPES}))
    isolated=pages[pages.small_rows.eq(1)]
    return dict(distributions=distributions,table_like_proxies=proxies,
        isolated=dict(pages=len(isolated),small_rows=int(isolated.small_rows.sum()),
                      **{t:int(isolated[t].sum()) for t in TYPES}))


def analyze(df, definition, baseline):
    small = df[candidate_membership(df,definition)]
    groups={}
    for field in ['source','wave','primary_class','script_class']:
        rows=[]
        for name,f in df.groupby(field,sort=True):
            subset=small[small[field].eq(name)]
            rows.append(dict(group=name,rows=len(f),small_rows=len(subset),
                share_of_all_small_pct=pct(len(subset),len(small)),density_pct=pct(len(subset),len(f)),
                **{t:int(subset.output_type.eq(t).sum()) for t in TYPES}))
        groups[field]=sorted(rows,key=lambda r:(-r['small_rows'],r['group']))
    books=books_table(df,small)
    nonnumeric=small[~small.output_type.eq('numeric')]
    nnbooks=books_table(df,nonnumeric)
    histogram=[]
    eligible=books[books.rows.ge(50)]
    edges=[0,1,5,10,25,50,75,100]
    buckets=[ratio_bucket(n,d,edges) for n,d in zip(eligible.small_rows,eligible.rows)]
    for i,label in enumerate(['0','(0–1%]','(1–5%]','(5–10%]','(10–25%]','(25–50%]','(50–75%]','(75–100%]']):
        histogram.append(dict(bucket=label,books=sum(x==i for x in buckets)))
    pages=page_table(df,small)
    return dict(small_rows=len(small),output_types={t:int(small.output_type.eq(t).sum()) for t in TYPES},
        G1=groups,G2=dict(small=concentration(books.small_rows),all_rows_baseline=baseline,
                          nonnumeric_only=concentration(small[small.output_type.eq('nonnumeric')].groupby('book').size())),
        G3=dict(top40_by_count=ranked_books(books),top40_by_density_min50=ranked_books(books,density=True),
                density_histogram_min50=histogram),
        G4=dict(scope='nonnumeric + mixed',top40_by_count=ranked_books(nnbooks),
                concentration=concentration(nnbooks.small_rows),all_rows_baseline=baseline),
        G5=dict(pages=pages.to_dict('records'),**page_summary(pages)),
        G6=dict(source_by_output_type=type_counts(small,['source']).reset_index().to_dict('records'),
                source_by_wave=pd.crosstab(small.source,small.wave).reset_index().to_dict('records')))


# Owner preparation copied from SS1 main; joins and classification functions imported.
def prepare_owners(df, input_info):
    records, replay_records, decision_vocab, replay_counts = [], [], collections.Counter(), {}
    for j,p in enumerate(INPUTS[1:],1):
        count = 0
        for r in read_rows(BASE/p):
            count += 1
            common = dict(line_id=r['line_id'], crop_sha256=crop_hash(r), source_file=p)
            if j == 1:
                records.append(dict(common, set='O_marks', sheet=r.get('sheet'), decision=r['owner_mark'],
                                    owner_class=owner_class(r['owner_mark']),note=r.get('note',''),updated=r.get('updated')))
            if j in [2,3]:
                replay_records.append(dict(common,set='replay_calibration' if j==2 else 'replay_segeval1',
                                           **{f'verdict_0{v}':r.get(f'verdict_0{v}') for v in [5,6,7,8]},
                                           reason_08=r.get('after',{}).get('reason')))
                if j == 2 and r.get('owner_rating') is not None:
                    rating=r['owner_rating']; dec=rating.get('decision'); decision_vocab[dec]+=1
                    records.append(dict(common,set='O_ratings',sheet=None,decision=dec,owner_class=owner_class(dec),
                                        note=rating.get('note',''),updated=rating.get('updated')))
            if j == 4:
                records.append(dict(common,set='R_150',reader_state=r['reader_state'],pipeline_decision=r['decision']))
        input_info[j]['row_count']=count
    joined, joins = join_records(df,records)
    replays, replay_joins = join_records(df,replay_records)
    replay_by_idx = collections.defaultdict(list)
    for r in replays:
        if r['census_index'] is not None: replay_by_idx[r['census_index']].append(r)
    by_idx = collections.defaultdict(list)
    unmatched_owner=[]
    for r in joined:
        if r['census_index'] is not None: by_idx[r['census_index']].append(r)
        elif r['set'] != 'R_150': unmatched_owner.append(r)
    owners=[]
    conflicts=[]
    for idx, rr in by_idx.items():
        oo=[r for r in rr if r['set'] != 'R_150']
        if not oo: continue
        d=df.iloc[idx].to_dict(); d['line_id']=d.pop('row_id'); d['census_index']=idx
        d['sets']=sorted(set(r['set'] for r in oo)); d['owner_judgments']=oo
        d['owner_classes']=sorted(set(r['owner_class'] for r in oo))
        d['owner_good']=any(r['owner_class']=='good' for r in oo)
        d['owner_bad']=any(r['owner_class']=='bad' for r in oo)
        d['owner_conflict']=d['owner_good'] and d['owner_bad']
        if d['owner_conflict']: conflicts.append(d['line_id'])
        d['note']='; '.join(r['note'] for r in oo if r.get('note'))
        d['owner_bad_box']=owner_bad_box(d['note'])
        d['replay_evidence']=replay_by_idx[idx]
        for v in [6,7,8]:
            values=sorted(set(r[f'verdict_0{v}'] for r in replay_by_idx[idx] if r.get(f'verdict_0{v}') is not None))
            d[f'verdict_0{v}']=values[0] if len(values)==1 else None
            if len(values)>1: conflicts.append(dict(line_id=d['line_id'],field=f'verdict_0{v}',values=values))
        d['reason_08']='; '.join(sorted(set(r['reason_08'] for r in replay_by_idx[idx] if r.get('reason_08'))))
        d['category_08']=reason_category(d['verdict_08'],d['reason_08']) if d['verdict_08'] else None
        owners.append(d)
    # Unmatched owner records remain in the all-owner export, with null census measurements.
    for r in unmatched_owner:
        d={k:None for k in df.columns}; d.update(line_id=r['line_id'],sets=[r['set']],owner_judgments=[r],
            owner_classes=[r['owner_class']],owner_good=r['owner_class']=='good',owner_bad=r['owner_class']=='bad',
            owner_conflict=False,note=r.get('note',''),owner_bad_box=owner_bad_box(r.get('note')),
            census_index=None,verdict_06=None,verdict_07=None,verdict_08=None,category_08=None,reason_08=None)
        owners.append(d)
    owners.sort(key=lambda r:(r['chars'] is None,r['chars'] or 0,r['A'] or 0,r['line_id']))
    return owners, joined, replay_by_idx, joins, replay_joins


# SS1 main T4 block copied VERBATIM below, including its original indentation.
# candidate_definitions is supplied as a local callable; no T4 computation changed.
def t4_copy(df, owners, joined, replay_by_idx, definitions):
    n = len(df)
    candidate_definitions = lambda: definitions
    t4=[]; matched_owners=[r for r in owners if r['census_index'] is not None]
    owner_groups={'O_marks':[r for r in joined if r['set']=='O_marks' and r['census_index'] is not None],
                  'O_ratings':[r for r in joined if r['set']=='O_ratings' and r['census_index'] is not None]}
    for sheet in sorted({r['sheet'] for r in owner_groups['O_marks']}):
        owner_groups['O_marks / '+sheet]=[r for r in owner_groups['O_marks'] if r['sheet']==sheet]
    for definition in candidate_definitions():
        membership=candidate_membership(df,definition); name=definition[0]
        for side,mask in [('inside',membership),('outside',~membership)]:
            f=df[mask]; base=dict(candidate=name,side=side)
            t4.append(dict(base,section='census',group='all',n=len(f),pct_census=pct(len(f),n),
                           pct_box_fail=pct(f.box_fail.sum(),len(f)),pct_KEEP=pct(f.verdict_05.eq('KEEP').sum(),len(f)),
                           n_chars_le_10=int(f.chars.le(10).sum()),
                           pct_box_fail_chars_le_10=pct(f[f.chars<=10].box_fail.sum(),f.chars.le(10).sum()),
                           xh_unusable_n=int((~f.xh_usable).sum())))
            for field in ['output_type','wave_group']:
                for value in sorted(df[field].unique()):
                    count=int(f[field].eq(value).sum())
                    t4.append(dict(base,section='capture_'+field,group=value,n=count,pct_census=pct(count,n),
                                   pct_of_group=pct(count,df[field].eq(value).sum()),pct_of_side=pct(count,len(f))))
            for group,rr in owner_groups.items():
                selected=[r for r in rr if mask.iloc[r['census_index']]]
                good={r['census_index'] for r in selected if r['owner_class']=='good'}
                t4.append(dict(base,section='owner',group=group,n=len(selected),
                    good=sum(r['owner_class']=='good' for r in selected),bad=sum(r['owner_class']=='bad' for r in selected),
                    other=sum(r['owner_class']=='other' for r in selected),
                    **false_reject_counts(good,df,replay_by_idx)))
            selected=[r for r in matched_owners if mask.iloc[r['census_index']]]
            good={r['census_index'] for r in selected if r['owner_good']}
            t4.append(dict(base,section='owner',group='unique',n=len(selected),good=sum(r['owner_good'] for r in selected),
                bad=sum(r['owner_bad'] for r in selected),other=sum(not r['owner_good'] and not r['owner_bad'] for r in selected),
                conflicts=sum(r['owner_conflict'] for r in selected),**false_reject_counts(good,df,replay_by_idx)))
            rr=[r for r in joined if r['set']=='R_150' and r['census_index'] is not None and mask.iloc[r['census_index']]]
            counts=collections.Counter(r['reader_state'] for r in rr)
            t4.append(dict(base,section='readers_only',group='R_150',n=len(rr),fine=counts.get('fine',0),
                           flagged=counts.get('flagged',0),unresolved=counts.get('unresolved',0),states=dict(counts)))
    return t4


def validate(result, n):
    checks=0
    def check(ok):
        nonlocal checks
        assert ok
        checks+=1
    for d in result['definitions'].values():
        total=d['small_rows']
        check(sum(d['output_types'].values())==total)
        for group in d['G1'].values():
            check(sum(r['rows'] for r in group)==n)
            check(sum(r['small_rows'] for r in group)==total)
            check(all(sum(r[t] for t in TYPES)==r['small_rows'] for r in group))
        pages=d['G5']['pages']
        check(sum(r['rows'] for r in pages)==n)
        check(sum(r['small_rows'] for r in pages)==total)
        check(all(sum(r[t] for t in TYPES)==r['small_rows'] for r in pages))
        for share in ['small_share','numeric_share']:
            check(sum(r['small_rows'] for r in d['G5']['distributions'] if r['share']==share)==total)
        check(sum(sum(r[t] for t in TYPES) for r in d['G6']['source_by_output_type'])==total)
        check(sum(sum(v for k,v in r.items() if k!='source') for r in d['G6']['source_by_wave'])==total)
        check(d['G2']['small']['rows']==total)
        check(d['G4']['concentration']['rows']==d['output_types']['mixed']+d['output_types']['nonnumeric'])
    return dict(status='PASS',checks_passed=checks)


def render(result):
    text=['# SS2 Q2 — origins and concentration of small segments\n',
          'Descriptive analysis only. Percentages use 0–100; undefined denominators are —.\n',
          '## Methods\n',md_table([dict(item=k,value=v) for k,v in result['methods'].items()]),
          '## Input and identifier metadata\n',md_table([dict(item=k,value=v) for k,v in result['metadata'].items()]),
          '## G0 — SS1 T4 extension\n',md_table(result['G0']),
          '### SS1 C7 reference — exact reproduction\n',
          'The following SS2 rows equal all 26 SS1 rows field for field; both copies are retained in q2.json.\n',
          md_table(result['G0_reference_check']['ss2_rows'])]
    for name,d in result['definitions'].items():
        text += [f'## {name}\n',md_table([dict(small_rows=d['small_rows'],**d['output_types'])])]
        for field,rows in d['G1'].items():
            text += [f'### G1 — {field}\n',md_table(rows)]
        text += ['### G2 — concentration\n',md_table([dict(scope=k,**v) for k,v in d['G2'].items()])]
        for field,rows in d['G3'].items(): text += [f'### G3 — {field}\n',md_table(rows)]
        text += ['### G4 — nonnumeric + mixed\n',md_table([dict(scope=k,**d['G4'][k]) for k in ['concentration','all_rows_baseline']]),
                 md_table(d['G4']['top40_by_count'])]
        for field in ['distributions','table_like_proxies']:
            text += [f'### G5 — {field}\n',md_table(d['G5'][field])]
        text += ['### G5 — isolated small rows\n',md_table([d['G5']['isolated']]),
                 '### G5 — every page\n',md_table(d['G5']['pages'])]
        for field,rows in d['G6'].items(): text += [f'### G6 — {field}\n',md_table(rows)]
    return '\n'.join(text)


def main():
    OUT.mkdir(exist_ok=True)
    receipt_path=SMALL/'q1/SS1_RECEIPT.json'
    previous=json.loads(receipt_path.read_text())
    imported_sha=sha(Path(ss1.__file__))
    if imported_sha!=previous['script_sha256']:
        raise RuntimeError('Imported SS1 hash differs from SS1 receipt')
    input_info=[dict(path=str(BASE/p),sha256=sha(BASE/p)) for p in INPUTS]
    aux=[dict(path=str(p),sha256=sha(p)) for p in [receipt_path,SMALL/'q1/q1.json']]
    slim=[]
    rule_counts=collections.Counter()
    examples=collections.defaultdict(list)
    print('Reading census',flush=True)
    for r in read_rows(BASE/INPUTS[0]):
        v={k:r[k] for k in ['row_id','crop_sha256','source','wave','primary_class','script_class','verdict_05']}
        v['chars']=chars(r)
        v.update(rotation(r['width_px'],r['height_px']))
        v['xh_usable']=xheight(r.get('xheight_px'),v['L'],v['S'])['xh_usable']
        v['output_type']=output_type(r['raw_text'],r['is_numeric_output'])
        v['wave_group']=wave_group(r['wave'])
        v['box_fail']=box_fail(reason_category(r['verdict_05'],r['reason_05']))
        v['book'],v['page'],rule=book_page(r['row_id'])
        rule_counts[rule]+=1
        if len(examples[rule])<3: examples[rule].append(dict(row_id=r['row_id'],book=v['book'],page=v['page']))
        slim.append(v)
    n=len(slim)
    input_info[0]['row_count']=n
    if n!=592466: raise RuntimeError(f'census count {n} != 592466')
    df=pd.DataFrame(slim); del slim
    if not df.row_id.is_unique: raise RuntimeError('duplicate row ids')
    print('Census verified; preparing owner inputs',flush=True)
    owners,joined,replay_by_idx,joins,replay_joins=prepare_owners(df,input_info)
    reference=('C7_chars_le_8_A_le_6','C7',8,6)
    actual=t4_copy(df,owners,joined,replay_by_idx,[reference])
    expected=[r for r in json.loads((SMALL/'q1/q1.json').read_text())['tables']['T4'] if r['candidate']==reference[0]]
    assert clean(actual)==expected, 'T4 C7 exact reproduction failed'
    print('T4 reference reproduced exactly:',len(actual),'rows',flush=True)
    g0=t4_copy(df,owners,joined,replay_by_idx,EXTENSIONS)
    baseline=concentration(df.groupby('book').size())
    methods=dict(definitions={'D_rec':'chars ≤ 8 and A ≤ 6','D_alt5':'chars ≤ 5 and A ≤ 4',
        'D_cells':'S ≤ 40 and L ≤ 200 and chars ≤ 10'},
        shared_definitions='Imported ss1_q1.chars, rotation and output_type; chars are saved characters.',
        ids='--sNNN page rule first; collection-v2 -p<digits>-l<digits> second; fallback strips trailing -l/--l digits and uses resulting book as page (no page token available).',
        concentration='Minimal number of descending-count books reaching ≥50/80/95%; ties may be split. Rankings break ties by book ascending. Empty totals yield zero books and null shares.',
        G2_nonnumeric='Literal nonnumeric output only; G4 separately includes mixed.',
        book_metadata='Sorted lists of every source/wave/primary_class observed in each book, without assigning a dominant value.',
        density='small rows / all rows in book; density ranking and histogram restrict to ≥50 rows. Zero-small books included.',
        page_buckets='Right-closed percentage ranges; zero shares included in first 0–10% page bucket. Exact 50% included in 25–50% bucket and in ≥50% proxies.',
        numeric_page_share='All numeric census rows / all rows in page; mixed excluded from numeric numerator.',
        G5='Each page printed per definition. Distribution numerator counts small rows. Type counts split small rows; proxy type percentages divide by all small rows of that type.',
        G6='Both crosstabs count small rows; output-type columns include explicit zeros.',
        G0='SS1 T4 is embedded in main; original block copied verbatim into t4_copy, not reimplemented. C7_chars_le_8_A_le_6 exact row equality against q1.json verified.',
        scope='Read-only inputs; descriptive tables; no judgement or recommendation. No network access.')
    result=dict(methods=methods,metadata=dict(census_rows=n,books=df.book.nunique(),pages=df.page.nunique(),
        id_rules=[dict(rule=k,rows=rule_counts[k],examples=examples[k]) for k in ['double_dash_s','collection_v2','fallback']],
        imported_ss1_sha256=imported_sha,owner_inputs=input_info[1:],owner_joins=joins,replay_joins=replay_joins,
        t4_reference_check=dict(candidate=reference[0],exact=True,rows=len(actual)),
        book_multiple_metadata_values={f:int(df.groupby('book')[f].nunique().gt(1).sum()) for f in ['source','wave','primary_class']}),
        G0=g0,G0_reference_check=dict(exact=True,ss1_rows=expected,ss2_rows=actual),definitions={})
    for name,definition in DEFINITIONS.items():
        print('Analyzing',name,flush=True)
        result['definitions'][name]=analyze(df,definition,baseline)
    validation=validate(result,n)
    result['metadata']['validation']=validation
    write_json(OUT/'q2.json',result)
    (OUT/'Q2_TABLES.md').write_text(render(result))
    test=subprocess.run([sys.executable,'-B','-m','pytest','-c','/dev/null','-p','no:cacheprovider',
        str(SMALL/'tests/test_ss2_q2.py'),'-q'],capture_output=True,text=True)
    (OUT/'tests.log').write_text(test.stdout+test.stderr)
    if test.returncode: raise RuntimeError('tests failed; see q2/tests.log')
    for info in input_info+aux:
        info['sha256_after']=sha(info['path'])
        assert info['sha256_after']==info['sha256'], 'Input changed'
    assert sha(Path(ss1.__file__))==imported_sha
    outputs=[OUT/'q2.json',OUT/'Q2_TABLES.md',OUT/'tests.log',Path(__file__).resolve(),SMALL/'tests/test_ss2_q2.py']
    receipt=dict(status='READY',inputs=input_info,owner_inputs=input_info[1:],auxiliary_inputs=aux,
        imported_ss1_script=dict(path=str(Path(ss1.__file__).resolve()),sha256=imported_sha,ss1_receipt_script_sha256=previous['script_sha256']),
        script_sha256=sha(__file__),outputs=[dict(path=str(p),sha256=sha(p)) for p in outputs],
        test_result=dict(returncode=test.returncode,output=test.stdout+test.stderr),
        versions=dict(python=sys.version,python_executable=sys.executable,pandas=pd.__version__,numpy=np.__version__,platform=platform.platform(),pytest=__import__('pytest').__version__),
        validation=validation,t4_reference_check=result['metadata']['t4_reference_check'],
        t4_verbatim_copy=True,input_hashes_unchanged=True,receipt_self_hash='Excluded to avoid circular self hash')
    write_json(OUT/'SS2_RECEIPT.json',receipt)
    print(json.dumps(clean(dict(metadata=result['metadata'],summaries={k:dict(small_rows=d['small_rows'],
        sources=d['G1']['source'][:3],concentration=d['G2'],proxies=d['G5']['table_like_proxies']) for k,d in result['definitions'].items()})),ensure_ascii=False),flush=True)


if __name__=='__main__':
    try:
        main()
    except Exception as exc:
        if OUT.exists(): write_json(OUT/'SS2_RECEIPT.json',dict(status='FAILED',reason=str(exc)))
        raise
