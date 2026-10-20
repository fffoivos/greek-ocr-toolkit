"""Assemble existing adjudications only. Never run readers or infer an unclear tier."""
from __future__ import annotations
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys
import unicodedata as ud
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from greekocr.labelfix.lqb import DEFAULT, PROJECTS, ROOT, HEADS, rows, sha256, dump, letters, factors

SPELL=PROJECTS/'greek-ocr-toolkit-spellcheck/docs/labelfix/spellcheck'
CARDS=PROJECTS/'greek-ocr-toolkit-spellcheck-r2cards'
COLLECT=PROJECTS/'greek-ocr-toolkit-sol-collect'
SAMPLE_TYPES={'print189':'enriched','owner39':'enriched','T4':'enriched','T2':'enriched','audit100':'decision_audit','yer_adjudication':'uniform','RU1_review':'enriched','RU1_audit':'decision_audit','RU1_two_sol':'enriched','N1_controls':'enriched','N1_lead':'enriched','R0_ia_letters':'locked_stratum'}
SAMPLE_DESCRIPTIONS={
    'print189':'the 189 selected printed-word marks cards',
    'owner39':'the 39 owner-reviewed reader-error regression cards',
    'T4':'selected witness words for marks (contrasts and capped diversity sampling)',
    'T2':'selected supervision words for marks and capitals',
    'yer_adjudication':'the seeded C1 uniform Russian yer draw within its stratum',
    'RU1_review':'lead-reviewed Russian yer/yat fault and control cells',
    'RU1_audit':'the Russian yer decision audit (30 edits and 10 keeps)',
    'RU1_two_sol':'Russian yer construction decisions with two Sol votes',
    'N1_controls':'approved numeric separator controls',
    'N1_lead':'lead-ruled raised numeric separator cells',
    'audit100':'selected sf6 release decisions, adjudicated for word marks',
    'R0_ia_letters':'24 pixel-adjudicated letter word scopes from locked Wikisource i-a (selected disagreements, 23 of 133 lines; selection-exposed v2 val)',
}

SCRATCH=Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad')


def decode_head(head, value):
    values={'none':0,'psili':1,'smooth':1,'dasia':2,'rough':2,'acute':1,'grave':2,'circumflex':3,'dialytika':1,'diaeresis':1,'subscript':1,'present':1}
    return values.get(value)


def sample_type_merge(records):
    types={r['sample_type'] for r in records}
    return next(iter(types)) if len(types)==1 else 'enriched'


def deduplicate(records):
    groups=defaultdict(list)
    for r in records:groups[(r['line_id'],json.dumps(r['slot'],sort_keys=True),r['class'])].append(r)
    truth=[];conflicts=[]
    for key, rs in sorted(groups.items()):
        values={json.dumps(r.get('target',ud.normalize('NFC',r['printed'])),ensure_ascii=False,sort_keys=True) for r in rs}
        if len(values)>1:
            conflicts.append(dict(key=key,sources=rs));continue
        r=min(rs,key=lambda r:r['tier']).copy()
        r['sample_type']=sample_type_merge(rs)
        r['population_eligible']=all(x.get('population_eligible',True) for x in rs)
        r['provenance_all']=[p for x in rs for p in x.get('provenance_all',[x['provenance']])]
        r['used_by']=sorted({v for x in rs for v in x['used_by']})
        # If a source is supervision, never silently turn its line into a holdout.
        r['exclude_from_training']=all(x['exclude_from_training'] for x in rs)
        r['rate_eligible']=all(x.get('rate_eligible',True) for x in rs)
        r['truth_id']='lqb1-'+__import__('hashlib').sha256(json.dumps(key,ensure_ascii=False).encode()).hexdigest()[:20]
        truth.append(r)
    return truth,conflicts


