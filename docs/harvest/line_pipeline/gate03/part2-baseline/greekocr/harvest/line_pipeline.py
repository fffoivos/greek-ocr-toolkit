"""Versioned, offline line filtering. Historical admission.evaluate is unchanged.

Offsets are Python Unicode code points in the immutable raw Google parent.
Readers and native segmentation are injected adapters, never implicit fallbacks.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from difflib import SequenceMatcher
import hashlib
import json
import math
import re
import unicodedata as ud

from . import admission as adm
from .text_primitives import codec_letter_script

PIPELINE_VERSION = "0.3"
TOOLS = ("polytonic", "cyrillic", "numerics", "dashes", "content_repair")
SUCCESS = frozenset({"applied", "verified_no_change", "tag_only"})


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def identity(row):
    return {k: row[k] for k in ("parent_id", "id", "split", "crop_sha256")}


def validate_row(row):
    for k in ("parent_id", "id", "source", "book_id", "edition_id", "page_id", "split", "raw_text", "crop_sha256"):
        if not isinstance(row.get(k), str) or (not row[k] and k != "raw_text"):
            raise ValueError("missing/invalid " + k)
    if row["split"] not in {"train", "dev", "test", "unassigned"}:
        raise ValueError("unknown split")
    if not re.fullmatch(r"[0-9a-f]{64}", row["crop_sha256"]):
        raise ValueError("invalid crop SHA256")


def expectations(row, metadata):
    """Page override > book declaration > existing provenance-bound source table."""
    book = metadata.get("books", {}).get(row["book_id"], {})
    page_key = canonical([row["source"], row["book_id"], row["page_id"]])
    declared = metadata.get("pages", {}).get(page_key, book)
    if declared:
        required = ("languages", "scripts", "orthography", "provenance")
        if any(not declared.get(k) for k in required):
            raise ValueError("incomplete declared book/page expectations")
        result = deepcopy(declared)
    else:
        policy = adm.expected_policy(row)
        language = policy["language"]
        # Do not invent Russian/Serbian or historical orthography from 'Cyrillic'.
        result = dict(languages=[language], scripts=policy["expected_letters"],
            orthography="polytonic" if "polytonic" in language else "monotonic" if "monotonic" in language else "unknown",
            provenance=policy["provenance"], allowed_characters=policy.get("expected_characters", []),latin_policy=policy["latin"])
    if not set(result["scripts"]) <= {"greek", "latin", "cyrillic", "other"}:
        raise ValueError("unknown expected script")
    return result


def inventory(text, codec):
    """Reuse the toolkit's inventory and codec-aware script/word primitives."""
    result = adm.inventory(text)
    scripts = Counter(codec_letter_script(c, codec) for c in text)
    scripts.pop(None, None)
    mixed = []
    for word in adm.words(text):
        seen = {codec_letter_script(c, codec) for c in word} - {None}
        if len(seen) > 1:
            mixed.append(word)
    result.update(scripts=dict(sorted(scripts.items())), mixed_words=mixed,
        characters=len(ud.normalize("NFC", text)), raw_codepoints=len(text),
        raw_text_sha256=digest(text), character_counts=dict(sorted(Counter(text).items())))
    return result


def content_issues(text, inv, expected, codec):
    issues = []
    allowed=set(expected["scripts"])
    if expected.get("latin_policy")=="mixed_class_or_minority":
        allowed.add("latin")
        if inv["scripts"].get("latin",0)>sum(n for s,n in inv["scripts"].items() if s!="latin"):
            issues.append(dict(reason="unexpected_language",detail="majority Latin under minority-Latin source policy"))
    unexpected = set(inv["scripts"]) - allowed
    if unexpected:
        issues.append(dict(reason="unexpected_script", scripts=sorted(unexpected)))
    if inv["mixed_words"]:
        issues.append(dict(reason="mixed_script_word", words=inv["mixed_words"]))
    outside = sorted({c for c in ud.normalize("NFD", text) if not c.isspace()} - codec["atoms"] - set(expected.get("allowed_characters", [])))
    if outside:
        issues.append(dict(reason="unexpected_character", characters=outside))
    return issues


