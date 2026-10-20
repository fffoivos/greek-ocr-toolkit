"""LQB3 offline rebuild. Frozen truth and all peer artifacts remain read-only."""
from __future__ import annotations
import html
import json
import math
from collections import defaultdict
from pathlib import Path
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from greekocr.labelfix import lqb
OUT=lqb.DEFAULT
COLLECT=lqb.PROJECTS/'greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3'
SX=lqb.PROJECTS/'greek-ocr-toolkit-spellcheck/artifacts/sx1'


def read(p):return json.loads(Path(p).read_text())
def bind(p,inputs):
    p=Path(p);inputs[str(p)]=lqb.sha256(p);return p

def wilson(e,n):
    if not n:return None
    z=1.959963984540054;p=e/n;d=1+z*z/n
    c=(p+z*z/(2*n))/d;r=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [0.0 if e==0 else max(0,c-r),1.0 if e==n else min(1,c+r)]

def measurement(cls,stratum,source,metric,e=None,n=None,typ='uniform',tier='A',need=None,**extra):
    return dict(class_name=cls,stratum=stratum,source_set=source,metric=metric,errors=e,n=n,
                rate=e/n if n else None,ci95=wilson(e,n) if n else None,
                sample_type=typ,tier=tier,status='measured' if n else 'not measured',truth_needed=need,**extra)