class Builder:
    def __init__(self):self.records=[];self.inputs={};self.issues=[];self.sources={}
    def bind(self,path):
        path=Path(path);self.inputs[str(path)]=sha256(path);return path
    def source(self,name,path,tier,readers,commit,used=(),exclude=True,rate=True):
        path=self.bind(path)
        self.sources[name]=dict(file=str(path),tier=tier,readers=readers,commit=commit,sample_type=SAMPLE_TYPES[name],sample_description=SAMPLE_DESCRIPTIONS.get(name,name+' selected fault/control cards'))
        if name=='yer_adjudication':self.sources[name].update(population='W1 ia_russian / cyrillic C1 stratum, resolved double-read yer positions',seed='20261016:C1:W1:<source>:<class>[:<stratum>]',sampling_reference=str(COLLECT/'docs/harvest/collect_v3/c1/C1_REPORT.md'))
        return dict(sample_type=SAMPLE_TYPES[name],sample_description=self.sources[name]['sample_description'],provenance=dict(set=name,file=str(path),sha256=self.inputs[str(path)],commit=commit),readers=readers,tier=tier,used_by=list(used),exclude_from_training=exclude,rate_eligible=rate)
    def add(self,meta,lid,slot,cls,printed,doc=None,**extra):
        if not lid:return
        self.records.append(dict(meta,truth_id=None,line_id=lid,slot=slot,**{'class':cls},printed=ud.normalize('NFC',printed),doc_id=doc or lid.split('--s')[0].split('-p')[0],**extra))
    def word(self,meta,lid,w,printed,doc=None,**ctx):
        ls=letters(printed)
        for i,ch in enumerate(ls):
            for h,target in zip(HEADS,factors(ch)):
                self.add(meta,lid,dict(kind='word_letter',word=w,letter=i,head=h),'marks',ch,doc,target=target,context=dict(printed_word=printed,**ctx))


