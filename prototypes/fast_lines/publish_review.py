"""Link saved review products and validate local links; never rerun experiments."""
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from .shared.manifest import OUT, load
from .shared.timing import dump
from .shared.review import detector_record
from .workflow import NAMES


def audit_variant_exports():
    """Apply the main-result export contract to optional saved comparators."""
    count=0; corrected=[]
    for name in NAMES:
        for path in sorted((OUT/name/'variants').glob('*/*.json')):
            data=json.loads(path.read_text())
            clean=detector_record(data,data['items'],data['seconds'])
            assert isinstance(clean['seconds'],(int,float)) and clean['seconds']>=0
            for item in clean['items']:
                assert 'baseline' in item and 'score' in item
            if clean!=data:
                saved=OUT/'shared/original-variant-exports'/path.relative_to(OUT)
                saved.parent.mkdir(parents=True,exist_ok=True)
                if not saved.exists(): saved.write_bytes(path.read_bytes())
                corrected.append(str(path.relative_to(OUT)))
                dump(path,clean)
            count+=1
    receipt=OUT/'shared/variant-validation.json'
    previous=json.loads(receipt.read_text()) if receipt.exists() else {}
    corrected=sorted(set(corrected+previous.get('clipped_exports',[])))
    dump(receipt,dict(status='passed',files=count,clipped_exports=corrected,
                     contract='Main-result coordinate clipping and discounted filtering; originals preserved'))


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]

    def handle_starttag(self, tag, attrs):
        self.links.extend(value for key,value in attrs if key in ('href','src') and value)


def main():
    audit_variant_exports()
    rows=load(OUT/'shared/manifest.json')['pages']
    for name in NAMES+['composition']:
        directory=OUT/name
        path=directory/'index.html'
        text=path.read_text()
        text=re.sub(r'<p id="saved-review-links">.*?</p>', '', text)
        links=[('summary.json','Timing summary'),('timing.jsonl','Raw timings')]
        links += [(p.name,p.stem) for p in sorted(directory.glob('contact-*.jpg'))]
        links += [(p,p) for p in ('README-results.md','page_failures.json','per_line_comparison.json') if (directory/p).exists()]
        navigation='<p id="saved-review-links">'+' · '.join(f'<a href="{html.escape(p)}">{html.escape(label)}</a>' for p,label in links)+'</p>'
        text=text.replace('</h1>','</h1>'+navigation,1)
        text=re.sub(r'<span class="saved-variants">.*?</span>', '', text)
        for row in rows:
            page=row['page']
            extra=[(p.relative_to(directory).as_posix(),p.parent.name) for p in sorted((directory/'variants').glob('*/'+page+'.json'))]
            extra += [(p.name,p.stem.split(page+'_',1)[-1]) for p in sorted(directory.glob(page+'_[25]_*.jpg'))]
            if extra:
                key=f'<a href="{page}.evidence.json">Ledger</a>'
                span='<span class="saved-variants"> · '+' · '.join(f'<a href="{html.escape(p)}">{html.escape(label)}</a>' for p,label in extra)+'</span>'
                text=text.replace(key,key+span)
        path.write_text(text)

    baseline=OUT/'shared/baseline/index.html'
    baseline.write_text(baseline.read_text().replace('../shared/references/','../references/'))
    perturb=OUT/'shared/perturbations'
    sheets=sorted(perturb.glob('*-sheet.jpg'))
    (perturb/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Q7 synthetic witnesses</title><h1>Synthetic perturbation pairs</h1><p>Known pixel changes, not real-page accuracy. Seven variants per exemplar. Only photometric witnesses were measured.</p><a href="measurements.json">Raw measurements</a>'+''.join(f'<p><a href="{p.name}">{p.stem}</a></p><img style="max-width:95vw" src="{p.name}">' for p in sheets))
    root=OUT/'shared/index.html'
    text=root.read_text()
    text=re.sub(r'<p id="audit-links">.*?</p>','',text)
    text+='<p id="audit-links"><a href="perturbations/index.html">Synthetic witnesses</a> · <a href="validation.json">Output audit</a> · <a href="failures_and_unknowns.json">All failures and unknowns</a> · <a href="review-link-validation.json">Link audit</a></p>'
    root.write_text(text)
    # Reserve the receipt before checking the root's link to it.
    receipt=OUT/'shared/review-link-validation.json'
    dump(receipt,dict(status='checking'))
    documents=[root,baseline,perturb/'index.html']+[OUT/n/'index.html' for n in NAMES+['composition']]
    documents += [OUT/'shared/references'/f'{r["page"]}.html' for r in rows]
    missing=[]; count=0
    for path in documents:
        parser=Links(); parser.feed(path.read_text())
        for link in parser.links:
            parts=urlsplit(link)
            if parts.scheme or not parts.path: continue
            count+=1
            if not (path.parent/unquote(parts.path)).exists():
                missing.append(dict(document=str(path.relative_to(OUT)),link=link))
    dump(receipt,dict(status='passed' if not missing else 'failed',documents=len(documents),local_links=count,missing=missing))
    assert not missing,missing[:12]
    print(json.dumps(dict(documents=len(documents),local_links=count,missing=len(missing))))


if __name__=='__main__':
    main()
