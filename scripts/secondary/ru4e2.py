"""Offline RU4E2 census and RU4E protocol adapter. No reading during preparation."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys
import unicodedata
import importlib
# Own helper modules must be loaded before the shared RU4E engine imports them.
sys.path.insert(0, str(Path(__file__).resolve().parent/'ru4e2_bound'))
for _name in ('common','ru1_census','scan_packs','scan_rollout','ru1_map_answers','ru2t_coverage','ledger'):
    importlib.import_module(_name)
import ru4e as m
from ru1_census import cyr

ART = m.WORK/'artifacts/ru1/ru4e2'
PACK = Path('/private/tmp/ru4e2/sol_packs/ru4e')
BOUND = m.HERE/'ru4e2_bound'
WAVE = Path.home()/'Projects/greek-page-ocr-wave1c/out/e4/wave1c_readback/remote/out/e4'
METADATA = m.COLLECTION.parents[1]/'cyrillic/source_books.json'


def selected(r):
    return r.get('script_class', '').casefold() == 'cyrillic' or sum(cyr(c) for c in r['label']) >= 3


def census(sources=m.SOURCES, metadata=METADATA):
    meta = {r['source']: r for r in m.rows(metadata)} if metadata.suffix == '.jsonl' else {r['source']: r for r in json.loads(metadata.read_text())}
    data = [dict(r, ru4e_split=s) for s,p in sources.items() for r in m.rows(p) if selected(r)]
    books = defaultdict(list)
    for r in data: books[m.bid(r)].append(r)
    result=[]
    for b, rr in sorted(books.items()):
        text=''.join(r['label'] for r in rr).casefold()
        pp=[p for r in rr for p in m.positions(r['label']) if p['kind']=='final']
        signs=Counter(p['google'] for p in pp)
        historical={c:text.count(c) for c in 'ѣіѳѵ'}
        pre=signs['ъ']>=5 or any(historical.values())
        source=rr[0]['source']; metadata_record=meta.get(source,{})
        language=metadata_record.get('catalogue_language', 'ru' if source=='wikisource_ru' else 'unknown')
        result.append(dict(book=b, rows=len(rr), splits=dict(Counter(r['ru4e_split'] for r in rr)),
            language_guess=language, language_basis='catalogue_language' if metadata_record else 'source wikisource_ru',
            final_soft=signs['ь'], final_hard=signs['ъ'], historical=historical,
            orthography='pre_reform' if pre else 'other',
            caveat='Mechanical threshold only; isolated historical letters do not prove historical Russian orthography.' if signs['ъ']<5 else None))
    return data,result


def compare_wave(data, wave=WAVE):
    """Compare actual production scored IDs, both instruments and all six arms."""
    target={r['id']:r for r in data if r['ru4e_split']=='test'}
    class_target={i for i,r in target.items() if r.get('script_class')=='cyrillic'}
    comparisons=[]
    for job,arm in [('job01','ctrl'),('job02','lc')]:
        for seed in range(3):
            for view in ['v2_test','v2_test_full_coverage']:
                path=wave/'wave1c'/job/'predictions'/f'{arm}_s{seed}_{view}.jsonl'
                receipt=path.with_suffix('.receipt.json')
                rr=m.rows(path)
                cyrrows=[r for r in rr if r.get('script_class')=='cyrillic']
                ids={r['line_id'] for r in cyrrows}
                comparisons.append(dict(path=str(path),sha256=m.sha(path), receipt=str(receipt),receipt_sha256=m.sha(receipt),
                    view=view, scored_rows=len(cyrrows), unique_ids=len(ids),
                    equals_all_census_test=ids==set(target), equals_script_class_test=ids==class_target,
                    missing_from_scored=sorted(set(target)-ids), outside_census=sorted(ids-set(target))))
    manifest=wave/'wave1c_prep/manifest_fix1.json'
    return dict(matches=all(r['equals_all_census_test'] for r in comparisons),
                production_manifest=str(manifest),manifest_sha256=m.sha(manifest),comparisons=comparisons)


def configure():
    # Import the bound runtime independently so helper import provenance is owned.
    # Helpers are exact copies of the RU4E protocol; only output paths are rebound.
    m.BOUND=BOUND


def clean_crop(path, cache=None):
    """Remove PNG ancillary metadata, proving native decoded mode/size/pixels identical."""
    import hashlib
    from PIL import Image
    cache = cache or PACK.parent.parent/'native_cache'
    cache.mkdir(parents=True,exist_ok=True)
    with Image.open(path) as original:
        original.load()
        if original.mode not in ('1','L','LA','RGB','RGBA'):
            raise ValueError('unsupported native mode '+original.mode)
        mode,size,pixels=original.mode,original.size,original.tobytes()
        clean=Image.frombytes(mode,size,pixels)
    dest=cache/(m.sha(path)+'.png')
    if not dest.exists(): clean.save(dest)
    with Image.open(dest) as checked:
        checked.load()
        if checked.info or (checked.mode,checked.size,checked.tobytes()) != (mode,size,pixels):
            raise ValueError('native pixel preservation failed')
    return dest,dict(original_crop=str(path.resolve()),original_crop_sha256=m.sha(path),
                     native_pixel_sha256=hashlib.sha256(pixels).hexdigest(),native_mode=mode,native_size=list(size))


def build():
    configure()
    data,books=census()
    ART.mkdir(parents=True,exist_ok=True)
    if (ART/'build.json').exists(): raise ValueError('refuse build overwrite')
    m.jsonl(ART/'census_all_rows.jsonl',data)
    m.jsonl(ART/'census_by_book.jsonl',books)
    eligible={r['book']:r for r in books if r['orthography']=='pre_reform'}
    scope=ART/'scope.json';m.dump(scope,dict(books=eligible))
    ids={r['id'] for r in data if m.bid(r) in eligible}
    info=m.build(books_path=scope,art=ART,pack=PACK,selected_ids=ids,prepare_crop=clean_crop)
    m.dump(ART/'wave1c_comparison.json',compare_wave(data))
    # Bind adapter, census, metadata, and owned helpers to the production driver.
    info['inputs'].update(m.bindings([Path(__file__),METADATA,*BOUND.glob('*')]))
    info['inputs'].update(m.bindings([m.HERE/'run_ru4e2_all.sh',m.HERE/'ru4e2_finalize.sh']))
    info['pack_inputs'].update(m.bindings([ART/'census_all_rows.jsonl',ART/'census_by_book.jsonl',ART/'wave1c_comparison.json']))
    info['schema']='RU4E2-v1'
    m.dump(ART/'build.json',info)
    return info


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['build','drive','finalize'])
    p.add_argument('--dry-run',action='store_true')
    p.add_argument('--apply-lead',type=Path)
    args=p.parse_args();configure()
    if args.action=='build': result=build()
    elif args.action=='drive': result=m.drive(ART,PACK,dry_run=args.dry_run)
    else: result=m.finalize(ART,PACK,apply_lead=args.apply_lead)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
