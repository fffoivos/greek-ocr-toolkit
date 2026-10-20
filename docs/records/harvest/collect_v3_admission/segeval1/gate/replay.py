"""Offline SEG-GATE-1: fresh crop passes, saved 0.5/0.6 comparisons and ratings."""
from collections import Counter
import gzip
import hashlib
import json
import os
from pathlib import Path
import signal
import sys
import time

D = Path(__file__).resolve().parent
DRAW = D.parent
ROOT = D.parents[4]
sys.path.insert(0,str(ROOT))
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',PYTHONDONTWRITEBYTECODE='1')
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[key] = '1'


def offline(event,args):
    if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo'):
        raise RuntimeError('network OFF: SEG-GATE-1')


sys.addaudithook(offline)
from greekocr.harvest.line_pipeline_native import NativeSegmenter, character_count


def load(path,key):
    values = [json.loads(s) for s in path.read_text().splitlines() if s.strip()]
    result = {r[key]:r for r in values}
    assert len(result) == len(values)
    return result


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


FAULT_FLAGS = ('multi_line','neighbour_whole_word','rotated','horizontally_missegmented')
FAULT_CODES = {'extra_text','missing_word_or_span','crop_clipped','merged_two_lines'}


def owner_state(owner):
    answer = owner.get('reader_answer') or {}
    faults = [k for k in FAULT_FLAGS if answer.get(k) == 'yes'] + sorted(FAULT_CODES & set(answer.get('errors',[])))
    if faults:
        return 'faulty',faults
    if any(answer.get(k) != 'no' for k in FAULT_FLAGS) or not isinstance(answer.get('errors'),list):
        return 'unresolved',[]
    return 'fine',[]


def confusion(records,version):
    return {v:{s:sum(r['verdict_'+version]==v and r['owner_standard_state']==s for r in records)
               for s in ('fine','faulty','unresolved')} for v in ('DROP','KEEP','UNCERTAIN')}


def context_pair(record):
    e = record['after']['evidence']; n = e.get('neighbour_evidence') or {}
    if not isinstance(n.get('whole_neighbour_words'),(int,float)):
        return None
    g = e['gate']
    return dict(line_id=record['line_id'],status=n['status'],resolved=n.get('whole_word_count_resolved'),
        crop_whole=g['whole_words'],context_whole=n['whole_neighbour_words'],
        crop_cutoff=g['cutoff_words'],context_cutoff=n.get('partial_neighbour_words'),
        crop_complete=len(g['complete_rows']),context_complete=n.get('additional_full_line_count'),
        whole_agrees=g['whole_words']==n['whole_neighbour_words'],
        cutoff_agrees=g['cutoff_words']==n.get('partial_neighbour_words'),
        complete_agrees=len(g['complete_rows'])==n.get('additional_full_line_count'))


