#!/usr/bin/env python3
"""Internal-only Anemi page-PDF acquisition; transport/login belong to O4c."""
from __future__ import annotations

import argparse
from contextlib import closing, contextmanager
import datetime
import fcntl
import hashlib
import html
import json
from pathlib import Path
import re
import sys
from urllib.parse import parse_qs, urlencode, urljoin, urlsplit

from o4c_discover_anemi import AnemiHTTP, BASE, authenticate
from o4c_common import EVIDENCE, ROOT, ProbeError, UA, append, read_rows, write_json

DEFAULT_PLAN = ROOT / "out/o4b/anemi/plan.jsonl"
RIGHTS = "CC BY-NC-ND; internal use only"
SCHEMA = "o4b-anemi-1"
OWNER_DECISION = "2026-10-08 10:50 Europe/Athens; internal training/evaluation; never redistribute"


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def positive_int(value):
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else None


def public_url(url, endpoint=None):
    parts = urlsplit(url)
    if parts.scheme != "https" or parts.netloc != urlsplit(BASE).netloc:
        raise ProbeError("expected public Anemi HTTPS URL")
    if endpoint and parts.path != endpoint:
        raise ProbeError("unexpected Anemi viewer endpoint")
    if parts.fragment or any(re.search(r"cookie|session|phpsess|token|password|username", key, re.I)
                             for key in parse_qs(parts.query)):
        raise ProbeError("private URL parameters excluded")
    return url


def record_key(record_id):
    return hashlib.sha256(record_id.encode()).hexdigest()[:24]


def volumes_for(row):
    """Deduplicate attachments within a record, retaining every distinct volume."""
    scans = row.get("scan_files") or []
    if not scans and row.get("download_url"):
        scans = [{"url": row["download_url"], "pages": row.get("pages"), "format": "PDF"}]
    result = {}
    for scan in scans:
        url = scan.get("url", "")
        if not urlsplit(url).path.lower().endswith(".pdf"):
            continue
        on_anemi = urlsplit(url).netloc == urlsplit(BASE).netloc
        if on_anemi:
            public_url(url)
        viewer = scan.get("viewer_url")
        if not viewer and on_anemi:
            viewer = next((v for v in row.get("viewer_urls", [])
                           if parse_qs(urlsplit(v).query).get("do") == [Path(urlsplit(url).path).name]), None)
        if not viewer and on_anemi:
            # This is the documented canonical catalogue viewer, never pdf_dump.
            viewer = BASE + "/php/pdf_pager.php?" + urlencode({
                "rec": row["document_id"], "do": Path(urlsplit(url).path).name, "pageno": 1,
                **({"maxpage": scan["pages"]} if positive_int(scan.get("pages")) else {})})
        if viewer:
            public_url(viewer, "/php/pdf_pager.php")
        params = parse_qs(urlsplit(viewer or "").query)
        rec = params.get("rec", [None])[0]
        if viewer and (rec != row["document_id"] or params.get("do") != [Path(urlsplit(url).path).name]):
            raise ProbeError("canonical record/viewer attachment mismatch")
        pages = positive_int(scan.get("pages"))
        candidate = {"volume_id": record_key(urlsplit(url).path), "source_pdf_url": url,
                     "viewer_url": viewer, "viewer_rec_id": rec, "pages": pages,
                     "pages_basis": "source-declared offered PDF"}
        if url not in result or result[url]["pages"] is None:
            result[url] = candidate
    return sorted(result.values(), key=lambda v: v["source_pdf_url"])


