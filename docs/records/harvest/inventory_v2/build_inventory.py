"""Build receipt-linked S1 deliverables without network or source mutations."""
from __future__ import annotations
import collections, hashlib, html, json, pathlib, re, statistics, unicodedata
from urllib.parse import unquote
from assessments import FACTS, RANKINGS

B=pathlib.Path(__file__).resolve().parent
def read(p,default=None):
    p=B/p
    return json.loads(p.read_text()) if p.exists() else default
def write(p,d):
    p=B/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def rel(p):return str(p.relative_to(B))
def norm(v):
    if isinstance(v,list):v=' '.join(str(x) for x in v)
    return ''.join(c for c in unicodedata.normalize('NFKD',str(v or '')).casefold() if c.isalnum())
def year(v):
    m=re.search(r'(?<!\d)(1[5-9]\d{2}|20\d{2})(?!\d)',str(v or ''))
    return int(m[1]) if m else None
def key(r):
    a=[r.get('title'),r.get('author',r.get('creator')),r.get('year'),r.get('publisher')]
    return tuple(norm(x) for x in a) if all(a) else None
def link(label,p):return f'[{label}]({p})'
def cell(t):return str(t).replace('|',' / ').replace('\n',' ')

old=[json.loads(x) for x in (B/'receipts/local/existing-editions.jsonl').read_text().splitlines()]
oldkeys=collections.defaultdict(list)
for r in old:
    if key(r):oldkeys[key(r)].append(r)
visual=read('receipts/local/visual-review.json')

# Site-wide namespace status census; mapping is verified against the saved site's JS.
for lang in ['el','ru','bg','sr']:
    rows=read(f'receipts/wikisource-el/stats-{lang}.txt',{}).get('data',[])
    if not rows:continue
    r=rows[-1]
    write(f'receipts/wikisource-{lang}/status-counts.json',dict(language=lang,timestamp=r[0],page_namespace_total=r[1],without_text=r[2],problematic=r[3],unproofread=r[1]-sum(r[2:6]),proofread=r[4],validated=r[5],transcluded=r[6],main_namespace_raw=r[7],disambiguation=r[8],basis=f'receipts/wikisource-el/stats-{lang}.txt',mapping_basis='receipts/wikisource-el/stats-js.txt',scope='All dates, site-wide Page namespace. Not a count of target-era usable or independent reference lines.'))

# Conservative bounded front-matter/credits census. It is not a whole-ebook scan search.
cat=read('receipts/gutenberg-greek/catalogue-links.json',[])
ids=sorted(set(int(x.split('/')[-1]) for x in cat if re.fullmatch(r'/ebooks/\d+',x)))
pg=[]
for n in ids:
    p=f'receipts/gutenberg-greek/ebook-{n}-result.json';r=read(p,{})
    h=read(f'receipts/gutenberg-greek/frontmatter-{n}-result.json',{})
    credits='';external=[];mentions=[];provision=[];edition_hint=None
    if r.get('ok'):
        blob=(B/r['http_receipt']).with_suffix('.body').read_text(errors='replace')
        m=re.search(r'<th>\s*Credits\s*</th>\s*<td[^>]*>(.*?)</td>',blob,re.S|re.I)
        if m:credits=html.unescape(re.sub('<[^>]*>',' ',m[1])).strip()
    text=(B/f'receipts/gutenberg-greek/frontmatter-{n}.txt').read_text() if h.get('ok') else ''
    # Locate explicit source-scan hosts in hyperlinks; exclude PG's boilerplate links.
    links=read(f'receipts/gutenberg-greek/frontmatter-{n}-links.json',[])
    for u in links:
        if re.search(r'archive\.org/(details|stream)|books\.google\.|gallica\.bnf|hathitrust\.org|commons\.wikimedia\.org/wiki/File:|digitale-sammlungen|anemi\.lib',u,re.I):external.append(u)
    for s in re.split(r'\n\s*\n',credits+'\n'+text[:16000]):
        if re.search(r'\b(?:scanned|source scans?|from images|images generously|digitized by)\b',s,re.I):mentions.append(s.strip()[:1000])
        if re.search(r'\b(?:book provided by|book made available by)\b',s,re.I):provision.append(s.strip()[:1000])
    # Printed title-page dates in a prefix are hints, never certified editions.
    dates=re.findall(r'(?<!\d)(?:18|19)\d{2}(?!\d)',text)
    pg.append(dict(ebook=n,catalogue_ok=r.get('ok',False),frontmatter_ok=h.get('ok',False),credits=credits,source_scan_locators=sorted(set(external)),scan_credit_mentions=mentions,book_provision_credits=provision,printed_date_hints=sorted(set(dates)),catalogue_receipt=p,frontmatter_receipt=f'receipts/gutenberg-greek/frontmatter-{n}-result.json',same_edition_verified=False))
