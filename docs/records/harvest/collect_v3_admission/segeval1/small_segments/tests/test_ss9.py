"""SS9 rule, raw-text reference parity, key bytes, and baseline regression."""
from pathlib import Path
import sys
import pytest
SS=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(SS/'tools'))
import ss9_survivors as s

@pytest.mark.parametrize('text,w,h,role,reason',[
 ('7',20,10,'prose','single_character_cell'),('12',20,10,'prose',None),
 ('a.',20,10,'prose','single_character_cell'),('ab',20,10,'prose',None),
 ('...',20,10,'prose','single_character_cell'),
 ('abcdefghi',100,10,'prose','short_line'),('abcdefghij',100,10,'prose',None),
 ('abc',100,10,'headings_caps','short_line'),('abcd',100,10,'headings_caps',None),
 ('12',100,10,'numerics_tables',None),('7',100,10,'numerics_tables','numeric_shape'),
 ('1.234',100,10,'prose',None),('XIV.',100,10,'prose',None),
 ('ab',0,10,'prose','cell_status_unresolved'),('ab',None,10,'prose','cell_status_unresolved')])
def test_rule(text,w,h,role,reason):
 assert s.short_line_exclusion(dict(raw_text=text,width_px=w,height_px=h,primary_class=role))==reason

def test_numeric_parity_raw_bed_and_150():
 ref=s.reference_numeric();rows=s.s8.rows(SS/'samples.jsonl')
 bed=[r for r in rows if not r['control']]
 sample=[r for r in bed if r['stratum']=='inside_by_source']
 assert len(bed)==417 and len(sample)==150
 for r in bed+sample: assert s.numeric_grammar(r['raw_text'])==ref(r['raw_text'])
 # Also exercise separators, canonical roman and raw Unicode whitespace.
 for text in ['', ' ', 'I.', 'XIV)', 'iiii', 'IIII', '1\t2', '§2', 'a2', '²', '١٢']:
  assert s.numeric_grammar(text)==ref(text)

def test_v3_preserves_bytes_and_order():
 assert s.verify_key()==59002

def test_v3_matches_census_rule():
 census={r['row_id']:r for r in s.q1.read_rows(s.q1.BASE/s.q1.INPUTS[0]) if r['characters']<=8 and min(r['width_px'],r['height_px'])>0 and max(r['width_px'],r['height_px'])/min(r['width_px'],r['height_px'])<=6}
 for r in s.q1.read_rows(SS/'small_population_key.v3.jsonl.gz'):
  assert {k:r[k] for k in s.FIELDS}==s.additions(census[r['row_id']],r['gate_failed'])

def test_rule_off_empty_gate_exact_baseline():
 ref=s.s8.load(s.OUT/'RULE_OFF_EMPTY_GATE.json')
 one=s.s8.load(SS/'q1/q1.json');two=s.s8.load(SS/'q2/q2.json');three=s.s8.load(SS/'q3/q3.json')
 assert ref['Q1']['T4']==one['tables']['T4']
 assert ref['Q1']['T2']==one['tables']['T2']
 assert ref['Q1']['owner_unique']==one['metadata']['owner_unique_matched_census_lines']==362
 assert ref['Q2']==two['definitions']['D_rec']
 assert ref['Q3']['T8']==three['T8']
 assert ref['Q3']['n']==three['scope']['T8_n']==150
 assert ref['Q3']['pool_total']==three['scope']['T8_pool']
 assert ref['Q3']['bed_counts']['bed']['n']==three['scope']['bed']==417
 for row in three['T7']['overall']['class']:
  assert ref['Q3']['bed_counts']['bed']['classes'][row['value']]==row['n']

def test_survivor_pools_and_sample():
 r=s.s8.load(s.OUT/'Q3_R1.json')['admitted_gate']
 key=list(s.q1.read_rows(SS/'small_population_key.v3.jsonl.gz'))
 expected=dict(s.C.Counter(x['source'] for x in key if x['survivor'] and x['output_type']!='numeric'))
 assert r['source_pools']==expected
 assert r['pool_total']==sum(expected.values())
 for rows in r['T8'].values():
  assert sum(x['n'] for x in rows)==r['n']
  assert sum(x['weighted_share'] for x in rows)==pytest.approx(1)
  assert sum(x['estimated_pool_rows'] for x in rows)==pytest.approx(r['pool_total'])
