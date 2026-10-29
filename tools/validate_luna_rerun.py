"""Check immutable runner/reviewer evidence, not semantic correctness."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[1]
RUNS = ["luna-rerun-2026-10-29", "luna-rerun-2026-10-29-r2", "luna-rerun-2026-10-29-r3"]
_gate_spec = importlib.util.spec_from_file_location("sid_gate_records", Path(__file__).with_name("validate_gate_records.py"))
gate_checker = importlib.util.module_from_spec(_gate_spec)
_gate_spec.loader.exec_module(gate_checker)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def file_at(root, relative):
    path = (root / relative).resolve()
    require(path.is_relative_to(root.resolve()) and path.is_file(), "Evidence path missing or outside root")
    return path


def validate_sidecar(path, root=ROOT, *, expected_artifacts=None):
    """Strict schema validation for NEW captured sidecars, not old prose records."""
    return gate_checker.validate_envelope(root, gate_checker.load_json(path),
                                         expected_artifacts=expected_artifacts)


def historical_schema_findings(root):
    """Known audit finding tied to preserved raw bytes; not a new behavior grade.

    Call only after validate() has checked raw hashes against frozen manifests.
    The historical integrity gate and frozen behavioral review remain separate
    from SC05 completeness; keeping their PASS never certifies this old record.
    """
    relative = "evaluation/citeguard/" + RUNS[-1] + "/raw/CE-T01.md"
    path = file_at(Path(root), relative)
    return [{"finding_id": "A02", "run_id": RUNS[-1], "case_id": "CE-T01",
             "artifact_ref": relative, "sha256": sha(path), "line_start": 5,
             "line_end": 17, "schema_valid": False,
             "missing_fields": ["artifact_ref", "artifact_revision", "applicable", "reason"],
             "reason": "Historical prose GateRecord lacks mandatory SC05 fields; frozen behavioral PASS is not SC05 PASS."}]


def validate(root=ROOT):
    root = Path(root)
    first_cases = first_rubric = None
    total = 0
    for index, name in enumerate(RUNS):
        folder = root / "evaluation/citeguard" / name
        inputs, manifest, review = [read(folder / n) for n in ("inputs.json", "run-manifest.json", "review.json")]
        rubric = read(folder / "rubric.json")
        if index == 0:
            first_cases, first_rubric = inputs["cases"], sha(folder / "rubric.json")
        require(inputs["cases"] == first_cases and sha(folder / "rubric.json") == first_rubric,
                "Cases or rubric changed across attempts")
        require(manifest["evidence_layer"] == "delegated_model_prompt_run" and manifest["configured_model"] == "gpt-6-luna",
                "Runner evidence layer or configured model changed")
        require("not installed-plugin activation" in manifest["runtime_context"], "Host boundary missing")
        require(manifest.get("input_sha256", manifest.get("inputs_sha256")) == sha(folder / "inputs.json"), "Input fingerprint mismatch")
        require(review["evidence_layer"] == "primary_review_of_delegated_run", "Review evidence layer changed")
        require(review["manifest_sha256"] == sha(folder / "run-manifest.json") and review["rubric_sha256"] == sha(folder / "rubric.json"), "Review provenance mismatch")
        expected = {c["id"] for c in inputs["cases"]}
        output_map = {o["case_id"]: o for o in manifest["outputs"]}
        review_map = {r["case_id"]: r for r in review["records"]}
        require(len(output_map) == len(manifest["outputs"]) == len(expected) and set(output_map) == expected, "Output case coverage mismatch")
        require(len(review_map) == len(review["records"]) == len(expected) and set(review_map) == expected, "Review case coverage mismatch")
        for cid, output in output_map.items():
            path = file_at(folder, output["output_path"])
            require(sha(path) == output["sha256"], "Raw output fingerprint mismatch")
            record = review_map[cid]
            require([c["criterion"] for c in record["criteria"]] == rubric["required_behavior_by_case"][cid], "Review does not match frozen criteria")
            for criterion in record["criteria"]:
                span = criterion["output_span"]
                require(span["path"] == output["output_path"] and span["sha256"] == output["sha256"], "Review output reference mismatch")
                require(type(span["line_start"]) is int and type(span["line_end"]) is int and 1 <= span["line_start"] <= span["line_end"] <= len(path.read_text(encoding="utf-8").splitlines()), "Review locator invalid")
                require(bool(criterion["reason"]), "Missing review reason")
            if record["status"] == "PASS":
                require(not record["hard_fail"] and all(c["status"] == "PASS" for c in record["criteria"]), "False case PASS")
        overrides = read(folder / "source-snapshot.json")["overrides"] if (folder / "source-snapshot.json").exists() else {}
        for relative, expected_hash in inputs["source_fingerprints"].items():
            actual = file_at(root, overrides.get(relative, relative))
            require(sha(actual) == expected_hash, "Candidate source fingerprint mismatch")
            item = manifest["candidate_source_fingerprints"][relative]
            recorded = item["actual_sha256"] if isinstance(item, dict) else item
            require(recorded == expected_hash, "Runner source identity mismatch")
        if index < len(RUNS) - 1:
            require(review["status"] == "FAIL" and any(r["hard_fail"] for r in review["records"]), "Historical failure was not preserved")
        else:
            require(review["status"] == "PASS" and all(r["status"] == "PASS" for r in review["records"]), "Final run has not passed primary review")
        total += len(output_map)
    return {"ok": True, "attempts": len(RUNS), "raw_outputs": total, "final_cases": len(expected),
            "semantic_verified_by_tool": False, "installed_host_verified": False,
            "historical_schema_findings": historical_schema_findings(root),
            "historical_sc05_certified": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sidecar", type=Path, help="Strictly validate a NEW captured JSON sidecar")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        print(json.dumps(validate_sidecar(args.sidecar, args.root) if args.sidecar else validate(args.root)))
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        raise SystemExit(1)
