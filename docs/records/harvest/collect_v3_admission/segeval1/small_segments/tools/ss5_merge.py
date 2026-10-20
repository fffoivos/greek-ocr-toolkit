"""SS5: mechanical answer merge, scoring and contact-sheet rendering; no crop judgments."""
import collections, difflib, hashlib, json, math, random, struct, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
SS = Path(__file__).resolve().parents[1]
Q = SS / 'q3'
FONT = Path('/System/Library/Fonts/Supplemental/Arial Unicode.ttf')
MAP = dict(word_or_phrase='word', heading_caps_display='caps_display', abbreviation_reference_label='abbrev_label', roman_numeral_lowercase='roman_lower', punctuation_only='punctuation', noise_non_text='noise', handwriting='handwriting', foreign_script_printed='foreign_script', map_figure_ornament_logo='figure_ornament', scan_watermark='watermark', show_through_mirrored='show_through', cut_fragment='cut_fragment', multi_line_crop='multi_line', text_covers_part_of_crop='part_of_line')
A_TYPES = set('noise handwriting figure_ornament watermark show_through cut_fragment multi_line part_of_line foreign_script other punctuation marker number'.split())
FIELDS = ('type','text','crop','rotated','detail')
def rows(p): return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def jsonl(p,x): p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in x))
def unique(rs, field='line_id'):
    out={}
    for r in rs:
        v=r.get(field)
        if not v or v in out: raise ValueError('missing or duplicated '+field+': '+str(v))
        out[v]=r
    return out

def merge(sample, key, mapped, opus, unavailable=()):
    samples=unique(sample); op=unique(opus); beds={}; controls=set()
    for ctx, spec in key['contexts'].items():
        for cid in spec['card_ids']:
            item=key['items'][cid]; lid=item['line_id']
            if item['control']: controls.add(lid); continue
            if lid in beds: raise ValueError('duplicated line_id in bed key: '+lid)
            beds[lid]=(ctx,cid)
    if set(samples)!=set(beds)|controls: raise ValueError('missing or extra line_id in sample/key coverage')
    answers={}
    for ctx,spec in key['contexts'].items():
        if ctx in unavailable: continue
        rr=mapped[ctx]; bycard=unique(rr,'card_id'); unique(rr)
        if set(bycard)!=set(spec['card_ids']): raise ValueError('missing or extra card/line_id: '+ctx)
        for cid in spec['card_ids']:
            r=bycard[cid]; item=key['items'][cid]
            if r.get('line_id')!=item['line_id'] or r.get('ctx')!=ctx or r.get('control')!=item['control']: raise ValueError('line_id/context/control mismatch')
            if not item['control']: answers[r['line_id']]=r
    if set(answers)!={lid for lid,(ctx,_) in beds.items() if ctx not in unavailable}: raise ValueError('missing or duplicated line_id in answers')
    out=[]
    for s in sample:
        lid=s['line_id']
        if lid not in beds: continue
        ctx,cid=beds[lid]; r=dict(s, sample_rotated=s.get('rotated'),ctx=ctx,card_id=cid)
        r.update({f:answers[lid][f] if lid in answers else None for f in FIELDS})
        if lid in op: r.update(opus_type=MAP.get(op[lid]['type'],op[lid]['type']),opus_note=op[lid].get('note'),opus_type_original=op[lid]['type'])
        out.append(r)
    return out

def score(rr, expectations):
    results=[]
    for r in rr:
        if not r['control']: continue
        e=expectations[r['line_id']]
        errors=[f for f in ('type','text','crop','rotated') if r[f] not in ([e['type']]+e.get('accept',[]) if f=='type' else [e[f]] if f=='rotated' else e[f])]
        results.append(dict(line_id=r['line_id'],card_id=r['card_id'],actual={f:r[f] for f in FIELDS},expected=e,errors=errors,ok=not errors))
    n=sum(not r['ok'] for r in results)
    return dict(count=len(results),error_count=n,flagged=n>1,results=results)

