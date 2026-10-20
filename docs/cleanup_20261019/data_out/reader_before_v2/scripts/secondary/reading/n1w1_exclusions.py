"""RU1 text-only census. Never imports image libraries or modifies collector inputs."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import unicodedata

PROJECTS = Path.home() / 'Projects'
COLLECT = PROJECTS / 'greek-ocr-toolkit-sol-collect'
SOURCE = PROJECTS / 'collect-v3-data/run/W1/features.jsonl'
EXCLUSIONS = COLLECT / 'docs/harvest/collect_v3/release_exclusions'
ART = Path(__file__).resolve().parents[2] / 'artifacts/ru1'
RULE = ('source == ia_russian; candidate_usable is true (fixed_usable, no text_exclusions, '
        'deduplicated by collector); crop and crop_sha256 and complete regeneration recipe present; '
        'id absent from union of release_exclusions.json classes[*].file. Crop existence is '
        'regenerability, not presence of the disposable original crop. Do not apply stratum_gate: '
        'ia_russian is withheld pending this correction. All selected rows also have usable_final=true.')
PRIOR_METHOD = ('Casefold Cyrillic token stem before the yer, without spelling normalization. '
                'Leave the target occurrence out of W1 label stem counts, including pre_hyphen. '
                'If other occurrences show both signs => both; only one => that sign_only. '
                'Otherwise unknown. No dictionary guesses or ink truth. Corpus evidence may itself '
                'contain Google errors; this is only a cross-check, never an edit decision.')

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()

def rows(path):
    with Path(path).open() as f:
        for line in f:
            if line.strip(): yield json.loads(line)

def dump(path, data):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

def jsonl(path, data):
    Path(path).write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in data))

def cyr(c):
    return c.isalpha() and 'CYRILLIC' in unicodedata.name(c, '')

def positions(text):
    result = []
    for i, ch in enumerate(text):
        if ch not in 'ъь' or i == 0 or not cyr(text[i-1]): continue
        nxt = text[i+1:i+2]
        if nxt and cyr(nxt): continue
        start = i-1
        while start > 0 and cyr(text[start-1]): start -= 1
        result.append(dict(offset=i, google=ch, kind='pre_hyphen' if nxt == '-' else 'final',
                           stem=text[start:i].casefold(), word=text[start:i+1]))
    return result

def mask(text):
    pp = positions(text); pieces=[]; last=0
    for n,p in enumerate(pp,1):
        pieces.extend([text[last:p['offset']], f'⟦{n}⟧']); last=p['offset']+1
    pieces.append(text[last:]); return ''.join(pieces), pp

def prior(p, vocab, leave_one_out=True):
    counts = dict(vocab.get(p['stem'], {}))
    if leave_one_out: counts[p['google']] = counts.get(p['google'], 0)-1
    signs = {c for c in 'ъь' if counts.get(c,0)>0}
    return 'both' if len(signs)==2 else next(iter(signs))+'_only' if signs else 'unknown'

def exclusion_ids():
    spec=EXCLUSIONS/'release_exclusions.json'; obj=json.loads(spec.read_text()); used={str(spec):sha(spec)}; ids=set()
    for cls in obj['classes'].values():
        p=EXCLUSIONS/cls['file']; used[str(p)]=sha(p)
        if 'sha256' in cls and used[str(p)] != cls['sha256']: raise ValueError('exclusion hash changed: '+str(p))
        ids.update(x.strip() for x in p.read_text().splitlines() if x.strip() and not x.startswith('#'))
    return ids, used

