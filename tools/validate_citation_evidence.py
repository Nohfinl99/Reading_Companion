"""Validate public CiteGuard records mechanically; never judge semantic support."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = Path("evaluation/citeguard/self-review.json")
CHECKS = {f"CR{i:02}" for i in range(1, 7)}
STATUSES = {"PASS", "FAIL", "PARTIAL", "NOT_RUN"}


class EvidenceError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise EvidenceError(message)


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        require(key not in obj, "Duplicate JSON key")
        obj[key] = value
    return obj


def load_json(path):
    require(path.stat().st_size <= 4 * 1024 * 1024, "Oversized evidence file")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def fingerprint(path):
    """Portable source identity for these UTF-8/LF synthetic records only."""
    return hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()


def contained(root, relative):
    require(isinstance(relative, str) and relative.strip(), "Missing evidence path")
    path = Path(relative)
    require(not path.is_absolute() and ".." not in path.parts, "Evidence path escapes repository")
    resolved = (root / path).resolve()
    require(resolved.is_relative_to(root.resolve()), "Evidence path escapes repository")
    require(resolved.is_file(), "Evidence file missing")
    return resolved


def check_span(root, span):
    path = contained(root, span["path"])
    require(fingerprint(path) == span.get("sha256_utf8_lf"), "Stale evidence fingerprint")
    lines = path.read_text(encoding="utf-8").splitlines()
    start, end = span.get("line_start"), span.get("line_end")
    require(type(start) is int and type(end) is int and 1 <= start <= end <= len(lines),
            "Invalid evidence locator")
    excerpt = span.get("excerpt")
    require(isinstance(excerpt, str) and excerpt.strip(), "Missing evidence excerpt")
    require(excerpt in "\n".join(lines[start - 1:end]), "Excerpt not at declared locator")


def validate(root=ROOT):
    root = Path(root)
    review = load_json(root / REVIEW)
    require(review.get("evidence_layer") == "assistant_authored_self_review",
            "Fixture evidence cannot be promoted to independent or host evidence")
    require(review.get("runtime_prompt_execution") == "NOT_RUN", "Fixture is not a host run")
    cases_path = root / "evaluation/citeguard/cases.json"
    require(fingerprint(cases_path) == review.get("case_spec_sha256_utf8_lf"),
            "Stale case specification fingerprint")
    cases = load_json(cases_path)["cases"]
    case_map = {case["id"]: case for case in cases}
    require(len(case_map) == len(cases), "Duplicate scenario ID")
    records = review["records"]
    require(len({record["case_id"] for record in records}) == len(records), "Duplicate review case")
    require({record["case_id"] for record in records} == set(case_map), "Case coverage mismatch")
    for record in records:
        case = case_map[record["case_id"]]
        gate = record["gate_record"]
        require(gate["gate_id"] == "G-CITATION-REVIEW", "Unexpected gate")
        require(gate["status"] in STATUSES, "Invalid SC05 gate status")
        require(gate["applicable"] is case["applicable"], "Applicability mismatch")
        require(bool(gate["reason"]), "Missing applicability reason")
        require(gate.get("artifact_revision") == 1, "Unexpected fixture artifact revision")
        artifact_path = contained(root, gate["artifact_ref"])
        source_spans, output_spans = gate["source_spans"], gate["output_spans"]
        require(bool(output_spans), "Missing output evidence")
        for span in source_spans + output_spans:
            check_span(root, span)
        require(all(contained(root, span["path"]) == artifact_path for span in output_spans),
                "Output evidence does not match reviewed artifact")
        if not gate["applicable"]:
            require(gate["status"] == "NOT_RUN", "Non-applicable gate cannot PASS")
            continue
        checks = gate["checks"]
        require(set(checks) == CHECKS, "Required review check missing or unknown")
        for check in checks.values():
            require(check["status"] in STATUSES | {"N/A"}, "Invalid check status")
            require(bool(check.get("reason")), "Missing check reason")
        if gate["status"] == "PASS":
            require(bool(source_spans), "PASS lacks source evidence")
            require(not gate["unresolved"], "PASS has unresolved checks")
            require(all(c["status"] in {"PASS", "N/A"} for c in checks.values()),
                    "PASS contains a failing or unrun check")
            for check in checks.values():
                refs = check.get("output_span_refs", [])
                require(bool(refs) and all(type(i) is int and 0 <= i < len(output_spans) for i in refs),
                        "PASS check lacks output evidence")
    knowledge = root / "skills/sid-reading-companion/references/knowledge"
    source = load_json(knowledge / "citeguard-source.json")
    text = (knowledge / "citeguard.md").read_text(encoding="utf-8")
    unit_ids = re.findall(r"^\| (CG-\d+) \|", text, re.MULTILINE)
    require(len(unit_ids) == len(set(unit_ids)), "Duplicate knowledge unit")
    require(set(unit_ids) == set(source["unit_revisions"]), "Manifest/unit ID mismatch")
    relations = load_json(knowledge / "citeguard-relations.json")
    for relation in relations["relations"]:
        require(relation["from"] in unit_ids and relation["target"] in unit_ids, "Unknown relation endpoint")
        require(relation["type"] in {"supports", "contrasts", "limits", "references", "conflicts"},
                "Invalid compiler relation")
        require(relation["basis"] in {"source_explicit", "source_interpretation"}, "Missing relation basis")
        require(bool(relation["proposition"]) and bool(relation["locator"]), "Missing relation evidence")
    return {"ok": True, "cases": len(records), "knowledge_units": len(unit_ids),
            "evidence_layer": "mechanical_helper", "semantic_verified": False,
            "host_verified": False, "fingerprint_mode": "UTF-8/LF"}


def main():
    try:
        result = validate()
    except (EvidenceError, KeyError, TypeError, ValueError, OSError) as error:
        print(json.dumps({"ok": False, "error": str(error), "semantic_verified": False}))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
