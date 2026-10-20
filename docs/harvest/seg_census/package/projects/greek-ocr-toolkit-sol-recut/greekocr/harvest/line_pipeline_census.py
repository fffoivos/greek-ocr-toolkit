"""Durable all-row census and explicit work queues. Default CLI is preflight."""
from __future__ import annotations
import argparse
from collections import Counter
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import sqlite3
import sys
import time
import uuid

from .line_pipeline import Pipeline, canonical, digest, inventory, identity, validate_row, orthography_for, SUCCESS, validate_result, preserve_holds, russian_eligible, expectations, validate_segmentation
from .line_pipeline_adapters import adapt_legacy
from .line_pipeline_native import file_sha, NativeWorker
from .line_pipeline_sources import canonicalize
from .line_pipeline_parallel import NativePool, Observation
from . import admission as adm


def records(path):
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as stream:
        for index, line in enumerate(stream, 1):
            if not line.strip():
                continue
            yield index, json.loads(line)


def atomic_json(path, value):
    path = Path(path); temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w") as stream:
        stream.write(canonical(value) + "\n"); stream.flush(); os.fsync(stream.fileno())
    temporary.replace(path)
    descriptor=os.open(path.parent,os.O_RDONLY)
    try:os.fsync(descriptor)
    finally:os.close(descriptor)


