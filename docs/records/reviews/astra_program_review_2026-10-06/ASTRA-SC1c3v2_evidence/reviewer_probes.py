"""SF5-only adversarial text probes; no inference or repository writes."""
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import unicodedata as u

from greekocr.labelfix import release_gate as gate
from greekocr.labelfix.text import ELISION, nfd, nfc
from scripts.labelfix.clariden import l1_common as common
from tests.labelfix.test_sf5 import synthetic
from scripts.labelfix.sf5_measure import BINDING

OUT=Path(__file__).parent


def letter(c):
    return c.isalpha() and c not in ELISION


def atoms(text):
    # Independent codepoint scan: a word-final sign follows a letter plus any
    # combining marks, and is followed by neither a letter nor a combining mark.
    text=nfd(text);boundary=0;result=[]
    for i,c in enumerate(text):
        if letter(c):boundary+=1
        if c not in ELISION:continue
        j=i-1
        while j>=0 and u.combining(text[j]):j-=1
        if j<0 or not letter(text[j]):continue
        if i+1<len(text) and (letter(text[i+1]) or u.combining(text[i+1])):continue
        result.append((boundary,c))
    return result


def marked_letters(text):
    return ''.join(c for c in nfd(text) if letter(c) or u.combining(c))


def apply(original,recogniser,mode='ENSEMBLE_AB',detected=False):
    r=synthetic(recogniser,detector_apostrophe=detected)
    v=common.overlay(dict(id='reviewer',label=original,script_class='greek_poly'),r,mode,BINDING)
    return v,r


def main():
    failures=[];counts=Counter();examples=[]
    patterns=[
        'κ{a} ἡ','μ{a}','ἄλλ{a}-','κ{a}-ἄλλο','κ{a}—α','κ{a}»',
        'κ{a}\'','κ{a}’','“κ{a}” α','κ{a} μ{a} α','κ{a} μ{b}',
        'ά{a} ἡ','α\u0301{a}','ΐ{a} α','κ{a}\nα','κ{a}-\nα',
        'κ{a} ᾿Ἀ','κ{a}᾿Ἀ','κ{a}. α','κ{a}” — μ{b}',
    ]
    for pattern in patterns:
        for a in ELISION:
            for b in ELISION:
                original=pattern.format(a=a,b=b)
                recogniser=pattern.format(a=b,b=a)
                expected={k for k,_ in atoms(original)}&{k for k,_ in atoms(recogniser)}
                assert expected
                for mode in gate.MODES:
                    for detected in (False,True):
                        value,_=apply(original,recogniser,mode,detected)
                        final=value.get('label',original)
                        missing=expected-{k for k,_ in atoms(final)}
                        counts['consensus_cases']+=1;counts['consensus_'+value['status']]+=1
                        if missing:failures.append(dict(kind='released_consensus_loss',original=original,
                            recogniser=recogniser,mode=mode,detected=detected,value=value))
    for original,recogniser in [('κ᾿ α',"κ' ε"),('κ᾿ α',"κ' αβ"),
                                ('κ᾿ α',"κ'"),('κ᾿ α',"' α"),('κ᾿-\nα',"κ'-\nε")]:
        for mode in gate.MODES:
            v,_=apply(original,recogniser,mode)
            counts['letter_mismatch_cases']+=1
            if v['status']!='hold' or 'label' in v:failures.append(dict(kind='mismatch_release',value=v))
            examples.append(dict(kind='letter_mismatch',original=original,recogniser=recogniser,
                                 mode=mode,status=v['status'],reasons=[x['detail'] for x in v['hold_slots']]))
    # Breathing attachment can remove only the designated prefix. Real elision
    # and closing/opening quote characters elsewhere must remain in the pair.
    pair_cases=[
        ('κ᾿ -᾿Α',"κ᾿ -'Ἀ",'κ᾿ -Α','κ᾿ -Ἀ'),
        ('κ᾿ “᾿Α”',"κ᾿ “'Ἀ”",'κ᾿ “Α”','κ᾿ “Ἀ”'),
        ('κ᾿’ -᾽Α',"κ᾿’ -'Ἀ",'κ᾿’ -Α','κ᾿’ -Ἀ'),
        ('-᾿Α',"-'Α",'-᾿Α',"-'Α"),
        ('κ᾿ α','κ α','κ᾿ α','κ α'),
        ('κ’','κ','κ’','κ'),
        ('-᾿Α',"-'Ἐ",'-᾿Α',"-'Ἐ"),
    ]
    for original,proposal,ea,eb in pair_cases:
        actual=gate._breathing_pair(original,proposal)
        counts['breathing_pair_cases']+=1
        if tuple(map(nfd,actual))!=(nfd(ea),nfd(eb)):
            failures.append(dict(kind='breathing_pair',original=original,proposal=proposal,actual=actual,expected=[ea,eb]))
        examples.append(dict(kind='breathing_pair',original=original,proposal=proposal,actual=actual))
    for spacing in '᾿᾽':
        for prefix in ('','-','κ᾿ ','“'):
            for base,breathing in [('Α','\u0313'),('Ε','\u0314'),('Ρ','\u0314'),('α','\u0313')]:
                for attached in (False,True):
                    original=prefix+spacing+base+'λα'
                    rec=prefix+spacing+base+(breathing if attached else '')+'λα'
                    for mode in gate.MODES:
                        v,_=apply(original,rec,mode);final=v.get('label',original)
                        counts['spacing_release_cases']+=1;counts['spacing_'+v['status']]+=1
                        expected=nfc(prefix+(base+breathing if attached else spacing+base)+'λα')
                        # Leading quotes remain detector-controlled, as verified
                        # against frozen SF4 in out_of_scope_quote_probe.json.
                        # Retention of an undetected leading quote is not SF5.
                        expected=expected.removeprefix('“')
                        if v['status']!='hold' and final!=expected:
                            failures.append(dict(kind='spacing_release',original=original,recogniser=rec,mode=mode,value=v,expected=expected))
    # A pure alias delta must be unchanged; a concurrent real combining-mark
    # delta must remain a correction. alias_only cannot erase mark content.
    for a in ELISION:
        for b in ELISION:
            for original_mark,new_mark in [('α','α'),('α','ά'),('ά','ὰ'),('ἀ','ἁ'),('ᾳ','α'),('ι','ϊ')]:
                for mode in gate.MODES:
                    original='κ'+a+' '+original_mark
                    recogniser='κ'+b+' '+new_mark
                    v,_=apply(original,recogniser,mode,True)
                    counts['alias_accounting_cases']+=1
                    changed=marked_letters(original)!=marked_letters(recogniser)
                    if not changed and (v['status']!='unchanged' or v.get('label')!=original or v['changes']):
                        failures.append(dict(kind='alias_counted_correction',value=v))
                    if changed and (v['status']!='corrected' or v['alias_only'] or marked_letters(v['label'])!=marked_letters(recogniser)):
                        failures.append(dict(kind='real_edit_hidden',value=v))
    result=dict(counts=dict(counts),failures=failures,examples=examples,
                inference_calls=0,native_crops=0,network=False)
    (OUT/'reviewer_probes.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(counts=counts,failures=len(failures)),indent=2))
    assert not failures


if __name__=='__main__':main()
