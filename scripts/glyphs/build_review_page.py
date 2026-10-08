"""Inline review data into the page template. Usage: build_review_page.py DATA.json OUT.html"""
import json, sys
from pathlib import Path
tpl = (Path(__file__).parent / 'review_page.html').read_text()
data = json.loads(Path(sys.argv[1]).read_text())
Path(sys.argv[2]).write_text(tpl.replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False).replace('</', '<\\/')))
