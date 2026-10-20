"""Rev-2 label admission. Literal labels and frozen T4b evidence survive."""
from collections import Counter,defaultdict
import re,unicodedata as ud
from .config import POLY,HOLD,SPECS,marks
from .vendor.conventions import (apply_conventions as frozen_conventions,
    roman_convention as frozen_roman,ROMAN_TABLE,ROMAN,AMBIGUOUS_ROMAN,WORD,key)
from .vendor.classify import inspect
from .vendor.lookalike_rule import apply as lookalike

CONTEXT=re.compile(r'(?:§|\b(?:κεφ(?:άλαιον|άλαιο|αλαιον|αλαιο)?|τόμ(?:ος|ου)?|τομ(?:ος|ου)?|vol|cap|chapter)\.?)\s*$',re.I)
AFTER_CONTEXT=re.compile(r'^\s*(?:§|(?:κεφ|τόμ|τομ|vol|cap|chapter)\b)',re.I)

def roman_convention(text,chapter_heading=False):
    words=list(WORD.finditer(text));fixes=[];ambiguous=[];changes={}
    for i,m in enumerate(words):
        token=m.group();mapped=''.join(ROMAN_TABLE.get(c,c) for c in token)
        suspect=any(c in ROMAN_TABLE for c in token)
        shape=set(token)<=ROMAN|set(ROMAN_TABLE)|AMBIGUOUS_ROMAN
        if not shape or not (suspect or set(token)&AMBIGUOUS_ROMAN):continue
        whole=bool(re.fullmatch('[IVXLCMD]+',mapped))
        before=text[:m.start()];after=text[m.end():]
        context=chapter_heading or bool(CONTEXT.search(before)) or bool(AFTER_CONTEXT.search(after))
        # Numeral sequences require a neighbouring whole numeral token, with
        # only list punctuation/whitespace between; ordinary prose is not context.
        for j in (i-1,i+1):
            if not 0<=j<len(words):continue
            q=words[j];qm=''.join(ROMAN_TABLE.get(c,c) for c in q.group())
            gap=text[q.end():m.start()] if j<i else text[m.end():q.start()]
            if re.fullmatch(r'[\s,;:()\[\]./–—-]+',gap or '') and re.fullmatch('[IVXLCMD]+',qm):context=True
        if whole and context:
            changes[m.start()]=mapped;fixes.append(dict(old=token,new=mapped,context='chapter_heading_or_adjacent_marker_or_numeral_sequence'))
        else:ambiguous.append(token)
    return WORD.sub(lambda m:changes.get(m.start(),m.group()),text),fixes,ambiguous

def word_scripts(text):
    result=[]
    for word in text.split():
        scripts=set()
        for c in word:
            if not c.isalpha():continue
            name=ud.name(c,'');scripts.add(next((s for s in ('Greek','Latin','Cyrillic') if s.upper() in name),'Other'))
        result.append([word,next(iter(scripts)) if len(scripts)==1 else 'Mixed' if scripts else 'none'])
    return result

def apply_rules(features,context=None,serbian=True):
    frozen_conventions(features,context)
    for r in features:
        # The authoritative Greek+Latin admission rule sees the literal fixed
        # label before any Roman mapping can hide a suspect token.
        rule_text=r['fixed_label'];r['lookalike_rule']='not_applicable'
        if r['source']=='ia_greek_latin':
            mapped,r['lookalike_rule']=lookalike(rule_text)
            if mapped is not None:rule_text=mapped
        text,fixes,ambiguous=roman_convention(rule_text,r.get('chapter_heading',False))
        r['roman_fixes']=fixes;r['roman_ambiguous']=ambiguous
        r['text_exclusions']=[x for x in r['text_exclusions'] if x!='ambiguous_roman_numeral']
        if ambiguous:r['text_exclusions'].append('ambiguous_roman_numeral')
        r['gazette_polytonic']=bool(r['source']=='gazette_modern' and (r.get('script_class')=='greek_poly' or r.get('primary_class') in ('poly1850','poly1900','greek_poly')))
        if r['gazette_polytonic']:
            r['text_exclusions'].append('gazette_polytonic_failed_v2')
            if r['primary_class']=='modern_scanned':r['primary_class']='poly1900'
        if r['source']=='gazette_modern':
            r['gazette_stratum']='probe_1982_1985' if 1982<=int(r.get('year') or 0)<=1985 else 'measured_1986_1990'
        r['literal_label']=r['fixed_label'];r['long_s_label_count']=text.count('ſ')
        text=text.replace('ſ','s');r['emdash_to_hyphen_count']=text.count('—');text=text.replace('—','-')
        # Count observed label substitutions, not unobserved physical glyphs.
        r['elstat_raised_dot_count']=0
        if r['source']=='elstat':
            text,n=re.subn(r'(?<=\d)·(?=\d)', '.',text);r['elstat_raised_dot_count']=n
        if r['lookalike_rule']=='excluded':r['text_exclusions'].append('lookalike_script_ambiguous')
        if r['source']=='bsb_poly1850' and r.get('primary_class')=='mixed_greek_latin':r['text_exclusions'].append('bsb_mixed_stratum_removed')
        r['label_after_conventions']=text;r['normalised_label']=text;r['label']=text
        r['crop_tight_page']=r['source'] in HOLD
        if 'p1_admitted' not in r:r['p1_admitted']=r.get('admitted',True)
        r['admitted']=bool(r['p1_admitted'] and not r['crop_tight_page'])
        r['marks_correction_required']=r['source'] in POLY or r['gazette_polytonic']
        r['source_marks']=marks(r['source']) if r['source'] in SPECS else None
        if r['gazette_polytonic']:
            r['source_marks']=dict(y=None,n=None,rate=None,evidence='1982-1990 Gazette-polytonic marks unmeasured; failed polytonic stratum is excluded, modern marks rate does not apply')
        r['codec_serbian_enabled']=serbian
        if r['source']=='serbia' and serbian:
            check=inspect(r.get('text',r['fixed_label']),r.get('confidence',1.),tall=r.get('tall_box',False),serbian=True)
            r['codec_v1_pass']=check['codec_v1_pass'];r['codec_unknown']=check['codec_unknown']
            r['original_usable']=bool(r.get('admitted',True) and check['codec_v1_pass'] and r.get('geometry_positive',False) is False)
            r['fixed_usable']=r['original_usable'] and r.get('fixed_text_gate_pass',True) and not r.get('native_withheld',False) and not r.get('duplicate_crop_label',False)
        r['tags']=[t for t in r.get('tags',[]) if t not in ('marks_correction_required','roman_lookalike_normalized','ambiguous_roman_numeral','dropped_line_end_hyphen','crop_tight_page','lookalike_script_ambiguous')]
        if fixes:r['tags'].append('roman_lookalike_normalized')
        if r['marks_correction_required']:r['tags'].append('marks_correction_required')
        if r['crop_tight_page']:r['tags'].append('crop_tight_page')
        r['tags']=sorted(set(r['tags']+r['text_exclusions']))
        r['candidate_usable']=bool(r['fixed_usable'] and not r['text_exclusions'])
        r['usable_final']=r['candidate_usable'] and not r['crop_tight_page']
    return features