def prepare_versions(inputs):
    registry=read(OUT/'versions.json')
    # W1 features do not contain the historical audit or R0 cohorts. Bind the
    # saved Google stream explicitly rather than silently substituting labels.
    supplemental=[]
    r0=ROOT/'docs/labelfix/spellcheck/R0_locked_set.jsonl'
    supplemental.append(dict(path=str(bind(r0,inputs)),sha256=lqb.sha256(r0),id_field='line_id',text_field='google'))
    sx_status='pending';sx_info={}
    if (SX/'RECEIPT.json').exists() and (SX/'sf6_release_extract_lqb.jsonl').exists():
        receipt=read(bind(SX/'RECEIPT.json',inputs))
        for field in ['extract','not_in_selection','truth_input','script']:
            entry=receipt[field];p=Path(entry.get('local_path',entry.get('path')))
            if not p.is_absolute():p=SX.parents[1]/p
            assert lqb.sha256(bind(p,inputs))==entry['sha256'],field
        extract=list(lqb.rows(SX/'sf6_release_extract_lqb.jsonl'))
        missing=list(lqb.rows(SX/'not_in_selection.jsonl'))
        old=list(lqb.rows(SX/'truth_v1_input.jsonl'))
        old_ids={r['line_id'] for r in old};ids={r['line_id'] for r in extract}
        missing_ids={r['line_id'] for r in missing}
        assert len(ids)==len(extract)==receipt['counts']['in_selection']
        assert not ids & missing_ids and ids|missing_ids==old_ids
        assert receipt['validation']['passed'] and receipt['extract']['transfer_sha_verified']
        prod=Path(registry['versions']['sf6_release']['receipt_local'])
        assert lqb.sha256(bind(prod,inputs))==receipt['remote']['receipt_sha256']
        release=[];held=[]
        for r in extract:
            mode=r['modes']['FULL']
            if mode['status']=='HOLD':
                assert mode['label'] is None and mode['hold_reasons'];held.append(r['line_id']);continue
            assert mode['status'] in ('released-corrected','released-unchanged') and isinstance(mode['label'],str)
            release.append(dict(line_id=r['line_id'],label=mode['label']))
        assert len(release)==receipt['counts']['modes']['FULL']['released']
        (OUT/'sf6_release_labels.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in release))
        p=OUT/'sf6_release_labels.jsonl'
        registry['versions']['sf6_release'].update(path=str(p),sha256=lqb.sha256(p),status='local',parent=None,
            population=dict(rows=len(release),definition='SX1 FULL released labels on extracted truth IDs; HOLD and absent IDs uncovered'),
            text_field='label',id_field='line_id',local_label_copy=str(p),sx1_receipt=str(SX/'RECEIPT.json'),
            sx1_receipt_sha256=lqb.sha256(SX/'RECEIPT.json'),read='Exact SX1 FULL released label only; no HOLD fallback')
        supplemental.append(dict(path=str(SX/'sf6_release_extract_lqb.jsonl'),sha256=receipt['extract']['sha256'],id_field='line_id',text_field='google_text'))
        current=list(lqb.rows(OUT/'truth_v1.jsonl'))
        assert {r['truth_id'] for r in old}<={r['truth_id'] for r in current}
        # The 24 later i-a scopes did not exist when SX1 was extracted.
        sx_info=dict(released=len(release),held=len(held),extract_lines=len(extract),
            old_truth_sha256=receipt['truth_input']['sha256'],later_truth_items=len(current)-len(old),
            later_truth_lines=len({r['line_id'] for r in current}-old_ids),
            note='SX1 binds the earlier frozen truth revision; later i-a scopes remain uncovered by sf6.')
        sx_status='scored'
    registry['versions']['google_raw']['supplemental_sources']=supplemental
    cards=read(bind(ROOT/'artifacts/n1/owner_sheet/cards.json',inputs))
    bind(ROOT/'artifacts/n1/n1t3/combined_decisions.json',inputs)
    bind(ROOT/'artifacts/n1/n1t2/slots.jsonl',inputs)
    bind(ROOT/'greekocr/numerics/owner_v2.py',inputs)
    from greekocr.numerics.combine_v2 import GLYPHS
    decisions={r['slot_id']:r for r in read(ROOT/'artifacts/n1/n1t3/combined_decisions.json')['decisions']}
    slots=defaultdict(list)
    for slot in lqb.rows(ROOT/'artifacts/n1/n1t2/slots.jsonl'):slots[slot['line_id']].append(slot)
    proposals=[];seen=set()
    for card in cards:
        assert card['line_id'] not in seen;seen.add(card['line_id'])
        lines={r['name']:r['text'] for r in card['rows']}
        assert 'Google' in lines and 'Ours' in lines
        edits={}
        for slot in slots[card['line_id']]:
            d=decisions[slot['slot_id']];a,b=slot['start'],slot['end']
            assert lines['Google'][a:b]==slot['glyph']
            glyph=GLYPHS.get(d.get('truth_candidate'),slot['glyph'])
            if glyph!=slot['glyph']:edits[a,b]=glyph
        rebuilt=lines['Google']
        for (a,b),glyph in sorted(edits.items(),reverse=True):rebuilt=rebuilt[:a]+glyph+rebuilt[b:]
        assert rebuilt==lines['Ours'],card['line_id']
        proposals.append(dict(line_id=card['line_id'],label=lines['Ours']))
    p=OUT/'n1_proposal_v1.jsonl';p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in proposals))
    registry['versions']['n1_proposal_v1']=dict(path=str(p),sha256=lqb.sha256(p),status='local',adoption='UNADOPTED',
        parent='google_raw',overlay=True,text_field='label',id_field='line_id',
        population=dict(overlay_rows=len(proposals),definition='Google stream with exact Ours lines from N1 owner sheet; other lines retain Google'),
        read='UNADOPTED Ours proposal; unsure gaps retain Google; N1 truth including approved controls is in-sample',
        source_cards_sha256=lqb.sha256(ROOT/'artifacts/n1/owner_sheet/cards.json'))
    lqb.dump(OUT/'versions.json',registry)
    return registry,sx_status,sx_info