pgsummary=dict(catalogue_ebooks=len(ids),catalogue_records_retrieved=sum(x['catalogue_ok'] for x in pg),frontmatter_prefixes_retrieved=sum(x['frontmatter_ok'] for x in pg),ebooks_with_explicit_source_scan_locator=sum(bool(x['source_scan_locators']) for x in pg),ebooks_with_scan_credit_mention=sum(bool(x['scan_credit_mentions']) for x in pg),ebooks_naming_source_scan_provider=sum(any(re.search(r'HathiTrust|Internet Archive|National Library|Google Books|Gallica',s,re.I) for s in x['scan_credit_mentions']) for x in pg),ebooks_with_book_provision_credit=sum(bool(x['book_provision_credits']) for x in pg),same_edition_pairs_certified=0,scope='Greek language catalogue; bibliographic Credits and first 32768 response bytes of each available HTML front matter. Counts are bounded citation evidence, not a census of later notes in complete ebooks. A book-provision credit is not a source-scan citation. Downloaded ebook prefixes are digital text, not evidence that an original scan is available.',negative_reference_witness=dict(ebook=34434,receipt='receipts/gutenberg-greek/frontmatter-34434-result.json',finding='Front matter explicitly reports polytonic-to-monotonic conversion, partly missing scan words imagined by the transcriber, and unresolved words. Not literal printed-page truth.'),identified_edition_example=dict(ebook=66595,receipt='receipts/gutenberg-greek/frontmatter-66595-result.json',title='Monumentum Ancyranum: The Deeds of Augustus',editor='William Fairley',year=1898,publisher='Department of History, University of Pennsylvania; Anvil Printing Company, Philadelphia',scan_credit='HathiTrust Digital Library; specific volume locator not supplied in inspected prefix',scan_edition_match_verified=False),ebooks=pg)
write('receipts/gutenberg-greek/citation-census.json',pgsummary)

sources=[];rights=['# Rights inventory','', 'Rights are recorded, not decided. A source declaration is not a copyright determination or an acquisition approval. Each item needs separate scan, underlying-text and access records. Cloud OCR, training, retention and redistribution are not inferred from free reading, a metadata licence, an old owner-admission note, a date, or a public-domain label in another jurisdiction.','', 'Where marked **owner decision**, the owner must decide whether to rely on Greek Law 2121/1993 Art. 21A/21B, which entity and access qualify, rights reservations, secure retention and any processor terms. This inventory does not assert that an exception applies. The requested legal framework is recorded in the [plan-input receipt](receipts/local/input-files.json); no legal eligibility finding is made.','', 'Short verbatim excerpts appear below; complete retrieved wording is retained in the linked HTTP body/terms receipt. Missing or blocked wording is explicitly unresolved. No permissions, forms, orders or gated-dataset terms were accepted.','']

