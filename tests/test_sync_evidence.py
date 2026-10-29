"""Tamper checks for real captured files; they do not grade semantic truth."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("sync_evidence", ROOT / "tools/validate_sync_evidence.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


@pytest.fixture
def capture(tmp_path):
    shutil.copytree(ROOT / checker.RUN, tmp_path / checker.RUN)
    for relative in checker.CONTEXT:
        target = tmp_path / checker.SKILL / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / checker.RUN / "context" / (relative + ".txt"), target)
    return tmp_path


def test_actual_capture_is_structurally_valid_in_its_scope():
    result = checker.validate()
    assert result["cases"] == 1
    assert result["criteria"] == 3
    assert result["structural_records"] == 1
    assert result["prior_scope_finding_retained"] is True
    assert result["semantic_verified_by_tool"] is False
    assert result["installed_host_verified"] is False
    assert result["gold_exclusion"] == "instruction_only_shared_filesystem"


@pytest.mark.parametrize("name,label", [("artifact.md", "Output"), ("sidecar.json", "Output"),
                                       ("rubric.json", "Rubric"), ("inputs.json", "Input"),
                                       ("fixture.txt", "Fixture"),
                                       ("context/references/citation-evidence.md.txt", "Context snapshot"),
                                       ("attempt1/artifact.md", "Prior attempt")])
def test_tampered_captured_bytes_are_rejected(capture, name, label):
    path = capture / checker.RUN / name
    path.write_bytes(path.read_bytes() + b"\n ")  # Valid trailing JSON whitespace where applicable.
    with pytest.raises(ValueError, match=label + " fingerprint mismatch"):
        checker.validate(capture)


def test_review_cannot_claim_pass_with_unpassed_criterion(capture):
    path = capture / checker.RUN / "review.json"
    review = json.loads(path.read_text(encoding="utf-8"))
    review["criteria"][0]["status"] = "NOT_RUN"
    path.write_text(json.dumps(review), encoding="utf-8")
    with pytest.raises(ValueError, match="False review PASS"):
        checker.validate(capture)


def test_review_evidence_must_have_real_locator(capture):
    path = capture / checker.RUN / "review.json"
    review = json.loads(path.read_text(encoding="utf-8"))
    review["criteria"][0]["output"]["line_end"] = 9999
    path.write_text(json.dumps(review), encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid review locator"):
        checker.validate(capture)


def test_future_context_edit_keeps_history_but_fails_current_release_check(capture):
    path = capture / checker.SKILL / "references/citation-evidence.md"
    path.write_bytes(path.read_bytes() + b"\nNew candidate revision.\n")
    assert checker.validate(capture)["current_context_checked"] is False
    with pytest.raises(ValueError, match="Current context fingerprint mismatch"):
        checker.validate(capture, require_current_context=True)


def test_cli_checks_captured_sidecar_with_caller_revision(capture):
    result = subprocess.run([sys.executable, str(ROOT / "tools/validate_sync_evidence.py"),
                             "--root", str(capture), "--require-current-context"],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["current_context_checked"] is True
