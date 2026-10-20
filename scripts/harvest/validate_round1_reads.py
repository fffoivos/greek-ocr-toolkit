#!/usr/bin/env python3
"""Network-free T17 scope, raw receipts, assignment/metric and review validation."""
from __future__ import annotations

import base64
from collections import Counter
import io
import json
from pathlib import Path
import re
import sys

from PIL import Image, ImageChops

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from scripts.harvest.round1_reads import ROOT, OUT, BULK, GOOGLE, ENGINES, DECADES, prepare, sha
from scripts.harvest.build_round1_reads import evaluate
from greekocr.harvest.round1_reads import cohort_summary, median_page, book_folder, numbered_image, page_text, review_html
from greekocr.harvest.readers import atomic, read_jsonl
from scripts.harvest.montage_controls import git_state, audit_git


def validate():
    plan = prepare()
    reservations = read_jsonl(GOOGLE/'budget.jsonl')
    expected = {(e,p['image_sha256']) for e in ENGINES for p in plan['pages']}
    actual = [(r['engine'],r['key']) for r in reservations]
    assert len(actual)==len(set(actual))==len(expected) and set(actual)==expected
    assert all(r['micro_usd']==1500 and r['state']=='reserved' for r in reservations)
    assert json.loads((GOOGLE/'budget.state.json').read_text())['calls']==len(actual)
    cost=json.loads((OUT/'cost_receipt.json').read_text())
    assert cost['calls_reserved']==len(actual) and cost['cost_usd']==len(actual)*.0015<=2
    assert cost['calls_by_engine']==dict(Counter(e for e,k in actual))
    for engine in ENGINES:
        ledger_path=GOOGLE/'docai/ledger.jsonl' if engine=='docai' else GOOGLE/'vision/adapter_receipts/ledger.jsonl'
        ledger=read_jsonl(ledger_path)
        assert len(ledger)==len({r['receipt_id'] for r in ledger})==plan['page_count']
        assert {r['crop_sha256'] for r in ledger}=={p['image_sha256'] for p in plan['pages']}
        assert all(r['status']=='ok' and r['cached'] is False and r['binding']==plan['bindings'][engine] for r in ledger)
        for r in ledger:
            assert r['raw_sha256']==sha(r['raw_json_path'])
        print(engine,'uncached successful ledger receipts',len(ledger),flush=True)
    records, summary=evaluate(plan,write=False)
    assert records==read_jsonl(OUT/'records.jsonl')
    assert summary==json.loads((OUT/'summary.json').read_text())
    assert len({r['id'] for r in records})==len(records)
    assert all(r['decade'] in DECADES for r in records)
    assert summary['overall']['tier1']+summary['overall']['tier2']+summary['overall']['tier3']==summary['overall']['lines']
    reviews=json.loads((OUT/'review_selection.json').read_text())
    assert len(reviews['pages'])==plan['page_count'] and len(reviews['books'])==len(summary['by_book'])
    page_by_id={p['id']:p for p in plan['pages']}
    paths=[]
    for p in plan['pages']:
        rows=[r for r in records if r['page_id']==p['id']]
        folder=BULK/'reads_d1_look'/str(p['decade'])/book_folder(p)
        path=folder/f"p{p['page']:04d}.png"
        assert path.with_suffix('.txt').read_text()==page_text(p,rows)
        with Image.open(path) as image:
            assert image.size==(p['width'],p['height']) and image.mode=='RGB'
            assert ImageChops.difference(image,numbered_image(REPO/p['image'],rows)).getbbox() is None
        paths.extend([path,path.with_suffix('.txt')])
    assert len(paths)==len(set(paths))==2*plan['page_count']
    assert len(list((BULK/'reads_d1_look').rglob('p*.png')))==plan['page_count']
    image_count=0
    for decade in DECADES:
        selected=[]
        books=sorted({p['book'] for p in plan['pages'] if p['decade']==decade}, key=lambda b:(summary['by_book'][b]['year'],summary['by_book'][b]['title'],b))
        for b in books:
            pages=[p for p in plan['pages'] if p['book']==b];rows=[r for r in records if r['book']==b]
            p=median_page(pages,rows)
            assert next(r for r in reviews['books'] if r['book']==b)['page_id']==p['id']
            selected.append((p,[r for r in rows if r['page_id']==p['id']],REPO/p['image']))
        html=(OUT/f'review_{decade}.html').read_text()
        assert html==review_html(decade,selected)
        assert html.count('data-book=')==len(books)
        assert html.count('data-line=')==sum(len(rows) for p,rows,path in selected)
        assert not re.search(r'<(?:script|link)\b',html,re.I)
        assert not re.search(r'src="(?!data:)',html)
        for encoded in re.findall('data:image/webp;base64,([A-Za-z0-9+/=]+)',html):
            with Image.open(io.BytesIO(base64.b64decode(encoded))) as image:
                assert image.width<=1200 and image.height<=1600 and image.format=='WEBP'
                image_count+=1
    audit=audit_git(json.loads((OUT/'git_before.json').read_text()),git_state())
    # Other owner sessions can commit concurrently. Observe their metadata
    # changes without rewriting Git or conflating them with T17 actions.
    assert (REPO/'.git/HEAD').read_text().strip()=='ref: refs/heads/main'
    validation=dict(status='passed',network_calls=0,pages=plan['page_count'],records=len(records),counted_lines=summary['overall']['lines'],
                    assignments_replayed=plan['page_count'],unique_reservations=len(actual),
                    native_overlay_pixels_verified=len(paths)//2,numbered_text_files_verified=len(paths)//2,
                    html_books_verified=len(summary['by_book']),inline_images_decoded=image_count,
                    cost_usd=cost['cost_usd'],git=audit,
                    git_policy='T17 invokes no Git commands and writes no .git files; concurrent metadata changes are observed')
    atomic(OUT/'validation.json',validation)
    print(json.dumps(validation,ensure_ascii=False))


if __name__=='__main__':
    validate()
