"""Recompute only the sealed unchanged draw with frozen observers and CP7 cache.

The adapter changes cache lookup only. It never redraws or rebuilds packs.
"""
import gzip
import os
import sys
from collections import Counter
from cp7_common import *
from freeze import verify_freeze
import measure
from prepare_population_geometry import page_manifest, valid
from greekocr.harvest.admission import page_medians, _page_key


def pack_hashes():
    return {str(p):sha(p) for bed in BEDS for p in sorted((PACK_ROOT/bed).rglob('*')) if p.is_file()}


def main():
    offline_guard();verify_freeze()
    selected=rows(HERE/'keys/draw.jsonl');before=read(HERE/'build_receipt.json')
    assert len(selected)==100 and sha(HERE/'keys/draw.jsonl')==before['draw_sha256']
    manifest=page_manifest(selected)
    assert all(valid(SEG/'CP7_geometry',p) for p in manifest), 'gate preparation incomplete'
    packs_before=pack_hashes()
    # Assert packs still match the CP7a2 byte bindings before observing anything.
    commit=read(SEG/'CP7_COMMIT_LIST.json')
    for item in commit['external_pack_artifacts']:
        assert packs_before[item['path']]==item['sha256']
    prior_cache_for=measure.cache_for
    by_pid={pid:p for p in manifest for pid in p['page_ids']}
    def cp7_cache_for(record):
        pid=record['id'].rsplit('-l',1)[0]
        if pid in by_pid:return SEG/'CP7_geometry/cache'/by_pid[pid]['page_id']
        return prior_cache_for(record)
    measure.cache_for=cp7_cache_for
    # Use identical full-snapshot page medians; stream unrelated rows away.
    wanted={_page_key(r) for r in selected}; median_records=[]
    for p,d in before['inputs'].items():
        if Path(p).name.startswith(('W1_features_','W2_features_')):
            assert sha(p)==d
            with Path(p).open() as f:
                for line in f:
                    r=json.loads(line)
                    if _page_key(r) in wanted:median_records.append(r)
    medians=page_medians(median_records)
    measured=[]
    for n,r in enumerate(selected):
        measured.append(measure.observe(r,median=medians.get(_page_key(r))))
        print(f'sealed observation {n+1}/100',flush=True)
    sealed=HERE/'keys/sealed_decisions.jsonl.gz'
    backup=HERE/'keys/sealed_decisions_cp7a2.jsonl.gz'
    if not backup.exists():
        with os.fdopen(os.open(backup,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb') as f:
            f.write(sealed.read_bytes())
    assert sha(backup)==before['sealed_decisions_sha256']
    sealed.write_bytes(gzip.compress(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in measured).encode(),mtime=0))
    os.chmod(sealed,0o600)
    rules=Counter(); exclusive=Counter()
    for c in measured:
        for name,positive in [('geometry_unavailable',c['geometry_unavailable']),('merged',c['merged']),
            ('neighbour_words',c['neighbour_words']),('orientation',c['orientation']),('crossing',c['crossing'].get('drop'))]:
            if positive is True:rules[name]+=1
        if c['screen_drop'] is True:
            active=[name for name,positive in [('geometry_unavailable',c['geometry_unavailable']),
                ('merged',c['merged']),('neighbour_words',c['neighbour_words']),
                ('crossing',c['crossing'].get('drop')),('orientation',c['orientation'])] if positive is True]
            assert active, 'drop with no attributed rule'
            exclusive[active[0]]+=1
    progress=read(SEG/'CP7_geometry/progress.json')
    prepared=[r for r in progress['results'] if r['status']=='prepared']
    total_s=sum(r['seconds'] for r in prepared); total_bytes=sum(r['bytes'] for r in prepared)
    cache_bytes=sum(p.stat().st_size for p in (SEG/'CP7_geometry').rglob('*') if p.is_file())
    packs_after=pack_hashes();assert packs_before==packs_after
    summary=dict(freeze_sha256=sha(SEG/'CP7_FREEZE.json'),draw_sha256=sha(HERE/'keys/draw.jsonl'),
        pages=len(manifest),pages_prepared=len(prepared),failures=progress['failures'],
        seconds_total=total_s,seconds_per_page=total_s/len(prepared),bytes_total=total_bytes,
        MB_per_page=cache_bytes/len(prepared)/1e6,cache_bytes_total=cache_bytes,
        geometry_unavailable=sum(c['geometry_unavailable'] for c in measured),
        unavailable_reasons=dict(Counter(c['structural'].get('reason','unspecified') for c in measured if c['geometry_unavailable'])),
        screen_drop=sum(c['screen_drop'] is True for c in measured),drop_by_rule=dict(rules),
        rule_counts_overlap=True,exclusive_drop_attribution=dict(exclusive),exclusive_priority=['geometry_unavailable','merged','neighbour_words','crossing','orientation'],orientation_unknown=sum(c['orientation_unknown'] for c in measured),
        sealed_decisions_sha256=sha(sealed),previous_sealed_sha256=sha(backup),
        packs_unchanged=True,pack_files=len(packs_after),readers_started=0,network='OFF',population_run_started=False)
    dump(HERE/'geometry_cp7a3_receipt.json',summary)
    dump(HERE/'pack_preservation_cp7a3.json',dict(unchanged=True,files=packs_after))
    # Keep build_receipt as historical CP7a2 evidence. Downstream validation uses
    # a current receipt carrying its original bindings plus the recomputed seal.
    current=dict(before,**{k:summary[k] for k in ('screen_drop','geometry_unavailable','orientation_unknown','sealed_decisions_sha256')},
                 supersedes='build_receipt.json',stage='CP7a3')
    dump(HERE/'build_receipt_cp7a3.json',current)
    verify_freeze()

if __name__=='__main__':main()
