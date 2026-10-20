"""Read-only migration of historical input computations into data specs and content diffs.

No old builder is executed as a script. Only its input/formatting AST statements
are evaluated, with output writes and source-split asset extraction excluded.
Production rendering never reads a builder. This utility needs BeautifulSoup.
"""
from __future__ import annotations
import ast
import base64
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
from bs4 import BeautifulSoup, NavigableString
import numpy as np
from PIL import Image
from greekocr.adjudicate.owner_sheet import render
from greekocr.adjudicate.deck import build_deck

ROOT = Path(__file__).resolve().parents[2]
PROJECTS = ROOT.parent
SC = PROJECTS/'greek-ocr-toolkit-spellcheck'
BUILDERS = SC/'docs/labelfix/spellcheck/R2_evidence/page_builders'
OUT = ROOT/'artifacts/cleanup_step4'


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)+'\n')


def _execute(nodes, name):
    # fail closed if a future source revision adds any file write in retained AST
    for node in nodes:
        for call in ast.walk(node):
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == 'open':
                if len(call.args)>1 and isinstance(call.args[1], ast.Constant) and any(c in str(call.args[1].value) for c in 'wax+'):
                    raise ValueError('output call in migration AST')
    from greekocr.labelfix import validate
    # Input rebinding only; no frozen source bytes are modified.
    original_inputs = validate.TEST_JSONL, validate.TOOLKIT
    validate.TEST_JSONL = PROJECTS/'greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_test.jsonl'
    validate.TOOLKIT = PROJECTS/'greek-ocr-toolkit'
    namespace = {'__name__': 'cu4_input_derivation'}
    try:
        with redirect_stdout(io.StringIO()):
            exec(compile(ast.Module(body=nodes, type_ignores=[]), str(BUILDERS/name), 'exec'), namespace)
    finally:
        validate.TEST_JSONL, validate.TOOLKIT = original_inputs
    return namespace


def _record(fragment, lid, group):
    soup = BeautifulSoup(fragment, 'html.parser')
    card = soup.select_one('.card')
    image = card.find('img')
    note = card.select_one('.notes')
    record = dict(line_id=lid, group=group, label=card.select_one('.lid').get_text(),
                  data={k[5:]:v for k,v in card.attrs.items() if k.startswith('data-')},
                  image=image['src'], alt=image['alt'], rows=[], tags=[],
                  note_data={k[5:]:v for k,v in note.attrs.items() if k.startswith('data-')})
    if note.has_attr('data-slot'): record['slot'] = int(note['data-slot'])
    for row in card.select('table.w tr'):
        segments=[]
        for child in row.td.children:
            if isinstance(child, NavigableString): segments.append(dict(text=str(child)))
            elif child.name == 'mark': segments.append(dict(text=child.get_text(), kind='no_ink' if 'no' in child.get('class',[]) else 'changed'))
            elif child.name == 'span' and 'muted' in child.get('class',[]): segments.append(dict(text=child.get_text(), kind='muted'))
            else: raise ValueError('unexpected owner row element')
        record['rows'].append(dict(name=row.th.get_text(), segments=segments))
    for tag in card.select('.pill'):
        record['tags'].append(dict(text=tag.get_text(), **{'class':' '.join(c for c in tag.get('class',[]) if c!='pill')}))
    zooms = card.select('img.zoom')
    if zooms: record['zooms'] = [dict(image=i['src'],alt=i['alt']) for i in zooms]
    lens = card.select_one('.lens')
    if lens: record['clean_image'] = lens['style'].removeprefix('background-image:url(').removesuffix(')')
    printed = card.select_one('.printed')
    if printed: record['printed'] = printed['value']
    return record


