"""Reproduce the seven-file SEG10 suite in a receipted temporary layout view."""
from pathlib import Path
import json, os, subprocess
from prepare_view import prepare

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
NAMES = ('test_content_gate.py', 'test_line_pipeline.py', 'test_seg_gate.py',
         'test_seg_deskew.py', 'test_seg_curve.py', 'test_seg_small.py', 'test_integration_fixes.py')
if __name__ == '__main__':
    view = prepare()
    command = [str(ROOT.parent / 'greek-ocr-toolkit-sol-recut/.venv/bin/python'), '-B', '-m',
               'pytest', '-q', '-p', 'no:cacheprovider', *[str(view/'tests'/n) for n in NAMES]]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONPATH='.', GIT_OPTIONAL_LOCKS='0')
    (OUT/'tests_command.txt').write_text('PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. ' + ' '.join(command) + '\n')
    with (OUT/'tests.log').open('w') as log:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
    print((OUT/'tests.log').read_text())
    raise SystemExit(result.returncode)
