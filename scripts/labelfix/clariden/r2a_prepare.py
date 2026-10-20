"""Offline, hash-bound R2a package preparation. Never submits or uses network."""
import json
import gzip
import shutil
from pathlib import Path
from scripts.labelfix.clariden.r1_common import rows, sha256, write_rows, write_json, nfd
from greekocr.labelfix.release_gate import policy_binding

ROOT=Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2a_20261017')
INPUT=Path('artifacts/labelfix_r2a/inputs')
PROJECTS=Path.home()/'Projects'
CARDS=PROJECTS/'greek-ocr-toolkit-spellcheck-r2cards'
S8=PROJECTS/'greek-ocr-toolkit-spellcheck-s8/docs/labelfix/spellcheck/S8_DEV/evidence'
EXPECTED='3dda20644c17b44e1a1c9f69781a9f1dd18657f6dc8b8b7e9cd14d8dd30a7667'


def copy_bound(source, dest, expected=None):
    source=Path(source); dest=Path(dest)
    h=sha256(source)
    if expected and h!=expected: raise ValueError('source hash mismatch: '+str(source))
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists() and sha256(dest)!=h: raise ValueError('existing destination differs: '+str(dest))
    if not dest.exists(): shutil.copyfile(source,dest)
    assert sha256(dest)==h
    return h


