"""One-book schema probe only, not the production registry builder.

Example (after the read-only remote probe):
  python3 out/runner4/hf_one_book_probe.py --root /private/tmp/runner4-hf-book-20261022
The root must already contain remote.json and Scripts-14.0.0.txt. Source rasters
and responses stay in their original locations. Only four small tables and an
analysis SQLite file are materialised outside Git. No network/upload/job calls.
"""
import argparse
from bisect import bisect_right
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import platform
import random
import sqlite3
import struct
import subprocess
import time
import unicodedata as ud

import pyarrow as pa
import pyarrow.parquet as pq

REPO = next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').exists() and (p/'.git').exists())
COLLECT = Path('/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data')
BOOK = 'bsb_poly1850--027215cc6d2a7e8a'
FEATURE_VERSION = 'runner4-hf-probe-v1'


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def file_info(p):
    b = p.read_bytes()
    return dict(path=str(p), bytes=len(b), sha256=hashlib.sha256(b).hexdigest())


def image_dimensions(p):
    """Native PNG/JPEG header dimensions; no decoder or image re-encoding."""
    with p.open('rb') as f:
        head=f.read(24)
        if head[:8]==b'\x89PNG\r\n\x1a\n':
            return struct.unpack('>II',head[16:24])
        assert head[:2]==b'\xff\xd8'
        f.seek(2)
        while True:
            marker=f.read(1)
            if not marker: raise ValueError('JPEG has no SOF')
            if marker!=b'\xff': continue
            while marker==b'\xff': marker=f.read(1)
            if marker[0] in (0xd8,0xd9): continue
            n=struct.unpack('>H',f.read(2))[0]
            if marker[0] in (0xc0,0xc1,0xc2,0xc3):
                v=f.read(5);height,width=struct.unpack('>HH',v[1:]);return width,height
            f.seek(n-2,1)