def masked_baseline(google,inputs):
    """Account for every masked-card source named by INPUTS, without promoting gates."""
    b=lqb.PROJECTS/'greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked'
    result=[];features={r['id']:r for r in lqb.rows(lqb.PROJECTS/'collect-v3-data/run/W1/features.jsonl')}
    bind(b/'checks/T6B_CHECKS.md',inputs);bind(b/'checks/t6b_results.json',inputs)
    for name in ['gazette_modern','kosmopolis','lekythos','gazette_probe_supplement']:
        keypath=b/('cards_probe_supplement_key.json' if name=='gazette_probe_supplement' else f'cards/{name}_key.json')
        key=read(bind(keypath,inputs));rs=[]
        for p in sorted((b/'checks/verdicts').glob(name+'__*.jsonl')):rs.extend(lqb.rows(bind(p,inputs)))
        cardpath=b/('cards_probe_supplement/cards.jsonl' if name=='gazette_probe_supplement' else f'cards/{name}/cards.jsonl')
        cards={r['card_id']:r for r in lqb.rows(bind(cardpath,inputs))}
        groups=defaultdict(list)
        for r in rs:
            lid=key[r['card_id']]['line_id'];f=features[lid];literal=cards[r['card_id']]['google_text']
            if literal!=google[lid]:
                from difflib import SequenceMatcher
                assert r['letters']=='y' and all(tag in ('equal','delete') for tag,*_ in SequenceMatcher(None,google[lid],literal,autojunk=False).get_opcodes())
                r['letters']='n';r['raw_adjustment']='Certified shorter label; raw Google extra text.'
                # Mark correctness for duplicated accented text is unbound.
                if r['marks']!='na':r['marks']='u'
            # Conditional sub-strata of a uniform source draw are kept apart.
            era=('probe_1982_1985' if f.get('year') and int(f['year'])<=1985 else 'measured_1986_1990') if f['source']=='gazette_modern' else ''
            groups[(f['source'],f['primary_class'],era)].append(r)
        for (source,cls,era),vals in sorted(groups.items()):
            label=('modern monotonic Greek' if cls in ('modern_scanned','greek_mono') else 'Latin' if cls=='latin' else 'numeric separators' if cls=='numerics_tables' else 'mixed-script lookalikes' if cls=='mixed_greek_latin' else 'polytonic marks')
            stratum='/'.join(x for x in (source,cls,era,'masked '+name) if x)
            for field in ['letters','marks','crop_ok']:
                known=[r[field] for r in vals if r[field] in ('y','n')]
                result.append(measurement(label,stratum,'T6b/'+name,field+' (masked card verdict)',known.count('n'),len(known),
                    need='Applicable certified marks verdicts.',na=sum(r[field]=='na' for r in vals),unknown=sum(r[field] not in ('y','n','na') for r in vals)))
    # These later uniform sources are not absent. Their final-Sol gate verdicts
    # do not supply the benchmark's A/B/C truth tier; marks explicitly await Opus.
    for name,label,stratum in [('caps1','capitals','headings_caps / first masked draw'),('caps3','capitals','headings_caps / remasked fresh draw'),('kosmo2','polytonic marks','kosmopolis / poly1850 / masked'),('ruc1','Cyrillic','ia_russian / cyrillic / RU1-labelled masked')]:
        d=read(bind(b/name/'results.json',inputs));bind(b/name/'build_receipt.json',inputs)
        for field in ['letters','marks','crop_ok']:
            need=('Opus mark adjudication is pending in this source.' if field=='marks' else
                  'Bind class-specific raw Google pixel truth with a benchmark A/B/C reader tier; source records final Sol gate verdicts, which are not silently promoted.')
            if name=='ruc1' and field=='letters':need='Raw Google re-score against printed letters; this uniform audit checks RU1 labels, not raw Google.'
            result.append(measurement(label,stratum,'masked/'+name,field+' source inventory',typ='uniform',tier='unassigned (final Sol gate)' if field!='marks' else 'pending Opus',need=need,source_diagnostic=d.get('bed',d.get('totals'))))
    return result


