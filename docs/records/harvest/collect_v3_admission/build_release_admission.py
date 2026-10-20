"""ADMW2 offline snapshot builder. No detectors, OCR, live feature reads or writes.

Use the collector interpreter with PYTHONDONTWRITEBYTECODE=1. Geometry roots
are indexed by source path + source hash, then validated by the CP2 adapter.
W1 retains ADM4's extra qualified strata; W2 uses W2C1 plus carried CAPS4.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
import os
from pathlib import Path
import statistics
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT))
from greekocr.harvest import admission as adm
from greekocr.harvest import geometry_observations as geo
from greekocr.harvest import orientation_screen as orient
from greekocr.harvest import separator_inventory as sep
from greekocr.harvest.neighbour_words import neighbour_word_evidence
from PIL import Image
sys.path.insert(0, str(BASE/'seg'))
from greekocr.harvest.qualified_admission import compose as _compose, edge_diagnostic
from greekocr.harvest.application_identity import identity
APPLICATION_SHA=None
def compose(*args,**kwargs):
    result=_compose(*args,**kwargs)
    if APPLICATION_SHA is not None:result["application_manifest_sha256"]=APPLICATION_SHA
    return result

PROJECTS = Path.home()/'Projects'
SNAPSHOTS = PROJECTS/'collect-v3-data/snapshots'
EXCLUSIONS = PROJECTS/'greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_exclusions/release_exclusions.json'
LIVE = PROJECTS/'collect-v3-data/run'
DEFAULT_GEOMETRY = [BASE/'seg/CP3_geometry', BASE/'seg/CP4_geometry',
                    BASE/'seg/CP7_geometry', PROJECTS/'collect-v3-data/geometry_prep', LIVE/'cache/g1b']
C1 = {('bsb_poly1850','poly1850'), ('ia_poly1850','poly1850'),
      ('nlg','poly1850'), ('nlg','poly1900'), ('nlg','greek_poly'),
      ('serbia','cyrillic'), ('elstat','numerics_tables')}
W1_EXTRA = {('kosmopolis','poly1900'), ('kosmopolis','poly1850'), ('lekythos','poly1900')}
W2_SOURCES = {s for s,c in C1} | {'gazette_modern'}
DROP_ORDER = ('text_rules','merged','neighbour_words','orientation','geometry_unavailable','crossing','unresolved')
ACCEPTED_ADMISSION_SHA = '35f86f4bbbf89eac81f946790110376bf03acea9dc55517bc6e98c143600468b'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False, separators=(',',':'))


def included(r, tranche):
    if r.get('candidate_usable') is not True: return False
    pair = (r['source'], r['primary_class'])
    caps = r['primary_class']=='headings_caps' and (tranche=='W1' or r['source'] in W2_SOURCES)
    return pair in C1 or (tranche=='W1' and pair in W1_EXTRA) or caps or (
        pair==('gazette_modern','modern_scanned') and r.get('gazette_stratum')=='measured_1986_1990')


def exclusions(path):
    config = json.loads(path.read_text())
    excluded = set(); bindings = {str(path):sha(path)}; counts = {}
    for name, meta in sorted(config['classes'].items()):
        p = path.parent/meta['file']
        digest = sha(p)
        if digest != meta['sha256']: raise ValueError('exclusion sha mismatch: '+name)
        ids = {x.strip() for x in p.read_text().splitlines() if x.strip() and not x.lstrip().startswith('#')}
        if len(ids)!=meta['n']: raise ValueError('exclusion count mismatch: '+name)
        excluded.update(ids); counts[name]=len(ids); bindings[str(p)]=digest
    return excluded, bindings, counts


def snapshot(path, tranche, excluded):
    manifest = path.parent/'SHA256_20261018_0524.txt'
    declared = {line.split()[1].lstrip('*'):line.split()[0] for line in manifest.read_text().splitlines() if line.strip()}
    h=hashlib.sha256(); heights=defaultdict(list); selected=[]; counts=Counter(); seen=set()
    fields = ('id','page_id','source','primary_class','gazette_stratum','label','confidence','bbox',
              'crop_bbox','crop_sha256','crop_source_image','crop_source_sha256','measured_row_id','tranche')
    with path.open('rb') as stream:
        for line in stream:
            h.update(line)
            if not line.strip(): continue
            r=json.loads(line); counts['snapshot_rows']+=1
            if r['tranche']!=tranche: raise ValueError('snapshot tranche mismatch')
            height=adm._height(r)
            if height is not None: heights[adm._page_key(r)].append(height)
            if not included(r,tranche): continue
            counts['qualified_before_exclusions']+=1
            if r['id'] in excluded:
                counts['excluded']+=1; continue
            if r['id'] in seen: raise ValueError('duplicate population id')
            seen.add(r['id'])
            # Admission uses the registered primary class, as ADM4 does. The
            # collector's script_class is an inventory, not that policy class.
            selected.append({k:r[k] for k in fields if k in r})
    if h.hexdigest()!=declared[path.name]: raise ValueError('snapshot sha mismatch')
    medians={k:statistics.median(v) for k,v in heights.items()}
    return selected, medians, dict(counts), {str(path):h.hexdigest(),str(manifest):sha(manifest)}


def cache_index(dirs):
    index=defaultdict(list); audit=[]
    for root in dirs:
        root=Path(root).expanduser().resolve()
        item=dict(path=str(root),exists=root.exists(),receipts=0,invalid_receipts=0)
        if root.exists():
            for p in sorted(root.rglob('receipt.json')):
                try:
                    r=json.loads(p.read_text())
                    if r.get('schema')!=geo.SCHEMA: continue
                    key=(str(Path(r['source']).resolve()),r['source_sha256'])
                    index[key].append(p.parent); item['receipts']+=1
                except (OSError, ValueError, KeyError): item['invalid_receipts']+=1
        audit.append(item)
    return index,audit


def source_key(r):
    return (str(Path(r['crop_source_image']).resolve()),r['crop_source_sha256'])


def load_page(r,index):
    errors=[]
    for p in index.get(source_key(r),[]):
        try: return geo.load_cached_page(r['crop_source_image'],p,r['crop_source_sha256']), errors
        except (OSError, ValueError, KeyError, EOFError) as e: errors.append(dict(cache=str(p),reason=str(e)))
    return None,errors



def bucket():
    return dict(pre_screen_n=0,admitted_n=0,dropped_n=0,geometry_unavailable_n=0,
        orientation_unknown_n=0,orientation_not_run_n=0,edge_clip_candidate_n=0,edge_clip_unavailable_n=0,
        dropped_per_rule={k:0 for k in DROP_ORDER},first_drop={k:0 for k in DROP_ORDER})


def count(b,r):
    b['pre_screen_n']+=1; b['admitted_n']+=int(r['pass']); b['dropped_n']+=int(not r['pass'])
    for name in ('geometry_unavailable','orientation_unknown'):
        b[name+'_n']+=int(r[name])
    b['orientation_not_run_n']+=int(r['orientation_status']=='not_run')
    b['edge_clip_candidate_n']+=int(r['edge_clip_candidate'] is True)
    b['edge_clip_unavailable_n']+=int(r['edge_clip_candidate'] is None)
    for name in r['rules_failed']: b['dropped_per_rule'][name]+=1
    if r['rules_failed']: b['first_drop'][r['rules_failed'][0]]+=1


def finish_bucket(b):
    b['unavailable_share']=b['geometry_unavailable_n']/b['pre_screen_n'] if b['pre_screen_n'] else 0
    assert b['pre_screen_n']==b['admitted_n']+sum(b['first_drop'].values())
    assert b['dropped_n']==sum(b['first_drop'].values())
    return b


class Jsonl:
    def __init__(self,path):
        self.path=Path(path);self.temp=self.path.with_suffix(self.path.suffix+'.tmp');self.f=self.temp.open('wb')
        self.h=hashlib.sha256();self.n=0;self.size=0
    def write(self,r):
        data=(encode(r)+'\n').encode();self.f.write(data);self.h.update(data);self.n+=1;self.size+=len(data)
    def finish(self):
        self.f.close(); dest=self.path
        if self.size>50_000_000:
            dest=Path(str(self.path)+'.gz')
            with self.temp.open('rb') as src, dest.with_suffix('.gz.tmp').open('wb') as raw:
                with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as gz:
                    import shutil
                    shutil.copyfileobj(src,gz)
            dest.with_suffix('.gz.tmp').replace(dest); self.temp.unlink()
            if self.path.exists(): self.path.unlink()
        else:
            self.temp.replace(dest)
            stale=Path(str(self.path)+'.gz')
            if stale.exists(): stale.unlink()
        return dict(path=dest.name,rows=self.n,uncompressed_bytes=self.size,uncompressed_sha256=self.h.hexdigest(),sha256=sha(dest))


def observe_page_job(payload):
    rows, medians, index, tolerance = payload
    page, invalid = load_page(rows[0], index)
    context = {}
    if page:
        with Image.open(page['source']) as image: context['image'] = image.convert('L')
        context['separators'] = sep.prepare(page)
    decisions = [compose(r, medians.get(adm._page_key(r)), page, context, tolerance) for r in rows]
    print(f"observed {rows[0]['page_id']} rows={len(rows)} geometry={page is not None}", flush=True)
    return decisions, invalid, page['binding'] if page else None


def run(tranche,dirs,out=BASE,snapshots=SNAPSHOTS,registry=EXCLUSIONS,workers=4):
    from stage_crops import INTERPRETER
    global APPLICATION_SHA
    APPLICATION_SHA=identity()
    if not os.path.samefile(sys.executable,INTERPRETER): raise RuntimeError('collector interpreter required')
    if sha(Path(adm.__file__))!=ACCEPTED_ADMISSION_SHA: raise ValueError('admission differs from aa3d9067')
    excluded,exbindings,excounts=exclusions(Path(registry))
    index,cache_audit=cache_index(dirs)
    calibration=BASE/'seg/CP5pb_calibration.json'
    tolerance=json.loads(calibration.read_text())['selected_tolerance']['value']
    result={}
    for wave in (('W1','W2') if tranche=='all' else (tranche,)):
        population,medians,popcounts,inputs=snapshot(Path(snapshots)/f'{wave}_features_20261018_0524.jsonl',wave,excluded)
        inputs.update(exbindings);inputs[str(calibration)]=sha(calibration)
        name='w1_originals_v3_screened' if wave=='W1' else 'w2_originals_v3'
        names=[name]+(['gazette_w2_originals_v3'] if wave=='W2' else [])
        writers={n:(Jsonl(out/(n+'_admission.jsonl')),Jsonl(out/(n+'_admitted.jsonl'))) for n in names}
        totals={n:bucket() for n in names};groups={n:defaultdict(bucket) for n in names}
        bypage=defaultdict(list)
        for r in population: bypage[source_key(r)].append(r)
        errors=[];valid_pages=[]
        ordered = sorted(bypage.items())
        for key, rows in ordered: rows.sort(key=lambda r:r['id'])
        # Independent source-bound pages, same unchanged consumers. Submit only
        # geometry hits; missing-cache rows remain cheap, fail-closed parent work.
        from concurrent.futures import ProcessPoolExecutor
        import multiprocessing
        with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context('fork')) as pool:
            jobs = {key:pool.submit(observe_page_job,(rows,medians,index,tolerance))
                    for key,rows in ordered if key in index}
            for i,(key,rows) in enumerate(ordered,1):
                if key in jobs:
                    decisions,invalid,binding=jobs.pop(key).result()
                    errors.extend(invalid)
                    if binding: valid_pages.append(binding)
                else:
                    decisions=[compose(r,medians.get(adm._page_key(r)),None,{},tolerance) for r in rows]
                for r,d in zip(rows,decisions):
                    for n in names:
                        if n.startswith('gazette_') and r['source']!='gazette_modern':continue
                        writers[n][0].write(d)
                        if d['pass']:
                            admitted=dict(r,row_id=r['id'],label=d['label'],admission=d,crop='original')
                            writers[n][1].write(admitted)
                        count(totals[n],d);count(groups[n][r['source']+'|'+r['primary_class']],d)
                if i%10==0 or key in index: print(f'{wave} pages {i}/{len(bypage)} rows={len(rows)} admitted={totals[name]["admitted_n"]}',flush=True)
        for n in names:
            files=[w.finish() for w in writers[n]]
            receipt=dict(application_manifest_sha256=APPLICATION_SHA,schema='ADMW2-1',accepted_commit='aa3d9067',builder_sha256=sha(__file__),
                admission_sha256=sha(adm.__file__),implementation_binding=geo.implementation_binding(),
                tranche=wave,view='gazette subset of W2' if n.startswith('gazette_') else 'whole tranche',
                population=popcounts,registered_exclusion_classes=excounts,inputs=inputs,
                caps_ruling='W2 headings_caps carried by CAPS4 W1 qualification (abaa200c)',
                w2_strata_ruling='W2C1 ed074681; no W1-only kosmopolis/lekythos strata in W2',
                medians='all snapshot rows on page before population/exclusion drops; bbox height; admission primary_class',
                order='source path + sha, then row id',totals=finish_bucket(totals[n]),
                counts_per_source_class={k:finish_bucket(v) for k,v in sorted(groups[n].items())},
                rule_accounting='dropped_per_rule overlaps; first_drop disjoint in DROP_ORDER',drop_order=DROP_ORDER,
                geometry_roots=cache_audit,invalid_cache_attempts=errors,validated_pages=valid_pages,
                orientation_policy='regional; unknown admits for orientation only; not_run when geometry cache absent',
                edge_clip_policy='CP5pb component_hits, calibrated xh tolerance; diagnostic only; never gating',
                unresolved_policy='only definite composed KEEP admitted',network='OFF',readers_started=0,files=files)
            (out/(n+'_receipt.json')).write_text(json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
            result[n]=receipt['totals']; print(n,encode(receipt['totals']),flush=True)
    return result


def offline_guard():
    """No sockets/readers/detectors, no live feature opens or live mutations."""
    import greekocr.pages
    from greekocr.glyphs import orientation
    def forbidden(*a,**kw):raise RuntimeError('ADMW2: detector/reader/network forbidden')
    greekocr.pages.process_page=forbidden
    orientation._osd=orientation.recognizer_polarity=forbidden
    def audit(event,args):
        if event.startswith('socket.') or event=='subprocess.Popen': forbidden()
        if event=='open':
            path,mode,flags=args
            if isinstance(path,int):return
            p=Path(path).resolve()
            if p.is_relative_to(LIVE):
                if p.name=='features.jsonl':raise RuntimeError('live features forbidden')
                if flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):raise RuntimeError('live writes forbidden')
        if event in ('os.mkdir','os.remove','os.rmdir','os.rename','os.link','os.symlink','os.chmod','os.truncate'):
            for value in (args[:2] if event in ('os.rename','os.link','os.symlink') else args[:1]):
                if Path(value).resolve().is_relative_to(LIVE):raise RuntimeError('live mutation forbidden')
    sys.addaudithook(audit)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tranche',choices=('W1','W2','all'),required=True)
    parser.add_argument('--geometry',nargs='*',type=Path,default=DEFAULT_GEOMETRY)
    parser.add_argument('--workers',type=int,default=4,help='independent page processes; deterministic output order')
    args=parser.parse_args();offline_guard();run(args.tranche,args.geometry,workers=args.workers)

if __name__=='__main__':main()
