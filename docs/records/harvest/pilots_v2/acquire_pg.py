"""Greek-bearing Gutenberg philology pilot, explicitly English/Greek mixed."""
import json,re
from bs4 import BeautifulSoup
from pilotlib import *

if __name__=='__main__':
    item='pronunciationofg00blacuoft';p=BASE/'bulk/text/pg69810.html';s=BeautifulSoup(p.read_text(),'html.parser')
    numbered=[]
    for node in s.select('.pagenum'):
        m=re.search(r'Page_(\d+)',str(node))
        if m:numbered.append(int(m[1]))
    numbered=sorted(set(numbered));selected=[numbered[i-1] for i in positions(len(numbered),50)];c=client('ia')
    write(BASE/'receipts/gutenberg-selection.json',dict(ebook=69810,title='The Pronunciation of Greek; Accent and Quantity',author='John Stuart Blackie',printed_year=1852,publisher='Sutherland and Knox, Edinburgh',source_url='https://www.gutenberg.org/ebooks/69810',html_path=str(p.relative_to(BASE)),html_sha256=sha(p),pg_last_update='2024-10-19 (header)',language_scope='English prose with substantial Greek; explicitly disclosed source-scope interpretation, not a Greek-language book',scan_provider_credit='This file was produced from images generously made available by The Internet Archive',credit_is_item_locator=False,scan_item=item,witness_status='exact title/author/imprint/year binding; provider credit names IA but no specific item locator',sample_printed_pages=selected,scan_ordinal_offset=4,page_mapping_status='physical scan ordinal 11 shows printed 7; ordinal 9 unnumbered first body leaf corresponds to printed 5; per-page header readback required',scope_decision='Agent uses Greek-bearing philology for the Greek alignment pilot; not an additional user approval. All/Greek-bearing yields are separated.'))
    meta=json.loads((BASE/'bulk/metadata'/(item+'.json')).read_text())['metadata']
    write(BASE/'receipts/items'/(item+'.json'),dict(pilot='gutenberg',item=item,title='The Pronunciation of Greek; Accent and Quantity',author='John Stuart Blackie',year=1852,language='English, Greek quotations',source_url='https://www.gutenberg.org/ebooks/69810',scan_url='https://archive.org/details/'+item,rights=dict(scan=meta.get('rights',meta.get('possible-copyright-status','not specified')),text='PG public domain in USA; PG licence; original text rights separate',cloud_ocr='P1 owner spend authorisation',retention='pilot evidence',training='evaluation candidate excluded from all training inputs',redistribution='source licence terms and attribution recorded')))
    selected_ordinals={printed+4 for printed in selected}
    for f in (BASE/'receipts/pages').glob('gutenberg--*.json'):
        r=json.loads(f.read_text())
        if r['page'] not in selected_ordinals:r['excluded']='outside_corrected_50_page_sample';write(f,r)
    for printed in selected:
        n=printed+4
        try:
            r=raster('gutenberg',item,n,f'https://archive.org/download/{item}/page/n{n-1}.jpg',c)
            r.pop('excluded',None)
            r.update(printed_page=str(printed),text_path=str(p.relative_to(BASE)),text_sha256=sha(p),text_revision='PG69810 last-update 2024-10-19; body hash '+sha(p),proofreading_status='Distributed Proofreaders source declaration; literal span pending blind pixel audit',page_mapping_status='physical_printed7_at_scan11_plus4; per_page_header_readback_required')
            write(BASE/'receipts/pages'/(r['id']+'.json'),r);print('gutenberg',printed,n,'ok',flush=True)
        except Exception as e:print('gutenberg',printed,type(e).__name__,str(e)[:140],flush=True)
