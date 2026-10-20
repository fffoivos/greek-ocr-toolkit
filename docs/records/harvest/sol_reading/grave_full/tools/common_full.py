"""Offline SR-G3 shared helpers. No writes outside the two grave_full roots."""
import collections, copy, hashlib, importlib.util, json, math, random, re, sys, shutil, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SR = ROOT.parent
PACK_ROOT = Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/d11f6140-6320-42d0-9f21-018ca3512d68/scratchpad/sol_reading_packs')
BED = PACK_ROOT/'grave_full'
def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec); spec.loader.exec_module(obj)
    return obj
g1 = module('sr_g1', SR/'grave/tools/build_grave.py')
g2 = module('sr_g2', SR/'grave/tools/score_grave.py')
sys.path.insert(0, str(SR/'tools'))
import scan_rollout
ACCENTS = g2.ACCENTS
sha = g1.sha

def dump(path, data):
    path = Path(path).resolve()
    if not any(path.is_relative_to(p.resolve()) for p in (ROOT, BED)):
        raise ValueError('Write outside grave_full')
    g1.dump(path, data)

def load(path):
    return json.loads(Path(path).read_text())

def opaque(seed):
    return 'k'+hashlib.sha256(seed.encode()).hexdigest()[:10]

def fraction(x, n):
    return dict(count=x, total=n, rate=x/n if n else None)

def frac(x, n):
    return f'{x}/{n}'+(f' ({x/n:.2%})' if n else ' (undefined)')

def public_rows(folder):
    return [json.loads(s) for s in (folder/'items.jsonl').read_text().splitlines()]

def validate(answers, key):
    # Reuse the full SR-G2 schema/order validation and duplicate-field parser.
    adapted = {i: dict(m, truth_accent=m.get('label_accent', m.get('truth_accent')),
                       **{'class': 'control'}, touches_punct=m.get('touches_punct', False))
               for i, m in key.items()}
    g2.score(answers, adapted)
    return {a['item_id']: a for a in answers}

def read_contexts(key, prefix, answer_root=None):
    answer_root = Path(answer_root) if answer_root else SR/'answers/grave_full'
    names = list(dict.fromkeys(m['context'] for m in key.values() if m['context'].startswith(prefix)))
    expected = {name+'.jsonl' for name in names}
    actual = {p.name for p in answer_root.glob(prefix+'*.jsonl')}
    if actual != expected:
        raise ValueError(f'Answer files mismatch: missing={sorted(expected-actual)} unexpected={sorted(actual-expected)}')
    answers = {}
    for name in names:
        part = {i: m for i, m in key.items() if m['context'] == name}
        errors, _ = scan_rollout.integrity(BED/name)
        if errors:
            raise ValueError('Pack integrity: '+name+': '+str(errors))
        # Reader answers/zoom are permitted additions; validate strict public
        # closure on only the manifest originals, without changing the reader.
        manifest = load(BED/f'MANIFEST.{name}.json')
        with tempfile.TemporaryDirectory(prefix='confirm-closure-', dir=scan_rollout.REPLAY_TMP) as tmp:
            folder = Path(tmp)
            for rel in manifest['files']:
                dest = folder/rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(BED/name/rel, dest)
            closure = g1.scan(folder, part)
            if closure['files'] != manifest['files']:
                raise ValueError('Public payload differs from manifest: '+name)
        answers.update(validate(g2.load_answers(answer_root/(name+'.jsonl')), part))
    return answers

def control_report(key, answers):
    out = {}
    for name in dict.fromkeys(m['context'] for m in key.values()):
        rows = [dict(item_id=i, g1_id=m['g1_id'], expected=m['truth_accent'], answer=answers[i]['accent'],
                     passed=answers[i]['accent'] == m['truth_accent'])
                for i, m in key.items() if m['context'] == name and m['role'] == 'control']
        errors = sum(not r['passed'] for r in rows)
        out[name] = dict(passes=len(rows)-errors, total=len(rows), errors=errors, flagged=errors>1, items=rows)
    return out

def control_pool():
    evidence = load(ROOT/'keys/CONTROL_VERIFICATION.json')
    key = load(SR/'grave/keys/key.json')
    pub = {r['item_id']: r for r in public_rows(PACK_ROOT/'grave/r1')}
    answers = {a['item_id']: a for a in g2.load_answers(SR/'answers/grave/r1.jsonl')}
    out = []
    for iid, v in evidence['items'].items():
        m = key[iid]
        if m['stratum'] not in ('lekythos__poly1900', 'kosmopolis__poly1900'):
            raise ValueError('NLG control forbidden')
        if v['printed'] != m['truth_accent'] or answers[iid]['accent'] != v['printed']:
            raise ValueError('Unverified control')
        for f in ('word_image', 'letter_image'):
            if sha(PACK_ROOT/'grave/r1'/pub[iid][f]) != v[f+'_sha256']:
                raise ValueError('Control pixel evidence changed')
        out.append((iid, m, pub[iid]))
    if {m['truth_accent'] for _, m, _ in out} != set(ACCENTS[:-1]):
        raise ValueError('Control pool needs all four accent types')
    return out

def choose_controls(pool, n, seed, avoid=()):
    rng = random.Random(seed); pool = list(pool); rng.shuffle(pool)
    selected = []
    # Balanced round-robin across types, prefer sources absent from p1 context.
    for j in range(n):
        kind = ACCENTS[j % 4]
        choices = [p for p in pool if p[1]['truth_accent'] == kind and p[0] not in {q[0] for q in selected}]
        if not choices:
            choices = [p for p in pool if p[1]['truth_accent'] == kind]
        choices.sort(key=lambda p: p[0] in avoid)
        selected.append(choices[0])
    return selected

def write_context(name, entries):
    """entries are (private record, public record, source image folder)."""
    folder = BED/name
    if folder.exists():
        # Permit idempotent rebuild only if the old payload still passes closure.
        old = public_rows(folder)
        g1.scan(folder, {p['item_id']: {'line_id': '__old__', 'stratum': '__old__'} for p in old})
        for path in (folder/'img').iterdir(): path.unlink()
    folder.mkdir(parents=True, exist_ok=True); (folder/'img').mkdir(exist_ok=True)
    key = {}; public = []
    for index, (m, p, source) in enumerate(entries):
        m, p = copy.deepcopy(m), copy.deepcopy(p)
        iid = opaque(f'sol-grave-full:{name}:{index}:{m.get("bed_id", m.get("g1_id"))}')
        if iid in key: raise ValueError('ID collision')
        p['item_id'] = iid; m['context'] = name
        for f in ('word_image', 'letter_image'):
            data = (Path(source)/p[f]).read_bytes()
            dest = folder/p[f]; dest.write_bytes(data)
        key[iid] = m; public.append(p)
    (folder/'items.jsonl').write_text(''.join(json.dumps(p, ensure_ascii=False)+'\n' for p in public))
    result = g1.scan(folder, key)
    manifest = BED/f'MANIFEST.{name}.json'
    dump(manifest, dict(bed='grave_full', context=name, files=result['files']))
    return key, dict(name=name, bed=sum(m['role']=='bed' for m in key.values()),
                     controls=sum(m['role']=='control' for m in key.values()), total=len(key),
                     manifest_sha256=sha(manifest), closure_ok=result['ok'])

def control_entries(chosen):
    return [(dict(m, role='control', g1_id=iid, pixel_verified=True), p, PACK_ROOT/'grave/r1')
            for iid, m, p in chosen]