class Ledger:
    def __init__(self, path, binding):
        self.directory=Path(path).parent
        self.generation_started=False
        self.binding_sha256=digest(canonical(binding))
        self.db = sqlite3.connect(path)
        self.db.executescript("""
            PRAGMA journal_mode=WAL;
            PRAGMA synchronous=FULL;
            CREATE TABLE IF NOT EXISTS run(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS observations(
                parent TEXT NOT NULL, id TEXT NOT NULL, split TEXT NOT NULL,
                source TEXT NOT NULL, book TEXT NOT NULL, edition TEXT NOT NULL,
                page TEXT NOT NULL, role TEXT NOT NULL, script TEXT NOT NULL,
                payload TEXT NOT NULL, raw_inventory TEXT NOT NULL,
                PRIMARY KEY(parent,id));
            CREATE INDEX IF NOT EXISTS parent_page_rows ON observations(parent,source,book,page);
            CREATE TABLE IF NOT EXISTS decisions(parent TEXT,id TEXT,disposition TEXT NOT NULL,payload TEXT NOT NULL,
                PRIMARY KEY(parent,id));
            CREATE TABLE IF NOT EXISTS corrections(tool TEXT,parent TEXT,id TEXT,payload TEXT NOT NULL,release_key TEXT NOT NULL,
                PRIMARY KEY(tool,parent,id));
            CREATE TABLE IF NOT EXISTS releases(key TEXT PRIMARY KEY,payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS measurements(key TEXT PRIMARY KEY,payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS measurement_failures(key TEXT,payload TEXT NOT NULL,reason TEXT NOT NULL);
        """)
        encoded = canonical(binding)
        existing = self.db.execute("SELECT value FROM run WHERE key='binding'").fetchone()
        if existing and existing[0] != encoded:
            raise ValueError("run inputs/code/config changed; use a new ledger, never resume stale decisions")
        self.db.execute("INSERT OR IGNORE INTO run VALUES ('binding',?)", (encoded,)); self.db.commit()
        self.total=self.db.execute("SELECT count(*) FROM observations").fetchone()[0]
        self.counts=Counter(dict(self.db.execute("SELECT disposition,count(*) FROM decisions GROUP BY disposition")))
        self.page_cache={}

    def register(self, row, codec):
        validate_row(row)
        old = self.db.execute("SELECT payload FROM observations WHERE parent=? AND id=?", (row["parent_id"],row["id"])).fetchone()
        payload = canonical(row)
        if old:
            if old[0] != payload:
                raise ValueError("same observation ID has different raw text, crop, split or metadata")
            return
        self.db.execute("INSERT INTO observations VALUES (?,?,?,?,?,?,?,?,?,?,?)", (
            row["parent_id"],row["id"],row["split"],row["source"],row["book_id"],row["edition_id"],row["page_id"],
            row.get("content_role",row.get("primary_class","prose")),row.get("script_class","unspecified"),payload,canonical(inventory(row["raw_text"],codec))))
        self.total+=1;self.page_cache.clear()

    def mark(self, key, value=True):
        with self.db:self.db.execute("INSERT OR REPLACE INTO run VALUES (?,?)",(key,canonical(value)))

    def generation(self):
        found=self.db.execute("SELECT value FROM run WHERE key='generation'").fetchone()
        return int(found[0]) if found else 0

    def begin_changes(self):
        if self.generation_started:return
        generation=self.generation()+1
        # Invalidate publication before changing any decision or phase.
        atomic_json(self.directory/"CURRENT.json",dict(status="in_progress",generation=generation,run_binding_sha256=self.binding_sha256))
        current=self.directory/"current"
        if current.is_symlink():current.unlink()
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO run VALUES ('generation',?)",(str(generation),))
            self.db.execute("DELETE FROM run WHERE key IN ('rows_complete','dedup_complete','export_complete')")
        self.generation_started=True

    def save_decision(self, row, decision):
        decision=dict(decision,run_binding_sha256=self.binding_sha256)
        encoded=canonical(decision)
        old=self.db.execute("SELECT payload,disposition FROM decisions WHERE parent=? AND id=?",(row["parent_id"],row["id"])).fetchone()
        if old and old[0]==encoded:return
        self.begin_changes()
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO decisions VALUES (?,?,?,?)", (row["parent_id"],row["id"],decision["disposition"],encoded))
        if old:self.counts[old[1]]-=1
        self.counts[decision["disposition"]]+=1

    def page_summary(self, row):
        key=tuple(row[k] for k in ("parent_id","source","book_id","page_id"))
        if key in self.page_cache:return self.page_cache[key]
        values = self.db.execute("SELECT raw_inventory FROM observations WHERE parent=? AND source=? AND book=? AND page=?", (row["parent_id"],row["source"],row["book_id"],row["page_id"]))
        n = numeric = digits = letters = 0
        for (payload,) in values:
            inv = json.loads(payload); n += 1
            numeric += inv["digits"] > 0 and inv["letter_count"] == 0
            digits += inv["digits"]; letters += inv["letter_count"]
        result=dict(line_count=n, numeric_line_fraction=numeric/n if n else 0, digits=digits, letters=letters)
        self.page_cache[key]=result
        return result

    def summary(self, detailed=True):
        total = self.total
        counts = {k:v for k,v in self.counts.items() if v}
        counts["UNPROCESSED"] = total-sum(counts.values())
        phases=dict(self.db.execute("SELECT key,value FROM run WHERE key IN ('inventory_complete','rows_complete','dedup_complete','export_complete')"))
        generation=self.generation()
        try:publication=json.loads((self.directory/"CURRENT.json").read_text())
        except (OSError,ValueError):publication={}
        phase_ok=bool(phases.get("inventory_complete")) and all(phases.get(p)==str(generation) for p in ("rows_complete","dedup_complete","export_complete")) and publication.get("status")=="completed" and publication.get("generation")==generation and publication.get("run_binding_sha256")==self.binding_sha256
        summary=dict(schema="line-filter-census-summary-v1",input_rows=total,dispositions=counts,reconciled=total==sum(counts.values()),
            complete=phase_ok and not counts.get("UNPROCESSED") and not counts.get("INFRA_ERROR"),generation=generation,phases=phases,
            run_binding_sha256=self.binding_sha256,population_accuracy_claim=False)
        if not detailed:return summary
        breakdown = [dict(zip(("parent","split","source","role","script","disposition","rows"), r)) for r in self.db.execute("""
            SELECT o.parent,o.split,o.source,o.role,o.script,coalesce(d.disposition,'UNPROCESSED'),count(*)
            FROM observations o LEFT JOIN decisions d USING(parent,id)
            GROUP BY o.parent,o.split,o.source,o.role,o.script,d.disposition""")]
        reasons, statuses, availability = Counter(), Counter(), Counter()
        for (payload,) in self.db.execute("SELECT payload FROM decisions"):
            d=json.loads(payload)
            for reason in d.get("reasons",[]):reasons[reason["reason"]]+=1
            for tool,result in d.get("routes",{}).items():statuses[tool+":"+result["status"]]+=1
            for stage in d.get("stages",[]):
                if stage["stage"]=="segmentation":availability[stage["result"].get("availability","measured")]+=1
        summary.update(overlapping_reason_counts=dict(reasons),route_status_counts=dict(statuses),segmentation_availability=dict(availability),by_stratum=breakdown)
        return summary


    def deduplicate(self):
        """Exact crop identity and held-out protection; never silently union parents."""
        held_crops={r[0] for r in self.db.execute("SELECT DISTINCT json_extract(payload,'$.crop_sha256') FROM observations WHERE split!='train' AND split!='unassigned'")}
        binding=json.loads(self.db.execute("SELECT value FROM run WHERE key='binding'").fetchone()[0])
        held_crops.update(binding.get("config",{}).get("final_policy",{}).get("heldout_crop_sha256",[]))
        groups={}
        for parent,i,payload,decision in self.db.execute("SELECT o.parent,o.id,o.payload,d.payload FROM observations o JOIN decisions d USING(parent,id) WHERE o.split='train' ORDER BY o.parent,o.id"):
            row=json.loads(payload);d=json.loads(decision)
            if d.get("pre_dedup_disposition")=="ADMIT":
                d.update(disposition="ADMIT",admitted=True,reasons=[])
            if d["disposition"]!="ADMIT":continue
            d["pre_dedup_disposition"]="ADMIT"
            groups.setdefault(row["crop_sha256"],[]).append((row,d))
        for crop,items in groups.items():
            labels={d["final_text_sha256"] for _,d in items}
            for index,(row,d) in enumerate(items):
                if crop in held_crops:
                    d.update(disposition="DROP",admitted=False,reasons=[dict(reason="heldout_crop_identity")])
                elif len(labels)>1:
                    d.update(disposition="HOLD",admitted=False,reasons=[dict(reason="same_crop_conflicting_labels")])
                elif index:
                    d.update(disposition="DROP",admitted=False,reasons=[dict(reason="duplicate_training_observation",retained_binding=identity(items[0][0]))])
                self.save_decision(row,d)

    def export(self, directory):
        root=Path(directory);root.mkdir(exist_ok=True)
        generations=root/"generations";generations.mkdir(exist_ok=True)
        generation=self.generation()
        export_id="g%d-%s"%(generation,uuid.uuid4().hex)
        directory=generations/("."+export_id+".tmp");directory.mkdir()
        final=generations/export_id
        files={}
        handles={}
        try:
            for name in ("decisions", "admitted_train", "admission_records", "evaluation_diagnostics"):
                handles[name]=(directory/(name+".jsonl.tmp")).open("w")
            for tool in ("polytonic","cyrillic","numerics","content_repair"):
                handles["pending_"+tool]=(directory/("pending_"+tool+".jsonl.tmp")).open("w")
            for parent,i,split,payload,decision in self.db.execute("SELECT o.parent,o.id,o.split,o.payload,d.payload FROM observations o LEFT JOIN decisions d USING(parent,id) ORDER BY o.parent,o.id"):
                row=json.loads(payload);d=json.loads(decision) if decision else dict(binding=identity(row),disposition="UNPROCESSED",admitted=False)
                handles["decisions"].write(canonical(d)+"\n")
                handles["admission_records"].write(canonical(dict(row_id=i,parent_id=parent,split=split,
                    **{"pass":d["disposition"]=="ADMIT"},label=d.get("final_text",row["raw_text"]),crop_sha256=row["crop_sha256"],
                    source=row["source"],primary_class=row.get("primary_class",row.get("content_role")),
                    pipeline_version="0.3",disposition=d["disposition"],decision=d))+"\n")
                if split!="train":handles["evaluation_diagnostics"].write(canonical(dict(row=row,decision=d))+"\n")
                elif d["disposition"]=="ADMIT":handles["admitted_train"].write(canonical(dict(row,final_text=d["final_text"],decision=d))+"\n")
                for tool,r in d.get("routes",{}).items():
                    if r["status"] in {"required_evidence_unresolved","proposal_only","failed"} and "pending_"+tool in handles:
                        queued=dict(row,label=row["raw_text"],text=row["raw_text"],crop=row.get("crop_path"),tool=tool,
                            expected=d.get("expectations"),required_binding=identity(row),raw_text_sha256=digest(row["raw_text"]),filter_obligation=r.get("obligation"))
                        if tool=="polytonic":queued["script_class"]="greek_poly"
                        handles["pending_"+tool].write(canonical(queued)+"\n")
            for name,stream in handles.items():
                stream.flush();os.fsync(stream.fileno());stream.close()
                target=directory/(name+".jsonl");(directory/(name+".jsonl.tmp")).replace(target)
                files[name]=dict(path=str(final/target.name),sha256=file_sha(target))
        finally:
            for stream in handles.values():stream.close()
        summary=self.summary()
        summary["phases"]["export_complete"]=str(generation)
        summary["complete"]=all(summary["phases"].get(k)==str(generation) for k in ("rows_complete","dedup_complete")) and bool(summary["phases"].get("inventory_complete")) and not summary["dispositions"].get("UNPROCESSED") and not summary["dispositions"].get("INFRA_ERROR")
        summary.update(outputs=files,export_id=export_id)
        atomic_json(directory/"summary.json",summary)
        directory.replace(final)
        descriptor=os.open(generations,os.O_RDONLY)
        try:os.fsync(descriptor)
        finally:os.close(descriptor)
        self.mark("export_complete",generation)
        # All compatibility files point through one atomically switched directory.
        temporary=root/".current.tmp"
        if temporary.is_symlink():temporary.unlink()
        temporary.symlink_to(Path("generations")/export_id,target_is_directory=True)
        temporary.replace(root/"current")
        for name in [*(n+".jsonl" for n in handles),"summary.json"]:
            alias=root/name
            if not alias.is_symlink():
                temporary=root/("."+name+".link.tmp")
                temporary.symlink_to(Path("current")/name);temporary.replace(alias)
        atomic_json(root/"CURRENT.json",dict(status="completed",generation=generation,export_id=export_id,
            run_binding_sha256=self.binding_sha256,summary_sha256=file_sha(final/"summary.json"),summary_path=str(final/"summary.json")))


