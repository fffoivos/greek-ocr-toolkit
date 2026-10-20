"""Offline RU1 finalisation. Check every accepted scan before any output write."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent/'reading'))
from common import ROOT, PACK_ROOT, rows, dump, jsonl, sha
from ru1_decide import accepted_contexts, combine
from ru1_map_answers import map_records


def scan_check(art):
    for ctx, reader, stem in accepted_contexts():
        path = art/f'answers/{stem}.scan.json'
        if not path.is_file(): raise ValueError('scan has not cleared: '+stem+' (missing)')
        scan = json.loads(path.read_text())
        if scan.get('ok') is not True or scan.get('violations') or scan.get('manifest_check_skipped'):
            raise ValueError('scan has not cleared: '+stem)


def finalize(art=ROOT, packs=PACK_ROOT, dry_run=False, owner_build=None):
    plan = dict(steps=['scan_check','mapping','combiner','owner_sheet','summary'],
                accepted_contexts=[s for _,_,s in accepted_contexts()], excluded=['ctx04.r2'])
    if dry_run:
        try: scan_check(art); plan['scans_cleared'] = True
        except (ValueError, OSError) as exc: plan.update(scans_cleared=False, pending=str(exc))
        return dict(plan, dry_run=True, writes=False)
    scan_check(art)
    # Validate all mappings in memory before writing any of them.
    mapped = []
    for ctx, reader, stem in accepted_contexts():
        key = json.loads((art/f'keys/{stem}.json').read_text())
        records, score = map_records(rows(art/f'answers/{stem}.jsonl'), key,
                                    rows(packs/ctx/reader/'items.jsonl'), reader)
        mapped.append((stem, records, score))
    for stem, records, score in mapped:
        jsonl(art/f'answers/{stem}.mapped.jsonl', records)
        dump(art/f'answers/{stem}.controls.json', score)
    decisions = combine(art)
    if decisions['status'] != 'complete': raise ValueError('incomplete combination')
    if owner_build is None:
        if art != ROOT or packs != PACK_ROOT: raise ValueError('owner builder requires canonical paths')
        from ru1_owner_sheet import build
        owner_build = build
    owner = owner_build()
    result = dict(plan, status='complete', decisions=decisions, owner_sheet=owner,
                  scans={s:sha(art/f'answers/{s}.scan.json') for _,_,s in accepted_contexts()})
    dump(art/'finalization.summary.json', result)
    return result


def main():
    p=argparse.ArgumentParser(); p.add_argument('--dry-run',action='store_true'); a=p.parse_args()
    try: print(json.dumps(finalize(dry_run=a.dry_run),ensure_ascii=False,indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc: raise SystemExit(str(exc))


if __name__ == '__main__': main()