def content_gate_exclusion(text, inv, expected, codec):
    """Owner gate: mixed words drop; otherwise foreign scripts hold."""
    issues = content_issues(text, inv, expected, codec)
    mixed = next((issue for issue in issues if issue["reason"] == "mixed_script_word"), None)
    foreign = next((issue for issue in issues if issue["reason"] == "unexpected_script"), None)
    reasons = [mixed] if mixed else []
    if foreign:
        reasons.append(dict(foreign, script_counts=inv["scripts"],
            characters=sorted({c for c in text if codec_letter_script(c, codec) in foreign["scripts"]})))
    if reasons:
        return ("DROP" if mixed else "HOLD"), reasons
    return None


def profile_issues(row, inv, metadata):
    """Frozen reviewed profiles only; current observations never train a baseline."""
    key = canonical([row["source"], row["book_id"], row["page_id"]])
    profiles = metadata.get("profiles", {})
    profile = profiles.get(key, profiles.get(row["book_id"]))
    if profile is None:
        return []
    if not profile.get("reviewed") or not profile.get("provenance") or not profile.get("sample_size"):
        raise ValueError("profile is not reviewed/provenance-bound")
    result = []
    for field, bounds in profile.get("line_bounds", {}).items():
        if field not in inv or not isinstance(inv[field], (int, float)):
            raise ValueError("unknown profile metric")
        lo, hi = bounds
        if not lo <= inv[field] <= hi:
            result.append(dict(reason="profile_anomaly", metric=field, observed=inv[field], bounds=bounds))
    for field, bounds in profile.get("page_bounds", {}).items():
        value = row.get("page_summary", {}).get(field)
        if value is None:
            result.append(dict(reason="page_profile_unavailable", metric=field))
        elif not bounds[0] <= value <= bounds[1]:
            result.append(dict(reason="page_profile_anomaly", metric=field, observed=value, bounds=bounds))
    return result


def routes(text, inv, expected, issues):
    result = set()
    if inv["scripts"].get("greek") and orthography_for(expected, "greek") not in {"monotonic", "modern"}:
        result.add("polytonic")
    if inv["scripts"].get("cyrillic"):
        result.add("cyrillic")
    if inv["digits"]:
        result.add("numerics")
    if any(c in text for c in "-–—−"):
        result.add("dashes")
    if issues:
        result.add("content_repair")
    return result


def orthography_for(expected, script):
    return expected.get("orthographies", {}).get(script, expected["orthography"])


def russian_eligible(expected):
    return bool({s.casefold() for s in expected["languages"]}&{"russian","ru","rus"}) and orthography_for(expected,"cyrillic")=="historical_russian"


def preserve_holds(result):
    if result.get("holds") or result.get("hold_slots") or result.get("evidence",{}).get("holds") or result.get("evidence",{}).get("hold_slots"):
        return dict(result,status="required_evidence_unresolved",edits=[],reason="explicit producer holds",producer_result=result)
    return result


def span_edits(parent, target):
    return [dict(start=i, end=j, before=parent[i:j], after=target[a:b])
            for op, i, j, a, b in SequenceMatcher(None, parent, target, autojunk=False).get_opcodes() if op != "equal"]


