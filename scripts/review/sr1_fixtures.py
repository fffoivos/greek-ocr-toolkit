"""Derive SR1 fixture/spec data from local read-only custodians, without running builders."""
from __future__ import annotations
import ast
import base64
from copy import deepcopy
import gzip
import json
from pathlib import Path
import shutil
import unicodedata as ud
from greekocr.adjudicate._files import dump, sha

ROOT = Path(__file__).resolve().parents[2]
PROJECTS = ROOT.parent
SC = PROJECTS/'greek-ocr-toolkit-spellcheck/docs/labelfix/spellcheck/R2_evidence'
S8 = PROJECTS/'greek-ocr-toolkit-spellcheck-s8/docs/labelfix/spellcheck/S8_DEV'
R2 = PROJECTS/'greek-ocr-toolkit-spellcheck-r2prep/docs/labelfix/spellcheck/R2'
OUT = ROOT/'artifacts/cleanup_sr1'


def main() -> None:
    out = OUT/'specs';out.mkdir(exist_ok=True)
    for name in ('reader_errors_heldout','accent_corrections_checked'):
        shutil.copyfile(ROOT/f'artifacts/cleanup_step4/specs/{name}.json',out/f'{name}.json')
    selected = json.loads(gzip.decompress((S8/'private/audit100/selected_overlays.json.gz').read_bytes()))['records']
    final = json.loads((S8/'audit100_private/audit100_final.json').read_text())
    records = [dict(line_id=r['line_id'], changes=[{k:c[k] for k in ('start','letter','from','to')} for c in r['changes']],
                    gate_decisions=[dict(start=g['start'],base=g['base'],evidence={k:g['evidence'].get(k,[]) for k in ('above','below')}) for g in r['gate_decisions']]) for r in selected]
    dump(OUT/'audit101.json',dict(records=records,verdicts={k:dict(ok=v['ok'],verdicts=[c[0] for c in v['cards']]) for k,v in final.items()}))
    # A line with multiple edits may have one word verdict covering both edits.
    data = json.loads((OUT/'audit101.json').read_text())
    for r in records:
        if len(data['verdicts'][r['line_id']]['verdicts'])!=len(r['changes']):
            data['verdicts'][r['line_id']].pop('verdicts')
    dump(OUT/'audit101.json',data)
    keys = [k for k in json.loads((S8/'private/audit100/items_key.json').read_text()) if not k.get('control')]
    def uri(path):
        return 'data:image/png;base64,'+base64.b64encode(path.read_bytes()).decode()
    cards=[]
    for lid,v in sorted(final.items(),key=lambda kv:kv[1]['ok']):
        items=[k for k in keys if k['line_id']==lid]
        card=dict(line_id=lid,group='good' if v['ok'] else 'bad',image=uri(S8/'audit100'/items[0]['line_img']),
                  rows=[],zooms=[],tags=[])
        for verdict,g,r,printed in v['cards']:
            it=next((i for i in items if ud.normalize('NFC',i['forms']['google'])==ud.normalize('NFC',g) and ud.normalize('NFC',i['forms']['released'])==ud.normalize('NFC',r)),None)
            if it:card['zooms'].append(dict(image=uri(S8/'audit100'/it['img']),alt='Word'))
            gn,rn=ud.normalize('NFC',g),ud.normalize('NFC',r)
            ours=dict(name='Ours',text=rn)
            if len(gn)==len(rn):
                ours=dict(name='Ours',segments=[dict(text=b,**(dict(kind='changed') if a!=b else {})) for a,b in zip(gn,rn)])
            card['rows'] += [dict(name='Google',text=gn),ours,dict(name='Printed',text=ud.normalize('NFC',printed or 'unreadable'))]
            cls,text={'released_right':('ok','matches the print'),'google_right':('bad','Google was right'),'unknown':('warn','unreadable')}[verdict]
            card['tags'].append({'class':cls,'text':text})
        cards.append(card)
    dump(out/'audit_words.json',dict(title='Accent Corrections Checked',intro='100 lines where we changed Google’s accents, read against the printed page. Ours is highlighted where it differs from Google.',
         groups=[dict(id='bad',heading='Wrong (17)'),dict(id='good',heading='Right (83)')],lines=cards))
    sample=json.loads((SC/'substitution_sample_60.json').read_text())
    mk={'acute':'\u0301','grave':'\u0300','circumflex':'\u0342','psili':'\u0313','dasia':'\u0314'}
    names={'acute':'acute','grave':'grave','circumflex':'circumflex','psili':'smooth breathing','dasia':'rough breathing'}
    lines=[]
    for tier in ('agree','other','noink'):
        for c in sample['sample'][tier]:
            path=PROJECTS/'greek-ocr-toolkit'/c['crop']
            slots=[dict(locator_span=s['body'],evidence={k:[dict(bbox=b) for b in s[k]] for k in ('above','below')}) for s in c['slots']]
            row=dict(line_id=c['line_id'],group=tier,image=str(path),clean_image=str(path),slots=slots,rows=[],tags=[])
            clusters=[]
            for ch in ud.normalize('NFD',c['label']):
                if ud.category(ch).startswith('M') and clusters:clusters[-1]+=ch
                else:clusters.append(ch)
            by={x['letter']:x for x in c['con']}
            google=[];ours=[];i=-1
            for cluster in clusters:
                if cluster[0].isalpha():i+=1
                con=by.get(i) if cluster[0].isalpha() else None
                new=cluster if not con else cluster[0]+''.join(mk[con['ours']] if m==mk[con['google']] else m for m in cluster[1:])
                style={} if not con else dict(kind='changed' if con['tier']=='agree' else 'no_ink')
                google.append(dict(text=ud.normalize('NFC',cluster),**style));ours.append(dict(text=ud.normalize('NFC',new),**style))
            row['rows']=[dict(name='Google',segments=google),dict(name='Ours',segments=ours)]
            for con in c['con']:
                det=' + '.join(names[m] for m in con['det'] if m in names) or 'no mark'
                cls,text={'agree':('ok','reader and detector agree'),'other':('warn','detector sees ink, names '+det),'noink':('bad','no ink found')}[con['tier']]
                row['tags'].append({'class':cls,'text':names[con['google']]+' → '+names[con['ours']]+' · '+text})
            lines.append(row)
    builder=ast.parse((SC/'page_builders/build_subst_page.py').read_text())
    intro=next(ast.literal_eval(n.value) for n in builder.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='intro' for t in n.targets))
    dump(out/'accent_substitutions.json',dict(title='Accent Substitutions',intro=intro,
         groups=[dict(id=t,heading=h+f" ({sample['sizes'][t]:,} lines)") for t,h in [('agree','Reader and detector agree'),('other','Detector sees ink, names another mark'),('noink','Detector sees no ink')]],lines=lines))
    overlay=OUT/'overlay';overlay.mkdir(exist_ok=True)
    for name in ('truth_overlay_v1.json','truth_overlay_v1_1.json'):
        shutil.copyfile(R2/name,overlay/name)
    evidence=overlay/'evidence/tranche6';evidence.mkdir(parents=True,exist_ok=True)
    for p in sorted((R2/'evidence/tranche6').iterdir()):
        if p.is_file():shutil.copyfile(p,evidence/p.name)
    mapping={'build_r1a_errors.py':'reader_errors_heldout.json','build_audit_template.py':'accent_corrections_checked.json','build_audit_page.py':'audit_words.json','build_subst_page.py':'accent_substitutions.json'}
    dump(OUT/'page_spec_index.json',{name:dict(spec='specs/'+target,source_sha256=sha(SC/'page_builders'/name)) for name,target in mapping.items()})
    dump(OUT/'source_receipt.json',dict(sources={str(p):sha(p) for p in [SC/'substitution_sample_60.json',S8/'private/audit100/selected_overlays.json.gz',S8/'audit100_private/audit100_final.json',S8/'private/audit100/items_key.json',R2/'truth_overlay_v1.json',R2/'truth_overlay_v1_1.json']},
          specs={p.name:sha(p) for p in sorted(out.glob('*.json'))}))


if __name__=='__main__':main()
