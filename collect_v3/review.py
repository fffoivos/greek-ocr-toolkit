"""Read checker verdicts without authoring a pass or opening the W2 gate."""
from collections import Counter
from pathlib import Path
from .common import rows,read_json,write_json,sha
from .cards import wilson_lower


def summarize(out,tranche,phase='C1',verdict_root=None,previous=None):
    root=Path(out)/tranche/phase.lower();receipt=read_json(root/'receipt.json');report=[]
    verdict_root=Path(verdict_root) if verdict_root else root
    for stratum in receipt['strata']:
        if stratum.get('stratum')=='blind_pages':continue
        name=stratum.get('name') or stratum['source']+'__'+stratum['primary_class'];cards_path=root/name/'cards.jsonl'
        public=rows(cards_path);expected={r['card_id'] for r in public}
        path=verdict_root/(name+'.jsonl')
        if not path.exists():
            report.append(dict(source=stratum['source'],primary_class=stratum['primary_class'],status='pending',n_cards=len(public)));continue
        verdicts=rows(path);ids=[r['card_id'] for r in verdicts]
        if len(ids)!=len(set(ids)) or set(ids)!=expected:raise ValueError('verdicts must match uniform cards exactly: '+name)
        for r in verdicts:
            if r.get('letters') not in ('y','n','u') or r.get('marks') not in ('y','n','na') or r.get('crop_ok') not in ('y','n'):raise ValueError('invalid v2 verdict: '+name)
        n=len(verdicts);letters=Counter(r['letters'] for r in verdicts);marks=Counter(r['marks'] for r in verdicts);crop=Counter(r['crop_ok'] for r in verdicts)
        ly=letters['y']/n if n else None;cy=crop['y']/n if n else None
        value=dict(source=stratum['source'],primary_class=stratum['primary_class'],gazette_stratum=stratum.get('gazette_stratum'),status='reviewed',n=n,letters=dict(letters),marks=dict(marks),crop_ok=dict(crop),letters_rate=ly,crop_ok_rate=cy,letters_wilson_lower=wilson_lower(letters['y'],n),crop_wilson_lower=wilson_lower(crop['y'],n),cards_sha256=sha(cards_path),verdicts_sha256=sha(path),supplements_pooled=False)
        if phase=='C1':value['exploratory_gate']='pass' if n>=40 and ly>=.9 and cy>=.9 else 'crop_tight_page' if n>=40 and ly>=.9 else 'stop_at_20_percent'
        else:value['release_assurance']=dict(letters_lower_ge_80=value['letters_wilson_lower'] is not None and value['letters_wilson_lower']>=.8,crop_lower_ge_80=value['crop_wilson_lower'] is not None and value['crop_wilson_lower']>=.8,gated=False)
        report.append(value)
    drift=[]
    if previous:
        prior=read_json(previous)
        index={(r['source'],r['primary_class'],r.get('gazette_stratum')):r for r in prior['strata'] if r['status']=='reviewed'}
        for r in report:
            old=index.get((r['source'],r['primary_class'],r.get('gazette_stratum')))
            if old and r['status']=='reviewed':drift.append(dict(source=r['source'],primary_class=r['primary_class'],letters_rate_delta=r['letters_rate']-old['letters_rate'],crop_ok_rate_delta=r['crop_ok_rate']-old['crop_ok_rate'],W1_n=old['n'],W2_n=r['n']))
    gazette=Path(out)/tranche/'audits/gazette_strata.json'
    probe=next((r for r in read_json(gazette)['strata'] if r['stratum']=='probe_1982_1985'),None) if gazette.exists() else None
    result=dict(gazette_probe_measurement=probe,phase=phase,tranche=tranche,strata=report,drift=drift,gate_written=False,notes=['Uniform cards only; targeted supplements are never pooled.','C1 uses point estimates and minimum n=40; small row pools are disclosed.','C2 fresh 100-card class check reports Wilson lower >=80% without gating.','For W1-to-W2 drift, also draw W2 --phase C1 on matching source/class strata and provide --previous.'])
    write_json(root/'review_report.json',result);return result
