"""Read-only pilot diagnostic. All writes are confined to this directory.

One process, one numerical thread, network denied, actual nice >=15 required.
Run with inherited nice >=15 (this session is already nice 20):
  .venv/bin/python -B docs/harvest/recut_v1/v2_pilot/diag/run_diag.py
"""
from __future__ import annotations

import os
import sys

sys.dont_write_bytecode = True
for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS"):
    os.environ[name] = "1"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import resource
import shutil
import time

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[4]
PILOT = Path.home() / "Projects/collect-v3-data/v2_masked/pilot"
MASKING = ROOT / "docs/harvest/recut_v1/masking"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(BASE))


def install_guard():
    if os.getpriority(os.PRIO_PROCESS, 0) < 15:
        raise RuntimeError("actual nice >=15 required")
    if BASE.resolve() != BASE:
        raise RuntimeError("symlinked diagnostic path")
    def writable(path):
        if isinstance(path, int):
            return
        if not Path(os.fsdecode(path)).absolute().resolve().is_relative_to(BASE):
            raise PermissionError(f"write outside diag: {path}")
    def audit(event, args):
        if event.startswith("socket.") and event not in ("socket.__new__",):
            raise PermissionError("T6c1b network OFF")
        if event == "open" and args[2] & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
            writable(args[0])
        elif event in ("os.mkdir", "os.remove", "os.rmdir", "os.chmod", "os.truncate"):
            writable(args[0])
        elif event in ("os.rename", "os.link", "os.symlink"):
            writable(args[0]); writable(args[1])
    sys.addaudithook(audit)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def rows(path):
    return [json.loads(s) for s in path.read_text().splitlines() if s.strip()]


def compressed(path):
    return json.loads(gzip.decompress(path.read_bytes()))


def counts(records, key):
    c = Counter(r[key] for r in records)
    return {k: c[k] for k in ("matched", "ambiguous", "unmatched")}


def page_analysis(page, curves):
    import numpy as np
    from matcher import candidates, match, runtime_fit, status, overlap_fraction
    fits = [runtime_fit(c) for c in curves]
    records = []
    for row in page["lines"]:
        box = row["crop_bbox"]
        before = candidates(box, fits)
        after = candidates(box, fits, min_horizontal_overlap=.5)
        bi = match(box, fits)
        ai = match(box, fits, min_horizontal_overlap=.5)
        assert bi == (before[0]["index"] if before else None)
        assert ai == (after[0]["index"] if after else None)
        # Nearby rejected curves are shown for miss/merge attribution. Distances
        # are observations only and never enter a second matching/scoring rule.
        x0,y0,x1,y1 = box
        nearby = []
        for i, f in enumerate(fits):
            overlap = overlap_fraction(box, f)
            if not overlap:
                continue
            xs = np.arange(max(x0,f.x0), min(x1,f.x1), dtype=float)
            base = np.interp(xs, np.arange(f.x0,f.x1), curves[i]["baseline"])
            mean = np.interp(xs, np.arange(f.x0,f.x1), curves[i]["meanline"])
            if float(min(mean.min(), base.min())) < y1+150 and float(max(mean.max(),base.max())) > y0-150:
                d = abs(float(np.median(f.base_at(np.arange(x0,x1,dtype=float))))-(y0+y1)/2)/max(1,f.xh)
                nearby.append(dict(index=i, distance_xh=d, overlap=overlap,
                                   x0=f.x0,x1=f.x1,xheight=f.xh,
                                   mean_at_crop=float(np.median(mean)), base_at_crop=float(np.median(base))))
        records.append(dict(id=row["id"],crop_bbox=box,before=status(before),after=status(after),
                            before_index=bi,after_index=ai,before_candidates=before,after_candidates=after,
                            nearby=sorted(nearby,key=lambda r:(r["distance_xh"],r["index"]))))
    return records


