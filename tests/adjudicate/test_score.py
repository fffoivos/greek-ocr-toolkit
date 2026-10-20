import ast
import math
from pathlib import Path
import numpy as np
import pytest
from greekocr.adjudicate.score import score, wilson, clopper_pearson_lb95


def test_s8_document_bootstrap_exact_port():
    source=Path.home()/'Projects/greek-ocr-toolkit-spellcheck-s8/scripts/labelfix/s8_score_truth.py'
    tree=ast.parse(source.read_text())
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('wilson','estimate')]
    ns=dict(np=np,math=math,REPS=4000)
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source),'exec'),ns)
    rows=[dict(line_id=f'b{doc}-p00001-l{line}',weight=float(1+line%3),a=(line+doc)%2,b=1)
          for doc in range(4) for line in range(5)]
    numer=lambda r:r['a'];denom=lambda r:r['b']
    assert score(rows,numer,denom)==ns['estimate'](rows,numer,denom,20261017)
    for successes in (0,1,100):
        assert wilson(successes/100,100)==ns['wilson'](successes/100,100)
    for r in rows:r['a']=1
    assert score(rows,numer,denom)['ci_method']=='Wilson-Kish'


def test_exact_bound_and_edge_cases():
    from greekocr.labelfix.validate import lb95
    for k,n in [(0,0),(0,20),(1,10),(9,10),(10,10),(90,100)]:
        assert clopper_pearson_lb95(k,n)==lb95(k,n)
    assert clopper_pearson_lb95(10,10)==pytest.approx(.05**.1)
    assert wilson(0,0) is None
    with pytest.raises(ValueError):wilson(float('nan'),2)
    with pytest.raises(ValueError):clopper_pearson_lb95(11,10)
    assert score([],lambda r:0,lambda r:0)['value'] is None
    assert score([dict(weight=1,line_id='x')],lambda r:0,lambda r:0)['ci'] is None
    with pytest.raises(ValueError):score([dict(weight=-1,line_id='x')],lambda r:0,lambda r:1)