def build_plan(rows):
    records = {}
    for row in rows:
        languages = row.get("language", [])
        if isinstance(languages, str):
            languages = [languages]
        # Individual detail pages spell out languages; the filtered census retains codes.
        codes = set(languages) | set(row.get("catalogue_languages", []))
        year = row.get("year")
        if not codes.intersection({"grc", "gre"}) or not positive_int(year) or not 1800 <= year <= 1950:
            continue
        volumes = volumes_for(row)
        if not volumes:
            continue
        rid = row["document_id"]
        if rid not in records:
            records[rid] = {"schema_version": SCHEMA, "record_id": rid, "title": row.get("title"),
                            "year": year, "language_codes": sorted(codes & {"grc", "gre"}),
                            "rights": RIGHTS, "rights_basis": "owner admission decision",
                            "owner_decision": OWNER_DECISION, "volumes": []}
        merged = {v["source_pdf_url"]: v for v in records[rid]["volumes"]}
        for volume in volumes:
            if volume["source_pdf_url"] not in merged or merged[volume["source_pdf_url"]]["pages"] is None:
                merged[volume["source_pdf_url"]] = volume
        records[rid]["volumes"] = sorted(merged.values(), key=lambda v: v["source_pdf_url"])
        records[rid]["language_codes"] = sorted(set(records[rid]["language_codes"]) | (codes & {"grc", "gre"}))
    for record in records.values():
        record["pages"] = (sum(v["pages"] for v in record["volumes"])
                           if all(v["pages"] is not None for v in record["volumes"]) else None)
        record["estimated_pages"] = sum(v["pages"] or 0 for v in record["volumes"])
        record["viewer_rec_ids"] = sorted({v["viewer_rec_id"] for v in record["volumes"] if v["viewer_rec_id"]})
        record["priority_band"] = "1800-1910" if record["year"] <= 1910 else "1911-1950"
    ranked = sorted(records.values(), key=lambda r: (r["year"] > 1910, r["year"],
                                                    r["pages"] if r["pages"] is not None else float("inf"),
                                                    r["record_id"]))
    for rank, record in enumerate(ranked, 1):
        record["rank"] = rank
    return ranked


def plan(catalogue=EVIDENCE / "anemi.jsonl", prior=EVIDENCE / "anemi_prior_ranking.json", out=DEFAULT_PLAN):
    prior_info = json.loads(Path(prior).read_text())
    records = build_plan(read_rows(catalogue))
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".jsonl.tmp")
    tmp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records))
    tmp.replace(out)
    write_json(out.with_suffix(".meta.json"), {
        "schema_version": SCHEMA, "catalogue_sha256": sha256(catalogue), "prior_ranking_sha256": sha256(prior),
        "prior_ranking": prior_info, "prior_ranking_role": "provenance only; O4c compatible ranking remains unchanged",
        "plan_sha256": sha256(out), "records": len(records),
        "volumes": sum(len(r["volumes"]) for r in records),
        "known_pages": sum(r["estimated_pages"] for r in records),
        "unknown_page_count_volumes": sum(v["pages"] is None for r in records for v in r["volumes"]),
        "ranking": "priority band, year ascending, total pages ascending (unknown last), record ID",
        "owner_decision": OWNER_DECISION, "rights": RIGHTS})
    return records


def pdf_resolution(body):
    """Decode exactly one page and measure its existing raster; never render/recompress."""
    import pypdfium2 as pdfium
    from pypdfium2.raw import FPDF_PAGEOBJ_IMAGE
    try:
        if not body.startswith(b"%PDF-"):
            raise ProbeError("viewer response is not a PDF")
        with pdfium.PdfDocument(body) as doc:
            if len(doc) != 1:
                raise ProbeError("viewer response must contain exactly one page")
            with closing(doc[0]) as page:
                points = list(page.get_size())
                images = []
                for obj in page.get_objects():
                    if obj.type != FPDF_PAGEOBJ_IMAGE:
                        continue
                    width, height = obj.get_px_size()
                    x0, y0, x1, y1 = obj.get_bounds()
                    images.append({"pixels": [width, height],
                                   "dpi_from_placement": [round(width * 72 / abs(x1-x0), 2) if x1 != x0 else None,
                                                          round(height * 72 / abs(y1-y0), 2) if y1 != y0 else None]})
                return {"page_points": points, "images": images,
                        "selection": "published page PDF; no width/height/downsampling parameters",
                        "raster_compression": "source PDF unchanged; losslessness unverified"}
    except ProbeError:
        raise
    except Exception:
        raise ProbeError("page PDF decoding failed") from None


def viewer_descriptor(http, volume):
    public_url(volume["viewer_url"], "/php/pdf_pager.php")
    meta, body = http.get(volume["viewer_url"], limit=1_000_000)
    match = re.search(r"<iframe\b[^>]*src=[\"']([^\"']+)", body.decode("utf-8", "replace"), re.I)
    if not match:
        raise ProbeError("viewer has no published page PDF")
    url = public_url(urljoin(meta["url"], html.unescape(match[1])), "/php/pdf_split.php")
    params = parse_qs(urlsplit(url).query)
    filename = params.get("filename", [""])[0]
    source_path = urlsplit(volume["source_pdf_url"]).path
    if not filename.endswith(source_path) or params.get("pagenum") != ["1"]:
        raise ProbeError("viewer page-PDF attachment mismatch")
    result = {"endpoint": BASE + "/php/pdf_split.php", "filename": filename,
              "source_pdf_url": volume["source_pdf_url"], "viewer_url": volume["viewer_url"],
              "viewer_sha256": meta["sha256"], "derivative": "page_pdf"}
    http.safe(result)
    return result


