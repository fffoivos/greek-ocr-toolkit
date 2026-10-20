"""Aggregate C1 verdicts per stratum: validates one verdict per card, Wilson CIs, gate letters>=90% and crop_ok>=90% (point, n=100)."""
import json,sys,math,collections,re
from pathlib import Path
R=Path(__file__).parent/'c1';KEYS=Path.home()/'Projects/collect-v3-data/run/W1/c1'
def wilson(k,n,z=1.96):
    p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d;return max(0,c-h),min(1,c+h)
out={}
for s in sorted(p.name for p in R.iterdir() if p.is_dir()):
    d=R/s;V={}
    for h in 'ab':
        cards=[json.loads(l)['card_id'] for l in open(d/f'cards_{h}.jsonl')]
        f=d/f'out_{h}.jsonl'
        if not f.exists():break
        v={(r:=json.loads(l))['card_id']:r for l in open(f) if l.strip()}
        if set(v)!=set(cards):
            assert set(v)<=set(cards),(s,h,'unknown card ids');print(s,h,'incomplete',len(v),'/',len(cards));break
        V.update(v)
    else:
        n=len(V);c=lambda k,val:sum(r[k]==val for r in V.values())
        err=collections.Counter(e for r in V.values() for e in r['errors'])
        L=c('letters','y');C=c('crop_ok','y');M=c('marks','y');Mna=c('marks','na')
        out[s]=dict(n=n,letters_y=L,letters_n=c('letters','n'),letters_u=c('letters','u'),letters_ci=[round(x,3) for x in wilson(L,n)],marks_y=M,marks_n=c('marks','n'),marks_na=Mna,crop_ok_y=C,crop_ok_ci=[round(x,3) for x in wilson(C,n)],gate='pass' if n==100 and L>=90 and C>=90 else 'fail',top_errors=err.most_common(5),
                  fails=[f"{k}: {r['detail']} [{','.join(r['errors'])}]" for k,r in sorted(V.items()) if r['letters']!='y' or r['crop_ok']!='y'])
        key=json.load(open(KEYS/f'{s}_key.json'))
        lid=lambda k:key[k]['line_id']
        MARK={'wrong_mark','missing_mark','extra_mark'}
        out[s]['mark_errors']=[dict(card_id=k,line_id=lid(k),errors=sorted(set(r['errors'])&MARK),detail=r['detail'],side='google_label') for k,r in sorted(V.items()) if r['marks']=='n']
        out[s]['neighbour_ink']=[dict(card_id=k,line_id=lid(k),errors=r['errors'],detail=r['detail']) for k,r in sorted(V.items()) if r['crop_ok']=='n' and set(r['errors'])&{'crop_overrun','merged_two_lines'}]
        SUP=set('⁰¹²³⁴⁵⁶⁷⁸⁹ⁿᵐᵃᵇᶜᵈᵉ')
        sup=lambda r:'superscript' in r['detail'].lower() or bool(SUP&set(r['detail']))
        lun=lambda r:'ϲ' in r['detail'] or 'lunate' in r['detail'].lower()
        out[s]['superscript']=[dict(card_id=k,line_id=lid(k),detail=r['detail']) for k,r in sorted(V.items()) if sup(r)]
        dash=lambda r:any(t in r['detail'] for t in ('—','–','dash'))
        out[s]['dash']=[dict(card_id=k,line_id=lid(k),detail=r['detail']) for k,r in sorted(V.items()) if dash(r)]
        sep=lambda r:'punctuation' in r['errors'] and bool(re.search(r'\d[·.,\-]\d',r['detail']))
        out[s]['separator']=[dict(card_id=k,line_id=lid(k),detail=r['detail']) for k,r in sorted(V.items()) if sep(r)]
        out[s]['lunate_sigma']=[k for k,r in sorted(V.items()) if lun(r)]
        # Codec-convention letters: a card whose only letter fault is a printed lunate sigma labelled σ counts as y.
        only_lun=[k for k,r in V.items() if r['letters']=='n' and lun(r) and set(r['errors'])&{'wrong_letter','lookalike_script_letter','missing_word_or_span','extra_text','digits','punctuation','hyphen'}=={'wrong_letter'} and not sup(r)]
        out[s]['letters_y_codec_convention']=L+len(only_lun);out[s]['lunate_only_cards']=sorted(only_lun)
        # Coordinator ruling: printed ϲ labelled σ is wrong_letter (strict) even where a checker scored it y.
        lun_y=[k for k,r in V.items() if r['letters']=='y' and lun(r)]
        out[s]['lunate_scored_y_by_checker']=sorted(lun_y);out[s]['letters_y']=L-len(lun_y);out[s]['letters_n']+=len(lun_y)
        out[s]['letters_ci']=[round(x,3) for x in wilson(L-len(lun_y),n)]
        out[s]['gate']='pass' if n==100 and L-len(lun_y)>=90 and C>=90 else 'fail'
        print(s,'n',n,'letters(strict)',out[s]['letters_y'],'marks',M,'/',n-Mna,'crop_ok',C,out[s]['gate'],'| codec-conv letters',out[s]['letters_y_codec_convention'],'superscript',len(out[s]['superscript']),'dash',len(out[s]['dash']),'separator',len(out[s]['separator']),err.most_common(3))
json.dump(out,open(R/'c1_results.json','w'),ensure_ascii=False,indent=1)