def baseline(truth,google,inputs):
    result=[]
    # No C1 y/n verdict certifies all four heads or their direction. Never turn
    # an aggregate mark pass/fail into an invented per-head opportunity census.
    for head in ['breathing','accent (including grave↔acute)','diaeresis','subscript']:
        for direction in ['missing','extra','wrong mark']:
            result.append(measurement('polytonic marks', 'no head-resolved uniform/locked truth', 'C1 + locked strata',head+' / '+direction,
                need='Uniform or eligible locked print truth with every '+head+' head certified, absent heads included, and Google-aligned direction. C1 supplies aggregate verdicts only.'))
    c1=COLLECT/'c1';bind(c1/'C1_REPORT.md',inputs);bind(c1/'LABEL_CHECK_v2.md',inputs);bind(c1/'c1_results.json',inputs)
    groups=defaultdict(list)
    for p in sorted((c1/'verdicts').glob('*.jsonl')):
        bind(p,inputs);groups[p.stem.rsplit('__',1)[0]].extend(lqb.rows(p))
    for stratum,rs in sorted(groups.items()):
        assert len(rs)==100 and len({r['card_id'] for r in rs})==100
        key=bind(lqb.PROJECTS/'collect-v3-data/run/W1/c1'/f'{stratum}_key.json',inputs)
        keys=read(key)
        # The checker's google_text was the literal_label on the uniform card.
        for r in rs:
            lid=keys[r['card_id']]['line_id']
            assert lid in google,lid
            literal=keys[r['card_id']]['literal_label']
            if google[lid]!=literal:
                # Two C1 labels removed a duplicated unmarked word before
                # checking. A y verdict certifies the shorter letter stream;
                # the extra raw letters are an error. No mark truth is inferred.
                from difflib import SequenceMatcher
                changes=[(tag,google[lid][a:b],literal[c:d]) for tag,a,b,c,d in SequenceMatcher(None,google[lid],literal,autojunk=False).get_opcodes() if tag!='equal']
                assert r['letters']=='y' and all(tag=='delete' and not any(__import__('unicodedata').combining(x) for x in __import__('unicodedata').normalize('NFD',text)) for tag,text,_ in changes),(lid,changes)
                r['letters']='n';r['errors']=list(set(r['errors'])|{'extra_text'})
                r['raw_adjustment']='C1 certified shorter label; raw Google contains extra unmarked text: '+repr(changes)
        cls=('mixed-script lookalikes' if 'mixed_greek_latin' in stratum else
             'modern monotonic Greek' if 'modern_scanned' in stratum else
             'Latin' if '__latin' in stratum else 'Cyrillic' if '__cyrillic' in stratum else
             'numeric separators' if 'numerics_tables' in stratum else 'polytonic marks')
        source='C1/'+stratum
        for field,metric in [('letters','letters / digits / words (strict card verdict)'),('marks','marks (any head; card verdict)'),('crop_ok','crop (physical card verdict)')]:
            vals=[r[field] for r in rs if r[field] in ('y','n')]
            result.append(measurement(cls,stratum,source,metric,vals.count('n'),len(vals),
                need='Diacritic-bearing uniform cards with marks verdicts.' if not vals else None,
                raw_adjustments=[dict(card_id=r['card_id'],reason=r['raw_adjustment']) for r in rs if r.get('raw_adjustment')],
                unknown=sum(r[field] not in ('y','n','na') for r in rs),na=sum(r[field]=='na' for r in rs)))
        # These rates are tag incidence per uniform card, never glyph rates.
        for tag in ['missing_mark','extra_mark','wrong_mark']:
            if cls=='polytonic marks':
                result.append(measurement(cls,stratum,source,tag+' (any head; tagged cards)',sum(tag in r['errors'] for r in rs),len(rs)))
        for label,tags in [('punctuation and dashes',('punctuation','hyphen')),('mixed-script lookalikes',('lookalike_script_letter',))]:
            result.append(measurement(label,stratum,source,'cards tagged '+ ' / '.join(tags),sum(bool(set(tags)&set(r['errors'])) for r in rs),len(rs)))
        if cls=='numeric separators':
            agg=read(c1/'c1_results.json')[stratum]
            result.append(measurement(cls,stratum,source,'separator-error cards (C1 adjudicated list)',len({r['card_id'] for r in agg['separator']}),len(rs)))
    for cls,need in [('capitals','Uniform or eligible locked capital-slot print truth, including correct controls.'),
                     ('superscripts and rare glyphs','Uniform or eligible locked certified superscript/rare-glyph opportunities; C1 occurrence lists do not certify correctness.')]:
        result.append(measurement(cls,'no eligible class-specific truth','truth_v1 + INPUTS.md',cls,need=need))
    # Keep the selected i-a word scopes visible but do not promote them to a
    # population estimate merely because their source cohort is locked.
    locked=[r for r in truth if r['sample_type']=='locked_stratum']
    for source in sorted({r['provenance']['set'] for r in locked}):
        rs=[r for r in locked if r['provenance']['set']==source]
        result.append(measurement('polytonic marks','wikisource i-a (selected word scopes)',source,'letters; selected locked scopes',typ='locked_stratum',
            need='Uniform full-line pixel adjudication and complete Google coverage; existing 24 word scopes are disagreement-enriched, population_eligible=false.',
            diagnostic=lqb.summarize(rs,google,'google_raw')['letters|A+B']))
    for cls in ['ru1_yer','ru2_yat']:
        buckets=defaultdict(list)
        for r in truth:
            if r['class']==cls and r['sample_type'] in lqb.POPULATION_TYPES and r.get('population_eligible',True):buckets[(r['provenance']['set'],r['sample_type'],r['tier'])].append(r)
        for (source,typ,tier),rs in buckets.items():
            values=[lqb.error(r,google[r['line_id']]) for r in rs if r['line_id'] in google]
            values=[v for v in values if v is not None]
            result.append(measurement('Cyrillic','ia_russian / cyrillic; resolved yer positions',source,cls+' slots',sum(v[0] for v in values),sum(v[1] for v in values),typ,tier,uncovered=len(rs)-len(values)))
    registry=COLLECT/'release_exclusions/release_exclusions.json';bind(registry,inputs)
    for name in ['locked_eval','locked_eval_ia_wikisource','eval_only_dev','locked_eval_ib_wikisource','n1_locked_eval']:
        result.append(measurement('locked source inventory',name,str(registry),'locked source coverage',typ='locked_stratum',tier='unassigned',
            need={'locked_eval_ia_wikisource':'Full-line pixel truth; only 24 selected i-a letter scopes certified.',
                  'locked_eval_ib_wikisource':'Two-reader pixel truth; reference transcription, not pixel truth.',
                  'n1_locked_eval':'Uniform/locked certified separator slots; approved N1 truth is enriched.'}.get(name,'Class-resolved pixel truth with reader tier and exact Google bindings; ID list is not truth.')))
    result.extend(masked_baseline(google,inputs))
    order=['polytonic marks','capitals','numeric separators','punctuation and dashes','superscripts and rare glyphs','mixed-script lookalikes','Latin','modern monotonic Greek','Cyrillic','locked source inventory']
    return sorted(result,key=lambda r:order.index(r['class_name']))


