"""Offline REG1 validation; run with python3 (stdlib only, no writes)."""

import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INPUT = Path.home() / "Projects/greek-ocr-toolkit-secondary/artifacts/n1/n1_locked_eval_line_ids_alt.txt"
RUN = Path.home() / "Projects/collect-v3-data/run"
ADMISSIONS = ROOT.parent / "release_admissions/w1_masked_1d.jsonl"
SUMMARY = ROOT.parent / "release_admissions/w1_masked_1d_summary.json"
EXPECTED_SHA = "3d6f0d29edf728514f0721ded09b9f3df65cbe352f70814e8bcbe49f51c430fe"
EXPECTED_COUNTS = {"elstat": 88, "gazette_1982_1985": 78, "gazette_1986_1990": 92}


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def overlap(ids, other):
    hits = sorted(ids.intersection(other))
    return {"n": len(hits), "ids": hits}


def compute():
    # Fail before using the supplied IDs if the input bytes differ.
    assert sha(INPUT) == EXPECTED_SHA, "STOP: input sha256 mismatch"
    lines = INPUT.read_text().splitlines()
    ids = set(lines)
    assert len(lines) == len(ids) == 258, "STOP: count or uniqueness mismatch"
    counts = Counter()
    matched = Counter()
    with (RUN / "W1/features.jsonl").open() as stream:
        for line in stream:
            row = json.loads(line)
            if row["id"] not in ids:
                continue
            matched[row["id"]] += 1
            if row["source"] == "elstat":
                source = "elstat"
            else:
                assert row["source"] == "gazette_modern"
                year = int(row["year"])
                assert 1982 <= year <= 1990
                source = "gazette_1982_1985" if year <= 1985 else "gazette_1986_1990"
            counts[source] += 1
    assert set(matched) == ids and all(n == 1 for n in matched.values()), "STOP: missing/duplicate W1 IDs"
    assert dict(counts) == EXPECTED_COUNTS, "STOP: source counts mismatch"

    manifest = json.loads((ROOT / "release_exclusions.json").read_text())
    classes = {}
    for name, entry in manifest["classes"].items():
        if name == "n1_locked_eval":
            continue
        classes[name] = overlap(ids, (ROOT / entry["file"]).read_text().splitlines())
        assert classes[name]["n"] == (6 if name == "rotated_crop" else 0), "STOP: unexpected exclusion overlap"

    arms = {name: set() for name in ("wave-1d", "wave-1d only", "release-v3-candidate")}
    arm_rows = Counter()
    with ADMISSIONS.open() as stream:
        for line in stream:
            row = json.loads(line)
            assert row["arm"] in arms, "STOP: unrecognized admission arm"
            arms[row["arm"]].add(row["row_id"])
            arm_rows[row["arm"]] += 1
    arm_overlaps = {name: overlap(ids, rows) for name, rows in arms.items()}
    assert arm_overlaps["wave-1d"]["n"] == arm_overlaps["wave-1d only"]["n"] == 0, "STOP: wave-1d overlap"
    assert arm_overlaps["release-v3-candidate"]["n"] == 0, "STOP: candidate overlap"
    w2 = RUN / "W2/features.jsonl"
    w2_ids = set()
    if w2.exists():
        with w2.open() as stream:
            for line in stream:
                row = json.loads(line)
                if row["id"] in ids:
                    w2_ids.add(row["id"])
    w2_overlap = {"file": str(w2), "exists": w2.exists(), **overlap(ids, w2_ids)}
    assert w2_overlap["n"] == 0, "STOP: W2 overlap"
    summary = json.loads(SUMMARY.read_text())
    return {
        "file": "n1_locked_eval_ids.txt",
        "n": 258,
        "sha256": EXPECTED_SHA,
        "owner": "secondary-corrections lead (N1)",
        "provenance": {
            "repo": "greek-ocr-toolkit-secondary",
            "branch": "opus/secondary-corrections",
            "commit": "b85a40e7c",
            "input_file": "artifacts/n1/n1_locked_eval_line_ids_alt.txt",
            "receipt": "artifacts/n1/N1L_RECEIPT.json",
        },
        "rule": "locked evaluation lines (62 reserved documents); never admitted to training",
        "id_format": "collect_v3 W1 row id (features.jsonl id)",
        "per_source": EXPECTED_COUNTS,
        "w1_id_existence": {"checked": 258, "missing": 0, "duplicate_matches": 0},
        "overlaps": {
            "admissions_file": "../release_admissions/w1_masked_1d.jsonl",
            "admissions_sha256": sha(ADMISSIONS),
            "admission_arm_rows": {name: arm_rows[name] for name in arms},
            "admission_arms": arm_overlaps,
            "wave_1d": overlap(ids, arms["wave-1d"] | arms["wave-1d only"]),
            "existing_exclusion_classes": classes,
            "rotated_crop_note": "6 expected and harmless overlaps; both classes exclude these lines",
            "w2": w2_overlap,
        },
        "admission_summary_binding": {
            "file": "../release_admissions/w1_masked_1d_summary.json",
            "release_exclusions_sha256": summary["release_exclusions_sha256"],
            "note": "w1_masked_1d_summary.json binds the previous release_exclusions sha; wave-1d overlap is 0 (including the legacy literal arm 'wave-1d only'). Admissions and the stratum gate are unchanged.",
        },
    }


if __name__ == "__main__":
    expected = compute()
    manifest = json.loads((ROOT / "release_exclusions.json").read_text())
    assert manifest["classes"]["n1_locked_eval"] == expected, "registered evidence differs from recomputed checks"
    copied = ROOT / expected["file"]
    assert copied.read_bytes() == INPUT.read_bytes(), "copy is not byte-identical"
    assert sha(copied) == EXPECTED_SHA
    print("PASS: sha256, byte identity, 258 unique W1 IDs, source counts, overlaps, JSON validity")
    print("release_exclusions sha256:", sha(ROOT / "release_exclusions.json"))