def boundary_hyphens(features,context=None):
    """Extend the attested dropped-hyphen rule across column/page boundaries.

    Witnesses retain both labels and boundary type for physical W1 checking.
    A continuation without the two-other-page lexical evidence remains unknown.
    """
    occurrences=defaultdict(set);nonfinal=Counter();bybook=defaultdict(list)
    if context:
        for w,ps in context['occurrences'].items():occurrences[w].update(tuple(p) for p in ps)
        nonfinal.update(context['nonfinal'])
    for r in features:
        words=[key(m.group()) for m in WORD.finditer(r['fixed_label'])]
        for w in words:occurrences[w].add((r['track'],r['page_id']))
        nonfinal.update(words[:-1]);bybook[r['source'],r.get('item',r['page_id'])].append(r)
    witnesses=[]
    for pool in bybook.values():
        pages=defaultdict(list)
        for r in pool:pages[r['page_id']].append(r)
        ordered=[];column={}
        for _,rr in sorted(pages.items(),key=lambda v:(v[1][0].get('page') or 0,v[0])):
            columns=[]
            for r in sorted(rr,key=lambda r:(r['crop_bbox'][0],r['crop_bbox'][1],r['id'])):
                found=next((col for col in columns if abs(col[0]['crop_bbox'][0]-r['crop_bbox'][0])<=1.5*r['page_median_row_height']),None)
                if found is None:columns.append([r])
                else:found.append(r)
            for n,col in enumerate(columns):
                for r in sorted(col,key=lambda r:(r['crop_bbox'][1],r['id'])):column[r['id']]=n;ordered.append(r)
        for i,r in enumerate(ordered):
            text=r['fixed_label'];tail=re.search(r'([^\W\d_]+)([-–—]?)\s*$',text)
            q=ordered[i+1] if i+1<len(ordered) else None
            head=re.match(r'\s*([^\W\d_]+)',q['fixed_label']) if q else None
            boundary='page' if q and q['page_id']!=r['page_id'] else 'column' if q and column[q['id']]!=column[r['id']] else 'line'
            # Do not cross uncollected page gaps.
            if boundary=='page' and isinstance(q.get('page'),int) and isinstance(r.get('page'),int) and q['page']!=r['page']+1:q=None;head=None
            lower=bool(head and head.group(1)[0].islower())
            if tail and q and lower and boundary in ('page','column') and not tail.group(2):
                a,b=key(tail.group(1)),key(head.group(1));other=occurrences[a+b]-{(r['track'],r['page_id']),(q['track'],q['page_id'])}
                if len(a)>=2 and len(b)>=2 and len(other)>=2 and nonfinal[a]==0:
                    r['hyphen_test']='dropped_end_hyphen_attested_join';r['join_evidence']=dict(tail=tail.group(1),head=head.group(1),joined_key=a+b,other_pages=[list(p) for p in sorted(other)])
                    if 'dropped_line_end_hyphen' not in r['text_exclusions']:r['text_exclusions'].append('dropped_line_end_hyphen')
                    r['candidate_usable']=False;r['usable_final']=False
            if tail and (tail.group(2) or lower or r.get('join_evidence')):
                witnesses.append(dict(id=r['id'],source=r['source'],item=r.get('item'),page_id=r['page_id'],crop=r.get('crop'),literal_label=text,normalised_label=r['label_after_conventions'],next_line_id=q['id'] if q else None,next_label=q['fixed_label'] if q else None,boundary=boundary if q else 'unavailable',hyphen_test=r.get('hyphen_test'),visible_label_hyphen=bool(tail.group(2)),hypothesis='check printed hyphen versus truncated/misread letter; no automatic glyph correction',verdict=None))
    return witnesses
