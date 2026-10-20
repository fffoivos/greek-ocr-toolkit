"""Build immutable benchmark candidates and historical references on a worker.

No OCR, model inference, new downloads, training, or filtering-policy changes.
Use existing lossless source adapters, native crop reconstruction and scorer.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import heapq
import json
import os
from pathlib import Path
import platform
import shutil
import time

from bench.benchmark_classes import classify
from bench.benchmark_suite import canonical
from bench.common import read_rows, sha256, write_json, write_rows
from bench.o2_select import spread
from train.cer import load_codec


def key(seed, *parts):
    return hashlib.sha256(canonical([seed,*parts]).encode()).hexdigest()


class Pools:
    """Bounded deterministic best-hash candidates per facet and source book."""
    def __init__(self, seed, per_book=42):
        self.seed, self.per_book = seed, per_book
        self.groups = defaultdict(lambda:defaultdict(list))
        self.counts = Counter()

    def add(self, row, groups):
        rank = int(key(self.seed,row['id']),16)
        for group in groups:
            self.counts[group] += 1
            heap = self.groups[group][row['doc']]
            entry = (-rank,row['id'],row)
            if len(heap) < self.per_book: heapq.heappush(heap,entry)
            elif entry[:2] > heap[0][:2]: heapq.heapreplace(heap,entry)

    def rows(self, group):
        return [entry[2] for heap in self.groups.get(group,{}).values() for entry in heap]


def choose(pool, taxonomy, split, excluded_crop_shas=()):
    selected, used, taken, pages = [], set(), defaultdict(int), Counter()
    used_crops=set(excluded_crop_shas)
    seed = taxonomy['seed']; mult = taxonomy['candidate_multiplier']
    cap = taxonomy['max_primary_lines_per_book']; page_cap = taxonomy['max_lines_per_page']
    divisor = 4 if split == 'dev' else 1
    targets = {k:v//divisor*mult for k,v in taxonomy['primary_targets'].items()}
    limit = sum(targets.values())

    def take(group, n, cell=None):
        # Stable page cap before the existing round-robin work spread.
        candidates, per_page, batch_crops = [], Counter(), set()
        for row in sorted(pool.rows(group),key=lambda r:key(seed,split,group,r['id'])):
            if cell is not None and row['primary'] != cell: continue
            if row['id'] in used or pages[row['page_id']]+per_page[row['page_id']] >= page_cap: continue
            crop=row.get('crop_sha256',row['id'])
            if crop in used_crops or crop in batch_crops: continue
            batch_crops.add(crop)
            per_page[row['page_id']] += 1; candidates.append(row)
        got = spread(candidates,min(n,limit-len(selected)),cap,taken,seed,split+'/'+group)
        for row in got:
            row = dict(row,candidate_split=split,selection_reason=group)
            selected.append(row);used.add(row['id']);used_crops.add(row.get('crop_sha256',row['id']));pages[row['page_id']] += 1

    for cell in sorted(targets,key=lambda c:(pool.counts['p:'+c],c)):
        # Meet rare facets WITHIN the cell budget before ordinary rows fill it.
        for facet,target in sorted(taxonomy['facet_test_targets'].items(),key=lambda kv:(pool.counts['f:'+kv[0]],kv[0])):
            remaining=targets[cell]-sum(r['primary']==cell for r in selected)
            missing=target//divisor*mult-sum(facet in r['facets'] for r in selected)
            if remaining>0 and missing>0:take('f:'+facet,min(remaining,missing),cell)
        remaining=targets[cell]-sum(r['primary']==cell for r in selected)
        if remaining>0:take('p:'+cell,remaining)
    # Overlay quotas use remaining slots. They are not additional release rows.
    for facet, target in taxonomy['facet_test_targets'].items():
        desired = target//divisor*mult
        have = sum(facet in r['facets'] for r in selected)
        if have < desired: take('f:'+facet,desired-have)
    # Unresolved Cyrillic language is an annotation queue, never a satisfied
    # Russian/Serbian/Bulgarian/Ukrainian primary quota.
    if len(selected) < limit: take('aux:cyrillic_unresolved',limit-len(selected))
    return sorted(selected,key=lambda r:r['id'])


def materialize(row, out, page_cache):
    from PIL import Image
    from greekocr.harvest.line_pipeline_native import reconstructed_crop, valid_box
    source = row.get('original_crop_path')
    if source and Path(source).is_file(): raw = Path(source).read_bytes()
    else:
        source = row.get('crop_source_image'); box = row.get('crop_bbox')
        if not source or not box: raise ValueError('missing reconstructable crop: '+row['id'])
        if source not in page_cache:
            if sha256(source) != row['source_page_sha256']: raise ValueError('changed source page')
            with Image.open(source) as image:
                image.load();page_cache[source] = image.copy()
            if len(page_cache) > 12:
                oldest = next(iter(page_cache));page_cache.pop(oldest).close()
        page = page_cache[source]
        if not valid_box(box,page.size): raise ValueError('invalid bound crop geometry')
        image, raw = reconstructed_crop(page,box,row.get('crop_color_mode','L'));image.close()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != row['crop_sha256']: raise ValueError('crop identity mismatch: '+row['id'])
    path = out/'images'/digest[:2]/(digest+'.png');path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists(): path.write_bytes(raw)
    row['crop_path'] = str(path.resolve())


def historical(config, out, taxonomy):
    """Reuse every reserved factory row, original label IDs and encoded PNG."""
    import pyarrow.parquet as pq
    panels, summary = {}, {}
    for item in config['historical']:
        mix_path = Path(item['mix']); mix = json.loads(mix_path.read_text())
        codec = load_codec(item['codec']); rows = []; seen = set(); shards = {}
        for component in mix['components']:
            folder = Path(component.get('shard_dir',component.get('build_dir')))
            if not folder.is_absolute(): folder = (mix_path.parent/folder).resolve()
            info = json.loads((folder/'build_info.json').read_text())
            for path in sorted((folder/'reserved').glob('shard-*.parquet')):
                digest = sha256(path);relative = str(path.relative_to(folder))
                expected = component.get('shard_sha256',info.get('shard_sha256',{})).get(relative)
                if not expected or digest != expected: raise ValueError('historical shard binding mismatch')
                shards[str(path)] = digest
                for batch in pq.ParquetFile(path).iter_batches(batch_size=256):
                    for record in batch.to_pylist():
                        identifier = record['line_id']
                        if identifier in seen: raise ValueError('duplicate historical line')
                        seen.add(identifier)
                        text = codec.decode(record['label_ids'])
                        if text != record['gt_nfd']: raise ValueError('historical reference/label IDs differ')
                        raw = record['image_png']; image_sha = hashlib.sha256(raw).hexdigest()
                        dest = out/'images'/image_sha[:2]/(image_sha+'.png');dest.parent.mkdir(parents=True,exist_ok=True)
                        if not dest.exists(): dest.write_bytes(raw)
                        row = dict(id=identifier,doc=record['source_doc_id'],text=text,
                            crop_path=str(dest.resolve()),crop_sha256=image_sha,
                            script_class=record['script_class'],width=record['width'],height=48,
                            font=record.get('font'),source=record.get('source_dataset'),
                            reference_status=item['reference_kind'],reference_source=str(path),
                            reference_encoding='existing factory label_ids decoded through bound reference codec',
                            source_split=record['split'],work_identity_status='unreviewed',
                            global_holdout_status='historical_benchmark_exposed',
                            crop_protocol='exact existing historical factory image_png; not a new crop')
                        row.update(classify(row)); row['strata'] = [row['primary'],*row['facets']]
                        rows.append(row)
        if len(rows) != item['expected_rows']: raise ValueError('historical population changed: '+item['id'])
        target = out/(item['id']+'.jsonl');write_rows(target,rows)
        panels[item['id']] = dict(path=target.name,sha256=sha256(target),rows=len(rows),scorable=True,
            reference_kind=item['reference_kind'],comparison_claim=item['comparison_claim'])
        summary[item['id']] = dict(rows=len(rows),mix=str(mix_path),mix_sha256=sha256(mix_path),
            codec_sha256=sha256(item['codec']),shards=shards,
            nfd_reference_units=sum(len(r['text']) for r in rows),
            primary_counts=dict(Counter(r['primary'] for r in rows)),
            facet_counts=dict(Counter(f for r in rows for f in r['facets'])))
        print('historical',item['id'],len(rows),flush=True)
    return panels, summary


def exposure_ids(value, *, id_is_line=False):
    """Typed known IDs only; never invent aliases across old IA namespaces."""
    lines, documents = set(), set()
    def add_slot(slot):
        if isinstance(slot,str) and ':t' in slot:lines.add(slot.rsplit(':t',1)[0])
    def visit(node):
        if isinstance(node,list):
            for item in node:visit(item)
        elif isinstance(node,dict):
            for field in ('line_id','row_id','source_line_id'):
                if isinstance(node.get(field),str):lines.add(node[field])
            if id_is_line and isinstance(node.get('id'),str):lines.add(node['id'])
            add_slot(node.get('slot_id'))
            for line in node.get('excluded_c1_line_ids',[]):
                if isinstance(line,str):lines.add(line)
            for slot in node.get('locked_slot_ids',[]):add_slot(slot)
            for field in ('development_documents','locked_documents'):
                for doc in node.get(field,[]):
                    if isinstance(doc,str):documents.add(doc)
            for item in node.values():
                if isinstance(item,(dict,list)):visit(item)
    visit(value)
    return lines,documents


def regression_inputs(config,out):
    """Archive scoped evidence without promoting heads/slots to whole lines."""
    exposed, documents, summary = set(), set(), []
    for n,item in enumerate(config.get('regression_sources',[])):
        path=Path(item['path'])
        if sha256(path)!=item['sha256']:raise ValueError('changed regression source')
        dest=out/'regression_evidence'/f'{n:02d}-{path.name}';dest.parent.mkdir(exist_ok=True)
        shutil.copyfile(path,dest)
        if item.get('format')=='jsonl':
            opener=gzip.open if str(path).endswith('.gz') else open
            with opener(path,'rt') as stream:records=[json.loads(line) for line in stream if line.strip()]
        elif item.get('format') in {'json_list','json'}:
            records=json.loads(path.read_text())
            if item['format']=='json_list' and not isinstance(records,list):raise ValueError('regression source is not the declared list')
        else:records=[]
        found,docs=exposure_ids(records,id_is_line=item.get('id_is_line',False))
        exposed.update(found);documents.update(docs)
        summary.append(dict(source=str(path),copied=str(dest.relative_to(out)),sha256=item['sha256'],
            truth_scope=item['truth_scope'],top_level_records=len(records),declared_line_identifiers=len(found),declared_document_identifiers=len(docs),
            full_line_transcription_gold=False))
    write_json(out/'tool_regression_manifest.json',dict(schema='ocr-tool-regression-sources-v1',
        status='development evidence; head/slot/word/decision scopes preserved',sources=summary,
        external_manifest_only=config.get('regression_external_manifests',[]),
        exposure_audit_complete=False,unresolved_memberships_remain_a_locked_release_blocker=True))
    return exposed,documents


def candidate_row(record, parent, metadata, index):
    from greekocr.harvest.line_pipeline_sources import canonicalize
    from greekocr.harvest.line_pipeline import expectations
    row = canonicalize(record,parent,metadata)
    bbox = row.get('crop_bbox');width = bbox[2]-bbox[0] if bbox else None;height = bbox[3]-bbox[1] if bbox else None
    try: expected = expectations(row,metadata)
    except ValueError: expected = {}
    langs = expected.get('languages',[])
    language = langs[0] if len(langs)==1 and langs[0] in {'el','ru','sr','bg','uk','la','en','fr','de','it'} else 'unknown'
    result = dict(id=parent['id']+'::'+row['id'],row_id=row['id'],parent_id=parent['id'],
        parent_sha256=parent['sha256'],source_record_index=index,
        source_record_sha256=hashlib.sha256(canonical(record).encode()).hexdigest(),
        proposal_text=row['raw_text'],raw_label=row['raw_text'],raw_label_field=row['raw_text_field'],
        raw_split=record.get('split'),canonical_split=row['split'],
        doc=row['book_id'],book_id=row['book_id'],edition_id=row['edition_id'],
        work_identity_status='unreviewed',canonical_work=None,global_holdout_status='unknown',
        page_id=row['page_id'],source=row['source'],year=row.get('year'),
        source_page_sha256=row.get('crop_source_sha256'),crop_sha256=row['crop_sha256'],
        original_crop_path=row.get('crop_path'),crop_source_image=row.get('crop_source_image'),crop_bbox=bbox,
        crop_color_mode=row.get('crop_color_mode','L'),width=width,height=height,
        primary_class=row.get('primary_class'),script_class=row.get('script_class'),
        language=language,language_expected=langs,orthography=expected.get('orthography','unknown'),
        expected_metadata=expected,reference_status='silver_teacher_proposal',reference_text=None,
        review_status='pending',selection_seed=None,development_exposures=[],
        reference_source=None,reference_offsets=None,reference_transformations=[],
        alignment_status='needs_same_edition_proofread_source',proofread_proposal_available=False,
        checkpoint_membership=None,codec_support_by_version={},
        source_revision=parent['sha256'],filter_decision_attached=None,production_admission_not_used=True)
    result.update(classify(result))
    return result


def checkpoint_inventory(config,out):
    entries,missing=[],[]
    for directory in config.get('checkpoint_roots',[]):
        root=Path(directory)
        if not root.exists():missing.append(directory);continue
        for binding_path in sorted(root.rglob('run_binding.json')):
            binding=json.loads(binding_path.read_text())
            weights=[]
            for pattern in ('best.pt','best.safetensors','best.ckpt'):
                for path in binding_path.parent.rglob(pattern):
                    weights.append(dict(path=str(path),sha256=sha256(path),bytes=path.stat().st_size))
            entries.append(dict(run_id=str(binding_path.parent.relative_to(root)),family_root=str(root),
                run_binding_path=str(binding_path),run_binding_sha256=sha256(binding_path),
                weights=weights,bound_run_metadata=binding,provenance_complete=False,
                membership_status='requires_expanded_training_tuning_work_and_corrector_audit'))
    write_json(out/'historical_checkpoint_inventory.json',dict(status='PARTIAL_INVENTORY',
        entries=entries,missing_roots=missing,
        note='Bindings are inventoried, not certified complete lineage. No unknown checkpoint is declared unseen.'))
    return entries


def build(config, out):
    if platform.system() == 'Darwin': raise RuntimeError('build on CSCS; MacBook is coordination-only')
    if not os.environ.get('SLURM_JOB_ID'): raise RuntimeError('benchmark build requires a Slurm worker')
    out = Path(out)
    if out.exists(): raise ValueError('immutable build output exists; use a fresh attempt')
    out.mkdir(parents=True);started = time.monotonic()
    taxonomy = json.loads(Path(config['taxonomy']).read_text())
    write_json(out/'inputs.json',config);write_json(out/'taxonomy.json',taxonomy)
    metadata = json.loads(Path(config['filter_config']['metadata']).read_text())
    parents = config['filter_config']['parents']
    for parent in parents:
        if sha256(parent['path']) != parent['sha256']: raise ValueError('changed raw parent')
    exposed_books, exposed_crops, owner_books = set(), set(), set()
    owners = json.loads(Path(config['owner_ratings']).read_text())['ratings']
    owner_by_id = {r['id']:r for r in owners}
    corrective_exposed,corrective_documents=regression_inputs(config,out)
    development_ids=set(owner_by_id)|corrective_exposed
    from greekocr.harvest.line_pipeline_census import records
    from greekocr.harvest.line_pipeline_sources import canonicalize
    # Known training/tuning exposure guards; absence is NOT a complete
    # historical checkpoint audit or canonical-work/mirror reconciliation.
    for parent in parents:
        for _, record in records(parent['path']):
            exposed_parent = parent.get('split') in {'train','dev'}
            row = canonicalize(record,parent,metadata)
            if exposed_parent:
                exposed_books.add(row['book_id']);exposed_crops.add(row['crop_sha256'])
            if record['id'] in development_ids: owner_books.add(row['book_id'])
            if row['book_id'] in corrective_documents:owner_books.add(row['book_id'])
    pools = {s:Pools(taxonomy['seed'],taxonomy['max_primary_lines_per_book']) for s in ('test','dev')}
    totals, primary, facets, rejection, source, known_exposure = Counter(),Counter(),Counter(),Counter(),Counter(),Counter()
    owner_rows = {}; unknown = Counter();resolved_corrective_ids=set();resolved_corrective_docs=set()
    index_path = out/'population_index.jsonl.gz'
    with gzip.open(index_path,'wt',encoding='utf-8') as stream:
        for parent in parents:
            count = 0
            for index, record in records(parent['path']):
                count += 1;row = candidate_row(record,parent,metadata,index)
                totals[parent['id']] += 1;primary[row['primary']] += 1;source[row['source']] += 1
                facets.update(row['facets']);rejection.update(record.get('rejection_reasons',[]))
                if row['language']=='unknown': unknown['language'] += 1
                if row['edition_id'].startswith('unresolved:'): unknown['edition'] += 1
                exposure = []
                if row['doc'] in exposed_books: exposure.append('known_training_or_tuning_book')
                if row['crop_sha256'] in exposed_crops: exposure.append('known_training_or_tuning_crop')
                if row['doc'] in owner_books: exposure.append('owner_or_corrective_development_book')
                if row['row_id'] in corrective_exposed: exposure.append('corrective_development_witness')
                if row['row_id'] in corrective_exposed:resolved_corrective_ids.add(row['row_id'])
                if row['doc'] in corrective_documents:resolved_corrective_docs.add(row['doc'])
                if row['row_id'] in owner_by_id:
                    exposure.append('owner_reviewed_development_witness');owner_rows[row['id']] = dict(row,reference_verdict=owner_by_id[row['row_id']]['decision'],annotation=owner_by_id[row['row_id']],reference_scope='segmentation only; not full transcription')
                if parent.get('split')=='test': exposure.append('historical_test_selection_exposed')
                row['development_exposures'] = exposure
                if exposure: row['global_holdout_status']='known_exposed'
                known_exposure.update(exposure)
                stream.write(canonical(dict(id=row['id'],parent_id=parent['id'],record_index=index,
                    book_id=row['doc'],primary=row['primary'],facets=row['facets'],known_exposures=exposure))+'\n')
                # Only acquisition populations not already train/dev or legacy
                # test enter the fresh candidate pool. Unknown work identity
                # still quarantines every candidate from locked release.
                if parent.get('split') in {'train','dev','test'} or exposure: continue
                split = 'dev' if int(key(taxonomy['seed'],'book-split',row['doc']),16)%5==0 else 'test'
                groups = ['p:'+row['primary'],*('f:'+f for f in row['facets'])]
                if row['primary'] in {'cyrillic_unresolved','russian_unresolved'}: groups.append('aux:cyrillic_unresolved')
                pools[split].add(row,groups)
            if count != parent['rows'] or sha256(parent['path']) != parent['sha256']:
                raise ValueError('raw parent count/hash changed while reading')
            write_json(out/'progress.json',dict(stage='candidate_inventory',rows=sum(totals.values()),parents=dict(totals)))
            print('inventoried',parent['id'],count,flush=True)
    if sum(totals.values()) != config['expected_raw_rows']: raise ValueError('raw denominator mismatch')
    selected = {'test':choose(pools['test'],taxonomy,'test')}
    selected['dev']=choose(pools['dev'],taxonomy,'dev',{r['crop_sha256'] for r in selected['test']})
    if {r['doc'] for r in selected['test']} & {r['doc'] for r in selected['dev']}:
        raise ValueError('candidate source-book split overlap')
    page_cache = {}
    all_rows = {r['id']:r for rows in selected.values() for r in rows}
    all_rows.update(owner_rows)
    # Segmentation candidates come from the same raw candidate supply, never
    # accepted rows only, and their predicted appearance is NOT ground truth.
    seg_pool = {r['id']:r for pool in pools.values() for group in pool.groups for r in pool.rows(group)}
    unique_seg={}
    for row in sorted(seg_pool.values(),key=lambda r:r['id']):unique_seg.setdefault(row['crop_sha256'],row)
    seg = spread(list(unique_seg.values()),taxonomy['segmentation_candidate_target'],8,defaultdict(int),taxonomy['seed'],'segmentation')
    seg = [dict(r,reference_verdict='UNRESOLVED',review_status='pending',panel='segmentation_candidates') for r in seg]
    all_rows.update({r['id']:r for r in seg})
    for n,row in enumerate(all_rows.values(),1):
        materialize(row,out,page_cache)
        if n%100==0:write_json(out/'progress.json',dict(stage='crop_materialization',processed=n,total=len(all_rows)))
    for image in page_cache.values(): image.close()
    panels, hist = historical(config,out,taxonomy)
    coverage = {}
    for split, rows in selected.items():
        for row in rows:
            row['crop_path'] = all_rows[row['id']]['crop_path'];row['selection_seed']=taxonomy['seed']
        name = 'recognition_'+split+'_candidates';target = out/(name+'.jsonl');write_rows(target,rows)
        panels[name] = dict(path=target.name,sha256=sha256(target),rows=len(rows),scorable=False,
            reference_kind='unreviewed_silver_proposals',comparison_claim='candidate coverage only')
        divisor = 4 if split=='dev' else 1
        counts = Counter(r['primary'] for r in rows)
        coverage[split] = dict(rows=len(rows),books=len({r['doc'] for r in rows}),
            primary={cell:dict(final_target=n//divisor,candidate_target=n//divisor*3,
                selected=counts[cell],locked_ready=0,shortfall=max(0,n//divisor*3-counts[cell])) for cell,n in taxonomy['primary_targets'].items()},
            auxiliary_primary_counts={k:v for k,v in counts.items() if k not in taxonomy['primary_targets']},
            facet_candidates=dict(Counter(f for r in rows for f in r['facets'])),
            facet_deficits={f:dict(candidate_target=n//divisor*3,selected=sum(f in r['facets'] for r in rows),
                raw_eligible_supply=pools[split].counts['f:'+f],shortfall=max(0,n//divisor*3-sum(f in r['facets'] for r in rows))) for f,n in taxonomy['facet_test_targets'].items()},
            reviewed_facet_counts=dict(Counter(f for r in rows for f in r['reviewed_facets'])),
            global_locked_ready=0)
    for name, rows in [('owner_regression',list(owner_rows.values())),('segmentation_candidates',seg)]:
        for row in rows: row['crop_path'] = all_rows[row['id']]['crop_path']
        target=out/(name+'.jsonl');write_rows(target,rows)
        panels[name] = dict(path=target.name,sha256=sha256(target),rows=len(rows),scorable=False,
            reference_kind='owner_development_segmentation' if name=='owner_regression' else 'unreviewed_segmentation',comparison_claim='segmentation task only')
    write_json(out/'historical_panels.json',hist)
    write_json(out/'candidate_coverage.json',dict(raw_rows=sum(totals.values()),by_parent=dict(totals),
        observed_primary=dict(primary),observed_facets=dict(facets),source_counts=dict(source),
        preexisting_rejections_counted_not_applied=dict(rejection),unknown_metadata=dict(unknown),
        known_exposure_counts=dict(known_exposure),selection=coverage,
        corrective_exposure_mapping=dict(declared_line_ids=len(corrective_exposed),resolved_line_ids=len(resolved_corrective_ids),
            unresolved_line_ids=sorted(corrective_exposed-resolved_corrective_ids),
            unresolved_document_ids=sorted(corrective_documents-resolved_corrective_docs)),
        bounded_draw_shortfall_is_not_absence_proof=True,
        owner_regression_rows=len(owner_rows),owner_ratings_unresolved_ids=sorted(set(owner_by_id)-{r['row_id'] for r in owner_rows.values()}),
        source_hashes={p['id']:p['sha256'] for p in parents},index_sha256=sha256(index_path)))
    candidates = [r for rows in selected.values() for r in rows]
    write_rows(out/'same_edition_alignment_queue.jsonl',[dict(id=r['id'],book_id=r['doc'],
        edition_id=r['edition_id'],page_id=r['page_id'],source=r['source'],year=r['year'],
        language_expected=r['language_expected'],alignment_status=r['alignment_status'],
        proofread_proposal_available=False,raw_google_is_not_independent_reference=True) for r in candidates])
    write_rows(out/'holdout_quarantine.jsonl',[dict(id=r['id'],book_id=r['doc'],canonical_work=None,
        global_holdout_status=r['global_holdout_status'],reasons=['canonical_work_and_every_checkpoint_audit_unresolved','literal_reference_pending']) for r in candidates])
    write_json(out/'provisional_work_reservations.json',dict(status='provisional source-book reservation; canonical-work identity unresolved',
        training_must_exclude_before_any_use=True,not_applied_to_running_filter_job=True,
        test_books=sorted({r['doc'] for r in selected['test']}),dev_books=sorted({r['doc'] for r in selected['dev']})))
    review_batches=[]
    for split, rows in selected.items():
        for start in range(0,len(rows),40):
            batch=rows[start:start+40];name=f'{split}-{start//40:03d}'
            write_rows(out/'review_batches'/(name+'.jsonl'),[dict(id=r['id'],crop_path=r['crop_path'],crop_sha256=r['crop_sha256'],language_context=r['language_expected'],page_id=r['page_id']) for r in batch])
            review_batches.append(dict(id=name,split=split,rows=len(batch),path='review_batches/'+name+'.jsonl',blind=True,proposal_hidden=True))
    write_json(out/'review_batches.json',dict(batch_size=40,batches=review_batches,readers=2,
        rule='blind pixels first; show source proposal only in a later verification phase; disagreements remain unresolved'))
    with (out/'verification_template.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=['id','text_verified','status','canonical_work','identity_evidence','language','orthography','reference_source','reviewer','uncertainty_reason']);writer.writeheader()
        for row in candidates: writer.writerow(dict(id=row['id'],status='pending'))
    checkpoints=checkpoint_inventory(config,out)
    write_json(out/'checkpoint_registry.json',dict(status='INCOMPLETE',required_families=config['checkpoint_families'],
        checkpoint_inventory='historical_checkpoint_inventory.json',inventoried_runs=len(checkpoints),
        known_training_tuning_source_books=sorted(exposed_books),
        known_owner_development_source_books=sorted(owner_books),
        reason='No complete all-historical-checkpoint training/tuning/corrector exposure registry was provided; unknown is not unseen.'))
    write_json(out/'locked_release_status.json',dict(status='NOT_READY',locked_rows=0,
        gates=dict(exact_inputs_and_selected_crops='PASS',raw_denominator='PASS',
            class_coverage='candidate counts only; see explicit deficits',literal_reference='PENDING',
            canonical_work_identity='PENDING',every_checkpoint_membership='PENDING',
            new_segmentation_truth='PENDING',historical_panels='FROZEN_SCORABLE'),
        no_gold_claim=True,no_training_launched=True))
    suite=dict(schema='ocr-benchmark-suite-v1',version='0.1',taxonomy=taxonomy,panels=panels,
        status='built historical suite and candidate/coverage release; new locked gold NOT_READY',
        references_not_filtered_per_model=True,selection_not_conditioned_on_filter=True,
        crop_store='images',inputs_sha256=sha256(out/'inputs.json'),
        coverage_sha256=sha256(out/'candidate_coverage.json'),
        elapsed_seconds=time.monotonic()-started,slurm_job_id=os.environ['SLURM_JOB_ID'])
    write_json(out/'suite.json',suite)
    write_json(out/'progress.json',dict(stage='completed',historical_rows=sum(v['rows'] for k,v in panels.items() if k.startswith('historical_')),
        candidate_rows=len(candidates),locked_gold_rows=0,raw_rows=sum(totals.values())))
    return suite


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--config',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();suite=build(json.loads(args.config.read_text()),args.out)
    print(canonical(dict(status=suite['status'],panels={k:v['rows'] for k,v in suite['panels'].items()})))


if __name__=='__main__':main()
