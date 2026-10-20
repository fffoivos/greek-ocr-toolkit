"""Apply recorded RU1 lead rulings and build an offline, parent-bound label version.
Uses only saved RU1 pixels/geometry and the read-only W1 features file; no readers.
"""
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from ru1_owner_sheet import google_offset
from reading.common import ROOT, WORK, PROJECTS, PACK_ROOT, SCRATCH, rows, dump, jsonl, sha

LEAD = WORK/'docs/records/labelfix/secondary/RU1_LEAD_REVIEW.md'
LEAD_REF = str(LEAD.relative_to(WORK))
SEED = '20261017:RU12:owner'
FEATURES = PROJECTS/'collect-v3-data/run/W1/features.jsonl'
LEAD_DIR = SCRATCH/'ru1_review/lead'


def rulings(decisions, cells):
    lookup = {(d['row_id'], d['offset']): d for d in decisions}
    assert len(lookup) == len(decisions)
    assert sorted(c['cell'] for c in cells) == list(range(1, 68))
    for c in cells:
        d = lookup[c['row_id'], c['offset']]
        ref = dict(reference=LEAD_REF, cell=c['cell'])
        if c['cell'] <= 27:
            decision = {9:'hold_uncertain',17:'hold_yat',23:'keep_soft',27:'hold_yat'}.get(c['cell'], 'edit_hard')
            assert c['set'] == 'review' and c['decision'] == 'lead_review'
            assert d['decision'] in {'lead_review', decision}
            d.setdefault('decision_before_lead', d['decision'])
            d['decision'] = decision
            d['lead_ruling'] = dict(ref, decision=decision)
        else:
            assert c['set'] == 'audit' and d['decision'] == c['decision']
            d['lead_audit_confirmed'] = dict(ref, decision=d['decision'])
    assert all(d['decision'] != 'lead_review' for d in decisions)
    return decisions


def version(w1, decisions, bed):
    candidates = {(m['row_id'], s['offset']) for m in bed if not m['control']
                  for s in m['slots'] if s['google']=='ь' and s['kind']=='final'}
    lookup = {(d['row_id'],d['offset']):d for d in decisions}
    assert set(lookup) == candidates
    grouped = defaultdict(list)
    for lid, off in candidates: grouped[lid].append(lookup[lid,off])
    out = []
    for lid, ds in sorted(grouped.items()):
        r = w1[lid]
        assert r['source'] == 'ia_russian'
        parent = r['label']; chars = list(parent); edits=[]; holds=[]
        for d in sorted(ds,key=lambda d:d['offset']):
            off=d['offset']
            assert parent[off]=='ь' and google_offset(parent,r['text'],off) is not None
            if d['decision']=='edit_hard':
                chars[off]='ъ'
                edits.append(dict(offset=off, **{'from':'ь','to':'ъ'}, basis='lead_ruling' if 'lead_ruling' in d else 'two_reads'))
            elif d['decision'].startswith('hold_'):
                holds.append(dict(offset=off,reason=d['decision']))
            else: assert d['decision']=='keep_soft'
        out.append(dict(id=lid,label_parent=parent,label_ru1_v1=''.join(chars),edits=edits,holds=holds,status='hold' if holds else 'ok'))
    return out


def word_segments(text, offset):
    a,b=offset,offset+1
    while a and text[a-1].isalpha(): a-=1
    while b<len(text) and text[b].isalpha(): b+=1
    return [dict(text=text[:a]),dict(text=text[a:b],kind='changed'),dict(text=text[b:])]


