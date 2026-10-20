"""Conservative NFD span alignment. Proposals remain pending blind pixel audit."""
from __future__ import annotations
from collections import Counter,defaultdict
import gzip
from difflib import SequenceMatcher
import html,json,re,sys,unicodedata as ud
from lxml import etree
from pilotlib import *
import p1b_align
sys.path.insert(0,str(ROOT))
from greekocr.harvest.wikisource import strip_wikitext
from greekocr.harvest.admission import inventory,script_class

def normal(text):return ' '.join(ud.normalize('NFD',text).split())

def normal_map(text):
    chars=[];indices=[]
    for i,c in enumerate(ud.normalize('NFD',text)):
        if c.isspace():
            if chars and chars[-1]!=' ':chars.append(' ');indices.append(i)
        else:chars.append(c);indices.append(i)
    if chars and chars[-1]==' ':chars.pop();indices.pop()
    return ''.join(chars),indices

def tei_pages(path):
    tree=etree.parse(str(path));root=tree.getroot();pages=defaultdict(lambda:dict(chars=[],owners=[],transformations=[]));state=[None];decisions=[]
    def add(text,owner):
        if state[0] is None:return
        page=pages[state[0]]
        value, mapping, repairs = p1b_align.repair_tei_node(text)
        for repair in repairs: page['transformations'].append(dict(owner=owner, **repair))
        for c, (i, raw_end, repair) in zip(value, mapping):
            mapped_owner = dict(owner, nfd_offset=i, nfd_end=raw_end, **({'repair': repair} if repair else {})) if owner else None
            if c.isspace():
                if page['chars'] and page['chars'][-1]!=' ':page['chars'].append(' ');page['owners'].append(mapped_owner)
            else:page['chars'].append(c);page['owners'].append(mapped_owner)
    def walk(node):
        tag=etree.QName(node).localname if isinstance(node.tag,str) else 'comment'
        xp=tree.getpath(node)
        if tag=='pb':state[0]=node.get('n','').removeprefix('p.');return
        if tag=='choice':
            chosen=next((c for name in ('orig','sic','abbr') for c in node if etree.QName(c).localname==name),None)
            decisions.append(dict(xpath=xp,tag='choice',selected=etree.QName(chosen).localname if chosen is not None else None,policy='printed branch orig/sic/abbr; unresolved choices abstain'))
            if chosen is None:add(' ⟦UNRESOLVED_CHOICE⟧ ',None)
            else:walk(chosen)
            return
        if tag in ('supplied','app','note','del'):
            decisions.append(dict(xpath=xp,tag=tag,action='excluded from body candidate; editorial/notes not flattened'))
            add(' ⟦EXCLUDED_REGION⟧ ',None);return
        if tag in ('lb','head','p','div'):add(' ',None)
        add(node.text,dict(xpath=xp,field='text'))
        for child in node:
            walk(child);add(child.tail,dict(xpath=tree.getpath(child),field='tail'))
        if tag in ('head','p','div'):add(' ',None)
    walk(root.find('.//{*}text'))
    result={}
    for n,p in pages.items():
        while p['chars'] and p['chars'][-1]==' ':p['chars'].pop();p['owners'].pop()
        result[n]=dict(text=''.join(p['chars']),owners=p['owners'],transformations=decisions+p['transformations'])
    return result

def pg_pages(path):
    tree=etree.parse(str(path),etree.HTMLParser());pages=defaultdict(lambda:dict(chars=[],owners=[]));state=[None];decisions=[]
    def add(text,owner):
        if state[0] is None:return
        p=pages[state[0]]
        for i,c in enumerate(ud.normalize('NFD',text or '')):
            if c.isspace():
                if p['chars'] and p['chars'][-1]!=' ':p['chars'].append(' ');p['owners'].append(dict(owner,nfd_offset=i) if owner else None)
            else:p['chars'].append(c);p['owners'].append(dict(owner,nfd_offset=i) if owner else None)
    def walk(node):
        if not isinstance(node.tag,str):return
        xp=tree.getpath(node);cl=set((node.get('class') or '').split());ident=node.get('id','')
        if node.tag in ('script','style','head') or ident.startswith('pg-') or cl&{'footnote','fnanchor','transnote','pg-boilerplate','pgheader','pgfooter'}:
            decisions.append(dict(xpath=xp,action='excluded',reason='DP boilerplate, moved footnote/reference or editorial transcriber note'));return
        if 'pagenum' in cl:
            m=re.fullmatch(r'Page_(\d+)',ident)
            if m:state[0]=m[1]
            decisions.append(dict(xpath=xp,action='page-marker removed and page witness retained',page=state[0]));return
        if node.tag in ('p','div','br','h1','h2','h3','li'):add(' ',None)
        add(node.text,dict(xpath=xp,field='text'))
        for child in node:
            walk(child);add(child.tail,dict(xpath=tree.getpath(child),field='tail'))
        if node.tag in ('p','div','br','h1','h2','h3','li'):add(' ',None)
    walk(tree.getroot());out={}
    for key,p in pages.items():
        if p['chars'] and p['chars'][-1]==' ':p['chars'].pop();p['owners'].pop()
        out[key]=dict(text=''.join(p['chars']),owners=p['owners'],transformations=dict(dp_header_footer='Gutenberg boilerplate removed',footnotes='moved footnotes and inline editorial reference anchors excluded; rejected scan regions remain in coverage',spelling_punctuation='no spelling/accent/dash rewrite; HTML node text in NFD; whitespace collapsed',decisions=decisions))
    return out

