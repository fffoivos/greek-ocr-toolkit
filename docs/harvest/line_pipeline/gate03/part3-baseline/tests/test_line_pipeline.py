"""Pipeline safety/integration tests using tiny metadata fixtures; no OCR/images."""
from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import pytest

from greekocr.harvest.line_pipeline import Pipeline, canonical, digest, identity, merge_edits, inventory
from greekocr.harvest.line_pipeline_adapters import adapt_legacy, byte_edits
from greekocr.harvest.line_pipeline_census import run, file_sha
from greekocr.harvest.line_pipeline_sources import canonicalize
from greekocr.harvest import admission as adm

NAMES=("segmentation","polytonic","cyrillic","numerics","dashes","content_repair")
VERSIONS={t:dict(version="0.1",digest=t) for t in NAMES}


def row(text="λόγος καὶ γράμματα", **kwargs):
    return dict(parent_id="parent",id="r1",source="bsb_poly1850",book_id="book",edition_id="edition",page_id="page",
        split="train",raw_text=text,crop_sha256="a"*64,primary_class="prose",script_class="greek_poly",**dict(dict(crop_bbox=[0,0,100,20]),**kwargs))


def expected(orthography="polytonic",scripts=None,languages=None,**extra):
    return dict(languages=languages or ["Greek"],scripts=scripts or ["greek"],orthography=orthography,provenance="fixture reviewed book metadata",**extra)


def segment(r, verdict="KEEP"):
    return dict(tool_version="0.1",binding=identity(r),raw_text_sha256=digest(r["raw_text"]),verdict=verdict,reason="frozen fixture")


def answer(r,t,target=None,status=None,**extra):
    from greekocr.harvest.line_pipeline import span_edits
    edits=[] if target is None else span_edits(r["raw_text"],target)
    return dict(tool=t,tool_version="0.1",tool_digest=t,binding=identity(r),raw_text_sha256=digest(r["raw_text"]),
        status=status or ("applied" if edits else "verified_no_change"),edits=edits,evidence={"qualified_fixture":True},**extra)


def engine(declaration=None, corrector=None, segmenter=segment, policy=None):
    return Pipeline(adm.load_codec(),VERSIONS,{"books":{"book":declaration or expected()}},policy or {},segmenter,corrector or (lambda r,t,e:answer(r,t)))


def test_length_is_final_and_can_be_rescued_by_a_qualified_edit():
    r=row("λόγος")
    calls=[]
    def correction(r,t,e):calls.append(t);return answer(r,t,"λόγος καὶ γράμματα")
    d=engine(corrector=correction).evaluate(r)
    assert d["disposition"]=="ADMIT" and calls==["polytonic"]
    assert [s["stage"] for s in d["stages"]]==["content_gate","segmentation","composition","final_eligibility"]


def test_segmentation_drop_does_not_run_readers():
    def bad(*a):raise AssertionError("reader invoked after segmentation drop")
    d=engine(corrector=bad,segmenter=lambda r:segment(r,"DROP")).evaluate(row())
    assert d["disposition"]=="DROP"
    assert all(v["status"]=="not_run_due_to_prior_exclusion" for v in d["routes"].values())


def test_uncertain_excludes_without_becoming_a_measured_defect():
    assert engine(segmenter=lambda r:segment(r,"UNCERTAIN")).evaluate(row())["disposition"]=="HOLD"


def test_all_relevant_routes_and_nonconflicting_composition():
    r=row("λόγος будуть 1.234 - γράμματα")
    declaration=expected(scripts=["greek","cyrillic"],languages=["Greek","Russian"],orthography="polytonic",orthographies={"cyrillic":"historical_russian"})
    observed=[]
    targets={"polytonic":"λόγος будуть 1.234 - γράμματα", "cyrillic":"λόγος будутъ 1.234 - γράμματα", "numerics":"λόγος будуть 1·234 - γράμματα"}
    def correct(r,t,e):
        observed.append(t)
        return answer(r,t,targets[t]) if t in targets else None
    d=engine(declaration,correct).evaluate(r)
    assert set(observed)=={"polytonic","cyrillic","numerics","dashes"}
    assert d["final_text"]=="λόγος будутъ 1·234 - γράμματα"
    assert d["routes"]["dashes"]["status"]=="tag_only"


def test_missing_result_is_not_no_change():
    d=engine(corrector=lambda *a:None).evaluate(row())
    assert d["disposition"]=="HOLD" and d["routes"]["polytonic"]["status"]=="required_evidence_unresolved"


def test_numeric_primary_role_survives_nonletter_script_class():
    r=row("1234")
    r.update(primary_class="numerics_tables",script_class="nonletter")
    d=engine(expected("monotonic"),lambda *a:None).evaluate(r)
    assert d["disposition"]=="ADMIT"
    assert d["routes"]["numerics"]["status"]=="verified_no_change"


def test_numeric_separator_uncertainty_is_not_auto_passed():
    r=row("1 . 234");r["primary_class"]="numerics_tables"
    assert engine(expected("monotonic"),lambda *a:None).evaluate(r)["disposition"]=="HOLD"


def test_legacy_tall_height_rule_is_absent():
    r=row();r.update(bbox=[0,0,300,200],page_median_line_height=10)
    assert engine().evaluate(r)["disposition"]=="ADMIT"


def test_raw_parent_is_preserved_and_normalization_is_audited():
    r=row(" λόγος\nκαὶ  γράμματα ")
    d=engine().evaluate(r)
    assert d["disposition"]=="ADMIT" and d["final_text"]=="λόγος καὶ γράμματα"
    assert d["raw_text_sha256"]==digest(r["raw_text"]) and d["normalization"]


def test_mixed_script_candidate_can_be_resolved_by_an_existing_tool():
    r=row("λόγoς καὶ γράμματα")
    def correct(r,t,e):return None if t=="content_repair" else answer(r,t,"λόγος καὶ γράμματα")
    d=engine(corrector=correct).evaluate(r)
    assert d["disposition"]=="DROP" and d["reasons"][0]==dict(reason="mixed_script_word", words=["λόγoς"])


def test_unrepaired_mixed_script_is_held():
    d=engine(corrector=lambda r,t,e:None if t=="content_repair" else answer(r,t)).evaluate(row("λόγoς καὶ γράμματα"))
    assert d["disposition"]=="DROP"


def test_script_route_created_after_composition_is_not_skipped():
    r=row("λόγος καὶ γράμματα")
    def correct(r,t,e):return answer(r,t,"λόγος καὶ γράμματα 1234") if t=="polytonic" else None
    d=engine(corrector=correct).evaluate(r)
    assert "numerics" in d["routes"] and d["routes"]["numerics"]["status"]=="verified_no_change"


def test_page_overrides_book_without_observed_text_inference():
    p=engine(expected("polytonic"));p.metadata["pages"]={canonical(["bsb_poly1850","book","page"]):expected("monotonic")}
    assert p.evaluate(row())["routes"]["polytonic"]["status"]=="not_applicable"


def test_profile_flags_require_independent_resolution():
    p=engine();p.metadata["profiles"]={"book":dict(reviewed=True,provenance="frozen independent book",sample_size=100,line_bounds={"digits":[0,0]})}
    d=p.evaluate(row("λόγος καὶ γράμματα 1234"))
    assert d["disposition"]=="HOLD" and d["reasons"][0]["reason"]=="profile_anomaly"


def test_unreviewed_profile_cannot_be_promoted():
    p=engine();p.metadata["profiles"]={"book":dict(line_bounds={"digits":[0,100]})}
    with pytest.raises(ValueError,match="reviewed"):p.evaluate(row())