class Features:
    def __init__(self, scripts):
        self.codec_path = REPO/'greekocr/_vendor/codec/v2.json'
        self.codec = json.loads(self.codec_path.read_text())
        self.atoms = {a['ch']:a for a in self.codec['atoms']}
        self.excluded = {c for c,a in self.atoms.items() if a['kind'] in ('punct','sym','space','digit')}
        self.punctuation = {c for c,a in self.atoms.items() if a['kind']=='punct'}
        self.ranges = []
        for line in scripts.read_text().splitlines():
            line = line.split('#')[0].strip()
            if not line:
                continue
            span, name = (s.strip() for s in line.split(';'))
            edges = span.split('..')
            self.ranges.append((int(edges[0],16),int(edges[-1],16),name))
        self.ranges.sort()
        self.starts = [r[0] for r in self.ranges]
        self.provenance = dict(feature_version=FEATURE_VERSION, unicode_version=ud.unidata_version,
            scripts=file_info(scripts),codec=file_info(self.codec_path),
            letter_method='codec-aware NFD-base/name; mirrored text_primitives.codec_letter_script',
            helper=file_info(REPO/'greekocr/harvest/text_primitives.py'))
        assert ud.unidata_version == '14.0.0', 'pin Scripts.txt to this Python Unicode version'

    def letter(self, c):
        if c in self.excluded or not ud.category(c).startswith('L'):
            return None, None
        for base in ud.normalize('NFD',c):
            if ud.category(base).startswith('M'):
                continue
            atom = self.atoms.get(base)
            if atom is not None:
                if atom['kind'] != 'base':
                    return None, None
                bucket = {'grek':'greek','latn':'latin','cyrl':'cyrillic'}.get(atom['script'],'other')
            else:
                bucket = next((s.lower() for s in ('GREEK','LATIN','CYRILLIC') if s in ud.name(base,'')), 'other')
            if bucket != 'other':
                return bucket, {'greek':'Greek','latin':'Latin','cyrillic':'Cyrillic'}[bucket]
            i = bisect_right(self.starts,ord(base))-1
            name = self.ranges[i][2] if i>=0 and ord(base)<=self.ranges[i][1] else 'Unknown'
            return bucket, name if name not in ('Common','Inherited') else None
        return None, None

    def compute(self, text, languages):
        nfc = ud.normalize('NFC',text)
        counts = Counter(); scripts = set(); polytonic = False
        for c in nfc:
            if c.isspace():
                continue
            if ud.category(c)=='Nd':
                counts['digits'] += 1
            elif ud.category(c).startswith('P') or c in self.punctuation:
                counts['punctuation'] += 1
            else:
                bucket, name = self.letter(c)
                counts[bucket or 'other'] += 1
                if name: scripts.add(name)
        greek_base = False
        for c in ud.normalize('NFD',text):
            if ud.category(c).startswith('M'):
                polytonic |= greek_base and ord(c) in (0x313,0x314,0x342,0x345,0x300)
            else:
                greek_base = self.letter(c)[0]=='greek'
        denom = sum(counts.values())
        r = dict(length_chars=len(nfc),length_raw_codepoints=len(text),nonspace_chars=denom,
                 polytonic_marks_present=polytonic,numbers_present=counts['digits']>0,
                 has_capitals=any(ud.category(c) in ('Lu','Lt') for c in text),
                 all_caps=any(c.lower()!=c.upper() for c in text) and not any(c.islower() for c in text),
                 mixed_script=len(scripts)>1,named_scripts=sorted(scripts))
        for bucket in ('greek','latin','cyrillic','digits','punctuation','other'):
            r[bucket+'_count'] = counts[bucket]
            r[bucket+'_pct'] = 100*counts[bucket]/denom if denom else 0.0
        heuristic = 'mul' if len(scripts)>1 else ({'Greek':'el','Latin':'und-Latn','Cyrillic':'und-Cyrl'}.get(next(iter(scripts)), 'und') if scripts else 'und')
        available = [(x['languageCode'],float(x['confidence']) if x.get('confidence') is not None and math.isfinite(float(x['confidence'])) else None) for x in languages if x.get('languageCode')]
        if available:
            code, conf = sorted(available,key=lambda x:(-(x[1] if x[1] is not None else -math.inf),x[0]))[0]
            r.update(language_guess=code,language_guess_confidence=conf,language_guess_method='google_detectedLanguages')
        else:
            r.update(language_guess=heuristic,language_guess_confidence=None,language_guess_method='script-tag-v1')
        r.update(script_language_guess=heuristic,script_language_confidence=None)
        return r


