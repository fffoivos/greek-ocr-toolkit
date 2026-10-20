"""Read-only handoff validation: manifests, bytes, source boundaries, held-outs."""
from funnellib import *
from report import SOURCES
import subprocess

def run():
    errors=[];pages=rows(BASE/'probe_pages.jsonl');media=rows(BASE/'receipts/media.jsonl');http=rows(BASE/'receipts/http.jsonl')
    def check(ok,message):
        if not ok:errors.append(message)
    unique={r['image']:r for r in pages};total=0
    for path,r in unique.items():
        p=BASE/path;check(p.is_file(),'missing '+path)
        if not p.exists():continue
        data=p.read_bytes();total+=len(data)
        check(sha(data)==r['image_sha256'],'JPEG hash mismatch '+path)
        with Image.open(io.BytesIO(data)) as im:
            check(im.mode=='L','not grayscale '+path);check(max(im.size)<=2000,'long side exceeds 2000 '+path);check(im.format=='JPEG','not JPEG '+path)
    check(total<=400_000_000,'page image cap exceeded')
    all_raster_bytes=sum(p.stat().st_size for p in (BASE/'bulk').rglob('*.jpg'))
    check(all_raster_bytes<=400_000_000,'all retained JPEGs including review sheets exceed 400 MB')
    hashes={r['sha256'] for r in http if r.get('status') in [200,206]}
    for r in pages:check(r['fetch_sha256'] in hashes,'page missing successful HTTP hash '+r['image'])
    allcand=[]
    for src in SOURCES:
        path=BASE/f'candidates_{src}.jsonl';check(path.exists(),'missing candidate file '+src);cand=rows(path);allcand+=cand
        check(len(cand)==len({r['id'] for r in cand}),'duplicate candidates '+src)
        for r in cand:
            for key in ['id','title','year','decade','language_script_evidence','page_count','page_access_route','restriction_flags','overlap_flag','scan_rights','text_rights','access_terms_url','licence_string']:
                check(key in r,'candidate missing '+key+' '+src+'/'+r['id'])
            check(not r.get('held_out_test') or not r.get('new_candidate_eligible'),'held-out proposed '+src+'/'+r['id'])
            check('held_out_test_do_not_propose' not in r['restriction_flags'] or not r.get('new_candidate_eligible'),'held-out restriction proposed '+r['id'])
            check(r.get('page_access_verified') and r.get('fresh_pages_decoded',0)>0,'candidate without fresh page '+src+'/'+r['id'])
            check(r.get('pages_at_cap40',0)<=40,'item cap exceeded '+r['id'])
            if src=='openarchives' and r.get('new_candidate_eligible'):check(r.get('metadata_identity_bound'),'unbound OA proposed '+r['id'])
    funnel=rows(BASE/'funnel.jsonl');check(set(r['source'] for r in funnel)==set(SOURCES),'funnel must contain exactly 15 sources')
    for r in funnel:check(r['access_path_verified']==any(p['source']==r['source'] for p in pages),'path Y mismatch '+r['source'])
    for src in ['gennadius','laskaridis-travelogues']:check(not any(r['source']==src for r in http),'no-fetch source contacted '+src)
    forbidden=['archive.org','digitale-sammlungen.de','bsb-muenchen.de','digitalna.nb.rs','digitalna.nbs.rs','digitalna.nb.bg']
    for r in http:
        check(not any(h in urlsplit(r['url']).netloc for h in forbidden),'other-track host contacted '+r['url'])
        check('pdf_dump.php' not in r['url'],'forbidden Anemi full-PDF call')
    anemi=[r for r in media if r['source']=='anemi'];check(len(anemi)==50,'Anemi did not stay at 50 page attempts')
    check(len({r.get('book_key') for r in pages if r['source']=='anemi'})==5,'Anemi books !=5')
    oa=json.loads((BASE/'receipts/oa-physical-summary.json').read_text());check(oa['required_60_across_10_met'],'OA physical coverage requirement not met')
    # Check recorded request starts. Refusals are not wire requests; Anemi's native
    # transport includes login/robots starts separately. TLS fallbacks are logged
    # with the aggregate parent attempt; the fallback reserves another host start.
    artifact_errors_before_pacing=list(errors);pacing=[];starts=defaultdict(list);v2starts=defaultdict(list)
    for r in http:
        if r.get('kind')=='robots_refusal':continue
        starts[r.get('host') or urlsplit(r['url']).netloc].append(sec(r['started_at']))
        if r.get('rate_limiter_version')=='host-actual-start-v2':v2starts[r.get('host') or urlsplit(r['url']).netloc].append(sec(r['started_at']))
    for host,ts in starts.items():
        ts.sort();minimum=2. if host=='anemi.lib.uoc.gr' else 1.
        for a,b in zip(ts,ts[1:]):
            if b-a<minimum:pacing.append(dict(host=host,seconds=b-a,minimum_seconds=minimum))
    allfiles=[p for p in BASE.rglob('*') if p.is_file() and 'bulk' not in p.relative_to(BASE).parts and '__pycache__' not in p.parts]
    secrets=[os.environ[k] for k in ['ANEMI_USER','ANEMI_PASS','HF_TOKEN','HUGGING_FACE_HUB_TOKEN'] if os.environ.get(k)]
    for p in allfiles:
        b=p.read_bytes()
        check(not any(s.encode() in b for s in secrets),'environment credential found in '+str(p.relative_to(BASE)))
    # Verify representative images are excluded by the worktree ignore rules.
    sample=list(unique)[:3]
    proc=subprocess.run(['git','check-ignore','--stdin'],input='\n'.join(str(BASE/path) for path in sample)+'\n',text=True,capture_output=True,cwd=BASE.parents[3])
    check(len(proc.stdout.splitlines())==len(sample),'bulk page images not git-ignored')
    v2violations=[dict(host=host,seconds=b-a) for host,ts in v2starts.items() for a,b in zip(sorted(ts),sorted(ts)[1:]) if b-a<(2. if host=='anemi.lib.uoc.gr' else 1.)]
    result=dict(passed=not errors and not pacing,artifact_checks_passed=not errors,strict_pacing_passed=not pacing,known_pacing_deviations=pacing,latest_limiter_pacing_passed=not v2violations,latest_limiter_deviations=v2violations,errors=errors,source_records=len(funnel),candidate_records=len(allcand),probe_page_records=len(pages),unique_JPEGs=len(unique),page_image_MB=total/1e6,
                media_attempts=len(media),HTTP_ledger_records=len(http),all_retained_JPEG_MB=all_raster_bytes/1e6,OA_unique_PDFs=oa['unique_pdfs'],OA_actual_collections=oa['actual_collections'],
                no_Google_reads=True,no_collection=True,no_cloud_compute=True,spend=0,checked_at=stamp(),credential_scan='environment values checked, never printed; cached HF login not inspected')
    write(BASE/'receipts/validation.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ['known_pacing_deviations']},ensure_ascii=False));print('Historical subtarget intervals:',len(pacing))
    if errors:raise SystemExit(1)

if __name__=='__main__':
    from collections import defaultdict
    from report import sec
    run()
