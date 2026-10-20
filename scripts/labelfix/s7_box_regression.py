"""Run the unmodified SF1 box instrument for every S7 candidate and note set."""
import json
from pathlib import Path
import subprocess
import sys


def main():
    base=Path('docs/records/labelfix/spellcheck');e=base/'S7_evidence'
    sets={'union':['owner_notes_review_v16_20261016.jsonl','owner_notes_examples_v10_20261016.jsonl'],
          'review':['owner_notes_review_v16_20261016.jsonl'],'examples':['owner_notes_examples_v10_20261016.jsonl']}
    outputs={}
    for variant in ('baseline','S1','S2','S3','accepted'):
        for label,notes in sets.items():
            path=e/f'boxes_S6_to_{variant}_{label}.json'
            p=subprocess.run([sys.executable,'-m','scripts.labelfix.box_regression',str(e/'saved_S6_boxes.json'),str(e/f'{variant}_boxes.json'),
                '--notes',*[str(base/n) for n in notes],'--out',str(path)],capture_output=True,text=True,check=True)
            outputs[variant+'_'+label]=json.loads(p.stdout)
        path=e/f'boxes_launch_to_{variant}.json'
        p=subprocess.run([sys.executable,'-m','scripts.labelfix.box_regression',str(e/'baseline_boxes.json'),str(e/f'{variant}_boxes.json'),
            '--notes',*[str(base/n) for n in sets['union']],'--out',str(path)],capture_output=True,text=True,check=True)
        outputs['launch_to_'+variant]=json.loads(p.stdout)
    (e/'box_summaries.json').write_text(json.dumps(outputs,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
