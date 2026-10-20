"""Owner sheet v2. Caller supplies complete, post-reading decisions per line."""
from .combine_v2 import GLYPHS, DASHES
GROUPS = ('Raised dot written as hyphen by Google','Dash type differs from Google',
          'Other disagreements','Needs a look','Agreement sample (12)')
INTRO = ('Printed marks include raised dots (·), full stops (.), commas (,), hyphens (-), en dashes (–), em dashes (—), spaces and empty gaps.\n'
         '“Ours” is our reading of every gap, prefilled in the editable field for you to correct.\n'
         'Dashes are only tagged in the training labels for now.\n'
         'boxes with a dashed outline are gaps we have not decided yet; their Google character is kept in Ours')
NAMES = {'-':'hyphen (-)','–':'en dash (–)','—':'em dash (—)','−':'minus (−)',
         '·':'raised dot (·)','·':'raised dot (·)','.':'full stop (.)',',':'comma (,)','':'nothing',' ':'space'}


def named(glyph):
    if glyph in NAMES: return NAMES[glyph]
    if glyph.isspace(): return 'space'
    return ' + '.join(NAMES.get(c,repr(c)) for c in glyph)


def card(line, slots, decisions):
    if len(slots)!=len(decisions) or {s['slot_id'] for s in slots}!={d['slot_id'] for d in decisions}:
        raise ValueError('line-complete decisions required')
    byid={d['slot_id']:d for d in decisions};text=line['text'];edits=[];gaps=[];zooms=[];boxes=[]
    flags=set();dash_types=set();uncertain=False
    for s in slots:
        d=byid[s['slot_id']];n=s['number'];a,b=s['start'],s['end'];g=s['glyph']
        if s['line_id']!=line['line_id'] or text[a:b]!=g: raise ValueError('line/offset mismatch')
        truth=d.get('truth_candidate');ours=GLYPHS.get(truth,g)
        if truth is None:
            uncertain=True
            flags.add(3)
        if truth in DASHES: dash_types.add(truth)
        if ours!=g:
            edits.append((a,b,ours))
            verified=d.get('status')=='lead_ruled' or (d.get('agreement') and d.get('reason')=='two_agreeing_valid_reads')
            flags.add(0 if g=='-' and truth=='raised dot' and verified else 1 if truth in DASHES else 2)
        gaps.append(f"{n}: {named(g)} → {named(ours)}; {'unsure:'+d['reason'] if truth is None else 'agreement' if d.get('agreement') else 'lead verified' if d.get('status')=='lead_ruled' else 'needs a look'}; {d.get('confidence','unresolved')} confidence" + ('; nothing (geometry)' if d.get('reason')=='nothing (geometry)' else '') + (f"; {s['geometry']['geom_status']}" if s['geometry']['geom_status']!='ok' else ''))
        geom=s['geometry']
        style='unsure' if truth is None else 'decided-changed' if ours!=g else 'decided-unchanged'
        if d.get('reason')=='nothing (geometry)' or s.get('read_reason')=='geometry-only':
            continue
        if geom['geom_status']=='ok':
            x0,x1=geom['gap'];top=geom['digit_top'];bottom=geom['baseline']
            # Original crop coordinates; renderer numbers these in enumeration order.
            boxes.append(dict(number=n,slot_id=s['slot_id'],style=style,locator_span=[x0,x1],evidence={'attached':[dict(bbox=[x0,top,max(x0+1,x1),bottom])]}))
        else: boxes.append(dict(number=n,slot_id=s['slot_id'],style=style,locator_span=None,evidence={}))
        if truth!='nothing' and s.get('zoom'):zooms.append(dict(image=s['zoom'],alt=f'gap {n}'))
    # Multiple token boundary slots can share offsets. Conflicting proposals fail closed.
    unique={}
    for a,b,v in edits:
        if (a,b) in unique and unique[a,b]!=v: raise ValueError('conflicting shared boundary')
        unique[a,b]=v
    ordered=sorted((a,b,v) for (a,b),v in unique.items())
    for x,y in zip(ordered,ordered[1:]):
        if x[1]>y[0]: raise ValueError('overlapping slot edits')
    ours=text
    for a,b,v in reversed(ordered):ours=ours[:a]+v+ours[b:]
    group=GROUPS[min(flags)] if flags else GROUPS[3] if uncertain else GROUPS[4]
    tags=[dict(text='changed' if ours!=text else 'unchanged')]+[dict(text=t) for t in sorted(dash_types)]+[dict(text='unsure:'+r) for r in sorted({byid[s['slot_id']]['reason'] for s in slots if byid[s['slot_id']].get('truth_candidate') is None})]+[dict(text=line['source_era'])]+([dict(text=line['source'])] if line.get('source') and line['source']!=line['source_era'] else [])
    return dict(line_id=line['line_id'],doc_id=line['line_id'],label=line['line_id'],
        image=line['crop'],slots=boxes,zooms=zooms,
        rows=[dict(name='Google',text=text),dict(name='Ours',text=ours),dict(name='Gaps',text='\n'.join(gaps))],
        printed=ours,data={'printed-source':'ours-proposal'},tags=tags,group=group)


def build(lines, slots, decisions):
    byline={l['line_id']:[] for l in lines};byid={d['slot_id']:d for d in decisions}
    if len(byid)!=len(decisions) or set(byid)!={s['slot_id'] for s in slots}: raise ValueError('complete unique decisions required')
    for s in slots: byline[s['line_id']].append(s)
    cards=[card(l,byline[l['line_id']],[byid[s['slot_id']] for s in byline[l['line_id']]]) for l in lines]
    # Complete lines are the review unit; agreement-only cards are a seeded sample.
    import hashlib
    agreements=[c for c in cards if c['group']==GROUPS[4]]
    ordered=sorted(agreements,key=lambda c:hashlib.sha256(('20261017:N1T:agreements:'+c['line_id']).encode()).hexdigest())
    keep={c['line_id'] for c in ordered[:12]}
    omitted=[c['line_id'] for c in agreements if c['line_id'] not in keep]
    cards=[c for c in cards if c['group']!=GROUPS[4] or c['line_id'] in keep]
    return cards,dict(title='N1 Numeric Separators',intro=INTRO,groups=[dict(id=g,heading=g) for g in GROUPS],
        agreement_sample_line_ids=sorted(keep),omitted_agreement_line_ids=omitted)
