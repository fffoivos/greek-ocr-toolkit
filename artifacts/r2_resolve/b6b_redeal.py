"""Offline B6b deal. No network or git operations; refuses any read answers.

Reader3 integration uses R.batch with the v2 public map, each folder's selected
scored controls and assigned order (the same call used by R.run's reader3 path).
Do not feed reduced answers to R.run directly: it regenerates the old full deal.
"""
import sys
sys.dont_write_bytecode = True
import collections
import hashlib
import json
import random
import re
import shutil
import tempfile
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.labelfix import r2_cards_resolve as R
BASE = ROOT / 'artifacts/r2_resolve'
SRC = Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad')
SEED = 20261017
EXCLUDED = 'aeead432bc9a619c69e081b1'
RULE = ('Seed 20261017; independent Random("20261017:<tranche>:selection") over sorted scored IDs. '
        'No replacement within a tranche. Shuffle polytonic-source and other pools separately; '
        'sort polytonic pool stably by descending count of breathing/grave/circumflex/subscript/diaeresis '
        'features in verified expected heads, then round-robin into b00,b01. '
        'Reserve missing scored-anchor breathing, accent, then subscript-or-diaeresis from remaining scored controls '
        '(prefer polytonic source, then seeded order), falling back to any letter when no scored-anchor example is available. Fill to 10 from remaining seeded pool. '
        'Head coverage is reported for all letters and separately for the scored anchor. '
        'Preserve each B6 folder data sequence and all public card objects; independently shuffle controls '
        'and sample insertion positions with Random("20261017:<tranche>:b<NN>:positions").')
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

def files_hash(p):
    return {str(x.relative_to(p)): sha(x) for x in sorted(p.rglob('*')) if x.is_file()}

def images(cards):
    return {f for c in cards for f in [c['word_image'], c['line_image']] + [v['image'] for v in c.get('paired_views', [])]}

def features(c, anchor=None):
    rows = c['expected_letter_heads']
    if anchor is not None:
        rows = [r for r in rows if r['index'] == anchor]
    return {h for h in R.HEADS if any(r[h] not in ('none', 'unknown') for r in rows)}

def poly_score(c):
    return sum(r[h] not in ('none', 'unknown') for r in c['expected_letter_heads'] for h in ('breathing', 'subscript', 'diaeresis')) + sum(r['accent'] in ('grave', 'circumflex') for r in c['expected_letter_heads'])

def scan(p, cards, keys):
    assert not any(x.is_symlink() for x in p.rglob('*'))
    assert {x.name for x in p.iterdir()} == {'cards.jsonl','img','README.md','answer_schema.json','answers.jsonl'}
    assert (p/'answers.jsonl').read_bytes() == b''
    assert not re.search(r'gpt|claude|gemini|llama|apertus|openai|anthropic|model', (p/'README.md').read_text(), re.I)
    allowed = {'card_id','word_image','line_image','anchor_index','anchor_base','options','extra_options','paired_views','witness_group'}
    for c in cards:
        assert set(c) <= allowed
        assert c['options'] != keys[c['card_id']]['public']['options'] or len(c['options']) <= 1
    expected_images = images(cards)
    assert {x.name for x in (p/'img').iterdir()} == expected_images
    needles = ['geometry_response','mining_key','expected_form','expected_letter_heads','crop_sha256','Google','google','/Users/','../','file://','http://','https://']
    needles += [k[f] for k in keys.values() for f in ('crop','line_id','doc','source')]
    for f in p.rglob('*'):
        if not f.is_file(): continue
        if f.suffix == '.png':
            assert f.parent == p/'img' and sha(f) == f.stem
            with Image.open(f) as im: assert not im.info, (f, im.info)
        else:
            txt = f.read_text()
            assert not any(n and n in txt for n in set(needles)), f
    return dict(passed=True, findings=[], scope='Recursive file/field allowlists, private text and paths, no symlinks, exact referenced PNG set, PNG content hashes and metadata; README model-name scan.')

def synthetic(c, control=None):
    form = control['expected_form'] if control else next(iter(c['options'].values()))
    heads = control['expected_letter_heads'] if control else [dict(index=i, **h) for i,h in enumerate(R.form_heads(form))]
    anchor = next((r for r in heads if r['index'] == c['anchor_index']), dict(index=c['anchor_index'], **dict.fromkeys(R.HEADS,'unknown')))
    return dict(card_id=c['card_id'],choice='literal',transcription=form,
                anchor_heads={h:anchor[h] for h in R.HEADS},letter_heads=[r for r in heads if r['index'] != c['anchor_index']],
                readability=control['expected_readability'] if control else 'readable',
                ownership_ok=control['expected_ownership_ok'] if control else True,
                confidence='high',note='Synthetic integration test; not a reading or truth.',usage=dict(input_tokens=0,output_tokens=0))

