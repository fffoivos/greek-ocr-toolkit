"""Local SR-B1 paths and serialization. Never imports source-worktree code."""
import hashlib
import json
from pathlib import Path
WORK = Path(__file__).resolve().parents[3]
ROOT = WORK/'artifacts/ru1'
PROJECTS = Path.home()/'Projects'
C1 = PROJECTS/'greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1'
EFF = C1/'efficiency'
RUN = PROJECTS/'collect-v3-data/run/W1/c1'
SCRATCH = Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad')
PACK_ROOT = SCRATCH/'sol_packs/ru1'
R2 = PROJECTS/'greek-ocr-toolkit-spellcheck-r2cards/docs/labelfix/spellcheck/R2/decks'
FIELDS = {'bsb':{'card_id','crop','google_text','word_scripts'}, 'yer':{'item_id','crop','masked_text','slots'}, 'owner39':{'card_id','word_image','line_image','anchor_index','anchor_base','options','extra_options'}}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p): return [json.loads(s) for s in Path(p).read_text().splitlines() if s.strip()]
def dump(p, obj):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def jsonl(p, data):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(''.join(json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n' for r in data))
def idfield(bed): return 'item_id' if bed=='yer' else 'card_id'
def itemfile(bed): return 'items.jsonl' if bed=='yer' else 'cards.jsonl'