def merge_edits(parent, results):
    """No last-writer wins. Identical edits coalesce; any ambiguous overlap holds."""
    unique = {}
    for result in results:
        for edit in result.get("edits", []):
            i, j = edit["start"], edit["end"]
            if type(i) is not int or type(j) is not int or not 0 <= i <= j <= len(parent):
                raise ValueError("invalid raw-parent span")
            if parent[i:j] != edit["before"] or not isinstance(edit["after"], str):
                raise ValueError("old span differs from immutable raw parent")
            key = (i, j, edit["before"], edit["after"])
            unique.setdefault(key, dict(edit, tools=[]))["tools"].append(result["tool"])
    edits = sorted(unique.values(), key=lambda e: (e["start"], e["end"]))
    for a, b in zip(edits, edits[1:]):
        overlap = b["start"] < a["end"] or b["start"] == a["start"] or (b["start"] == a["end"] and b["start"] == b["end"])
        if overlap:
            raise ValueError("conflicting/ambiguous overlapping tool edits")
    text = parent
    for edit in reversed(edits):
        text = text[:edit["start"]] + edit["after"] + text[edit["end"]:]
    return text, edits


def candidate_scope(parent, text, edits, tool):
    """Candidate identity anchored to raw coordinates, unaffected by earlier edits."""
    origins=[];at=0
    for e in edits:
        origins.extend([[i,i+1] for i in range(at,e["start"])])
        origins.extend([["edit",e["start"],e["end"],digest(e["after"]),i] for i in range(len(e["after"]))])
        at=e["end"]
    origins.extend([[i,i+1] for i in range(at,len(parent))])
    if len(origins)!=len(text):raise ValueError("invalid composed-text coordinate map")
    if tool=="numerics":
        spans=[m.span() for m in re.finditer(r"\d[\d\s.,·+\-−–—/%:]*",text)]
    elif tool=="dashes":spans=[(i,i+1) for i,c in enumerate(text) if c in "-–—−"]
    elif tool in {"polytonic","cyrillic"}:
        script="greek" if tool=="polytonic" else "cyrillic"
        spans=[m.span() for m in re.finditer(r"\S+",text) if any(adm.letter_script(c)==script for c in m.group())]
    else:spans=[(0,len(text))]
    return digest(canonical([dict(text=text[a:b],raw_anchors=origins[a:b]) for a,b in spans]))


def validate_result(result, row, tool, versions):
    if result.get("tool") != tool or result.get("tool_version") != versions[tool]["version"]:
        raise ValueError("tool/version mismatch")
    if result.get("binding") != identity(row) or result.get("raw_text_sha256") != digest(row["raw_text"]):
        raise ValueError("result belongs to a different crop, split or raw parent")
    if result.get("tool_digest") != versions[tool]["digest"]:
        raise ValueError("tool implementation/release digest mismatch")
    if result.get("status") not in SUCCESS | {"proposal_only", "required_evidence_unresolved", "failed"}:
        raise ValueError("unknown tool result status")
    if result["status"]=="tag_only" and tool!="dashes":
        raise ValueError("tag_only is qualified only for the dash tagger")
    if result["status"] in SUCCESS and not result.get("evidence"):
        raise ValueError("successful tool result lacks evidence")
    if result["status"] != "applied" and result.get("edits"):
        raise ValueError("non-applied result contains edits")
    # Run span validation even when no other tool is scheduled.
    merge_edits(row["raw_text"], [result])
    if tool=="cyrillic" and any(e["before"]!="ь" or e["after"]!="ъ" for e in result.get("edits",[])):
        raise ValueError("RU1 result exceeds qualified hard-sign edits")
    if tool=="cyrillic" and any(e["end"]<len(row["raw_text"]) and (row["raw_text"][e["end"]].isalpha() or ud.category(row["raw_text"][e["end"]]).startswith("M")) for e in result.get("edits",[])):
        raise ValueError("RU1 result exceeds qualified word-final positions")
    if tool=="numerics" and any(e["before"] not in {"-","."} or e["after"]!="·" for e in result.get("edits",[])):
        raise ValueError("numeric result exceeds qualified separator edits")


def validate_segmentation(result,row,version):
    if not isinstance(result,dict):raise ValueError("native segmentation result must be an object")
    if result.get("tool_version")!=version or result.get("binding")!=identity(row) or result.get("raw_text_sha256")!=digest(row["raw_text"]):
        raise ValueError("segmentation evidence binding/version mismatch")
    if result.get("verdict") not in {"KEEP","DROP","UNCERTAIN"} or not isinstance(result.get("reason"),str):
        raise ValueError("invalid segmentation verdict/reason")
    canonical(result)


