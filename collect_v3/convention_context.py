"""Rebuild T4b word-attestation context from raw cached OCR, without features oracle.

The context contains word keys and page IDs, no lines for candidate training.
It lets the same dropped-hyphen rule retain its original cross-page evidence.
"""
from pathlib import Path
from collections import defaultdict,Counter
from .common import rows,read_json,write_json,sha
from .vendor.assembly_fix import page_tokens,assemble_line
from .vendor.conventions import WORD,key

def build(projects,destination):
    projects=Path(projects);occ=defaultdict(set);nonfinal=Counter();inputs=[];n=0
    for track in ('ia','intl','gr'):
        base=projects/f'greek-ocr-toolkit-sol-funnel-{track}'/'docs/harvest/sample_v1'/track
        bypage=defaultdict(set)
        for r in rows(base/'lines.jsonl'):bypage[r['page_id']].add(r['id'])
        for p in rows(base/'pages.jsonl'):
            if p['id'] not in bypage:continue
            parsed=read_json(base/'google/parsed/docai'/(p['image_sha256']+'.json'));rawpath=Path(parsed['raw_json_path'])
            if not rawpath.exists():
                hits=list((base/'google/docai').rglob(rawpath.name))
                if len(hits)!=1:raise ValueError('cannot bind raw convention input')
                rawpath=hits[0]
            raw=read_json(rawpath);tokens,_,_=page_tokens(raw['document'],(p['width'],p['height']))
            inputs.append(dict(path=str(rawpath),sha256=sha(rawpath)))
            for b in rows(base/'bulk/lines'/(p['id']+'.jsonl')):
                if b['id'] not in bypage[p['id']]:continue
                fixed=assemble_line(raw['document'],b['docai_index'],tokens)['fixed_label'];words=[key(m.group()) for m in WORD.finditer(fixed)]
                for w in words:occ[w].add((track,p['id']))
                nonfinal.update(words[:-1]);n+=1
    context=dict(occurrences={k:[list(p) for p in sorted(v)] for k,v in sorted(occ.items())},nonfinal=dict(sorted(nonfinal.items())))
    write_json(destination,context);write_json(Path(destination).with_name('convention_context_receipt.json'),dict(lines=n,words=len(occ),inputs=inputs,network=False,provider_calls=0,method='word-attestation index rebuilt by T4b assembly from full cached F2 raw responses; features.jsonl is not read'))
    return context

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--projects-root',default=str(Path.home()/'Projects'));p.add_argument('--output',default='docs/harvest/collect_v3/convention_context.json');a=p.parse_args();build(a.projects_root,a.output)
