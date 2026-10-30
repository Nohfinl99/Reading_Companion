"""Validate SC05 citation sidecars structurally; never decide semantic support.

The artifact registry is the caller's declared revision baseline, not an inferred
history. Supply expected_artifacts (or CLI --expected-artifact) when comparing
against a separately held current revision. Historical records may use the
explicit legacy UTF-8/LF fingerprint profile via validate_record only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PureWindowsPath

CHECKS = {f"CR{i:02}" for i in range(1, 7)}
STATUSES = {"PASS", "FAIL", "PARTIAL", "NOT_RUN"}
REQUIRED = {"gate_id", "artifact_ref", "artifact_revision", "applicable", "reason",
            "status", "source_spans", "output_spans", "checks", "repair_owner", "unresolved"}


class GateValidationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise GateValidationError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key")
        result[key] = value
    return result


def load_json(path):
    path = Path(path)
    require(path.stat().st_size <= 4 * 1024 * 1024, "Oversized gate sidecar")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def contained(root, relative):
    require(isinstance(relative, str) and bool(relative.strip()), "Missing evidence path")
    relative = relative.replace("\\", "/")
    path = Path(relative)
    require(not path.is_absolute() and not PureWindowsPath(relative).drive
            and ".." not in path.parts, "Evidence path escapes repository")
    resolved = (Path(root) / path).resolve()
    require(resolved.is_relative_to(Path(root).resolve()), "Evidence path escapes repository")
    require(resolved.is_file(), "Evidence file missing")
    return resolved


def raw_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def lf_hash(path):
    return hashlib.sha256(Path(path).read_text(encoding="utf-8").encode("utf-8")).hexdigest()


def check_span(root, span, legacy=False):
    require(isinstance(span, dict), "Invalid evidence span")
    path = contained(root, span.get("path"))
    key = "sha256_utf8_lf" if legacy else "sha256"
    digest = lf_hash(path) if legacy else raw_hash(path)
    require(span.get(key) == digest, "Stale evidence fingerprint")
    lines = path.read_text(encoding="utf-8").splitlines()
    start, end = span.get("line_start"), span.get("line_end")
    require(type(start) is int and type(end) is int and 1 <= start <= end <= len(lines),
            "Invalid evidence locator")
    excerpt = span.get("excerpt")
    require(isinstance(excerpt, str) and bool(excerpt.strip()), "Missing evidence excerpt")
    require(excerpt in "\n".join(lines[start - 1:end]), "Excerpt not at declared locator")
    return path


def validate_record(root, record, *, artifacts=None, legacy=False):
    """Validate one G-CITATION-REVIEW, optionally against a current registry.

    artifacts maps artifact_ref to {artifact_revision, sha256}. A strict new
    record requires that registry; the legacy adapter supplies its known revision
    separately and retains the original authored fingerprint profile.
    """
    require(isinstance(record, dict), "Invalid GateRecord")
    missing = REQUIRED - set(record)
    require(not missing, "Missing GateRecord fields: " + ", ".join(sorted(missing)))
    require(record["gate_id"] == "G-CITATION-REVIEW", "Unexpected gate")
    require(type(record["artifact_revision"]) is int and record["artifact_revision"] >= 1,
            "Invalid artifact revision")
    artifact = contained(root, record["artifact_ref"])
    if not legacy:
        require(isinstance(artifacts, dict) and record["artifact_ref"] in artifacts,
                "Missing artifact revision baseline")
    if artifacts is not None:
        baseline = artifacts.get(record["artifact_ref"])
        require(isinstance(baseline, dict), "Missing artifact revision baseline")
        require(record["artifact_revision"] == baseline.get("artifact_revision"),
                "Stale artifact revision")
        require(raw_hash(artifact) == baseline.get("sha256"), "Stale artifact fingerprint")
    require(type(record["applicable"]) is bool, "Invalid applicability")
    require(isinstance(record["reason"], str) and bool(record["reason"].strip()),
            "Missing applicability reason")
    require(record["status"] in STATUSES, "Invalid SC05 gate status")
    require(record["repair_owner"] is None or
            (isinstance(record["repair_owner"], str) and bool(record["repair_owner"].strip())),
            "Invalid repair owner")
    require(isinstance(record["unresolved"], list) and
            all(isinstance(x, str) and bool(x.strip()) for x in record["unresolved"]),
            "Invalid unresolved list")
    source, output = record["source_spans"], record["output_spans"]
    require(isinstance(source, list) and isinstance(output, list), "Invalid evidence lists")
    require(bool(output), "Missing output evidence")
    for span in source + output:
        check_span(root, span, legacy)
    require(all(contained(root, span["path"]) == artifact for span in output),
            "Output evidence does not match reviewed artifact")
    checks = record["checks"]
    require(isinstance(checks, dict), "Invalid review checks")
    if not record["applicable"]:
        require(record["status"] == "NOT_RUN", "Non-applicable gate cannot PASS")
        require(not checks, "Non-applicable gate must not execute citation checks")
        return {"status": "NOT_RUN", "applicable": False}
    require(set(checks) == CHECKS, "Required review check missing or unknown")
    for check in checks.values():
        require(isinstance(check, dict) and check.get("status") in STATUSES | {"N/A"},
                "Invalid check status")
        require(isinstance(check.get("reason"), str) and bool(check["reason"].strip()),
                "Missing check reason")
        for field, spans in (("output_span_refs", output), ("source_span_refs", source)):
            refs = check.get(field, [])
            require(isinstance(refs, list) and all(type(i) is int and 0 <= i < len(spans) for i in refs),
                    "Invalid check evidence reference")
        if check["status"] == "PASS":
            require(bool(check.get("output_span_refs")), "PASS check lacks output evidence")
    if record["status"] == "PASS":
        require(bool(source), "PASS lacks source evidence")
        require(not record["unresolved"], "PASS has unresolved checks")
        require(all(c["status"] in {"PASS", "N/A"} for c in checks.values()),
                "PASS contains a failing or unrun check")
    return {"status": record["status"], "applicable": True}


def validate_envelope(root, envelope, *, expected_artifacts=None):
    require(isinstance(envelope, dict) and envelope.get("contract_version") == "PS1",
            "Missing PS1 envelope")
    for field in ("scope", "evidence_layer"):
        require(isinstance(envelope.get(field), str) and bool(envelope[field].strip()),
                "Missing envelope " + field)
    items = envelope.get("artifacts")
    require(isinstance(items, list) and bool(items), "Missing artifact registry")
    artifacts = {}
    artifact_paths = set()
    for item in items:
        require(isinstance(item, dict), "Invalid artifact registry entry")
        reference = item.get("artifact_ref")
        path = contained(root, reference)
        require(reference not in artifacts and path not in artifact_paths, "Duplicate artifact registry entry")
        require(type(item.get("artifact_revision")) is int and item["artifact_revision"] >= 1,
                "Invalid artifact revision")
        require(item.get("sha256") == raw_hash(path), "Stale artifact fingerprint")
        if expected_artifacts is not None:
            require(reference in expected_artifacts and item["artifact_revision"] == expected_artifacts[reference],
                    "Stale artifact revision against caller baseline")
        artifacts[reference] = item
        artifact_paths.add(path)
    records = envelope.get("gate_records")
    require(isinstance(records, list) and bool(records), "Missing gate_records")
    seen = set()
    for record in records:
        validate_record(root, record, artifacts=artifacts)
        identity = (record["gate_id"], record["artifact_ref"], record["artifact_revision"])
        require(identity not in seen, "Duplicate GateRecord")
        seen.add(identity)
    return {"ok": True, "records": len(records), "evidence_layer": "mechanical_helper",
            "declared_evidence_layer": envelope["evidence_layer"], "scope": envelope["scope"],
            "semantic_verified": False, "host_verified": False,
            "revision_baseline": "caller" if expected_artifacts is not None else "declared_registry"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sidecar", type=Path)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--expected-artifact", action="append", default=[], metavar="PATH=REVISION")
    args = parser.parse_args(argv)
    try:
        expected = {}
        for value in args.expected_artifact:
            key, revision = value.rsplit("=", 1)
            require(key not in expected and int(revision) >= 1, "Invalid expected revision")
            expected[key] = int(revision)
        result = validate_envelope(args.root, load_json(args.sidecar), expected_artifacts=expected or None)
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(json.dumps({"ok": False, "error": str(error), "semantic_verified": False}))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