class ArtifactCorrector:
    def __init__(self, ledger, versions, parent_hashes):
        self.ledger,self.versions,self.parent_hashes=ledger,versions,parent_hashes

    def load(self, release):
        if release["status"] not in {"released","candidate_pre_audit"}:
            raise ValueError("unknown correction release status")
        if release["parent_manifest_sha256"] != self.parent_hashes[release["parent_id"]]:
            raise ValueError("correction source parent fingerprint mismatch")
        if file_sha(release["path"])!=release["sha256"]:
            raise ValueError("correction file fingerprint mismatch")
        key=digest(canonical(release))
        if self.ledger.db.execute("SELECT 1 FROM releases WHERE key=?",(key,)).fetchone():return
        with self.ledger.db:
            for _,record in records(release["path"]):
                if release.get("format")=="line-tool-result-v1":
                    bound=record.get("binding",{});i=bound.get("id")
                    if bound.get("parent_id")!=release["parent_id"] or record.get("tool")!=release["tool"]:
                        raise ValueError("canonical result parent/tool mismatch")
                else:i=record.get("id",record.get("line_id"))
                if not isinstance(i,str) or not i:raise ValueError("correction record missing nonempty ID")
                if any(record.get(alias,i)!=i for alias in ("id","line_id")):
                    raise ValueError("contradictory correction ID aliases")
                original=self.ledger.db.execute("SELECT payload FROM observations WHERE parent=? AND id=?",(release["parent_id"],i)).fetchone()
                if not original:raise ValueError("correction ID not in registered parent")
                if release.get("format")=="line-tool-result-v1":validate_result(record,json.loads(original[0]),release["tool"],self.versions)
                previous=self.ledger.db.execute("SELECT payload FROM corrections WHERE tool=? AND parent=? AND id=?",(release["tool"],release["parent_id"],i)).fetchone()
                payload=canonical(record)
                if previous:
                    raise ValueError("duplicate correction row across artifacts: "+str(i))
                self.ledger.db.execute("INSERT INTO corrections VALUES (?,?,?,?,?)",(release["tool"],release["parent_id"],i,payload,key))
            if file_sha(release["path"])!=release["sha256"]:raise ValueError("correction artifact changed while indexing")
            self.ledger.db.execute("INSERT INTO releases VALUES (?,?)",(key,canonical(release)))

    def __call__(self,row,tool,expected):
        found=self.ledger.db.execute("SELECT c.payload,r.payload FROM corrections c JOIN releases r ON r.key=c.release_key WHERE c.tool=? AND c.parent=? AND c.id=?",(tool,row["parent_id"],row["id"])).fetchone()
        if not found:return None  # sparse omission is NEVER no-change
        record,release=map(json.loads,found)
        if release.get("format")=="line-tool-result-v1":
            producer=record.get("evidence",{}).get("producer",{})
            for key,value in release.get("producer",{}).items():
                if producer.get(key)!=value:raise ValueError("manifest/record producer mismatch: "+key)
            evidence=dict(record.get("evidence",{}),artifact_sha256=release["sha256"],release_status=release["status"],
                parent_manifest_sha256=release["parent_manifest_sha256"],original_record_sha256=digest(canonical(record)),
                adapter_version="0.2",adapter_toolchain_digest=self.versions[tool]["digest"])
            result=dict(record,evidence=evidence)
        else:result=adapt_legacy(row,tool,record,release,self.versions)
        result=preserve_holds(result)
        if release["status"]!="released" and result["status"] in SUCCESS:
            result=dict(result,status="proposal_only",edits=[])
        if tool=="cyrillic" and (result.get("edits") or orthography_for(expected,"cyrillic")=="historical_russian") and not russian_eligible(expected):
            result=dict(result,status="required_evidence_unresolved",edits=[],reason="RU1 Russian language/historical orthography not eligible")
        if tool=="polytonic" and orthography_for(expected,"greek")!="polytonic":
            result=dict(result,status="required_evidence_unresolved",edits=[],reason="polytonic orthography eligibility unresolved")
        return result