def summarize(records,failures,elapsed,cohort,sources):
    flips = []
    pairs = []
    for r in records:
        e = r['after']['evidence']; g = e['gate']
        if r['verdict_06'] != r['verdict_07']:
            flips.append(dict(line_id=r['line_id'],verdict_06=r['verdict_06'],verdict_07=r['verdict_07'],
                reason_06=r['before']['reason'],reason_07=r['after']['reason'],gate_reason=g['reason'],
                whole_words=g['whole_words'],cutoff_words=g['cutoff_words'],complete_rows=g['complete_rows'],
                main_cut=g['main_cut'],reader_state=r.get('reader_state'),
                owner_standard_state=r.get('owner_standard_state'),owner_faults=r.get('owner_faults'),
                reader_answer=r.get('reader_answer'),owner_rating=r.get('owner_rating')))
        pair = context_pair(r)
        if pair: pairs.append(pair)
    write_jsonl(D/f'flips_{cohort}.jsonl',flips)
    write_jsonl(D/f'context_pairs_{cohort}.jsonl',pairs)
    comparisons = []
    for r in records:
        a,b = r['after']['evidence'],r['before']['evidence']
        if a['gate']['verdict'] == 'PASS':
            comparisons.append(dict(line_id=r['line_id'],
                box_exact=a['box_evidence']==b['box_evidence'],padding_exact=a['padding_evidence']==b['padding_evidence']))
    summary = dict(rows=len(records),failures=failures,elapsed_seconds=elapsed,flip_count=len(flips),
        transitions=dict(Counter(r['verdict_06']+'->'+r['verdict_07'] for r in records)),
        gate_reasons=dict(Counter(r['after']['evidence']['gate']['reason'] for r in records)),
        stage_b_comparisons=comparisons,stage_b_exact=sum(r['box_exact'] and r['padding_exact'] for r in comparisons),
        context_pairs=len(pairs),context_resolved_pairs=sum(p['resolved'] is True for p in pairs),
        context_whole_agree=sum(p['whole_agrees'] for p in pairs),
        context_resolved_whole_agree=sum(p['whole_agrees'] and p['resolved'] is True for p in pairs),
        context_cutoff_agree=sum(p['cutoff_agrees'] for p in pairs),
        context_complete_agree=sum(p['complete_agrees'] for p in pairs),
        context_unavailable=sum(bool(r['after']['evidence'].get('neighbour_evidence')) and context_pair(r) is None for r in records),
        source_sha256={str(p):sha(p) for p in sources},policy_sha256=records[0]['after']['policy_sha256'])
    if cohort == 'segeval1':
        summary['confusion'] = {v:confusion(records,v) for v in ('05','06','07')}
        summary['owner_standard_states'] = dict(Counter(r['owner_standard_state'] for r in records))
        summary['errors'] = {v:dict(FP=summary['confusion'][v]['DROP']['fine'],FN=summary['confusion'][v]['KEEP']['faulty'],
                                  UNC=sum(summary['confusion'][v]['UNCERTAIN'].values())) for v in ('05','06','07')}
        summary['original_50_rejects'] = {v:dict(FP=sum(r['verdict_05']=='DROP' and r['verdict_'+v]=='DROP' and r['owner_standard_state']=='fine' for r in records)) for v in ('05','06','07')}
    else:
        rated = [r for r in records if r.get('owner_rating') and r['owner_rating'].get('decision') in ('KEEP','DROP')]
        summary['owner_rated'] = len(rated)
        summary['owner_ratings'] = dict(Counter(r['owner_rating']['decision'] for r in rated))
        summary['rating_agreement'] = {v:dict(agree=sum(r['verdict_'+v]==r['owner_rating']['decision'] for r in rated),
            FP=sum(r['verdict_'+v]=='DROP' and r['owner_rating']['decision']=='KEEP' for r in rated),
            FN=sum(r['verdict_'+v]=='KEEP' and r['owner_rating']['decision']=='DROP' for r in rated),
            UNC=sum(r['verdict_'+v]=='UNCERTAIN' for r in rated)) for v in ('06','07')}
        summary['rated_flips'] = sum(f['owner_rating'] is not None for f in flips)
    (D/f'summary_{cohort}.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('source_sha256','stage_b_comparisons')},ensure_ascii=False,indent=2),flush=True)
    assert all(r['box_exact'] and r['padding_exact'] for r in comparisons), 'Stage-B drift from 0.6'
    assert not failures


def write_jsonl(path,rows):
    path.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True,allow_nan=False)+'\n' for r in rows))


def timeout(signum,frame):
    raise TimeoutError('native row exceeded 120 seconds')


