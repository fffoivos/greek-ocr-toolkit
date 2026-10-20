import json
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq
import pytest
import build_c2 as b
P=Path(__file__).resolve().parent
@pytest.fixture
def codec():return b.codec_map(P/'evidence/wave2/codec/v2.1.json')
@pytest.mark.parametrize('label,expected',[
 ('Ἄνθρωπος ᾧ ᾠδή','ανθρωπος ω ωδη'),
 ('Άνθρωπος Μαΐου','ανθρωπος μαιου'),
 ('ÉCOLE naïve Straße ŒUVRE','ecole naive straße œuvre'),
 ('ЁЖИК ЙОГА ЇЇ Є Ґ','ежик иога іі є ґ'),
 ('123, — ! ? 45.6',''),
 ('  Α,  Β!   Γ  ','α β γ'),
 ('ΟΣ ος ς Σ','ος ος ς σ'),
 ('',''),
 ('A\tB\nC','abc'),
 ('ᾳ ῃ ῳ','α η ω')])
def test_projection(codec,label,expected):assert b.project(label,codec)==expected

def test_outside_codec(codec):
 with pytest.raises(ValueError,match='outside codec'):b.project('漢',codec)

def test_original_columns(codec,tmp_path):
 before=pa.table({'line_id':['a','b'],'pool_index':[9,2],'gt_nfd':['Ἄ','123'],'pixels':[b'\x00\xff',b'\x03'],'split':['train','train'],'codec_version':['v2.1']*2})
 after=b.augment(before,codec);p=tmp_path/'shard-00000.parquet';pq.write_table(after,p,use_compliant_nested_type=False);actual=pq.read_table(p);b.assert_original(before,actual)
 assert actual['base_label_ids'].to_pylist()==[[codec['α']],[]]
 assert actual['base_label'].to_pylist()==['α','']
 changed=actual.set_column(0,'line_id',pa.array(['b','a']))
 with pytest.raises(ValueError,match='original columns changed'):b.assert_original(before,changed)

def test_real_rows(codec,tmp_path):
 before=pq.read_table(P/'evidence/sample.parquet');assert len(before)>=1000
 after=b.augment(before,codec);p=tmp_path/'shard-00000.parquet';pq.write_table(after,p,use_compliant_nested_type=False);actual=pq.read_table(p);b.assert_original(before,actual)
 for r in actual.select(['gt_nfd','base_label','base_label_ids']).to_pylist():
  assert r['base_label']==b.project(r['gt_nfd'],codec)
  assert r['base_label_ids']==[codec[c] for c in r['base_label']]

def test_all_labels_audit():
 audit=b.read(P/'LABEL_AUDIT.json');assert audit['rows']==592180
 assert audit['projection_source_sha256']==b.projection_sha()
 assert all(len(x)==20 for x in audit['examples'].values())

def test_clone_pool(codec,tmp_path):
 source=tmp_path/'source';(source/'train').mkdir(parents=True)
 before=pa.table({'line_id':['a'],'gt_nfd':['ἄ'],'split':['train'],'codec_version':['v2.1']})
 pq.write_table(before,source/'train/shard-00000.parquet',use_compliant_nested_type=False);b.dump(source/'build_info.json',dict(shard_sha256=b.inventory(source),written={'train':1},codec_version='v2.1'))
 target=tmp_path/'derivative';receipt=b.clone_pool(source,target,P/'evidence/wave2/codec/v2.1.json')
 assert receipt['source_columns_equal'] and receipt['pool_index_equal']
 assert receipt['source_shard_inventory_sha256']==b.digest(b.inventory(source))
 b.assert_original(before,pq.read_table(target/'train/shard-00000.parquet'))
 with pytest.raises(FileExistsError):b.clone_pool(source,target,P/'evidence/wave2/codec/v2.1.json')

def test_reject_already_augmented(codec):
 before=pa.table({'line_id':['a'],'gt_nfd':['α']})
 with pytest.raises(ValueError,match='already has'):b.augment(b.augment(before,codec),codec)
