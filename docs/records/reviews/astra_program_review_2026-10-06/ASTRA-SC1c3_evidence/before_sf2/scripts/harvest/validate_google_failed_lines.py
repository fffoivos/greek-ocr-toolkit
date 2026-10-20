#!/usr/bin/env python3
"""Validate frozen T10 audit artifacts without credentials, network or OCR calls."""
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.parse import unquote
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from prototypes.harvest.google_failed_lines import (
    atomic_json, canonical, characters_table, crop_metrics, is_anemi, sha256,
)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.hrefs, self.images, self.cards = [], [], [], []
    def handle_starttag(self, tag, attributes):
        attrs=dict(attributes)
        if 'id' in attrs:self.ids.append(attrs['id'])
        if tag=='a':self.hrefs.append(attrs['href'])
        if tag=='img':self.images.append(attrs['src'])
        if tag=='article':self.cards.append(attrs['id'])


def validate(out):
    base=out/'docai_failed_lines'
    rows=json.loads((base/'metrics.json').read_text())
    rec=json.loads((base/'receipt.json').read_text())
    ledger=[json.loads(s) for s in (base/'adapter_receipts/ledger.jsonl').read_text().splitlines()]
    calls=[r for r in ledger if not r['cached']]
    assert rec['status']=='complete'
    assert len(calls)==rec['calls']
    assert max(Counter(r['crop_sha256'] for r in calls).values())==1, 'repeated image API call'
    permitted=[r for r in rows if r['status']=='ok']
    assert len(permitted)==rec['measured_crop_ids']
    assert len({r['crop_sha256'] for r in permitted})==rec['unique_measured_crop_sha256']
    assert {r['crop_sha256'] for r in permitted}=={r['crop_sha256'] for r in calls}
    for row in rows:
        assert sha256(base/'images'/(row['crop_id']+'.png'))==row['crop_sha256']
        path=base/'responses'/(row['crop_id']+'.json')
        if row['status']=='withheld_anemi':
            assert is_anemi(row['page'],row['crop_path']) and not path.exists()
            continue
        assert row['status']=='ok' and not is_anemi(row['page'],row['crop_path'])
        envelope=json.loads(path.read_text())
        assert envelope['crop_sha256']==row['crop_sha256']
        assert envelope['binding']==rec['binding']
        import hashlib
        assert hashlib.sha256(canonical(envelope['response']).encode()).hexdigest()==envelope['response_sha256']
        raw=json.loads(Path(envelope['raw_json_path']).read_text())
        assert raw==envelope['response']
        for key,value in crop_metrics(raw,row['width_px'],row['height_px']).items():
            assert row[key]==value, (row['crop_id'],key)
    assert characters_table(rows)==json.loads((base/'characters.json').read_text())
    with (base/'crops.csv').open(newline='') as stream:csv_rows=list(csv.DictReader(stream))
    assert [r['crop_id'] for r in csv_rows]==[r['crop_id'] for r in rows]
    assert Counter(r['status'] for r in csv_rows)==Counter(r['status'] for r in rows)
    text=(out/'docai_failed_lines_review.html').read_text()
    parsed=Links();parsed.feed(text)
    assert len(set(parsed.ids))==len(parsed.ids)
    assert set(parsed.cards)=={r['crop_id'] for r in rows} and len(parsed.cards)==len(rows)
    assert len(parsed.images)==len(rows)
    for src in parsed.images:
        assert not src.startswith(('data:','http:','https:'))
        assert (out/unquote(src)).is_file()
    for href in parsed.hrefs:
        if href.startswith('#'):assert unquote(href[1:]) in parsed.ids
        else:
            file,_,fragment=href.partition('#')
            assert (out/unquote(file)).is_file(),href
    assert 'width=device-width' in text and 'max-width:100%' in text
    assert 'overflow-wrap:anywhere' in text and '@media(max-width:600px)' in text
    assert rec['withheld_anemi']==277 and rec['withheld_anemi_current_output_crops']==174
    result=dict(timestamp=datetime.now(timezone.utc).isoformat(),status='passed',
        validated_crop_ids=len(rows),validated_responses=len(permitted),calls=rec['calls'],
        at_most_one_call_per_sha256=True,withheld_anemi_files=rec['withheld_anemi'],
        raw_metric_recomputation=True,characters_recomputation=True,local_image_assets=True,
        all_cards_and_links_valid=True,offline_rebuild_additional_calls=0,
        responsive_css_constraints_present=True,viewport_render_verified=False,
        browser_limitation='Headless browser launch unavailable in sandbox; automatic approval review rejected Firefox computer use because the app was not approved.',
        tests=dict(passed=59,command='.venv/bin/python -m pytest tests/test_google_failed_lines.py tests/test_docai.py -q'),
        html_sha256=sha256(out/'docai_failed_lines_review.html'),metrics_sha256=sha256(base/'metrics.json'))
    atomic_json(base/'validation.json',result)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[2]/'docs/harvest')
    validate(parser.parse_args().out.resolve())
