"""Offline integrity/coverage validation, not rights or OCR-quality approval."""
import hashlib,json,pathlib,re,sys
from urllib.parse import unquote,urlsplit
from PIL import Image
from assessments import FACTS,RANKINGS
B=pathlib.Path(__file__).resolve().parent
(B/'receipts/local/validation.json').write_text('{"status":"RUNNING"}\n')
checks=[];failures=[]
def check(label,condition,detail=None):
    checks.append(dict(check=label,passed=bool(condition),detail=detail))
    if not condition:failures.append(label)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[json.loads(s) for s in (B/'sources.jsonl').read_text().splitlines()]
total=json.loads((B/'receipts/local/totals.json').read_text())
check('exact requested source coverage',len(rows)==len(FACTS) and {r['source_id'] for r in rows}==set(FACTS))
check('one record per source',len(rows)==len({r['source_id'] for r in rows}))
required=['exists','access_path','machine_path_verified','date_range','print_vs_digital_probe','target_classes','lines_per_page','overlap','rights','blocker','workaround','receipt_paths','aligned_proofread']
for r in rows:
    sid=r['source_id'];check(sid+' required fields',all(k in r for k in required))
    paths=r['receipt_paths'];check(sid+' receipt paths exist',all((B/p).is_file() for p in paths))
    check(sid+' page cap',r['print_vs_digital_probe']['pages']<=20)
    check(sid+' complete detector accounting',all(p['line_receipt'] and (B/p['line_receipt']).exists() for p in r['probe_pages']))
    for p in r['probe_pages']:
        image=B/p['image_path'];receipt=json.loads((B/p['receipt']).read_text());lines=json.loads((B/p['line_receipt']).read_text())
        check(sid+' raster hash '+image.name,sha(image)==receipt['sha256']==lines['image_sha256'])
        with Image.open(image) as im:
            check(sid+' decoded dimensions '+image.name,im.width==lines['width'] and im.height==lines['height'])
            check(sid+' single raster '+image.name,getattr(im,'n_frames',1)==1)
        check(sid+' detector count '+image.name,lines['non_discounted_lines']==sum(x['discounted'] is None for x in lines['lines']))
    expected_live=any(p['origin']=='new bounded HTTP raster probe' for p in r['probe_pages'])
    check(sid+' live-path evidence',(r['machine_path_verified']=='Y')==expected_live)
    check(sid+' all rights fields',all(k in r['rights'] for k in ['scan_rights','text_rights','access_terms_url','cloud_ocr_processing','retention_terms','training_use','redistribution_terms','owner_decisions']))

for p in B.glob('receipts/*/http/*.json'):
    r=json.loads(p.read_text());body=p.with_suffix('.body')
    check('HTTP stored body '+str(p.relative_to(B)),body.exists() and sha(body)==r['sha256'])
    check('HTTP no session headers '+str(p.relative_to(B)),not any(k.lower() in ['set-cookie','authorization','proxy-authorization'] for k in r.get('headers',{})))

for path,key,expected in [('sources','sources',len(rows)),('verified raster paths','verified_paths',sum(r['machine_path_verified']=='Y' for r in rows)),('aligned lead coverage','proofread_sources',sum(r['aligned_proofread'] is not None for r in rows)),('probe page total','probe_pages',sum(r['print_vs_digital_probe']['pages'] for r in rows)),('probe bytes total','probe_raster_bytes',sum(r['print_vs_digital_probe']['raster_bytes'] for r in rows)),('source rights decisions','owner_decisions',sum(len(r['rights']['owner_decisions']) for r in rows))]:check(path,total[key]==expected)
check('new/local raster byte conservation',total['new_network_image_bytes']+total['reused_local_image_bytes']==total['probe_raster_bytes'])
check('zero Anemi image probes',next(r for r in rows if r['source_id']=='anemi')['print_vs_digital_probe']['pages']==0)
check('zero Google Books image probes',next(r for r in rows if r['source_id']=='google-books')['print_vs_digital_probe']['pages']==0)
check('every requested category ranked',{x[0] for x in RANKINGS}=={x['category'] for x in json.loads((B/'receipts/local/plan-targets.json').read_text())['categories']})
check('target priorities refer to covered sources',all(s in FACTS for _,ss,_ in RANKINGS for s in ss))
for p in [B/'INVENTORY.md',B/'RIGHTS.md']:
    local=[]
    for u in re.findall(r'\]\(([^)]+)\)',p.read_text()):
        if '://' in u or u.startswith('#'):continue
        u=unquote(u.split('#')[0]);local.append(u)
    check(p.name+' local links',all((B/x).exists() for x in local),[x for x in local if not (B/x).exists()])
footer=(B/'INVENTORY.md').read_text().splitlines()[-1]
expected=f'S1: done | sources: {total["sources"]} verified_paths: {total["verified_paths"]} | proofread_sources: {total["proofread_sources"]} | probes: {total["probe_pages"]} pages {total["probe_MB_decimal"]:.3f} MB | owner_decisions: {total["owner_decisions"]} | top_pilots: '+ '; '.join(total['top_pilots'])
check('exact required footer',footer==expected)
for f in json.loads((B/'receipts/local/input-files.json').read_text()):
    if '/greekocr/' in f['path']:check('unchanged runtime input '+f['path'],sha(pathlib.Path(f['path']))==f['sha256'])
vis=json.loads((B/'receipts/local/visual-review.json').read_text())
for v in vis['fully_classified_detector_pages']:
    p=B/'receipts'/v['source']/(v['probe']+'-lines.json');r=json.loads(p.read_text());valid={x['index'] for x in r['lines'] if x['discounted'] is None}
    check('numbered within-line witness '+v['source'],set(v['positive_indices'])<=valid and len(v['positive_indices'])==len(set(v['positive_indices'])))
secret_hits=[]
for p in B.rglob('*'):
    if p.is_file() and p.suffix in ['.body','.json','.jsonl','.txt','.md']:
        data=p.read_bytes()
        if re.search(rb'hf_[A-Za-z0-9]{25,}|AIza[A-Za-z0-9_-]{25,}|"(?:set-cookie|authorization)"\s*:',data,re.I):secret_hits.append(str(p.relative_to(B)))
check('no token-shaped secrets or session headers',not secret_hits,secret_hits)
out=dict(status='PASS' if not failures else 'FAIL',checks=len(checks),failures=failures,limitations='Integrity, cap, provenance and arithmetic checks only. Not legal clearance, exact edition non-overlap, physical detector correctness, source-wide yield or reference release.',details=checks)
(B/'receipts/local/validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(out['status'],len(checks),'checks',len(failures),'failures')
if failures:print('\n'.join(failures));sys.exit(1)