def rate_text(r):
    if not r['n']:return 'not measured — '+r['truth_needed']
    lo,hi=r['ci95'];suffix="".join(f"; {key} {r[key]}" for key in ["unknown","na","uncovered"] if r.get(key))
    return f"{r['errors']}/{r['n']}; {100*r['rate']:.2f}%; 95% Wilson CI {100*lo:.2f}–{100*hi:.2f}%"+suffix

def summary_html(score):
    data=read(OUT/'baseline_v2.json');h=read(OUT/'headline_v2.json')
    esc=lambda x:html.escape(str(x))
    parts=['<section class="lqb-intro"><h2>BASELINE — Google against truth</h2>',
        '<p>Uniform and locked sources only. Every rate stays within its named stratum. Card verdicts, tagged-card incidence and glyph slots have different denominators. No pooled population rate.</p>',
        '<div style="overflow-x:auto"><table id="baseline"><thead><tr><th>Class / scope</th><th>Stratum</th><th>Google errors/n; rate; 95% Wilson CI</th><th>sample_type</th><th>Tier</th><th>Source set</th></tr></thead><tbody>']
    for r in data:
        parts.append('<tr>'+''.join('<td>'+esc(x)+'</td>' for x in [r['class_name']+' / '+r['metric'],r['stratum'],rate_text(r),r['sample_type'],r['tier'],r['source_set']])+'</tr>')
    parts+=['</tbody></table></div>', '<p>C1: tier A under the LQB3 owner ruling (two Opus readers per stratum, 50 cards each; one read per card). KEY-IN-REACH, not opened per transcripts. Card-level rates include crop failures; they are not conditional on crop_ok. Two raw Google duplicate-word errors are restored against C1-certified shorter labels (Latin c056; Serbia c005); C1 letter counts therefore increase by one error in each stratum. C1 missing/extra/wrong tags do not establish a complete head-resolved truth census. Superscript, dash and separator occurrence lists are not all error lists.</p>',
        '<h2>Marks delta — google_raw → sf6_release</h2><p id="headline">'+esc(h['line'])+'</p>',
        '<p>'+esc(h['bottom_line'])+'</p>',
        '<h2>Version scores — selected samples and diagnostics</h2><p>N1 proposal is UNADOPTED. Approved controls and lead rulings are in-sample for n1_proposal_v1; they do not enter its headline. sf6 HOLD labels are uncovered. Only covered out-of-sample items enter deltas. Cyrillic decision audits remain below.</p><div style="overflow-x:auto"><table><thead><tr><th>class</th><th>version</th><th>sample_type</th><th>out-of-sample</th><th>in-sample errors/n</th><th>uncovered items</th></tr></thead><tbody>']
    for cls in lqb.GROUPS:
        for name,version in score['versions'].items():
            row=version[cls+'|A+B']
            for typ,r in row['by_sample_type'].items():
                if not r['truth_items']:continue
                inside=r['in_sample']
                parts.append('<tr>'+''.join('<td>'+esc(x)+'</td>' for x in [cls,name+(' (UNADOPTED)' if name=='n1_proposal_v1' else ''),typ,lqb.measurement_text(r),f"{inside['errors']}/{inside['opportunities']}",r['uncovered']])+'</tr>')
    parts.append('</tbody></table></div><p>Not measured fields require the truth named above. See SCORE_v2.md and LQB3_RECEIPT.json for sources and coverage. Witness cards below retain frozen adjudicated slots.</p></section>')
    return ''.join(parts)