def page_url(descriptor, index):
    public_url(descriptor["endpoint"], "/php/pdf_split.php")
    if not descriptor["filename"].endswith(urlsplit(descriptor["source_pdf_url"]).path):
        raise ProbeError("saved viewer descriptor does not match attachment")
    return descriptor["endpoint"] + "?" + urlencode({"filename": descriptor["filename"],
                                                       "pageno": index + 1, "pagenum": 1})


def valid_receipt(receipt, directory, record, volume, index):
    """Only a complete source-bound receipt AND a current file hash permit a skip."""
    try:
        if (receipt.get("schema_version") != SCHEMA or receipt.get("rights") != RIGHTS
                or receipt.get("record_id") != record["record_id"] or receipt.get("volume_id") != volume["volume_id"]
                or receipt.get("page_index") != index or receipt.get("status") != 200
                or receipt.get("state") != "saved" or receipt.get("derivative") != "page_pdf"
                or receipt.get("page_number") != index + 1 or receipt.get("viewer_rec_id") != volume["viewer_rec_id"]
                or not isinstance(receipt.get("resolution"), dict) or not positive_int(receipt.get("bytes"))
                or receipt.get("source_pdf_url") != volume["source_pdf_url"]):
            return False
        public_url(receipt["url"], "/php/pdf_split.php")
        params = parse_qs(urlsplit(receipt["url"]).query)
        if (params.get("pageno") != [str(index + 1)] or params.get("pagenum") != ["1"]
                or not params.get("filename", [""])[0].endswith(urlsplit(volume["source_pdf_url"]).path)):
            return False
        if datetime.datetime.fromisoformat(receipt["fetched_at"]).tzinfo is None:
            return False
        expected = f"{volume['volume_id']}/page-{index + 1:06d}.pdf"
        if receipt.get("path") != expected:
            return False
        path = directory / expected
        if not path.resolve().is_relative_to(directory.resolve()):
            return False
        return (path.is_file() and path.stat().st_size == receipt["bytes"] and sha256(path) == receipt["sha256"])
    except (KeyError, TypeError, ValueError, OSError, ProbeError):
        return False


def receipt_rows(path):
    result = []
    if path.exists():
        for line in path.read_text().splitlines():
            try:
                receipt = json.loads(line)
                if isinstance(receipt, dict):
                    result.append(receipt)
            except (ValueError, KeyError, TypeError):
                continue
    return result


def latest_receipts(directory):
    # A process interruption can leave a partial final JSON line. Never treat it as a page receipt.
    return {(r["volume_id"], r["page_index"]): r for r in receipt_rows(directory / "receipts.jsonl")
            if "volume_id" in r and "page_index" in r}


def receipt_identity(receipt):
    return tuple(receipt.get(k) for k in ("record_id", "volume_id", "page_index", "sha256", "state"))


def append_receipt(path, receipt):
    # Separate a torn tail from the next append; old damaged evidence is retained.
    if path.exists() and path.stat().st_size:
        with path.open("rb+") as stream:
            stream.seek(-1, 2)
            if stream.read(1) != b"\n":
                stream.write(b"\n")
    append(path, receipt)