def automatic_result(row, tool, expected, version, tool_digest, observed_text=None):
    """Only exact scope/candidate negatives and tag-only dashes can be automatic."""
    text = row["raw_text"] if observed_text is None else observed_text
    evidence = None
    status = "verified_no_change"
    if tool == "dashes":
        status, evidence = "tag_only", dict(dashes=[dict(offset=i, character=c) for i, c in enumerate(text) if c in "-–—−"], policy="no qualified general dash repair")
    elif tool == "numerics" and not any(c in text for c in ".-·"):
        evidence = dict(candidate_scan="no adjacent numeric separator candidate")
    elif tool == "cyrillic":
        lang = {s.lower() for s in expected["languages"]}
        orthography = orthography_for(expected, "cyrillic")
        if orthography == "modern" and lang & {"serbian", "sr", "srp", "russian", "ru"}:
            evidence = dict(scope="RU1 historical hard-sign rule is not applicable to declared modern orthography")
        elif orthography == "historical_russian" and lang & {"russian", "ru", "rus"} and not re.search(r"ь(?=$|[^\w])", text):
            evidence = dict(candidate_scan="no historical Russian word-final soft sign")
    if evidence is None:
        return None
    return dict(tool=tool, tool_version=version, tool_digest=tool_digest, binding=identity(row), raw_text_sha256=digest(row["raw_text"]),coverage_text_sha256=digest(text),
        status=status, edits=[], evidence=evidence)


def final_eligibility(row, text, inv, expected, codec, policy):
    issues = content_issues(text, inv, expected, codec)
    # Admission role is independent of script inventory. Explicit book/page role
    # takes precedence; a script_class of 'nonletter' cannot erase numeric role.
    role = expected.get("content_role") or row.get("content_role") or row.get("primary_class") or "prose"
    numeric = role == "numerics_tables"
    letters = inv["letter_count"]
    if numeric:
        separators = policy.get("numeric_separators", ".,·-/ ")
        n = len(ud.normalize("NFC", text))
        good = sum(ud.category(c) == "Nd" or c in separators for c in ud.normalize("NFC", text))
        if inv["digits"] < policy.get("numeric_min_digits", 4) or good < policy.get("numeric_min_shape", .6) * n:
            issues.append(dict(reason="numeric_shape"))
    else:
        minimum = policy.get("heading_min_letters", 4) if role == "headings_caps" else policy.get("prose_min_letters", 10)
        if letters < minimum:
            issues.append(dict(reason="short_line", role=role, letters=letters, minimum=minimum))
        if inv["nonspace_count"] and 3 * (inv["nonspace_count"] - letters) > inv["nonspace_count"]:
            issues.append(dict(reason="nonletter_fraction"))
    confidence = row.get("confidence", row.get("docai_confidence"))
    if confidence is not None:
        if not isinstance(confidence, (int, float)) or not math.isfinite(confidence) or not 0 <= confidence <= 1:
            raise ValueError("invalid confidence")
        if confidence < policy.get("min_confidence", .89):
            issues.append(dict(reason="low_confidence"))
    # No legacy tall_box rule: current frozen segmentation owns padding/height.
    atoms = list(ud.normalize("NFD", text))
    outside_codec = sorted(set(atoms) - codec["atoms"])
    if outside_codec:
        issues.append(dict(reason="codec_unencodable", characters=outside_codec))
    required = len(atoms) + sum(a == b for a, b in zip(atoms, atoms[1:]))
    if policy.get("require_ctc_steps") and row.get("ctc_output_steps") is None:
        issues.append(dict(reason="ctc_steps_unavailable", unresolved=True))
    elif row.get("ctc_output_steps") is not None:
        steps = row["ctc_output_steps"]
        if type(steps) is not int or steps < 1:
            raise ValueError("invalid CTC output steps")
        if required > steps:
            issues.append(dict(reason="ctc_infeasible", required=required, available=steps))
    if row["split"] == "train" and row["edition_id"] in policy.get("heldout_editions", []):
        issues.append(dict(reason="heldout_edition"))
    return issues


