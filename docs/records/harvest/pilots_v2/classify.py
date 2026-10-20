"""P1 text-admission overlay. Frozen main admission is imported unchanged."""
from __future__ import annotations
import json,re,sys,unicodedata as ud
from collections import Counter
from pilotlib import ROOT
sys.path.insert(0,str(ROOT))
from greekocr.harvest.admission import inventory,script_class,normalize_label

codec=json.loads((ROOT/'greekocr/_vendor/codec/v1.json').read_text())
ALPHABET={a['ch'] for a in codec['atoms']}

def codec_characters(value):
    # The shipped codec binds every token explicitly; never drop unknowns.
    if isinstance(value,dict):
        for key in ['tokens','id_to_token','vocab','characters','codepoints']:
            if key in value:return codec_characters(value[key])
    if isinstance(value,list):
        return set(x for x in value if isinstance(x,str) and len(x)==1)
    return set()

def inspect(text,confidence=None,tall=False,human_gt=False):
    text=normalize_label(text);inv=inventory(text);letters=[c for c in text if ud.category(c).startswith('L')]
    caps=len(letters)>=3 and all(not c.islower() for c in letters) and any(c.isupper() for c in letters)
    visible=sum(not c.isspace() and not ud.category(c).startswith(('M','C')) for c in text)
    numeric=visible>0 and inv['digits']/visible>=.4
    leaders=list(re.finditer(r'(?:\.[ \t]*){5,}',text))
    mixed=inv['greek_letters']>0 and bool(inv['latin_words'])
    tags=[]
    if caps:tags.append('caps')
    if numeric:tags.append('numeric')
    leader_pattern=any(any(c.isalpha() for c in text[:m.start()]) and re.fullmatch(r'\s*(?:\d+[.,]?|[IVXLCDM]+)\s*',text[m.end():]) for m in leaders)
    if leaders:tags.append('dot_run_candidate')
    if leader_pattern:tags.append('leaders')
    if tall and (caps or (3<=inv['letter_count']<=120 and len(text.split())<=14)):tags.append('heading')
    if re.search(r'[«»“”]|(?:^|\s)[—–-](?=\s|[Α-ω])',text):tags.append('dialogue_punctuation')
    if re.search(r'\b(?:ΔΡΑΧ|ΤΙΜΗ|ΠΩΛΕΙΤΑΙ|ΑΓΓΕΛ|ΣΥΝΔΡΟΜ)',text.upper()):tags.append('advertisement_candidate')
    reasons=[];rules=[]
    if not human_gt and (confidence is None or confidence<.89):reasons.append('low_confidence')
    if inv['letter_count']<10:
        if caps:rules.append('caps_3_letters')
        elif numeric:rules.append('digits_40pct')
        elif leaders:rules.append('leader_run')
        else:reasons.append('short_line')
    if 3*(inv['nonspace_count']-inv['letter_count'])>inv['nonspace_count']:
        if numeric:rules.append('digits_40pct')
        elif leaders:rules.append('leader_run')
        else:reasons.append('symbol_heavy')
    if inv['other_letters']:reasons.append('foreign_script')
    if inv['mixed_words']:reasons.append('mixed_word')
    if tall:
        if 'heading' in tags:rules.append('heading_crop')
        else:reasons.append('tall_box')
    if not rules:rules=['base']
    runs=[dict(start=m.start(),end=m.end(),dot_count=m.group().count('.'),canonical='.'*m.group().count('.'),dot_count_label='DOTS:'+str(m.group().count('.')),count_source='source GT' if human_gt else 'DocAI symbols/text; physical count unverified') for m in leaders]
    canonical_label=re.sub(r'(?:\.[ \t]*){5,}',lambda m:'.'*m.group().count('.')+(' ' if m.group()[-1].isspace() else ''),text)
    unknown=sorted(set(ud.normalize('NFD',text))-ALPHABET)
    return dict(text=text,canonical_label=canonical_label,script_class=script_class(text,inv) if inv['letter_count'] else 'nonletter',mixed_line=mixed,line_tags=tags,inventory=inv,visible_characters=visible,digit_visible_fraction=inv['digits']/visible if visible else 0,admitted=not reasons,rejection_reasons=reasons,admission_rules=sorted(set(rules)),leader_runs=runs,codec_v1_pass=not unknown,codec_unknown=unknown,confidence=confidence,confidence_scope='not applicable: source-declared manually corrected GT' if human_gt else 'mean of DocAI symbols in exact line text anchors')