def groups(rs, seed=20261019):
    a=[r for r in rs if r['type'] in A_TYPES or r['text'] in ('unreadable','not_text')]; used={r['line_id'] for r in a}
    b=[r for r in rs if r['line_id'] not in used and r.get('opus_type') is not None and r['type'] is not None and r['opus_type']!=r['type']]; used.update(r['line_id'] for r in b)
    rest=sorted((r for r in rs if r['line_id'] not in used),key=lambda r:r['line_id'])
    # Round up to include at least 10 percent of the remaining rows.
    c=random.Random(seed).sample(rest,math.ceil(len(rest)*.1))
    return {'A':a,'B':b,'C':c}

def labels(r,index):
    lines=[f"{index}. {r['line_id']}",f"Google: {r.get('raw_text','')}",f"Sol: {r['type']} / {r['text']} / {r['crop']} / {r['rotated']}"]
    if 'opus_type' in r: lines.append('Opus: '+r['opus_type'])
    if r.get('detail'): lines.append('detail: '+r['detail'])
    return lines

def wrapped(text,font,width=900):
    out=[]
    for paragraph in text.split('\n'):
        line=''
        for char in paragraph:
            if line and font.getlength(line+char)>width: out.append(line);line=''
            line+=char
        out.append(line)
    return out

def font_cmap(path):
    """Read Unicode cmap directly; avoid dependencies or silent missing-glyph boxes."""
    data=path.read_bytes(); tables={}
    for i in range(struct.unpack_from('>H',data,4)[0]):
        tag,_,off,length=struct.unpack_from('>4sIII',data,12+i*16); tables[tag]=(off,length)
    off,_=tables[b'cmap']; covered=set()
    for i in range(struct.unpack_from('>H',data,off+2)[0]):
        platform,encoding,rel=struct.unpack_from('>HHI',data,off+4+8*i)
        if platform not in (0,3):continue
        start=off+rel; fmt=struct.unpack_from('>H',data,start)[0]
        if fmt==4:
            n=struct.unpack_from('>H',data,start+6)[0]//2
            ends=struct.unpack_from('>'+str(n)+'H',data,start+14)
            starts=struct.unpack_from('>'+str(n)+'H',data,start+16+2*n)
            deltas=struct.unpack_from('>'+str(n)+'h',data,start+16+4*n)
            for j,(lo,hi) in enumerate(zip(starts,ends)):
                ropos=start+16+6*n+2*j; ro=struct.unpack_from('>H',data,ropos)[0]
                for cp in range(lo,hi+1):
                    glyph=struct.unpack_from('>H',data,ropos+ro+2*(cp-lo))[0] if ro else cp
                    if (glyph+deltas[j])%65536 if glyph else 0: covered.add(cp)
        elif fmt==12:
            for j in range(struct.unpack_from('>I',data,start+12)[0]):
                lo,hi,glyph=struct.unpack_from('>III',data,start+16+12*j)
                covered.update(range(lo+(glyph==0),hi+1))
    return covered

def render(gs):
    font=ImageFont.truetype(str(FONT),18); cmap=font_cmap(FONT)
    assert all(ord(c) in cmap for c in 'Ελληνικά БУШ 中文'), 'font lacks required scripts'
    ordered=[(g,r) for g,rr in gs.items() for r in rr]; index=[]; geometry=[]; missing=set()
    dest=Q/'eye_sheets'; dest.mkdir(exist_ok=True)
    for start in range(0,len(ordered),8):
        name=f'eye_{start//8+1:03}.png'; cards=[]
        for local,(group,r) in enumerate(ordered[start:start+8],1):
            lines=[part for line in labels(r,local) for part in wrapped(line,font)]
            missing.update(c for l in lines for c in l if not c.isspace() and ord(c) not in cmap)
            card=Image.new('RGB',(940,228+26*len(lines)+18),'white'); d=ImageDraw.Draw(card)
            with Image.open(r['crop_path']) as source:
                scale=min(4,900/source.width,200/source.height); size=(max(1,math.floor(source.width*scale)),max(1,math.floor(source.height*scale)))
                crop=source.convert('RGB').resize(size,Image.Resampling.NEAREST)
            card.paste(crop,(21,11)); d.rectangle((20,10,21+size[0],11+size[1]),outline='red',width=1)
            for n,line in enumerate(lines):d.text((20,220+26*n),line,font=font,fill='black')
            cards.append(card); index.append(dict(sheet=name,index=local,line_id=r['line_id'],group=group))
            geometry.append(dict(sheet=name,index=local,line_id=r['line_id'],scale=scale,rendered_size=size,frame=[20,10,21+size[0],11+size[1]],label_lines=len(lines)))
        sheet=Image.new('RGB',(940,sum(c.height for c in cards)),'white'); y=0
        for card in cards:sheet.paste(card,(0,y));y+=card.height
        sheet.save(dest/name)
        with Image.open(dest/name) as check: check.verify()
    if missing: raise ValueError('font missing label characters: '+repr(sorted(missing)))
    jsonl(Q/'eye_index.jsonl',index);jsonl(Q/'eye_geometry.jsonl',geometry)
    return len(set(r['sheet'] for r in index))

