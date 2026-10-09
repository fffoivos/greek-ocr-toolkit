"""Compare part-two delivery with the frozen part-one table acceptance figures.

Run after rendering and after the offline acceptance/integration/score scripts.
No annotation or detector input is changed by this audit.
"""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'.astra/previous_round4_part1'
OUT=ROOT/'.astra/out'


def read(p):
    return json.loads(p.read_text())


def main():
    old=read(OLD/'acceptance/summary.json');new=read(OUT/'acceptance/summary.json')
    old_delivery=read(OLD/'acceptance/delivery-audit.json')
    new_delivery=read(OUT/'acceptance/delivery-audit.json')
    integration=read(OUT/'integration/summary.json')
    rows=[]
    for key in sorted(old):
        a,b=old[key],new[key]
        before=read(OLD/f'{key}.cells.json')['cells'];after=read(OUT/f'{key}.cells.json')['cells']
        signature=lambda rs:[(r['box_pixels'],r['box_page'],r['table_id'],r['cell_id']) for r in rs]
        table_signature=lambda rs:signature([r for r in rs if r['table_id'] is not None])
        old_coverage={(r['table'],r['cell'],r['element']):r['coverage'] for r in a['geometry']['omissions']}
        regressions=[]
        for r in b['geometry']['omissions']:
            prior=old_coverage.get((r['table'],r['cell'],r['element']),1.)
            if r['coverage']<prior-1e-10:
                regressions.append(dict(element=r['element'],old=prior,new=r['coverage']))
        bad={}
        def check(name,oldval,newval,higher_bad=True):
            if (newval>oldval if higher_bad else newval<oldval):
                bad[name]=dict(old=oldval,new=newval)
        check('crossing_pieces',len(a['geometry']['crossing_pieces']),len(b['geometry']['crossing_pieces']))
        check('admitted_annotation_elements',a['admitted_exactly_once'],b['admitted_exactly_once'],False)
        check('layout_invariant',int(a['layout_invariant']),int(b['layout_invariant']),False)
        previous_discovery={r['id']:r['maximum_extent_coverage'] for r in a['discovery']}
        for r in b['discovery']:
            check('discovery/'+r['id'],previous_discovery[r['id']],r['maximum_extent_coverage'],False)
        ia=old_delivery[key]['integration'];ib=new_delivery[key]['integration']
        for metric in ('missing_from_final_tables','duplicated_in_final_tables','wrong_owner_labels','ambiguous_input_pieces','unmatched_input_pieces'):
            check(metric,len(ia[metric]),len(ib[metric]))
        fa={(r['table'],r['mode'],r['variant']):r for r in a['frozen']}
        for r in b['frozen']:
            for metric in ('lost','duplicated','wrong_owner'):
                check(f'frozen/{r["table"]}/{r["mode"]}/{r["variant"]}/{metric}',fa[(r['table'],r['mode'],r['variant'])][metric],r[metric])
        rows.append(dict(key=key,all_piece_geometry_equal=signature(before)==signature(after),
                         table_piece_geometry_equal=table_signature(before)==table_signature(after),
                         current_pieces=len(after),old_pieces=len(before),
                         complete_elements=dict(old=sum(t['complete'] for t in a['geometry']['tables']),
                                                new=sum(t['complete'] for t in b['geometry']['tables'])),
                         element_coverage_regressions=regressions,acceptance_regressions=bad,
                         integration_status=integration[key].get('status'),
                         geometry=dict(old=a['geometry']['tables'],new=b['geometry']['tables']),
                         crossing_pieces=[len(a['geometry']['crossing_pieces']),len(b['geometry']['crossing_pieces'])],
                         final_missing=[len(ia['missing_from_final_tables']),len(ib['missing_from_final_tables'])],
                         final_wrong=[len(ia['wrong_owner_labels']),len(ib['wrong_owner_labels'])],
                         passed=not regressions and not bad and not integration[key].get('errors')
                           and integration[key].get('status')=='ConversionStatus.SUCCESS'))
    files=['acceptance/summary.json','acceptance/delivery-audit.json','integration/summary.json']
    result=dict(baseline_commit='376ab5d',pages=len(rows),passed=all(r['passed'] for r in rows),rows=rows,
                receipts={f:hashlib.sha256((OUT/f).read_bytes()).hexdigest() for f in files})
    (OUT/'table-preservation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    assert result['passed'],'Part-one table acceptance regression; see table-preservation.json'


if __name__=='__main__':
    main()
