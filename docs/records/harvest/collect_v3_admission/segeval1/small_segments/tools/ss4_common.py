"""SS4 paths; reuse the handover's serialization without copying its tools."""
import sys
from pathlib import Path
SS=Path(__file__).resolve().parents[1]
SR=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading')
sys.path.insert(0,str(SR/'tools'))
from common import sha, rows, dump, jsonl
PACK_ROOT=Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/348df0f7-fdb5-4e71-a9ef-0c7b4b33457e/scratchpad/ss_packs')
SCANNER=SR/'tools/scan_rollout.py'
SCANNER_SHA='e44f8c8a3c6d478c3dc299863478fcab210298f1c1429870d516c546f0f54ad1'
def check_scanner(path=SCANNER):
    if sha(path)!=SCANNER_SHA: raise ValueError('canonical scanner sha256 mismatch')
    return str(path)
def assignment(ctx,layout="type"):
    if layout not in ("type", "type2"): raise ValueError("unknown layout")
    key=__import__('json').loads((SS/f'q3/keys/{layout}.json').read_text())
    if ctx not in key['contexts']: raise ValueError('unknown context')
    return key['contexts'][ctx], key['items']