def main():
    outputs=['typing.jsonl','AGREEMENT.md','AGREEMENT.json','eye_index.jsonl','eye_geometry.jsonl','PROMPT_DIFF.diff','SS5_tests.log','SS5_RECEIPT.json']
    if any((Q/p).exists() for p in outputs) or (Q/'eye_sheets').exists():raise ValueError('SS5 output already exists; refusing overwrite')
    inputs=[Q/p for p in ['sample.jsonl','key_opus.jsonl','keys/type2.json','LEAD_CONTROLS.json','LEAD_CONTROLS.v1.json','usage_ledger.jsonl']]
    key=read(Q/'keys/type2.json'); sample=rows(Q/'sample.jsonl'); opus=rows(Q/'key_opus.jsonl'); mapped={}; scans={}; unavailable=[]; checks={}
    for ctx in key['contexts']:
        scanpath=Q/f'answers/{ctx}.scan.json'; raw=Q/f'answers/{ctx}.jsonl'
        scan=read(scanpath) if scanpath.exists() else {}; clean=scan.get('ok') is True and scan.get('violations')==[]
        scans[ctx]={'clean':clean,'scanner_version':scan.get('scanner_version')}
        if ctx=='t04' and (not raw.exists() or not clean): unavailable.append(ctx);continue
        if not clean:raise ValueError('unclean scan: '+ctx)
        paths=[Q/f'answers/{ctx}{suffix}' for suffix in ('.jsonl','.mapped.jsonl','.check.json','.scan.json')];inputs.extend(paths)
        rr=rows(paths[1]); mapped[ctx]=rr;check=read(paths[2]); checks[ctx]=check
        if not check.get('valid'):raise ValueError('invalid check: '+ctx)
        # Cross-check raw answers against mapped answers and frozen key expectations.
        rawby=unique(rows(raw),'card_id'); mappedby=unique(rr,'card_id')
        if set(rawby)!=set(mappedby): raise ValueError('raw/mapped coverage mismatch: '+ctx)
        for cid,r in mappedby.items():
            if any(rawby[cid][f]!=r[f] for f in FIELDS):raise ValueError('raw/mapped answer mismatch')
    v1=read(Q/'LEAD_CONTROLS.v1.json'); amended=read(Q/'LEAD_CONTROLS.json')
    for item in key['items'].values():
        if item['control'] and item['expected']!=v1['controls'][item['line_id']]:raise ValueError('frozen key differs from v1')
    controls={ctx:dict(v1=score(rr,v1['controls']),amended=score(rr,amended['controls'])) for ctx,rr in mapped.items()}
    typed=merge(sample,key,mapped,opus,unavailable);jsonl(Q/'typing.jsonl',typed)
    compared=[r for r in typed if r.get('stratum')=='opus' and 'opus_type' in r and r['type'] is not None]
    disagreements=[dict(line_id=r['line_id'],opus=r['opus_type'],sol=r['type'],google_text=r['raw_text']) for r in compared if r['type']!=r['opus_type']]
    matrix=collections.defaultdict(collections.Counter)
    for r in compared:matrix[r['opus_type']][r['type']]+=1
    flagged=[ctx for ctx,v in controls.items() if v['amended']['flagged']]
    promptpaths=sorted((Q/'prompts_rendered').rglob('*.md')); inputs.extend(promptpaths)
    prompts={ctx:dict(path=str((Q/'prompts_rendered'/f'{ctx}.md').relative_to(Q)),sha256=sha(Q/'prompts_rendered'/f'{ctx}.md')) for ctx in key['contexts']}
    diff=''.join(difflib.unified_diff((Q/'prompts_rendered/type2/t04.md').read_text().splitlines(True),(Q/'prompts_rendered/t04.md').read_text().splitlines(True),fromfile='prompts_rendered/type2/t04.md (original)',tofile='prompts_rendered/t04.md (environment amendment)'))
    (Q/'PROMPT_DIFF.diff').write_text(diff)
    voids=sorted((Q/'answers').glob('*VOID*')); inputs.extend(voids)
    report=dict(controls=controls,flagged_contexts=flagged,amendments=amended.get('amendments',[]),scans=scans,unavailable_contexts=unavailable,untyped_rows=sum(r['type'] is None for r in typed),bed_rows=len(typed),excluded_control_line_ids=sorted({r['line_id'] for r in key['items'].values() if r['control']}),opus_mapping=MAP,unmapped_opus_types=sorted({r['type'] for r in opus}-set(MAP)),compared_rows=len(compared),exact_matches=len(compared)-len(disagreements),exact_agreement=(len(compared)-len(disagreements))/len(compared) if compared else None,confusion_matrix={k:dict(v) for k,v in sorted(matrix.items())},disagreements=disagreements,rendered_prompts=prompts,all_prompt_versions={str(p.relative_to(Q)):sha(p) for p in promptpaths},void_evidence=[str(p.relative_to(Q)) for p in voids],notes=['No reading runs or crop judgments performed.','sample.jsonl includes 20 distinct controls: excluded from bed output.','Sol rotated replaces the sample rotated field; original sample value preserved as sample_rotated.','Opus types in typing.jsonl are mapped codes; originals also preserved.','Group C: ceil(10% of remainder), random.Random(20261019), candidates sorted by line_id.'])
    dump(Q/'AGREEMENT.json',report)
    md=['# SS5 agreement','',f"Bed rows: {len(typed)}; untyped: {report['untyped_rows']}. Controls excluded: 20.",f"Flagged under amended expectations (>1 erroneous control): {', '.join(flagged) or 'none'}.",'','## Controls','', '| Context | v1 errors | Amended errors | Flagged |','|---|---:|---:|---|']
    for ctx,v in controls.items():md.append(f"| {ctx} | {v['v1']['error_count']}/{v['v1']['count']} | {v['amended']['error_count']}/{v['amended']['count']} | {v['amended']['flagged']} |")
    for ctx,v in controls.items():
        for version,result in v.items():
            md.extend(['',f'### {ctx}: {version}'])
            for r in result['results']:
                if not r['ok']:md.append(f"- {r['line_id']} ({r['card_id']}): errors {', '.join(r['errors'])}; actual `{json.dumps(r['actual'],ensure_ascii=False)}`; expected `{json.dumps(r['expected'],ensure_ascii=False)}`")
            if not result['error_count']:md.append('No errors.')
    md.extend(['','## Stratum 1 (opus)', '',f"Exact agreement: {report['exact_matches']}/{len(compared)} = {report['exact_agreement']:.4%}.",'','Rows = mapped Opus; columns = Sol.'])
    columns=sorted({r['type'] for r in compared});md+=['','| Opus / Sol | '+' | '.join(columns)+' |','|---|'+'---:|'*len(columns)]
    for t,counts in sorted(matrix.items()):md.append('| '+t+' | '+' | '.join(str(counts.get(c,0)) for c in columns)+' |')
    md.extend(['','### Disagreements','','| line_id | Opus | Sol | Google text |','|---|---|---|---|'])
    for r in disagreements:md.append('| '+' | '.join(str(r[k]).replace('|','\\|').replace('\n',' ') for k in ('line_id','opus','sol','google_text'))+' |')
    md.extend(['','## Opus mapping','',*['- '+k+' → '+v for k,v in MAP.items()],'Unmapped types (kept verbatim): '+str(report['unmapped_opus_types']), '', '## Prompt provenance','',*['- '+ctx+': `'+p['path']+'` SHA256 `'+p['sha256']+'`' for ctx,p in prompts.items()],'','t04 rerun adds only the environment restrictions shown below. Original and amended prompts are preserved.','```diff',diff.rstrip(),'```','','## Control amendments','',json.dumps(report['amendments'],ensure_ascii=False,indent=2),'','## Void evidence (never merged)','',*['- '+p for p in report['void_evidence']],'','## Method notes','',*report['notes']])
    (Q/'AGREEMENT.md').write_text('\n'.join(md)+'\n')
    gs=groups(typed); sheets=render(gs)
    test=SS/'tests/test_ss5_merge.py'; run=subprocess.run([sys.executable,'-B',str(test)],capture_output=True,text=True);(Q/'SS5_tests.log').write_text(run.stdout+run.stderr)
    if run.returncode:raise ValueError('SS5 tests failed: see q3/SS5_tests.log')
    finalize(inputs,typed,report,prompts,gs,sheets,flagged,outputs,run)