def code_binding():
    here=Path(__file__).parent
    paths=list(here.glob("line_pipeline*.py"))+list((here/"filtering_assets").glob("*"))
    # Existing underlying toolkit code is also pinned: no silent dependency drift.
    paths+=list(here.parent.rglob("*.py"))
    return {str(p.relative_to(here.parent.parent)):file_sha(p) for p in sorted(set(paths)) if p.is_file()}


def verify_versions(versions, component_roots=None):
    roots=component_roots or {}
    projects=Path(__file__).resolve().parents[3]
    for name,tool in versions.items():
        if tool["version"]!="0."+str(tool["iteration_count"]) or len(tool["documented_iterations"])!=tool["iteration_count"]:
            raise ValueError("version/iteration history mismatch: "+name)
        components=tool["components"]
        if digest(json.dumps(components,sort_keys=True,separators=(",",":")))!=tool["digest"]:
            raise ValueError("invalid tool digest: "+name)
        for relative,wanted in components.items():
            path=Path(relative);root=Path(roots.get(path.parts[0],projects/path.parts[0]))
            actual=root.joinpath(*path.parts[1:])
            if file_sha(actual)!=wanted:raise ValueError("tool source/release changed: "+relative)


def run(config, out, *, execute=False, allow_local=False, retry_errors=False, retry_holds=False, segmenter_factory=None, validate_inputs_only=False):
    if not execute:
        return dict(status="preflight",parents=config["parents"],correction_artifacts=config.get("corrections",[]),processing_started=False)
    if platform.system()=="Darwin" and not allow_local and segmenter_factory is None:
        raise RuntimeError("MacBook is not a processing worker; use the prepared worker package")
    if segmenter_factory is None and not config.get('runtime_manifest'):
        raise ValueError('native census requires runtime_manifest')
    runtime_sha=None
    if config.get('runtime_manifest'):
        from .line_pipeline_runtime import validate
        if segmenter_factory is None:
            import shutil
            node=shutil.which('node')
            if node is None:raise FileNotFoundError('Node runtime unavailable')
            runtime_sha=validate(config['runtime_manifest'],dict(node=node,predictor=config['predictor']))
        else:runtime_sha=validate(config['runtime_manifest'])
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    versions=json.loads(Path(config["versions"]).read_text())["tools"]
    if segmenter_factory is None:verify_versions(versions,config.get("component_roots"))
    metadata=json.loads(Path(config["metadata"]).read_text())
    codec=adm.load_codec(config.get("codec"))
    parent_hashes={}
    for parent in config["parents"]:
        if parent["id"] in parent_hashes:raise ValueError("duplicate parent identity")
        if file_sha(parent["path"])!=parent["sha256"]:raise ValueError("parent SHA mismatch")
        parent_hashes[parent["id"]]=parent["sha256"]
    binding=dict(config=config,versions_sha256=file_sha(config["versions"]),metadata_sha256=file_sha(config["metadata"]),codec_sha256=codec["sha256"],code=code_binding(),predictor_sha256=file_sha(config["predictor"]) if config.get("predictor") else None,runtime_sha256=runtime_sha)
    ledger=Ledger(out/"ledger.sqlite",binding)
    atomic_json(out/"progress.json",dict(ledger.summary(detailed=False),stage="inventory_registration"))
    # Inventory EVERY row before any filter. This also powers immutable page counts.
    for parent in config["parents"]:
        count=0;seen=set()
        for _,record in records(parent["path"]):
            row=canonicalize(record,parent,metadata)
            if row["id"] in seen:raise ValueError("duplicate row ID in parent manifest")
            seen.add(row["id"]);ledger.register(row,codec);count+=1
            if count%1000==0:
                ledger.db.commit();atomic_json(out/"progress.json",dict(ledger.summary(detailed=False),stage="inventory_registration",current_parent=parent["id"],registered=count))
        if count!=parent["rows"]:raise ValueError("parent row-count mismatch")
        if file_sha(parent["path"])!=parent["sha256"]:raise ValueError("parent changed while registering")
        ledger.db.commit()
    ledger.db.execute("INSERT OR REPLACE INTO run VALUES ('inventory_complete','true')");ledger.db.commit()
    policy=dict(config.get("final_policy",{}))
    policy["heldout_editions"]=sorted(set(policy.get("heldout_editions",[]))|{r[0] for r in ledger.db.execute("SELECT DISTINCT edition FROM observations WHERE split!='train'")})
    corrector=ArtifactCorrector(ledger,versions,parent_hashes)
    for release in config.get("corrections",[]):corrector.load(release)
    if validate_inputs_only:
        result=dict(status="PASS",preflight_complete=True,complete=False,processing_started=False,
            scope="all-parent canonical registration and correction schema; no native filtering or training admission",
            input_rows=ledger.total,run_binding_sha256=ledger.binding_sha256,parent_hashes=parent_hashes,
            by_parent_split=[dict(parent=p,split=s,rows=n) for p,s,n in ledger.db.execute(
                "SELECT parent,split,count(*) FROM observations GROUP BY parent,split ORDER BY parent,split")],
            source_split_counts=[dict(parent=p,source_split=s,rows=n) for p,s,n in ledger.db.execute(
                "SELECT parent,json_extract(payload,'$.source_split'),count(*) FROM observations GROUP BY parent,json_extract(payload,'$.source_split') ORDER BY parent")],
            correction_rows=ledger.db.execute("SELECT count(*) FROM corrections").fetchone()[0],
            correction_releases=ledger.db.execute("SELECT count(*) FROM releases").fetchone()[0],
            decisions=ledger.db.execute("SELECT count(*) FROM decisions").fetchone()[0],runtime_sha256=runtime_sha)
        atomic_json(out/"input-preflight.json",result)
        atomic_json(out/"progress.json",dict(ledger.summary(detailed=False),stage="input_preflight_complete"))
        ledger.db.close()
        return result
    factory=segmenter_factory or (lambda:NativeWorker(config["versions"],config["predictor"],config.get("row_timeout_seconds",120),config.get('runtime_manifest')))
    pool=NativePool(factory,config.get("native_workers",1),config.get('native_prefetch_factor',2))
    code_sha=digest(canonical(binding["code"]))
    cache_keys={}
    runtime=dict(native_workers=pool.workers,native_prefetch_factor=pool.prefetch_factor,native_attempts=0,cached_measurements=0,native_seconds_sum=0,unavailable=0,invalid_cache_entries=0)
    started=time.monotonic()
    def prepare(row):
        try:expectations(row,metadata)
        except ValueError:return Observation()
        if row.get("crop_identity_status","bound")!="bound":return Observation()
        key=digest(canonical(dict(binding=identity(row),raw=digest(row["raw_text"]),source=row.get("crop_source_sha256"),bbox=row.get("crop_bbox"),code=code_sha,runtime_sha256=runtime_sha)))
        cache_keys[(row["parent_id"],row["id"])]=key
        previous=ledger.db.execute("SELECT payload FROM measurements WHERE key=?",(key,)).fetchone()
        if previous:
            try:
                result=json.loads(previous[0]);validate_segmentation(result,row,versions["segmentation"]["version"])
                return Observation(result=result,cached=True)
            except (ValueError,TypeError,KeyError,AttributeError) as exc:
                with ledger.db:
                    ledger.db.execute("INSERT INTO measurement_failures VALUES (?,?,?)",(key,previous[0],str(exc)))
                    ledger.db.execute("DELETE FROM measurements WHERE key=?",(key,))
                runtime["invalid_cache_entries"]+=1
        return None
    observation=None
    def segmentation(row):
        if observation.error:raise observation.error
        if observation.result is None:raise RuntimeError("native observation was not prepared")
        return observation.result
    pipeline=Pipeline(codec,versions,metadata,policy,segmentation,corrector)
    def pending_rows():
        # Payload iteration and all SQLite access happen on this thread only.
        ids=ledger.db.execute("SELECT parent,id FROM observations ORDER BY parent,id").fetchall()
        for parent,i in ids:
            previous=ledger.db.execute("SELECT disposition FROM decisions WHERE parent=? AND id=?",(parent,i)).fetchone()
            if previous and not (retry_errors and previous[0]=="INFRA_ERROR" or retry_holds and previous[0]=="HOLD"):continue
            row=json.loads(ledger.db.execute("SELECT payload FROM observations WHERE parent=? AND id=?",(parent,i)).fetchone()[0])
            row["page_summary"]=ledger.page_summary(row)
            yield row
    try:
        for processed,(row,observation) in enumerate(pool.ordered(pending_rows(),prepare),1):
            runtime["native_attempts"]+=observation.attempted
            runtime["cached_measurements"]+=observation.cached
            runtime["native_seconds_sum"]+=observation.seconds
            key=cache_keys.pop((row["parent_id"],row["id"]),None)
            if isinstance(observation.error,FileNotFoundError):
                runtime["unavailable"]+=1
                observation.result=dict(binding=identity(row),raw_text_sha256=digest(row["raw_text"]),tool_version=versions["segmentation"]["version"],verdict="UNCERTAIN",reason=str(observation.error),availability="unavailable")
                observation.error=None
            elif observation.attempted and observation.error is None:
                try:
                    validate_segmentation(observation.result,row,versions["segmentation"]["version"])
                    encoded=canonical(observation.result)
                except (ValueError,TypeError,KeyError,AttributeError) as exc:
                    with ledger.db:ledger.db.execute("INSERT INTO measurement_failures VALUES (?,?,?)",(key,repr(observation.result),str(exc)))
                    observation.result=None;observation.error=exc
                else:
                    with ledger.db:ledger.db.execute("INSERT INTO measurements VALUES (?,?)",(key,encoded))
            try:decision=pipeline.evaluate(row)
            except (KeyboardInterrupt,SystemExit):raise
            except Exception as exc:
                decision=dict(binding=identity(row),disposition="INFRA_ERROR",admitted=False,reasons=[dict(reason="infrastructure_or_invalid_evidence",error_type=type(exc).__name__,detail=str(exc))])
            ledger.save_decision(row,decision)
            if processed%100==0:atomic_json(out/"progress.json",dict(ledger.summary(detailed=False),stage="filtering"))
        ledger.mark("rows_complete",ledger.generation())
        ledger.deduplicate()
        ledger.mark("rows_complete",ledger.generation())
        ledger.mark("dedup_complete",ledger.generation())
        ledger.export(out)
    finally:
        active_exception=sys.exc_info()[0] is not None
        cleanup_errors=[]
        try:cleanup_errors=pool.close()
        finally:
            runtime["filtering_and_export_seconds"]=time.monotonic()-started
            runtime["cleanup_errors"]=cleanup_errors
            try:atomic_json(out/"runtime.json",runtime)
            finally:
                try:atomic_json(out/"progress.json",ledger.summary())
                finally:ledger.db.close()
        if cleanup_errors and not active_exception:
            raise RuntimeError("native cleanup failed; see runtime.json")
    return json.loads((out/"summary.json").read_text())


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config",type=Path);parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--execute",action="store_true");parser.add_argument("--allow-local",action="store_true")
    parser.add_argument("--retry-errors",action="store_true")
    parser.add_argument("--retry-holds",action="store_true")
    args=parser.parse_args();result=run(json.loads(args.config.read_text()),args.out,execute=args.execute,allow_local=args.allow_local,retry_errors=args.retry_errors,retry_holds=args.retry_holds)
    print(canonical({k:v for k,v in result.items() if k not in {"by_stratum","outputs"}}))


if __name__=="__main__":main()
