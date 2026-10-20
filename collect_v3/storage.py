"""Hash-verified retained inputs and disposable local analysis products."""
from pathlib import Path
import shutil
from .common import read_json,write_json,sha,rows


def verify_page(record):
    for pathkey,hashkey in (('image','image_sha256'),('response','response_sha256')):
        if sha(record[pathkey])!=record[hashkey]:raise ValueError('retained '+pathkey+' hash mismatch')


def remove_tree(path,root):
    path=Path(path);root=Path(root).resolve()
    if path.is_symlink() or root not in path.resolve().parents:raise ValueError('refuse cleanup outside work root')
    if path.is_dir():shutil.rmtree(path)
    else:path.unlink(missing_ok=True)


def discard_page_work(record,cache,out):
    """Only derivatives of a durably bound raster/response may be removed."""
    verify_page(record)
    for r in record.get('rows',[]):
        if r.get('crop'):remove_tree(r['crop'],out)
    detector=Path(cache)/'g1b'/record['id']
    if detector.exists():remove_tree(detector,cache)


def textless(raw):
    document=raw.get('document') or {}
    return not document.get('text') or not any(p.get('lines') for p in document.get('pages',[]))


def page_rows(record,cache,out,context=None,serbian=True):
    if 'rows' in record:return record['rows']
    verify_page(record)
    from .pipeline import analyse
    page=dict(record['analysis_page'],image=record['image'])
    raw=read_json(record['response'])
    if textless(raw):return []  # Google found no text (blank leaf, plate): zero rows, as in the runner.
    result=analyse(page,raw,cache,Path(out)/record['tranche']/'crops',serbian=serbian,convention_context=context)
    for r in result:
        r['tranche']=record['tranche'];r['crop_source_image']=record['image'];r['crop_source_sha256']=record['image_sha256']
    discard_page_work(dict(record,rows=result),cache,out)
    return result


def compact(out,cache,tranche):
    """Retain inputs, binding/route receipts and checker verdicts; drop bulk work."""
    out=Path(out);cache=Path(cache);count=0
    # Validate every retained pair before deleting any work product.
    records=[(p,read_json(p)) for p in (out/tranche/'pages').glob('*.json')]
    for _,r in records:
        if r.get('status')=='completed':verify_page(r)
    for p,r in records:
        if r.get('status')!='completed':continue
        discard_page_work(r,cache,out)
        r.pop('rows',None);r['storage_policy']='one crop-source raster + raw Google response; derivatives disposable'
        write_json(p,r);count+=1
    for name in ('crops','page_previews','features.jsonl','candidates.jsonl','crop_tight_page.jsonl','excluded.jsonl','audits'):
        path=out/tranche/name
        if path.exists():remove_tree(path,out)
    # Never remove checker files or keys, whose ID mapping binds their judgments.
    for phase in ('c1','c2'):
        for name in ('crops','pages'):
            for path in (out/tranche/phase).glob('*/'+name):remove_tree(path,out)
    return dict(pages=count,raster_and_response_verified=True,regenerable_removed=True)


def verify_recipe(out,tranche):
    state=Path(out)/tranche/'state.json'
    if not state.exists():return
    identity=read_json(state)['identity'];base=Path(__file__).parent
    for field,name in {'pipeline_sha256':'pipeline.py','reader_sha256':'reader.py','assembly_sha256':'vendor/assembly_fix.py','conventions_sha256':'vendor/conventions.py','rules_sha256':'rules.py','lookalike_sha256':'vendor/lookalike_rule.py','classify_sha256':'vendor/classify.py','binding_sha256':'processor_binding.json'}.items():
        if field in identity and sha(base/name)!=identity[field]:raise ValueError('regeneration recipe changed: '+name)


def materialize(out,tranche,cache=None,serbian=True):
    """Rebuild exports without provider/Google calls; each page's crops are transient."""
    from .runner import finalize
    out=Path(out);cache=Path(cache or out/'cache')
    for wave in ('W1','W2') if tranche=='W2' else ('W1',):verify_recipe(out,wave)
    gate=None
    if tranche=='W2':
        from .runner import gate_sources
        sources=sorted({read_json(p)['source'] for p in (out/'W2/pages').glob('*.json')})
        gate=gate_sources(out/'c1_gate.json',sources)
    return finalize(out,tranche,gate=gate,serbian=serbian,cache=cache)


def ensure_crop(row):
    """Render only a requested review crop from its retained source raster."""
    from PIL import Image
    import io
    from .common import atomic_bytes,sha_bytes
    path=Path(row['crop'])
    if path.exists():
        if sha(path)!=row['crop_sha256']:raise ValueError('crop hash mismatch')
        return path
    with Image.open(row['crop_source_image']) as image:
        if sha(row['crop_source_image'])!=row['crop_source_sha256']:raise ValueError('crop source hash mismatch')
        crop=image.convert('L').crop(row['crop_bbox']);buf=io.BytesIO();crop.save(buf,format='PNG',compress_level=3)
    data=buf.getvalue()
    if sha_bytes(data)!=row['crop_sha256']:raise ValueError('regenerated crop hash mismatch')
    atomic_bytes(path,data);return path