def main():
    inputs={}
    (OUT/'validation/lqb3').mkdir(parents=True,exist_ok=True)
    for p in [Path(__file__), ROOT/'scripts/lqb/build_scoreboard.py',ROOT/'greekocr/labelfix/lqb.py']:bind(p,inputs)
    registry,status,sx=prepare_versions(inputs)
    truth,flags=lqb.load_truth(OUT/'truth_v1.jsonl')
    for p in ['truth_v1.jsonl','truth_v1_flags.jsonl','truth_v1.manifest.json','INPUTS.md'] :bind(OUT/p,inputs)
    names=list(registry['versions']);wanted={r['line_id'] for r in truth};cache={}
    predictions={n:lqb.load_version(n,registry,wanted,cache) for n in names}
    if '--reuse-score' in sys.argv:
        previous=read(OUT/'LQB3_RECEIPT.json')
        assert previous['outputs']['versions.json']==lqb.sha256(OUT/'versions.json')
        assert previous['outputs']['score_v2.json']==lqb.sha256(OUT/'score_v2.json')
        assert previous['inputs'][str(OUT/'truth_v1.jsonl')]==lqb.sha256(OUT/'truth_v1.jsonl')
        assert previous['inputs'][str(OUT/'truth_v1_flags.jsonl')]==lqb.sha256(OUT/'truth_v1_flags.jsonl')
        score=read(OUT/'score_v2.json')
    else:score=lqb.run(OUT/'truth_v1.jsonl',registry,names)
    score['paired']['google_raw→sf6_release']=lqb.paired(truth,predictions['google_raw'],predictions['sf6_release'],'google_raw','sf6_release')
    lqb.dump(OUT/'score_v2.json',score)
    base=baseline(truth,lqb.load_version('google_raw',registry),inputs);lqb.dump(OUT/'baseline_v2.json',base)
    parts=[];breakdown={}
    for source in sorted({r['provenance']['set'] for r in truth if r['class']=='marks'}):
        rs=[r for r in truth if r['class']=='marks' and r['provenance']['set']==source]
        for typ in sorted({r['sample_type'] for r in rs}):
            v=lqb.paired([r for r in rs if r['sample_type']==typ],predictions['google_raw'],predictions['sf6_release'],'google_raw','sf6_release')['marks|A+B']
            breakdown[source+'/'+typ]=v
            if v['items']:parts.append(f"{source} ({typ}): {v['a_errors']} → {v['b_errors']} errors / {v['items']} known mark-head opportunities; delta {v['b_errors']-v['a_errors']:+d}")
    line='; '.join(parts) if status=='scored' else 'sf6 pending — SX1 extract has not landed.'
    if status=='scored' and not parts:line='sf6 scored; no covered out-of-sample mark truth.'
    measured=sum(r['status']=='measured' for r in base)
    n1=score['versions']['n1_proposal_v1']['n1_separator|A+B']
    bottom=f"The baseline measures {measured} separate stratum/scopes; {len(base)-measured} scopes remain not measured. {line}. N1 is an unadopted proposal: {n1['in_sample']['errors']}/{n1['in_sample']['opportunities']} in-sample separator errors; {n1['uncovered']} truth items uncovered. These selected-sample changes do not establish a population improvement."
    lqb.dump(OUT/'headline_v2.json',dict(line=line,bottom_line=bottom,by_source=breakdown))
    # Retain the existing approved renderer and native witness-card pipeline.
    sys.path.insert(0,str(lqb.PROJECTS/'greek-ocr-toolkit-cleanup'))
    import greekocr
    greekocr.__path__.append(str(lqb.PROJECTS/'greek-ocr-toolkit-cleanup/greekocr'))
    import importlib.util
    spec=importlib.util.spec_from_file_location('_lqb_board',ROOT/'scripts/lqb/build_scoreboard.py');board=importlib.util.module_from_spec(spec);spec.loader.exec_module(board)
    board.summary_html=summary_html
    board.main(score_path=OUT/'score_v2.json')
    md=['# Label Quality Scoreboard v2','', '## BASELINE — Google against truth','',
        'Strata are never pooled. C1 is tier A under the LQB3 owner ruling: two Opus readers per stratum, 50 cards each; one read per card. KEY-IN-REACH, not opened per transcripts. Rates are per card verdict/tag unless explicitly marked as slots. Unknown and na verdicts are excluded from the applicable denominator.','',
        '| Class / scope | Stratum | Google errors/n, rate, 95% Wilson CI | sample_type | Tier | Source |','|---|---|---|---|---|---|']
    for r in base:md.append('| '+' | '.join(str(x).replace('|','/') for x in [r['class_name']+' / '+r['metric'],r['stratum'],rate_text(r),r['sample_type'],r['tier'],r['source_set']])+' |')
    md+=['','## Marks delta', '',line,'',bottom,'',
        'Only FULL released SX1 labels are scored. HOLD null labels are uncovered; no composed-text or guessed source fallback. SX1 Google text is bound as a supplementary google_raw source. The additional R0 Google stream covers certified i-a scopes only; its human reference is not adopted as print truth. SX1 used the earlier truth SHA; all its truth IDs are verified as a subset of current truth. The later 24 i-a scopes remain outside the extract.','',
        'The 12 head/direction rows need complete certified head truth; C1 aggregate verdicts and error tags cannot supply missing head opportunities. C1 aggregate mark, letter and crop verdicts are all retained, including mixed-script and greek_poly strata. Tagged-card rates count each card once. C1 literal labels differ from raw Google on Latin c056 and Serbia c005: both certify letters=y on a shorter label, so the raw duplicate unmarked text is restored as a letter error (+1 in each stratum); physical crop and marks verdicts stay as read. Raw adjustments are recorded in baseline_v2.json. T6b masked draws are split by source, script class and Gazette era; their separate probe supplement is never pooled. Gazette masked c056 similarly restores a raw duplicate-text letter error; its mark verdict is unavailable on raw text. Later CAPS1/CAPS3/KOSMO2/RUC1 source diagnostics are bound but not promoted from final-Sol gates or pending Opus marks to benchmark truth. The C1 separator list identifies error cards; superscript/lunate/dash occurrence lists are not promoted to error truth. i-a selected word scopes are diagnostic only; i-b reference transcription, not pixel truth. All locked-source inventory gaps are explicit above.','',
        '## Version scores','', '[Machine-readable scores](score_v2.json) retain A/B/C tiers, sample-type splits, in-sample counts, regression-only counts and uncovered truth. [Headline by source](headline_v2.json) records paired document-bootstrap intervals (4,000 replicates, seed 20261017); selected-sample intervals are descriptive. Owner39 and sf6 construction truth stay excluded by used_by. [Historical v1](SCORE_v1.md) retains original method and source citations; v2 supersedes its pending sf6 and rejected C1 status.','',
        f"N1 proposal is **UNADOPTED**. Exact Ours lines override google_raw; other lines retain Google. All N1 approved-control/lead truth retains n1_* contamination: in-sample {n1['in_sample']['errors']}/{n1['in_sample']['opportunities']}; out-of-sample {n1['headline']['errors']}/{n1['headline']['opportunities']}. No truth is rewritten and no proposal is adopted.",'',
        '## Reproduction and receipt','',
        '```sh','PYTHONDONTWRITEBYTECODE=1 ../greek-ocr-toolkit-sol-collect/.venv/bin/python -B scripts/lqb/build_v2.py',
        'PYTHONDONTWRITEBYTECODE=1 ../greek-ocr-toolkit-sol-collect/.venv/bin/python -B -m pytest tests/test_lqb.py tests/test_lqb3.py -q -p no:cacheprovider --basetemp=docs/labelfix/lqb/validation/lqb3/pytest_tmp',
        'PYTHONDONTWRITEBYTECODE=1 ../greek-ocr-toolkit-sol-collect/.venv/bin/python -B scripts/lqb/validate_scoreboard.py --browser','```','',
        'Network OFF; no new readers, inference, .git writes, peer writes or publication. Frozen truth and flags stay unchanged. [LQB3 receipt](LQB3_RECEIPT.json) binds all source and output hashes. [Test log](tests_lqb3.txt) and [layout checks](validation/checks.json) record validation separately.']
    (OUT/'SCORE_v2.md').write_text('\n'.join(md)+'\n')
    receipt=dict(schema='lqb3-v2',network=False,git_writes=False,peer_writes=False,new_readers=0,inputs=inputs,sf6=status,sx1=sx,
        baseline_rows=len(base),measured=measured,not_measured=len(base)-measured,versions=len(names),headline=line,
        outputs={p:lqb.sha256(OUT/p) for p in ['versions.json','score_v2.json','baseline_v2.json','headline_v2.json','scoreboard.html','SCORE_v2.md','sf6_release_labels.jsonl','n1_proposal_v1.jsonl'] if (OUT/p).exists()})
    lqb.dump(OUT/'LQB3_RECEIPT.json',receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('inputs','outputs')},ensure_ascii=False))

if __name__=='__main__':main()
