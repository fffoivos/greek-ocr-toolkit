"""Bind R2C and Addendum A saved populations; no inference or submission."""
import io
import json
import re
import shutil
from collections import Counter
from pathlib import Path
from PIL import Image
from scripts.labelfix.clariden.r1_common import rows, sha256, write_rows, write_json, document_split

PROJECTS=Path.home()/'Projects'
HERE=Path.cwd()
CARDS=PROJECTS/'greek-ocr-toolkit-spellcheck-r2cards/docs/labelfix/spellcheck/R2'
S8=PROJECTS/'greek-ocr-toolkit-spellcheck-s8'
HARVEST=PROJECTS/'greek-ocr-toolkit'
REMOTE='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3'
OUT=Path('artifacts/labelfix_r2/population')

def alias(d):return d.split(':')[-1]
def line_doc(i):return re.split(r'--n\d+|-p\d+|-l\d+',i)[0]

def build():
    OUT.mkdir(parents=True,exist_ok=True)
    roles=json.loads((CARDS/'doc_roles.json').read_text())
    # Verify all inputs bound by R2C before reusing its exclusions.
    for p,h in roles['input_sha256'].items():
        if sha256(p)!=h:raise ValueError('R2C input changed: '+p)
    c1=list(rows(roles['c1_selection_fallback']));c1ids={r['id'] for r in c1};c1docs={alias(r['doc']) for r in c1}
    val={alias(d) for d in document_split(c1)['validation']}
    train=list(rows(HARVEST/'docs/harvest/collection/v2/import_real_v2_train.jsonl'))
    allrows=train+list(rows(HARVEST/'docs/harvest/collection/v2/import_real_v2_dev.jsonl'))+list(rows(HARVEST/'docs/harvest/collection/v2/import_real_v2_test.jsonl'))
    lookup={r['id']:alias(r['doc']) for r in allrows}
    ids={}
    ids['C1_validation']={r['id'] for r in train if alias(r['doc']) in val}
    ids['S8_DEV']=set((S8/'docs/labelfix/spellcheck/S8_DEV/S8_DEV_ids.txt').read_text().split())
    ids['audit100']={r['line_id'] for r in rows(S8/'docs/labelfix/spellcheck/clariden/L1R3_evidence/production_3680729_3680730/audit100_ids.jsonl')}
    ids['heldout666']={r['line_id'][:-6] for r in rows(PROJECTS/'greek-page-ocr/out/e3b/predictions/full_s0_wikisource_human.jsonl') if r['source_dataset']=='wikisource_el'}
    ex=PROJECTS/'greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_exclusions'
    release=json.loads((ex/'release_exclusions.json').read_text());books={}
    for name,spec in release['classes'].items():
        p=ex/spec['file']
        if not p.exists():p=next(q for q in ex.glob('*.txt') if sha256(q)==spec['sha256'])
        assert sha256(p)==spec['sha256']
        ids['release_'+name]=set(p.read_text().split());books['release_'+name]=set(spec.get('books',[]))
    docs={k:{lookup.get(i,line_doc(i)) for i in v}|books.get(k,set()) for k,v in ids.items()}
    candidates=[r for r in train if r['script_class']=='greek_poly' and alias(r['doc']) in c1docs and r['id'] not in c1ids]
    assert len(candidates)==33198
    exclusion=[]
    for name,values in ids.items():
        before=len(candidates)
        line_only=name in ('release_separator_ambiguous','release_rotated_crop')
        candidates=[r for r in candidates if r['id'] not in values and (line_only or alias(r['doc']) not in docs[name])]
        exclusion.append(dict(rule=name,excluded=before-len(candidates),remaining=len(candidates),documents=len({r['doc'] for r in candidates})))
    rolemap={'supervision':'train','validation':'validation_reserve','witness':'witness','calibration':'calibration'}
    eligible=list(rows(CARDS/'eligible_lines.jsonl'))
    population=[];local=[];binding={}
    for r in eligible+[dict(r,pool='v2',document=r['doc'],teacher_seen_document=True) for r in candidates]:
        seen=r.get('teacher_seen_document',False);d=r['document']
        source=r['source'] if r['pool']=='W1' else r['wave']+':'+r['source']
        role='train' if seen else rolemap[roles['documents'][d]['role']]
        binding.setdefault(d,dict(eligible=True,source=source,role=role,teacher_seen_document=seen))
        assert binding[d]['role']==role
        p=Path(r['crop']) if r['pool']=='W1' else HARVEST/r['crop']
        if r['pool']=='W1':
            h=r['crop_sha256']
            if not p.exists():p=CARDS/'native_crops'/(h+'.png')
            if not p.exists():
                p=OUT/'recreated'/(h+'.png');p.parent.mkdir(exist_ok=True)
                with Image.open(r['crop_source_image']) as im:im.convert('L').crop(r['crop_bbox']).save(p,compress_level=3)
            assert sha256(p)==h
            remote=f'{REMOTE}/labelfix_r2_20261017/crops/{h}.png'
        else:
            h=sha256(p);remote=None
        rr=dict(line_id=r['id'],doc=d,source=source,role=role,image=remote,crop=r['crop'],crop_sha256=h,teacher_seen_document=seen,population_source=r['pool'])
        population.append(rr);local.append(dict(line_id=r['id'],local=str(p),sha256=h,crop=r['crop'],pool=r['pool']))
    assert len({r['line_id'] for r in population})==len(population)
    write_rows(OUT/'population_unstaged.jsonl',population);write_rows(OUT/'local_crops.jsonl',local)
    rb=dict(documents=binding,eligible_line_ids=[r['line_id'] for r in population],excluded_documents=sorted(set.union(*(v for k,v in docs.items() if k not in ('release_separator_ambiguous','release_rotated_crop')))),excluded_lines=sorted(set.union(*ids.values())),r2c_sha256=sha256(CARDS/'doc_roles.json'))
    write_json(OUT/'roles.json',rb)
    report=dict(lines=len(population),roles=dict(Counter(r['role'] for r in population)),source_role=dict(Counter(r['population_source']+'/'+r['source']+'/'+r['role'] for r in population)),teacher_seen=sum(r['teacher_seen_document'] for r in population),teacher_seen_initial=33198,teacher_seen_exclusions=exclusion)
    write_json(OUT/'counts.json',report);print(json.dumps(report,indent=2))

if __name__=='__main__':build()
