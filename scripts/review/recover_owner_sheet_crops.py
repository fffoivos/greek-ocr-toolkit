"""Preserve embedded owner-sheet rasters before source-checkout crop cleanup.

Run only against reviewed HTML artifacts. Existing cache entries must match.
Source path strings and card records remain unchanged; all writes are local.
"""
from __future__ import annotations

import base64
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from scripts.layout_paths import relocated


class EmbeddedCards(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
        self.cards = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'div' and attrs.get('class') == 'card':
            self.images = []
        if tag == 'img':
            self.images.append(attrs['src'])
        if tag == 'div' and attrs.get('class') == 'notes':
            self.cards[attrs.get('data-id', attrs['data-line'])] = list(self.images)


def main():
    root = Path(__file__).resolve().parents[2]
    dest = root/'artifacts/owner_sheets/v2/recovered_crops'
    dest.mkdir(exist_ok=True)
    index = {}
    for name in ('failure_modes_per_class', 'segmentation_failures'):
        spec = json.loads((relocated(root/f'docs/owner_sheets/{name}/spec.json')).read_text())
        parser = EmbeddedCards()
        html_path = root/f'artifacts/owner_sheets/v2/{name}.html'
        html_bytes = html_path.read_bytes()
        parser.feed(html_bytes.decode())
        for card in spec['lines']:
            # OS5 may be added to the spec before its first successful render.
            if card['doc_id'] not in parser.cards:
                continue
            uris = parser.cards[card['doc_id']]
            paths = [card['image']] + [z['image'] for z in card.get('zooms', [])]
            assert len(uris) == len(paths)
            for path, uri in zip(paths, uris):
                data = base64.b64decode(uri.split(',', 1)[1])
                cached = dest/(hashlib.sha256(path.encode()).hexdigest() + '.png')
                if cached.exists():
                    assert cached.read_bytes() == data
                else:
                    cached.write_bytes(data)
                entry = dict(cache=str(cached.relative_to(root)), sha256=hashlib.sha256(data).hexdigest())
                assert path not in index or index[path] == entry
                index[path] = entry
    (dest/'index.json').write_text(json.dumps(index, indent=2) + '\n')
    print(f'Preserved {len(index)} unique embedded rasters')


if __name__ == '__main__':
    main()
