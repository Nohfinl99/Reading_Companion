"""SC05 structural guards and paired valid controls; not semantic evaluation."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("gate_records", ROOT / "tools/validate_gate_records.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


@pytest.fixture
def sidecar(tmp_path):
    (tmp_path / "source.txt").write_text("In simulation S, recovery was 60%.\n", encoding="utf-8")
    (tmp_path / "artifact.md").write_text("Recovery was 60% in simulation S.\n", encoding="utf-8")
    def span(name):
        path = tmp_path / name
        return {"path": name, "sha256": checker.raw_hash(path), "line_start": 1,
                "line_end": 1, "excerpt": path.read_text(encoding="utf-8").strip()}
    record = {"gate_id": "G-CITATION-REVIEW", "artifact_ref": "artifact.md",
              "artifact_revision": 2, "applicable": True, "reason": "Review supplied simulation only",
              "status": "PASS", "source_spans": [span("source.txt")],
              "output_spans": [span("artifact.md")], "repair_owner": None, "unresolved": [],
              "checks": {key: {"status": "PASS", "reason": "Observed fixture behavior",
                                 "output_span_refs": [0], "source_span_refs": [0]}
                         for key in checker.CHECKS}}
    envelope = {"contract_version": "PS1", "scope": "Interpretation of supplied simulation",
                "evidence_layer": "assistant_authored_self_review",
                "artifacts": [{"artifact_ref": "artifact.md", "artifact_revision": 2,
                               "sha256": checker.raw_hash(tmp_path / "artifact.md")}],
                "gate_records": [record]}
    return tmp_path, envelope


def test_valid_sidecar_is_only_structurally_verified(sidecar):
    root, data = sidecar
    result = checker.validate_envelope(root, data, expected_artifacts={"artifact.md": 2})
    assert result["ok"] is True
    assert result["semantic_verified"] is False
    assert result["host_verified"] is False
    assert result["revision_baseline"] == "caller"


@pytest.mark.parametrize("field", sorted(checker.REQUIRED))
def test_new_record_missing_required_field_is_rejected(sidecar, field):
    root, data = sidecar
    del data["gate_records"][0][field]
    with pytest.raises(checker.GateValidationError, match="Missing GateRecord fields"):
        checker.validate_envelope(root, data)


def test_record_revision_must_match_registry(sidecar):
    root, data = sidecar
    data["gate_records"][0]["artifact_revision"] = 1
    with pytest.raises(checker.GateValidationError, match="Stale artifact revision"):
        checker.validate_envelope(root, data)


def test_declared_registry_cannot_override_callers_current_revision(sidecar):
    root, data = sidecar
    with pytest.raises(checker.GateValidationError, match="caller baseline"):
        checker.validate_envelope(root, data, expected_artifacts={"artifact.md": 3})


@pytest.mark.parametrize("name", ["source.txt", "artifact.md"])
def test_stale_bytes_are_rejected(sidecar, name):
    root, data = sidecar
    with (root / name).open("a", encoding="utf-8") as handle:
        handle.write("Changed content.\n")
    with pytest.raises(checker.GateValidationError, match="Stale .* fingerprint"):
        checker.validate_envelope(root, data)


@pytest.mark.parametrize("path", ["../private.txt", "C:/private.txt", "C:\\private.txt", "/private.txt"])
def test_cross_platform_path_escape_is_rejected(sidecar, path):
    root, data = sidecar
    data["gate_records"][0]["source_spans"][0]["path"] = path
    with pytest.raises(checker.GateValidationError, match="escapes repository"):
        checker.validate_envelope(root, data)


def test_symlink_escape_is_rejected(sidecar):
    root, data = sidecar
    outside = root.parent / "outside-evidence.txt"
    outside.write_text("Outside evidence.\n", encoding="utf-8")
    try:
        os.symlink(outside, root / "outside-link.txt")
    except OSError as error:
        pytest.skip("Symlink creation unavailable: " + str(error))
    data["gate_records"][0]["source_spans"][0]["path"] = "outside-link.txt"
    with pytest.raises(checker.GateValidationError, match="escapes repository"):
        checker.validate_envelope(root, data)


def test_artifact_path_alias_cannot_declare_two_revisions(sidecar):
    root, data = sidecar
    duplicate = copy.deepcopy(data["artifacts"][0])
    duplicate.update(artifact_ref="./artifact.md", artifact_revision=3)
    data["artifacts"].append(duplicate)
    with pytest.raises(checker.GateValidationError, match="Duplicate artifact registry"):
        checker.validate_envelope(root, data)


def test_span_must_exist_and_contain_excerpt(sidecar):
    root, data = sidecar
    span = data["gate_records"][0]["source_spans"][0]
    span["line_end"] = 2
    with pytest.raises(checker.GateValidationError, match="Invalid evidence locator"):
        checker.validate_envelope(root, data)
    span["line_end"] = 1
    span["excerpt"] = "Fabricated excerpt"
    with pytest.raises(checker.GateValidationError, match="Excerpt not"):
        checker.validate_envelope(root, data)


def test_output_must_be_the_reviewed_artifact(sidecar):
    root, data = sidecar
    data["gate_records"][0]["output_spans"] = copy.deepcopy(data["gate_records"][0]["source_spans"])
    with pytest.raises(checker.GateValidationError, match="does not match reviewed artifact"):
        checker.validate_envelope(root, data)


@pytest.mark.parametrize("status", ["NOT_RUN", "PARTIAL", "FAIL"])
def test_pass_cannot_hide_unpassed_required_check(sidecar, status):
    root, data = sidecar
    data["gate_records"][0]["checks"]["CR02"]["status"] = status
    with pytest.raises(checker.GateValidationError, match="PASS contains"):
        checker.validate_envelope(root, data)


def test_pass_cannot_hide_unresolved_gap(sidecar):
    root, data = sidecar
    data["gate_records"][0]["unresolved"] = ["Required source not checked"]
    with pytest.raises(checker.GateValidationError, match="PASS has unresolved"):
        checker.validate_envelope(root, data)


def test_pass_check_needs_actual_output_reference(sidecar):
    root, data = sidecar
    data["gate_records"][0]["checks"]["CR02"]["output_span_refs"] = []
    with pytest.raises(checker.GateValidationError, match="PASS check lacks"):
        checker.validate_envelope(root, data)


def test_non_applicable_route_does_not_execute_ce(sidecar):
    root, data = sidecar
    gate = data["gate_records"][0]
    gate.update(applicable=False, reason="Progress only", status="NOT_RUN", checks={})
    assert checker.validate_envelope(root, data)["ok"] is True
    gate["status"] = "PASS"
    with pytest.raises(checker.GateValidationError, match="Non-applicable gate"):
        checker.validate_envelope(root, data)


def test_partial_is_valid_for_in_scope_unresolved_check(sidecar):
    root, data = sidecar
    gate = data["gate_records"][0]
    gate.update(status="PARTIAL", unresolved=["Additional source context unavailable"], repair_owner="CE02")
    gate["checks"]["CR02"]["status"] = "NOT_RUN"
    assert checker.validate_envelope(root, data)["ok"] is True


def test_cli_validates_actual_sidecar_and_rejects_duplicate_json_key(sidecar):
    root, data = sidecar
    sidecar_path = root / "gate.json"
    sidecar_path.write_text(json.dumps(data), encoding="utf-8")
    result = subprocess.run([sys.executable, str(ROOT / "tools/validate_gate_records.py"),
                             str(sidecar_path), "--root", str(root),
                             "--expected-artifact", "artifact.md=2"], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["semantic_verified"] is False
    adapter = subprocess.run([sys.executable, str(ROOT / "tools/validate_luna_rerun.py"),
                              "--sidecar", str(sidecar_path), "--root", str(root)],
                             capture_output=True, text=True)
    assert adapter.returncode == 0, adapter.stdout + adapter.stderr
    assert json.loads(adapter.stdout)["semantic_verified"] is False
    sidecar_path.write_text('{"scope":"a","scope":"b"}', encoding="utf-8")
    with pytest.raises(checker.GateValidationError, match="Duplicate JSON key"):
        checker.load_json(sidecar_path)
