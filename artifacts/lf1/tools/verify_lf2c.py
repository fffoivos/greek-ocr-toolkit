"""Offline mechanical LF2c identity checks; no crop display or label judgment."""
import collections
import hashlib
import json
from pathlib import Path
from lf1 import BASE, rows, sha, dump
from prod_adapter import DRAW, DRAW_FIELDS, DRAW_POLICY, adapt, key, draw_counts


def text_sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def main():
    old=DRAW.with_name('candidates.jsonl')
    assert sha(old)=='70a29c202691584a3382e77505ef56db7b9a0d1347fa5ac2eccc95ac8e9acfe5'
    assert sha(DRAW)=='0432c56f75ed1efded00b76e7aeabcc0a2bf9441bfad00e825e4e105006134c2'
    before,after=rows(old),rows(DRAW)
    assert len(before)==len(after)==3341
    assert before==[{k:v for k,v in r.items() if k not in DRAW_FIELDS} for r in after]
    counts=collections.Counter((r['split'],r['in_quota']) for r in after)
    assert counts=={('test',True):2340,('dev',True):453,('test',False):468,('dev',False):80}
    scopes=draw_counts(after)
    dump(BASE/'prod/partition_v3_receipt.json',dict(draw=str(DRAW),draw_sha256=sha(DRAW),
        previous_draw=str(old),previous_draw_sha256=sha(old),rows=3341,
        original_fields_and_order_equal=True,draw_policy=DRAW_POLICY,scopes=scopes,
        counts={side:dict(in_quota=counts[side,True],reserve=counts[side,False]) for side in ('test','dev')}))

    historical=json.loads((BASE/'prod/build_input_w1a.receipt.json').read_text())
    previous_input=Path(historical['output']); assert sha(previous_input)==historical['output_sha256']
    previous=rows(previous_input);wanted={key(r) for r in previous}
    subset=[r for r in after if key(r) in wanted]
    assert len(subset)==576
    readout=DRAW.parents[1]/'census05_readout/candidates_readout.jsonl'
    assert sha(readout)==historical['readout_sha256']
    current,_=adapt(subset,[r for r in rows(readout) if key(r) in wanted])
    identities=lambda rr:[(r['line_id'],text_sha(r['label'])) for r in rr]
    assert identities(current)==identities(previous)
    current_by_id={r['line_id']:r for r in current}
    roster_path=BASE/'candidate_contexts_w1a.json'
    contexts=json.loads(roster_path.read_text());checks=[];beds=[]
    for context in contexts:
        key_path=Path(context['key']);manifest=Path(context['manifest']);directory=Path(context['directory'])
        assert sha(key_path)==context['key_sha256']
        assert sha(manifest)==context['manifest_sha256']
        files=json.loads(manifest.read_text())['files']
        assert all(sha(directory/name)==digest for name,digest in files.items())
        private=json.loads(key_path.read_text())['items']
        cards={r['card_id']:r for r in rows(directory/'items.jsonl')}
        assert set(cards)==set(private)
        for card_id,row in private.items():
            if row['control']:continue
            new=current_by_id[row['line_id']]
            assert text_sha(row['label'])==text_sha(new['label'])==text_sha(cards[card_id]['google_text'])
            beds.append(dict(context=context['name'],card_id=card_id,line_id=row['line_id'],
                             old_label_sha256=text_sha(row['label']),v3_label_sha256=text_sha(new['label'])))
        checks.append(dict(name=context['name'],key_sha256=sha(key_path),manifest_sha256=sha(manifest),
                           payload_files=len(files),payload_hashes_match=True))
    assert len(beds)==len({r['line_id'] for r in beds})==576
    assert {r['line_id'] for r in beds}==set(current_by_id)
    dump(BASE/'prod/w1a_v3_identity_receipt.json',dict(draw_sha256=sha(DRAW),
        previous_input_sha256=sha(previous_input),readout_sha256=sha(readout),
        roster_sha256=sha(roster_path),bed_rows=576,contexts=checks,bed_identity=beds,
        same_line_ids_and_order=True,same_label_sha256=True,pack_hashes_unchanged=True,rebuilt=False))
    print('v3 rows/order equal; in-quota 2340/453 reserve 468/80; W1 576 ids/label shas and 12 pack payloads unchanged')


if __name__=='__main__':main()