def build():
    from greekocr.adjudicate import owner_sheet
    renderer=PROJECTS/'greek-ocr-toolkit-cleanup/greekocr/adjudicate/owner_sheet.py'
    assert Path(owner_sheet.__file__).resolve()==renderer
    inputs={}
    def bind(p):
        p=Path(p);inputs[str(p.resolve())]=sha(p);return p
    for p in [Path(__file__),Path(__file__).with_name('ru1_owner_sheet.py'),Path(__file__).parent/'reading/common.py',LEAD,FEATURES,renderer,renderer.with_suffix('.css'),renderer.with_suffix('.js')]: bind(p)
    for original,snapshot in [('decisions.jsonl','decisions.pre_ru1_v1.jsonl'),('decisions.summary.json','decisions.summary.pre_ru1_v1.json'),('owner_sheet/summary.json','owner_sheet/summary_RU1F.json')]:
        dest=ROOT/snapshot
        if not dest.exists(): dest.write_bytes((ROOT/original).read_bytes())
        bind(dest)
    cells=json.loads(bind(LEAD_DIR/'sheets_index.json').read_text())['items']
    refs=json.loads(bind(LEAD_DIR/'references.json').read_text())
    decisions=rulings(rows(ROOT/'decisions.pre_ru1_v1.jsonl'),cells)
    bed=[]; location={}
    for n in range(1,5):
        ctx=f'ctx{n:02}'
        key=json.loads(bind(ROOT/f'keys/{ctx}.json').read_text())
        items={i['item_id']:i for i in rows(bind(PACK_ROOT/ctx/'r1/items.jsonl'))}
        for iid,m in key['items'].items():
            bed.append(m)
            if not m['control']:location[m['row_id']]=(ctx,items[iid],m)
    w1={r['id']:r for r in rows(FEATURES) if r['source']=='ia_russian'}
    labels=version(w1,decisions,bed)
    jsonl(ROOT/'decisions.jsonl',decisions); bind(ROOT/'decisions.jsonl')
    decision_summary=json.loads((ROOT/'decisions.summary.pre_ru1_v1.json').read_text())
    decision_summary.update(stage='RU1-2',counts=dict(Counter(d['decision'] for d in decisions)),
        lead_review_reasons={},lead_review_resolved=27,lead_audit_confirmed=40,
        prior_disagreement_policy='withdrawn as a review trigger by the lead',lead_reference=LEAD_REF)
    dump(ROOT/'decisions.summary.json',decision_summary)
    jsonl(ROOT/'ru1_v1.jsonl',labels)
    manifest=dict(schema='ru1_v1',rows=len(labels),row_counts=dict(Counter(r['status'] for r in labels)),
        edit_counts_by_basis=dict(Counter(e['basis'] for r in labels for e in r['edits'])),
        decision_counts=dict(Counter(d['decision'] for d in decisions)),
        sha256=sha(ROOT/'ru1_v1.jsonl'),offset_unit='Python Unicode code point index in label_parent',
        excluded_controls=[dict(source_id=m['source_id'],row_id=m['row_id'],w1_id=m['w1_id'],label_action='keep label',reason='bed control') for m in bed if m['control']])
    geom=json.loads((ROOT/'owner_sheet/summary_RU1F.json').read_text())['geometry']
    geometry={(g['line_id'],g['label_offset']):g for g in geom}
    geometry.update({(c['row_id'],c['offset']):c['geometry'] for c in cells})
    pool=sorted([d for d in decisions if d['decision']=='edit_hard'],key=lambda d:(d['row_id'],d['offset']))
    selected=random.Random(SEED).sample(pool,12)
    held=sorted([d for d in decisions if d['decision'].startswith('hold_')],key=lambda d:(d['row_id'],d['offset']))
    assert len(held)==3 and len({d['row_id'] for d in held})==3
    labelmap={r['id']:r for r in labels}; cards=[]; cardmeta=[]
    font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',20)
    for d in selected+held:
        lid=d['row_id'];off=d['offset'];ctx,item,meta=location[lid];g=geometry[lid,off]
        path=bind(PACK_ROOT/ctx/'r1'/item['crop'])
        assert sha(path)==meta['source_crop_sha256']==w1[lid]['crop_sha256']
        with Image.open(path) as im: image=im.convert('RGB')
        final=image.crop(g['final_box']);final=final.resize((final.width*8,final.height*8),Image.Resampling.NEAREST)
        triplet=[]
        for sign in ['ъ','ь']:
            ref=refs[meta['book']][sign]
            with Image.open(bind(ref['path'])) as im: triplet.append(im.convert('RGB'))
        imgs=[triplet[0],final,triplet[1]]
        widths=[max(im.width+24,280) for im in imgs]
        panel=Image.new('RGB',(sum(widths),max(im.height for im in imgs)+90),'white');draw=ImageDraw.Draw(panel);x=0
        for caption,im,width in zip(['hard sign ъ, flag','this letter, 8×','soft sign ь, no flag'],imgs,widths):
            draw.text((x+8,8),caption,font=font,fill='black');panel.paste(im,(x+(width-im.width)//2,42));x+=width
        word=image.crop(g['word_box']);word=word.resize((word.width*3,word.height*3),Image.Resampling.NEAREST)
        goff=google_offset(w1[lid]['label'],w1[lid]['text'],off);assert goff==g['google_offset']
        group='held' if d in held else 'edit'
        cards.append(dict(line_id=lid,slot=off,label=lid,image=panel,alt='hard sign ъ, flag | this letter, 8× | soft sign ь, no flag',
            zooms=[dict(image=word,alt='word crop')],group=group,
            rows=[dict(name='Google',segments=word_segments(w1[lid]['text'],goff)),dict(name='Proposed',segments=word_segments(labelmap[lid]['label_ru1_v1'],off))],
            tags=[dict(text='edit' if group=='edit' else d['decision']),dict(text=meta['book'])]))
        cardmeta.append(dict(id=lid,offset=off,group=group,book=meta['book'],final_scale=8,geometry=g,references=refs[meta['book']]))
    counts=manifest['decision_counts']
    intro=('Pre-1918 Russian prints mark some word endings with a hard sign (ъ, a small flag on top), and Google writes it as the soft sign (ь, no flag). '
        f"The decisions are {counts['edit_hard']} changes, {counts['keep_soft']} kept, and 3 held back (two are a different letter and one is uncertain). "
        'The lead confirmed all 30 sampled changes and all 10 sampled keeps. '
        'There is nothing to review here unless a letter on the left does not look like the one in the middle.')
    html=owner_sheet.render(cards,dict(title='RU1 Hard Sign Decisions',intro=intro,groups=[dict(id='edit',heading='What a change looks like'),dict(id='held',heading='Held back')]))
    size=len(html.encode());assert size<5_000_000
    (ROOT/'owner_sheet/ru1_sheet.html').write_text(html)
    summary=dict(schema='RU12-owner-v1',cards=15,edit_cards=12,hold_cards=3,sample_seed=SEED,sample_population=len(pool),
        html_bytes=size,html_MB=size/1_000_000,html_sha256=sha(ROOT/'owner_sheet/ru1_sheet.html'),renderer=str(renderer),geometry=cardmeta,
        reference_limitation='Same RU1-L book references, including agreement references not adjudicated; provenance retained per card.')
    dump(ROOT/'owner_sheet/summary.json',summary)
    assert all(sha(p)==h for p,h in inputs.items()),'input drift'
    manifest['inputs']=inputs
    dump(ROOT/'ru1_v1_manifest.json',manifest)
    dump(ROOT/'RU12_RECEIPT.json',dict(schema='RU12-receipt-v1',status='BUILT_AWAITING_TESTS',python=sys.executable,
        constraints=dict(network_used=False,git_writes=False,reader_run=False,external_writes=False),manifest=manifest,owner_sheet=summary,
        outputs={str(p.relative_to(WORK)):sha(p) for p in [ROOT/'decisions.jsonl',ROOT/'decisions.summary.json',ROOT/'ru1_v1.jsonl',ROOT/'ru1_v1_manifest.json',ROOT/'owner_sheet/ru1_sheet.html',ROOT/'owner_sheet/summary.json']}))
    print(json.dumps({k:v for k,v in manifest.items() if k not in {'inputs','excluded_controls'}},indent=2))

if __name__=='__main__':build()
