"""Inline review data into a page template. Usage: build_review_page.py DATA.json OUT.html [--template NAME.html]"""
import json, sys
from pathlib import Path
name = sys.argv[sys.argv.index('--template') + 1] if '--template' in sys.argv else 'review_page.html'
tpl = (Path(__file__).parent / name).read_text()
data = json.loads(Path(sys.argv[1]).read_text())
Path(sys.argv[2]).write_text(tpl.replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False).replace('</', '<\\/')))