def dryrun(t, folder, assigned, controls, v2):
    # Worktree-local temp is required by the resolver's output safety guard.
    with tempfile.TemporaryDirectory(prefix='b6b-', dir=BASE) as tmp:
        temp = Path(tmp); deck = temp/'deck'
        R.write(deck/'blind/cards.jsonl', assigned)
        R.dump(deck/'private/controls_proposed.json', dict(controls=controls))
        cmap = {c['card_id']:c for c in controls}
        answers = [synthetic(c, cmap.get(c['card_id'])) for c in assigned]
        results = []
        for errors in (0,1,2):
            aa = json.loads(json.dumps(answers))
            bad = {c['card_id'] for c in controls[:errors]}
            for a in aa:
                if a['card_id'] in bad: a['readability'] = 'partial' if a['readability']=='readable' else 'readable'
            answer_path = temp/'answers'/f'answers_{errors}.jsonl'; R.write(answer_path,aa)
            # Exact reader3 call from R.run, with v2 mapping/control subset/order.
            _,gate = R.batch(answer_path,{c['card_id']:c for c in assigned},controls,[c['card_id'] for c in assigned])
            cli_gate = R.validate_batch(deck,answer_path,folder/'cards.jsonl',temp/f'validation_{errors}')
            receipt = json.loads((temp/f'validation_{errors}/validation_receipt.json').read_text())
            assert receipt['controls'] == 10
            assert gate == cli_gate and gate['control_errors'] == errors and gate['accepted'] == (errors<=1)
            assert gate['invalid_answer_count'] == 0
            results.append(dict(injected_errors=errors,controls_evaluated=10,gate=gate))
        R.dump(v2/'private/dry_run'/f'{folder.name}.json',dict(synthetic=True,truth_published=False,passed=True,reader3_path='R.batch (same function and argument roles as R.run reader3); R.validate_batch with exact v2 deck adapter',cases=results))
    return dict(passed=True,controls_evaluated=10,error_cases=[0,1,2],temporary_answers_removed=True)

# Preflight ALL destinations before any rebuild.
folders = [SRC/f'r2read_{t}_r3'/f'b{j:02}' for t in ('T2','T4') for j in range(2)]
for p in folders:
    assert p.is_dir() and not p.is_symlink()
    assert (p/'answers.jsonl').is_file() and (p/'answers.jsonl').read_bytes() == b'', f'STOP: nonempty/missing answers: {p}'
    assert {x.name for x in p.iterdir()} == {'cards.jsonl','img','README.md','answer_schema.json','answers.jsonl'}
