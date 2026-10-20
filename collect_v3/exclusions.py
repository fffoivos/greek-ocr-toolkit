"""Frozen exclusions and conservative cross-provider edition resolution.

An exact provider/media/bibliographic identity is excluded. A title/year alias
without a corroborating author or page hash is quarantined, never admitted.
"""
from __future__ import annotations
import re, unicodedata as ud
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit,unquote
from .common import iter_rows, read_json, sha, write_json, write_rows, sha_bytes, dumps, lock

HASH_FIELDS={'pdf_sha256','image_sha256','page_image_sha256','original_sha256','PDF_sha256','fetch_sha256','full_pdf_sha256'}
ID_FIELDS={'provider_id','book_id','book_key','item','identifier','record_id','doc','edition_duplicate_of','alias_of'}
KEYS=('provider_id','media_hash','title_year','title_year_author')

def norm(value):
    if isinstance(value,list):value=' '.join(map(str,value))
    return ''.join(c for c in ud.normalize('NFD',str(value or '').casefold()) if c.isalnum())

def title_year(title,year):
    return f'{norm(title)}|{year}' if title and year else None

def bibliography(r):
    metadata=r.get('catalogue_metadata') or r.get('metadata') or {}
    title=r.get('true_title') or r.get('edition_title') or r.get('title') or metadata.get('title') or metadata.get('Наслов')
    year=r.get('year') or r.get('publication_year')
    author=r.get('author') or r.get('authors') or r.get('creator') or metadata.get('authors') or metadata.get('Аутор')
    return title_year(title,year),norm(author)

def provider_keys(value, provider=None):
    value=str(value or ''); out=set()
    if not value:return out
    out.add(value)
    if provider:out.add(provider+':'+value)
    if ':' in value and not value.startswith(('http','URN:')):out.add(value.split(':',1)[1])
    if value.startswith(('http://','https://')):
        p=urlsplit(value);out.add(unquote(p.netloc.lower()+p.path.rstrip('/')+('?' + p.query if p.query else '')))
        for pat in [r'archive.org/(?:details|download)/([^/]+)',r'(bsb\d+)',r'/metadata/[^?]+',r'(\d{11})\.pdf']:
            m=re.search(pat,value)
            if m:out.add(m.group(1) if m.lastindex else m.group())
    return out

class Exclusions:
    def __init__(self, data=None):
        data=data or {};self.keys={k:set(data.get(k,[])) for k in KEYS}
        self.editions=data.get('editions',[]);self._edition_index={}
        for e in self.editions:self._edition_index.setdefault(e['title_year'],[]).append(e)
        self.quarantined={(r['source'],r['item']):r for r in data.get('quarantined',[])}
    def add(self,r,provider=None):
        if not isinstance(r,dict):return
        local_ids=set();local_hashes=set()
        for k,v in r.items():
            if k in ID_FIELDS or k in ('provider_keys','source_url','item_url','pdf_url','url','aliases'):
                for x in v if isinstance(v,list) else [v]:
                    if isinstance(x,(str,int)):local_ids.update(provider_keys(x,provider))
            if k in HASH_FIELDS and isinstance(v,str):local_hashes.add(v)
            if k=='key' and r.get('key_type') in ('page_image_sha256','pdf_sha256','full_pdf_sha256') and isinstance(v,str):local_hashes.add(v)
            if k=='sha256' and r.get('scope') in ('full_pdf','page_image'):local_hashes.add(v)
            if isinstance(v,dict): self.add(v,provider)
            if isinstance(v,list):
                for x in v:
                    if isinstance(x,dict):self.add(x,provider)
        if isinstance(r.get('id'),str) and not r.get('page_id') and not (r.get('item') and 'page' in r) and not re.search(r'-l\d{3,}$',r['id']):local_ids.update(provider_keys(r['id'],provider))
        self.keys['provider_id'].update(local_ids);self.keys['media_hash'].update(local_hashes)
        ty,author=bibliography(r)
        if ty:
            self.keys['title_year'].add(ty)
            if author:self.keys['title_year_author'].add(ty+'|'+author)
            edition=dict(title_year=ty,author=author,provider_ids=sorted(local_ids),media_hashes=sorted(local_hashes))
            # Input-row multiplicity is irrelevant to identity resolution.
            if edition not in self._edition_index.get(ty,[]):
                self.editions.append(edition);self._edition_index.setdefault(ty,[]).append(edition)
            for title in r.get('title_aliases',[]):
                alias=title_year(title,r.get('year') or r.get('publication_year'))
                if alias:
                    self.keys['title_year'].add(alias)
                    if author:self.keys['title_year_author'].add(alias+'|'+author)
    def resolve(self,r,provider=None,source=None):
        if source and (source,str(r.get('id'))) in self.quarantined:
            return 'quarantined',self.quarantined[source,str(r['id'])]['reasons']
        test=Exclusions();test.add(r,provider)
        exact=[k for k in ('provider_id','media_hash','title_year_author') if self.keys[k]&test.keys[k]]
        if exact:return 'excluded',exact
        if self.keys['title_year']&test.keys['title_year']:
            return 'quarantined',['title_year_without_corroborated_author_or_media']
        # A provider's unresolved overlap assertion is evidence to quarantine.
        if r.get('overlap_matches') or any((r.get('overlap_screen') or {}).get(k) for k in ('collected','held_out')):
            return 'quarantined',['provider_overlap_requires_alias_resolution']
        return 'eligible',[]
    def match(self,r,provider=None):
        status,reasons=self.resolve(r,provider)
        return reasons if status!='eligible' else []
    def export(self):
        return dict({k:sorted(v) for k,v in self.keys.items()},editions=sorted(self.editions,key=dumps))