def prepare(page,tei_cache):
    raw=BASE/page['text_path']
    if page['pilot']=='wikisource':
        source=raw.read_text();clean=strip_wikitext(source)
        text=normal('\n'.join(l['text'] for l in clean['lines']))
        raw_normal,raw_indices=normal_map(source)
        return dict(text=text,raw_normal=raw_normal,raw_indices=raw_indices,raw_path=page['text_path'],transformations=dict(cleaner_sha256=sha(ROOT/'greekocr/harvest/wikisource.py'),header_footer='noinclude excluded from proofread body; retained in raw source',hyphenation=clean['hyphenation'],unknown_templates=clean['unknown_templates'],variant_selections=clean['variant_selections'],templates=clean['templates'],nfd=True,whitespace='collapsed with raw NFD offset map'),status=page['proofreading_status'])
    if page['pilot'] in ('perseus','gutenberg'):
        if str(raw) not in tei_cache:tei_cache[str(raw)]=tei_pages(raw) if page['pilot']=='perseus' else pg_pages(raw)
        cache=tei_cache[str(raw)]; text=cache.get(page['printed_page'],dict(text='',owners=[],transformations=[]))
        text=dict(text); text['body_nfd_characters']=len(text['text']); text['body_start']=0
        if page['pilot']=='perseus' and page['printed_page'].isdigit():
            prev=cache.get(str(int(page['printed_page'])-1))
            if prev and prev['text']:
                # TEI pb moves a complete joined word to the preceding page.
                offset=prev['text'].rfind(' ')+1; tail=prev['text'][offset:]
                text['text']=tail+' '+text['text']; text['owners']=prev['owners'][offset:]+[None]+text['owners']
                text['body_start']=len(tail)+1
                text['transformations']=list(text['transformations'])+[dict(rule='previous_tei_page_last_word_context', printed_page=page['printed_page'], previous_page=str(int(page['printed_page'])-1), text=tail)]
        return dict(**text,raw_path=page['text_path'],status=page['proofreading_status'])
    raise ValueError('source not qualified for alignment')

def literal_ownership(proof,start,end,label):
    if 'raw_normal' in proof:
        occurrences=[m.start() for m in re.finditer(re.escape(label),proof['raw_normal'])]
        if len(occurrences)!=1:return None,'raw_wikitext_span_not_unique_or_markup_interrupted'
        a=occurrences[0];b=a+len(label);mapping=proof['raw_indices']
        return [dict(path=proof['raw_path'],coordinate='NFD raw wikitext characters',start=mapping[a],end=mapping[b-1]+1)],None
    owners=proof['owners'][start:end];groups=[]
    for c,owner in zip(label,owners):
        if owner is None:
            if not c.isspace():return None,'editorial_or_unresolved_text_ownership'
            continue
        key=(owner['xpath'],owner['field'])
        if owner.get('repair'):
            groups.append(dict(path=proof['raw_path'],xpath=key[0],field=key[1],coordinate='NFD XML text-node characters',start=owner['nfd_offset'],end=owner['nfd_end'],emitted=c,repair=owner['repair']))
            continue
        if groups and (groups[-1]['xpath'],groups[-1]['field'])==key and not groups[-1].get('repair') and groups[-1]['end']==owner['nfd_offset']:groups[-1]['end']+=1
        else:groups.append(dict(path=proof['raw_path'],xpath=key[0],field=key[1],coordinate='NFD XML text-node characters',start=owner['nfd_offset'],end=owner['nfd_offset']+1))
    return groups,None

def align_page(page, lines, proof):
    return p1b_align.align_page(page, lines, proof, literal_ownership, inventory, script_class)

if __name__=='__main__':
    # The offline rerun preserves the P1 baseline and applies margin geometry.
    from rerun_p1b import main
    main()
