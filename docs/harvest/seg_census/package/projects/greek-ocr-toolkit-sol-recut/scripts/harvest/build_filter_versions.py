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
      "numerics":("0.2",["N1 automatic ink candidate (rejected 0/5)","N1 assisted two-reader and lead-pixel release"],
          [PROJECTS/"greek-ocr-toolkit-secondary/artifacts/n1/n1_v1_w1.jsonl"],"assisted separator corrections; failed automatic candidate is disabled"),
      "dashes":("0.1",["dash tags; no general repair release"],[ROOT/"greekocr/harvest/line_pipeline.py"],"tag only"),
      "segmentation":("0.5",["29fa466 crop guides","5d664bf font normalized","cad8709 target-box normalization","b2f8d95 whole-word tolerance","405d4f1 padding 1.5 heights"],
          [ROOT/"greekocr/harvest/filtering_assets/segmentation-policy.js",ROOT/"greekocr/harvest/filtering_assets/crop-tools.py",ROOT/"greekocr/harvest/filtering_assets/font-models.json",ROOT/"greekocr/harvest/filtering_assets/service.mjs",
           ROOT/"greekocr/harvest/filtering_assets/collector/collect_v3/vendor/geometry/ownership.py",ROOT/"greekocr/harvest/filtering_assets/collector/collect_v3/vendor/geometry/magnitude.py"],"owner accepted current decisions unchanged on 2026-10-18"),
    }
    for tool in ("content_gate","content_repair","composer","final_eligibility","census"):
        definitions[tool]=("0.2",["first integrated graph implementation","Astra review: composed coverage, producer binding and atomic exports"],
            [ROOT/"greekocr/harvest/line_pipeline.py",ROOT/"greekocr/harvest/line_pipeline_census.py"],
            "evidence-backed external repair interface; missing evidence holds" if tool=="content_repair" else "existing toolkit primitives with new orchestration")
    definitions["inventory"]=("0.1",["first integrated graph implementation"],[ROOT/"greekocr/harvest/line_pipeline.py"],"existing toolkit inventory primitives")
    version,history,paths,scope=definitions["census"]
    definitions["census"]=("0.5",history+["bounded parallel native workers for CSCS","profiled CSCS throughput tuning with bounded queue lookahead and node-scale worker qualification","parent-confirmed collection-v2 legacy evaluation split aliases with retained lineage"],paths+[ROOT/"greekocr/harvest/line_pipeline_sources.py",ROOT/"greekocr/harvest/line_pipeline_parallel.py",ROOT/"greekocr/harvest/line_pipeline_native.py",ROOT/"greekocr/harvest/line_pipeline_runtime.py",ROOT/"greekocr/harvest/geometry_observations.py",*[ROOT/"scripts/harvest/clariden"/name for name in ("worker.py","bootstrap.py","filter_crop_paths.py","filter_worker.sbatch","package.py")]],scope)
    tools={}
    for name,(version,iterations,paths,scope) in definitions.items():
        components={str(path.relative_to(PROJECTS)):hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
        encoded=json.dumps(components,sort_keys=True,separators=(",",":"))
        tools[name]=dict(version=version,documented_iterations=iterations,iteration_count=len(iterations),scope=scope,
            components=components,digest=hashlib.sha256(encoded.encode()).hexdigest())
    return dict(schema="ocr-filter-tool-versions-v1",versioning="0.n: documented named method generations, not commit count, accuracy or number of individual edits. Rejected generations remain in history. Previously undocumented patch rounds are not invented; exact source hashes identify patches within a named generation.",
        owner_decisions=dict(segmentation="accepted_as_is; no threshold/detector tuning or new segmentation qualification required for this implementation task"),tools=tools)


if __name__=="__main__":
    target=ROOT/"docs/harvest/line_pipeline/tool_versions.json";target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(build(),ensure_ascii=False,indent=2)+"\n")
    print(target)