for sid,f in FACTS.items():
    folder=B/'receipts'/sid
    results=[]
    for p in sorted(folder.glob('*-result.json')):
        d=json.loads(p.read_text());d['result_receipt']=rel(p);results.append(d)
    probes=[]
    for p in sorted(folder.glob('probe-*.json')):
        d=json.loads(p.read_text())
        if 'label' not in d or not d.get('image_path'):continue
        lp=p.with_name(p.stem+'-lines.json');lines=json.loads(lp.read_text()) if lp.exists() else None
        d['probe_receipt']=rel(p);d['line_receipt']=rel(lp) if lines else None
        d['line_count']=lines['non_discounted_lines'] if lines else None
        d['visual_review']=visual['page_review'].get(d['image_path'],{'media_class':'unreviewed','scripts':'unknown'})
        probes.append(d)
    counts=collections.Counter(x['visual_review']['media_class'] for x in probes)
    metrics=dict(pages=len(probes),raster_bytes=sum(x['bytes'] for x in probes),new_network_image_bytes=sum(x['bytes'] for x in probes if x.get('origin') is None),reused_local_image_bytes=sum(x['bytes'] for x in probes if x.get('origin')),media_counts=dict(counts),digital_edition_pages=counts['digital-edition'],scanned_print_pages=counts['scanned-print'],unclassified_or_other_pages=sum(v for k,v in counts.items() if k not in ('digital-edition','scanned-print')),detector_lines=[x['line_count'] for x in probes],detector_mean=round(statistics.mean(x['line_count'] for x in probes),2) if probes and all(x['line_count'] is not None for x in probes) else None,target_class_estimates=[x for x in visual['fully_classified_detector_pages'] if x['source']==sid])
    ledger=folder/'transfer.jsonl';trans=[json.loads(x) for x in ledger.read_text().splitlines()] if ledger.exists() else []
    metrics['recorded_http_body_bytes']=sum(x['bytes'] for x in trans)
    if sid=='openarchives':metrics['recorded_http_body_bytes']+=read('receipts/openarchives/hf-authenticated-result.json',{}).get('bytes',0)
    # Live scan path requires an actual fresh raster. Reused images are not live-path verification.
    machine=any(not p.get('origin') for p in probes)
    # Metadata-only availability is tracked separately, never substituted for a page path.
    live=any(r.get('ok') for r in results)
    exists='Y (live catalogue/metadata)' if live else 'unconfirmed live; indexed/prior lead only'
    if sid=='snhell':exists='unconfirmed; DNS failed'
    if sid in ['persee-bch','e-rara','e-periodica']:exists='primary catalogue indexed; crawler robots-blocked'
    if sid=='russian-national-library':exists='national-library routes identified; live material blocked'
    candidates=[]
    if sid=='internet-archive':
        for p in folder.glob('*metadata.txt'):
            try:d=json.loads(p.read_text())
            except Exception:continue
            m=d.get('metadata',{});i=m.get('identifier')
            if i:candidates.append(dict(id=i,title=m.get('title'),author=m.get('creator'),year=year(m.get('date')),publisher=m.get('publisher'),language=m.get('language'),rights=m.get('rights'),licenseurl=m.get('licenseurl'),access_restricted=m.get('access-restricted-item'),basis=rel(p)))
    if sid=='bsb-mdz':candidates=[dict(id='bsb11189761',title='Philologus. 33. 1874',author=None,year=1874,publisher=None,catalogue_series_publisher='Berlin : de Gruyter; not certified as the historic printed imprint',rights='https://rightsstatements.org/vocab/NoC-NC/1.0/',basis='receipts/bsb-mdz/manifest.txt')]
    if sid=='wikisource-el':candidates=[dict(id='Βίοι Πελοποννησίων ανδρών.djvu',title='Βίοι Πελοποννησίων ανδρών',author='Φώτιος Χρυσανθόπουλος',year=1888,publisher='Σταύρος Ανδρόπουλος',rights=dict(scan='Commons source-declared PD-scan and PD-old-100-expired; source says author died in 1879',text_contributions='CC BY-SA 4.0 with possible additional terms',rights_basis='receipts/wikisource-el/commons-rights.txt',assessment='Source declaration, not an independent copyright determination'),basis='receipts/wikisource-el/index.txt')]
    if sid=='wikisource-ru':candidates=[dict(id='Graham 1913 V–VI',title='Англичанин о русском Севере',author='С. Грэхем; А. Воскресенский (translation)',year=1913,publisher=None,rights=dict(scan='Commons file page asserts US public-domain status; wider territorial status unverified',text_contributions='Wikisource CC BY-SA; underlying-work and translator rights separate',rights_basis='receipts/wikisource-ru/commons-rights.txt'),basis='receipts/wikisource-ru/edition-index.txt')]
    if sid=='hellenic-parliament':
        for p in folder.glob('*item-metadata.txt'):
            try:d=json.loads(p.read_text())
            except Exception:continue
            m=d.get('metadata',{});candidates.append(dict(id=d.get('uuid'),title=d.get('name'),author=[v['value'] for v in m.get('dc.contributor.author',[])],year=year([v['value'] for v in m.get('dc.date.issued',[])]),publisher=[v['value'] for v in m.get('dc.publisher',[])],rights=m.get('dc.rights',[]),basis=rel(p)))
    for p in probes:
        c=p.get('catalogue')
        if c:candidates.append(dict(id=c['book'],title=c.get('title'),author=c.get('author',c.get('creator')),year=c.get('year'),publisher=c.get('publisher'),rights=c.get('rights_raw',c.get('licence')),basis=p['probe_receipt']))
    matches=[]
    for c in candidates:
        exact=oldkeys.get(key(c),[]) if key(c) else []
        ids=[x for x in old if c.get('id') and x.get('id') and (c['id']==x['id'] or str(c['id']) in str(x['id']))]
        titles=[x for x in old if norm(c.get('title')) and norm(c.get('title'))==norm(x.get('title')) and (not c.get('year') or not x.get('year') or c['year']==x['year'])]
        matches.append(dict(candidate=c,complete_edition_key=key(c),exact_four_field_matches=exact,identifier_matches=ids[:20],title_year_candidates=titles[:20],disposition='known/possible overlap; do not acquire for training' if exact or ids or titles else 'not cleared: incomplete old metadata prevents certified non-overlap'))
    overlap=dict(method='NFKD/casefold title + author + year + publisher; identity/title/year matches are additional conservative flags, never non-overlap certificates.',inputs='receipts/local/overlap-inputs.json',requested_wave_manifests_found=0,candidate_count=len(candidates),complete_candidate_keys=sum(key(c) is not None for c in candidates),complete_existing_keys=sum(key(x) is not None for x in old),matches=matches,conclusion='Existing identifiers/title candidates flagged' if any(x['exact_four_field_matches'] or x['identifier_matches'] or x['title_year_candidates'] for x in matches) else 'No certified edition clearance; missing manifests/author/publisher prevent an all-clear')
    write(f'receipts/{sid}/edition-overlap.json',overlap)
    qlabel=f.get('quote_label');quote=None;terms_url=None;quote_basis=None
    if qlabel:
        qp=folder/(qlabel+'.txt')
        if qp.exists():
            t=html.unescape(re.sub(r'<[^>]+>',' ',qp.read_text(errors='replace')));t=' '.join(t.split())
            start=f.get('quote_start','');i=t.casefold().find(start.casefold())
            if i>=0:
                sentence=re.split(r'(?<=[.!?])\s',t[i:],maxsplit=1)[0]
                sentence=sentence.strip(' ,')
                words=sentence.split();quote=' '.join(words[:25])+(' …' if len(words)>25 else '')
                quote_basis=rel(qp)
                if sid=='perseus-first1k':
                    raw=qp.read_text();m=re.search(r'<licence[^>]*>(.*?)</licence>',raw,re.S)
                    if m:quote=' '.join(re.sub('<[^>]*>',' ',m[1]).split())
                if sid=='patrologia-graeca':quote=f['quote_start']
    tr=read(f'receipts/{sid}/{f.get("terms_label","home")}-result.json',{})
    terms_url=tr.get('response_url',tr.get('url'))
    if not terms_url:
        seed=next((r for r in results if r.get('url')),{});terms_url=seed.get('response_url',seed.get('url'))
    owner=[dict(id='S1-rights-'+sid,status='owner decision',question='Which item rights/licence, lawful-access and retention/processor conditions permit the intended copies? If relying on Art. 21A/21B, the owner must decide applicability; this inventory does not.') ] if f['owner'] else []
    right=dict(scan_rights=f['scan'],text_rights=f['text'],access_terms_url=terms_url,terms_receipt=tr.get('result_receipt',f'receipts/{sid}/{f.get("terms_label","home")}-result.json'),verbatim_excerpt_ref=f'RIGHTS.md#{sid}',verbatim_excerpt_source=quote_basis,cloud_ocr_processing='Not explicitly authorised by the retrieved wording; owner assessment required. No cloud processing performed.',retention_terms='Not established beyond the linked source wording; no research retention entitlement inferred.',training_use='No training permission determined by this inventory.',redistribution_terms='Source licence/statement and item restrictions recorded above; no redistribution decision made.',owner_decisions=owner,item_rights=[c for c in candidates if c.get('rights') or c.get('licenseurl')])
    if sid=='anemi':right['retention_terms']='Systematic storage/printing of whole digital items is explicitly forbidden in the source notice; any exception assessment is an owner decision.'
    if sid=='laskaridis-travelogues':right['cloud_ocr_processing']='Terms include a written-consent restriction on processing digital images; applicability and any exception remain an owner decision.'
    if sid=='openarchives':right['redistribution_terms']='Aggregator terms defer third-party material to original-provider terms; no blanket HF or aggregator permission is inferred.'
    write(f'receipts/{sid}/probe-pages.json',dict(source=sid,metrics=metrics,pages=[dict(image_path=p['image_path'],item=p.get('item'),page=p['page'],bytes=p['bytes'],origin=p.get('origin','new bounded HTTP raster probe'),http_receipt=p.get('http_receipt'),probe_receipt=p['probe_receipt'],line_receipt=p['line_receipt']) for p in probes]))
    receipt_paths=[rel(p) for p in sorted(folder.glob('*.json'))]+[rel(folder/'transfer.jsonl')] if ledger.exists() else [rel(p) for p in sorted(folder.glob('*.json'))]
    record=dict(schema='s1-source-inventory-v2',source_id=sid,name=f['name'],group=f['group'],exists=exists,access_path=f['path'],machine_path_verified='Y' if machine else 'N',machine_path_definition='Fresh individual raster retrieved and decoded. For aligned text, additionally inspect the text/edition witness. Metadata/table/old-image success is separate.',metadata_access_verified=live,date_range=f['dates'],print_vs_digital_probe=metrics,target_classes=f['targets'],lines_per_page=dict(detector_mean=metrics['detector_mean'],target_class_estimates=metrics['target_class_estimates'],limitation='All-segment detector counts are not target-class, admitted, codec-surviving or production yields. Target estimates are limited to the explicitly reviewed numbered pages; all other target yields are unknown.'),overlap=dict(summary=overlap['conclusion'],receipt=f'receipts/{sid}/edition-overlap.json'),rights=right,blocker=f['blocker'],workaround=f['workaround'],aligned_proofread=f.get('aligned'),probe_pages=[dict(image_path=p['image_path'],receipt=p['probe_receipt'],line_receipt=p['line_receipt'],origin=p.get('origin','new bounded HTTP raster probe'),page=p['page'],item=p.get('item')) for p in probes],receipt_paths=sorted(set(receipt_paths)),http_attempts=results)
    if sid.startswith('wikisource-'):record['proofreading_status_counts']=read(f'receipts/{sid}/status-counts.json')
    if sid=='gutenberg-greek':record['citation_census_receipt']='receipts/gutenberg-greek/citation-census.json'
    if sid=='openarchives':record['metadata_census_receipt']='receipts/openarchives/local-metadata-census.json'
    write(f'receipts/{sid}/source-assessment.json',record);sources.append(record)
    rights += [f'<a id="{sid}"></a>',f'## {f["name"]}','',f'Terms/access record: {link("source page",terms_url)}; {link("receipt",f"receipts/{sid}/{f.get("terms_label","home")}-result.json")}.', '']
    if quote:rights += ['> '+quote,'',f'Verbatim excerpt from {link("saved wording",quote_basis)}.','']
    else:rights += ['**Verbatim applicable terms not recovered.** The linked receipt identifies the refusal, missing page, licence-only metadata or absence of relevant wording. No permissive wording is invented.','']
    rights += ['| Field | Recorded status |','|---|---|',f'| Scan rights | {cell(right["scan_rights"])} |',f'| Text rights | {cell(right["text_rights"])} |',f'| Access | {cell(f["path"])} |',f'| Cloud OCR | {cell(right["cloud_ocr_processing"])} |',f'| Retention | {cell(right["retention_terms"])} |',f'| Training | {cell(right["training_use"])} |',f'| Redistribution | {cell(right["redistribution_terms"])} |',f'| Exception / owner | {"**Owner decision** — applicability of Art. 21A/21B is not asserted." if owner else "Explicit source licence recorded; no exception claimed. Item/edition and processing checks still apply."} |','',f'Item-specific rights and access observations: {link("source assessment",f"receipts/{sid}/source-assessment.json")}; {link("edition/overlap receipt",f"receipts/{sid}/edition-overlap.json")}.','']

