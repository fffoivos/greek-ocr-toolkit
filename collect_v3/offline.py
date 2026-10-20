"""Network-blocked F2 replay and evidence production. No credentials are used."""
from __future__ import annotations
from collections import Counter,defaultdict
from contextlib import contextmanager
import json,os,shutil,socket,time
from pathlib import Path
from unittest.mock import patch
from .common import read_json,write_json,write_rows,rows,sha,atomic_bytes
from .config import SPECS,config,POLY
from .transport import HTTP,HostBucket
from .runner import run

@contextmanager
def no_network():
    def denied(*args,**kw):raise AssertionError('network forbidden in offline proof')
    with patch.object(socket.socket,'connect',denied),patch('socket.create_connection',denied),patch('socket.getaddrinfo',denied):yield

class VirtualClock:
    def __init__(self):self.now=1_800_000_000.
    def time(self):return self.now
    def sleep(self,seconds):self.now+=seconds

class MockDocAI:
    def __init__(self,fixtures,bucket=None):self.fixtures=fixtures;self.calls=0;self.images={r['page']['image_sha256']:r for r in fixtures};self.keys=[];self.bucket=bucket;self.events=[]
    def read(self,image):
        key=sha(image)
        start=self.bucket.acquire('eu-documentai.googleapis.com') if self.bucket else time.time()
        self.events.append(dict(host='eu-documentai.googleapis.com',start=start))
        self.calls+=1;self.keys.append(key)
        return read_json(self.images[key]['raw'])

class MockRoutes:
    def __init__(self,fixtures,http,cache):self.fixtures={r['page']['id']:r for r in fixtures};self.http=http;self.cache=Path(cache)
    def prune(self,page,item_complete=False):
        return self.http.evict(self.fixtures[page['id']]['url'])
    def fetch(self,draw):
        fixture=self.fixtures[draw['id']];p=dict(fixture['page']);data=self.http.get(fixture['url'])
        path=self.cache/'pages'/(p['id']+'.jpg');atomic_bytes(path,data);p.update(image=str(path),source=draw['source'],track=fixture['track'])
        return p

def fixtures(projects):
    import os
    if os.environ.get('COLLECT_V3_FIXTURE_ROOT'):
        from .portable import load
        return load(os.environ['COLLECT_V3_FIXTURE_ROOT'])
    projects=Path(projects);selected=[];overrides={};features=rows(projects/'greek-ocr-toolkit-sol-funnel-gr/docs/harvest/screen_v1/features.jsonl');fids={r['id'] for r in features}
    source_map={'ia_poly1850':('ia','poly1850'),'ia_greek_latin':('ia','greek_latin'),'ia_russian':('ia','cyrillic'),'bsb_poly1850':('intl','bsb'),'serbia':('intl','serbian'),'nlg':('gr','nlg-digital'),'kosmopolis':('gr','kosmopolis'),'lekythos':('gr','lekythos'),'gazette_poly1900':('gr','government-gazette'),'gazette_modern':('gr','government-gazette'),'elstat':('gr','elstat')}
    for source in SPECS:
        track,oldsource=source_map[source];base=projects/f'greek-ocr-toolkit-sol-funnel-{track}'/'docs/harvest/sample_v1'/track
        aggregate=rows(base/'lines.jsonl');overrides.update({r['id']:r for r in aggregate});pool=[]
        for page in rows(base/'pages.jsonl'):
            if page['source']!=oldsource:continue
            if source=='bsb_poly1850' and page.get('census_group')!='bsb_poly1850':continue
            if source=='gazette_poly1900' and not 1910<=page.get('year',0)<=1959:continue
            if source=='gazette_modern' and not 1982<=page.get('year',0)<=1990:continue
            if not (base/'bulk/lines'/(page['id']+'.jsonl')).exists():continue
            if not any(r['page_id']==page['id'] for r in features):continue
            parsed=base/'google/parsed/docai'/(page['image_sha256']+'.json')
            if not parsed.exists():continue
            rawpath=Path(read_json(parsed)['raw_json_path'])
            if not rawpath.exists():
                hits=list((base/'google/docai').rglob(rawpath.name))
                if len(hits)!=1:continue
                rawpath=hits[0]
            cache=base/'cache/g1b'/page['id']
            if not (cache/'receipt.json').exists():continue
            p=dict(page,image=str(base/page['image']))
            host='archive.org' if source.startswith('ia_') else 'api.digitale-sammlungen.de' if source.startswith('bsb') else 'digitalcollections.nlg.gr' if source=='nlg' else 'kosmopolis.library.upatras.gr' if source=='kosmopolis' else 'lekythos.library.ucy.ac.cy' if source=='lekythos' else 'ia37rg02wpsa01.blob.core.windows.net' if source.startswith('gazette') else 'dlib.statistics.gr' if source=='elstat' else 'digitalna.nb.rs'
            url=f'https://{host}/download/{page["item"]}/page/n{page["page"]}.jpg' if source.startswith('ia_') else f'https://{host}/offline-cached-F2/{page["id"]}.jpg'
            pool.append(dict(source=source,track=track,legacy_source=oldsource,page=p,raw=str(rawpath),detector_cache=str(cache),url=url))
        pick=sorted(pool,key=lambda r:r['page']['id'])[:3]
        if len(pick)!=3:raise ValueError(f'{source}: need 3 cached F2 pages; found {len(pick)}')
        selected.extend(pick)
    return selected,overrides,features

