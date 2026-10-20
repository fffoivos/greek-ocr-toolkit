import json, re
from lxml import etree
from pilotlib import *

if __name__=='__main__':
    path=BASE/'bulk/text/tlg0015.tlg001.xml';root=etree.parse(str(path));item='bub_gb_ghIMAAAAYAAJ';c=client('ia')
    meta=fetch(c,'https://archive.org/metadata/'+item,BASE/'bulk/metadata'/(item+'.json'));d=json.loads(meta.read_text())
    scan=next(f['name'] for f in d['files'] if f['name'].endswith('_scandata.xml'))
    sp=fetch(c,'https://archive.org/download/'+item+'/'+scan,BASE/'bulk/metadata'/(item+'-scandata.xml'))
    sr=etree.parse(str(sp));mapping={}
    for p in sr.findall('.//pageData/page'):
        label=p.findtext('pageNumber')
        if label and label.isdigit():mapping.setdefault(label,[]).append(int(p.get('leafNum')))
    pbs=[x.get('n').removeprefix('p.') for x in root.findall('.//{*}text//{*}pb')]
    if not mapping:
        # Physical contact-sheet anchors: scan ordinals 39,56,74,87,105,
        # 122,140,153,170,188 show printed 30,47,65,78,96,113,131,144,
        # 161,179. Keep this an explicit provisional offset; a page read must
        # verify its printed page before labels can be considered.
        eligible=[n for n in pbs if n.isdigit()]
        selected=[eligible[i-1] for i in positions(len(eligible),50)]
        mapping={n:[int(n)+8] for n in selected}
        mapping_status='physical_sample_offset_plus_9; per_page_header_readback_required'
    else:
        eligible=[n for n in pbs if n in mapping and len(mapping[n])==1]
        selected=[eligible[i-1] for i in positions(len(eligible),50)]
        mapping_status='scandata_unique_printed_page'
    write(BASE/'receipts/perseus-selection.json',dict(text_path=str(path.relative_to(BASE)),text_sha256=sha(path),revision='03776b39f4047c5cff06f5296fae4b2bae4b08fb',source_header=etree.tostring(root.find('.//{*}sourceDesc')).decode(),scan_metadata=d['metadata'],scan_metadata_sha256=sha(meta),scandata_sha256=sha(sp),page_map=mapping,selected_printed_pages=selected,proofreading_status='source-declared corrected/encoded; no Wikisource validation grade',witness_status='header explicitly names scan; title-page physical confirmation pending'))
    write(BASE/'receipts/items'/f'{item}.json',dict(pilot='perseus',item=item,title='Herodiani Ab excessu divi Marci',editor='Immanuel Bekker',publisher='Teubner, Leipzig',year=1855,source_url='https://archive.org/details/'+item,rights=dict(scan=d['metadata'].get('rights',d['metadata'].get('possible-copyright-status','unresolved')),text='First1KGreek TEI licence in pinned header',cloud_ocr='owner P1 authorised',retention='pilot evidence',training='evaluation candidate; excluded from training, lexicons and synthetic seeds',redistribution='component licence recorded')))
    selected_ordinals={mapping[label][0]+1 for label in selected}
    for f in (BASE/'receipts/pages').glob('perseus--*.json'):
        r=json.loads(f.read_text())
        if r['page'] not in selected_ordinals:r['excluded']='outside_final_50_text_page_sample';write(f,r)
    for label in selected:
        leaf=mapping[label][0]
        try:
            r=raster('perseus',item,leaf+1,f'https://archive.org/download/{item}/page/n{leaf}.jpg',c)
            r.pop('excluded',None)
            r.update(printed_page=label,page_mapping_status=mapping_status,text_path=str(path.relative_to(BASE)),text_sha256=sha(path),text_revision='03776b39f4047c5cff06f5296fae4b2bae4b08fb',proofreading_status='source-declared corrected/encoded')
            write(BASE/'receipts/pages'/(r['id']+'.json'),r);print('perseus',label,leaf,'ok',flush=True)
        except Exception as e:print('perseus',label,type(e).__name__,str(e)[:150],flush=True)