def derive_owner_specs():
    source = (BUILDERS/'build_r1a_errors.py').read_text()
    tree = ast.parse(source)
    # Rebind only historical relative inputs to their actual read-only custodians.
    replacements = {
        'artifacts/labelfix_r1/score_3678928_K1c_vsS6/A_mapped_lines.jsonl.gz': str(PROJECTS/'greek-ocr-toolkit-spellcheck-r1/artifacts/labelfix_r1/score_3678928_K1c_vsS6/A_mapped_lines.jsonl.gz'),
        'docs/records/labelfix/spellcheck/print_truth_s0.json': str(ROOT/'docs/records/labelfix/spellcheck/print_truth_s0.json'),
    }
    class Inputs(ast.NodeTransformer):
        def visit_Constant(self,node):
            if isinstance(node.value,str) and node.value in replacements: return ast.copy_location(ast.Constant(replacements[node.value]),node)
            return node
    tree=Inputs().visit(tree)
    nodes=[]
    for n in tree.body:
        if n.lineno < 63 and not (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('S','src') for t in n.targets)):
            nodes.append(n)
        elif isinstance(n,ast.FunctionDef) and n.name=='card': nodes.append(n)
        elif isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('H','tot','intro') for t in n.targets):nodes.append(n)
    ns=_execute(nodes,'build_r1a_errors.py')
    groups=[dict(id=k, heading=f'{h} ({len(ns["cards"][k])})') for k,h in ns['H']]
    lines=[_record(ns['card'](c),c['lid'],k) for k,_ in ns['H'] for c in ns['cards'][k]]
    specs={'reader_errors_heldout':dict(title='Reader Errors Held-out',intro=ns['intro'],groups=groups,lines=lines)}
    tree=ast.parse((BUILDERS/'build_audit_template.py').read_text())
    nodes=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom)) or 32 <= n.lineno < 116]
    ns=_execute(nodes,'build_audit_template.py')
    lines=[]
    for key,ids in [('bad',ns['bad']),('good',ns['good'])]:
        for lid in ids:
            record=_record(ns['card'](lid),lid,key)
            # Qualify the shared renderer's overlay drawing from native inputs,
            # rather than handing it an already annotated historical raster.
            record['image']=ns['crop'][lid]
            record['slots']=ns['recs'][lid]['changes'][0]['evidence']['slots']
            record['opening_quotes']=ns['recs'][lid].get('opening_quotes') or []
            lines.append(record)
    specs['accent_corrections_checked']=dict(title='Accent Corrections Checked', intro=ns['intro'],
        groups=[dict(id='bad',heading=f'Wrong ({len(ns["bad"])})'),dict(id='good',heading=f'Right ({len(ns["good"])})')],lines=lines)
    for name,spec in specs.items(): dump(OUT/'specs'/f'{name}.json',spec)
    return specs


def _pixels(uri):
    with Image.open(io.BytesIO(base64.b64decode(uri.split(',',1)[1]))) as image:
        return np.array(image.convert('RGBA'))