@dataclass
class Pipeline:
    codec: dict
    versions: dict
    metadata: dict
    policy: dict
    segmenter: object
    corrector: object

    def __post_init__(self):
        self.toolchain_digest=digest(canonical(self.versions))
        self.toolchain_versions={name:tool["version"] for name,tool in self.versions.items()}

    def evaluate(self, row):
        validate_row(row)
        raw = row["raw_text"]
        out = dict(schema="line-filter-decision-v1", pipeline_version=PIPELINE_VERSION,
            toolchain_digest=self.toolchain_digest,toolchain_versions=self.toolchain_versions,
            binding=identity(row), raw_text_sha256=digest(raw), final_text=raw,
            stages=[], routes={}, reasons=[], disposition="HOLD", admitted=False)

        def finish(disposition, reasons):
            out.update(disposition=disposition, admitted=disposition == "ADMIT", reasons=reasons)
            for tool in TOOLS:
                out["routes"].setdefault(tool, dict(status="not_run_due_to_prior_exclusion" if disposition != "ADMIT" else "not_applicable"))
            return out

        try:
            expected = expectations(row, self.metadata)
        except ValueError as exc:
            return finish("HOLD", [dict(reason="expectations_unresolved", detail=str(exc))])
        inv = inventory(raw, self.codec)
        out.update(expectations=expected, raw_inventory=inv)
        preliminary = content_issues(raw, inv, expected, self.codec)
        anomalies = profile_issues(row, inv, self.metadata)
        out["stages"].append(dict(stage="content_gate", suspicious=preliminary, profile_flags=anomalies))
        exclusion = content_gate_exclusion(raw, inv, expected, self.codec)
        if exclusion:
            disposition, reasons = exclusion
            out["stages"][-1]["excluded"] = reasons[0]["reason"]
            return finish(disposition, reasons)
        if row.get("crop_identity_status", "bound") != "bound":
            return finish("HOLD", [dict(reason="crop_identity_unresolved")])
        # Remaining suspicion routes to repair without early length rules.
        seg = self.segmenter(row)
        validate_segmentation(seg,row,self.versions["segmentation"]["version"])
        out["stages"].append(dict(stage="segmentation", result=seg))
        if seg["verdict"] != "KEEP":
            return finish("DROP" if seg["verdict"] == "DROP" else "HOLD", [dict(reason="segmentation", detail=seg["reason"])])
        scheduled, results = set(), {}
        text, edits = raw, []
        for _ in range(len(TOOLS) + 1):
            current = inventory(text, self.codec)
            issues = content_issues(text, current, expected, self.codec)
            needed = routes(text, current, expected, issues)
            # Anomalies need independent resolution, never profile self-promotion.
            if anomalies or profile_issues(row,current,self.metadata):
                needed.add("content_repair")
            new = needed - scheduled
            if not new:
                break
            for tool in sorted(new):
                result = self.corrector(row, tool, expected)
                if result is None:
                    result = automatic_result(row, tool, expected, self.versions[tool]["version"], self.versions[tool]["digest"],observed_text=text)
                if result is None:
                    result = dict(tool=tool, tool_version=self.versions[tool]["version"], tool_digest=self.versions[tool]["digest"], binding=identity(row),
                        raw_text_sha256=digest(raw), status="required_evidence_unresolved", edits=[], evidence={}, reason="missing qualified tool result")
                result=preserve_holds(result)
                validate_result(result, row, tool, self.versions)
                if tool=="cyrillic" and (result.get("edits") or orthography_for(expected,"cyrillic")=="historical_russian") and not russian_eligible(expected):
                    result=dict(result,status="required_evidence_unresolved",edits=[],reason="RU1 requires Russian language and historical Russian orthography")
                results[tool] = result
                out["routes"][tool] = result
            scheduled |= new
            unresolved = [dict(reason="correction_unresolved", tool=t, status=r["status"]) for t, r in results.items() if r["status"] not in SUCCESS and t != "content_repair"]
            if unresolved:
                return finish("HOLD", unresolved)
            try:
                text, edits = merge_edits(raw, [r for r in results.values() if r["status"] in SUCCESS])
            except ValueError as exc:
                return finish("HOLD", [dict(reason="conflicting_edits", detail=str(exc))])
        else:
            return finish("HOLD", [dict(reason="routing_did_not_stabilize")])
        out.update(final_text=text,edits=edits)
        for tool,result in results.items():
            if tool=="content_repair" or result["status"] not in SUCCESS:continue
            own,own_edits=merge_edits(raw,[result])
            required=candidate_scope(raw,text,edits,tool)
            certified=candidate_scope(raw,own,own_edits,tool)
            if required!=certified and result.get("coverage_text_sha256")!=digest(text):
                refreshed=None if result.get("edits") else automatic_result(row,tool,expected,self.versions[tool]["version"],self.versions[tool]["digest"],observed_text=text)
                if refreshed is not None:
                    results[tool]=refreshed;out["routes"][tool]=refreshed
                else:
                    out["routes"][tool]=dict(result,status="required_evidence_unresolved",edits=[],previous_result=result,
                        reason="composed candidate scope changed",obligation=dict(candidate_scope_sha256=required,composed_text_sha256=digest(text),composed_text=text))
                    return finish("HOLD",[dict(reason="candidate_scope_requires_recheck",tool=tool)])
        # Canonical equivalence and whitespace only; no punctuation/mark folding.
        normalized = " ".join(ud.normalize("NFC", text).split())
        out["normalization"] = dict(before=text, after=normalized, policy="NFC-and-whitespace-only") if normalized != text else None
        text = normalized
        final_inv = inventory(text, self.codec)
        out.update(final_text=text, final_text_sha256=digest(text), final_inventory=final_inv, edits=edits)
        out["stages"].append(dict(stage="composition", tools=sorted(scheduled), edits=edits))
        final_anomalies=profile_issues(row,final_inv,self.metadata)
        profile_scope=digest(canonical(dict(text_sha256=digest(text),issues=final_anomalies,profiles=self.metadata.get("profiles",{}))))
        if final_anomalies and results.get("content_repair",{}).get("evidence",{}).get("profile_resolution_sha256")!=profile_scope:
            out["routes"]["content_repair"]=dict(status="required_evidence_unresolved",reason="final profile anomaly",obligation=dict(profile_scope_sha256=profile_scope,composed_text=text))
            return finish("HOLD",final_anomalies)
        if "content_repair" in results and results["content_repair"]["status"] not in SUCCESS:
            if results["content_repair"].get("reason") != "missing qualified tool result":
                return finish("HOLD", [dict(reason="content_repair_unresolved")])
            if content_issues(text, final_inv, expected, self.codec):
                return finish("HOLD", [dict(reason="content_repair_unresolved")])
            out["routes"]["content_repair"] = dict(results["content_repair"],status="verified_no_change",
                evidence=dict(resolved_by=sorted(t for t in results if t!="content_repair"), verification="final script/character re-inventory cleared original suspicion"))
        if row["split"] == "unassigned" or row.get("edition_identity_status", "bound") != "bound":
            return finish("HOLD", [dict(reason="split_or_edition_identity_unresolved")])
        failures = final_eligibility(row, text, final_inv, expected, self.codec, self.policy)
        out["stages"].append(dict(stage="final_eligibility", checks=failures))
        return finish("HOLD" if any(r.get("unresolved") for r in failures) else "DROP" if failures else "ADMIT", failures)
