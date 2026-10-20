import json,sys
from collections import Counter,defaultdict
from PIL import Image
from pilotlib import *
from classify import inspect

if __name__=='__main__':
    allrows=[]
    for gt in sorted((BASE/'bulk/ajax/data').glob('*/GT-pairs/*.gt.txt')):
        image=gt.with_suffix('').with_suffix('.png')
        if not image.exists():raise ValueError('unpaired GT '+str(gt))
        with Image.open(image) as im:size=list(im.size)
        text=gt.read_text();r=inspect(text,human_gt=True)
        allrows.append(dict(id=gt.stem.removesuffix('.gt'),item=gt.parents[1].name,label_source='GT4HistComment manually corrected and reverified (publisher declaration)',text_path=str(gt.relative_to(BASE)),text_sha256=sha(gt),crop_path=str(image.relative_to(BASE)),crop_sha256=sha(image),size=size,**r))
    path=BASE/'bulk/ajax-lines.jsonl';path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in allrows))
    summary=dict(lines=len(allrows),published_readme_count=3356,count_difference=len(allrows)-3356,source_revision=json.loads((BASE/'receipts/ajax-acquisition.json').read_text())['revision'],actual_file_count_not_readme_proxy=True,paired_images=len(allrows),page_images=len(list((BASE/'bulk/ajax/data').glob('*/imgs/*.png'))),script_classes=dict(Counter(r['script_class'] for r in allrows)),mixed_lines=sum(r['mixed_line'] for r in allrows),mixed_share=sum(r['mixed_line'] for r in allrows)/len(allrows),admitted_content_rules=sum(r['admitted'] for r in allrows),admitted_and_codec=sum(r['admitted'] and r['codec_v1_pass'] for r in allrows),admitted_mixed_codec=sum(r['admitted'] and r['codec_v1_pass'] and r['mixed_line'] for r in allrows),tags=dict(Counter(t for r in allrows for t in r['line_tags'])),rejection_reasons=dict(Counter(t for r in allrows for t in r['rejection_reasons'])),confidence_policy='Google confidence gate is inapplicable to published human GT. Counts are content-rule admission plus shipped codec v1; no score fabricated.',google_reads=0,cost_usd=0,rows_sha256=sha(path),per_item={})
    for item in sorted({r['item'] for r in allrows}):
        rs=[r for r in allrows if r['item']==item];summary['per_item'][item]=dict(lines=len(rs),mixed=sum(r['mixed_line'] for r in rs),admitted=sum(r['admitted'] for r in rs),codec_admitted=sum(r['admitted'] and r['codec_v1_pass'] for r in rs))
    write(BASE/'receipts/ajax-summary.json',summary);print(json.dumps(summary,ensure_ascii=False,indent=2))