# Bind all original B6 outputs before adding sibling v2 outputs.
originals = {str(p.relative_to(ROOT)): sha(p) for p in sorted(BASE.rglob('*')) if p.is_file() and 'tiebreak_v2' not in p.parts and p.name not in ('b6b_redeal.py','b6b_final_receipt.json','r3_deal_receipt_v2.json')}
summary = []
for t in ('T2','T4'):
    out = BASE/t; old = out/'tiebreak'; v2 = out/'tiebreak_v2'
    assert not v2.exists(), f'Refuse overwrite: {v2}'
    deck = ROOT/'docs/labelfix/spellcheck/R2/decks'/t
    keys = {k['card_id']:k for k in R.read(deck/'private/key.jsonl')}
    scored = json.loads((deck/'private/controls_proposed.json').read_text())['controls']
    assert all(c['lead_verified'] is True and c['card_id'] != EXCLUDED for c in scored)
    cmap = {c['card_id']:c for c in scored}
    pending = {c['card_id'] for c in R.read(out/'pending_tiebreak.jsonl')}
    oldcards = R.read(old/'blind/cards.jsonl'); mapping = {c['card_id']:c for c in oldcards}
    rng = random.Random(f'{SEED}:{t}:selection')
    poly = sorted([c for c in scored if keys[c['card_id']]['script_class']=='greek_poly'],key=lambda c:c['card_id'])
    other = sorted([c for c in scored if c not in poly],key=lambda c:c['card_id'])
    rng.shuffle(poly); rng.shuffle(other); poly.sort(key=poly_score,reverse=True)
    chosen = [poly[0::2],poly[1::2]]
    remaining = other[:]
    for j in range(2):
        for need in ({'breathing'},{'accent'},{'subscript','diaeresis'}):
            if not any(features(c,keys[c['card_id']]['anchor_index'])&need for c in chosen[j]):
                candidate = next((c for c in remaining if features(c,keys[c['card_id']]['anchor_index'])&need),None)
                if candidate is None and not any(features(c)&need for c in chosen[j]):
                    candidate = next((c for c in remaining if features(c)&need),None)
                if candidate: chosen[j].append(candidate); remaining.remove(candidate)
        while len(chosen[j]) < 10: chosen[j].append(remaining.pop(0))
    selected_ids = {c['card_id'] for batch in chosen for c in batch}
    assert len(selected_ids) == 40//2
    selected = [c for c in oldcards if c['card_id'] in pending|selected_ids]
    assert len(selected) == len(pending)+20
    (v2/'blind').mkdir(parents=True); (v2/'private').mkdir()
    R.write(v2/'blind/cards.jsonl', selected)
    shutil.copyfile(old/'blind/answer_schema.json',v2/'blind/answer_schema.json')
    shutil.copyfile(old/'blind/README.md',v2/'blind/README.md')
    for f in images(selected): shutil.copyfile(old/'blind'/f,v2/'blind'/f)
    R.dump(v2/'private/option_mapping.json',{c['card_id']:c for c in selected})
    R.dump(v2/'private/control_ids.json',sorted(selected_ids))
    R.dump(v2/'private/controls_proposed.json',dict(controls=[cmap[i] for i in sorted(selected_ids)]))
    receipts=[]; data_seen=[]
    for j in range(2):
        p=SRC/f'r2read_{t}_r3'/f'b{j:02}'
        before=files_hash(p)
        data=[c for c in R.read(p/'cards.jsonl') if c['card_id'] in pending]
        assert all(c==mapping[c['card_id']] for c in data)
        data_seen += [c['card_id'] for c in data]
        controls=[mapping[c['card_id']] for c in chosen[j]]
        positions_rng=random.Random(f'{SEED}:{t}:b{j:02}:positions')
        positions_rng.shuffle(controls)
        positions=set(positions_rng.sample(range(len(data)+10),10))
        di=iter(data); ci=iter(controls)
        assigned=[next(ci) if n in positions else next(di) for n in range(len(data)+10)]
        readme=(p/'README.md').read_text()
        assert not re.search(r'gpt|claude|gemini|llama|apertus|openai|anthropic|model',readme,re.I), 'Unexpected model name: review exact README edit first'
        assert (p/'answers.jsonl').read_bytes()==b'', 'STOP: answers changed'
        R.write(p/'cards.jsonl',assigned)
        needed=images(assigned)
        for f in (p/'img').iterdir():
            if f.name not in needed: f.unlink()
        for f in needed: shutil.copyfile(old/'blind'/f,p/'img'/f)
        (p/'answers.jsonl').write_bytes(b'')
        assert (p/'README.md').read_text()==readme
        leak=scan(p,assigned,keys)
        dry=dryrun(t,p,assigned,chosen[j],v2)
        coverage=lambda anchor: dict(collections.Counter(h for c in chosen[j] for h in features(c,keys[c['card_id']]['anchor_index'] if anchor else None)))
        receipts.append(dict(folder=str(p),cards=len(assigned),data_cards=len(data),controls=10,
            card_ids=[c['card_id'] for c in assigned],selected_control_ids=[c['card_id'] for c in chosen[j]],
            control_positions=sorted(positions),control_source_classes=dict(collections.Counter(keys[c['card_id']]['script_class'] for c in chosen[j])),
            head_coverage_all_letters=coverage(False),head_coverage_scored_anchor=coverage(True),
            pre_rebuild_hashes=before,hashes=files_hash(p),README_unchanged=True,answers_empty_before=True,answers_empty_after=True,leak_scan=leak,resolver_dry_run=dry))
        summary.append(dict(tranche=t,folder=p.name,cards=len(assigned),data=len(data),controls=10))
    assert set(data_seen)==pending and len(data_seen)==len(pending)
    assert len(pending)==(78 if t=='T2' else 102)
    R.dump(out/'r3_deal_receipt_v2.json',dict(seed=SEED,selection_rule=RULE,folders=receipts,
        source_manifest_sha256=sha(old/'blind/cards.jsonl'),v2_manifest_sha256=sha(v2/'blind/cards.jsonl'),
        private_map=str(v2/'private/option_mapping.json'),private_map_outside_reader_folders=True,
        v2_hashes=files_hash(v2),scored_pool=len(scored),polytonic_source_pool=len(poly),
        scored_pool_feature_availability={h:sum(h in features(c) for c in scored) for h in R.HEADS},
        forbidden_control_id=EXCLUDED,controls_unique_within_tranche=True,
        control_gate_max_errors=1,network='OFF',reader_launched=False,
        integration='Gate each folder independently with R.batch using v2 mapping, selected controls and folder order. Join accepted normalized votes by card ID to B6 reader votes. R.run --reader3 regenerates B6 full deal and must not be used directly on v2. Synthetic dry-runs use R.validate_batch on temporary exact v2 deck adapters; no synthetic truth is published.'))
for rel,digest in originals.items(): assert sha(ROOT/rel)==digest, rel
for p in folders: assert (p/'answers.jsonl').read_bytes()==b''
R.dump(BASE/'b6b_final_receipt.json',dict(passed=True,seed=SEED,counts=summary,total_cards=sum(x['cards'] for x in summary),data_cards=180,control_readings=40,
    B6_original_output_hashes_unchanged=originals,all_answers_empty=True,leak_scan_pass=True,resolver_dry_run_pass=True,network='OFF',git_operations=False))
print(json.dumps(summary,indent=2))
print('B6b READY: folders 4; cards 220 (data 180, controls 40); leak scan pass; resolver dry-run pass')
