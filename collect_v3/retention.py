"""Source-weighted retained/temporary disk forecast, decimal GB, never a measurement of collection."""
from collections import defaultdict,Counter
from pathlib import Path
from .common import read_json,write_json,rows,disk_bytes,dumps
from .config import SPECS


def project(replay,out):
    replay=Path(replay);out=Path(out);by_source=defaultdict(list)
    bindings={r['page_id']:r for r in read_json(replay/'fixture_bindings.json')['pages']}
    aggregate={r['id']:r for r in rows(replay/'W1/features.jsonl')}
    for p in sorted((replay/'W1/pages').glob('*.json')):
        r=read_json(p);rr=r['rows'];binding=bindings[r['id']]
        compact={k:v for k,v in r.items() if k!='rows'}
        components=dict(page_raster=Path(r['image']).stat().st_size,google_response=Path(r['response']).stat().st_size,page_binding=len((dumps(compact)+'\n').encode()),crops=sum(Path(x['crop']).stat().st_size for x in rr),working_page_rows=p.stat().st_size-len((dumps(compact)+'\n').encode()),features=sum(len((dumps(aggregate[x['id']])+'\n').encode()) for x in rr))
        components['separated_exports']=components['features']
        components['detector_cache']=disk_bytes(binding['detector_cache'])
        by_source[r['source']].append(components)
    sources=[];totals=Counter();max_page_work=0
    retained_keys={'page_raster','google_response','page_binding'}
    for source,spec in SPECS.items():
        samples=by_source[source]
        projected={key:round(sum(r[key] for r in samples)/len(samples)*spec[0]) for key in samples[0]}
        totals.update(projected)
        max_page_work=max(max_page_work,max(sum(r[k] for k in ('crops','detector_cache','features')) for r in samples))
        sources.append(dict(source=source,pages=spec[0],witness_pages=len(samples),projected_retained_bytes={k:v for k,v in projected.items() if k in retained_keys},projected_regenerable_bytes={k:v for k,v in projected.items() if k not in retained_keys}))
    static=sum((out/name).stat().st_size for name in ('convention_context.json','exclusions_manifest.json','exclusions_index.json','W1_manifest.jsonl','W2_manifest.jsonl','W2_gazette_probe_qualified.jsonl') if (out/name).exists())
    # Control receipts/SQLite/catalogue bounds are not bulk crop derivatives.
    control_reserve=100_000_000
    retained=sum(totals[k] for k in retained_keys)+static+control_reserve
    regenerable=sum(v for k,v in totals.items() if k not in retained_keys)
    source_pdf_slot=160_000_000  # enforced HTTP body cap; one resolved/rendered item at a time
    # finalize writes the aggregate and one separated export per row, while
    # transient page rows still exist. Crops/detectors are removed per page.
    finalization_work=sum(totals[k] for k in ('working_page_rows','features','separated_exports'))
    review_work=disk_bytes(replay/'W1/c1')
    atomic_replacement=totals['features']  # interrupted/resumed finalization can replace an existing aggregate
    peak=retained+atomic_replacement+max(finalization_work+max_page_work+source_pdf_slot,totals['features']+totals['separated_exports']+review_work+max_page_work)
    receipt=dict(schema='collect-v3-retention-3',pages=sum(s[0] for s in SPECS.values()),storage_diet_default=True,prune_images_default=False,retained_GB=round(retained/1e9,2),regenerable_GB=round(regenerable/1e9,2),peak_working_set_GB=round(peak/1e9,2),required_raster_and_geometry_GB=round((totals['page_raster']+totals['google_response'])/1e9,2),retained_bytes={**{k:totals[k] for k in retained_keys},'static_portable':static,'control_metadata_reserve':control_reserve,'exceptional_unstable_source_pdfs':0},regenerable_bytes={k:v for k,v in totals.items() if k not in retained_keys},peak_components_bytes=dict(retained=retained,atomic_replacement_headroom=atomic_replacement,finalization_work=finalization_work,maximum_single_page_work=max_page_work,source_pdf_slot=source_pdf_slot,measured_C1_review_work=review_work),sources=sources,target_retained_GB=20,target_met=retained<=20e9,basis='Source-weighted means of three cached F2 pages/source; 6850 pages. One retained raster plus raw Google JSON per page. Hash/route receipts retained; rows/crops/cache/exports rebuilt offline.',source_pdf_policy='Delete stable-URL PDFs after durable render hash binding; resolve/render one item before next. PDFs without stable re-download URLs are retained as explicit exceptions.',limitations=['Projection, not measured collection disk use; page mix can change it.','Peak is disk occupancy including retained inputs and transient finalization; not process RAM.','100 MB control/SQLite reserve is an allowance, not a measured full-run size.','No unstable-URL PDF is budgeted for the frozen planned sources; any such discovered exception adds its measured bytes to retained and peak and requires re-projection.','C1 review workspace is measured on the 30-page replay, not a production review-size guarantee; clean-work removes copies after review while preserving checker files/keys.'])
    write_json(out/'retention_projection.json',receipt)
    return receipt

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--replay',required=True);p.add_argument('--output-root',default='docs/harvest/collect_v3');a=p.parse_args();r=project(a.replay,a.output_root);print(f"retained={r['retained_GB']}GB regenerable={r['regenerable_GB']}GB peak={r['peak_working_set_GB']}GB")
