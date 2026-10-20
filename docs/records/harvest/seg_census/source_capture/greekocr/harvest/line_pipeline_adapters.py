"""Adapters for existing SF7, RU1 and N1 ledgers. No new OCR or voting rules."""
from __future__ import annotations

from .line_pipeline import digest, identity, span_edits, merge_edits, canonical


def byte_edits(raw, patches):
    encoded = raw.encode("utf-8")
    edits = []
    for patch in patches:
        a, b = patch["raw_byte_start"], patch["raw_byte_end"]
        if type(a) is not int or type(b) is not int or not 0 <= a <= b <= len(encoded):
            raise ValueError("invalid UTF-8 patch offsets")
        # decode() refuses a boundary inside a multibyte character.
        start = len(encoded[:a].decode("utf-8"))
        end = len(encoded[:b].decode("utf-8"))
        before = encoded[a:b].decode("utf-8")
        if before != patch["before"]:
            raise ValueError("UTF-8 patch parent mismatch")
        edits.append(dict(start=start, end=end, before=before, after=patch["after"]))
    return edits


def adapt_legacy(row, tool, record, release, versions):
    """Release must already be fingerprinted and bound to this input parent.

    A sparse release's missing rows MUST NOT call this function as unchanged.
    Crop identity is inherited only through the explicitly bound parent manifest.
    """
    if release["parent_id"] != row["parent_id"]:
        raise ValueError("correction artifact parent mismatch")
    if record.get("id", record.get("line_id")) != row["id"]:
        raise ValueError("correction row ID mismatch")
    raw = row["raw_text"]
    parent = record.get("label_parent", record.get("parent_text"))
    parent_sha = record.get("parent_text_sha256", record.get("original_label_sha256"))
    if parent is not None:
        if parent != raw:
            raise ValueError("legacy literal parent mismatch")
    elif parent_sha != digest(raw):
        raise ValueError("legacy artifact lacks exact raw-parent binding")
    target = record.get("text", record.get("label", record.get("composed_text", raw)))
    status = record.get("status", "ok")
    unresolved = bool(record.get("holds") or record.get("hold_slots") or status in {"hold", "out_of_scope", "failed"})
    if unresolved:
        state, edits = "required_evidence_unresolved", []
    elif release["status"] != "released":
        state, edits = "proposal_only", []
    else:
        edits = byte_edits(raw, record["byte_patches"]) if tool == "polytonic" and "byte_patches" in record else span_edits(raw, target)
        rebuilt, _ = merge_edits(raw, [dict(tool=tool, edits=edits)])
        if rebuilt != target:
            raise ValueError("patches do not reconstruct declared result")
        if tool == "cyrillic" and any(e["before"] != "ь" or e["after"] != "ъ" for e in edits):
            raise ValueError("RU1 artifact exceeds its qualified substitution")
        if tool == "numerics" and any(e["before"] not in {"-", "."} or e["after"] != "·" for e in edits):
            raise ValueError("N1 artifact exceeds its qualified separator edits")
        state = "applied" if edits else "verified_no_change"
    producer={k:record[k] for k in ("policy_digest","policy_sha","policy_sha256","parent","source_job","variant","wave","release_policy","detector_version","r1_sha") if k in record}
    for key,value in release.get("producer",{}).items():
        if producer.get(key)!=value:raise ValueError("manifest/record producer mismatch: "+key)
    return dict(tool=tool, tool_version=versions[tool]["version"], tool_digest=versions[tool]["digest"],
        binding=identity(row), raw_text_sha256=digest(raw), status=state, edits=edits,
        evidence=dict(artifact_sha256=release["sha256"], release_status=release["status"],
            parent_manifest_sha256=release["parent_manifest_sha256"], original_status=status,
            legacy_holds=record.get("holds", record.get("hold_slots", [])),producer=producer,
            original_record_sha256=digest(canonical(record)),adapter_version="0.2",
            adapter_toolchain_digest=versions[tool]["digest"]))
