from pathlib import Path
import subprocess


def test_shipped_owner_javascript_runtime():
    root=Path(__file__).resolve().parents[2]
    result=subprocess.run(['/opt/homebrew/bin/node',str(Path(__file__).with_name('owner_sheet_runtime.cjs')),
                           str(root/'greekocr/adjudicate/owner_sheet.js')],capture_output=True,text=True)
    assert result.returncode==0,result.stdout+result.stderr
