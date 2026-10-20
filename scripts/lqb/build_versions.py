"""Bind the five requested versions without fetching sf6."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from greekocr.labelfix.lqb import DEFAULT, PROJECTS, ROOT, sha256, rows, dump


def main():
    manifest=json.loads((DEFAULT/'truth_v1.manifest.json').read_text())
    w1=PROJECTS/'collect-v3-data/run/W1/features.jsonl'
    admission=PROJECTS/'greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_admissions/w1_masked_1d.jsonl'
    census=PROJECTS/'greek-ocr-toolkit-spellcheck/artifacts/sq1/census.json';sf=json.loads(census.read_text())
    n=sum(1 for _ in rows(w1));versions={}
    for name,field,parent in [('google_raw','text',None),('w1_label','label','google_raw')]:
        versions[name]=dict(path=str(w1),sha256=manifest['inputs'][str(w1)],population=dict(rows=n,definition='all local W1 feature rows'),parent=parent,text_field=field,id_field='id',status='local',read=f"features row['{field}']; id exact; no fallback to another text field")
    ru=ROOT/'artifacts/ru1/ru1_v1.jsonl'
    versions['ru1_v1']=dict(path=str(ru),sha256=sha256(ru),population=dict(rows=n,overlay_rows=sum(1 for _ in rows(ru)),definition='all w1_label rows; exact-id RU1 replacements'),parent='w1_label',overlay=True,text_field='label_ru1_v1',id_field='id',status='local',read="label_ru1_v1 on exact overlay id; otherwise w1_label (including non-Russian rows)")
    versions['w1_masked_1d']=dict(path=str(admission),sha256=sha256(admission),population=dict(rows=sum(1 for _ in rows(admission)),definition='only admission ids, label inherited unchanged from w1_label'),parent='w1_label',inherit_label=True,id_field='row_id',status='local',read='exact admission id membership then parent w1_label; missing parent id is not covered')
    release=PROJECTS/'greek-ocr-toolkit-spellcheck/docs/labelfix/spellcheck/clariden/L1R3_evidence/production_3680729_3680730/release/receipt.json'
    assert sha256(release)==sf['receipt_sha256']
    rel=json.loads((release.parent/'release/release_full.json').read_text())
    versions['sf6_release']=dict(path=sf['run'],sha256=rel['overlay_sha256'],status='remote_unfetched',population=dict(rows=sf['selected_lines'],definition='remote sf6 FULL selected lines; no local full label copy'),parent=None,text_field='label',id_field='line_id',read='FULL overlay label only for corrected/unchanged rows; HOLD needs bound source label, never composed_text; no inference from receipt summaries',receipt_sha256=sf['receipt_sha256'],receipt_local=str(release),selection_path=sf['selection'],selection_sha256=sf['selection_sha256'],policy_digest='6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406',local_label_copy=None)
    dump(DEFAULT/'versions.json',dict(schema='lqb-versions-v1',versions=versions))
    print({k:v['population'] for k,v in versions.items()})

if __name__=='__main__':main()