def test_codec_failure_never_reverts_a_required_correction():
    p=engine(corrector=lambda r,t,e:answer(r,t,r["raw_text"]+" \u0378"))
    d=p.evaluate(row())
    assert d["disposition"] in {"DROP","HOLD"} and not d["admitted"]


def test_ctc_and_split_checks_are_final():
    r=row();r["ctc_output_steps"]=2
    assert any(x["reason"]=="ctc_infeasible" for x in engine().evaluate(r)["reasons"])
    r=row();r["split"]="unassigned"
    assert engine().evaluate(r)["disposition"]=="HOLD"


def test_train_heldout_edition_is_excluded():
    d=engine(policy={"heldout_editions":["edition"]}).evaluate(row())
    assert d["disposition"]=="DROP"


@pytest.mark.parametrize("change",["crop","raw","version","digest"])
def test_stale_tool_bindings_are_rejected(change):
    def correct(r,t,e):
        a=answer(r,t)
        if change=="crop":a["binding"]["crop_sha256"]="b"*64
        elif change=="raw":a["raw_text_sha256"]="b"*64
        elif change=="version":a["tool_version"]="0.99"
        else:a["tool_digest"]="stale"
        return a
    with pytest.raises(ValueError):engine(corrector=correct).evaluate(row())


def test_edit_overlap_identical_and_conflicting():
    a=dict(tool="a",edits=[dict(start=0,end=1,before="α",after="ἄ")])
    text,edits=merge_edits("αβ",[a,dict(a,tool="b")])
    assert text=="ἄβ" and edits[0]["tools"]==["a","b"]
    with pytest.raises(ValueError,match="overlap"):merge_edits("αβ",[a,dict(tool="b",edits=[dict(start=0,end=1,before="α",after="ἁ")])])


def test_utf8_parent_patches_and_boundaries():
    assert byte_edits("αβ",[dict(raw_byte_start=0,raw_byte_end=2,before="α",after="ἄ")])[0]["end"]==1
    with pytest.raises(UnicodeDecodeError):byte_edits("αβ",[dict(raw_byte_start=1,raw_byte_end=2,before="α",after="ἄ")])


def test_legacy_holds_and_candidate_releases_stay_held():
    r=row("будуть")
    release=dict(parent_id="parent",parent_manifest_sha256="parent_sha",sha256="artifact_sha",status="released")
    result=adapt_legacy(r,"cyrillic",dict(id="r1",label_parent="будуть",label="будутъ",status="hold",holds=["missing vote"]),release,VERSIONS)
    assert result["status"]=="required_evidence_unresolved" and not result["edits"]
    release["status"]="candidate_pre_audit"
    assert adapt_legacy(r,"cyrillic",dict(id="r1",label_parent="будуть",label="будутъ"),release,VERSIONS)["status"]=="proposal_only"


def test_source_adapters_keep_unassigned_and_unbound_rows():
    parent=dict(id="new",format="collect-v3-features")
    r=canonicalize(dict(id="source--book--s001-l0001",page_id="source--book--s001",source="elstat",text="1234",primary_class="numerics_tables",script_class="nonletter"),parent,{})
    assert r["split"]=="unassigned" and r["crop_identity_status"]=="unavailable" and r["raw_text"]=="1234"


def census_config(tmp_path, rows):
    data=tmp_path/"input.jsonl";data.write_text("".join(canonical(r)+"\n" for r in rows))
    versions=tmp_path/"versions.json";versions.write_text(canonical(dict(tools=VERSIONS)))
    metadata=tmp_path/"metadata.json";metadata.write_text(canonical(dict(books={"book":expected("monotonic")})))
    return dict(versions=str(versions),metadata=str(metadata),parents=[dict(id="parent",path=str(data),sha256=file_sha(data),rows=len(rows))],final_policy={},corrections=[])


def test_census_resume_and_full_input_inventory(tmp_path):
    a=row("1234");a.update(primary_class="numerics_tables",script_class="nonletter")
    b=dict(a,id="r2",raw_text="5678",crop_sha256="b"*64)
    config=census_config(tmp_path,[a,b]);calls=[]
    def factory():
        def observe(r):calls.append(r["id"]);return segment(r)
        return observe
    first=run(config,tmp_path/"run",execute=True,segmenter_factory=factory)
    assert first["input_rows"]==2 and first["dispositions"]["ADMIT"]==2 and first["complete"]
    run(config,tmp_path/"run",execute=True,segmenter_factory=factory)
    assert calls==["r1","r2"]
    db=sqlite3.connect(tmp_path/"run/ledger.sqlite")
    assert db.execute("SELECT count(*) FROM observations").fetchone()[0]==2


def test_census_crash_resume_and_explicit_infrastructure_errors(tmp_path):
    a=row("1234");a.update(primary_class="numerics_tables",script_class="nonletter")
    b=dict(a,id="r2",crop_sha256="b"*64)
    config=census_config(tmp_path,[a,b]);seen=[]
    def factory():
        def observe(r):
            seen.append(r["id"])
            if r["id"]=="r2":raise KeyboardInterrupt()
            return segment(r)
        return observe
    with pytest.raises(KeyboardInterrupt):run(config,tmp_path/"run",execute=True,segmenter_factory=factory)
    result=run(config,tmp_path/"run",execute=True,segmenter_factory=lambda:segment)
    assert result["dispositions"]["ADMIT"]==2 and result["complete"]
    changed=deepcopy(config);changed["final_policy"]={"numeric_min_digits":5}
    with pytest.raises(ValueError,match="changed"):run(changed,tmp_path/"run",execute=True,segmenter_factory=lambda:segment)


def test_census_evaluation_cohort_is_preserved_and_train_leakage_blocked(tmp_path):
    a=row("1234");a.update(primary_class="numerics_tables",script_class="nonletter")
    b=dict(a,id="test1",split="test")
    config=census_config(tmp_path,[a,b])
    result=run(config,tmp_path/"run",execute=True,segmenter_factory=lambda:segment)
    assert result["dispositions"]["ADMIT"]==1 and result["dispositions"]["DROP"]==1
    assert len((tmp_path/"run/evaluation_diagnostics.jsonl").read_text().splitlines())==1
    assert not (tmp_path/"run/admitted_train.jsonl").read_text()


def test_preflight_starts_no_work_and_writes_nothing(tmp_path):
    config=census_config(tmp_path,[row()])
    assert not run(config,tmp_path/"out")["processing_started"]
    assert not (tmp_path/"out").exists()


def test_census_infrastructure_error_is_incomplete_not_a_policy_drop(tmp_path):
    config=census_config(tmp_path,[row()])
    def failure(r):raise TimeoutError("fixture worker failure")
    result=run(config,tmp_path/"run",execute=True,segmenter_factory=lambda:failure)
    assert result["dispositions"]["INFRA_ERROR"]==1 and not result["complete"]
    assert not result["dispositions"].get("DROP")


def test_native_worker_timeout_is_hard_and_restarts_cleanly():
    import sys
    from greekocr.harvest.line_pipeline_native import NativeWorker
    worker=NativeWorker("unused","unused",timeout=.05)
    worker.command=[sys.executable,"-c","import sys,time;sys.stdin.readline();time.sleep(20)"]
    with pytest.raises(TimeoutError):worker({})
    assert worker.process is None


def test_missing_sparse_overlay_cannot_qualify_a_row(tmp_path):
    config=census_config(tmp_path,[row()])
    # Monotonic context does not schedule polytonic; change to polytonic.
    Path(config["metadata"]).write_text(canonical(dict(books={"book":expected()})))
    result=run(config,tmp_path/"run",execute=True,segmenter_factory=lambda:segment)
    assert result["dispositions"]["HOLD"]==1
    assert (tmp_path/"run/pending_polytonic.jsonl").read_text()


