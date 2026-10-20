"""Offline N1-Cc rendering and candidate census; no packs or ink judgments."""
import json
import random
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from n1cb_prepare import (ROOT, OUT, SCRATCH, COLLECT, COLLECT_PY, RUN,
                          sha, rows, write, interpreter, sheet)

SEED = '20261017:N1Cc:raised'
APPROVED = {
    'baseline dot': [*range(1,13),14,15,*range(18,25)],
    'comma': list(range(25,48)),
    'hyphen or dash': [49,50,51,53,54,*range(56,71),73,75,76,77,78,80,81],
    'nothing': [84,87,89,90,91,92,94],
}


def main():
    sys.path.insert(0, str(ROOT))
    from greekocr.numerics.locks import load_locks
    from greekocr.numerics.slots_geom import locate_slot
    from greekocr.numerics.tokens import tokenize
    from n1_render import render
    from PIL import Image

    inputs = {}
    def bind(p):
        p = Path(p); inputs[str(p)] = sha(p); return p
    # Bind every earlier persistent artifact, plus all retained rendered images.
    prior = {str(p):sha(p) for p in OUT.rglob('*') if p.is_file()}
    cb = json.loads((OUT/'N1Cb_GENERATION.json').read_text())
    for p,d in cb['outputs'].items():
        assert sha(p)==d, p
        prior[p]=d
    for name in ['frame_step1.jsonl','locked_eval_docs.json','n1_reserved_docs.txt',
                 'n1_reserved_doc_line_ids.txt','n1_locked_eval_line_ids.txt',
                 'step1_rendered_v2.jsonl','controls/candidates_v2.jsonl',
                 'controls/c1_references_v2.jsonl','N1Cb_GENERATION.json']:
        bind(OUT/name)
    bind(ROOT/'docs/records/labelfix/secondary/N1_CONTROL_REVIEW.md')
    bind(ROOT/'docs/records/labelfix/secondary/prompts/sep.md')
    locks = load_locks(OUT)
    frame = [r for r in rows(OUT/'frame_step1.jsonl') if r['partition']=='step1']
    devdocs = {r['document'] for r in frame}
    c1 = set(json.loads((OUT/'locked_eval_docs.json').read_text())['excluded_c1_line_ids'])
    sheets = SCRATCH/'n1_ctrl_sheets'
    index = json.loads(bind(sheets/'sheets_index.json').read_text())
    oldcontrols = {r['slot_id']:r for name in ['controls/candidates_v2.jsonl','controls/c1_references_v2.jsonl'] for r in rows(OUT/name)}
    approved=[]
    for truth,cells in [*APPROVED.items(),('raised dot',[1,2,3,4])]:
        reference = truth=='raised dot'
        for cell in cells:
            matches=[r for r in index if r['cell_number']==cell and r['reference_only']==reference]
            assert len(matches)==1
            entry=matches[0]; r=dict(oldcontrols[entry['slot_id']])
            r.update(truth=truth,approval_sheet=entry['sheet'],approval_cell_number=cell,
                     c1_control_only=reference,reference_only=False)
            approved.append(r)
    assert len(approved)==len({r['slot_id'] for r in approved})==82
    w1=rows(bind(RUN/'W1/features.jsonl')); byid={r['id']:r for r in w1}
    def doc(row): return row['source']+':'+row['item']
    c1_document_conflicts=[]
    for r in approved:
        locks.assert_fit_rows([r['line_id']])
        document=doc(byid[r['line_id']]);r['document']=document
        assert document not in locks.reserved_docs
        if document in devdocs:
            assert r['c1_control_only']
            c1_document_conflicts.append(dict(slot_id=r['slot_id'],document=document))
        assert (r['line_id'] in c1)==r['c1_control_only']
    ambiguous_path=bind(COLLECT/'docs/records/harvest/collect_v3/release_exclusions/w1_elstat_separator_ambiguous_ids.txt')
    ambiguous=set(ambiguous_path.read_text().splitlines())
    responses={}
    def geometry(row,slot):
        locks.assert_fit_rows([row['id']])
        page=json.loads(bind(RUN/'W1/pages'/(row['page_id']+'.json')).read_text())
        response=Path(page['response'])
        if str(response) not in responses:
            assert sha(bind(response))==page['response_sha256']
            responses[str(response)]=json.loads(response.read_text())['document']
        return locate_slot(row,slot,responses[str(response)])
    pool=[];rejected=[];eligible_rows=set()
    for row in w1:
        if doc(row) in devdocs|locks.reserved_docs or row['id'] in c1: continue
        if row['id'] not in ambiguous and not (row['source']=='elstat' or row['source'].startswith('gazette')):continue
        # Google text is the sampling source. The exact localiser refuses label changes.
        for ti,t in enumerate(tokenize(row['text'])):
            if t.digit_count<4:continue
            for s in t.slots:
                if s.boundary or not s.glyph:continue
                origins=[]
                if row['id'] in ambiguous:origins.append('ambiguous_row')
                if s.glyph in ('·','-') and 'thousands' in s.grammar_candidates:origins.append('google_thousands')
                if not origins:continue
                slot=dict(asdict(s),slot_id=f"{row['id']}:t{ti}:s{s.index}",line_id=row['id'],
                          token_start=t.start,token_end=t.end,document=doc(row),source=row['source'],
                          google_token=t.text,selection_sources=origins)
                g=geometry(row,slot)
                if g['geom_status']=='ok':pool.append(dict(slot=slot,geometry=g));eligible_rows.add(row['id'])
                else:rejected.append(dict(slot_id=slot['slot_id'],line_id=row['id'],geometry=g))
    pool.sort(key=lambda r:r['slot']['slot_id'])
    assert len(pool)==len({r['slot']['slot_id'] for r in pool})
    draw=list(pool);random.Random(SEED).shuffle(draw)
    selected=[];counts=Counter()
    for r in draw:
        d=r['slot']['document']
        if counts[d]>=3:continue
        selected.append(r);counts[d]+=1
        if len(selected)==36:break
    requests=[]
    for ident in sorted({r['slot']['line_id'] for r in selected}):
        locks.assert_fit_rows([ident]);row=byid[ident];bind(row['crop_source_image']);requests.append(row)
    request=SCRATCH/'n1_cache/n1cc_crop_requests.jsonl';result=SCRATCH/'n1_cache/n1cc_crop_results.json'
    if request.exists():assert rows(request)==requests
    else:write(request,requests,True)
    if not result.exists():
        subprocess.run(['/usr/bin/arch','-arm64',str(COLLECT_PY),'-B',str(ROOT/'scripts/numerics/n1cb_prepare.py'),'--regenerate',str(request),str(result)],check=True)
    cropdata=json.loads(result.read_text());assert not any(r['crop_unavailable'] for r in cropdata['records'])
    crops={r['line_id']:r for r in rows(OUT/'controls/crop_checks_v2.jsonl')+cropdata['records']}
    outputs={}
    comparisons=[]
    def rerender(old):
        locks.assert_fit_rows([old['line_id']])
        crop=crops[old['line_id']];assert sha(crop['crop'])==old['crop_sha256']
        new=render(crop['crop'],old['geometry'],SCRATCH/'n1_cache/rendered_cc')
        new['measurements']=json.loads(json.dumps(new['measurements']))
        if old.get('zoom'):
            assert new['measurements']==old['measurements']
            assert new['line_sha256']==old['line_sha256']
            assert new['zoom_sha256']!=old['zoom_sha256']
            with Image.open(old['zoom']) as before, Image.open(new['zoom']) as after:
                assert after.size==(before.width,before.height+24)
                assert after.crop((0,12,before.width,12+before.height)).tobytes()==before.convert('RGB').tobytes()
            comparisons.append(dict(slot_id=old['slot_id'],measurements_equal=True,line_equal=True,
                                    previous_zoom=old['zoom'],previous_zoom_sha256=old['zoom_sha256'],zoom_interior_equal=True))
        for k in ['line','zoom']:outputs[new[k]]=new[k+'_sha256']
        return dict(old,**new)
    bed=[rerender(r) for r in rows(OUT/'step1_rendered_v2.jsonl')]
    approved=[rerender(r) for r in approved]
    candidates=[]
    for i,p in enumerate(selected,101):
        s=p['slot'];r=dict(slot_id=s['slot_id'],line_id=s['line_id'],document=s['document'],source=s['source'],
            google_glyph=s['glyph'],grammar=s['grammar_candidates'],geometry=p['geometry'],
            google_token=s['google_token'],selection_sources=s['selection_sources'],cell_number=i,
            crop_sha256=byid[s['line_id']]['crop_sha256'],crop_unavailable=False)
        candidates.append(rerender(r))
    paths=[];ccindex=[]
    for i in range(0,len(candidates),12):
        path=sheets/f'n1cc_raised_{i//12+1:02d}.png';assert not path.exists()
        batch=candidates[i:i+12];sheet(batch,path);paths.append(str(path))
        ccindex.extend(dict(sheet=str(path),cell_number=r['cell_number'],slot_id=r['slot_id'],google_glyph=r['google_glyph'],reference_only=False) for r in batch)
    # The seven approved multi-digit empty-gap controls come first.
    sample=sorted(approved,key=lambda r:(r['truth']!='nothing',r['c1_control_only'],r['approval_cell_number']))[:12]
    for r in sample:r['cell_number']=r['approval_cell_number']
    check=sheets/'n1cc_zoom_check.png';assert not check.exists();sheet(sample,check)
    write(sheets/'sheets_index_cc.json',dict(raised=ccindex,zoom_check=[dict(sheet=str(check),cell_number=r['approval_cell_number'],slot_id=r['slot_id'],truth=r['truth']) for r in sample]))
    write(SCRATCH/'n1_cache/n1cc_approved_proposed.jsonl',approved,True)
    products={'step1_rendered_v3.jsonl':bed,
              'controls/raised_candidates_cc.jsonl':candidates,'controls/raised_pool_cc.jsonl':pool,
              'controls/raised_rejected_geometry_cc.jsonl':rejected,
              'controls/crop_checks_cc.jsonl':cropdata['records'],'zoom_measurement_checks_cc.jsonl':comparisons}
    for name,value in products.items():write(OUT/name,value,True);outputs[str(OUT/name)]=sha(OUT/name)
    for p in paths+[str(check),str(sheets/'sheets_index_cc.json'),str(request),str(result)]:outputs[p]=sha(p)
    for p,d in prior.items():assert sha(p)==d,p
    summary=dict(step1=len(bed),controls=len(approved),zoom_rerendered=len(bed)+len(approved),
        new_candidate_zooms=len(candidates),approved_truth_counts=dict(Counter(r['truth'] for r in approved)),
        raised_pool=len(pool),raised_pool_rows=len(eligible_rows),raised_pool_documents=len({r['slot']['document'] for r in pool}),
        raised_geometry_rejected=len(rejected),candidates=len(candidates),candidates_per_document=dict(counts),
        sheets=paths,zoom_check=str(check),measurement_records_reverified=len(comparisons),seed=SEED)
    write(SCRATCH/'n1_cache/n1cc_generation_pending.json',dict(inputs=inputs,outputs=outputs,prior_unchanged=prior,summary=summary,
        c1_document_conflicts=c1_document_conflicts,
        interpreters=dict(renderer=interpreter(),collector=cropdata['interpreter']),
        pool_policy='Union: nonempty inner separators in 4+-digit tokens on ambiguous rows; or Google ·/- grammar-thousands slots in 4+-digit tokens on any W1 elstat/gazette row. Exact geometry ok; step1/reserved documents and all C1 lines excluded.',
        checks=dict(approved_count=True,rejected_cells_excluded=True,document_exclusions=not c1_document_conflicts,c1_controls_only=True,
                    original_zooms_preserved=True,zoom_interiors_identical=True,side_measurements_unchanged=True,
                    prior_artifacts_unchanged=True,network=False,git_writes=False,reader_run=False,packs_built=False,
                    collector_root_writes=False,run_lock_access=False,locked_eval_rendered=False)))
    print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':main()
