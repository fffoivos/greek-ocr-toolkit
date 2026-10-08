import json
from pathlib import Path
import subprocess
import unicodedata as ud
import numpy as np
import pytest
from PIL import Image
from greekocr.real import DocumentPartition, resolve_exclusions, adjudicate_lines, adjudicate_file, native_rows, import_dataset, import_real_shards, extract_lines, build_partition
from greekocr.annotate import script_class, word_tags, line_categories, load_word_tags
from greekocr.score import strict_cer, edit_distance, score_readings, summarize_predictions, write_readout
from greekocr.ops import file_sha256
from greekocr._vendor.train.mix import shard_inventory

@pytest.mark.parametrize('text,expected',[('ἅλφα','greek_poly'),('άλφα','greek_mono'),('α\u0300','greek_poly'),
 ('α\u0313','greek_poly'),('a α','greek_latin_cs'),('Русский','cyrillic'),('latin','latin'),('123',None)])
def test_script_rules(text,expected):assert script_class(text)==expected


def test_canonical_partition_and_exclusions(partition_file):
    p=DocumentPartition(partition_file)
    assert p.assign('book')==p.assign('mirror')==('work','train')
    assert p.assign('held')==('excluded',None)
    with pytest.raises(ValueError,match='unreviewed'):p.assign('not-reviewed')
    assert resolve_exclusions({'alias':'work'},['alias'])==['alias','work']
    with pytest.raises(ValueError,match='unresolved'):resolve_exclusions({'alias':'work'},['unknown'])

@pytest.mark.parametrize('mutation',['reviewed','unknown_exposure','missing_cohort','invalid_override'])
def test_partition_fail_closed(partition_file,mutation):
    obj=json.loads(partition_file.read_text())
    if mutation=='reviewed':obj['reviewed']=False
    if mutation=='unknown_exposure':obj['cohorts']['C1']['documents']=['unknown']
    if mutation=='missing_cohort':obj['cohorts']['C1']['documents']=[]
    if mutation=='invalid_override':obj['split_overrides']={'unknown':'train'}
    partition_file.write_text(json.dumps(obj))
    with pytest.raises(ValueError):DocumentPartition(partition_file)

@pytest.mark.parametrize('teacher,script,admitted',[(True,'greek_poly',True),(False,'greek_poly',False),(True,'cyrillic',False)])
def test_adjudication_two_blind_readings(line_record,teacher,script,admitted):
    row=dict(line_record,script_class=script);calls=[]
    def read(path):calls.append(path);return row['text']
    result=adjudicate_lines([row],read,read if teacher else None)[0]
    assert result['admitted']==admitted and all(isinstance(p,Path) for p in calls)
    assert len(calls)==(2 if teacher and script=='greek_poly' else 1)


def test_adjudication_disagreement_errors_rejected_rows(line_record):
    def fail(path):raise RuntimeError('recorded reader failure')
    row=adjudicate_lines([line_record],fail,lambda p:line_record['text'])[0]
    assert not row['admitted'] and row['adjudication']['errors']
    row=adjudicate_lines([line_record],lambda p:line_record['text'],lambda p:'different')[0]
    assert row['label_tier']=='flagged'
    calls=[];read=lambda p:calls.append(p) or line_record['text']
    row=adjudicate_lines([dict(line_record,admitted=False)],read,read)[0]
    assert not row['admitted'] and row['adjudication']['exact_agreement'] and len(calls)==2


def test_adjudication_files_receipt(tmp_path,line_record):
    records=tmp_path/'records.jsonl';records.write_text(json.dumps(line_record)+'\n')
    receipt=adjudicate_file(records,tmp_path/'adjudicated',lambda p:line_record['text'],lambda p:line_record['text'])
    assert receipt['admitted']==1 and receipt['records_sha256']==file_sha256(records) and not receipt['training']
    assert (tmp_path/'adjudicated/records.jsonl').is_file()


