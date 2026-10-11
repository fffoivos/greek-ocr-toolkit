#!/usr/bin/env python3
"""Offline T12 artifact integrity and credit reconciliation; never makes HTTP calls."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from prototypes.harvest import google_failed_lines as g
from prototypes.harvest.transkribus_failed_lines import compare_rows, agreement


class Review(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[]
        self.cards=[]
        self.images=[]
        self.links=[]

    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.append(attrs['id'])
        if tag=='article':self.cards.append(attrs.get('id'))
        if tag=='img':self.images.append(attrs)
        if tag=='a':self.links.append(attrs.get('href',''))


def validate(out,passed_tests=None):
    out=out.resolve()
    root=out/'transkribus_failed_lines'
    groups={e:json.loads((out/(e+'_failed_lines')/'metrics.json').read_text()) for e in ('docai','vision','transkribus')}
    types=list(json.loads((root/'summary.json').read_text())['types'])
    types=[t for t in types if t!='control_owner_verified']
    for e,rows_for_engine in groups.items():
        g.summarise(rows_for_engine,types,engine_name={'docai':'Document AI','vision':'Cloud Vision','transkribus':'Transkribus'}[e])
    rows=groups['transkribus']
    receipt=json.loads((root/'receipt.json').read_text())
    comparison=json.loads((root/'comparison.json').read_text())
    pairs=compare_rows(groups,out)
    saved=json.loads((root/'three_engines.json').read_text())
    assert pairs==saved,'three-way metrics differ from raw responses'
    assert comparison['sources']['ALL']==agreement(pairs)
    for source in ('Anemi','Vouli'):
        assert comparison['sources'][source]==agreement([r for r in pairs if r['source']==source])
    assert len(rows)==469
    assert Counter(r['source'] for r in rows)==dict(Anemi=174,Vouli=295)
    ids={r['crop_id'] for r in rows}
    assert len(ids)==len(rows)
    assert all(ids=={r['crop_id'] for r in groups[e]} for e in ('docai','vision'))
    measured=[r for r in rows if r['status']=='ok']
    assert len(measured)==receipt['measured_crop_ids']
    unique={r['crop_sha256'] for r in measured}
    assert len(unique)==receipt['unique_measured_crop_sha256']
    assert comparison['rare_glyph_crops_transkribus']==sum(any(c in r['text'] for c in 'ϗȣϛϲϝϙϡ') for r in measured)
    assert json.loads((root/'characters.json').read_text())==g.characters_table(rows)
    for row in rows:
        assert g.sha256(Path(row['crop_path']))==row['crop_sha256'],'source image changed'
        if row['status']=='ok':
            envelope=json.loads(g.response_path(root,row,'transkribus').read_text())
            assert envelope['response']['job']['status']=='FINISHED'
            assert str(envelope['response']['job']['processId'])==envelope['request_id']
            assert envelope['binding']['model_id']==148525
            assert envelope['binding']['mode']=='single_line'
            assert envelope['credits_used']>=0
            assert envelope['credentials']=='environment credentials used'
    with (root/'three_engines.csv').open(newline='') as stream:
        csv_rows=list(csv.DictReader(stream))
    assert len(csv_rows)==len(rows) and {r['crop_id'] for r in csv_rows}==ids
    for csv_row,row in zip(csv_rows,pairs):
        assert csv_row['crop_id']==row['crop_id']
        for e in ('docai','vision','transkribus'):
            assert csv_row[e+'_text']==(row[e+'_text'] or '')
    review_path=out/'three_engines_review.html'
    parser=Review();parser.feed(review_path.read_text())
    assert len(parser.ids)==len(set(parser.ids)),'duplicate HTML IDs'
    assert not any(re.search(r'\s',x) for x in parser.ids),'whitespace in HTML IDs'
    assert len(parser.cards)==469 and set(parser.cards)==ids
    assert all(x.startswith('an-') for x in parser.cards[:174]),'Anemi is not first'
    assert all(not x.startswith('an-') for x in parser.cards[174:])
    by_id={r['crop_id']:r for r in rows}
    for im in parser.images:
        path=out/unquote(im['src'])
        row=by_id[path.stem]
        assert path.is_file() and g.sha256(path)==row['crop_sha256']
        assert (int(im['width']),int(im['height']))==(row['width_px'],row['height_px'])
    assert len(parser.images)==469
    for link in parser.links:
        if link.startswith('#'):assert unquote(link[1:]) in parser.ids
        elif '://' not in link:assert (out/unquote(link.split('#')[0])).is_file(),link
    assert receipt['credits_after']>=50
    completed=sum(p['credits_used'] for p in receipt['pages'])
    unassigned=-sum(p['creditValue'] for p in receipt['unassigned_charged_jobs'])
    assert completed==receipt['page_credit_total']
    assert completed+unassigned==receipt['reconciled_page_credit_total']
    assert completed+unassigned==receipt['credits_before']-receipt['credits_after']
    assert receipt['credits_reconciled']
    assert len({p['request_id'] for p in receipt['pages']})==len(receipt['pages'])
    assert receipt['calls']==sum(r['role']=='submit' for r in receipt['http_call_records'])
    assert len({r['call_id'] for r in receipt['http_call_records']})==receipt['http_calls']
    assert len(list((root/'responses').glob('*.json')))==len(unique)
    value=dict(status='passed',crop_ids=len(rows),measured_crop_ids=len(measured),
        unique_images=len(unique),raw_and_metrics_recomputed=True,source_and_review_image_hashes=True,
        all_local_links=True,anemi_first=True,credit_reconciliation=True,
        credits_used=receipt['credits_used'],network_calls=0,
        tests=dict(passed=passed_tests),browser_render='unverified: Firefox Computer Use denied; Playwright browser executable absent',
        native_crop_visual_checks=4)
    g.atomic_json(root/'validation.json',value)
    return value


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=g.DEFAULT_OUT)
    parser.add_argument('--passed-tests',type=int)
    args=parser.parse_args()
    print(json.dumps(validate(args.out,args.passed_tests),ensure_ascii=False))


if __name__=='__main__':main()