def build(projects, output, frames=None, frame_inputs=None):
    """Freeze once. Reuse requires unchanged inputs and an intact manifest."""
    projects=Path(projects);output=Path(output);output.mkdir(parents=True,exist_ok=True)
    manifest=output/'exclusions_manifest.json';receipt=output/'exclusions_receipt.json'
    with lock(output/'exclusions_build.lock'):
        if manifest.exists():
            rec=read_json(receipt)
            if sha(manifest)!=rec['manifest_sha256']:raise ValueError('frozen exclusion manifest hash mismatch')
            if sha(output/'exclusions_index.json')!=rec['manifest_sha256']:raise ValueError('exclusion index differs from frozen manifest')
            for f in rec['inputs']:
                if not Path(f['path']).exists() or sha(f['path'])!=f['sha256']:raise ValueError('frozen exclusion input changed: '+f['path'])
            return Exclusions(read_json(manifest))
        ex=Exclusions();files=[]
        main=projects/'greek-ocr-toolkit';o2=projects/'greek-ocr-toolkit-sol-inventory/docs/harvest/oa_rebind_v1/o2'
        collection=main/'docs/harvest/collection'
        required=[collection/'import_real_all.jsonl',collection/'v2/import_real_v2_all.jsonl',o2/'books.jsonl',o2/'wave4_test_books.jsonl']
        if any(not p.exists() for p in required):raise FileNotFoundError('required collection/O2 exclusion input missing')
        inputs=[*collection.rglob('*.jsonl'),o2/'books.jsonl',o2/'wave4_test_books.jsonl',o2/'v2_meta1/book_metadata.jsonl']
        for wave in ('round1','mixed','cyrillic','openarchives','wikisource'):
            inputs += [p for n in ('books.json','selection.json','holdout_books.json') if (p:=main/'docs/harvest'/wave/n).exists()]
        for p in sorted(set(inputs)):
            if not p.exists():continue
            if p.suffix=='.json':
                value=read_json(p);rr=value if isinstance(value,list) else value.get('books',[])
            else:rr=iter_rows(p)
            n=0
            for r in rr:ex.add(r);n+=1
            files.append(dict(path=str(p),sha256=sha(p),records=n,kind='v1_v2_test_dev'))
        for t in ('ia','intl','gr'):
            b=projects/f'greek-ocr-toolkit-sol-funnel-{t}'/'docs/harvest/sample_v1'/t
            ps=[b/'pages.jsonl',*b.glob('sampled_*.jsonl'),*b.glob('draw_*.jsonl'),*b.glob('verification_*.jsonl')]
            if t=='ia':ps += [b/'probe_pages.jsonl',b/'census_reviews.jsonl']
            for p in sorted(set(ps)):
                if not p.exists():continue
                n=0
                for r in iter_rows(p):ex.add(r,'ia' if t=='ia' else None);n+=1
                files.append(dict(path=str(p),sha256=sha(p),records=n,kind='F2_sampled'))
            if t=='ia':
                p=b/'receipts/draws.json'
                for rr in read_json(p).values():
                    for r in rr:ex.add(r,'ia')
                files.append(dict(path=str(p),sha256=sha(p),kind='F2_A0_draws'))
        decisions=[];quarantined=[];aliases=[]
        for source,pool in sorted((frames or {}).items()):
            for r in sorted(pool,key=lambda r:r['id']):
                status,reasons=ex.resolve(r,r.get('provider'))
                decision=dict(source=source,item=r['id'],status=status,reasons=reasons)
                decisions.append(decision)
                if status=='quarantined':quarantined.append(decision)
                if status=='excluded' and any(k in reasons for k in ('title_year_author','media_hash')):
                    ty,author=bibliography(r);aliases.append(dict(decision,title_year=ty,author=author,evidence='bibliographic author equality and/or exact PDF/page hash',provider_ids=sorted(provider_keys(r['id'],r.get('provider')))))
        files.extend(dict(f,kind='draw_frame') for f in (frame_inputs or []))
        data=dict(schema='collect-v3-exclusions-2',**ex.export(),quarantined=quarantined,alias_resolutions=aliases,inputs=files)
        write_json(manifest,data);write_json(output/'exclusions_index.json',data)
        write_rows(output/'exclusion_decisions.jsonl',decisions)
        write_rows(output/'quarantined_items.jsonl',quarantined)
        write_json(receipt,dict(schema='collect-v3-exclusions-2',manifest_sha256=sha(manifest),counts_per_key={k:len(v) for k,v in ex.keys.items()},quarantined_items=len(quarantined),alias_resolutions=len(aliases),decisions=dict(Counter(r['status'] for r in decisions)),inputs=files,network=False,policy='exact provider/hash or title+year+author excludes; ambiguous title/year quarantines; rescans with no bibliographic or hash evidence remain unproven'))
        return Exclusions(data)
