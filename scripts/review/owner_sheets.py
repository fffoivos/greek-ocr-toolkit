"""Small offline spec-to-standard-sheet build entry point."""
import json
from pathlib import Path
from scripts.layout_paths import relocated
from greekocr.adjudicate.owner_sheet import render
ROOT=Path(__file__).resolve().parents[2]
def build(name):
    spec=json.loads((relocated(ROOT/'docs/owner_sheets')/name/'spec.json').read_text())
    output=ROOT/'artifacts/owner_sheets'/f'{name}.html'
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(render(spec['lines'],spec))
    return output