def test_native_pairs_bom_suffix_and_ambiguity(tmp_path):
    (tmp_path/'x.txt').write_text('\ufeffἅλφα\n');Image.new('L',(100,48),255).save(tmp_path/'x.png')
    (tmp_path/'docs.tsv').write_text('path\tsource_doc_id\nx.txt\tbook\n')
    spec=dict(format='pairs',text_suffix='.txt',image_suffix='.png',document_map='docs.tsv')
    # Keep the document map outside the text glob, as required by the native importer.
    rows=list(native_rows(spec,tmp_path));assert rows[0]['text']=='ἅλφα'
    Image.new('L',(100,48),255).save(tmp_path/'x.jpg')
    assert len(list(native_rows(spec,tmp_path)))==1
    spec.pop('image_suffix')
    with pytest.raises(ValueError,match='exactly one image'):list(native_rows(spec,tmp_path))


def test_dataset_import_rights_and_bound_crops(tmp_path,partition_file):
    root=tmp_path/'native';root.mkdir();(root/'a.gt.txt').write_text('\ufeffἅλφα\n')
    Image.new('L',(100,48),255).save(root/'a.png');(root/'docs.tsv').write_text('path\tsource_doc_id\na.gt.txt\tbook\n')
    spec=dict(format='pairs',root='native',document_map='docs.tsv',source_dataset='polyton_db',label_tier='gold',
      licence='CC-BY-4.0',source_url='https://example.org/recorded-source',licence_evidence='recorded licence',
      attribution='fixture',rights_reviewed=True)
    manifest=tmp_path/'datasets.json';manifest.write_text(json.dumps({'datasets':[spec]}))
    receipt=import_dataset(manifest,partition_file,tmp_path/'imported')
    assert receipt['admitted']==1 and not receipt['training_shards_written']
    spec['rights_reviewed']=False;manifest.write_text(json.dumps({'datasets':[spec]}))
    with pytest.raises(ValueError,match='rights'):import_dataset(manifest,partition_file,tmp_path/'bad')
    assert not (tmp_path/'bad').exists()


def test_real_shards_bind_word_tags(tmp_path,monkeypatch):
    out=tmp_path/'real'
    def run(command,**kwargs):
        assert command[1]=='import-real' and kwargs['timeout']==5
        out.mkdir();(out/'shard-0.parquet').write_bytes(b'fixture');(out/'word_tags.jsonl').write_text('{}\n')
        (out/'build_info.json').write_text(json.dumps(dict(kind='real',partition_id='p',
          shard_sha256=shard_inventory(out),word_tags_sha256=file_sha256(out/'word_tags.jsonl'))))
    monkeypatch.setattr(subprocess,'run',run)
    assert import_real_shards('records','crops','/worker/factory',out,partition='p',timeout=5)['kind']=='real'
    assert load_word_tags(out)==[{}]
    (out/'word_tags.jsonl').write_text('tampered')
    with pytest.raises(ValueError,match='sidecar'):load_word_tags(out)
    (out/'build_info.json').write_text('{}')
    assert load_word_tags(out) is None


def test_extract_missing_text_layer_recorded_pdf(tmp_path,partition_file):
    import pypdfium2 as pdfium
    pdf=pdfium.PdfDocument.new();page=pdf.new_page(100,100);pdf.save(tmp_path/'blank.pdf');page.close();pdf.close()
    sources=tmp_path/'sources.json';sources.write_text(json.dumps({'books':[dict(input_path='blank.pdf',
      source_doc_id='book',source_dataset='parliament',licence='CC-BY-4.0',rights_reviewed=True,
      source_url='https://example.org/fixture',licence_evidence='fixture',attribution='fixture')]}))
    result=extract_lines(sources,partition_file,tmp_path/'lines')
    assert result['admitted']==0 and result['page_failures']=={'no_text_layer':1}


def test_categories_preserve_unknown_metadata_and_word_tags():
    tags=line_categories(dict(text='ΑΒΓ ... 123 a α',width=1600))
    assert {'dotted_leaders','numerics','mixed_script','long_lines','footnote_size_unknown','font_style_unknown'}<=set(tags)
    assert word_tags('ἄλφα Latin')[0]['text_nfd']==ud.normalize('NFD','ἄλφα')
    assert word_tags('ἄλφα Latin')[1]['script_class']=='latin'
    assert 'footnote_size' in line_categories(dict(text='x',font_size_pt=8))