def test_legacy_positive_artifacts_reconstruct_literal_changes():
    root=Path(__file__).resolve().parents[1]
    secondary=root.parent/"greek-ocr-toolkit-secondary"
    spell=root.parent/"greek-ocr-toolkit-spellcheck"
    cases=[]
    for tool,path,parent_key,target_key in [
        ("cyrillic",secondary/"artifacts/ru1/ru1_v3_edits.jsonl","label_parent","label"),
        ("numerics",secondary/"artifacts/n1/n1_v1_w1.jsonl","parent_text","text")]:
        with path.open() as stream:
            record=next(r for line in stream if (r:=json.loads(line)).get("edits") and not r.get("holds"))
        cases.append((tool,record,record[parent_key],record[target_key],path))
    path=spell/"artifacts/sf7_rc1/release_edits_only_A.jsonl"
    with path.open() as stream:record=json.loads(next(stream))
    raw=record["text"].encode()
    for p in sorted(record["byte_patches"],key=lambda p:p["output_byte_start"],reverse=True):
        raw=raw[:p["output_byte_start"]]+p["before"].encode()+raw[p["output_byte_end"]:]
    assert digest(raw.decode())==record["parent_text_sha256"]
    cases.append(("polytonic",record,raw.decode(),record["text"],path))
    for tool,record,parent,target,path in cases:
        r=row(parent);r["id"]=record.get("id",record.get("line_id"))
        release=dict(parent_id="parent",parent_manifest_sha256="fixture parent",sha256=file_sha(path),status="released")
        a=adapt_legacy(r,tool,record,release,VERSIONS)
        assert a["status"]=="applied" and merge_edits(parent,[a])[0]==target


def test_exact_crop_duplicate_count_is_not_inflated(tmp_path):
    a=row("1234");a.update(primary_class="numerics_tables",script_class="nonletter")
    config=census_config(tmp_path,[a,dict(a,id="duplicate")])
    result=run(config,tmp_path/"run",execute=True,segmenter_factory=lambda:segment)
    assert result["dispositions"]["ADMIT"]==1 and result["dispositions"]["DROP"]==1
    repeated=run(config,tmp_path/"run",execute=True,segmenter_factory=lambda:segment)
    assert repeated["dispositions"]==result["dispositions"]


def test_missing_native_crop_is_explicit_unavailable_and_retryable(tmp_path):
    a=row("1234");a.update(primary_class="numerics_tables",script_class="nonletter")
    config=census_config(tmp_path,[a])
    def missing(r):raise FileNotFoundError("fixture crop")
    first=run(config,tmp_path/"run",execute=True,segmenter_factory=lambda:missing)
    assert first["dispositions"]["HOLD"]==1 and first["segmentation_availability"]["unavailable"]==1
    second=run(config,tmp_path/"run",execute=True,retry_holds=True,segmenter_factory=lambda:segment)
    assert second["dispositions"]["ADMIT"]==1


# Astra review regressions: all fixtures below are metadata or tiny fake processes.
def test_composition_cannot_reuse_a_numeric_negative_for_new_separator():
    r=row("λόγος καὶ γράμματα 1234")
    def correct(r,t,e):
        if t=="polytonic":return answer(r,t,"λόγος καὶ γράμματα 1.234")
        return None
    d=engine(corrector=correct).evaluate(r)
    assert d["disposition"]=="HOLD"
    assert d["routes"]["numerics"]["obligation"]["composed_text"]==d["final_text"]


def test_unrelated_edit_does_not_invalidate_numeric_coverage():
    r=row("λογος καὶ γράμματα 1.234")
    def correct(r,t,e):
        if t=="polytonic":return answer(r,t,"λόγος καὶ γράμματα 1.234")
        if t=="numerics":return answer(r,t,"λογος καὶ γράμματα 1·234")
    assert engine(corrector=correct).evaluate(r)["disposition"]=="ADMIT"


def test_final_profile_is_checked_and_resolution_binds_composed_text():
    from greekocr.harvest.line_pipeline import profile_issues
    profiles={"book":dict(reviewed=True,provenance="independent",sample_size=100,line_bounds={"digits":[0,0]})}
    target="λόγος καὶ γράμματα 1234"
    scope=digest(canonical(dict(text_sha256=digest(target),issues=profile_issues(row(),inventory(target,adm.load_codec()),{"profiles":profiles}),profiles=profiles)))
    calls=[]
    def correct(r,t,e):
        calls.append(t)
        if t=="polytonic":return answer(r,t,target)
        if t=="content_repair":
            a=answer(r,t);a["evidence"]["profile_resolution_sha256"]=scope;return a
    p=engine(corrector=correct);p.metadata["profiles"]=profiles
    assert p.evaluate(row())["disposition"]=="ADMIT" and "content_repair" in calls
    def stale(r,t,e):
        a=correct(r,t,e)
        if t=="content_repair":a["evidence"]["profile_resolution_sha256"]="stale"
        return a
    p.corrector=stale
    assert p.evaluate(row())["disposition"]=="HOLD"


def test_legacy_producer_is_preserved_and_manifest_mismatch_rejected():
    r=row("будуть")
    record=dict(id="r1",label_parent="будуть",label="будутъ",policy_digest="old-policy",source_job="job1")
    release=dict(parent_id="parent",parent_manifest_sha256="parent_sha",sha256="artifact_sha",status="released",producer={"policy_digest":"old-policy"})
    a=adapt_legacy(r,"cyrillic",record,release,VERSIONS)
    assert a["evidence"]["producer"]["policy_digest"]=="old-policy"
    assert a["evidence"]["original_record_sha256"]==digest(canonical(record))
    release["producer"]["policy_digest"]="wrong"
    with pytest.raises(ValueError,match="producer mismatch"):adapt_legacy(r,"cyrillic",record,release,VERSIONS)


def artifact_fixture(tmp_path,r,result,status="released"):
    from greekocr.harvest.line_pipeline_census import Ledger,ArtifactCorrector
    ledger=Ledger(tmp_path/"ledger.sqlite",{"fixture":True});ledger.register(r,adm.load_codec());ledger.db.commit()
    path=tmp_path/"correction.jsonl";path.write_text(canonical(result)+"\n")
    release=dict(parent_id="parent",parent_manifest_sha256="parent_sha",sha256=file_sha(path),path=str(path),tool=result["tool"],format="line-tool-result-v1",status=status)
    loader=ArtifactCorrector(ledger,VERSIONS,{"parent":"parent_sha"});loader.load(release)
    return ledger,loader,release


def test_canonical_artifact_uses_bound_id_and_candidate_dash_cannot_bypass(tmp_path):
    r=row("λόγος καὶ γράμματα -")
    ledger,loader,_=artifact_fixture(tmp_path,r,answer(r,"dashes",status="tag_only"),"candidate_pre_audit")
    assert loader(r,"dashes",expected())["status"]=="proposal_only"
    assert ledger.db.execute("SELECT id FROM corrections").fetchone()[0]=="r1"


@pytest.mark.parametrize("tool,before,after",[("cyrillic","б","ь"),("numerics","1","2")])
def test_canonical_artifacts_cannot_exceed_qualified_tool_scope(tmp_path,tool,before,after):
    r=row(before)
    with pytest.raises(ValueError,match="exceeds qualified"):
        artifact_fixture(tmp_path,r,answer(r,tool,after))


