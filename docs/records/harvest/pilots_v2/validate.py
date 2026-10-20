"""Read-back validation of P1 costs, source custody, labels, sheets and files."""
import argparse,csv,json,re,sys,unicodedata as ud
from collections import Counter,defaultdict
from urllib.parse import unquote
from bs4 import BeautifulSoup
from lxml import etree
from PIL import Image
from pilotlib import *

def require(condition,message):
    if not condition:raise AssertionError(message)

def verify_files():
    count=0
    with (BASE/'FILES.tsv').open() as stream:
        for r in csv.DictReader(stream,delimiter='\t'):
            p=BASE/r['path'];require(p.is_file(),'missing file '+r['path']);require(p.stat().st_size==int(r['bytes']),'size '+r['path']);require(sha(p)==r['sha256'],'hash '+r['path']);count+=1
    return count

def validate(check_files=False):
    pages=rows(BASE/'pages.jsonl');selected=[r for r in pages if not r.get('excluded') and r['pilot'] in ['ia1850','ia1900','bsb','elstat','kosmopolis','openarchives','ajax','wikisource','gutenberg','perseus']]
    paid_pages=[r for r in selected if r['pilot']!='ajax'];records=rows(BASE/'bulk/records.jsonl');pilots=rows(BASE/'pilots.jsonl');budget=rows(BASE/'receipts/p1-budget.jsonl');provider=rows(BASE/'receipts/p1-provider-ledger.jsonl')
    require(len(paid_pages)==544,'544 actual scan deliveries');require(len(budget)==539,'539 distinct paid attempts');require(sum(r['micro_usd'] for r in budget)==808500,'integer reservation arithmetic');require(sum(r['micro_usd'] for r in budget)<=5_000_000,'hard USD 5 cap');require(all(r['engine']=='docai' for r in budget),'Document AI only');require(len({r['key'] for r in budget})==len(budget),'no duplicate reservation')
    charged=[r for r in provider if not r['cached']];require(len(charged)==len(budget),'provider/reservation count');require({r['key'] for r in budget}=={r['crop_sha256'] for r in charged},'provider/reservation image custody');require(all(r['status']=='ok' and r['pages_billed']==1 for r in charged),'all provider attempts succeeded')
    t={r['key']:r['time'] for r in budget}
    from datetime import datetime
    for r in charged:
        require(t[r['crop_sha256']]<=datetime.fromisoformat(r['timestamp'].replace('Z','+00:00')).timestamp(),'reservation precedes provider request')
        require(sha(pathlib.Path(r['raw_json_path']))==r['raw_sha256'],'raw Google response hash')
    require(sum(r['pages_read'] for r in pilots)==544,'pilot read arithmetic');require(abs(sum(r['cost_usd'] for r in pilots)-.8085)<1e-9,'pilot cost arithmetic')
    for p in selected:
        image=BASE/p['image'];require(sha(image)==p['image_sha256'],'native page hash '+p['id'])
        with Image.open(image) as im:require(max(im.size)<=3500 and list(im.size)==[p['width'],p['height']],'capped native frame '+p['id'])
        if p['pilot']!='ajax':
            a=json.loads((BASE/'receipts/analysis'/(p['id']+'.json')).read_text());require(a['status']=='ok','analysis '+p['id'])
    require(len([p for p in selected if p['pilot']=='ajax'])==68,'68 Ajax source pages');require(not any(r.get('pilot')=='ajax' for r in [json.loads(p.read_text()) for p in (BASE/'receipts/reads').glob('*.json')]),'Ajax has no Google reads')
    ajax=rows(BASE/'bulk/ajax-geometry-final.jsonl');gt=rows(BASE/'bulk/ajax-lines.jsonl')
    require(len(ajax)==len(gt)==3364 and {r['id'] for r in ajax}=={r['id'] for r in gt},'all published Ajax pairs retained through geometry accounting')
    require(sum(r.get('binding')=='original_page_not_published_in_archive' for r in ajax)==332,'missing Ajax native pages explicitly unresolved')
    axs=next(p for p in pilots if p['pilot']=='ajax');require(axs['geometry_evaluable']+axs['geometry_unresolved']==axs['admitted_codec'],'Ajax geometry denominator includes unbound rows')
    for pilot in ['wikisource','gutenberg','perseus']:require(sum(p['pilot']==pilot for p in paid_pages)==50,'50 alignment pages '+pilot)
    old={r['url'] for r in json.loads((ROOT/'docs/harvest/wikisource/manifest.json').read_text())}
    require(not any(p.get('page_url') in old for p in paid_pages if p['pilot']=='wikisource'),'no overlap with prior 400 Wiki pages')
    ia=Counter(p['item'] for p in paid_pages if p['pilot'] in ['ia1850','ia1900']);require(all(20<=n<=40 for n in ia.values()),'IA per-document sample bounds')
    usable=[r for r in records if r['usable_candidate']];require(all(r['admitted'] and r['codec_v1_pass'] and r['geometry_positive'] is False and not r['duplicate_crop_label'] for r in usable),'usable candidate conjunction');require(len({(r['crop_sha256'],r['canonical_label']) for r in usable})==len(usable),'usable crop/label deduplication')
    for s in pilots:
        if s['pilot']=='ajax':continue
        rr=[r for r in records if r['pilot']==s['pilot']];require(len(rr)==s['lines'],'line denominator '+s['pilot']);require(sum(r['usable_candidate'] for r in rr)==s['usable_candidates'],'usable count '+s['pilot']);require(sum(s['primary_allocations'].values())==s['usable_candidates'],'disjoint allocations '+s['pilot'])
    aligned=rows(BASE/'bulk/alignment.jsonl');accepted=[r for r in aligned if r['accepted']];require(len(accepted)==1992,'all-language alignment candidates');trees={};raw={};claimed=defaultdict(list)
    ap=rows(BASE/'alignment_pages.jsonl');ag=rows(BASE/'alignment_coverage.jsonl');regions=rows(BASE/'alignment_regions.jsonl')
    require(len(ap)==150 and sum(g['pages'] for g in ag)==150,'all alignment pages in grouped coverage')
    require({r['id'] for r in regions}=={r['id'] for r in aligned},'all accepted and rejected regions manifested')
    require(sum(p['document_nonspace_nfd_characters_outside_line_anchors'] for p in ap)==0,'document characters outside line anchors recorded')
    require(sum(g['target_lines'] for g in ag)==sum(r['accepted_for_target_reference'] for r in aligned)==1223,'target coverage line arithmetic')
    require(sum(g['all_page_ocr_nfd_characters'] for g in ag)==sum(p['google_nfd_characters'] for p in ap),'grouped full document character denominator')
    for p in ap:
        receipt=json.loads((BASE/'receipts/reads'/(p['page_id']+'.json')).read_text())
        parsed=json.loads((BASE/receipt['result']).read_text())
        raw_response=json.loads(pathlib.Path(parsed['raw_json_path']).read_text())
        document=raw_response.get('document',raw_response)
        normalized=re.sub(r'\s+',' ',ud.normalize('NFD',document.get('text',''))).strip()
        require(len(normalized)==p['google_nfd_characters'],'full document coverage denominator '+p['page_id'])
    for r in accepted:
        require(not r['reasons'] and r['geometry_positive'] is False,'accepted alignment gate '+r['id']);require(sha(BASE/r['crop_path'])==r['crop_sha256'],'alignment crop '+r['id']);text=[]
        for owner in r['literal_source_ownership']:
            p=BASE/owner['path']
            if 'xpath' in owner:
                if str(p) not in trees:trees[str(p)]=etree.parse(str(p),etree.HTMLParser() if p.suffix=='.html' else etree.XMLParser())
                nodes=trees[str(p)].xpath(owner['xpath']);require(len(nodes)==1,'unique source node');value=getattr(nodes[0],owner['field']) or '';text.append(ud.normalize('NFD',value)[owner['start']:owner['end']])
            else:
                if str(p) not in raw:raw[str(p)]=ud.normalize('NFD',p.read_text())
                text.append(raw[str(p)][owner['start']:owner['end']])
        require(re.sub(r'\s','',''.join(text))==re.sub(r'\s','',ud.normalize('NFD',r['human_label'])),'literal source ownership '+r['id'])
        a,b=r['source_span_nfd'];require(all(max(a,c)>=min(b,d) for c,d in claimed[r['page_id']]),'no duplicated proofread span');claimed[r['page_id']].append((a,b))
    for pilot in ['wikisource','gutenberg','perseus']:
        sheet=BASE/'blind_sheets'/pilot/'sheet.html';soup=BeautifulSoup(sheet.read_text(),'html.parser');require(len(soup.select('article'))==40,'40 blind cards');require(len(soup.select('input[type=radio]'))==120,'three choices per card');require(not soup.select('input[checked]'),'no judgments fabricated')
        key=json.loads((BASE/'receipts/blind-keys'/(pilot+'.json')).read_text())['cards'];require(sum(r['accepted'] for r in key)==20,'20 accepted blind controls');require(sum(not r['accepted'] for r in key)==20,'20 rejected blind controls')
        for tag in soup.select('img[src],a[href]'):
            target=tag.get('src',tag.get('href'));require((sheet.parent/unquote(target)).resolve().is_file(),'blind link '+target)
        for f in [BASE/'blind_sheets'/pilot/'cards-01-20.jpg',BASE/'blind_sheets'/pilot/'cards-21-40.jpg']:
            with Image.open(f) as im:require(im.width==1600 and im.height>1000,'static blind raster')
    for f in (BASE/'receipts/sheets').glob('*.json'):
        r=json.loads(f.read_text());require(r['pages']==20 and len({p['page_id'] for p in r['mapping']})==20,'20 distinct contact pages');require(sha(BASE/r['path'])==r['sha256'],'contact sheet hash')
    require(len(list((BASE/'receipts/sheets').glob('*.json')))==10,'10 source contact sheets');require(len(list((BASE/'receipts/blind-sheets').glob('*.json')))==3,'3 blind packs')
    overlap=json.loads((BASE/'receipts/edition-overlap.json').read_text());require(not any(r['exact_known_heldout_match'] for r in overlap['items'] if r['pilot'] in ['ia1850','ia1900','bsb','elstat','kosmopolis','openarchives']),'no exact known heldout collection match')
    source=json.loads((BASE/'receipts/source-bindings.json').read_text());require(source['main_harvest_source_unchanged'],'main harvest unchanged')
    for path,value in source['harvest_sources'].items():require(sha(ROOT/path)==value,'frozen harvest source')
    report=(BASE/'PILOTS.md').read_text();totals=json.loads((BASE/'receipts/totals.json').read_text());require(report.splitlines()[-1]==totals['footer'],'exact footer readback')
    for target in re.findall(r'\]\(([^)]+)\)',report):
        if target.startswith(('http:','https:')):continue
        if target in ('FILES.tsv','receipts/validation.json') and not check_files:continue
        require((BASE/target).is_file(),'report link '+target)
    result=dict(passed=True,pages_read=544,paid_attempts=539,reserved_usd=.8085,raw_source_ownership_checked=len(accepted),target_reference_candidates=sum(r['accepted_for_target_reference'] for r in accepted),released_reference_lines=0,contact_sheets=10,blind_packs=3,blind_cards=120,main_harvest_unchanged=True,report_sha256=sha(BASE/'PILOTS.md'),file_inventory_verified=verify_files() if check_files else 'run --check after FILES.tsv build',qualification_limit='strict Greek-language Gutenberg IA-cited pair unqualified; exploratory Greek-bearing philology cohort separated',interactive_browser_qa='blocked; static raster sheets and links validated')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args();result=validate(args.check)
    if not args.check:write(BASE/'receipts/validation.json',result)
    print(json.dumps(result,ensure_ascii=False))