def finalize(inputs,typed,report,prompts,gs,sheets,flagged,outputs,run):
    test=SS/'tests/test_ss5_merge.py'
    ledger=rows(Q/'usage_ledger.jsonl')
    def totals(rr):
        out=collections.Counter()
        for r in rr:out.update(r.get('usage',{}))
        return dict(out)
    for r in typed:
        p=Path(r['crop_path']);inputs.append(p)
        if sha(p)!=r['crop_sha256']:raise ValueError('crop hash mismatch: '+r['line_id'])
    inputs.extend([Path(__file__),test,FONT]); outpaths=[Q/p for p in outputs if p!='SS5_RECEIPT.json']+sorted((Q/'eye_sheets').glob('*.png'))
    receipt=dict(status='READY',inputs={str(p):sha(p) for p in sorted(set(inputs))},outputs={str(p.relative_to(Q)):sha(p) for p in outpaths},receipt_hash_note='Receipt excludes itself to avoid a circular hash.',counts=dict(typing=len(typed),untyped=report['untyped_rows'],eye_sheets=sheets,groups={g:len(rr) for g,rr in gs.items()},compared=report['compared_rows'],exact_matches=report['exact_matches']),flagged_contexts=flagged,controls={ctx:{v:res['error_count'] for v,res in scores.items()} for ctx,scores in report['controls'].items()},rendered_prompts=prompts,void_evidence=report['void_evidence'],font=dict(name=ImageFont.truetype(str(FONT),18).getname(),path=str(FONT),sha256=sha(FONT),size_px=18,unicode_cmap_checked=True,missing_label_characters=[]),tests=dict(command=[sys.executable,'-B',str(test)],returncode=run.returncode,log='SS5_tests.log',result=run.stderr.strip()),usage=dict(ledger_entries=len(ledger),all_totals=totals(ledger),nonvoid_totals=totals([r for r in ledger if not r.get('void')]),void_totals=totals([r for r in ledger if r.get('void')]),wall_s=sum(r.get('wall_s',0) for r in ledger),note='Ledger summed as recorded, including repeated labels; no new reading usage.'),rendering=dict(per_sheet=8,max_crop_size=[900,200],max_upscale=4,resampling='NEAREST',frame='1 px red outside crop edge; all crop pixels retained',verification='PNG decode, geometry checks and Unicode cmap; sheets not interpreted'),notes=report['notes'])
    dump(Q/'SS5_RECEIPT.json',receipt)
    print(f"SS5 READY: typing {len(typed)} rows, eye sheets {sheets} (A {len(gs['A'])}, B {len(gs['B'])}, C {len(gs['C'])}), agreement q3/AGREEMENT.md, receipt q3/SS5_RECEIPT.json")
if __name__=='__main__':
    try:main()
    except Exception as e: print('SS5 FAILED: '+str(e));sys.exit(1)
