"""RU1-S offline clearance of ctx04's recorded, overwritten split panels.
Keeps the original failed scan. No reader, crop regeneration or shell replay.
Only a SHA-bound literal panel command is supported, with original manifest
pixels as inputs; every unmatched returned image must match mode/size/pixels.
"""
import base64
import io
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'reading'))
from common import ROOT, PACK_ROOT, rows, dump, sha
from scan_rollout import image_blocks, match_image, integrity
from PIL import Image

PANEL_COMMAND = """python3 - <<'PY'
import json,subprocess,math
for i,line in enumerate(open('items.jsonl'),1):
 r=json.loads(line)
 w,h=map(int,subprocess.check_output(['magick','identify','-format','%w %h',r['crop']]).decode().split())
 parts=[]
 for j in range(4):
  x=w*j//4; end=w*(j+1)//4
  p=f'zoom/{i:03}part{j}.png';parts.append(p)
  subprocess.run(['magick',r['crop'],'-crop',f'{end-x}x{h}+{x}+0','+repage','-resize','400%',p],check=True)
 subprocess.run(['magick',*parts,'-background','white','-gravity','west','-append',f'zoom/{i:03}panel.png'],check=True)
print('88 split enlargement panels created')
PY"""


def panel(source, output):
    with Image.open(source) as im: w,h=im.size
    parts=[]
    for j in range(4):
        x=w*j//4; end=w*(j+1)//4
        dest=output.with_name(output.stem+f'part{j}.png');parts.append(dest)
        subprocess.run(['magick',str(source),'-crop',f'{end-x}x{h}+{x}+0','+repage','-resize','400%',str(dest)],check=True,capture_output=True)
    subprocess.run(['magick',*[str(p) for p in parts],'-background','white','-gravity','west','-append',str(output)],check=True,capture_output=True)


def clear(rollout):
    directory=PACK_ROOT/'ctx04/r2';scanpath=ROOT/'answers/ctx04.r2.scan.json'
    scan=json.loads(scanpath.read_text());records=rows(rollout)
    if integrity(directory)[0]:raise ValueError('pack integrity failure')
    if PANEL_COMMAND not in scan['commands']:raise ValueError('recorded command differs')
    targets={v['record'] for v in scan['violations']}
    if any(v['reason']!='image provenance: unmatched image provenance' for v in scan['violations']):raise ValueError('unhandled non-image violation')
    # The command was recorded before every target image, not inferred later.
    # JSON-encoded tool arguments contain escaped newlines; check decoded strings.
    from scan_rollout import quoted_property
    command_records=[]
    for i,r in enumerate(records):
        p=r.get('payload') or {};raw=p.get('input',p.get('arguments',''))
        if isinstance(raw,str) and PANEL_COMMAND in quoted_property(raw,'cmd'):command_records.append(i)
    if not command_records or any(min(command_records)>=i for i in targets):raise ValueError('command not prior to images')
    proofs=[];sources={};manifest=directory.parent/'MANIFEST.r2.json'
    with tempfile.TemporaryDirectory(prefix='ru1s-panel-') as temp:
        temp=Path(temp);candidates=[]
        for n,item in enumerate(rows(directory/'items.jsonl'),1):
            source=directory/item['crop'];sources[str(source)]=sha(source)
            # No reader-generated zoom can enter the fresh reproduction tree.
            native=temp/f'{n:03}native.png';shutil.copyfile(source,native)
            dest=temp/f'{n:03}panel.png';panel(native,dest)
            with Image.open(dest) as im:candidates.append((dest.name,dest.read_bytes(),im.convert('RGB')))
        for ordinal in sorted(targets):
            matched=[]
            for b in image_blocks(records[ordinal]['payload']):
                url=b['image_url'];url=url.get('url') if isinstance(url,dict) else url
                data=base64.b64decode(url.split(',',1)[1],validate=True)
                m=match_image(data,candidates)
                if m is None:raise ValueError(f'unresolved returned image at {ordinal}')
                if m:
                    # Supplemental clearance is exact only, never approximate.
                    if m['match'] not in {'bytes','pixels'}:raise ValueError('nonexact panel match')
                    matched.append(m)
            needed=sum(v['record']==ordinal for v in scan['violations'])
            if len(matched)<needed:raise ValueError(f'unresolved panel images at {ordinal}: {len(matched)}/{needed}')
            proofs.append(dict(record=ordinal,unmatched_images=needed,exact_panel_matches=matched))
    if integrity(directory)[0] or any(sha(p)!=h for p,h in sources.items()):raise ValueError('input drift')
    result=dict(method='fresh original-only reproduction of literal recorded four-part 4x panel command; exact mode/size/pixels',
        rollout=str(rollout),rollout_sha256=sha(rollout),manifest_sha256=sha(manifest),source_sha256=sources,
        original_failed_scan_sha256=sha(ROOT/'RU1S_original_scans/ctx04.r2.scan.json'),proofs=proofs)
    dump(ROOT/'RU1S_panel_clearance.json',result)
    scan.update(ok=True,violations=[],resolved_violations=scan['violations'],supplemental_clearance=result)
    dump(scanpath,scan)
    print('ctx04/r2: all remaining provenance findings cleared by exact original-only panel reproduction')

if __name__=='__main__':clear(Path(sys.argv[1]))
