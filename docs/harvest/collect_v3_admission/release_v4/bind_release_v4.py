#!/usr/bin/env python3
"""Coordinator-only local binding on Clariden; no network, compute or submission.

Reads completed census receipts and coordinator-bound released sf7 artifacts.
Copies package metadata to a NEW content-addressed package. Never overwrites.
Large inputs are sized, not hashed/parsed; the release batch hashes them twice.
"""
import argparse
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import sqlite3
import build_release_v4 as b
from package_release_v4 import identity, seal


def bind_config(root, cfg, census_config, tool_versions, readout, census_manifest=None):
    cfg=copy.deepcopy(cfg)
    attempt=Path(cfg['census_attempt'])
    current=attempt/'CURRENT.json'
    cur=json.loads(current.read_text())
    b.require(cur['status']=='completed', 'census_06 not complete')
    summary=Path(cur['summary_path']);summ=json.loads(summary.read_text())
    b.require(b.sha(summary)==cur['summary_sha256'] and summ['complete'] and summ['reconciled'], 'census summary receipt mismatch')
    generation=summary.parent
    cc=json.loads(Path(census_config).read_text());tv=json.loads(Path(tool_versions).read_text())
    b.require('polytonic' not in cc.get('routes_out_of_scope',[]), 'polytonic out of scope')
    db=attempt/'ledger.sqlite'
    wal=Path(str(db)+'-wal')
    b.require(not wal.exists() or wal.stat().st_size==0, 'unfinished census WAL')
    with sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True) as con:
        binding=json.loads(con.execute("SELECT value FROM run WHERE key='binding'").fetchone()[0])
    b.require(b.digest(b.canonical(binding))==cur['run_binding_sha256']==summ['run_binding_sha256'], 'census run binding mismatch')
    b.require(binding['config']==dict(cc,routes_out_of_scope=cc.get('routes_out_of_scope',[])), 'census config differs from completed run')
    b.require(binding['versions_sha256']==b.sha(tool_versions), 'census versions differ from completed run')
    cfg['census_run_binding']=binding
    ledgers=[dict(x) for x in cc['corrections'] if x['tool']=='polytonic']
    b.require(ledgers and all(x.get('status')=='released' for x in ledgers), 'sf7 binding pending')
    # Require the configuration's actual version file, not an unrelated manifest.
    b.require(Path(cc['versions']).resolve()==Path(tool_versions).resolve(), 'census tool_versions path mismatch')
    v=tv['tools']['polytonic']
    b.require(v['version']==cfg['sf7']['version'] and v['digest']==cfg['sf7']['tool_digest'], 'released sf7 components/version changed')
    expected=json.loads((root/'inputs/census06_expected_tool_versions.json').read_text())['tools']
    b.require(tv['tools']==expected, 'census_06 tool drift')
    for r in cfg['registry']:
        if r['mode']=='census_internal':
            v=tv['tools'][r['tool']]
            r.update(binding_status='bound',file=str(Path(tool_versions).resolve()),sha256=b.sha(tool_versions),version=v['version'],tool_digest=v['digest'],artifacts=[x for x in cc['corrections'] if x['tool']==r['tool']])
    v=tv['tools']['polytonic']
    b.require('released' in v['scope'] and 'candidate_pre_audit' not in v['scope'], 'polytonic not released in versions')
    for x in ledgers:
        p=Path(x['path']);b.require(p.is_absolute() and p.is_file(), 'sf7 ledger path missing')
        b.require(p.stat().st_size < 64*1024*1024, 'sf7 binding needs compute qualification; ledger exceeds 64 MiB')
        b.require(b.sha(p)==x['sha256'], 'sf7 ledger sha mismatch')
    cfg['sf7'].update(binding_status='bound',ledgers=ledgers,ledger_shas=[x['sha256'] for x in ledgers])
    sfreg=next(r for r in cfg['registry'] if r['name']=='sf7')
    sfreg.update(artifacts=ledgers,ledger_shas=cfg['sf7']['ledger_shas'],binding_status='bound')
    mapping={'CURRENT.json':current,'summary.json':summary,'readout.json':Path(readout),
             'census06_config.json':Path(census_config),'census06_tool_versions.json':Path(tool_versions),
             **{n:generation/(n+'.jsonl') for n in ('admitted_train','admission_records','decisions','evaluation_diagnostics')}}
    for item in cfg['inputs']:
        if item.get('group')!='census_06':continue
        n=item['name'];p=mapping[n].resolve()
        if item['kind']=='large':
            h=summ['outputs'][n]['sha256']
        else:
            b.require(p.stat().st_size < 64*1024*1024, 'binding metadata too large');h=b.sha(p)
        item.update(path=str(p),sha256=h,bytes=p.stat().st_size)
    # Cache ledger sizes separately so bindings remain byte-equal to census config.
    cfg['sf7']['ledger_sizes']={x['sha256']:Path(x['path']).stat().st_size for x in ledgers}
    if 'crops4c' in cfg:
        from crops4c_contract import bind
        bind(cfg, Path(census_manifest), Path(tool_versions), b.sha, b.require)
    _,_,pending=b.input_check(root,cfg,light=True)
    b.require(not pending, 'pending bindings: '+','.join(pending))
    return cfg


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--census-config',type=Path,required=True)
    p.add_argument('--tool-versions',type=Path,required=True)
    p.add_argument('--readout',type=Path,required=True)
    p.add_argument('--census-manifest',type=Path,required=True,help='final bound census06 DEPLOY_SHA256SUMS')
    a=p.parse_args();root=Path(__file__).resolve().parent
    # Verify original package before using its pinned immutable bindings.
    from verify_release_v4 import package
    from contextlib import redirect_stdout
    with redirect_stdout(sys.stderr):package(root)
    _,cfg=b.load_config(root/'INPUTS.json')
    cfg=bind_config(root,cfg,a.census_config,a.tool_versions,a.readout,a.census_manifest)
    base=Path(cfg['work_root'])/'release_v4'
    # Staging and final package remain within release_v4; no source package writes.
    stage=Path(tempfile.mkdtemp(prefix='binding-',dir=base))
    try:
        for name in (root/'DEPLOY_PATHS.txt').read_text().splitlines():
            target=stage/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/name,target)
        b.write_json(stage/'INPUTS.json',cfg)
        template=dict(schema='release-v4-corrections-registry-v1',versions=[dict(r,release_rows_touched=None,release_rows_with_record=None) for r in cfg['registry']],sf7=cfg['sf7'])
        b.write_json(stage/'corrections_registry.json',template)
        ident=seal(stage);destination=base/'pkg'/ident[:8]
        b.require(not destination.exists(), 'bound package already exists')
        # package/core identity checked before atomic no-overwrite destination creation.
        destination.mkdir()
        for child in stage.iterdir():shutil.move(str(child),str(destination/child.name))
        with redirect_stdout(sys.stderr):package(destination)
        print(destination)
    finally:
        shutil.rmtree(stage)

if __name__=='__main__':main()
