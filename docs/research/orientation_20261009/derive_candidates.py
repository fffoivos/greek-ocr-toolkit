"""Score a two-hypothesis OCR fallback from actual four-way OCR measurements.

The choice of axis comes only from ink geometry, never the angle label. Costs
include that geometry plus the two measured Tesseract subprocess costs. This
is a derived evaluation, not a separately timed optimized implementation.
"""
from research_orientation import *
def main():
    gs={(r['id'],r['scope']):r for r in [json.loads(l) for l in (ROOT/'geometry.jsonl').read_text().splitlines()]}
    with (ROOT/'constrained_vote.jsonl').open('w') as f:
        for r in [json.loads(l) for l in (ROOT/'ocr_vote.jsonl').read_text().splitlines()]:
            g=gs[r['id'],r['scope']];axis=g['axis_cw'];indices=[axis//90,(axis+180)//90]
            ix=max(indices,key=lambda i:r['scores'][i]);pred=ix*90 if r['scores'][ix]>0 else None
            new={k:r[k] for k in ['id','scope','unit','kind','truth_cw']}
            new.update(pred_cw=pred,correct=pred==r['truth_cw'],axis_cw=axis,scores=[r['scores'][i] for i in indices],seconds=g['seconds']+sum(r['details'][i]['neural_seconds'] for i in indices),timing='derived two measured forwards + geometry; excludes PNG preprocessing')
            f.write(json.dumps(new)+'\n')
    print('Derived 148 constrained votes',flush=True)
if __name__=='__main__':main()