def main():
    b=Builder()
    # Both peer references and the binding local brief are frozen as inputs.
    for p in [DEFAULT/'LQB_PLAN.md',DEFAULT/'INPUTS.md',SPELL/'LQB_MARKS_INPUTS.md',COLLECT/'docs/harvest/collect_v3/release_exclusions/release_exclusions.json']:b.bind(p)
    b.bind(COLLECT/'docs/harvest/collect_v3/c1/C1_REPORT.md')
    b.bind(CARDS/'docs/labelfix/spellcheck/R2/R2C_REPORT.md')
    b.bind(ROOT/'docs/records/briefs/R0c_scoring.md')
    b.bind(PROJECTS/'greek-ocr-toolkit-sol-wsr0/docs/harvest/wikisource_r0/RECEIPT.md')
    b.bind(ROOT/'docs/records/labelfix/spellcheck/R0_expected_truth_ib.json')
    # W1 is read once. Keep label/crop metadata only; never touch collector locks.
    features=PROJECTS/'collect-v3-data/run/W1/features.jsonl';b.bind(features)
    w1={r['id']:{k:r.get(k) for k in ('id','label','text','item','source','crop','crop_sha256')} for r in rows(features)}
    p=SPELL/'print_truth_s0.json';m=b.source('print189',p,'A',['blind Opus r1','blind Opus r2','Opus tiebreak as needed'],'33cacf520',used=['sf6_release','S6','sf6_gate','SF7','quote_alias'])
    b.bind(SPELL/'print_truth/key_SEALED.json')
    for key,r in json.loads(p.read_text()).items():
        if not r.get('printed'):continue
        lid,w=key.rsplit('|',1);b.word(m,lid,int(w),r['printed'])
    p=SPELL/'R2_evidence/reader_errors_39_owner_final.json';m=b.source('owner39',p,'A',['owner'],'33cacf520',used=['sf6_release','R1-A','SF7','quote_alias'],rate=False)
    owner_locations={r['db_id']:r for r in json.loads(b.bind(SPELL/'R2_evidence/reader_errors_39_card_inputs.json').read_text())}
    b.bind(SPELL/'R2_evidence/owner_sheet_notes_20261017.jsonl');b.bind(SPELL/'R2_evidence/OWNER_REMARKS_20261017.md')
    for r in json.loads(p.read_text())['cards']:
        k=owner_locations[r['db_id']];word=r['truth_word']
        # The single owner correction is already recorded in the final file.
        i=k['letter_in_word'];ch=letters(word)[i] if i<len(letters(word)) else None
        if r.get('owner_status')=='corrected':
            word='ἦγε' if r['line_id']=='384c3f89-p000059-l0013' else word
            ch=letters(word)[i]
        if ch is None:b.issues.append(dict(set='owner39',id=r['db_id'],reason='letter outside printed word'));continue
        for h,t in zip(HEADS,factors(ch)):
            b.add(m,r['line_id'],dict(kind='word_letter',word=k['word_index'],letter=i,head=h),'marks',ch,target=t,context=dict(printed_word=word))
    # Resolved T4/T2: known heads only, controls excluded; the peer establishes A.
    for deck,exclude in [('T4',True),('T2',False)]:
        p=CARDS/f'artifacts/r2_resolve/{deck}/final/resolved.jsonl'
        m=b.source(deck,p,'A',['blind Opus r1','blind Opus r2','2-of-3 Opus tiebreak as needed'],'45c8c63ce',used=['R2a'] if deck=='T2' else ['R2a_selection'],exclude=exclude)
        kp=b.bind(CARDS/f'docs/labelfix/spellcheck/R2/decks/{deck}/private/key.jsonl');keys={r['card_id']:r for r in rows(kp)}
        for r in rows(p):
            if r.get('control') or r.get('status')!='resolved' or not r.get('printed_form'):continue
            k=keys[r['card_id']];lid=k['line_id'];word=r['printed_form'];w=k['word_index']
            # letter_heads can contain UNKNOWN even on a resolved word.
            for lh in r['letter_heads']:
                i=lh['index'];ls=letters(word)
                if i>=len(ls):b.issues.append(dict(set=deck,id=r['card_id'],reason='head outside printed word'));continue
                ch=ls[i]
                for h in HEADS:
                    value=lh.get('diaeresis' if h=='dialytika' else h)
                    if value not in {'none','psili','dasia','smooth','rough','acute','grave','circumflex','dialytika','diaeresis','subscript','present'}:continue
                    target=decode_head(h,value)
                    if target!=factors(ch)[HEADS.index(h)]:
                        b.issues.append(dict(set=deck,id=r['card_id'],head=h,reason='printed form and resolved head disagree'));continue
                    b.add(m,lid,dict(kind='word_letter',word=w,letter=i,head=h),'marks',ch,k['doc'],target=target,context=dict(printed_word=word,card_id=r['card_id'],physical_index=k['crop_letter_offset']+i))
    # CQ1 is a view of T2 targets, never an independent truth reading.
    cq=b.bind(CARDS/'artifacts/cq1/keys/cap1.json');m=dict(m);m['used_by']=sorted(set(m['used_by']+['CQ1']))
    for r in json.loads(cq.read_text())['items'].values():
        if r.get('control'):continue
        b.add(m,r['line_id'],dict(kind='letter_index',index=r['crop_letter_index']),'capitals',letters(r['printed_form'])[r['letter_index']],r['doc'],context=dict(subset_file=str(cq)))
    # S8's peer reference does not state reader models. Keep the data bound,
    # inventory the resolved items, and make the tier uncertainty reviewable.
    dev=PROJECTS/'greek-ocr-toolkit-spellcheck-s8/docs/labelfix/spellcheck/S8_DEV/evidence/dev_truth.jsonl.gz';b.bind(dev)
    dev_items=[r for r in rows(dev) if r.get('type')=='item' and not r.get('control') and r.get('status')=='resolved' and r.get('truth')]
    b.issues.append(dict(set='S8_DEV',reason='peer says two-reader adjudicated, but does not identify reader models/blinding; tier unclear',resolved_items=len(dev_items),file=str(dev)))
    # Owner release audit, positions bound by the sealed saved card key.
    audit=SPELL/'S8_DEV/audit100_private/audit100_final.json';b.bind(audit);b.bind(SPELL/'L1A2_AUDIT100_RESULT.md')
    ap=b.bind(SPELL/'S8_DEV/private/audit100/items_key.json')
    ak=json.loads(ap.read_text());audit_results=json.loads(audit.read_text())
    m=b.source('audit100',audit,'A',['two blind Opus readers','Opus tiebreak as needed; owner review per peer summary'],'33cacf520',used=['SF7','quote_alias'])
    for lid,result in audit_results.items():
        for status,g,released,printed in result['cards']:
            if status=='unknown' or not printed:continue
            match=[r for r in ak if not r.get('control') and r['line_id']==lid and r['forms']['google']==g and r['forms']['released']==released]
            if len(match)!=1:
                b.issues.append(dict(set='audit100',id=lid,reason='nonunique word binding'));continue
            b.word(m,lid,match[0]['word_index'],printed,audit_key=str(ap))
    sub=SPELL/'R2_evidence/substitution_sample_60.json';b.bind(sub)
    b.issues.append(dict(set='substitution60',tier='A',reason='sample contains proposed substitutions; aggregate owner precision and notes do not bind complete printed heads for all 60; no blank-note acceptance convention authorized for this sheet',file=str(sub)))
    # RU1: original yer truth, with exact W1 mappings in the control inventory.
    p=ROOT/'artifacts/ru1/keys/control_inventory.json';m=b.source('yer_adjudication',p,'A',['blind Opus r1','blind Opus r2'],'ab6f58f732c495ebcbbbd6b5094b540e3f7ebd3d',used=['ru1_v1'])
    b.bind(COLLECT/'docs/harvest/collect_v3/c1/yer_adjudication/table.json')
    for r in json.loads(p.read_text()):
        lid=r.get('w1_id') or r.get('source_id')
        for s in r['slots']:
            t=s.get('control_truth')
            if t not in ('ъ','ь','ѣ'):continue
            b.add(m,lid,dict(kind='offset',offset=s['offset']),'ru2_yat' if t=='ѣ' else 'ru1_yer',t,r.get('book'))
    lead=ROOT/'docs/records/labelfix/secondary/RU1_LEAD_REVIEW.md';idx=b.bind(SCRATCH/'ru1_review/lead/sheets_index.json');cells=json.loads(idx.read_text())['items'];seen={(r['row_id'],r['offset']) for r in cells}
    for partition in ('review','audit'):
        m=b.source('RU1_'+partition,lead,'B',['lead pixel ruling'],'ab6f58f732c495ebcbbbd6b5094b540e3f7ebd3d',used=['ru1_v1'] if partition=='review' else [])
        for r in cells:
            if r['set']!=partition or r['cell']==9:continue
            t=({17:'ѣ',27:'ѣ',23:'ь'}.get(r['cell'],'ъ') if partition=='review' else 'ъ' if r['decision']=='edit_hard' else 'ь')
            b.add(m,r['row_id'],dict(kind='offset',offset=r['offset']),'ru2_yat' if t=='ѣ' else 'ru1_yer',t,r['book'],context=dict(cell=r['cell'],mapping_file=str(idx)))
    # Remaining two-agreeing Sol decisions are construction evidence, in-sample.
    p=ROOT/'artifacts/ru1/decisions.jsonl';m=b.source('RU1_two_sol',p,'C',['Sol r1','Sol r2'],'ab6f58f732c495ebcbbbd6b5094b540e3f7ebd3d',used=['ru1_v1'])
    for r in rows(p):
        if (r['row_id'],r['offset']) in seen:continue
        votes=[v.get('call') for v in r.get('reads',{}).values() if v.get('gate_status')=='VALID']
        if len(votes)!=2 or len(set(votes))!=1 or votes[0] not in ('ь','ъ'):continue
        b.add(m,r['row_id'],dict(kind='offset',offset=r['offset']),'ru1_yer',votes[0])
    # N1 exact gap slots; source control record omits offsets, so lossless
    # numeric tokenization recovers the same token/slot pair, never its truth.
    from greekocr.numerics.tokens import tokenize
    slots={}
    for p in [ROOT/'artifacts/n1/frame_step1.jsonl',*sorted((ROOT/'artifacts/n1').glob('n1t*/slots.jsonl'))]:
        b.bind(p)
        for r in rows(p):slots[r['slot_id']]=r
    dashp=b.bind(ROOT/'artifacts/n1/controls/dash_types.jsonl');dashes={r['slot_id']:r['truth'] for r in rows(dashp)}
    for name,p in [('N1_controls',ROOT/'artifacts/n1/controls/approved.jsonl'),('N1_lead',ROOT/'artifacts/n1/lead_t.jsonl')]:
        m=b.source(name,p,'B',['lead pixel ruling'],'ab6f58f732c495ebcbbbd6b5094b540e3f7ebd3d',used=['n1_*'])
        for r in rows(p):
            sid=r['slot_id'];lid=sid.split(':t')[0];t=r['truth']
            if t=='hold' or lid=='lekythos--dcfa99599048d352--s000-l0144':continue
            if t=='hyphen or dash':t=dashes.get(sid)
            if not t:b.issues.append(dict(set=name,id=sid,reason='dash type unresolved'));continue
            ref=w1[lid]['label'];loc=slots.get(sid)
            if loc is None:
                try:
                    tok,slot=sid.rsplit(':t',1)[1].split(':s');loc=next(s for s in tokenize(ref)[int(tok)].slots if s.index==int(slot));a,z=loc.start,loc.end
                except (IndexError,StopIteration):b.issues.append(dict(set=name,id=sid,reason='gap not located'));continue
            else:a,z=loc['start'],loc['end']
            b.add(m,lid,dict(kind='gap',id=sid),'n1_separator',t,r.get('document'),context=dict(reference=ref,start=a,end=z,dash_type=dashes.get(sid)))
    # C1 has one Opus read per card, not two blind reads per item.
    report=b.bind(COLLECT/'docs/harvest/collect_v3/c1/C1_REPORT.md')
    for p in sorted((COLLECT/'docs/harvest/collect_v3/c1/verdicts').glob('*.jsonl')):
        b.bind(p);b.issues.append(dict(set='C1/'+p.stem,file=str(p),items=sum(1 for _ in rows(p)),reason='one Opus reader per card (two disjoint 50-card halves); no defined A/B/C tier'))
    b.issues.append(dict(set='locked_strata',file=str(COLLECT/'docs/harvest/collect_v3/release_exclusions/release_exclusions.json'),reason='ID registry is not printed truth; Wikisource scan-aligned transcription has no stated A/B/C reader tier; locked (ii)/(ia) truth file not supplied by peer reference'))
    # Owner overlay v1.1 is an explicit revision of earlier truth, applied
    # symmetrically before deduplication, exactly as the peer scorer requires.
    overlay=b.bind(PROJECTS/'greek-ocr-toolkit-spellcheck-r2prep/docs/labelfix/spellcheck/R2/truth_overlay_v1_1.json')
    ov=json.loads(overlay.read_text())
    ownerloc=owner_locations['384c3f89-p000059-l0013:s33']
    for r in b.records:
        slot=r.get('slot') or {}
        if r['line_id']=='384c3f89-p000059-l0013' and r['class']=='marks' and slot.get('word')==ownerloc['word_index'] and slot.get('letter')==ownerloc['letter_in_word']:
            r['original_target']=r['target']
            r['target']=ov['entries'][0]['new_tuple'][HEADS.index(slot['head'])]
            r['printed']='ἦ'
            word=r['context']['printed_word'];ls=letters(word)
            # For this recorded eta correction the word is explicitly ἦγε.
            r['context']['printed_word']='ἦγε'
            r['truth_overlay']=dict(file=str(overlay),sha256=b.inputs[str(overlay)],version=ov['version'])
    # One document identity across independently supplied truth sources.
    for r in b.records:
        if r['line_id'] in w1:
            feature=w1[r['line_id']]
            r['doc_id']=feature['source']+':'+feature['item']
        elif '-p' in r['line_id']:
            r['doc_id']=r['line_id'].split('-p')[0]
    # Existing R0 pixel adjudication only; no new reading or recogniser work.
    local=ROOT/'docs/records/labelfix/spellcheck'
    for p in [local/'R0_REPORT.md',ROOT/'docs/records/briefs/R0_recogniser_audit.md',local/'R0_expected_truth_ia.json',local/'R0_adjudication_private/ia/items_key.json',ROOT/'docs/records/harvest/wikisource/READS.md']:b.bind(p)
    p=local/'R0_evidence/scoring/letter_units.jsonl'
    m=b.source('R0_ia_letters',p,'A',['two blind Opus readers; R0b AGREED; controls passed'],'R0c existing local evidence')
    ia_lines={r['line_id']:r for r in rows(b.bind(local/'R0_locked_set.jsonl'))}
    key={r['id']:r for r in json.loads((local/'R0_adjudication_private/ia/items_key.json').read_text())}
    census=list(rows(b.bind(local/'R0_evidence/ia/word_disagreement_census.jsonl')))
    verdict={r['id']:r for r in json.loads((local/'R0_expected_truth_ia.json').read_text())}
    for unit in rows(p):
        if unit['stratum']!='wikisource_ia':continue
        k=key[unit['card_id']];assert not k['control'] and verdict[unit['card_id']]['adjudicated']['status']=='AGREED'
        lid=unit['line_id'];ref=''.join(x[0] for x in letters(ia_lines[lid]['google']))
        form=''.join(x[0] for x in letters(k['forms']['google']))
        line_words=sorted([r for r in census if r['line_id']==lid],key=lambda r:r['start'])
        joined=''.join(''.join(x[0] for x in letters(r['reference_forms']['google'])) for r in line_words)
        assert joined==ref,(lid,joined,ref)
        a=sum(len(letters(r['reference_forms']['google'])) for r in line_words if r['end']<=k['start'])
        assert ref[a:a+len(form)]==form,(unit['card_id'],a,form)
        b.add(dict(m,population_eligible=False),lid,dict(kind='base_span',start=a,end=a+len(form)),'letters',unit['truth'],unit['doc'],context=dict(reference=ref,card_id=unit['card_id'],full_line_certified=False,edition_caveat='Wikisource edition normalization is reference only; literal R0 pixel forms override transcription within these selected scopes; no full-line or population claim.'))
    for issue in b.issues:
        if issue['set']=='locked_strata':issue['reason']='i-a has 24 tier-A pixel-adjudicated word scopes (125 known letters/23 lines), added separately; remaining i-a and all 1,246 i-b lines are reference transcription, not pixel truth; i-b reader slots remain pending'
    truth,conflicts=deduplicate(b.records)
    DEFAULT.mkdir(parents=True,exist_ok=True)
    for name,records in [('truth_v1.jsonl',truth),('conflicts.jsonl',conflicts)]:
        (DEFAULT/name).write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in records))
    # Exclusion is line-level. A T2-supervised line must never be exported as
    # excluded merely because another source supplies a different slot on it.
    supervision={r['line_id'] for r in truth if not r['exclude_from_training']}
    exclusions=sorted({r['line_id'] for r in truth if r['exclude_from_training']}-supervision)
    (DEFAULT/'truth_v1_exclusion_ids.txt').write_text(''.join(x+'\n' for x in exclusions))
    for instrument in [Path(__file__),ROOT/'greekocr/labelfix/lqb.py',PROJECTS/'greek-ocr-toolkit-spellcheck-r2prep/scripts/labelfix/r2_score.py',PROJECTS/'greek-ocr-toolkit-cleanup/greekocr/adjudicate/score.py']:b.bind(instrument)
    membership=Counter((r['class'],r['tier'],p['set']) for r in truth for p in {p['set']:p for p in r['provenance_all']}.values())
    counts=Counter((r['class'],r['tier'],r['provenance']['set']) for r in truth)
    manifest=dict(schema='lqb-truth-v1.1',sample_type_counts=dict(Counter(x['sample_type'] for x in b.sources.values())),letters_truth=dict(sets=1,word_scopes=24,known_letters=125,lines=23,full_lines=0,population_eligible=False,ib='reference transcription, not pixel truth'),sha256=sha256(DEFAULT/'truth_v1.jsonl'),items=len(truth),tiers=dict(Counter(r['tier'] for r in truth)),classes=dict(Counter(r['class'] for r in truth)),counts=[dict(zip(('class','tier','set'),k),n=v) for k,v in sorted(counts.items())],source_membership_counts=[dict(zip(('class','tier','set'),k),n=v) for k,v in sorted(membership.items())],commit_semantics='peer reference commit where supplied; local sources use current worktree base ab6f58f732c495ebcbbbd6b5094b540e3f7ebd3d; exact file identity is always sha256',conflicts=len(conflicts),exclusion_ids=len(exclusions),supervision_overlap_lines=len(supervision & {r['line_id'] for r in truth if r['exclude_from_training']}),inputs=b.inputs,sources=b.sources,issues=b.issues)
    dump(DEFAULT/'truth_v1.manifest.json',manifest)
    print(json.dumps({k:v for k,v in manifest.items() if k not in ('inputs','sources','issues','counts')}))

if __name__=='__main__':main()
