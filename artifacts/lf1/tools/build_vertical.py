"""Offline vertical re-read packs from sealed first-read rosters; no readers."""
import argparse
import json
from pathlib import Path
import random
from build import pack, SEED
from lf1 import BASE, sha, rows, dump


def build_vertical(rosters, batch):
    output=BASE/f'candidate_contexts_vert_{batch}.json'
    if output.exists():raise FileExistsError('vertical roster already exists')
    bed=[]
    for roster in rosters:
        for context in json.loads(Path(roster).read_text()):
            if sha(context['key'])!=context['key_sha256']:raise ValueError('key custody changed')
            if sha(context['manifest'])!=context['manifest_sha256']:raise ValueError('manifest custody changed')
            key=json.loads(Path(context['key']).read_text())['items']
            manifest=json.loads(Path(context['manifest']).read_text())['files']
            directory=Path(context['directory'])
            if sha(directory/'items.jsonl')!=manifest['items.jsonl']:raise ValueError('items custody changed')
            for card in rows(directory/'items.jsonl'):
                row=key[card['card_id']]
                if row['control'] or row.get('draw_class')!='vertical_turned':continue
                crop=directory/card['crop']
                if sha(crop)!=row['pack_crop_sha256'] or sha(crop)!=manifest[card['crop']]:
                    raise ValueError('pack crop custody changed')
                assert card['google_text']==row['label'], 'pack label differs from key'
                bed.append(dict(row,source_crop=str(crop),source_sha256=sha(crop),
                    first_context=context['name'],first_card_id=card['card_id']))
    poolfile=BASE/'keys/control_pool.json'
    pool=[r for r in json.loads(poolfile.read_text()) if r['pool_id']!='lf1-control-turned']
    random.Random(SEED).shuffle(bed)
    prompt=BASE/'prompts/lf1_vertical.md'
    contexts=[pack(f'candidate_vert_{batch}_{n//50+1:05d}',bed[n:n+50],pool,exact_bytes=True)
              |dict(prompt=str(prompt),prompt_sha256=sha(prompt),reread='vertical_turned',
                     first_rosters=[str(p.resolve()) for p in rosters]) for n in range(0,len(bed),50)]
    dump(output,contexts)
    receipt=dict(rosters={str(p):sha(p) for p in rosters},seed=SEED,bed=len(bed),contexts=len(contexts),
        controls_per_context=len(pool),omitted_control='lf1-control-turned',
        omission_reason='turned horizontal line expectation undefined under vertical statement',
        control_pool_sha256=sha(poolfile),prompt=str(prompt),prompt_sha256=sha(prompt),
        labels='copied verbatim',crops='exact first-pack bytes',reader_runs=0)
    dump(BASE/f'receipts/candidate_contexts_vert_{batch}_build.json',receipt)
    return receipt


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rosters',type=Path,nargs='+',required=True)
    p.add_argument('--batch',required=True)
    a=p.parse_args();print(json.dumps(build_vertical(a.rosters,a.batch)))

if __name__=='__main__':main()