def compare_owner(reference, emitted):
    old=BeautifulSoup(reference,'html.parser');new=BeautifulSoup(emitted,'html.parser')
    diffs=[]; rows=[]; element_changes=[]
    def check(where,a,b):
        if a!=b: diffs.append(dict(element=where,before=a,after=b))
    check('title',old.title.get_text(),new.title.get_text())
    check('headings',[h.get_text() for h in old.select('main h1,main h2')],[h.get_text() for h in new.select('main h1,main h2')])
    check('section/card sequence',[(el.name,el.select_one('.lid').get_text() if el.get('class') == ['card'] else el.get_text()) for el in old.select('main > h2, main > .card')],[(el.name,el.select_one('.lid').get_text() if el.get('class') == ['card'] else el.get_text()) for el in new.select('main > h2, main > .card')])
    check('intro',old.select_one('main .meta').get_text(),new.select_one('main .meta').get_text())
    oc=old.select('.card');nc=new.select('.card');check('card count',len(oc),len(nc))
    def data(el):return {k:v for k,v in el.attrs.items() if k.startswith('data-')}
    for i,(a,b) in enumerate(zip(oc,nc)):
        before=len(diffs)
        lid=a.select_one('.lid').get_text()
        check(f'{i}/line',lid,b.select_one('.lid').get_text())
        check(f'{i}/data',data(a),data(b))
        for selector in ('table.w tr','.pill'):
            def content(card):
                return [dict(text=el.get_text(),classes=el.get('class',[]),marks=[dict(text=m.get_text(),classes=m.get('class',[])) for m in el.select('mark')]) for el in card.select(selector)]
            check(f'{i}/{selector}',content(a),content(b))
        check(f'{i}/notes',data(a.select_one('.notes')),data(b.select_one('.notes')))
        ap=a.select_one('.printed');bp=b.select_one('.printed')
        check(f'{i}/printed',ap.get('value') if ap else None,bp.get('value') if bp else None)
        ai=a.select('img');bi=b.select('img');check(f'{i}/images/count',len(ai),len(bi))
        image_rows=[]
        for j,(x,y) in enumerate(zip(ai,bi)):
            xp,yp=_pixels(x['src']),_pixels(y['src']); equal=np.array_equal(xp,yp)
            check(f'{i}/image{j}/pixels',True,equal)
            check(f'{i}/image{j}/alt',x.get('alt'),y.get('alt'))
            image_rows.append(dict(index=j,shape=list(xp.shape),equal=equal,pixel_sha256=hashlib.sha256(xp.tobytes()).hexdigest()))
        al=a.select_one('.lens');bl=b.select_one('.lens')
        check(f'{i}/magnifier',al is not None,bl is not None)
        clean=None
        if al and bl:
            x=_pixels(al['style'].removeprefix('background-image:url(').removesuffix(')'))
            y=_pixels(bl['style'].removeprefix('background-image:url(').removesuffix(')'))
            clean=np.array_equal(x,y);check(f'{i}/clean pixels',True,clean)
        rows.append(dict(index=i,line=lid,content_diffs=len(diffs)-before,images=image_rows,clean_pixels_equal=clean))
    # Inventory the remaining DOM differences per element, separately from content.
    for index,(a,b) in enumerate(zip(oc,nc)):
        ae=[a]+list(a.find_all(True));be=[b]+list(b.find_all(True))
        if len(ae)!=len(be):
            element_changes.append(dict(card=index,element='structure',before=len(ae),after=len(be),reason='shared card markup'))
        for j,(x,y) in enumerate(zip(ae,be)):
            for attr in sorted(set(x.attrs)|set(y.attrs)):
                if x.get(attr)!=y.get(attr):
                    def compact(value):
                        return ('sha256:'+hashlib.sha256(value.encode()).hexdigest()) if isinstance(value,str) and len(value)>200 else value
                    element_changes.append(dict(card=index,line=a.select_one('.lid').get_text(),element=f'{j}:{x.name}',attribute=attr,
                        before=compact(x.get(attr)),after=compact(y.get(attr)),
                        reason='accessible label/textarea identity; note data/document ID unchanged' if attr in ('id','for') else 'see content diff and asset changes'))
    return dict(cards=len(oc),diffs=diffs,items=rows,non_content_element_changes=element_changes,
        non_content_changes=[
            'Complete doctype/head/body, UTF-8 and responsive viewport added; whitespace/attribute quoting may differ.',
            'Shared packaged CSS/JS replace builder-source extraction; external font CSS link removed for offline operation.',
            'Note label/textarea IDs added to the accent page; original data attributes and document IDs preserved.',
            'Shared note JS reads each document rather than a 1000-document collection query, protects edits during load, and retains merge/debounce/blur behavior.',
            'Printed edits also save printed_edited; absent Printed fields remain absent.',
            'Tap toggles lens consistently; original touch handler always showed it. Lens crop, dimensions and Z unchanged.',
            'Shared CSS adds muted text color and fixes zoom width specificity; light/dark tokens unchanged.'])


def derive_r0_spec():
    r0=PROJECTS/'greek-ocr-toolkit-spellcheck-r0/docs/labelfix/spellcheck'
    blind=r0/'R0_cards_ib';private=r0/'R0_adjudication_private/ib/items_key.json'
    original=json.loads((blind/'items_blind.json').read_text());keys=json.loads(private.read_text())
    key={r['id']:r for r in keys}
    records={False:[],True:[]}
    for i,card in enumerate(original):
        k=key[card['id']]
        records[bool(k['control'])].append(dict(id=card['id'],position=i,
            image=str(blind/card['line_img']),line_image=str(blind/card['line_img']),
            options={o:card[o] for o in ('A','B','C') if o in card},
            control=bool(k['control']),known_answer=(card[k['expected_choice']] if k['control'] else None),
            pixel_verified=bool(k.get('pixel_verified')), zoom_scale=k['zoom_scale'],crop_box=k['crop_box'],
            old_img=card['img'],old_line_img=card['line_img'],private=k))
    spec=dict(protocol='historical',preserve_order=True,schema='r0',items=records[False],controls=records[True],seed=20261017,
              source_blind_sha256=hashlib.sha256((blind/'items_blind.json').read_bytes()).hexdigest(),
              source_key_sha256=hashlib.sha256(private.read_bytes()).hexdigest())
    dump(OUT/'specs/R0_cards_ib.json',spec)
    return spec,original,blind


