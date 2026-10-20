"""Score controls against sealed truths, including unresolved responses."""
from collections import Counter
from greekocr.numerics.combine_v2 import control_matches


def score(key, mapped, approved, dash_types=None):
    if dash_types is not None:
        from n1t_packs import typed_controls
        # Validate the external seal even when approved already contains typed truths.
        generic=[dict(r,truth="hyphen or dash") if r["truth"] in ("hyphen", "en dash", "em dash", "any dash") else dict(r) for r in approved]
        typed=typed_controls(generic,dash_types)
        if any(a["truth"] not in ("hyphen or dash",b["truth"]) for a,b in zip(approved,typed)):
            raise ValueError("approved/dash-type truth mismatch")
        approved=typed
    truths = {r['slot_id']: r['truth'] for r in approved}
    expected = {v['slot_id']: v['control_truth'] for v in key['items'].values()}
    if not key.get('calibration') or expected != truths:
        raise ValueError('calibration must contain every sealed control exactly once')
    if len(expected) != len(key['items']):
        raise ValueError('duplicate calibration slot')
    if len(truths)!=len(approved) or len(mapped['slots'])!=len(expected) or {r['item_id'] for r in mapped['slots']}!=set(key['items']) or len({r['slot_id'] for r in mapped['slots']})!=len(expected):
        raise ValueError('incomplete or duplicate mapped calibration')
    if any(key['items'][r['item_id']]['slot_id']!=r['slot_id'] for r in mapped['slots']):
        raise ValueError('mapped item/slot mismatch')
    matrix = {}; totals = Counter(); correct = Counter(); disagreements = []
    for row in mapped['slots']:
        truth = truths[row['slot_id']]
        prediction = row['meaning'] if row['status'] in ('ok', 'unreadable') else '<'+row['status']+'>'
        totals[truth] += 1
        matrix.setdefault(truth, Counter())[prediction] += 1
        correct[truth] += control_matches(truth, prediction)
        if not control_matches(truth, prediction):
            disagreements.append(dict(slot_id=row['slot_id'], item_id=row['item_id'], truth=truth,
                                      prediction=prediction, status=row['status']))
    return dict(items=sum(totals.values()), correct=sum(correct.values()),
                per_class={c: dict(total=totals[c], correct=correct[c], accuracy=correct[c]/totals[c]) for c in sorted(totals)},
                confusion_matrix=matrix, disagreements=disagreements,
                unexpected_ids=mapped['unexpected_ids'], context_status=mapped['context_status'])


def lead_gate(result):
    classes=result['per_class']
    raised=classes.get('raised dot',{})
    typed=sum(classes.get(c,{}).get('correct',0) for c in ('hyphen','en dash','em dash'))
    false_raised=sum(row.get('raised dot',0) for truth,row in result['confusion_matrix'].items() if truth!='raised dot')
    population={c:v['total'] for c,v in classes.items()}=={'raised dot':4,'baseline dot':21,'comma':23,'hyphen':14,'en dash':6,'em dash':5,'any dash':2,'nothing':7}
    checks=dict(complete_population=population,raised_4_of_4=raised.get('correct')==4,
                no_false_raised=false_raised==0,typed_dash_23_of_25=typed>=23,
                at_most_3_disagreements=len(result['disagreements'])<=3,
                no_unexpected_ids=not result['unexpected_ids'])
    return dict(status='PASS' if all(checks.values()) else 'HOLD',checks=checks,
                typed_dash_correct=typed,typed_dash_total=25,false_raised=false_raised)