def test_strict_atoms_do_not_repair_prediction_order():
    reference='α\u0313\u0345';prediction='α\u0345\u0313'
    assert edit_distance(reference,prediction)==2 and strict_cer(reference,prediction)==pytest.approx(2/3)
    assert strict_cer('','')==0 and strict_cer('','x')==1

@pytest.mark.parametrize('gold,pred',[('ἅλφα','ἅλφα'),('ἅλφα',ud.normalize('NFD','ἅλφα'))])
def test_bakeoff_nfd_marks_and_homoglyphs(gold,pred):
    result=score_readings([dict(text=gold,prediction=pred,cohort='gold',script_class='greek_poly',crop_path='fixture')])
    assert result['overall']['cer']==0 and result['mark_f1']==1 and result['marks']['rough_breathing']['recall']==1
    result=score_readings([dict(text='Α',prediction='A',cohort='gold',script_class='greek_mono',crop_path='fixture')])
    assert result['greek_to_latin_homoglyphs']==1


def test_mark_fn_fp_f1_and_category_readout(tmp_path):
    result=score_readings([dict(text='ἅ',prediction='ά',cohort='gold',script_class='greek_poly',crop_path='fixture')])
    assert result['marks']['rough_breathing']['fn']==1 and result['mark_f1']==pytest.approx(2/3)
    assert result['marks']['acute']['f1']==1
    row=dict(gt='ΑΒΓ',prediction='ΑΒΓ',script_class='greek_mono',arm='f50',seed=0,instrument='real_test',crop_path='fixture')
    summary=summarize_predictions([row]);assert summary['by_category']['all_caps']['cer']==0
    path=tmp_path/'prediction.jsonl';path.write_text(json.dumps(row)+'\n')
    report=write_readout([path],tmp_path/'readout')
    assert report['results']['f50_s0/real_test']['by_category']['all_caps']['lines']==1
    with pytest.raises(ValueError,match='GT must'):summarize_predictions([dict(row,gt='ά')])


def test_partition_builder_binds_both_cohort_evidence(tmp_path):
    o5=tmp_path/'o5.json';o5.write_text(json.dumps(dict(document_assignment=dict(reserved=['test']))))
    c1=tmp_path/'c1.json';c1.write_text(json.dumps(dict(documents=['clean'])))
    mapping=tmp_path/'map.json';mapping.write_text(json.dumps(dict(documents={'test':'test-work','clean':'clean-work','train':'train-work'})))
    out=tmp_path/'partition.json';result=build_partition(o5,c1,mapping,out,reviewed=True)
    assert result['cohorts']['O5_E1_test']['source_sha256']==file_sha256(o5)
    assert DocumentPartition(out).assign('test')==('test-work',None)
    assert DocumentPartition(out).assign('clean')==('clean-work',None)


def test_native_xml_geometry_and_explicit_spaces(tmp_path):
    from greekocr._vendor.bench.o4b_import_datasets import xml_lines
    image=tmp_path/'page.png';Image.new('L',(100,100),255).save(image)
    xml=tmp_path/'page.xml';xml.write_text('''<alto><Layout><Page><PrintSpace><TextBlock>
<TextLine ID="l1" HPOS="10" VPOS="10" WIDTH="60" HEIGHT="20"><String CONTENT="άλφα"/><SP/><String CONTENT="beta"/></TextLine>
</TextBlock></PrintSpace></Page></Layout></alto>''')
    rows=list(xml_lines(xml,image,'alto'));assert rows[0]['text']=='άλφα beta' and rows[0]['image'].size==(60,20)
    xml.write_text(xml.read_text().replace('WIDTH="60"','WIDTH="600"'))
    with pytest.raises(ValueError,match='coordinate'):list(xml_lines(xml,image,'alto'))
