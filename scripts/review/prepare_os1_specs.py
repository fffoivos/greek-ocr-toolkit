"""Offline source binding and deterministic OS1 selection. Never modifies inputs."""
from __future__ import annotations
from greekocr.ops.data_root import input_path as _data_input
import collections, hashlib, json, random, re
from pathlib import Path
from scripts.layout_paths import relocated
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
PROJECTS = Path.home() / 'Projects'
BASE = PROJECTS / 'greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3'
W = PROJECTS / 'collect-v3-data/run/W1'
T = PROJECTS / 'greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked'
DEST = relocated(ROOT / 'docs/owner_sheets')
SEED = 20261017
INPUTS = {}

def bind(p):
    p = Path(p)
    if str(p) not in INPUTS:
        h = hashlib.sha256()
        with _data_input(p).open('rb') as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b''): h.update(chunk)
        INPUTS[str(p)] = h.hexdigest()
    return p

def read(p): return json.loads(_data_input(bind(p)).read_text())
def rows(p): return [json.loads(l) for l in _data_input(bind(p)).read_text().splitlines() if l.strip()]
def clean(s): return s.replace('?', '[uncertain]')
def dump(p, x):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n')

ALIASES = {'b':'bsb_poly1850__poly1850', 'i':'ia_poly1850__poly1850',
 'n':'nlg__poly1850','g':'nlg__greek_poly','p':'nlg__poly1900',
 'k':'kosmopolis__poly1900','l':'lekythos__poly1900',
 'm':'ia_poly1850__mixed_greek_latin','a':'ia_poly1850__latin',
 'r':'ia_russian__cyrillic','s':'serbia__cyrillic','e':'elstat__numerics_tables',
 'z':'gazette_modern__modern_scanned__probe_1982_1985',
 'q':'gazette_modern__modern_scanned__measured_1986_1990',
 'tk':'kosmopolis','tl':'lekythos','tz':'gazette_modern'}

