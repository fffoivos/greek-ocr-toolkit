"""Record documented tool generations and exact component fingerprints."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[2]
PROJECTS=ROOT.parent


def build():
    definitions={
      "polytonic":("0.7",["S1","S2","S3","S4","S5","SF6","SF7"],
          [PROJECTS/"greek-ocr-toolkit-spellcheck/scripts/labelfix/release_gate_sf7.py"],"SF7 A; existing detector/readers; exact release candidate_pre_audit"),
      "cyrillic":("0.3",["ru1_v1","ru1_v2_train","ru1_v3_edits"],
          [PROJECTS/"greek-ocr-toolkit-secondary/scripts/secondary/ru1_decide.py",PROJECTS/"greek-ocr-toolkit-secondary/artifacts/ru1/ru1_v3_edits.jsonl"],"historical Russian ь→ъ only"),
      "numerics":("0.3",["N1 automatic ink candidate (rejected 0/5)","N1 assisted two-reader and lead-pixel release","census_03 integration: digit/separator/digit adjacency for automatic candidate negatives"],
          [PROJECTS/"greek-ocr-toolkit-secondary/artifacts/n1/n1_v1_w1.jsonl",ROOT/"greekocr/harvest/line_pipeline.py"],"assisted separator corrections; failed automatic candidate is disabled"),
      "dashes":("0.1",["dash tags; no general repair release"],[ROOT/"greekocr/harvest/line_pipeline.py"],"tag only"),
      "segmentation":("0.13",["29fa466 crop guides","5d664bf font normalized","cad8709 target-box normalization","b2f8d95 whole-word tolerance","405d4f1 padding 1.5 heights","0.5 + row-frame text box","crop-only line inventory and cut-off gate before length","owner's three rules; remove target-cut veto and taller-than-upright guard","every letter body >=95% visible for a whole neighbour word","every h > w crop turns 90 degrees right before all detection and measurement","main-row ink measured along its existing base curve","small segments use every ink component in the processed crop frame","length band 0.30–2.00 (coordinator decision under the owner's end-to-end mandate, 19 Oct 21:34; fitted on owner marks, s5)"],
          [ROOT/"greekocr/glyphs/components.py",ROOT/"greekocr/harvest/line_pipeline_native.py",ROOT/"greekocr/harvest/filtering_assets/segmentation-policy.js",ROOT/"greekocr/harvest/filtering_assets/crop-tools.py",ROOT/"greekocr/harvest/filtering_assets/font-models.json",ROOT/"greekocr/harvest/filtering_assets/service.mjs",
           ROOT/"greekocr/harvest/filtering_assets/collector/collect_v3/vendor/geometry/ownership.py",ROOT/"greekocr/harvest/filtering_assets/collector/collect_v3/vendor/geometry/magnitude.py"],"0.9-s5: one length band 0.30–2.00 for all rows; S4 measurement, small path, mode 2, padding 1.5 and gate unchanged"),
    }
    for tool in ("content_gate","content_repair","composer","final_eligibility","census"):
        definitions[tool]=("0.2",["first integrated graph implementation","Astra review: composed coverage, producer binding and atomic exports"],
            [ROOT/"greekocr/harvest/line_pipeline.py",ROOT/"greekocr/harvest/line_pipeline_census.py"],
            "evidence-backed external repair interface; missing evidence holds" if tool=="content_repair" else "existing toolkit primitives with new orchestration")
    version,history,paths,scope=definitions["content_gate"]
    definitions["content_gate"]=("0.3",history+["owner gate: mixed-script word drops, unexpected script holds, before segmentation; short ordinary lines excluded before segmentation (letters); cells and numeric lines exempt with more than one letter-or-digit"],paths,scope)
    version,history,paths,scope=definitions["final_eligibility"]
    definitions["final_eligibility"]=("0.3",history+["cells: alnum > 1 is the only length/shape check, consistent with the gate"],paths,scope)
    version,history,paths,scope=definitions["composer"]
    definitions["composer"]=("0.3",history+["PIPE032: declared routes_out_of_scope bypass correction lookup and automatic results; retain explicit non-success route evidence"],paths,scope)
    definitions["inventory"]=("0.1",["first integrated graph implementation"],[ROOT/"greekocr/harvest/line_pipeline.py"],"existing toolkit inventory primitives")
    version,history,paths,scope=definitions["census"]
    definitions["census"]=("0.6",history+["bounded parallel native workers for CSCS","profiled CSCS throughput tuning with bounded queue lookahead and node-scale worker qualification","parent-confirmed collection-v2 legacy evaluation split aliases with retained lineage","census_03 integration: union configured heldout_crop_sha256 with observed held-out crops"],paths+[ROOT/"greekocr/harvest/line_pipeline_sources.py",ROOT/"greekocr/harvest/line_pipeline_parallel.py",ROOT/"greekocr/harvest/line_pipeline_native.py",ROOT/"greekocr/harvest/line_pipeline_runtime.py",ROOT/"greekocr/harvest/geometry_observations.py",*[ROOT/"scripts/harvest/clariden"/name for name in ("worker.py","bootstrap.py","filter_crop_paths.py","filter_worker.sbatch","package.py")]],scope)
    version,history,paths,scope=definitions["census"]
    definitions["census"]=("0.7",history+["PIPE032: bind release correction scope; export corrections_not_applied and count routed rows by tool and disposition"],paths,scope)
    tools={}
    for name,(version,iterations,paths,scope) in definitions.items():
        components={str(path.relative_to(PROJECTS)):hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
        encoded=json.dumps(components,sort_keys=True,separators=(",",":"))
        tools[name]=dict(version=version,documented_iterations=iterations,iteration_count=len(iterations),scope=scope,
            components=components,digest=hashlib.sha256(encoded.encode()).hexdigest())
    tools["segmentation"]["label"]="0.9-s5"
    return dict(schema="ocr-filter-tool-versions-v1",versioning="0.n: documented named method generations, not commit count, accuracy or number of individual edits. Rejected generations remain in history. Previously undocumented patch rounds are not invented; exact source hashes identify patches within a named generation.",
        coordinator_decisions=dict(polytonic_release_scope="20 Oct: census_05 runs with polytonic out of scope under the owner's end-to-end mandate; routed rows retain raw Google labels for polytonic, with other in-scope edits and checks unchanged; SF7 enters when its audit passes; coordinator decision, not an owner ruling",segmentation_s5="0.30–2.00 adopted under the owner's end-to-end mandate (you don't have to wait for me, resolve these end to end); coordinator ledger 19 Oct 21:34; reported to owner: frozen the configuration at 0.9-s4 measurement, gate 0.3, band 0.30–2.00, one band for everything; no objection reported since; coordinator decision, not an owner ruling"),
        owner_decisions=dict(segmentation="accepted_as_is; no threshold/detector tuning or new segmentation qualification required for this implementation task"),tools=tools)


if __name__=="__main__":
    target=ROOT/"docs/harvest/line_pipeline/tool_versions.json";target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(build(),ensure_ascii=False,indent=2)+"\n")
    print(target)
