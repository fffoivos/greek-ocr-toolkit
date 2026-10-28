"""Bind a completed release locally on Clariden; one switch selects harvest variant."""
import argparse
from pathlib import Path
from common import atomic, read, spec


def bind(template, harvest_root, out, relocations=None, horizon='full'):
    cfg = read(template)
    root = Path(__file__).resolve().parent
    cfg['registry_v2'] = spec(root / 'registry_v2.jsonl.gz')
    cfg['harvest_root'] = str(Path(harvest_root).resolve())
    cfg['harvest_receipt'] = spec(Path(harvest_root) / 'RELEASE_RECEIPT.json')
    cfg['harvest_transfer'] = spec(Path(harvest_root) / 'TRANSFER.json')
    cfg['relocations'] = read(relocations) if relocations else {}
    cfg['horizon_recipe'] = horizon
    # S1's production namespace mapped these exact assets to capstor.
    # Only these asset directories are rewritten; every file/shard is SHA checked.
    base = '/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3'
    cfg['s1_asset_relocations'] = {base + '/' + part: base.replace('/iopsstor/', '/capstor/') + '/' + part
                                    for part in ('scaling_w3', 'benchmark_0.2')}
    cfg['relocations'] = {**cfg['s1_asset_relocations'], **cfg['relocations']}
    for key in ('s1_subset', 's1_records', 's1_build_info', 's1_shared_mix', 's1_node', 'factory', 'synthetic', 'seal_suite'):
        for logical, physical in cfg['s1_asset_relocations'].items():
            value = cfg[key]['path']
            if value.startswith(logical + '/'):
                cfg[key]['path'] = physical + value[len(logical):]
    atomic(out, cfg)
    return cfg


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--template', default=str(Path(__file__).with_name('data.template.json')))
    p.add_argument('--harvest-root', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--relocations')
    p.add_argument('--horizon', choices=('full', 's1-literal', 'longer'), default='full')
    a = p.parse_args()
    bind(a.template, a.harvest_root, a.out, a.relocations, a.horizon)
