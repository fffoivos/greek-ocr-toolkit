"""Bind homogeneous pixel-reviewed page script classes to cached card lines.

Unknown pages and pages containing both Greek systems stay eligible. This
manifest contains no Google text, recognizer marks, or blind mark verdicts.
"""
import json
from pathlib import Path
from scripts.labelfix.m2_run import BASE, inventory, sha, write_rows


def build(output):
    harvest=BASE.parent
    lookup={};bindings={}
    for track in ('gr','ia'):
        key=harvest/'sample_v1'/track/'blind_pages_key.json'
        if not key.exists():continue
        bindings[str(key)]=sha(key)
        pages={r['file']:r['page_id'] for r in json.loads(key.read_text())}
        for path in sorted(BASE.glob(track+'_pages_*.jsonl')):
            bindings[str(path)]=sha(path)
            for row in map(json.loads,path.read_text().splitlines()):
                page_id=pages.get(row['page'])
                if page_id:lookup[page_id]=(row['scripts'],str(path),row['page'])
    rows=[]
    for card in inventory():
        lid=card['key']['line_id'];page=lid.rsplit('-l',1)[0]
        scripts,path,review_page=lookup.get(page,([],None,None))
        rows.append(dict(id=card['id'],line_id=lid,page_id=page,scripts=scripts,
            provenance='pixel-reviewed homogeneous page inherited by line' if scripts else 'unknown',
            annotation_path=path,review_page=review_page))
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    write_rows(output,rows)
    output.with_suffix('.receipt.json').write_text(json.dumps(dict(source_sha256=bindings,manifest_sha256=sha(output),
        rule='Only greek_monotonic without greek_polytonic is excluded; mixed and unknown remain eligible',
        reference_text_used=False),ensure_ascii=False,indent=2)+'\n')
    return rows


if __name__=='__main__':
    build('docs/labelfix/spellcheck/S7_evidence/m2_script_classes.jsonl')
