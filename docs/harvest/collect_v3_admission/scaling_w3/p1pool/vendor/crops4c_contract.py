"""CROPS4C full/smoke custody; no crop generation or network access."""
import json
from pathlib import Path

FILES = ('upload_receipt.json', 'crops_manifest.jsonl', 'crops_sha256.txt', 'sha256check.log', 'prepared-check.log')


def validate(r, smoke, cfg, inputs, require):
    c = r['context']
    require(r['status'] == 'ok' and r['mode'] == 'full', 'CROPS4C status/mode')
    require(c['tranche'] == 'all' and c['include_heldout'] is True, 'CROPS4C selection scope')
    require(r['output_base'] == cfg['work_root'], 'CROPS4C output base')
    require(r['sha256check_exit'] == r['mismatches'] == r['failures'] == 0, 'CROPS4C failures')
    require(r['byte_exact'] == r['selected'] == r['written'] + r['skipped_valid'], 'CROPS4C totals')
    require(r['train_selected'] + r['heldout_selected'] == r['selected'], 'CROPS4C split totals')
    require(isinstance(r['selection_sha256'], str) and len(r['selection_sha256']) == 64, 'CROPS4C selection digest')
    require(set(r['per_tranche']) == {'W1','W2'}, 'CROPS4C tranches')
    for n in ('selected','written','skipped_valid','mismatches','failures','bytes'):
        require(all(type(r['per_tranche'][t][n]) is int and r['per_tranche'][t][n] >= 0 for t in ('W1','W2')) and sum(v[n] for v in r['per_tranche'].values()) == r[n], 'CROPS4C per_tranche '+n)
    for v in r['per_tranche'].values():
        require(v['selected'] == v['written'] + v['skipped_valid'] and v['mismatches'] == v['failures'] == 0, 'CROPS4C tranche reconciliation')
    require(c['inputs'] == inputs, 'CROPS4C census inputs')
    require(c == cfg['crops4c']['context'], 'CROPS4C runtime context')
    require(smoke['status'] == 'ok' and smoke['mode'] == 'smoke' and smoke['selected'] == smoke['byte_exact'] == 500 and smoke['context'] == dict(c,tranche='W2'), 'CROPS4C smoke')
    require(smoke['sha256check_exit'] == smoke['failures'] == smoke['mismatches'] == 0, 'CROPS4C smoke failures')
    require(smoke['output_base'] == str(Path(cfg['crops4c']['smoke_attempt'])/'smoke'), 'CROPS4C smoke base')


def check(root, cfg, byname, sha, require):
    spec = cfg['crops4c']
    require(spec['binding_status'] == 'bound', 'CROPS4C pending')
    for f in spec['files']:
        require(sha(f['path']) == f['sha256'], 'CROPS4C binding sha: '+f['path'])
    a = Path(spec['attempt'])
    r = json.loads((a/'upload_receipt.json').read_text())
    smoke = json.loads((Path(spec['smoke_attempt'])/'upload_receipt.json').read_text())
    summary = json.loads(byname['summary.json'].read_text())
    inputs = {n:sha(byname[n]) for n in ('CURRENT.json','summary.json')}
    inputs.update({n:summary['outputs'][n]['sha256'] for n in ('admitted_train','decisions','evaluation_diagnostics')})
    validate(r, smoke, cfg, inputs, require)
    return dict(name='crops4c',check='full_smoke_and_custody',files=spec['files'],selection_sha256=r['selection_sha256'],train_selected=r['train_selected'],heldout_selected=r['heldout_selected'])


def bind(cfg, manifest, versions, sha, require):
    """Capture final code and runtime pins from authenticated full receipt."""
    spec=cfg['crops4c']; base=manifest.parent.resolve()
    require(base.name == sha(manifest)[:16], 'CROPS4C final census code id')
    entries={n:h for h,n in (line.split('  ',1) for line in manifest.read_text().splitlines())}
    def member(path, expected=None):
        path=Path(path).resolve()
        require(path.is_relative_to(base), 'CROPS4C file outside final census code')
        rel=str(path.relative_to(base))
        require(rel in entries and sha(path)==entries[rel] and (expected is None or entries[rel]==expected), 'CROPS4C final manifest member')
    member(versions)
    attempt=Path(spec['attempt']); smoke=Path(spec['smoke_attempt'])
    r=json.loads((attempt/'upload_receipt.json').read_text());c=r['context']
    native='e7dbe6c47061529953102b1af93422b593460e7510b22e27dbde69bcfbf052b7'
    member(c['reconstruction_file'],native)
    require(c['reconstruction_module']=='greekocr.harvest.line_pipeline_native' and c['reconstruction_function']=='reconstructed_crop' and c['reconstruction_sha256']==native, 'CROPS4C reconstruction')
    require(Path(c['reconstruction_file']).resolve()==Path(c['census_code']).resolve()/'greekocr/harvest/line_pipeline_native.py', 'CROPS4C census_code')
    package=Path(cfg['work_root'])/'crops4_package/9a3b80c1'
    deploy=package/'DEPLOY_SHA256SUMS'
    require(sha(deploy)==cfg['crops4c_package_manifest_sha256'], 'CROPS4C package manifest')
    sums={n:h for h,n in (line.split('  ',1) for line in deploy.read_text().splitlines())}
    require(c['code_sha256']==sums['materialise_crops.py']==sha(package/'materialise_crops.py'), 'CROPS4C materialiser')
    for pathkey,hashkey in (('interpreter','interpreter_sha256'),('codec_preload','codec_preload_sha256')):
        require(Path(c[pathkey]).is_absolute() and sha(c[pathkey])==c[hashkey], 'CROPS4C runtime '+pathkey)
    files=[manifest,deploy,package/'materialise_crops.py',Path(c['reconstruction_file']),Path(c['interpreter']),Path(c['codec_preload'])]
    files.extend(a/n for a in (attempt,smoke) for n in FILES)
    spec.update(binding_status='bound',context=c,census_manifest=dict(path=str(manifest),sha256=sha(manifest),code_id=base.name),files=[dict(path=str(p),sha256=sha(p)) for p in files])