def prepare():
    INPUT.mkdir(parents=True,exist_ok=True)
    custody={}
    for rel in ('artifacts/r2a_manifest/r2a_slots.jsonl','artifacts/r2_resolve/T4/final/resolved.jsonl'):
        custody[rel]=copy_bound(CARDS/rel,rel,EXPECTED if rel.endswith('r2a_slots.jsonl') else None)
    manifest=list(rows('artifacts/r2a_manifest/r2a_slots_v2.jsonl'))
    receipt=json.loads(Path('artifacts/r2a_manifest/receipt.json').read_text())
    assert sha256('artifacts/r2a_manifest/r2a_slots_v2.jsonl')==receipt['manifest_v2_sha256']
    assert sha256('artifacts/r2a_manifest/r2a_slots.jsonl')==receipt['manifest_v1_sha256']
    custody['artifacts/r2a_manifest/r2a_slots_v2.jsonl']=receipt['manifest_v2_sha256']
    custody['artifacts/r2a_manifest/receipt.json']=sha256('artifacts/r2a_manifest/receipt.json')
    assert len(manifest)==1572 and not any('replaces' in r or 'removes' in r for r in manifest)
    # Keep original source records as custody inputs. Native byte copies use content addressing.
    keys={}
    for deck in ('T2','T4'):
        p=CARDS/f'docs/labelfix/spellcheck/R2/decks/{deck}/private/key.jsonl'
        copy_bound(p,INPUT/f'{deck}_key.jsonl')
        keys[deck]={r['card_id']:r for r in rows(p)}
    copy_bound(CARDS/'docs/labelfix/spellcheck/R2/doc_roles.json',INPUT/'doc_roles.json')
    copy_bound(CARDS/'docs/labelfix/spellcheck/R2/eligible_lines.jsonl',INPUT/'eligible_lines.jsonl')
    labels={r['id']:r for r in rows(INPUT/'eligible_lines.jsonl')}
    selected={r['line_id']:r for r in manifest}; witness=list(rows('artifacts/r2_resolve/T4/final/resolved.jsonl'))
    assert len(witness)==791
    train_docs={r['doc'] for r in manifest}; witness_docs={keys['T4'][r['card_id']]['doc'] for r in witness}
    assert not train_docs & witness_docs
    def crop(k):
        h=k['crop_sha256']; dest=Path('docs/harvest/r2a/crops')/f'{h}.png'
        source=Path(k['crop'])
        if not source.exists():
            source=CARDS/'docs/labelfix/spellcheck/R2/native_crops'/f'{h}.png'
        if not source.exists():
            source=Path('artifacts/labelfix_r2/population/upload')/f'{h}.png'
        if not source.exists() and k.get('line_id') in labels:
            from PIL import Image
            row=labels[k['line_id']]; dest.parent.mkdir(parents=True,exist_ok=True)
            with Image.open(row['crop_source_image']) as im: im.convert('L').crop(row['crop_bbox']).save(dest,compress_level=3)
            source=dest
        copy_bound(source,dest,h)
        return str(ROOT/dest),str(dest)
    wanted_labels={r['line_id'] for r in manifest}|{keys['T4'][r['card_id']]['line_id'] for r in witness}
    write_rows(INPUT/'eligible_selected.jsonl',[dict(id=lid,label=labels[lid]['label']) for lid in sorted(wanted_labels)])
    cohorts={}; cropfiles=set()
    for name,kk in [('native',[keys['T2'][r['card_id']] for r in manifest]),('witness',[keys['T4'][r['card_id']] for r in witness])]:
        lines={}
        for k in kk:
            image,local=crop(k);cropfiles.add(local)
            lines[k['line_id']]=dict(line_id=k['line_id'],id=k['line_id'],doc=k['doc'],source=selected[k['line_id']]['source'] if name=='native' else k['source'],
                role='train' if name=='native' else 'witness',crop=image,image=image,crop_sha256=k['crop_sha256'],
                recogniser_text=labels[k['line_id']]['label'])
        cohorts[name]=sorted(lines.values(),key=lambda r:r['line_id'])
        write_rows(INPUT/f'{name}.jsonl',cohorts[name])
    # Reuse receipt-bound job-1 recogniser alignments for native overlay identities.
    wanted={r['line_id'] for r in cohorts['native']}; align={}
    run=Path('artifacts/labelfix_r2/output_3681404'); receipt=json.loads((run/'READBACK_RECEIPT.json').read_text())
    bound={r['path']:r['sha256'] for r in receipt['files']}
    for p in sorted((run/'B').glob('*-alignments.jsonl.gz')):
        rr=[r for r in rows(p) if r['line_id'] in wanted]
        if rr:
            assert sha256(p)==bound[str(p.relative_to(run))]
            align.update({r['line_id']:r for r in rr})
    assert set(align)==wanted
    for r in cohorts['native']:
        a=align[r['line_id']]; assert a['crop_sha256']==r['crop_sha256']
        r['recogniser_text']=a['alignment']['prediction']
    write_rows(INPUT/'native.jsonl',cohorts['native'])
    write_rows(INPUT/'native_alignments.jsonl.gz',[dict(crop=r['crop'],alignment=align[r['line_id']]['alignment']) for r in cohorts['native']])
    spec=json.loads(Path('docs/records/labelfix/spellcheck/R2/evidence/job1/DEV_pending.json').read_text())
    copy_bound(S8/'dev_truth.jsonl.gz',INPUT/'dev_truth.jsonl.gz',spec['sha256'])
    copy_bound(S8/'remote.json.gz',INPUT/'dev_saved.json.gz')
    sources=json.loads((S8/'sources.json').read_text()); saved=json.loads(gzip.decompress((S8/'remote.json.gz').read_bytes()))
    dev=[]; da=[]
    for lid in spec['line_ids']:
        s=sources[lid]; text=nfd(saved['runtime'][lid]['recogniser_text']); a=saved['alignments'][lid]['alignment']
        assert text==a['prediction']
        h=sha256(s['original_path']); image,local=crop(dict(crop=s['original_path'],crop_sha256=h));cropfiles.add(local)
        dev.append(dict(id=lid,line_id=lid,doc=s['doc'],source=s['source'],role='witness',crop=image,image=image,crop_sha256=h,recogniser_text=text,wave=s['wave']))
        da.append(dict(crop=image,alignment=a))
    assert len(dev)==600 and sum(r.get('type')=='item' for r in rows(INPUT/'dev_truth.jsonl.gz'))==1793
    write_rows(INPUT/'dev.jsonl',dev);write_rows(INPUT/'dev_alignments.jsonl.gz',da)
    old=json.loads(Path('config/r2_job.json').read_text())
    inv=PROJECTS/'greek-ocr-toolkit-spellcheck/.cache/labelfix/clariden/C1_crop_inventory.jsonl.gz'
    assert sha256(inv)==old['sha256'][old['inventory']]
    inventory=list(rows(inv)); old_hashes={r['sha256'] for r in inventory}
    assert not old_hashes & {r['slot_id'][0] for r in manifest}
    inventory += [dict(crop=r['crop'],sha256=r['crop_sha256']) for r in cohorts['native']]
    write_rows(INPUT/'inventory.jsonl.gz',inventory)
    cfg=dict(schema='r2a-job-v1',mock=False,source_commit='bd8b5b7e5+R2J3-package',policy=policy_binding(),
        data=old['data'],heldout=old['heldout'],teacher=old['teacher'],recognizer=old['recognizer'],
        manifest='artifacts/r2a_manifest/r2a_slots_v2.jsonl',inventory=str(INPUT/'inventory.jsonl.gz'),
        native=str(INPUT/'native.jsonl'),native_alignments=str(INPUT/'native_alignments.jsonl.gz'),
        witness=str(INPUT/'witness.jsonl'),witness_key=str(INPUT/'T4_key.jsonl'),witness_truth='artifacts/r2_resolve/T4/final/resolved.jsonl',
        roles=str(INPUT/'doc_roles.json'),eligible=str(INPUT/'eligible_selected.jsonl'),dev=str(INPUT/'dev.jsonl'),dev_alignments=str(INPUT/'dev_alignments.jsonl.gz'),dev_truth=str(INPUT/'dev_truth.jsonl.gz'),
        heldout_truth='docs/records/labelfix/spellcheck/S4_lines.jsonl.gz',overlay='docs/records/labelfix/spellcheck/R2/truth_overlay_v1_1.json',
        checkpoints={'A16':dict(path=old['teacher'],sha256=old['sha256'][old['teacher']]),**{'BASE'+k: v for k,v in spec['proposed_job']['checkpoints'].items()}},
        readiness=dict(native_width_decision_pending=False,slot_id=['82e8f64cbca6e513163d4452641a51a215a0e744b8c4a338a6dc0fdf7ec740e8',46],reason='frozen_extractor_width_gate: slot quarantined; no exception'),
        coordinator_accepted_deviation=receipt['coordinator_accepted_deviation'],
        seeds=[20261016,20261017,20261018],expected_slots=1572,expected_dev_lines=600,expected_dev_items=1793,
        forecast=dict(native_minutes=15.9,training_minutes=17.5,inference_scoring_minutes=20,total_minutes=53.4,requested_minutes=81))
    cfg['sha256']={p:old['sha256'][p] for p in (old['teacher'],old['recognizer'])}
    for p,v in cfg['checkpoints'].items():cfg['sha256'][v['path']]=v['sha256']
    for field in ('native','native_alignments','witness','witness_key','witness_truth','eligible','roles','dev','dev_alignments','dev_truth','heldout_truth','overlay','manifest','inventory'):
        cfg['sha256'][cfg[field]]=sha256(cfg[field])
    for path in ('data','heldout'):
        p=str(Path(cfg[path])/'extraction_receipt.json');cfg['sha256'][p]=old['sha256'][p]
    write_json('config/r2a_job.json',cfg)
    write_json(INPUT/'custody.json',dict(source_manifest=custody,manifest_v1_sha256=receipt['manifest_v1_sha256'],manifest_v2_sha256=receipt['manifest_v2_sha256'],coordinator_accepted_deviation=receipt['coordinator_accepted_deviation'],training_slots=len(manifest),witness_cards=len(witness),
        native_lines=len(cohorts['native']),witness_lines=len(cohorts['witness']),dev_lines=600,dev_items=1793,crop_files=len(cropfiles),
        crop_bytes=sum(Path(p).stat().st_size for p in cropfiles),old_inventory_sha256=sha256(inv),old_crop_overlap=0))
    print(json.dumps(json.loads((INPUT/'custody.json').read_text())))

if __name__=='__main__':prepare()
