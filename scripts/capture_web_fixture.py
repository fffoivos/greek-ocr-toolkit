"""One explicit Wikisource acquisition; all tests use saved inputs only."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.parse import quote

from greekocr.real.sources.web_sources import _PoliteHTTP, USER_AGENT


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', type=Path, required=True)
    args = parser.parse_args()
    url = 'https://el.wikisource.org/wiki/' + quote('Ύμνος εις την Ελευθερίαν'.replace(' ', '_'))
    args.dest.mkdir(parents=True, exist_ok=False)
    receipt = dict(schema='web-render-fixture-capture-v1', url=url,
                   fetched_at=datetime.now(timezone.utc).isoformat(), user_agent=USER_AGENT,
                   licence='work-specific; transcription CC-BY-SA-4.0; underlying work review required',
                   robots_respected=True, interval=1.0, final_url=None, status=None,
                   html_sha256=None, capture_status='skipped')
    try:
        response = _PoliteHTTP().get(url)
        receipt.update(final_url=response['url'], status=response['status'])
        if response['status'] != 200:
            raise ValueError('fixture HTTP ' + str(response['status']))
        body = response['body']
        if not any(mark.encode() in body for mark in ('Ἐ', 'ἀ', 'ὁ', 'Ἀ')):
            raise ValueError('response does not contain expected polytonic text')
        (args.dest / 'source.html').write_bytes(body)
        receipt.update(html_sha256=hashlib.sha256(body).hexdigest(), capture_status='captured')
    except (OSError, ValueError) as error:
        receipt['reason'] = str(error)
    (args.dest / 'capture_receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