def pilot_pages():
    from PIL import Image
    sample = json.loads((PILOT / "sample.json").read_text())
    selected = [next(p for p in sample if p["wave"] == w) for w in ("parliament", "vouli")]
    out = []
    for p in selected:
        started = time.monotonic()
        assert sha(p["raster"]) == p["scan"]["sha"]
        name = p["wave"] + "--" + p["page_id"]
        external = PILOT / "curves" / (name + ".json.gz")
        local = BASE / (name + ".curves.json.gz")
        if external.exists():
            curves = compressed(external)
            observed = dict(curves_origin=str(external), curves_sha256=sha(external), detector_rerun=False)
            receipt = json.loads((PILOT / "pages" / (name + ".json")).read_text())
            assert receipt["curves_sha256"] == observed["curves_sha256"]
        elif local.exists():
            value = compressed(local)
            assert value["raster_sha256"] == p["scan"]["sha"]
            for path, digest in value["source_hashes"].items():
                assert sha(ROOT/path) == digest
            curves = value["curves"]
            observed = value["observation"] | dict(curves_sha256=sha(local), curves_origin=str(local))
        else:
            from greekocr.pages import process_page
            from greekocr.pages.lines import CURVES
            with Image.open(p["raster"]) as native:
                t = time.monotonic()
                result = process_page(native)
            curves = []
            for line in result.segmentation.lines:
                if line.discounted is not None:
                    continue
                c = dict(x0=line.x0,x1=line.x1,xheight=line.xheight)
                c.update({k:getattr(line,k).tolist() for k in CURVES})
                curves.append(c)
            observed = dict(detector_rerun=True,detector_seconds=time.monotonic()-t,
                            nice=os.getpriority(os.PRIO_PROCESS,0),threads=1,workers=1)
            source_hashes = {k:sha(ROOT/k) for k in json.loads((MASKING/"params.json").read_text())["source_hashes"]}
            write_value = dict(curves=curves,raster_sha256=p["scan"]["sha"],source_hashes=source_hashes,observation=observed)
            local.write_bytes(gzip.compress(json.dumps(write_value,allow_nan=False).encode(),mtime=0))
            observed.update(curves_origin=str(local),curves_sha256=sha(local))
        rr = page_analysis(p,curves)
        if p["wave"] == "parliament":
            saved_path = PILOT/"lines"/(name+".jsonl")
            saved = {r["id"]:r for r in rows(saved_path)}
            for r in rr:
                old = saved[r["id"]]
                assert old["runtime_index"] == r["before_index"]
                assert old["candidates"] == r["before_candidates"]
                status = "matched" if old["match_status"] == "ok" else old["match_status"]
                assert status == r["before"]
            observed.update(pilot_records_sha256=sha(saved_path),pilot_record_reproduction=True)
        write(BASE/(name+".matches.json"),rr)
        out.append(dict(wave=p["wave"],page_id=p["page_id"],raster=p["raster"],
                        raster_sha256=p["scan"]["sha"],size=[p["scan"]["w"],p["scan"]["h"]],
                        lines=len(rr),curves=len(curves),before=counts(rr,"before"),after=counts(rr,"after"),
                        matching_index_differences=sum(r["before_index"]!=r["after_index"] for r in rr),
                        candidate_set_differences=sum(r["before_candidates"]!=r["after_candidates"] for r in rr),
                        seconds=time.monotonic()-started,**observed))
        print(p["wave"],out[-1]["before"],out[-1]["after"],flush=True)
    write(BASE/"pages.json",out)


def f2_check():
    from matcher import candidates,match,original_match,runtime_fit,status
    dev = rows(MASKING/"dev/records.jsonl")
    dev_ids = {r["id"] for r in dev}
    dev_pages = {r["page_id"] for r in dev}
    f2 = rows(MASKING/"f2/records.jsonl")
    groups=defaultdict(list)
    for r in f2:
        groups[r["page_id"]].append(r)
    checks=[]; bindings=[]
    frozen = json.loads((MASKING/"params.json").read_text())
    for k,v in frozen["source_hashes"].items():
        assert sha(ROOT/k)==v
    for page_id,group in groups.items():
        path=MASKING/group[0]["runtime_curves_path"]
        value=compressed(path)
        assert value["binding"]["source_hashes"]==frozen["source_hashes"]
        bindings.append(dict(page_id=page_id,path=str(path.relative_to(ROOT)),sha256=sha(path)))
        fits=[runtime_fit(c) for c in value["lines"]]
        for r in group:
            box=r["old_box"];bi=original_match(box,fits);ai=match(box,fits,min_horizontal_overlap=.5)
            before=candidates(box,fits);after=candidates(box,fits,min_horizontal_overlap=.5)
            checks.append(dict(id=r["id"],page_id=page_id,stratum=r["stratum"],dev_card=r["id"] in dev_ids,
                               dev_page=page_id in dev_pages,saved_index=r["runtime_index"],
                               before_index=bi,after_index=ai,before=status(before),after=status(after),
                               saved_reproduced=bi==r["runtime_index"],default_identical=match(box,fits)==bi,
                               candidates_identical=before==after))
    subsets={}
    for label,rr in (("dev_cards",[r for r in checks if r["dev_card"]]),
                     ("all_lines_on_dev_pages",[r for r in checks if r["dev_page"]]),("all_f2",checks)):
        subsets[label]=dict(lines=len(rr),pages=len({r['page_id'] for r in rr}),before=counts(rr,"before"),after=counts(rr,"after"),
                            saved_index_differences=sum(not r["saved_reproduced"] for r in rr),
                            default_index_differences=sum(not r["default_identical"] for r in rr),
                            index_differences=sum(r["before_index"]!=r["after_index"] for r in rr),
                            candidate_set_differences=sum(not r["candidates_identical"] for r in rr))
    write(BASE/"f2_check.json",dict(subsets=subsets,checks=checks,curve_bindings=bindings,
                                   dev_records_sha256=sha(MASKING/"dev/records.jsonl"),
                                   f2_records_sha256=sha(MASKING/"f2/records.jsonl")))
    print('F2',subsets,flush=True)


def main():
    install_guard()
    parser=argparse.ArgumentParser();parser.add_argument('--f2-only',action='store_true');args=parser.parse_args()
    if not args.f2_only:
        pilot_pages()
    f2_check()
    write(BASE/"execution.json",dict(utc=datetime.now(timezone.utc).isoformat(),nice=os.getpriority(os.PRIO_PROCESS,0),
                                    workers=1,numerical_threads=1,network="OFF; audit hook denies socket operations",
                                    write_scope=str(BASE),free_disk_bytes=shutil.disk_usage(ROOT).free,
                                    peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                                    matcher_sha256=sha(BASE/"matcher.py"),runner_sha256=sha(__file__)))


if __name__=='__main__':
    main()