def reemit():
    for name,spec in derive_owner_specs().items():
        emitted=render(spec['lines'],spec)
        (OUT/f'{name}.html').write_text(emitted)
        reference=OUT/'reference'/f'{name}.html'
        diff=compare_owner(reference.read_text(),emitted)
        diff['reference_sha256']=hashlib.sha256(reference.read_bytes()).hexdigest()
        dump(OUT/f'{name}_diff.json',diff)
        print(name,diff['cards'],'cards',len(diff['diffs']),'content diffs')
    spec,original,source=derive_r0_spec()
    # Re-emission goes only to a temporary tree; retain receipt and full diff here.
    with tempfile.TemporaryDirectory(prefix='cu4-r0-') as temporary:
        spec['blind_dir']=str(Path(temporary)/'blind')
        receipt=build_deck(spec)
        emitted=json.loads((Path(receipt['blind_dir'])/'items_blind.json').read_text())
        diffs=[];items=[]
        if [c['id'] for c in original]!=[c['id'] for c in emitted]:diffs.append('item set/order')
        keys={k['id']:k for k in json.loads(Path(receipt['private_key']).read_text())}
        original_keys={k['id']:k for k in json.loads((source.parent/'R0_adjudication_private/ib/items_key.json').read_text())}
        for old,new in zip(original,emitted):
            changes=[]
            if {k:v for k,v in old.items() if k not in ('img','line_img')}!={k:v for k,v in new.items() if k not in ('img','line_img')}:changes.append('id/options/order')
            if keys[old['id']]['control']!=original_keys[old['id']]['control']:changes.append('control placement')
            images=[]
            for field in ('img','line_img'):
                with Image.open(source/old[field]) as a,Image.open(Path(receipt['blind_dir'])/new[field]) as b:
                    equal=np.array_equal(np.array(a),np.array(b))
                    if not equal:changes.append(field+' pixels')
                    images.append(dict(field=field,old=old[field],new=new[field],equal=equal,size=list(a.size)))
            items.append(dict(id=old['id'],control=keys[old['id']]['control'],diffs=changes,images=images))
            diffs.extend(dict(id=old['id'],cause=c) for c in changes)
        dump(OUT/'R0_cards_ib_diff.json',dict(items=items,diffs=diffs,receipt=receipt,
            protocol_changes=receipt['protocol_changes']+['Private key remains sibling-separated and write-once; no key relocation relative to R0-ib.',
            'Historical item/options/control positions replayed explicitly, not rerandomised. Targets re-cropped from native full-line rasters using the sealed crop boxes; frozen selection/locator geometry is not recomputed.',
            'Old localStorage viewer replaced by common viewer/instructions/schema and code-emitted reader-2 manifest. No reader results are rescored.',
            'New resolution defaults to literal-form control checks; historical R0 bare-letter control gating is not silently substituted.']))
        print('R0_cards_ib',len(items),'cards',len(diffs),'content diffs')

if __name__=='__main__':
    import socket
    from greekocr.recogniser.guard import forbid_forward
    def network_off(*args, **kwargs): raise RuntimeError('CU4 network OFF')
    socket.socket.connect = network_off
    socket.create_connection = network_off
    with forbid_forward(): reemit()
    inputs = [BUILDERS/n for n in ('build_r1a_errors.py', 'build_audit_template.py', 'snap6/build_owner.py')]
    inputs += [SC/'scripts/labelfix/r1_error_types.py',
               PROJECTS/'greek-ocr-toolkit-spellcheck-r1/artifacts/labelfix_r1/score_3678928_K1c_vsS6/A_mapped_lines.jsonl.gz',
               ROOT/'docs/records/labelfix/spellcheck/print_truth_s0.json',
               PROJECTS/'greek-ocr-toolkit-spellcheck-s8/docs/labelfix/spellcheck/S8_DEV/private/audit100/selected_overlays.json.gz',
               PROJECTS/'greek-ocr-toolkit-spellcheck-s8/docs/labelfix/spellcheck/S8_DEV/private/audit100/items_key.json',
               PROJECTS/'greek-ocr-toolkit-spellcheck-s8/docs/labelfix/spellcheck/S8_DEV/audit100_private/audit100_final.json',
               PROJECTS/'greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl',
               PROJECTS/'greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_test.jsonl']
    from greekocr.labelfix.validate import PRED_DIR
    inputs += [PRED_DIR/f'full_s0_{suffix}.jsonl' for suffix in ('v2_test','wikisource_human')]
    dump(OUT/'derivation_receipt.json',dict(network=False,forward_guard=True,
         inputs={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
         substitutions=['Main print_truth_s0.json absent; used tracked cleanup copy, byte-identical to spellcheck and R1 copies.'],
         print_truth_copies={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'docs/records/labelfix/spellcheck/print_truth_s0.json', SC/'docs/labelfix/spellcheck/print_truth_s0.json', PROJECTS/'greek-ocr-toolkit-spellcheck-r1/docs/labelfix/spellcheck/print_truth_s0.json']}))