def main():
    results = read(BASE/'c1/c1_results.json')
    records = {}; all_c1 = []
    for stage, folder in [('C1', BASE/'c1/verdicts'), ('T6b', T/'checks/verdicts')]:
        for vp in sorted(folder.glob('*.jsonl')):
            bed = vp.stem.rsplit('__',1)[0]
            if stage == 'T6b' and bed not in ('kosmopolis','lekythos','gazette_modern'): continue
            kp = W/'c1'/f'{bed}_key.json' if stage == 'C1' else T/'cards'/f'{bed}_key.json'
            key = read(kp)
            for v in rows(vp):
                info = key[v['card_id']]
                r = dict(v, **{k:val for k,val in info.items() if k not in v}, stage=stage, bed=bed,
                         verdict_path=str(vp), key_path=str(kp))
                records[(stage,bed,v['card_id'])] = r
                if stage == 'C1': all_c1.append(r)
    # Bind the aggregate lists as independent evidence; fail on stale card associations.
    for bed, aggregate in results.items():
        for value in aggregate.values():
            if isinstance(value,list):
                for item in value:
                    if isinstance(item,dict) and 'line_id' in item:
                        assert records[('C1',bed,item['card_id'])]['line_id'] == item['line_id']
    yer = read(BASE/'c1/yer_adjudication/table.json')
    for y in yer:
        if y['set']=='c1':
            r=records[('C1',ALIASES['r'],y['card_id'])]
            r['yer_adjudication']=y
    needed={r['line_id'] for r in records.values()}
    features={}
    fp=bind(W/'features.jsonl')
    with fp.open() as f:
        for line in f:
            r=json.loads(line)
            if r['id'] in needed: features[r['id']]=r
    for r in records.values():
        f=features[r['line_id']]
        r['label']=r.get('literal_label', f.get('literal_label',f['text']))
        r['source']=f['source']; r['class']=f['primary_class']
    def refs(alias, numbers):
        return [records[('T6b' if alias.startswith('t') else 'C1',ALIASES[alias],f'c{n:03}')] for n in numbers]
    def pool(*pairs): return [r for alias,nums in pairs for r in refs(alias,nums)]
    # Explicit, reviewable fault-to-evidence mapping; selection within each pool is seeded.
    pools=[
      [pool(('b',[4,19]),('i',[52]),('n',[17,55])),
       pool(('b',[2]),('i',[4,15]),('n',[7,32,66,70])),
       pool(('b',[87]),('i',[10,53,77,80]),('n',[66])),
       pool(('i',[7]),('m',[60,67])),
       pool(('m',[40,58]),('b',[86]))],
      [pool(('k',[9,10,13,41,51,61,68]),('l',[9,30,33,35,42,44,50,69,70,83,92]),('p',[23,41,51,84,86,87,94,99]),('tk',[12,41,67,79]),('tl',[6,15,18,22,70,86,89])),
       pool(('tk',[54,62]),('tl',[88])),
       pool(('k',[17,30,40,71,81]),('l',[31,51]),('p',[7,31,77]),('tk',[74]),('tl',[41,74])),
       pool(('g',[12]),('l',[98]))],
      [pool(('b',[86]),('m',[14,69,85]),('n',[11])),
       pool(('r',[67]),('q',[4])), pool(('a',[60])), pool(('q',[74])), []],
      [pool(('e',[38,93])),pool(('e',[13])),pool(('tz',[17,22,28])),pool(('e',[68]),('tz',[37])),
       pool(('b',[41]),('i',[5,88,93,95]),('a',[66]),('m',[59]))],
      [pool(('s',[18,52,58,60,73,80]),('r',[3,76,79,80,84]),('n',[58,97]),('m',[57,77])),
       pool(('p',[81,83,100]),('tk',[97])),pool(('k',[42]),('r',[37])),
       pool(('z',[71,43]),('q',[84]),('l',[85,93,97]),('tl',[62,97]),('a',[41])),
       pool(('p',[3]),('z',[14]),('n',[14,96]))],
      [pool(('m',[28,59,80,85,91])),pool(('m',[2,10])),pool(('m',[17])),pool(('m',[48]))],
      [pool(('a',[4,10,62])),pool(('a',[23,47,65])),pool(('a',[64]))],
      [pool(('r',[int(y['card_id'][1:]) for y in yer if y['set']=='c1' and y['google_yer_errors']>0])),
       pool(('r',[38,57])),pool(('r',[11,26,98]))],
      [pool(('s',[32,49,77,97])),pool(('s',[14,17,57]))],
      [pool(('q',[3,6,15,24,42,56,59,67,68,70,76,79,82,95,96,97]),('z',[4,24,29,30,34,35,40,41,58,65,76,78,79,82,84,85,89,99]),('tz',[56,77,91])),
       pool(('z',[11,15,20,25,27,53,68])),pool(('tz',[73]),('q',[54])),pool(('z',[3,55]),('tz',[97]))]
    ]
    coordinator=bind(DEST/'inputs/label_failure_modes_coordinator.html')
    soup=BeautifulSoup(coordinator.read_text(),'html.parser')
    source_sections=soup.select('section.cls')[:9]
    headings=['polytonic 1850s','polytonic 1900s','capitals/headings','numerics','punctuation/dialogue',
              'mixed Greek+Latin','Latin','Cyrillic Russian','Cyrillic Serbian','modern monotonic Gazette']
    sections=[]; groups=[]; choices=[]
    for i,heading in enumerate(headings):
        si=i if i<8 else i-1
        if i==8: si=7
        section=source_sections[si]
        stats=section.select_one('.stats').get_text(' ',strip=True).replace('model CER','E3 CER')
        sections.append(dict(id=f's{i}',heading=heading,header=stats,coordinator_class=section.h2.get_text(' ',strip=True)))
        fault_rows=section.select('tr')[1:]
        if i==7: fault_rows=fault_rows[:3]
        if i==8: fault_rows=fault_rows[3:]
        assert len(fault_rows)==len(pools[i]), (i,len(fault_rows),len(pools[i]))
        for j,(tr,candidates) in enumerate(zip(fault_rows,pools[i])):
            cells=tr.select('td');fault=cells[0].get_text(' ',strip=True);rate=cells[2].get_text(' ',strip=True)
            group=dict(id=f's{i}f{j}',section=f's{i}',heading=f'{fault} · {rate}',fault=fault,rate=rate)
            groups.append(group); choices.append((group,candidates))
    # Scarce pools allocated first, with each line appearing once per sheet and one db document.
    used=set(); selected={};rng=random.Random(SEED)
    for group,candidates in sorted(choices,key=lambda pair:len({r['line_id'] for r in pair[1]})):
        unique={r['line_id']:r for r in candidates}; ordered=[unique[k] for k in sorted(unique)]
        rng.shuffle(ordered); available=[r for r in ordered if r['line_id'] not in used]
        picked=available[:3]; used.update(r['line_id'] for r in picked); selected[group['id']]=picked
        group['candidate_count']=len(unique);group['available_after_dedup']=len(available)
        group['candidate_ids']=sorted(unique)
        if len(picked)<3:
            group['gap']=f'fewer than 3 cards ({len(picked)})' if picked else 'no card in the checked sets'
            if unique and not available: group['gap_reason']='Witness already shown in another fault subsection; one note document per line.'
    def printed(r):
        for key in ('printed','printed_text','adjudicated_print'):
            if r.get(key): return r[key],key
        # Reconstruct only when every checker clause is an exact, unique substitution in this label.
        text=r['label'];detail=r.get('detail','')
        if not detail or any(c in detail for c in '()/[]?'): return '', 'No complete line adjudication; partial detail retained in Note.'
        for clause in detail.split(';'):
            if clause.count(' → ')!=1: return '', 'No complete line adjudication; partial detail retained in Note.'
            ink,google=map(str.strip,clause.split(' → '))
            if not ink or not google or text.count(google)!=1: return '', 'No complete line adjudication; partial detail retained in Note.'
            text=text.replace(google,ink,1)
        return text,'Exact substitutions from every checker clause in the full Google label; no new reading.'
    def card(r,group,class_name,fault):
        lid=r['line_id'];image=crop(lid);bind(image)
        pr,basis=printed(r)
        return dict(line_id=lid,doc_id=lid,image=str(image),clean_image=str(image),alt='Full Google line crop',
           rows=[dict(name='Google',text=r['label'])],printed=pr,note=clean(r.get('detail','')),
           tags=[dict(text=t) for t in (class_name,fault,r['source'])],group=group,
           provenance=dict(stage=r['stage'],card_id=r['card_id'],verdict_path=r['verdict_path'],key_path=r['key_path'],
                           checker_detail=r.get('detail',''),printed_basis=basis,crop=crop_receipts[lid],**({'yer_adjudication':r['yer_adjudication']} if 'yer_adjudication' in r else {})))
    crop_receipts={}
    def crop(lid):
        original=W/'crops'/f'{lid}.png'
        if original.is_file():
            crop_receipts[lid]=dict(original_path=str(original),reconstructed=False)
            return original
        f=features[lid];page=bind(f['crop_source_image'])
        target=ROOT/'artifacts/owner_sheets/recovered_crops'/f'{lid}.png'
        target.parent.mkdir(parents=True,exist_ok=True)
        with Image.open(page) as im: im.convert('RGB').crop(f['crop_bbox']).save(target)
        crop_receipts[lid]=dict(original_path=str(original),reconstructed=True,page=str(page),bbox=f['crop_bbox'],
                               expected_sha256=f['crop_sha256'],recovered_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
        return target
    a=dict(title='Failure modes per class',intro='Rates and faults from the coordinator. Printed follows explicit checker substitutions where the full line can be reconstructed; otherwise it is empty. Notes retain checker detail.',
           seed=SEED,sections=sections,groups=groups,lines=[])
    for g in groups:
        for r in selected[g['id']]: a['lines'].append(card(r,g['id'],sections[int(g['section'][1:])]['heading'],g['fault']))
    dump(DEST/'failure_modes_per_class/spec.json',a)
    # Sheet A is rendered before preparing B.
    from scripts.review.owner_sheets import build
    build('failure_modes_per_class')
    sg_all=rows(BASE/'segmentation_gallery/examples.jsonl')
    sg=[r for r in sg_all if r['id'].startswith('sg1-')]
    assert len(sg)==24
    types={'merged_multi_line':'merged','box_fragment':'fragment','readable_half_line_overrun':'overrun',
           'clipped_edge':'clipped','rotated_vertical_line':'rotated'}
    bcards={}
    for e in sg:
        lid=e['line_id'];group=types[e['type']]
        # SG1 holds original geometry; use native crop pixels, not the resized gallery crop.
        if lid in features:
            image=crop(lid)
        else:
            image=Path(e['original_crop_path'])
            if not image.is_file():
                page=bind(e['page_raster']);image=ROOT/'artifacts/owner_sheets/recovered_crops'/f'{lid}.png'
                image.parent.mkdir(parents=True,exist_ok=True)
                with Image.open(page) as im: im.convert('RGB').crop(e['crop_bbox']).save(image)
        bind(image)
        strip=BASE/'segmentation_gallery'/e['image_paths']['page_strip'] if e['image_paths'].get('page_strip') else None
        r=next((v for v in records.values() if v['line_id']==lid),None)
        if r:
            c=card(r,group,e['class'],group)
        else:
            c=dict(line_id=lid,doc_id=lid,image=str(image),clean_image=str(image),alt='Full Google line crop',
              rows=[dict(name='Google',text=e['label_text'])],printed='',note=clean(e['card_verdict_detail']),tags=[],group=group,
              provenance=dict(stage=e['verdict_stage'],verdict_path=e['verdict_path'],key_path=e['key_path'],checker_detail=e['card_verdict_detail'],printed_basis='No complete line adjudication'))
            bind(e['verdict_path']);bind(e['key_path'])
        c['provenance']['sg1_id']=e['id'];c['provenance']['classification_note']=e.get('classification_note')
        if 'crop' not in c['provenance']:
            c['provenance']['crop']=dict(original_path=e['original_crop_path'],reconstructed=str(image)!=e['original_crop_path'],
                page=e['page_raster'],bbox=e['crop_bbox'],expected_sha256=e['expected_crop_sha256'],
                recovered_sha256=hashlib.sha256(image.read_bytes()).hexdigest())
        if strip: bind(strip);c['zooms']=[dict(image=str(strip),alt="Page strip with Google's crop box drawn in red")]
        c['tags']=[dict(text=t) for t in (group,e['source'],e['class'],f"crop height {e['crop_height']} px")]
        bcards[lid]=c
    # All eight merged witnesses: seven explicit tags plus the full-previous-line detail.
    merged=[r for r in all_c1 if 'merged_two_lines' in r['errors']]+refs('z',[98])
    assert len(merged)==8
    fragments=pool(('a',[97]),('l',[94]),('g',[6]),('n',[88]))
    clipped=refs('q',[84])+refs('z',[1,53,86,91]);assert len(clipped)==5
    column=refs('e',[68])
    overrun_by_bed=collections.defaultdict(list)
    for r in all_c1:
        if 'crop_overrun' in r['errors'] and 'merged_two_lines' not in r['errors'] and r not in column and r not in merged:
            overrun_by_bed[r['bed']].append(r)
    # Round-robin over strata; seed the order inside each stratum.
    for bed,rr in sorted(overrun_by_bed.items()):
        rr.sort(key=lambda r:r['line_id']);rng.shuffle(rr)
    overruns=[]
    while len(overruns)<12:
        for bed in sorted(overrun_by_bed):
            rr=overrun_by_bed[bed]
            if rr and len(overruns)<12: overruns.append(rr.pop())
    for group,rr in [('merged',merged),('fragment',fragments),('column',column),('clipped',clipped),('overrun',overruns)]:
        for r in rr:
            lid=r['line_id']
            if lid in bcards:
                c=bcards[lid]
                if group not in [t['text'] for t in c['tags']]:c['tags'].append(dict(text=group))
                continue
            c=card(r,group,r['class'],group)
            with Image.open(c['image']) as im:h=im.height
            c['tags'].append(dict(text=f'crop height {h} px'))
            bcards[lid]=c
    rotated=[c for c in bcards.values() if c['group']=='rotated']
    assert len(rotated)==4
    for c in rotated:
        with Image.open(c['image']) as im: assert im.height>im.width,(c['line_id'],im.size)
    # Add native page strips for every additional C1 card with a cached source page.
    assetdir=ROOT/'artifacts/owner_sheets/segmentation_strips';assetdir.mkdir(parents=True,exist_ok=True)
    for c in bcards.values():
        if c.get('zooms'): continue
        f=features[c['line_id']];page=Path(f.get('crop_source_image',''))
        if not page.is_file():c['provenance']['strip_gap']='No cached source page';continue
        bind(page)
        with Image.open(page) as im:
            x0,y0,x1,y1=f['crop_bbox'];pad=max(y1-y0,round(f.get('page_median_row_height',y1-y0)*1.5))
            bounds=[max(0,x0-pad),max(0,y0-pad),min(im.width,x1+pad),min(im.height,y1+pad)]
            strip=im.crop(bounds).convert('RGB');draw=ImageDraw.Draw(strip)
            bx=f['bbox'];a0,b0=bounds[:2]
            draw.rectangle([bx[0]-a0,bx[1]-b0,bx[2]-a0-1,bx[3]-b0-1],outline=(255,40,30),width=2)
            path=assetdir/f"{c['line_id']}.png";strip.save(path,optimize=True)
        c['zooms']=[dict(image=str(path),alt="Page strip with Google's box drawn in red")]
        c['provenance']['strip']=dict(page=str(page),bounds=bounds,google_bbox=f['bbox'])
    counts=read(BASE/'segmentation_gallery/counts.json')
    headers=[]
    for source,v in counts['per_source'].items():
        def rate(stage):
            r=v[stage]['overrun_per_100'];return 'not measured' if r is None else str(r)+' / 100'
        headers.append(f"{source}: screen_merged {v['screen_merged']}/{v['feature_rows']}; rotated {v['rotated_crop']}/{v['feature_rows']}; overrun before {rate('C1')}, after {rate('T6b')}")
    headers += ['Screen counts use all feature rows. Overrun comparisons are unpaired C1 / T6b samples; they do not measure a causal masking fix.',
                'Cross-cutting geometry: length mismatch of 3+ atoms is 2.8% of test lines and 44% of all edits. Printed rows with no Google box: 19% of rows (coordinator figure). The counts provenance scopes the latter measurement to missed admitted boxes in an archived visual adjudication.']
    order=['merged','fragment','overrun','column','clipped','rotated']
    b=dict(title='Segmentation failures',intro='\n'.join(headers),seed=SEED,groups=[dict(id=g,heading=g) for g in order],
      lines=sorted(bcards.values(),key=lambda c:(order.index(c['group']),c['line_id'])),
      missing_box_hook=dict(id='missing_box',heading='missing box',enabled=False,input='SG2 strips; excluded by OS1 scope',observed_records=sum(r['id'].startswith('sg2-') for r in sg_all),required=['line_id','page strip','absent Google box evidence','checker detail']),
      selection=dict(merged_ids=[r['line_id'] for r in merged],fragment_ids=[r['line_id'] for r in fragments],clipped_ids=[r['line_id'] for r in clipped],overrun_ids=[r['line_id'] for r in overruns],column_ids=[r['line_id'] for r in column],rotated_ids=[c['line_id'] for c in rotated]))
    dump(DEST/'segmentation_failures/spec.json',b)
    build('segmentation_failures')
    dump(DEST/'input_sha256.json',INPUTS)
    print(json.dumps(dict(A=len(a['lines']),subsections=len(groups),gaps=sum('gap' in g for g in groups),B=len(b['lines']),groups=collections.Counter(c['group'] for c in b['lines'])),indent=2))

if __name__=='__main__':main()
