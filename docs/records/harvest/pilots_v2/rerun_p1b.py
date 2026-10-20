"""Offline P1b rerun. Only cached pages, reads and detector outputs are opened.

P1 artifacts remain immutable. This runner does not import a provider client or
invoke acquisition/read scripts. Execute from any directory with the P1 Python.
"""
import gzip
import json
import pathlib
from collections import Counter, defaultdict
import align
from pilotlib import BASE, rows, sha, write
from p1b_align import EDGES, margin_numerals, token_text, token_bbox

DEST=BASE/'p1b'


def jsonl(path, records):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(''.join(json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n' for r in records))


def summarize(records,pages):
    out={}
    for source in ['wikisource','perseus','gutenberg']:
        pp=[p for p in pages if p['pilot']==source]; rr=[r for r in records if r['pilot']==source]
        accepted=[r for r in rr if r['accepted']];target=[r for r in rr if r['accepted_for_target_reference']]
        source_chars=sum(p['proofread_nfd_characters'] for p in pp); google_chars=sum(p['google_nfd_characters'] for p in pp)
        kept=sum(r['source_span_nfd'][1]-r['source_span_nfd'][0] for r in accepted)
        target_chars=sum(r['source_span_nfd'][1]-r['source_span_nfd'][0] for r in target)
        label_chars=sum(len(align.normal(r['human_label'])) for r in target)
        out[source]=dict(pages=len(pp),provider_lines=len(rr),all_language_labels=len(accepted),target_labels=len(target),
            labels_per_page=len(target)/len(pp),all_labels_per_page=len(accepted)/len(pp),
            retained_source_nfd_characters=kept,target_retained_source_nfd_characters=target_chars,target_label_nfd_characters=label_chars,
            proofread_body_nfd_characters=source_chars,all_page_ocr_nfd_characters=google_chars,
            body_coverage_pct=100*kept/source_chars,target_page_ocr_coverage_pct=100*target_chars/google_chars,
            zero_target_pages=sum(not any(r['accepted_for_target_reference'] and r['page_id']==p['page_id'] for r in rr) for p in pp),
            rejection_reasons=dict(Counter(x for r in rr for x in r['reasons'])))
    return out


def main():
    baseline=json.loads((DEST/'baseline.json').read_text())
    for rel,digest in baseline['sha256'].items():assert sha(BASE/rel)==digest,('P1 baseline drift',rel)
    before=rows(BASE/'bulk/alignment.jsonl'); before_pages=rows(BASE/'alignment_pages.jsonl'); expected={p['page_id'] for p in before_pages}
    output=[]; pages=[]; cache={};inputs=[]
    for pid in sorted(expected):
        page=json.loads((BASE/'receipts/pages'/f'{pid}.json').read_text())
        assert not page.get('excluded')
        lines=rows(BASE/'bulk/lines'/f'{pid}.jsonl');assert lines
        parsed=BASE/'google/parsed/docai'/(page['image_sha256']+'.json')
        raw=pathlib.Path(json.loads(parsed.read_text())['raw_json_path'])
        document=json.loads(raw.read_text())['document']
        inputs.append(dict(page_id=pid,image=page['image'],image_sha256=sha(BASE/page['image']),raw_read_path=str(raw),raw_read_sha256=sha(raw),lines_sha256=sha(BASE/'bulk/lines'/f'{pid}.jsonl')))
        assert inputs[-1]['image_sha256']==page['image_sha256']
        tokens=[dict(text=token_text(document,t),bbox=token_bbox(t,page['width'],page['height'])) for t in document['pages'][0].get('tokens',[])]
        if page['pilot']=='perseus':
            for line in lines:line['margin_numerals']=margin_numerals(line,tokens)
        proof=align.prepare(page,cache)
        aligned,summary=align.align_page(page,lines,proof)
        summary['provider_line_nfd_characters']=summary['google_nfd_characters']
        summary['google_nfd_characters']=len(align.normal(document.get('text','')))
        old_page=next(p for p in before_pages if p['page_id']==pid)
        summary.update(layout=old_page['layout'],regime=old_page['regime'])
        summary['target_retained_lines']=sum(r['accepted_for_target_reference'] for r in aligned)
        summary['target_retained_nfd_characters']=sum(r['source_span_nfd'][1]-r['source_span_nfd'][0] for r in aligned if r['accepted_for_target_reference'])
        # Keep the derivation needed to reproduce source ownership, including cross-page context.
        write(DEST/'proofread'/(pid+'.json'),proof)
        output.extend(aligned);pages.append(summary)
        print(pid,sum(r['accepted'] for r in aligned),flush=True)
    assert {r['id'] for r in output}=={r['id'] for r in before}
    assert Counter(p['pilot'] for p in pages)==dict(wikisource=50,perseus=50,gutenberg=50)
    old={r['id']:r for r in before}
    for r in output:
        r['before_candidate_text']=old[r['id']]['candidate_text'];r['before_accepted']=old[r['id']]['accepted']
        r['text_changed']=(r['candidate_text'] or r['google_text'])!=(old[r['id']]['candidate_text'] or old[r['id']]['google_text'])
    signatures=Counter((e['google_text'],e['label_text']) for r in output if r['pilot']=='wikisource' for e in r['alignment_edits'] if any(align.p1b_align.wordchar(c) for c in e['google_text']+e['label_text']))
    for r in output:
        if r['disagrees_with_page_read']:
            r['disagreement_evidence']=dict(role='owner/ink triage; reader disagreement does not establish print truth',
                repeated_edit_signatures=[dict(google=a,label=b,occurrences=signatures[(a,b)]) for a,b in {(e['google_text'],e['label_text']) for e in r['alignment_edits']} if signatures[(a,b)]>=2],
                expanded_hyphenation='expanded_hyphenation_disagreement' in r['flags'])
    jsonl(DEST/'alignment.jsonl',output)
    jsonl(DEST/'alignment_pages.jsonl',pages)
    jsonl(DEST/'cached_inputs.jsonl',inputs)
    counts=dict(edge_fixed=sum(any(any(c in EDGES for c in e['text']) and not ((old[r['id']]['candidate_text'] or '').startswith(e['text']) if e['side']=='left' else (old[r['id']]['candidate_text'] or '').endswith(e['text'])) for e in r['edge_glyph_ownership']) for r in output),
        ou_fixed=sum('ȣ' in (r['candidate_text'] or '') and '??' in (old[r['id']]['candidate_text'] or '') for r in output),
        margin_withheld=sum('margin_numeral_in_crop' in r['reasons'] for r in output),
        disagree_flags=sum(r['accepted'] and r['disagrees_with_page_read'] for r in output),
        disagree_candidates=sum(r['disagrees_with_page_read'] for r in output),
        changed_text_regions=sum(r['text_changed'] for r in output))
    for rel,digest in baseline['sha256'].items():assert sha(BASE/rel)==digest,('baseline changed during rerun',rel)
    summary=dict(before=summarize(before,before_pages),after=summarize(output,pages),counts=counts,
        alignment_sha256=sha(DEST/'alignment.jsonl'),method_sha256=sha(BASE/'p1b_align.py'),tei_parser_sha256=sha(BASE/'align.py'),
        pages=150,new_google_calls=0,new_spend_usd=0,released_reference_lines=0,
        release_gate='second blind adjudication pending; flags do not veto otherwise eligible proposals',
        coverage_contract='same 150 pages; retained source NFD spans / full cached page OCR NFD characters; literal rendered label NFD characters separately counted')
    write(DEST/'summary.json',summary)
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':main()