def prepare_mock(output,fixtures):
    output=Path(output);output.mkdir(parents=True,exist_ok=True);write_json(output/'OFFLINE_FIXTURE_ONLY.json',{'live_launch_allowed':False,'spend_usd':0});manifest=[]
    for f in fixtures:
        p=f['page'];manifest.append(dict(id=p['id'],source=f['source'],tranche='W1',item=p['item'],page=p['page'],seed=20261016,rights={'scope':'cached F2 offline test only'}))
    write_rows(output/'W1_manifest.jsonl',manifest)
    mapping={f['url']:Path(f['page']['image']) for f in fixtures}
    def sender(url):
        if url.endswith('/robots.txt'):return 200,{},b'User-agent: *\nAllow: /\n'
        if url not in mapping:raise AssertionError('mock HTTP cache miss; no network fallback')
        return 200,{'Content-Type':'image/jpeg'},mapping[url].read_bytes()
    vc=VirtualClock();bucket=HostBucket(output/'cache/hosts',clock=vc.time,sleep=vc.sleep)
    http=HTTP(output/'cache',sender=sender,bucket=bucket)
    return manifest,http,MockDocAI(fixtures,bucket),MockRoutes(fixtures,http,output/'cache')

def parity(output,selected,expected,projects):
    actual={r['id']:r for p in (Path(output)/'W1/pages').glob('*.json') for r in read_json(p).get('rows',[])}
    fixturepage={f['page']['id']:f for f in selected}
    import os
    stats=read_json(Path(os.environ['COLLECT_V3_FIXTURE_ROOT'])/'statistics.json') if os.environ.get('COLLECT_V3_FIXTURE_ROOT') else read_json(Path(projects)/'greek-ocr-toolkit-sol-funnel-gr/docs/harvest/screen_v1/receipts/statistics.json')
    marktags={(r['track'],r['source']):r['marks_correction_required'] for r in stats['sources']}
    comparisons=Counter();diff=[];checks=0;linecount=0;policy=Counter()
    fields=['id','page_id','item','year','source','track','crop_page_path','screen_decision','old_label','fixed_label','assembly_changed','dropped_token_ids','original_usable','admitted','codec_v1_pass','geometry_positive','crop_bbox','crop_sha256','page_median_row_height','height_ratio','label_density','google_line_contributors','google_paragraph_contributors','google_paragraph_ids','docai_line_index','xheight','xheight_method','body_component_count','ink_width','ink_pixels','projection_peaks','projection_peak_y','internal_gap_xh','crop_height_xh','token_count','token_row_clusters','token_y_spread_xh','density_ratio','fixed_text_gate_pass','fixed_usable','primary_class','label_after_conventions','roman_fixes','roman_ambiguous','long_s_label_count','text_exclusions','hyphen_test','next_column_line_id','join_evidence','tags','screen_reject','screen_reasons','usable_after_screen','usable_final','training_usable_final']
    for e in expected:
        if e['page_id'] not in fixturepage:continue
        linecount+=1;r=dict(actual[e['id']]);r.update(r['t4b_compatibility']);f=fixturepage[e['page_id']]
        # Frozen T4b compatibility view; production keeps retired screen flag-only
        # and applies the explicitly requested source-level marks policy.
        r['source']=f['legacy_source'];r['track']=f['track'];r['crop_page_path']=f['page']['image'];r['screen_decision']='reject_crop' if r['screen_reject'] else 'keep_crop'
        r['tags']=[t for t in r['tags'] if t!='marks_correction_required']
        if marktags[f['track'],f['legacy_source']]:r['tags'].append('marks_correction_required')
        r['tags']=sorted(set(r['tags']));r['usable_after_screen']=r['fixed_usable'] and not r['screen_reject'];r['usable_final']=r['usable_after_screen'] and not r['text_exclusions'];r['training_usable_final']=r['usable_final']
        r['label_after_conventions']=r['t4b_label_after_conventions']
        if actual[e['id']]['screen_merged']:policy['screen_flag_true']=policy.get('screen_flag_true',0)+1
        if set(actual[e['id']]['tags'])!=set(r['tags']):policy['explicit_source_marks_tag_change']+=1
        for field in fields:
            checks+=1;comparisons[field]+=1
            a=r.get(field);b=e.get(field)
            # Floating point operations may differ only at the last bit when
            # the provider geometry is reconstructed; record exact mismatches.
            if a!=b:diff.append(dict(id=e['id'],field=field,actual=a,expected=b))
    write_json(Path(output)/'parity_details.json',dict(lines=linecount,field_comparisons=checks,fields=dict(comparisons),differences=diff,explicit_W1_policy_changes=dict(policy),scope='Every listed field recomputed from saved raw DocAI, native page and cached detector; legacy tags use source-level T4b statistics. Human withholds/duplicate receipts are replayed from F2 line ledger.'))
    return dict(status='ok' if not diff else 'diff',lines=linecount,field_comparisons=checks,differences=len(diff),explicit_W1_policy_changes=dict(policy))

