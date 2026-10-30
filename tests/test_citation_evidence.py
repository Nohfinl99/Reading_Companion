"""Tamper/rejection checks for public evidence; not semantic prompt evaluations."""
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("citation_evidence", ROOT / "tools/validate_citation_evidence.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


@pytest.fixture
def copy_repo(tmp_path):
    for part in ("evaluation/citeguard", "skills/sid-reading-companion/references/knowledge"):
        shutil.copytree(ROOT / part, tmp_path / part)
    return tmp_path


def mutate(root, change):
    path = root / checker.REVIEW
    obj = json.loads(path.read_text(encoding="utf-8"))
    change(obj)
    path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")


def test_valid_records_are_only_mechanically_verified():
    result = checker.validate()
    assert result["cases"] == 8
    assert result["semantic_verified"] is False
    assert result["host_verified"] is False


def test_missing_case_is_rejected(copy_repo):
    mutate(copy_repo, lambda obj: obj["records"].pop())
    with pytest.raises(checker.EvidenceError, match="coverage"):
        checker.validate(copy_repo)


def test_stale_output_is_rejected(copy_repo):
    path = copy_repo / "evaluation/citeguard/outputs/CE-T01.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nChanged meaning.\n", encoding="utf-8")
    with pytest.raises(checker.EvidenceError, match="Stale evidence"):
        checker.validate(copy_repo)


def test_fabricated_excerpt_is_rejected(copy_repo):
    mutate(copy_repo, lambda obj: obj["records"][0]["gate_record"]["source_spans"][0].update(excerpt="FABRICATED EVIDENCE"))
    with pytest.raises(checker.EvidenceError, match="Excerpt not"):
        checker.validate(copy_repo)


def test_missing_required_check_is_rejected(copy_repo):
    mutate(copy_repo, lambda obj: obj["records"][0]["gate_record"]["checks"].pop("CR02"))
    with pytest.raises(checker.EvidenceError, match="Required review check"):
        checker.validate(copy_repo)


def test_false_pass_with_unrun_check_is_rejected(copy_repo):
    mutate(copy_repo, lambda obj: obj["records"][0]["gate_record"]["checks"]["CR02"].update(status="NOT_RUN"))
    with pytest.raises(checker.EvidenceError, match="PASS contains"):
        checker.validate(copy_repo)


def test_source_escape_is_rejected(copy_repo):
    mutate(copy_repo, lambda obj: obj["records"][0]["gate_record"]["source_spans"][0].update(path="../private.txt"))
    with pytest.raises(checker.EvidenceError, match="escapes repository"):
        checker.validate(copy_repo)


def test_fixture_cannot_be_relabelled_independent(copy_repo):
    mutate(copy_repo, lambda obj: obj.update(evidence_layer="independently_reviewed"))
    with pytest.raises(checker.EvidenceError, match="cannot be promoted"):
        checker.validate(copy_repo)


def test_unknown_graph_endpoint_is_rejected(copy_repo):
    path = copy_repo / "skills/sid-reading-companion/references/knowledge/citeguard-relations.json"
    obj = json.loads(path.read_text(encoding="utf-8"))
    obj["relations"][0]["target"] = "CG-MISSING"
    path.write_text(json.dumps(obj), encoding="utf-8")
    with pytest.raises(checker.EvidenceError, match="Unknown relation endpoint"):
        checker.validate(copy_repo)


def test_application_note_references_do_not_declare_units(copy_repo):
    path = copy_repo / "skills/sid-reading-companion/references/knowledge/citeguard.md"
    text = path.read_text(encoding="utf-8")
    # Both existing IDs and a reference-only unknown ID stay outside declarations.
    text += "\n## Application notes regression fixture\n\n| CG-01 | reference |\n| CG-99 | reference only |\n"
    path.write_text(text, encoding="utf-8")
    assert checker.validate(copy_repo)["knowledge_units"] == 7


def test_duplicate_declaration_inside_units_is_still_rejected(copy_repo):
    path = copy_repo / "skills/sid-reading-companion/references/knowledge/citeguard.md"
    text = path.read_text(encoding="utf-8")
    text = text.replace("## Units\n", "## Units\n\n| CG-01 | duplicate declaration | locator |\n", 1)
    path.write_text(text, encoding="utf-8")
    with pytest.raises(checker.EvidenceError, match="Duplicate knowledge unit"):
        checker.validate(copy_repo)