@contextmanager
def destination_lock(dest):
    dest.mkdir(parents=True, exist_ok=True)
    with (dest / "wave.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def selected_indices(record, page_range=None):
    if page_range == "explicit":
        result = {}
        for v in record["volumes"]:
            values = v.get("selected_page_indices", [])
            if values != sorted(set(values)) or any(not isinstance(i, int) or i < 0 or i >= v["pages"] for i in values):
                raise ValueError("explicit indices must be unique sorted in-volume pages")
            result[v["volume_id"]] = values
        return result
    if page_range is None:
        return {v['volume_id']: list(range(v['pages'] or 0)) for v in record['volumes']}
    match = re.fullmatch(r'middle:([1-9][0-9]*)', page_range)
    if not match or any(v['pages'] is None for v in record['volumes']):
        raise ValueError('page-range requires middle:N and known volume lengths')
    count = int(match[1]); total = sum(v['pages'] for v in record['volumes'])
    start = max(0, (total - count) // 2); end = min(total, start + count)
    result = {}; offset = 0
    for v in record['volumes']:
        result[v['volume_id']] = [i for i in range(v['pages']) if start <= offset+i < end]
        offset += v['pages']
    return result


def select_records(plan, selection):
    chosen = json.loads(Path(selection).read_text())
    if isinstance(chosen, dict): chosen = chosen['records']
    ids = [r if isinstance(r, str) else r.get('record_id', r.get('document_id')) for r in chosen]
    by_id = {r['record_id']:r for r in plan}
    if len(set(ids)) != len(ids) or any(i not in by_id for i in ids):
        raise ValueError('selection has duplicate or unknown record IDs')
    return [by_id[i] for i in ids]


def fetch_wave(records, *, wave, max_pages, max_bytes, dest, http_root=EVIDENCE, http_factory=AnemiHTTP,
               login=authenticate, emit=print, page_range=None):
    if any(n < 0 for n in (wave, max_pages, max_bytes)):
        raise ValueError("wave, max-pages and max-bytes must be nonnegative")
    dest = Path(dest)
    with destination_lock(dest):
        selected = json.loads(json.dumps(records[:wave]))
        for r in selected:
            indices = selected_indices(r, page_range)
            for v in r["volumes"]: v["selected_page_indices"] = indices[v["volume_id"]]
        guard = http_factory(interval=2, root=http_root)
        guard.safe(selected)
        manifest_path = dest / "wave_manifest.json"
        if manifest_path.exists():
            saved = json.loads(manifest_path.read_text())
            by_id = {r["record_id"]: r for r in saved["records"]}
            for record in selected:
                old = by_id.get(record["record_id"])
                if old and old != record:
                    def without_selection(value):
                        value = json.loads(json.dumps(value))
                        for v in value["volumes"]: v.pop("selected_page_indices", None)
                        return value
                    if page_range != "explicit" or without_selection(old) != without_selection(record):
                        raise ProbeError("destination record plan changed; use a fresh destination")
                    for ov, nv in zip(old["volumes"], record["volumes"]):
                        nv["selected_page_indices"] = sorted(set(ov["selected_page_indices"]) | set(nv["selected_page_indices"]))
        else:
            by_id = {}
        by_id.update({r["record_id"]: r for r in selected})
        write_json(manifest_path, {"schema_version": SCHEMA, "records": sorted(by_id.values(), key=lambda r: r["rank"]),
                                   "rights": RIGHTS})
        summary = {"selected_records": len(selected), "records": 0, "pages": 0, "skipped_pages": 0,
                   "bytes": 0, "saved_bytes": 0, "errors": [], "stop_reason": "complete"}
        http = None
        started = 0
        global_receipts = {receipt_identity(r) for r in receipt_rows(dest / "ledger.jsonl")}

        def start_http():
            nonlocal http, started
            if http is None:
                http = guard
                started = http.transferred
                # O4c's exhausted discovery cap is historical. Owner-authorized O4b has a new wave cap,
                # charged against the SAME ledger, including robots/login/error/redirect bodies.
                http.budget = started + max_bytes
                login(http)
            return http

        def transferred():
            return http.transferred - started if http is not None else 0

        for record in selected:
            directory = dest / "records" / record_key(record["record_id"])
            directory.mkdir(parents=True, exist_ok=True)
            write_json(directory / "record.json", record)
            receipts = latest_receipts(directory)
            verified = {(v["volume_id"], i) for v in record["volumes"] for i in v.get("selected_page_indices", range(v["pages"] or 0))
                        if valid_receipt(receipts.get((v["volume_id"], i), {}), directory, record, v, i)}
            done = len(verified)
            complete = True
            for volume in record["volumes"]:
                if volume["pages"] is None or volume["viewer_url"] is None:
                    summary["errors"].append({"record_id": record["record_id"], "volume_id": volume["volume_id"],
                                              "error": "source page count unknown; volume not acquired"})
                    complete = False
                    continue
                descriptor = None
                descriptor_path = directory / volume["volume_id"] / "viewer.json"
                for index in volume.get("selected_page_indices", range(volume["pages"])):
                    if (volume["volume_id"], index) in verified:
                        receipt = receipts[(volume["volume_id"], index)]
                        guard.safe(receipt)
                        if receipt_identity(receipt) not in global_receipts:
                            append_receipt(dest / "ledger.jsonl", receipt)
                            global_receipts.add(receipt_identity(receipt))
                        summary["skipped_pages"] += 1
                        continue
                    if summary["pages"] >= max_pages or transferred() >= max_bytes:
                        summary["stop_reason"] = "page-budget" if summary["pages"] >= max_pages else "byte-budget"
                        complete = False
                        break
                    url = None
                    try:
                        client = start_http()
                        if descriptor is None:
                            if descriptor_path.exists():
                                descriptor = json.loads(descriptor_path.read_text())
                                if descriptor["source_pdf_url"] != volume["source_pdf_url"]:
                                    raise ProbeError("saved viewer source mismatch")
                            else:
                                descriptor = viewer_descriptor(client, volume)
                                write_json(descriptor_path, descriptor)
                        url = page_url(descriptor, index)
                        client.safe(url)
                        meta, body = client.get(url, limit=max_bytes - transferred())
                        if meta["url"] != url:
                            raise ProbeError("page response URL changed")
                        if (meta["status"] != 200 or meta.get("truncated")
                                or meta["sha256"] != hashlib.sha256(body).hexdigest()):
                            raise ProbeError("incomplete or mismatched page response")
                        resolution = pdf_resolution(body)
                        relative = f"{volume['volume_id']}/page-{index + 1:06d}.pdf"
                        receipt = {"schema_version": SCHEMA, "record_id": record["record_id"],
                                   "volume_id": volume["volume_id"], "page_index": index, "page_number": index + 1,
                                   "source_pdf_url": volume["source_pdf_url"], "viewer_rec_id": volume["viewer_rec_id"],
                                   "url": url, "status": meta["status"], "bytes": len(body), "sha256": meta["sha256"],
                                   "fetched_at": meta["fetched_at"], "path": relative, "state": "saved",
                                   "derivative": "page_pdf", "resolution": resolution, "rights": RIGHTS}
                        client.safe(receipt)
                        path = directory / relative
                        path.parent.mkdir(parents=True, exist_ok=True)
                        temp = path.with_suffix(".pdf.part")
                        temp.write_bytes(body)
                        temp.replace(path)
                        append_receipt(directory / "receipts.jsonl", receipt)
                        append_receipt(dest / "ledger.jsonl", receipt)
                        global_receipts.add(receipt_identity(receipt))
                        summary["pages"] += 1
                        summary["saved_bytes"] += len(body)
                        done += 1
                        emit(f"ANEMI_PROGRESS record={record['record_id']} pages={done}/{record['pages']} bytes={transferred()}")
                    except (ProbeError, OSError, ValueError, KeyError):
                        # Exception text and authenticated response bodies never enter logs/files.
                        tail = read_rows(http.ledger)[-1:] if http is not None else []
                        if url and tail and tail[0]["url"] == url:
                            meta = tail[0]
                            failed = {"schema_version": SCHEMA, "record_id": record["record_id"],
                                      "volume_id": volume["volume_id"], "page_index": index,
                                      "source_pdf_url": volume["source_pdf_url"], "state": "failed",
                                      "derivative": "page_pdf", "rights": RIGHTS,
                                      **{k: meta[k] for k in ("url", "status", "bytes", "sha256", "fetched_at", "truncated")}}
                            http.safe(failed)
                            append_receipt(directory / "receipts.jsonl", failed)
                            append_receipt(dest / "ledger.jsonl", failed)
                        budget_stop = http is not None and (http.transferred >= http.budget or
                            any(m.get("truncated") for m in tail))
                        if budget_stop:
                            summary["stop_reason"] = "byte-budget"
                        else:
                            summary["stop_reason"] = "errors"
                            summary["errors"].append({"record_id": record["record_id"], "volume_id": volume["volume_id"],
                                                      "page_index": index, "error": "page acquisition failed; inspect public transport ledger"})
                        complete = False
                        if budget_stop:
                            break
                        # Fail this volume closed; a later invocation retries its first gap.
                        break
                if summary["stop_reason"] != "complete":
                    break
            if complete:
                summary["records"] += 1
            emit(f"ANEMI_PROGRESS record={record['record_id']} pages={done}/{record['pages']} bytes={transferred()}")
            if summary["stop_reason"] != "complete":
                break
        summary["bytes"] = transferred()
        if summary["errors"] and summary["stop_reason"] == "complete":
            summary["stop_reason"] = "errors"
        summary["transport_ledger"] = str(Path(http_root) / "transfer.jsonl")
        summary["transport_start_bytes"] = started if http is not None else None
        summary["user_agent"] = UA
        write_json(dest / "last_wave.json", summary)
        emit(f"ANEMI_WAVE_DONE records={summary['records']} pages={summary['pages']} bytes={summary['bytes']}")
        return summary


def verify(dest):
    dest = Path(dest)
    manifest = json.loads((dest / "wave_manifest.json").read_text())
    report = {"records": len(manifest["records"]), "complete_records": 0, "pages": 0, "bytes": 0,
              "missing_pages": 0, "invalid_pages": 0, "unknown_page_count_volumes": 0, "gaps": [],
              "unreceipted_files": [], "global_ledger_gaps": []}
    global_receipts = {receipt_identity(r) for r in receipt_rows(dest / "ledger.jsonl")}
    for record in manifest["records"]:
        directory = dest / "records" / record_key(record["record_id"])
        receipts = latest_receipts(directory)
        complete = True
        expected_files = set()
        for volume in record["volumes"]:
            if volume["pages"] is None:
                report["unknown_page_count_volumes"] += 1
                report["gaps"].append({"record_id": record["record_id"], "volume_id": volume["volume_id"],
                                       "reason": "unknown-page-count"})
                complete = False
            for index in volume.get("selected_page_indices", range(volume["pages"] or 0)):
                receipt = receipts.get((volume["volume_id"], index), {})
                expected_files.add(f"{volume['volume_id']}/page-{index + 1:06d}.pdf")
                if valid_receipt(receipt, directory, record, volume, index):
                    report["pages"] += 1
                    report["bytes"] += receipt["bytes"]
                    if receipt_identity(receipt) not in global_receipts:
                        report["global_ledger_gaps"].append({"record_id": record["record_id"],
                                                            "volume_id": volume["volume_id"], "page_index": index})
                else:
                    reason = "invalid-receipt-or-file" if receipt else "missing-receipt"
                    report["invalid_pages" if receipt else "missing_pages"] += 1
                    report["gaps"].append({"record_id": record["record_id"], "volume_id": volume["volume_id"],
                                           "page_index": index, "reason": reason})
                    complete = False
        for path in directory.rglob("*.pdf"):
            relative = str(path.relative_to(directory))
            if relative not in expected_files or not any(r.get("path") == relative for r in receipts.values()):
                report["unreceipted_files"].append(str(path.relative_to(dest)))
        report["complete_records"] += int(complete)
    report["ok"] = not report["gaps"] and not report["unreceipted_files"] and not report["global_ledger_gaps"]
    return report


def nonnegative(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("must be nonnegative")
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("plan")
    p.add_argument("--catalogue", type=Path, default=EVIDENCE / "anemi.jsonl")
    p.add_argument("--prior-ranking", type=Path, default=EVIDENCE / "anemi_prior_ranking.json")
    p.add_argument("--out", type=Path, default=DEFAULT_PLAN)
    p = commands.add_parser("fetch")
    p.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    p.add_argument("--records", type=Path, help="JSON selected record IDs or proposal rows")
    p.add_argument("--page-range", help="middle:N pages per record, spanning volumes")
    p.add_argument("--wave", type=nonnegative, required=True, help="top N catalogue records")
    p.add_argument("--max-pages", type=nonnegative, required=True, help="newly saved pages this invocation")
    p.add_argument("--max-bytes", type=nonnegative, required=True, help="all new HTTP response bytes this invocation")
    p.add_argument("--dest", type=Path, required=True)
    p.add_argument("--http-root", type=Path, default=EVIDENCE, help="shared O4c ledger/lock/rate-state root")
    p = commands.add_parser("verify")
    p.add_argument("dest", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "plan":
            records = plan(args.catalogue, args.prior_ranking, args.out)
            print(f"ANEMI_PLAN records={len(records)} volumes={sum(len(r['volumes']) for r in records)} pages={sum(r['estimated_pages'] for r in records)}")
        elif args.command == "fetch":
            records = read_rows(args.plan)
            if args.records: records = select_records(records, args.records)
            summary = fetch_wave(records, wave=args.wave, max_pages=args.max_pages,
                                 max_bytes=args.max_bytes, dest=args.dest, http_root=args.http_root, page_range=args.page_range)
            return int(bool(summary["errors"]))
        else:
            report = verify(args.dest)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return int(not report["ok"])
    except KeyboardInterrupt:
        print("ANEMI_STOP interrupted; committed page receipts remain resumable", file=sys.stderr)
        return 130
    except (ProbeError, OSError, ValueError, KeyError):
        print("ANEMI_ERROR operation failed; no private exception details logged", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
