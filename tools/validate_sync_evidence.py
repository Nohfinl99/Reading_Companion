"""Check the captured 0.3.7 citation run structurally, not its semantic truth.

Default replay uses immutable context snapshots. --require-current-context adds
the release-time comparison with canonical source; it does not rewrite history.
Runner gold exclusion was instruction-only on a shared filesystem, not blinding.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = Path("evaluation/citeguard/sync-0.3.7")
SKILL = Path("skills/sid-reading-companion")
CONTEXT = {"SKILL.md", "references/master-instruction.md", "references/knowledge-compiler.md",
           "references/reading-protocols.md", "references/stack-contracts.md",
           "references/citation-evidence.md", "references/knowledge/citeguard.md"}
OUTPUTS = {"artifact.md", "sidecar.json", "runner-notes.json"}
_spec = importlib.util.spec_from_file_location("sid_gate_records", Path(__file__).with_name("validate_gate_records.py"))
gates = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gates)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_hash(root, relative, expected, label):
    path = gates.contained(root, relative)
    require(gates.raw_hash(path) == expected, label + " fingerprint mismatch")
    return path


def check_locator(root, span, expected_path, expected_hash):
    require(isinstance(span, dict) and span.get("path") == expected_path,
            "Review evidence path mismatch")
    path = check_hash(root, span["path"], span.get("sha256"), "Review evidence")
    require(span["sha256"] == expected_hash, "Review evidence identity mismatch")
    start, end = span.get("line_start"), span.get("line_end")
    require(type(start) is int and type(end) is int and
            1 <= start <= end <= len(path.read_text(encoding="utf-8").splitlines()),
            "Invalid review locator")


def validate(root=ROOT, *, require_current_context=False):
    root = Path(root)
    folder = root / RUN
    inputs, rubric, manifest, review = [gates.load_json(folder / name) for name in
                                        ("inputs.json", "rubric.json", "run-manifest.json", "review.json")]
    require(inputs["run_id"] == manifest["run_id"] == review["run_id"] == "sync-0.3.7-ce-record",
            "Run identity mismatch")
    require(inputs["model_requested"] == manifest["configured_model"] == "gpt-6-luna",
            "Runner configured model mismatch")
    require(manifest["evidence_layer"] == "delegated_model_prompt_run", "Runner evidence layer mismatch")
    require(review["evidence_layer"] == rubric["review_layer"] == "primary_review_of_delegated_run",
            "Review evidence layer mismatch")
    require("not installed-plugin activation" in manifest["runtime_context"] and
            "instruction-only gold exclusion" in manifest["runtime_context"], "Runner boundary missing")
    require(manifest["host_activation"] == manifest["learner_outcome"] == "NOT_RUN" and
            manifest["external_independent_review"] is False, "Unsupported evidence promotion")
    check_hash(folder, "inputs.json", manifest["input_sha256"], "Input")
    check_hash(folder, "rubric.json", manifest["rubric_sha256"], "Rubric")
    check_hash(folder, "rubric.json", review["rubric_sha256"], "Review rubric")
    check_hash(folder, "run-manifest.json", review["manifest_sha256"], "Review manifest")
    check_hash(folder, "fixture.txt", manifest["fixture_sha256"], "Fixture")
    require(inputs["fixture_sha256"] == manifest["fixture_sha256"], "Input fixture mismatch")
    fingerprints = inputs["source_fingerprints"]
    require(set(fingerprints) == CONTEXT and manifest["source_fingerprints"] == fingerprints,
            "Context coverage or identity mismatch")
    for relative, expected in fingerprints.items():
        check_hash(folder, "context/" + relative + ".txt", expected, "Context snapshot")
        if require_current_context:
            check_hash(root, (SKILL / relative).as_posix(), expected, "Current context")
    require(set(manifest["outputs"]) == OUTPUTS, "Output coverage mismatch")
    for relative, expected in manifest["outputs"].items():
        check_hash(folder, relative, expected, "Output")
    prior = manifest["prior_attempt"]
    require(set(prior["files"]) == OUTPUTS and bool(prior["finding"].strip()) and
            manifest["repairs"] == 1, "Historical scope repair finding missing")
    for relative, expected in prior["files"].items():
        check_hash(folder, "attempt1/" + relative, expected, "Prior attempt")
    criteria = rubric["criteria"]
    require(isinstance(criteria, list) and len(criteria) == 3 and len(set(criteria)) == 3,
            "Frozen criteria coverage mismatch")
    require([item["criterion"] for item in review["criteria"]] == criteria, "Review criteria mismatch")
    require(review["status"] == "PASS" and bool(review["scope"].strip()), "Capture has not passed scoped review")
    for item in review["criteria"]:
        require(item["status"] == "PASS" and bool(item["reason"].strip()), "False review PASS")
        check_locator(folder, item["source"], "fixture.txt", manifest["fixture_sha256"])
        check_locator(folder, item["output"], "artifact.md", manifest["outputs"]["artifact.md"])
    notes = gates.load_json(folder / "runner-notes.json")
    require(notes["execution"] == "delegated_model_prompt_run" and
            notes["model_requested"] == manifest["configured_model"] and
            notes["host"] == notes["learner_outcome"] == "NOT_RUN", "Runner notes evidence mismatch")
    sidecar = gates.load_json(folder / "sidecar.json")
    structural = gates.validate_envelope(folder, sidecar, expected_artifacts={"artifact.md": 1})
    require(len(sidecar["gate_records"]) == 1 and sidecar["gate_records"][0]["status"] == "PASS"
            and sidecar["gate_records"][0]["applicable"] is True, "Final citation gate has not passed")
    return {"ok": True, "cases": 1, "criteria": len(criteria), "context_files": len(fingerprints),
            "prior_scope_finding_retained": True, "structural_records": structural["records"],
            "current_context_checked": require_current_context, "evidence_layer": "mechanical_helper",
            "semantic_verified_by_tool": False, "installed_host_verified": False,
            "external_independent_review": False, "gold_exclusion": "instruction_only_shared_filesystem"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--require-current-context", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = validate(args.root, require_current_context=args.require_current_context)
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(json.dumps({"ok": False, "error": str(error), "semantic_verified_by_tool": False}))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
