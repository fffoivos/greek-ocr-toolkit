"""Small offline evidence fixtures for the T24b repository-capacity block."""
from collections import Counter
import json

import pyarrow as pa
import pyarrow.parquet as pq

from greekocr.harvest import openarchives as oa
from scripts.harvest.openarchives_preflight import identity_audit


def write_inputs(tmp_path,links,docs):
    parquet=tmp_path/'external_pdfs.parquet';jsonl=tmp_path/'doc_metadata.jsonl'
    pq.write_table(pa.Table.from_pylist(links),parquet)
    jsonl.write_text(''.join(json.dumps(r)+'\n' for r in docs))
    return parquet,jsonl


def link(repo,number):
    return dict(collection_slug=repo,edm_url=f'https://oa.invalid/edm/{repo}/{number}',
        pdf_links_json=json.dumps([f'https://pdf.invalid/{repo}/{number}.pdf']),
        external_link=f'https://pdf.invalid/{repo}/{number}',status_code=200,type='thesis')


def document(repo,pdf_repo,number):
    return dict(source_metadata=dict(collection_slug=repo,filename=str(number)+'.pdf',
        pdf_links_json=f'https://pdf.invalid/{pdf_repo}/{number}.pdf',metadata_json='{}'),
        pipeline_metadata=dict(download_success=True,ocr_success=True,filter='ok',is_empty=False,percentage_greek=90,
            mojibake_badness_score=None,greek_badness_score=None,page_count=100))


def test_cross_collection_exact_url_is_diagnostic_not_a_join(tmp_path):
    args=write_inputs(tmp_path,[link('actual',1)],[document('wrong','actual',1)])
    pool,_,summary=oa.build_pool(*args);audit=identity_audit(*args)
    assert len(pool)==1 and pool[0]['collection_slug']=='wrong' and summary['counts']['joined_metadata_rows']==1
    assert audit['counts']['unmatched']==1
    assert audit['counts']['unmatched_url_exists_in_other_collection']==1
    assert audit['examples'][0]['metadata_collection_slug']=='wrong'
    assert audit['examples'][0]['matching_external_collections']==['actual']


def test_explicit_edm_can_join_despite_collection_url_disagreement(tmp_path):
    row=document('wrong','actual',1);row['source_metadata']['edm_url']=link('actual',1)['edm_url']
    args=write_inputs(tmp_path,[link('actual',1)],[row])
    pool,_,_=oa.build_pool(*args);audit=identity_audit(*args)
    assert len(pool)==1 and pool[0]['join_method']=='url_informational'
    assert audit['counts']['explicit_edm_fields']==1 and audit['counts']['joined']==1
    assert audit['counts'].get('unmatched',0)==0 and not audit['examples']


def test_identity_diagnostics_only_cover_quality_and_page_pool(tmp_path):
    good=document('a','a',1);bad=document('b','b',1);bad['pipeline_metadata']['filter']='noise'
    args=write_inputs(tmp_path,[link('a',1),link('b',1)],[good,bad])
    audit=identity_audit(*args)
    assert audit['counts']['before_join']==audit['counts']['joined']==1
    assert set(audit['per_repository'])=={'a'}


def test_two_large_repositories_cannot_provide_130_capped_documents(tmp_path):
    links=[link(repo,n) for repo in ('a','b') for n in range(30)]
    docs=[document(repo,repo,n) for repo in ('a','b') for n in range(30)]
    pool,_,summary=oa.build_pool(*write_inputs(tmp_path,links,docs))
    draw=oa.stratified_draw(pool)
    assert len(pool)==60 and summary['capacity_at_10_per_repository']==len(draw)==20
    assert Counter(b['collection_slug'] for b in draw)=={'a':10,'b':10}
    assert draw==oa.stratified_draw(pool[::-1])


def test_multiple_external_url_rows_are_retained_only_as_evidence(tmp_path):
    a,b=link('a',1),link('b',1);b['pdf_links_json']=a['pdf_links_json']
    args=write_inputs(tmp_path,[a,b],[document('wrong','a',1)])
    audit=identity_audit(*args)
    assert audit['examples'][0]['matching_external_collections']==['a','b']
    assert len(audit['examples'][0]['external_matches'])==2
    assert len(oa.build_pool(*args)[0])==1