def test_tag_only_is_restricted_to_dash_tagger():
    with pytest.raises(ValueError,match="tag_only"):
        engine(corrector=lambda r,t,e:answer(r,t,status="tag_only")).evaluate(row())


def test_generation_is_incomplete_if_dedup_crashes(tmp_path,monkeypatch):
    from greekocr.harvest.line_pipeline_census import Ledger
    r=row("1234");r.update(primary_class="numerics_tables",script_class="nonletter")
    config=census_config(tmp_path,[r]);out=tmp_path/"run"
    original=Ledger.deduplicate
    def crash(self):raise RuntimeError("dedup crash")
    monkeypatch.setattr(Ledger,"deduplicate",crash)
    with pytest.raises(RuntimeError,match="dedup crash"):run(config,out,execute=True,segmenter_factory=lambda:segment)
    progress=json.loads((out/"progress.json").read_text())
    assert not progress["complete"] and progress["dispositions"]["ADMIT"]==1
    monkeypatch.setattr(Ledger,"deduplicate",original)
    assert run(config,out,execute=True,segmenter_factory=lambda:segment)["complete"]


def test_retry_invalidates_previous_publication_before_changed_rows(tmp_path,monkeypatch):
    from greekocr.harvest.line_pipeline_census import Ledger
    r=row("1234");r.update(primary_class="numerics_tables",script_class="nonletter")
    config=census_config(tmp_path,[r]);out=tmp_path/"run"
    def missing(r):raise FileNotFoundError("fixture missing crop")
    first=run(config,out,execute=True,segmenter_factory=lambda:missing)
    assert first["complete"]
    def crash(self,*args):raise RuntimeError("export crash")
    monkeypatch.setattr(Ledger,"export",crash)
    with pytest.raises(RuntimeError,match="export crash"):
        run(config,out,execute=True,retry_holds=True,segmenter_factory=lambda:segment)
    current=json.loads((out/"CURRENT.json").read_text())
    assert current["status"]=="in_progress" and current["generation"]>first["generation"]
    assert not (out/"summary.json").exists()
    assert not json.loads((out/"progress.json").read_text())["complete"]


def test_export_files_share_one_immutable_generation(tmp_path):
    r=row("1234");r.update(primary_class="numerics_tables",script_class="nonletter")
    out=tmp_path/"run";summary=run(census_config(tmp_path,[r]),out,execute=True,segmenter_factory=lambda:segment)
    current=json.loads((out/"CURRENT.json").read_text())
    assert current["status"]=="completed" and file_sha(current["summary_path"])==current["summary_sha256"]
    for info in summary["outputs"].values():
        assert Path(info["path"]).parent.name==summary["export_id"] and file_sha(info["path"])==info["sha256"]
    decision=json.loads((out/"decisions.jsonl").read_text())
    assert decision["run_binding_sha256"]==summary["run_binding_sha256"] and decision["toolchain_versions"]


def test_native_worker_partial_line_obeys_deadline_and_restarts():
    import sys,time
    from greekocr.harvest.line_pipeline_native import NativeWorker
    worker=NativeWorker("unused","unused",timeout=.05)
    worker.command=[sys.executable,"-c","import sys,time;sys.stdin.readline();sys.stdout.write('{');sys.stdout.flush();time.sleep(.5)"]
    started=time.monotonic()
    with pytest.raises(TimeoutError):worker({})
    assert time.monotonic()-started<.4 and worker.process is None
    worker.command=[sys.executable,"-c", "import sys,json;sys.stdin.readline();print(json.dumps(dict(ok=True,result=dict(fixture=1))),flush=True)"]
    worker.timeout=2
    try:assert worker({})=={"fixture":1}
    finally:worker.close()


def test_native_worker_malformed_protocol_is_closed():
    import sys
    from greekocr.harvest.line_pipeline_native import NativeWorker
    worker=NativeWorker("unused","unused",timeout=2)
    worker.command=[sys.executable,"-c","import sys;sys.stdin.readline();print('invalid',flush=True)"]
    with pytest.raises(ValueError):worker({})
    assert worker.process is None



def test_progress_summary_uses_counters_without_reading_decision_payloads(tmp_path):
    from greekocr.harvest.line_pipeline_census import Ledger
    ledger=Ledger(tmp_path/"ledger.sqlite",{"fixture":True})
    r=row();ledger.register(r,adm.load_codec());ledger.save_decision(r,engine().evaluate(r))
    statements=[];ledger.db.set_trace_callback(statements.append)
    assert ledger.summary(detailed=False)["dispositions"]["ADMIT"]==1
    assert not any("FROM observations" in sql or "FROM decisions" in sql for sql in statements)



def test_export_commit_failure_cannot_report_complete(tmp_path,monkeypatch):
    from greekocr.harvest import line_pipeline_census as census
    r=row("1234");r.update(primary_class="numerics_tables",script_class="nonletter")
    config=census_config(tmp_path,[r]);out=tmp_path/"run";original=census.atomic_json
    def failure(path,value):
        if Path(path).name=="CURRENT.json" and value.get("status")=="completed":raise RuntimeError("commit crash")
        return original(path,value)
    monkeypatch.setattr(census,"atomic_json",failure)
    with pytest.raises(RuntimeError,match="commit crash"):run(config,out,execute=True,segmenter_factory=lambda:segment)
    assert not json.loads((out/"progress.json").read_text())["complete"]
    monkeypatch.setattr(census,"atomic_json",original)
    assert run(config,out,execute=True,segmenter_factory=lambda:segment)["complete"]



def test_explicit_canonical_holds_survive_success_status(tmp_path):
    r=row();a=answer(r,"polytonic");a["holds"]=["missing second reader"]
    ledger,loader,_=artifact_fixture(tmp_path,r,a)
    assert loader(r,"polytonic",expected())["status"]=="required_evidence_unresolved"
    assert engine(corrector=lambda *args:a).evaluate(r)["disposition"]=="HOLD"


def test_ru1_rejects_internal_soft_sign_in_both_formats(tmp_path):
    from greekocr.harvest.line_pipeline import validate_result
    r=row("сильный русский текст");target="силъный русский текст"
    a=answer(r,"cyrillic",target)
    with pytest.raises(ValueError,match="word-final"):artifact_fixture(tmp_path,r,a)
    release=dict(parent_id="parent",parent_manifest_sha256="parent_sha",sha256="artifact_sha",status="released")
    legacy=adapt_legacy(r,"cyrillic",dict(id="r1",label_parent=r["raw_text"],label=target),release,VERSIONS)
    with pytest.raises(ValueError,match="word-final"):validate_result(legacy,r,"cyrillic",VERSIONS)


@pytest.mark.parametrize("language,orthography",[("Serbian","historical_russian"),("Russian","modern"),("Cyrillic","historical_russian")])
def test_ru1_requires_russian_language_and_historical_orthography(language,orthography):
    r=row("будуть русский текст")
    def correct(r,t,e):return answer(r,t,"будутъ русский текст")
    d=engine(expected(orthography,scripts=["cyrillic"],languages=[language]),correct).evaluate(r)
    assert d["disposition"]=="HOLD" and not d["admitted"]


def test_qualified_ru1_word_final_historical_russian_is_allowed():
    r=row("будуть русский текст")
    d=engine(expected("historical_russian",scripts=["cyrillic"],languages=["Russian"]),lambda r,t,e:answer(r,t,"будутъ русский текст")).evaluate(r)
    assert d["disposition"]=="ADMIT"