(B/'sources.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in sources))
(B/'RIGHTS.md').write_text('\n'.join(rights)+'\n')
byid={r['source_id']:r for r in sources}
totals=dict(sources=len(sources),verified_paths=sum(r['machine_path_verified']=='Y' for r in sources),proofread_sources=sum(r['aligned_proofread'] is not None for r in sources),probe_pages=sum(r['print_vs_digital_probe']['pages'] for r in sources),probe_raster_bytes=sum(r['print_vs_digital_probe']['raster_bytes'] for r in sources),new_network_image_bytes=sum(r['print_vs_digital_probe']['new_network_image_bytes'] for r in sources),reused_local_image_bytes=sum(r['print_vs_digital_probe']['reused_local_image_bytes'] for r in sources),recorded_http_body_bytes=sum(r['print_vs_digital_probe']['recorded_http_body_bytes'] for r in sources),owner_decisions=sum(len(r['rights']['owner_decisions']) for r in sources),top_pilots=['IA historical Greek print','Ajax mixed-line GT','BSB Philologus contents/body'])
totals['probe_MB_decimal']=round(totals['probe_raster_bytes']/1_000_000,3)
totals['definitions']={'sources':'Requested source records covered, including blocked or unverified leads.','proofread_sources':'Named aligned-text leads inventoried, including sources not confirmed as proofread or edition-bound.','verified_paths':'Fresh individual raster retrieved and decoded; not rights or quality clearance.','owner_decisions':'Source-level unresolved rights/exception decision tickets; not a count of all legal subquestions.','probe_pages':'New raster probes plus individually receipted local witnesses; each saved page counted once.'}
write('receipts/local/totals.json',totals)
write('receipts/local/ranked-pilots.json',[dict(category=c,ranked_sources=ss,first_pilot_reason=why,target_receipt='receipts/local/plan-targets.json') for c,ss,why in RANKINGS])

report=['# Source inventory for data plan v2','', 'Inventory of source access, rights evidence and bounded probes. “Done” means the requested source inventory and blocker ledger are delivered; it does not mean every route, right or yield is qualified. The [machine-readable records](sources.jsonl), [rights record](RIGHTS.md), [totals receipt](receipts/local/totals.json), [input hashes](receipts/local/input-files.json) and per-source assessments hold the supporting evidence.','', 'The first pilots recommended are **IA historical Greek print**, **Ajax mixed-line ground truth**, and **BSB Philologus contents/body**. These are recommendations for the next owner-approved work, not acquisition or read authorisation. Numeric-source access qualification starts with ELSTAT; its page yield remains unknown.','', 'Machine path **Y** means a fresh individual page raster was retrieved and decoded. It does not mean rights clearance or a usable OCR pipeline. Catalogue/table access and previously harvested images are recorded separately. **N** includes robots refusal, CAPTCHA/access restrictions, missing endpoints, timeouts, and routes for which only metadata or old images were verified. Print/digital counts describe only saved probe pages, never a repository proportion. Unknown target-class yield remains unknown.','', 'All source HTTP requests use the unchanged project O4c User-Agent and robots/rate transport, with a separate receipt root in this worktree. No Anemi credentials were used; no Anemi images were requested. HF credentials were injected from Keychain into one command environment and were not recorded. No Google OCR/cloud reads, paid API use, production acquisition, gate acceptance, orders or messages occurred. The source-level image cap and byte accounting are checked in [validation](receipts/local/validation.json).','', 'Probe totals count every saved witness once, including explicitly marked copies of existing local pages. Decimal MB is the sum of probe raster-file bytes; it is not total network traffic. The totals receipt separates newly fetched image bytes, local image bytes and recorded HTTP response-body bytes. TLS/header bytes and failed connection setup are outside that body-byte measure.','', 'Edition dedupe is **not cleared**. The requested `collection/*/wave_manifest.json` paths were absent in this worktree and the read-only main checkout. Available `docs/harvest/*/books.json` and `source_books.json` plus O4c are hashed and compared conservatively. Missing authors/publishers prevent an absence-of-overlap certificate. Known identifier/title matches are flagged, including reused witnesses and the old IA lexicon. See [overlap inputs](receipts/local/overlap-inputs.json).','', 'Key corrections are recorded below and in source assessments: IA Greek discovery was rebuilt rather than reusing the old Cyrillic-heavy list; current Patras domains and a Pleias digital-form licence were found; Pergamos has a working published-JPEG route but its sampled leaf is handwriting; Parliament licences vary even within proceedings; ELSTAT’s yearbook series begins later than its wider historical publication collection.','']

if (B/'receipts/local/commit-blocked.json').exists():
    report[2:2]=['The local commit is **blocked by the managed filesystem policy**: Git cannot create the worktree index lock. No worker commit or push exists. The [commit-block receipt](receipts/local/commit-blocked.json) and [source-bound handoff](commit_inventory.py) preserve the requested branch and exact commit scope.','']
for group in ['Greek and Cyprus repositories','International scan repositories','Aligned proofread text']:
    report += ['## '+group,'','| Source / receipt | Exists | Access path | Machine path | Dates / scope | Probe print / digital / other | Target and lines per page | Edition overlap | Rights | Blocker and workaround |','|---|---|---|---|---|---|---|---|---|---|']
    for r in sources:
        if r['group']!=group:continue
        sid=r['source_id'];m=r['print_vs_digital_probe'];mean=m['detector_mean']
        probe='Not sampled; share unknown' if not m['pages'] else f'{m["scanned_print_pages"]} / {m["digital_edition_pages"]} / {m["unclassified_or_other_pages"]}; n={m["pages"]}'
        lc='unknown (no image count)' if mean is None else f'{mean:g} detected segments/page; target yield unmeasured'
        if m['target_class_estimates']:
            v=m['target_class_estimates'][0];lc+=f'; {len(v["positive_indices"])} same-line mixed segments on the specifically classified body page'
        report.append('| '+' | '.join(cell(x) for x in [link(r['name'],f'receipts/{sid}/source-assessment.json'),r['exists'],r['access_path'],r['machine_path_verified'],r['date_range'],probe,r['target_classes']+'; '+lc,link(r['overlap']['summary'],r['overlap']['receipt']),link('recorded / unresolved',f'RIGHTS.md#{sid}'),r['blocker']+' Workaround: '+r['workaround']])+' |')
    report.append('')

report += ['## Aligned-text availability and edition binding','', '| Source | Text | Licence / scope | Printed edition identified | Same-edition scans online / witness | Quality limit |','|---|---|---|---|---|---|']
for r in sources:
    a=r['aligned_proofread']
    if not a:continue
    report.append('| '+' | '.join(cell(x) for x in [r['name'],a['text_available'],r['rights']['text_rights'],str(a['edition_identified'])+': '+str(a['edition'] or 'unresolved'),str(a['same_edition_scans'])+': '+a['scan_where'],a['quality']])+' |')
report += ['','## Count receipts and important limits','', '| Census | Receipt-backed observation |','|---|---|']
for lang in ['el','ru','bg','sr']:
    x=read(f'receipts/wikisource-{lang}/status-counts.json',{})
    report.append(f'| Wikisource {lang} | {link(str(x.get("proofread"))+" proofread; "+str(x.get("validated"))+" validated; "+str(x.get("page_namespace_total"))+" Page-namespace pages",f"receipts/wikisource-{lang}/status-counts.json")}; all dates, snapshot {x.get("timestamp")}; not a count of usable aligned lines. |')
report.append(f'| Gutenberg Greek | {link(str(pgsummary["catalogue_ebooks"])+" ebooks; "+str(pgsummary["catalogue_records_retrieved"])+" metadata records; "+str(pgsummary["frontmatter_prefixes_retrieved"])+" bounded prefixes; "+str(pgsummary["ebooks_with_explicit_source_scan_locator"])+" with an explicit source-scan locator; "+str(pgsummary["ebooks_with_scan_credit_mention"])+" with a scan-credit mention", "receipts/gutenberg-greek/citation-census.json")}. Prefix/citation counts do not certify exact printed-edition correspondence or exclude citations later in an ebook. |')
oa=read('receipts/openarchives/local-metadata-census.json',{})
report.append(f'| Open Archives | {link(str(oa.get("counts",{}).get("ocr_success_true"))+" ocr_success documents in "+str(oa.get("counts",{}).get("documents"))+" local metadata records", "receipts/openarchives/local-metadata-census.json")}. HF link-table byte identity is verified; the local metadata projection extraction revision is not. No fresh PDFs fetched. |')
ia=[]
for code in ['gre','grc','ell']:
    d=read(f'receipts/internet-archive/greek-{code}.txt',{})
    if d.get('response'):ia.append(f'{code}={d["response"]["numFound"]}')
report.append('| IA language discovery | '+link('; '.join(ia),'receipts/internet-archive/source-assessment.json')+'. Queries use the requested date window; variant counts overlap and must not be summed. Full-text language/year/collection facets and returned snippets are retained separately. |')
report += ['', f'Gutenberg scan attribution: {pgsummary["ebooks_naming_source_scan_provider"]} ebook names a scan provider in the inspected prefix (HathiTrust), while no specific source-scan URL was found. The identified Fairley edition and the conversion/guessed-word counterexample are preserved in the [citation census](receipts/gutenberg-greek/citation-census.json). A provider credit is not a same-edition pairing.', '', 'The [visual review](receipts/local/visual-review.json) distinguishes actual within-line Greek/Latin-script witnesses from separate-column co-occurrence, records a German-only page in a Cyrillic-selected item, and leaves clean Open Archives rasters scan-vs-digital uncertain. Detector output is descriptive: split/merged rows, furniture and unusual layouts can affect counts. Only the explicitly numbered mixed pages have manually classified target counts; no production yield is extrapolated.','', '## Ranked shortlist for each plan category','', 'Targets are disjoint primary usable-row allocations from the [plan-target receipt](receipts/local/plan-targets.json). Rankings and pilot reasons are judgments, not measured supply or acquisition promises. All unmeasured quotas wait for the later rights-cleared pilot.','', '| Category | Usable-row target | Ranked sources | First pilot and reason |','|---|---:|---|---|']
targets={x['category']:x['usable_rows_target'] for x in read('receipts/local/plan-targets.json')['categories']}
for c,ss,why in RANKINGS:report.append('| '+' | '.join(cell(x) for x in [c,link(str(targets[c]),'receipts/local/plan-targets.json'),' → '.join(byid[s]['name'] for s in ss),why])+' |')
report += ['', 'No source is released for acquisition, cloud processing, training, redistribution or independent-reference use by this inventory. The next concrete work is the ranked bounded pilot after the owner’s item-rights decision, edition/held-out exclusion and page-path qualification.','',f'S1: done | sources: {totals["sources"]} verified_paths: {totals["verified_paths"]} | proofread_sources: {totals["proofread_sources"]} | probes: {totals["probe_pages"]} pages {totals["probe_MB_decimal"]:.3f} MB | owner_decisions: {totals["owner_decisions"]} | top_pilots: '+ '; '.join(totals['top_pilots'])]
(B/'INVENTORY.md').write_text('\n'.join(report)+'\n')
print(json.dumps(totals,indent=2))