def run(cohort):
    versions_path = ROOT/'docs/harvest/line_pipeline/tool_versions.json'
    versions = json.loads(versions_path.read_text())['tools']
    predictor = ROOT/'scripts/harvest/filter_runtime/target/debug/greekocr-frozen-font-predict'
    worker = NativeSegmenter(versions,predictor)
    before_path = DRAW/f'deskew/replay_{cohort}.jsonl'
    before = load(before_path,'line_id')
    sources = [before_path,versions_path,predictor]
    if cohort == 'segeval1':
        paths = [DRAW/'keys/selected_features.jsonl',DRAW/'keys/sealed_decisions.jsonl',DRAW/'scored/owner_rows.jsonl']
        features,sealed,owner = [load(p,k) for p,k in zip(paths,['row_id','row_id','line_id'])]
        sources += paths
        assert len(before)==150 and before.keys()==features.keys()==sealed.keys()==owner.keys()
        inputs = []
        for rid,b in before.items():
            s = sealed[rid]
            row = dict(features[rid],**s['segmentation']['binding'],raw_text=s['google_text'],crop_path=str(DRAW/'crops'/f'{rid}.png'))
            state,faults = owner_state(owner[rid])
            inputs.append((rid,row,dict(verdict_05=s['segmentation']['verdict'],reader_state=owner[rid]['reader_state'],
                reader_answer=owner[rid]['reader_answer'],owner_standard_state=state,owner_faults=faults,sealed_decision=s['decision'])))
    else:
        site = ROOT.parent/'ocr-review-sites-20261018'
        paths = [site/'review-data/box-length-experiment.json',site/'review-data/font-normalized/predicted-rows.json.gz',
                 site/'qa/word-tolerance/context-evidence.json',site/'review-data/population.json']
        report = json.loads(paths[0].read_text())['rows']
        natives = {r['id']:r for r in json.loads(gzip.decompress(paths[1].read_bytes()))}
        contexts = {r['id']:r for r in json.loads(paths[2].read_text())['rows']}
        pop = json.loads(paths[3].read_text()); chunks = {}
        sources += paths
        worker.context = lambda row,*args:contexts.get(row['id'],dict(status='unavailable',reason='no saved calibration source context'))
        inputs = []
        for old in report:
            rid = old['id']; meta = natives[rid]
            if meta.get('google_text') is None or 'content_class' not in meta:
                chunk = old['index']//pop['detail_chunk_size']
                path = site/f'population-data/details/{chunk:05d}.json.gz'
                if chunk not in chunks:
                    chunks[chunk] = json.loads(gzip.decompress(path.read_bytes())); sources.append(path)
                detail = chunks[chunk][old['index']%pop['detail_chunk_size']]
                assert detail[0]==rid and detail[4]==old['image_sha256']
                codes = dict(part.split(':') for part in detail[8].split('|'))
                meta['google_text'] = detail[2];meta['content_class'] = pop['codebooks']['classes'][int(codes['class'])]
            assert character_count(meta['google_text']) == old['characters']
            row = dict(id=rid,parent_id='accepted-calibration-888',split='unassigned',crop_sha256=old['image_sha256'],
                crop_path=str(site/'population-images'/(old['image_sha256']+'.png')),raw_text=meta['google_text'],
                script_class=old['script'],primary_class=meta['content_class'])
            inputs.append((rid,row,dict(owner_rating=old['owner_rating'],index=old['index'],
                context_source='frozen saved raw source-context observations; crop detection fresh')))
        assert len(inputs)==888 and {r[0] for r in inputs}==before.keys()
    failures=[]; records=[]; started=time.monotonic()
    signal.signal(signal.SIGALRM,timeout)
    try:
        with (D/f'replay_{cohort}.jsonl').open('w') as output:
            for i,(rid,row,metadata) in enumerate(inputs,1):
                b = before[rid]['after']
                try:
                    signal.alarm(120)
                    after = worker(row)
                    assert after['tool_version']=='0.7' and after['policy_sha256']==worker.policy_sha
                    assert after['binding']==b['binding'] and after['raw_text_sha256']==b['raw_text_sha256']
                except Exception as exc:
                    failures.append(dict(line_id=rid,type=type(exc).__name__,error=str(exc)));print(json.dumps(failures[-1]),flush=True);continue
                finally:signal.alarm(0)
                record = dict(line_id=rid,before=b,after=after,verdict_06=b['verdict'],verdict_07=after['verdict'],**metadata)
                records.append(record)
                output.write(json.dumps(record,ensure_ascii=False,sort_keys=True,allow_nan=False)+'\n');output.flush()
                if i%25==0:print(f'{cohort} {i}/{len(inputs)} measured',flush=True)
    finally:worker.close()
    summarize(records,failures,time.monotonic()-started,cohort,sources)
    assert len(records)==len(inputs)


if __name__=='__main__':
    assert sys.argv[1] in ('segeval1','calibration')
    run(sys.argv[1])