def test_parallel_census_matches_single_worker_and_preserves_order(tmp_path):
    import threading
    a=row('1234');a.update(primary_class='numerics_tables',script_class='nonletter')
    rows=[dict(a,id=f'r{i:02}',crop_sha256=digest(str(i))) for i in range(12)]
    config=census_config(tmp_path,rows)
    single=run(config,tmp_path/'single',execute=True,segmenter_factory=lambda:segment)
    config['native_workers']=4
    barrier=threading.Barrier(4);instances=[]
    class Worker:
        def __init__(self):instances.append(self)
        def __call__(self,r):barrier.wait(timeout=2);return segment(r)
    parallel=run(config,tmp_path/'parallel',execute=True,segmenter_factory=Worker)
    assert single['dispositions']==parallel['dispositions'] and parallel['complete']
    def decisions(path):
        result=[json.loads(x) for x in path.read_text().splitlines()]
        for d in result:d.pop('run_binding_sha256')
        return result
    assert decisions(tmp_path/'single/decisions.jsonl')==decisions(tmp_path/'parallel/decisions.jsonl')
    assert len(instances)==4
    runtime=json.loads((tmp_path/'parallel/runtime.json').read_text())
    assert runtime['native_attempts']==12 and runtime['native_workers']==4


@pytest.mark.parametrize('prefetch_factor',[1,2,8,16,64])
def test_parallel_prepare_stays_on_coordinator_and_queue_is_bounded(prefetch_factor):
    import threading
    from greekocr.harvest.line_pipeline_parallel import NativePool
    caller=threading.get_ident();seen=[];completed=[]
    class Worker:
        def __call__(self,r):
            assert threading.get_ident()!=caller
            completed.append(r);return r
    def prepare(r):
        assert threading.get_ident()==caller
        seen.append(r);return None
    pool=NativePool(Worker,3,prefetch_factor)
    try:
        total=max(100,3*prefetch_factor+10)
        output=pool.ordered(range(total),prepare)
        first=next(output)
        assert len(seen)==3*prefetch_factor and first[0]==0
        rest=list(output)
        assert [first[0]]+[i for i,_ in rest]==list(range(total))
    finally:pool.close()


@pytest.mark.parametrize('factor',[0,65,True,2.5])
def test_invalid_prefetch_bound_is_rejected(factor):
    from greekocr.harvest.line_pipeline_parallel import NativePool
    with pytest.raises(ValueError,match='native_prefetch_factor'):NativePool(lambda:None,2,factor)


@pytest.mark.parametrize('workers,factor',[(64,64),(256,16)])
def test_global_pending_limit_accepts_boundary_without_starting_workers(workers,factor):
    from greekocr.harvest.line_pipeline_parallel import NativePool
    pool=NativePool(lambda:None,workers,factor)
    try:assert not pool.instances
    finally:assert pool.close()==[]


def test_global_pending_limit_rejects_excess_window():
    from greekocr.harvest.line_pipeline_parallel import NativePool
    with pytest.raises(ValueError,match='4096'):NativePool(lambda:None,128,64)


def test_lookahead_keeps_work_available_behind_a_straggler():
    import threading
    from greekocr.harvest.line_pipeline_parallel import NativePool
    release=threading.Event();all_fast=threading.Event();prepared=[];completed=[];output=[];errors=[]
    class Worker:
        def __call__(self,i):
            if i==0:assert release.wait(3)
            else:
                completed.append(i)
                if len(completed)==7:all_fast.set()
            return i
    pool=NativePool(Worker,2,4)
    def consume():
        try:output.extend(i for i,_ in pool.ordered(range(12),lambda i:prepared.append(i)))
        except BaseException as exc:errors.append(exc)
    thread=threading.Thread(target=consume);thread.start()
    try:
        assert all_fast.wait(2)
        assert len(prepared)==8 and not output
    finally:release.set();thread.join(3);pool.close()
    assert not errors and output==list(range(12))


def test_parallel_infrastructure_failure_does_not_become_drop(tmp_path):
    a=row('1234');a.update(primary_class='numerics_tables',script_class='nonletter')
    rows=[dict(a,id=str(i),crop_sha256=digest(str(i))) for i in range(5)]
    config=census_config(tmp_path,rows);config['native_workers']=3
    def observe(r):
        if r['id']=='2':raise TimeoutError('one failed worker request')
        return segment(r)
    result=run(config,tmp_path/'run',execute=True,segmenter_factory=lambda:observe)
    assert result['dispositions']['ADMIT']==4 and result['dispositions']['INFRA_ERROR']==1 and not result['complete']


def test_unbound_crop_never_starts_native_work(tmp_path):
    a=row('1234');a.update(crop_identity_status='unavailable',primary_class='numerics_tables',script_class='nonletter')
    config=census_config(tmp_path,[a]);config['native_workers']=4
    def factory():raise AssertionError('unbound crop scheduled')
    result=run(config,tmp_path/'run',execute=True,segmenter_factory=factory)
    assert result['dispositions']['HOLD']==1
    assert json.loads((tmp_path/'run/runtime.json').read_text())['native_attempts']==0


@pytest.mark.parametrize('workers',[0,257,True,2.5])
def test_native_pool_rejects_invalid_worker_count(workers):
    from greekocr.harvest.line_pipeline_parallel import NativePool
    with pytest.raises(ValueError,match='native_workers'):NativePool(lambda:None,workers)



def test_pool_cleanup_attempts_every_worker():
    from greekocr.harvest.line_pipeline_parallel import NativePool
    closed=[]
    class Worker:
        def __init__(self,n):self.n=n
        def close(self):
            closed.append(self.n)
            if self.n==0:raise RuntimeError('cleanup fixture')
    pool=NativePool(lambda:None,2);pool.instances=[Worker(0),Worker(1)]
    errors=pool.close()
    assert closed==[0,1] and len(errors)==1


def test_census_cleanup_failure_preserves_progress_and_primary_error(tmp_path,monkeypatch):
    from greekocr.harvest.line_pipeline_census import Ledger
    r=row('1234');r.update(primary_class='numerics_tables',script_class='nonletter')
    config=census_config(tmp_path,[r]);out=tmp_path/'run'
    class Worker:
        def __call__(self,r):return segment(r)
        def close(self):raise RuntimeError('cleanup failure')
    def crash(*a):raise ValueError('primary export failure')
    monkeypatch.setattr(Ledger,'export',crash)
    with pytest.raises(ValueError,match='primary export failure'):run(config,out,execute=True,segmenter_factory=Worker)
    assert (out/'progress.json').exists()
    assert json.loads((out/'runtime.json').read_text())['cleanup_errors']
    db=sqlite3.connect(out/'ledger.sqlite');db.execute('BEGIN EXCLUSIVE');db.rollback();db.close()


@pytest.mark.parametrize('fault',['binding','verdict','nan','scalar'])
def test_invalid_native_evidence_is_not_cached_and_retry_recovers(tmp_path,fault):
    r=row('1234');r.update(primary_class='numerics_tables',script_class='nonletter')
    config=census_config(tmp_path,[r]);config['native_workers']=2;out=tmp_path/'run'
    def broken(r):
        result=segment(r)
        if fault=='binding':result['raw_text_sha256']='wrong'
        if fault=='verdict':result['verdict']='UNKNOWN_SUCCESS'
        if fault=='nan':result['value']=float('nan')
        if fault=='scalar':return 42
        return result
    first=run(config,out,execute=True,segmenter_factory=lambda:broken)
    assert first['dispositions']['INFRA_ERROR']==1
    db=sqlite3.connect(out/'ledger.sqlite')
    assert db.execute('SELECT count(*) FROM measurements').fetchone()[0]==0
    assert db.execute('SELECT count(*) FROM measurement_failures').fetchone()[0]==1
    db.close()
    calls=[]
    def healthy(r):calls.append(r['id']);return segment(r)
    second=run(config,out,execute=True,retry_errors=True,segmenter_factory=lambda:healthy)
    assert second['complete'] and second['dispositions']['ADMIT']==1 and calls==['r1']