def sql_store(db, name, table):
    # Preserve scalar queryability and JSON-encode the few nested provenance fields.
    types = {f.name:('INTEGER' if pa.types.is_integer(f.type) or pa.types.is_boolean(f.type) else 'REAL' if pa.types.is_floating(f.type) else 'TEXT') for f in table.schema}
    db.execute('CREATE TABLE '+name+' ('+','.join('"'+k+'" '+v for k,v in types.items())+')')
    def scalar(v):
        return canonical(v) if isinstance(v,(list,dict)) else v
    db.executemany('INSERT INTO '+name+' VALUES ('+','.join('?' for _ in types)+')',
                   [[scalar(r.get(k)) for k in types] for r in table.to_pylist()])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--book-registry',type=Path,required=True)
    args = parser.parse_args(); root = args.root.resolve()
    assert not root.is_relative_to(REPO), 'data must remain outside Git'
    start = time.perf_counter()
    registry_path = args.book_registry.resolve()
    registry_records = pq.read_table(registry_path).to_pylist()
    matching_books = [r for r in registry_records if any(a['namespace']=='line_id_prefix' and a['value']==BOOK for a in r['aliases'])]
    assert len(matching_books)==1, 'source book must join exactly one canonical book'
    canonical_book = matching_books[0]
    assert not canonical_book['conflict'] and canonical_book['exportable'], 'book split conflict blocks export'
    registry_info = file_info(registry_path)
    instrument_path = registry_path.with_name('row_instruments.parquet')
    instrument_info = file_info(instrument_path)
    instruments = defaultdict(list)
    for membership in pq.read_table(instrument_path).to_pylist():
        instruments[membership['row_id']].append(membership)
    remote = json.loads((root/'remote.json').read_text())
    feature = Features(root/'Scripts-14.0.0.txt')
    source_records = sorted([p for w in ('W1','W2') for p in (COLLECT/f'run/{w}/pages').glob(BOOK+'--s*.json')])
    by_page = defaultdict(list)
    for r in remote['book_rows']: by_page[r['page_id']].append(r)
    release = {(r['parent_id'],r['row_id']):r for r in remote['book_release_rows']}
    pages=[];boxes=[];rows=[];features=[];inputs=[];page_runs=[];languages={};raw_box_ids={}
    for path in source_records:
        d = json.loads(path.read_text()); inputs.append(file_info(path))
        if 'image' not in d:
            page_id=digest(canonical(['collect-v3',d['id'],None,'native-raster-v1']))
            assert not by_page[d['id']]
            pages.append(dict(page_id=page_id,source_page_id=d['id'],source_namespace='collect-v3',source=d['source'],
                book_id=BOOK,edition_id=None,provider_item_id=d['item'],physical_page_number=None,image_path=None,image_sha256=None,
                image_bytes=None,width_px=None,height_px=None,split='unassigned',rights_json=None,
                source_record_sha256=file_info(path)['sha256'],acquisition_status=d['status'],acquisition_reason=d.get('reason')))
            page_runs.append(dict(page_id=page_id,run_id=None,status='not_run',box_count=0,result_sha256=None,reason=d.get('reason')))
            continue
        image = Path(d['image']); response = Path(d['response'])
        im = file_info(image); resp = file_info(response)
        assert im['sha256']==d['image_sha256'] and resp['sha256']==d['response_sha256']
        inputs.extend([im,resp])
        width,height = image_dimensions(image)
        source_page = d['id']; page_rows = by_page[source_page]
        editions = {r['edition_id'] for r in page_rows}; splits = {r['split'] for r in page_rows}
        page_id = digest(canonical(['collect-v3',source_page,im['sha256'],'native-raster-v1']))
        pages.append(dict(page_id=page_id,source_page_id=source_page,source_namespace='collect-v3',source=d['source'],
            book_id=BOOK,edition_id=next(iter(editions)) if len(editions)==1 else None,
            provider_item_id=d['item'],physical_page_number=d['page'],image_path=str(image),image_sha256=im['sha256'],
            image_bytes=im['bytes'],width_px=width,height_px=height,split=next(iter(splits)) if len(splits)==1 else ('mixed' if splits else 'unassigned'),
            rights_json=canonical(d.get('rights')),source_record_sha256=file_info(path)['sha256'],acquisition_status=d['status']))
        doc = json.loads(response.read_text())['document']; assert len(doc['pages'])==1
        google = doc['pages'][0]; gw=google['dimension']['width'];gh=google['dimension']['height']
        assert (gw,gh)==(width,height), 'probe handles only matching native Google frames'
        run_id = digest(canonical(['google',resp['sha256'],d.get('tranche'),'retained-response-v1']))
        raw = []
        for i,line in enumerate(google.get('lines',[])):
            poly = line['layout']['boundingPoly']
            px = [[float(v.get('x',0)),float(v.get('y',0))] for v in poly.get('vertices',[])]
            norm = [[float(v.get('x',0)),float(v.get('y',0))] for v in poly.get('normalizedVertices',[])]
            if not px: px = [[x*width,y*height] for x,y in norm]
            bbox = [min(x for x,y in px),min(y for x,y in px),max(x for x,y in px),max(y for x,y in px)]
            box_id=digest(canonical([page_id,run_id,'raw_line',0,i]))
            raw_box_ids[(source_page,i)]=box_id
            raw.append(dict(box_id=box_id,page_id=page_id,segmenter='google',segmenter_run_id=run_id,geometry_kind='raw_line',
                polygon_px=px,polygon_norm=[[x/width,y/height] for x,y in px],bbox_px=bbox,
                bbox_norm=[bbox[0]/width,bbox[1]/height,bbox[2]/width,bbox[3]/height],raw_polygon_norm=norm,
                reading_order=i,emitted_item_index=i,raw_page_index=0,raw_line_index=i,
                raw_segmenter_json=canonical(line),response_stored_sha256=resp['sha256'],response_original_sha256=d['response_sha256'],
                response_representation='original_json',crop_ids=[],source_box_ids=[],
                effective_detected_languages_json=canonical(line['layout'].get('detectedLanguages') or google.get('detectedLanguages',[])),
                detected_languages_scope='line' if line['layout'].get('detectedLanguages') else 'page'))
            languages[(source_page,i)] = line['layout'].get('detectedLanguages') or google.get('detectedLanguages',[])
        for top,b in enumerate(sorted(raw,key=lambda b:(b['bbox_px'][1],b['bbox_px'][0],b['box_id']))): b['line_index_from_top']=top
        boxes.extend(raw)
        page_runs.append(dict(page_id=page_id,run_id=run_id,status='ok' if raw else 'zero_detections',box_count=len(raw),result_sha256=resp['sha256']))
        derived=[]
        for r in sorted(page_rows,key=lambda r:r['row_id']):
            row_key=digest(canonical([r['parent_id'],r['row_id']]))
            box_id=digest(canonical([page_id,run_id,'harvest_derived',r['parent_id'],r['row_id']]))
            bbox=r['bbox'];x0,y0,x1,y1=bbox;poly=[[x0,y0],[x1,y0],[x1,y1],[x0,y1]]
            crop_id=digest(canonical([r['crop_sha256'],page_id,r['crop_bbox'],'source-crop-v1']))
            anchor=raw_box_ids[(source_page,r['docai_line_index'])]
            derived.append(dict(box_id=box_id,page_id=page_id,segmenter='google',segmenter_run_id=run_id,geometry_kind='harvest_derived',
                polygon_px=poly,polygon_norm=[[x/width,y/height] for x,y in poly],bbox_px=bbox,
                bbox_norm=[x0/width,y0/height,x1/width,y1/height],raw_polygon_norm=None,
                reading_order=r['docai_line_index'],emitted_item_index=None,raw_page_index=0,raw_line_index=r['docai_line_index'],
                raw_segmenter_json=None,response_stored_sha256=resp['sha256'],response_original_sha256=d['response_sha256'],
                response_representation='original_json',crop_ids=[crop_id],source_box_ids=[anchor],
                contributor_count=r['google_line_contributors'],lineage_status='anchor_only_not_full_contributor_reconstruction'))
            member=release.get((r['parent_id'],r['row_id']))
            if member:
                assert member['crop_sha256']==r['crop_sha256'] and member['label']==r['raw_text']
                assert r['crop']['exists'], 'release crop must exist'
            rows.append(dict(row_key=row_key,parent_id=r['parent_id'],row_id=r['row_id'],box_id=box_id,page_id=page_id,
                status={'ADMIT':'used','HOLD':'held','DROP':'dropped'}[r['disposition']],census_disposition=r['disposition'],census_generation=2,
                usage_scope='train_candidate' if r['split']=='train' else 'evaluation_diagnostic',
                reasons_json=canonical(r['reasons']),reason_codes=[x['reason'] if isinstance(x,dict) else x for x in r['reasons']],
                decision_sha256=r['decision_sha256'],decision_locator='sqlite:observations/decisions:'+canonical([r['parent_id'],r['row_id']]),
                label_raw=r['raw_text'],label_raw_sha256=digest(r['raw_text']),raw_text_field=r['raw_text_field'],
                label_corrected=r['final_text'],label_corrected_sha256=digest(r['final_text']),
                label_version_id='census06:g2:final_text',corrections_applied_json=canonical(r['edits']),
                normalization_json=canonical(r['normalization']),correction_route_statuses_json=canonical(r['routes']),split=r['split'],
                release_memberships=['v4:release_v4_admission'] if member else [],crop_id=crop_id,crop_sha256=r['crop_sha256'],
                crop_path=r['crop']['path'],crop_available=r['crop']['exists'],crop_bbox_px=r['crop_bbox'],
                bbox_px=bbox,source=r['source'],book_id=BOOK,edition_id=r['edition_id'],primary_class=r['primary_class']))
            for variant,text in [('raw',r['raw_text']),('census_corrected',r['final_text'])]:
                f=feature.compute(text,languages[(source_page,r['docai_line_index'])]);dims=r['crop'].get('dimensions')
                f.update(row_key=row_key,label_variant=variant,feature_version=FEATURE_VERSION,label_sha256=digest(text),
                    census_primary_class=r['primary_class'],crop_width_px=dims[0] if dims else None,crop_height_px=dims[1] if dims else None,
                    crop_aspect=dims[0]/dims[1] if dims else None,x_center_norm=(x0+x1)/2/width,y_center_norm=(y0+y1)/2/height,
                    line_index_from_top=None,confidence=google['lines'][r['docai_line_index']]['layout'].get('confidence'),
                    confidence_scope='Google line layout; distinct from language confidence')
                features.append(f)
        for top,b in enumerate(sorted(derived,key=lambda b:(b['bbox_px'][1],b['bbox_px'][0],b['box_id']))): b['line_index_from_top']=top
        boxes.extend(derived)
    assert len(pages)==40 and len(rows)==len(remote['book_rows'])==1429
    top_index={b['box_id']:b['line_index_from_top'] for b in boxes};row_boxes={r['row_key']:r['box_id'] for r in rows}
    for f in features: f['line_index_from_top']=top_index[row_boxes[f['row_key']]]
    for record in pages + rows:
        observed_split = {'val':'dev', 'reserved':'test'}.get(record['split'], record['split'])
        assert observed_split == 'unassigned' or observed_split == canonical_book['split'].replace('seal04_', ''), 'source split disagrees with canonical book'
        record['source_book_id'] = record['book_id']
        record['source_split'] = record['split']
        record['book_id'] = canonical_book['book_id']
        record['split'] = canonical_book['split']
        record['book_split_labels'] = canonical_book['split_labels']
        record['book_split_assignment_status'] = canonical_book['assignment_status']
        record['book_split_exportable'] = canonical_book['exportable']
        record['book_aliases_json'] = canonical(canonical_book['aliases'])
        record['split_provenance_json'] = canonical(canonical_book['assignments'])
        record['book_registry_sha256'] = registry_info['sha256']
        record['harvest_protection'] = canonical_book['harvest_protection']
    for record in rows:
        memberships = instruments.get(record['row_id'], [])
        record['lqb_row'] = any(m['kind']=='lqb' for m in memberships)
        record['release_excluded_row'] = any(m['kind']=='release_exclusion' for m in memberships)
        record['row_instruments_json'] = canonical(memberships)
        record['row_instruments_sha256'] = instrument_info['sha256']
    tables={}
    for name,data in [('pages',pages),('boxes',boxes),('rows',rows),('row_features',features)]:
        columns=sorted({key for record in data for key in record})
        tables[name]=pa.Table.from_pylist([{key:record.get(key) for key in columns} for record in data])
    outputs=[];db=sqlite3.connect(root/'registry.sqlite')
    for name,table in tables.items():
        p=root/(name+'.parquet');pq.write_table(table,p,compression='zstd');outputs.append(file_info(p))
        assert pq.read_table(p).to_pylist()==table.to_pylist()
        db.execute('DROP TABLE IF EXISTS '+name);sql_store(db,name,table)
    db.executescript('CREATE UNIQUE INDEX IF NOT EXISTS page_pk ON pages(page_id);CREATE UNIQUE INDEX IF NOT EXISTS box_pk ON boxes(box_id);CREATE UNIQUE INDEX IF NOT EXISTS row_pk ON rows(row_key);CREATE UNIQUE INDEX IF NOT EXISTS row_identity ON rows(parent_id,row_id);CREATE UNIQUE INDEX IF NOT EXISTS feature_pk ON row_features(row_key,label_variant,feature_version);')
    db.commit()
    checks=dict(all_rows_join=db.execute('SELECT count(*) FROM rows r JOIN boxes b USING(box_id) JOIN pages p ON p.page_id=b.page_id').fetchone()[0],
        used_join=db.execute("SELECT count(*) FROM rows r JOIN boxes b USING(box_id) JOIN pages p ON p.page_id=b.page_id WHERE r.status='used'").fetchone()[0],
        orphan_features=db.execute('SELECT count(*) FROM row_features f LEFT JOIN rows r USING(row_key) WHERE r.row_key IS NULL').fetchone()[0],
        raw_boxes_without_anchor_row=db.execute("SELECT count(*) FROM boxes b WHERE geometry_kind='raw_line' AND NOT EXISTS (SELECT 1 FROM rows r JOIN boxes d ON d.box_id=r.box_id WHERE json_extract(d.source_box_ids,'$[0]')=b.box_id)").fetchone()[0])
    db.execute('DROP TABLE IF EXISTS book_registry')
    book_table=pa.Table.from_pylist([canonical_book]);sql_store(db,'book_registry',book_table)
    checks['rows_box_page_book_split_join']=db.execute('SELECT count(*) FROM rows r JOIN boxes b USING(box_id) JOIN pages p ON p.page_id=b.page_id JOIN book_registry k ON k.book_id=r.book_id WHERE p.book_id=k.book_id AND p.split=k.split AND r.split=k.split').fetchone()[0]
    checks['pages_book_split_join']=db.execute('SELECT count(*) FROM pages p JOIN book_registry k USING(book_id) WHERE p.split=k.split').fetchone()[0]
    assert checks['rows_box_page_book_split_join']==1429 and checks['pages_book_split_join']==40
    assert checks['all_rows_join']==1429 and checks['used_join']==sum(r['status']=='used' for r in rows) and checks['orphan_features']==0
    db.close();outputs.append(file_info(root/'registry.sqlite'))
    # Independent count/position checks on a reproducible 1,000-key sample; a full
    # independent recomputation of all semantic features remains a production check.
    sampled=random.Random(20261022).sample(sorted(r['row_key'] for r in rows),1000)
    fm={(f['row_key'],f['label_variant']):f for f in features};rm={r['row_key']:r for r in rows}
    bm={b['box_id']:b for b in boxes};pm={p['page_id']:p for p in pages}
    for key in sampled:
        r=rm[key];b=bm[r['box_id']];p=pm[b['page_id']]
        for variant,field in [('raw','label_raw'),('census_corrected','label_corrected')]:
            f=fm[key,variant];s=ud.normalize('NFC',r[field])
            assert f['length_chars']==len(s) and f['nonspace_chars']==len(''.join(s.split()))
            assert sum(f[k+'_count'] for k in ('greek','latin','cyrillic','digits','punctuation','other'))==f['nonspace_chars']
            assert f['digits_count']==sum(ud.category(c)=='Nd' for c in s)
            assert abs(f['y_center_norm']-(b['bbox_px'][1]+b['bbox_px'][3])/2/p['height_px'])<1e-9
    for text,want in [('',False),('123',False),('ΑΒΓ',True),('ΑβΓ',False)]: assert feature.compute(text,[])['all_caps']==want
    assert feature.compute('אع',[])['mixed_script']
    assert feature.compute('Αa',[])['language_guess']=='mul'
    for text,want in [('ἄ',True),('ά',False),('ὰ',True)]: assert feature.compute(text,[])['polytonic_marks_present']==want
    # Example subset export preserves existing row IDs, label variant and crop hashes.
    selected=[dict(parent_id=r['parent_id'],row_id=r['row_id'],row_key=r['row_key'],crop_sha256=r['crop_sha256'],box_id=r['box_id'],label_variant='raw') for r in rows if r['status']=='used' and fm[r['row_key'],'raw']['greek_pct']>=50]
    p=root/'selected_rows.jsonl';p.write_text(''.join(canonical(r)+'\n' for r in selected));outputs.append(file_info(p))
    (root/'segmenter_page_results.json').write_text(canonical(page_runs)+'\n');outputs.append(file_info(root/'segmenter_page_results.json'))
    manifest=dict(schema='runner4-hf-one-book-probe-v2',book_id=canonical_book['book_id'],source_book_id=BOOK,provider_item_id='bsb11759351',
        canonical_book_registry=registry_info,canonical_split=canonical_book['split'],
        row_instrument_registry=instrument_info,harvest_protection=canonical_book['harvest_protection'],
        row_instrument_counts=dict(lqb=sum(r['lqb_row'] for r in rows),release_excluded=sum(r['release_excluded_row'] for r in rows)),
        scope='all 40 harvested page records for this book; not all pages of the provider volume',
        remote_input=file_info(root/'remote.json'),source_selection=file_info(REPO/'docs/programme_20261019/registry/SOURCE_MANIFEST.json'),
        code=file_info(Path(__file__).resolve()),producing_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
        code_state='uncommitted probe; code SHA authoritative',python=platform.python_version(),pyarrow=pa.__version__,
        features=feature.provenance,inputs=inputs,counts={n:t.num_rows for n,t in tables.items()},
        boxes_by_kind=dict(Counter(b['geometry_kind'] for b in boxes)),statuses=dict(Counter(r['status'] for r in rows)),
        release_v4_members=len(release),missing_crop_by_status=remote['book_counts']['missing_crops_by_status'],
        source_bytes=dict(pages=sum(p['image_bytes'] or 0 for p in pages),responses=sum(x['bytes'] for x in inputs if '/responses/' in x['path']),crops_verified_remotely=remote['book_counts']['crop_bytes']),
        checks=checks,features_sample=dict(rows=1000,variants=2000,seed=20261022,keyset_sha256=digest(canonical(sampled)),
            checks='independent NFC lengths, denominator, digit counts, bucket sums, page y centres; fixed script/capital/mark witnesses',
            limitation='not independent verification of every script/language/correction feature'),
        selected_rows=len(selected),outputs=outputs,seconds=time.perf_counter()-start,
        limitations=['Live ledger read-only g2 probe, not immutable decision-export readback.',
            'Derived boxes retain source envelope and known Google anchor; full contributor reconstruction is pending.',
            'No toolkit inference/import, no raster/crop shard construction, no HF creation/upload/tag.',
            'Some held/dropped crops absent in CROPS4C custody; their measured crop dimensions remain null.'])
    p=root/'manifest.json';p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    receipt={k:v for k,v in manifest.items() if k!='inputs'};receipt['manifest']=file_info(p)
    (REPO/'out/runner4/HF_ONE_BOOK_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    summary={k:v for k,v in remote.items() if k not in ('book_rows','book_release_rows','release_v4_sf7_book')}
    summary['remote_probe']=file_info(root/'remote.json')
    (REPO/'out/runner4/HF_SOURCE_PROBE.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(counts=manifest['counts'],boxes_by_kind=manifest['boxes_by_kind'],status=manifest['statuses'],release_members=len(release),checks=checks,seconds=manifest['seconds'],manifest=str(p))))


if __name__=='__main__':
    main()