def replay(projects,output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    context=output.parent/'convention_context.json'
    if not context.exists():
        import os
        if os.environ.get('COLLECT_V3_FIXTURE_ROOT'):
            shutil.copyfile(Path(os.environ['COLLECT_V3_FIXTURE_ROOT'])/'convention_context.json',context)
        else:
            from .convention_context import build
            build(projects,context)
    shutil.copyfile(context,output/'convention_context.json')
    fs,overrides,expected=fixtures(projects);manifest,http,reader,routes=prepare_mock(output,fs)
    c=config(output_root=str(output),cache=str(output/'cache'),storage_diet=False)
    with no_network():result=run(c,'W1',list(SPECS),http=http,reader=reader,routes=routes,fixture_detector={f['page']['id']:f['detector_cache'] for f in fs},baseline_overrides=overrides)
    proof=parity(output,fs,expected,projects)
    write_json(output/'fixture_bindings.json',dict(pages=[dict(source=f['source'],page_id=f['page']['id'],image=f['page']['image'],image_sha256=f['page']['image_sha256'],raw=f['raw'],raw_sha256=sha(f['raw']),detector_cache=f['detector_cache']) for f in fs]))
    write_json(output/'mock_request_timing.json',dict(clock='injected virtual clock for replay; separate rate receipt uses real wall time',requests=http.events+reader.events))
    return dict(result=result,parity=proof,pages_per_source=dict(Counter(f['source'] for f in fs)),mock_http_requests=len(http.events),mock_docai_reads=reader.calls,network=False,provider_calls=0,spend_usd=0)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--projects-root',default=str(Path.home()/'Projects'));p.add_argument('--output',default='docs/harvest/collect_v3/offline_replay');a=p.parse_args()
    print(json.dumps(replay(a.projects_root,a.output)))