def test_poisoned_existing_cache_is_quarantined_and_remeasured(tmp_path):
    r=row('1234');r.update(primary_class='numerics_tables',script_class='nonletter')
    config=census_config(tmp_path,[r]);out=tmp_path/'run'
    run(config,out,execute=True,segmenter_factory=lambda:segment)
    db=sqlite3.connect(out/'ledger.sqlite')
    key,payload=db.execute('SELECT key,payload FROM measurements').fetchone();bad=json.loads(payload);bad['raw_text_sha256']='wrong'
    db.execute('UPDATE measurements SET payload=? WHERE key=?',(canonical(bad),key))
    d=json.loads(db.execute('SELECT payload FROM decisions').fetchone()[0]);d.update(disposition='INFRA_ERROR',admitted=False)
    db.execute('UPDATE decisions SET disposition=?,payload=?',('INFRA_ERROR',canonical(d)));db.commit();db.close()
    calls=[]
    def healthy(r):calls.append(r['id']);return segment(r)
    result=run(config,out,execute=True,retry_errors=True,segmenter_factory=lambda:healthy)
    assert result['complete'] and result['dispositions']['ADMIT']==1 and calls==['r1']
    assert json.loads((out/'runtime.json').read_text())['invalid_cache_entries']==1



@pytest.mark.parametrize('counts',[[1,1],[4,8],[1,257],[],[1,True]])
def test_qualification_requires_unique_workers_and_serial_baseline(tmp_path,counts):
    import importlib.util
    path=Path(__file__).resolve().parents[1]/'scripts/harvest/clariden/worker.py'
    spec=importlib.util.spec_from_file_location('cscs_qualification',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    with pytest.raises(ValueError,match='serial 1'):
        module.qualify(tmp_path,tmp_path/'out',1,counts)
    assert not (tmp_path/'out').exists()



def test_existing_original_crop_mapping_keeps_wave_and_rejects_traversal(tmp_path):
    import importlib.util
    path=Path(__file__).resolve().parents[1]/'scripts/harvest/clariden/worker.py'
    spec=importlib.util.spec_from_file_location('cscs_crop_paths',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    record=dict(crop='docs/harvest/harvest_big/round1/crops/book/p000016-l0004.png',wave='round1')
    assert module.old_crop(record,tmp_path/'filter-run')==tmp_path/'collection_v2/crops/round1/book/p000016-l0004.png'
    record['crop']='docs/harvest/harvest_big/round1/crops/../p000016-l0004.png'
    with pytest.raises(ValueError):module.old_crop(record,tmp_path/'filter-run')


@pytest.mark.parametrize('fault',['no_attempts','cache','invalid_cache','unavailable','cleanup','incomplete'])
def test_qualification_cannot_promote_cached_or_failed_work(tmp_path,monkeypatch,fault):
    import importlib.util
    path=Path(__file__).resolve().parents[1]/'scripts/harvest/clariden/worker.py'
    spec=importlib.util.spec_from_file_location('cscs_receipt_gate',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    monkeypatch.setattr(module,'worker_guard',lambda:None)
    monkeypatch.setattr(module,'environment',lambda root:{})
    def sample(root,out,n):
        p=out/'sample.jsonl';p.write_text('{}\n');return p,1
    monkeypatch.setattr(module,'sample',sample)
    def fake_run(config,directory,**kwargs):
        directory.mkdir()
        runtime=dict(native_attempts=1,cached_measurements=0,invalid_cache_entries=0,unavailable=0,cleanup_errors=[])
        if fault=='no_attempts':runtime['native_attempts']=0
        if fault=='cache':runtime['cached_measurements']=1
        if fault=='invalid_cache':runtime['invalid_cache_entries']=1
        if fault=='unavailable':runtime['unavailable']=1
        if fault=='cleanup':runtime['cleanup_errors']=['failure']
        (directory/'runtime.json').write_text(canonical(runtime))
        return dict(complete=fault!='incomplete',dispositions={})
    monkeypatch.setattr(module,'run',fake_run)
    with pytest.raises(RuntimeError):module.qualify(tmp_path,tmp_path/'out',1,[1])
    assert not (tmp_path/'out/qualification.json').exists()


def test_reconstruction_reuses_existing_grayscale_png_contract():
    import io,hashlib
    from PIL import Image
    from greekocr.harvest.line_pipeline_native import reconstructed_crop,source_crop_matches
    # Tiny synthetic color fixture, no native detector or corpus image.
    page=Image.new('RGB',(4,4),(17,83,149));box=[1,1,3,3]
    expected=page.convert('L').crop(box);buffer=io.BytesIO();expected.save(buffer,format='PNG',compress_level=3)
    crop,raw=reconstructed_crop(page,box)
    assert crop.mode=='L' and raw==buffer.getvalue() and source_crop_matches(page,crop,box)
    wrong,wrong_raw=reconstructed_crop(page,box,'RGB')
    assert hashlib.sha256(raw).digest()!=hashlib.sha256(wrong_raw).digest()


def test_runtime_codec_drift_is_rejected_before_any_row(tmp_path,monkeypatch):
    from greekocr.harvest import line_pipeline_runtime as runtime
    manifest=tmp_path/'runtime.json'
    expected=dict(executables={},threads={k:'1' for k in runtime.THREAD_KEYS},opencv_threads=1,preload=[dict(path='/codec',sha256='a')])
    manifest.write_text(canonical(expected))
    monkeypatch.setattr(runtime,'capture',lambda executables:expected)
    assert runtime.validate(manifest)==runtime.file_identity(manifest)['sha256']
    monkeypatch.setattr(runtime,'capture',lambda executables:dict(expected,preload=[dict(path='/codec',sha256='b')]))
    with pytest.raises(ValueError,match='native runtime changed: preload'):runtime.validate(manifest)
    config=census_config(tmp_path,[row('1234')]);config['runtime_manifest']=str(manifest)
    with pytest.raises(ValueError,match='native runtime changed'):run(config,tmp_path/'run',execute=True,segmenter_factory=lambda:segment)
    assert not (tmp_path/'run/ledger.sqlite').exists()


def test_runtime_manifest_change_refuses_stale_resume(tmp_path,monkeypatch):
    from greekocr.harvest import line_pipeline_runtime as runtime
    manifest=tmp_path/'runtime.json';manifest.write_text('first runtime')
    monkeypatch.setattr(runtime,'validate',lambda p:runtime.file_identity(p)['sha256'])
    config=census_config(tmp_path,[row('1234')]);config['runtime_manifest']=str(manifest)
    out=tmp_path/'run';run(config,out,execute=True,segmenter_factory=lambda:segment)
    manifest.write_text('second runtime')
    with pytest.raises(ValueError,match='changed'):run(config,out,execute=True,segmenter_factory=lambda:segment)


def test_native_subprocess_receives_runtime_manifest():
    from greekocr.harvest.line_pipeline_native import NativeWorker
    worker=NativeWorker('versions.json','predictor',runtime_manifest='/bound/runtime.json')
    assert worker.command[-2:]==['--runtime-manifest','/bound/runtime.json']


def test_real_native_census_requires_runtime_manifest(tmp_path,monkeypatch):
    import greekocr.harvest.line_pipeline_census as census
    monkeypatch.setattr(census.platform,'system',lambda:'Linux')
    with pytest.raises(ValueError,match='requires runtime_manifest'):
        run({},tmp_path/'run',execute=True)
    assert not (tmp_path/'run').exists()


def test_runtime_validates_actual_selected_executables(tmp_path,monkeypatch):
    from greekocr.harvest import line_pipeline_runtime as runtime
    expected=dict(executables=dict(node=dict(path='/pinned/node',sha256='old')),
        threads={k:'1' for k in runtime.THREAD_KEYS},opencv_threads=1)
    p=tmp_path/'runtime.json';p.write_text(canonical(expected));seen=[]
    def capture(actual):
        seen.append(actual)
        return dict(expected,executables=dict(node=dict(path=actual['node'],sha256='old')))
    monkeypatch.setattr(runtime,'capture',capture)
    with pytest.raises(ValueError,match='executables'):runtime.validate(p,dict(node='/other/node'))
    assert seen==[dict(node='/other/node')]


def test_real_coordinator_checks_actual_runtime_before_ledger(tmp_path,monkeypatch):
    import shutil
    import greekocr.harvest.line_pipeline_census as census
    from greekocr.harvest import line_pipeline_runtime as runtime
    monkeypatch.setattr(census.platform,'system',lambda:'Linux')
    monkeypatch.setattr(shutil,'which',lambda name:'/selected/node')
    seen=[]
    def validate(path,actual):
        seen.append((path,actual));raise ValueError('fixture runtime drift')
    monkeypatch.setattr(runtime,'validate',validate)
    with pytest.raises(ValueError,match='fixture runtime drift'):
        run(dict(runtime_manifest='/runtime.json',predictor='/selected/predictor'),tmp_path/'run',execute=True)
    assert seen==[('/runtime.json',dict(node='/selected/node',predictor='/selected/predictor'))]
    assert not (tmp_path/'run').exists()


def test_original_parent_crop_manifest_binds_physical_path_without_rewriting_parent():
    from greekocr.harvest.line_pipeline_sources import canonicalize
    r=dict(id='row',doc='book',source='bsb_poly1850',label='raw',crop='historical/crops/row.png',split='train')
    metadata=dict(crops={canonical(['old-train','row']):dict(path='/worker/originals/round1/book/row.png',sha256='a'*64)})
    result=canonicalize(r,dict(id='old-train',format='collection-v2'),metadata)
    assert result['crop_path']=='/worker/originals/round1/book/row.png'
    assert result['crop_sha256']=='a'*64 and result['raw_text']=='raw' and result['parent_id']=='old-train'
    assert r['crop']=='historical/crops/row.png'


def test_parent_manifest_split_is_preserved_without_new_data_guess():
    from greekocr.harvest.line_pipeline_sources import canonicalize
    r=dict(id='row',doc='book',source='bsb_poly1850',label='raw')
    parent=dict(id='old-test',format='collection-v2',split='test')
    assert canonicalize(r,parent,{})['split']=='test'
    assert canonicalize(r,dict(parent,split='dev'),{})['split']=='dev'
    assert canonicalize(r,dict(id='new',format='collection-v2'),{})['split']=='unassigned'
    with pytest.raises(ValueError,match='split conflicts'):
        canonicalize(dict(r,split='train'),parent,{})


@pytest.mark.parametrize('original,cohort',[('val','dev'),('reserved','test')])
def test_legacy_evaluation_alias_requires_confirmed_parent_and_preserves_lineage(original,cohort):
    from greekocr.harvest.line_pipeline import validate_row
    r=dict(id='row',doc='book',source='elstat',label='1234',split=original)
    parent=dict(id='old-'+cohort,format='collection-v2',split=cohort)
    adapted=canonicalize(r,parent,{})
    validate_row(adapted)
    assert adapted['split']==cohort and adapted['source_split']==original
    assert r['split']==original
    for wrong in ('train','unassigned',None):
        with pytest.raises(ValueError,match='split conflicts'):
            canonicalize(r,dict(parent,split=wrong),{})
    for metadata in ({'books':{'book':{'split':'train'}}},
                     {'row_splits':{canonical([parent['id'],'row']):'train'}}):
        with pytest.raises(ValueError,match='split conflicts'):
            canonicalize(r,parent,metadata)
    assert canonicalize(r,parent,{'books':{'book':{'split':cohort}}})['split']==cohort


@pytest.mark.parametrize('layer',['raw','book','row'])
def test_frozen_original_parent_rejects_canonical_cohort_overrides(layer):
    r=dict(id='row',doc='book',source='elstat',label='1234',split='test')
    parent=dict(id='old-test',format='collection-v2',split='test');metadata={}
    if layer=='raw':r['split']='train'
    if layer=='book':metadata={'books':{'book':{'split':'train'}}}
    if layer=='row':metadata={'row_splits':{canonical(['old-test','row']):'train'}}
    with pytest.raises(ValueError,match='split conflicts'):
        canonicalize(r,parent,metadata)


@pytest.mark.parametrize('cohort,alias',[('dev','val'),('test','reserved')])
@pytest.mark.parametrize('layer',['book','row'])
@pytest.mark.parametrize('raw_present',[True,False])
def test_matching_metadata_aliases_are_canonicalized(cohort,alias,layer,raw_present):
    r=dict(id='row',doc='book',source='elstat',label='1234')
    if raw_present:r['split']=cohort
    parent=dict(id='old-'+cohort,format='collection-v2',split=cohort)
    metadata={'books':{'book':{'split':alias}}} if layer=='book' else {'row_splits':{canonical([parent['id'],'row']):alias}}
    assert canonicalize(r,parent,metadata)['split']==cohort


def test_original_train_dev_test_aliases_run_through_census_without_train_leakage(tmp_path):
    config=census_config(tmp_path,[]);config['parents']=[]
    for literal,cohort in [('train','train'),('val','dev'),('reserved','test')]:
        record=dict(id='book--s001-l'+cohort,doc='book',source='elstat',label='1234',
                    split=literal,crop_sha256='a'*64,primary_class='numerics_tables',script_class='nonletter',edition_id='edition')
        path=tmp_path/(cohort+'.jsonl');path.write_text(canonical(record)+'\n')
        config['parents'].append(dict(id='old-'+cohort,format='collection-v2',split=cohort,path=str(path),sha256=file_sha(path),rows=1))
    summary=run(config,tmp_path/'run',execute=True,segmenter_factory=lambda:segment)
    assert summary['complete'] and summary['input_rows']==3
    evaluation=[json.loads(line) for line in (tmp_path/'run/evaluation_diagnostics.jsonl').read_text().splitlines()]
    assert {(item['row']['split'],item['row']['source_split']) for item in evaluation}=={('dev','val'),('test','reserved')}
    assert not (tmp_path/'run/admitted_train.jsonl').read_text()


def test_all_parent_input_preflight_uses_registration_without_native_or_census_completion(tmp_path):
    config=census_config(tmp_path,[row('1234')])
    def factory():raise AssertionError('metadata preflight must not create a native worker')
    result=run(config,tmp_path/'preflight',execute=True,segmenter_factory=factory,validate_inputs_only=True)
    assert result['status']=='PASS' and result['preflight_complete']
    assert not result['complete'] and not result['processing_started'] and result['decisions']==0
    assert result['input_rows']==1 and result['by_parent_split']==[dict(parent='parent',split='train',rows=1)]
    assert not (tmp_path/'preflight/CURRENT.json').exists()
    broken=deepcopy(config);broken['parents'][0]['sha256']='0'*64
    with pytest.raises(ValueError,match='parent SHA mismatch'):
        run(broken,tmp_path/'bad',execute=True,segmenter_factory=factory,validate_inputs_only=True)


def test_full_preparation_blocks_missing_original_crop(tmp_path,monkeypatch):
    import importlib.util
    path=Path(__file__).resolve().parents[1]/'scripts/harvest/clariden/worker.py'
    spec=importlib.util.spec_from_file_location('cscs_prepare',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    monkeypatch.setattr(module,'worker_guard',lambda:None);monkeypatch.setattr(module,'environment',lambda root:{})
    data=tmp_path/'parent.jsonl';data.write_text(canonical(dict(id='missing',crop='not-present',wave='round1'))+'\n')
    monkeypatch.setattr(module,'inputs',lambda root:[dict(id='old',path=str(data))])
    monkeypatch.setattr(module,'old_crop',lambda r,root:root/'missing.png')
    def inventory(root,out):
        out.mkdir();(out/'inventory.json').write_text(canonical(dict(source_pages_missing=0)))
    monkeypatch.setattr(module,'inventory',inventory)
    with pytest.raises(RuntimeError,match='original crops missing'):module.prepare(tmp_path,tmp_path/'out',8)
    assert not (tmp_path/'out/config.json').exists()
    assert json.loads((tmp_path/'out/missing_original_crops.json').read_text())==[dict(parent_id='old',id='missing')]


def test_native_context_reuses_narrow_existing_envelope_quarantine():
    import numpy as np
    from greekocr.harvest.geometry_observations import prepare_geometry_row,vendor_ownership,invalid_geometry_dependencies
    from greekocr.harvest.line_pipeline_native import ASSETS
    ownership=vendor_ownership(ASSETS/'collector')
    row=dict(row_id='bad',x0=20,x1=28,xheight=2,owned_box=[20,1,28,8],component_ids=[1])
    for k in ownership.CURVES:row[k]=np.full(8,1. if k in ('top','font_top','accent_top') else 8.)
    row.update(meanline=np.full(8,3.),baseline=np.full(8,5.));row['bottom'][0]=0
    ink=np.zeros((10,40),bool);labels=np.zeros_like(ink,dtype=int)
    prepared,invalid=prepare_geometry_row(row,dict(line_indices=[10]),ink,labels,ownership)
    assert prepared is None and invalid['reason']=='nonpositive_row_envelope'
    assert invalid['minimum_bottom_minus_top']==-1
    target=dict(row_id='target',neighbours=dict(above=-1),_x=np.array([2]),_y=np.array([3]))
    page=dict(rows=[target],invalid_rows=[invalid],structure={'bad':dict(line_indices=[10])},ownership=ownership)
    assert invalid_geometry_dependencies(page,[0,0,8,10])==[]
    assert invalid_geometry_dependencies(page,[20,0,28,10])==['bad']
    target['neighbours']['above']=10
    assert invalid_geometry_dependencies(page,[0,0,8,10])==['bad']
    broken=dict(row);broken['meanline']=np.full(8,6.)
    with pytest.raises(ValueError,match='positive own body curves'):prepare_geometry_row(broken,dict(line_indices=[10]),ink,labels,ownership)
    broken=dict(row);broken['accent_top']=np.full(7,1.)
    with pytest.raises(ValueError,match='invalid_detector_geometry'):prepare_geometry_row(broken,dict(line_indices=[10]),ink,labels,ownership)
    broken=dict(row);broken['accent_top']=np.full(8,float('nan'))
    with pytest.raises(ValueError,match='invalid_detector_geometry'):prepare_geometry_row(broken,dict(line_indices=[10]),ink,labels,ownership)


def test_qualification_ignores_only_known_orientation_clock():
    import importlib.util
    path=Path(__file__).resolve().parents[1]/'scripts/harvest/clariden/worker.py'
    spec=importlib.util.spec_from_file_location('cscs_scientific_comparison',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    first=dict(run_binding_sha256='a',stages=[dict(stage='segmentation',result=dict(verdict='KEEP',reason='bound',
        frame=dict(orientation=dict(angle=90,evidence=dict(seconds=1.2,confidence=.9))),evidence=dict(seconds=55,box=[1,2,3,4])))])
    second=deepcopy(first);second['run_binding_sha256']='b';second['stages'][0]['result']['frame']['orientation']['evidence']['seconds']=8.4
    assert module.scientific_decision(first)==module.scientific_decision(second)
    assert first['stages'][0]['result']['frame']['orientation']['evidence']['seconds']==1.2
    horizontal=deepcopy(first);horizontal['stages'][0]['result']['frame']['orientation']=None
    assert module.scientific_decision(horizontal)['stages'][0]['result']['frame']['orientation'] is None
    for key in ['verdict','angle','box','other_seconds']:
        changed=deepcopy(second);r=changed['stages'][0]['result']
        if key=='verdict':r['verdict']='DROP'
        elif key=='angle':r['frame']['orientation']['angle']=0
        elif key=='box':r['evidence']['box']=[1,2,3,5]
        else:r['evidence']['seconds']=56
        assert module.scientific_decision(first)!=module.scientific_decision(changed)


@pytest.mark.parametrize('factors',[[],[8],[2,2],[2,65],[2,True]])
def test_qualification_rejects_ambiguous_prefetch_cases(tmp_path,factors):
    import importlib.util
    path=Path(__file__).resolve().parents[1]/'scripts/harvest/clariden/worker.py'
    spec=importlib.util.spec_from_file_location('prefetch_qualification',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    with pytest.raises(ValueError,match='prefetch factors'):module.qualify(tmp_path,tmp_path/'out',1,[1,16],prefetch_factors=factors)
    assert not (tmp_path/'out').exists()


def test_qualification_rejects_excess_window_before_worker_startup(tmp_path):
    import importlib.util
    path=Path(__file__).resolve().parents[1]/'scripts/harvest/clariden/worker.py'
    spec=importlib.util.spec_from_file_location('window_qualification',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    with pytest.raises(ValueError,match='4096'):
        module.qualify(tmp_path,tmp_path/'out',1,[1,128],prefetch_factors=[2,64])
    assert not (tmp_path/'out').exists()


def test_empty_rule_refit_is_recognized_without_changing_detector(monkeypatch):
    import numpy as np,cv2
    from greekocr.pages.pixels import _direct_rules
    from greekocr.harvest.line_pipeline_native import empty_oblique_rule_fit
    # Tiny synthetic support plane; Hough output is fixed, no corpus/detector run.
    ink=np.zeros((80,40),bool);ink[:,10]=True
    monkeypatch.setattr(cv2,'HoughLinesP',lambda *args,**kwargs:np.array([[[10,0,10,79]]]))
    original=np.polyfit;calls=[]
    def lose_support(x,y,*args,**kwargs):
        calls.append(len(x))
        return np.array([0.,10000.]) if len(calls)==1 else original(x,y,*args,**kwargs)
    monkeypatch.setattr(np,'polyfit',lose_support)
    try:_direct_rules(ink,3.,[])
    except TypeError as exc:assert empty_oblique_rule_fit(exc)
    else:pytest.fail('fixture must reproduce the frozen empty refit failure')
    assert calls==[80,0]
    try:original(np.array([]),np.array([]),1)
    except TypeError as exc:assert not empty_oblique_rule_fit(exc)
    assert not empty_oblique_rule_fit(TypeError('expected non-empty vector for x'))
    assert not empty_oblique_rule_fit(ValueError('expected non-empty vector for x'))
    assert not empty_oblique_rule_fit(TypeError('unrelated runtime failure'))
