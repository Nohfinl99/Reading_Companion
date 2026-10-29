"""Reject tampered run evidence; these tests do not grade model semantics."""
import importlib.util
import json
from pathlib import Path
import shutil

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("luna_evidence", ROOT / "tools/validate_luna_rerun.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


@pytest.fixture
def evidence_copy(tmp_path):
    for name in checker.RUNS:
        shutil.copytree(ROOT / "evaluation/citeguard" / name, tmp_path / "evaluation/citeguard" / name)
    inputs = json.loads((ROOT / "evaluation/citeguard" / checker.RUNS[-1] / "inputs.json").read_text(encoding="utf-8"))
    for relative in inputs["source_fingerprints"]:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    return tmp_path


def edit_manifest(root, change):
    path = root / "evaluation/citeguard" / checker.RUNS[-1] / "run-manifest.json"
    obj = json.loads(path.read_text(encoding="utf-8"))
    change(obj)
    path.write_text(json.dumps(obj), encoding="utf-8")


def test_run_integrity_is_not_semantic_verification():
    result = checker.validate()
    assert result["raw_outputs"] == 30
    assert result["semantic_verified_by_tool"] is False


def test_changed_raw_output_is_rejected(evidence_copy):
    path = evidence_copy / "evaluation/citeguard" / checker.RUNS[-1] / "raw/CE-T07.md"
    path.write_text("Fabricated state.", encoding="utf-8")
    with pytest.raises(ValueError, match="Raw output fingerprint"):
        checker.validate(evidence_copy)


def test_run_cannot_be_promoted_to_host(evidence_copy):
    edit_manifest(evidence_copy, lambda obj: obj.update(evidence_layer="actual_host_run"))
    with pytest.raises(ValueError, match="evidence layer"):
        checker.validate(evidence_copy)


def test_missing_output_is_rejected(evidence_copy):
    path = evidence_copy / "evaluation/citeguard" / checker.RUNS[-1] / "raw/CE-T08.md"
    path.unlink()
    with pytest.raises(ValueError, match="Evidence path missing"):
        checker.validate(evidence_copy)


def test_referenced_source_snapshot_must_match_run(evidence_copy):
    folder = evidence_copy / "evaluation/citeguard" / checker.RUNS[-1]
    override = json.loads((folder / "source-snapshot.json").read_text(encoding="utf-8"))["overrides"]
    path = evidence_copy / override["skills/sid-reading-companion/references/citation-evidence.md"]
    path.write_text(path.read_text(encoding="utf-8") + "\nNew runtime rule.\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Candidate source fingerprint"):
        checker.validate(evidence_copy)


def test_historical_raw_is_unchanged_and_schema_finding_stays_visible(evidence_copy):
    raw = evidence_copy / "evaluation/citeguard" / checker.RUNS[-1] / "raw/CE-T01.md"
    before = raw.read_bytes()
    result = checker.validate(evidence_copy)
    assert raw.read_bytes() == before
    assert result["ok"] is True  # Frozen run integrity, not old SC05 certification.
    assert result["historical_sc05_certified"] is False
    finding = result["historical_schema_findings"][0]
    assert finding["schema_valid"] is False
    assert finding["sha256"] == checker.sha(raw)
    assert "artifact_revision" in finding["missing_fields"]
