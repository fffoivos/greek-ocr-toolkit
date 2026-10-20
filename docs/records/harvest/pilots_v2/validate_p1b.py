"""Validate cached-read identity, literal/repair ownership and blind-pack completeness."""
import json
import re
import unicodedata as ud
from collections import Counter,defaultdict
from urllib.parse import unquote
from lxml import etree
from bs4 import BeautifulSoup
from pilotlib import BASE,rows,sha,write
from rerun_p1b import DEST,summarize
from p1b_align import EDGES,HYPHENS,wordchar


def main():
    checks=0
    def require(ok,message):
        nonlocal checks
        checks+=1
        if not ok:raise AssertionError(message)
    before=rows(BASE/'bulk/alignment.jsonl');after=rows(DEST/'alignment.jsonl');old={r['id']:r for r in before}
    baseline=json.loads((DEST/'baseline.json').read_text())
    for rel,value in baseline['sha256'].items():require(sha(BASE/rel)==value,'unchanged P1 evidence '+rel)
    inputs=rows(DEST/'cached_inputs.jsonl')
    require(len(inputs)==150,'150 cached inputs')
    for r in inputs:
        require(sha(r['raw_read_path'])==r['raw_read_sha256'],'raw read unchanged '+r['page_id'])
        require(sha(BASE/r['image'])==r['image_sha256'],'page unchanged '+r['page_id'])
    require(set(old)=={r['id'] for r in after},'all original regions retained')
    trees={};texts={};claims=defaultdict(list);raw_atoms={}
    accepted=[r for r in after if r['accepted']]
    for r in after:
        require(not (r['margin_numerals'] and r['accepted']),'no contaminated label admitted')
        require(r['human_label'] is not None if r['accepted'] else r['human_label'] is None,'proposal label gate')
        require(r['text_changed']==((r['candidate_text'] or r['google_text'])!=(old[r['id']]['candidate_text'] or old[r['id']]['google_text'])),'change classification')
        if not r['accepted']:continue
        require(not r['reasons'] and r['geometry_positive'] is False,'acceptance gate')
        require(sha(BASE/r['crop_path'])==r['crop_sha256'],'native crop hash')
        proof=json.loads((DEST/'proofread'/(r['page_id']+'.json')).read_text());a,b=r['source_span_nfd']
        require(all(max(a,c)>=min(b,d) for c,d in claims[r['page_id']]),'no repeated source span')
        claims[r['page_id']].append((a,b))
        if b<len(proof['text']) and wordchar(proof['text'][b]):
            require(any(e['side']=='right' and any(c in HYPHENS for c in e['text']) for e in r['edge_glyph_ownership']),'inside-word end must own a printed split')
        literal=[]
        for owner in r['literal_source_ownership']:
            path=BASE/owner['path']
            if 'xpath' in owner:
                if str(path) not in trees:trees[str(path)]=etree.parse(str(path),etree.HTMLParser() if path.suffix=='.html' else etree.XMLParser())
                nodes=trees[str(path)].xpath(owner['xpath']);require(len(nodes)==1,'unique node owner')
                raw=ud.normalize('NFD',getattr(nodes[0],owner['field']) or '')[owner['start']:owner['end']]
            else:
                if str(path) not in texts:texts[str(path)]=ud.normalize('NFD',path.read_text())
                raw=texts[str(path)][owner['start']:owner['end']]
            atoms=[(owner['path'],owner.get('xpath'),owner.get('field'),owner['start']+i) for i,c in enumerate(raw) if not c.isspace()]
            require(all(atom not in raw_atoms or raw_atoms[atom]==r['id'] for atom in atoms),'no source atom duplicated across pages '+r['id'])
            for atom in atoms:raw_atoms[atom]=r['id']
            if owner.get('repair'):
                require(raw==owner['repair']['raw'],'exact damaged source interval')
                require(owner['emitted']=='ȣ' and owner['repair']['emitted']=='ȣ','only adjudicated ligature replacement')
                literal.append(owner['emitted'])
            else:literal.append(raw)
        require(re.sub(r'\s','',''.join(literal))==re.sub(r'\s','',proof['text'][a:b]),'source ownership reconstruction '+r['id'])
        body=proof['text'][a:b]
        for correction in reversed(r['printed_corrections']):
            c,d=correction['source_nfd'];require(body[c-a:d-a]==correction['raw'],'printed correction source interval')
            body=body[:c-a]+correction['emitted']+body[d-a:]
        require(body==r['label_segments'][1]['text'],'explicit body corrections only')
        require(ud.normalize('NFC',''.join(s['text'] for s in r['label_segments']))==r['human_label'],'printed label reconstruction')
        for side,idx in [('left',0),('right',-1)]:
            for edge in r['edge_glyph_ownership']:
                if edge['side']!=side:continue
                c,d=edge['query_nfd'];q=ud.normalize('NFD',r['alignment_query'])
                require(q[c:d]==edge['text'],'edge from cached query')
    require(len({r['page_id'] for r in inputs})==150,'150 unique immutable input identities')
    pages=rows(DEST/'alignment_pages.jsonl');summary=json.loads((DEST/'summary.json').read_text())
    require(summary['after']==summarize(after,pages),'summary yield arithmetic')
    require(Counter(p['pilot'] for p in pages)==dict(wikisource=50,perseus=50,gutenberg=50),'same denominators')
    require(summary['method_sha256']==sha(BASE/'p1b_align.py'),'method binding')
    require(summary['tei_parser_sha256']==sha(BASE/'align.py'),'TEI parser binding')
    keys={p.stem:json.loads(p.read_text()) for p in (DEST/'delta_keys').glob('*.json')}
    originals={x['line_id'] for s in ['wikisource','perseus','gutenberg'] for x in json.loads((BASE/'receipts/blind-keys'/(s+'.json')).read_text())['cards']}
    for name,key in keys.items():
        require(Counter(c['pilot'] for c in key['cards'] if not c['changed'])==dict(wikisource=10,perseus=10,gutenberg=10),'10 unchanged controls each source')
        actual={c['line_id'] for c in key['cards'] if c['changed']}
        wanted={r['id'] for r in after if r['text_changed'] and (name=='complete' or r['id'] in originals)}
        require(actual==wanted,'every changed card '+name)
        count=0
        for path in (DEST/'delta_blind'/name).glob('sheet-*.html'):
            soup=BeautifulSoup(path.read_text(),'html.parser');count+=len(soup.select('article'))
            require(not soup.select('input[checked]'),'no invented judgments')
            require(len(soup.select('input'))==3*len(soup.select('article')),'three choices')
            require(not re.search('accepted|rejected|disagrees_with_page_read|margin_numeral_in_crop',soup.get_text()),'disposition blind')
            for tag in soup.select('[src],a[href]'):
                target=tag.get('src',tag.get('href'));require((path.parent/unquote(target)).resolve().is_file(),'local blind link '+target)
        require(count==len(key['cards']),'card/key count')
    # Bind regression dispositions to original cards without calling them new adjudications.
    regression=[]
    byid={r['id']:r for r in after}
    for s in ['wikisource','perseus','gutenberg']:
        for c in json.loads((BASE/'receipts/blind-keys'/(s+'.json')).read_text())['cards']:
            r=byid[c['line_id']]
            regression.append(dict(source=s,original_card=c['card'],line_id=r['id'],before_label=c['label'],after_candidate=r['candidate_text'],accepted=r['accepted'],flags=r['flags'],reasons=r['reasons']))
    jsonl=lambda p,rs:p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rs))
    jsonl(DEST/'original_card_regressions.jsonl',regression)
    margin_original=[r for r in regression if r['source']=='perseus' and 'margin_numeral_in_crop' in r['reasons']]
    require(len(margin_original)==12,'all 12 original margin crops withheld')
    carry=[r for r in regression if r['source']=='perseus' and r['original_card'] in [2,4,6,14]]
    require(all(r['accepted'] and 'cross_page_tei_fragment' in r['flags'] for r in carry),'all 4 cross-page fragments restored')
    write(DEST/'validation.json',dict(status='passed',checks=checks,accepted_proposals=len(accepted),new_google_reads=0,new_spend_usd=0,
        original_margin_cards_withheld=len(margin_original),cross_page_cards_restored=len(carry),judgments_received=0,
        limitation='Contract, source reconstruction and sheet checks are not a second pixel adjudication.'))
    print('P1b validation passed:',checks,'checks')

if __name__=='__main__':main()
