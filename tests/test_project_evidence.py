"""Structural checks for the 0.3.8 project-evidence audit helper."""
import hashlib
import importlib.util
import json
from pathlib import Path
import os

import pytest

ROOT = Path(__file__).resolve().parents[1]
HELPER_PATH = ROOT / "skills/sid-reading-companion/scripts/project_evidence.py"
spec = importlib.util.spec_from_file_location("project_evidence", HELPER_PATH)
project_evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(project_evidence)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit_files(tmp_path):
    root = tmp_path / "record-root"
    root.mkdir()
    artifact = root / "answer.md"
    source = root / "source.md"
    artifact.write_text("Selected direct evidence for service A.\n", encoding="utf-8")
    source.write_text("The source reports service A checks passed.\n", encoding="utf-8")
    artifact_hash, source_hash = digest(artifact), digest(source)
    output_span = {"path": "answer.md", "sha256": artifact_hash, "line_start": 1, "line_end": 1,
                   "excerpt": "Selected direct evidence for service A."}
    source_span = {"path": "source.md", "sha256": source_hash, "line_start": 1, "line_end": 1,
                   "excerpt": "The source reports service A checks passed."}
    record = {
        "contract_version": project_evidence.PROFILE_VERSION,
        "case_id": "synthetic-case",
        "artifact": {"path": "answer.md", "sha256": artifact_hash},
        "selection": {
            "selection_id": "S1", "purpose": "Report service A evidence", "scope": "service A in supplied file",
            "basis": "ai_selection", "universe_ref": "supplied source file", "criterion": "Direct service A evidence",
            "members": [{"ref": "source.md#1", "origin": "source", "source_locators": [source_span],
                         "inclusion_reason": "Directly addresses the target component."}],
            "exclusions_or_not_evaluated": "No other sources supplied; corpus outside this file not examined.",
            "completeness": "complete_in_verified_scope", "count": 1, "count_basis": "derived_after_selection",
        },
        "searched": {
            "boundary": "One supplied source file for service A", "inspected": ["source.md"],
            "not_examined": ["Files outside the bundle"],
            "stop_reason": "The supplied source directly addresses the target; no other files were included.",
            "stop_basis": [source_span],
        },
        "source_context": {
            "source_snapshot": {"source_id": "SYN-1", "path": "source.md", "sha256": source_hash,
                                "document_version": "1", "document_date": "2026-10-30"},
            "implementation_revision": {"status": "unknown", "value": None, "evidence": []},
            "current_runtime": {"status": "unknown", "value": None, "evidence": []},
        },
        "handoff": {"next_owner": "reviewer-Z", "ack_status": "unknown", "ack_evidence": []},
        "narrative": "The audit is limited to the supplied source.",
    }
    record_path = root / "record.json"
    record_path.write_text(json.dumps(record), encoding="utf-8")
    return root, record_path, record, output_span, source_span


def review_for(result, record, output_span, source_span):
    return {
        "review_version": "project-evidence-review-0.3.8",
        "input_artifact_sha256": record["artifact"]["sha256"],
        "rendered_artifact": {"path": "visible.md", "sha256": result["rendered_sha256"]},
        "source_sha256": record["source_context"]["source_snapshot"]["sha256"],
        "reviewer": "human-reviewer-1",
        "criterion": "All frozen selection and handoff criteria are met.",
        "reason": "Each required check was compared to the supplied source and rendered artifact.",
        "status": "PASS",
        "checks": {
            key: {"status": "PASS", "reason": f"Reviewed {key} against the stated criterion.",
                  "output_spans": [output_span], "source_spans": [source_span]}
            for key in ("selection_and_scope", "stop_reason", "source_snapshot_identity",
                        "implementation_and_runtime_boundary", "handoff_owner_and_ack")
        },
    }


def test_validate_renders_required_fields_and_defaults_to_partial(tmp_path):
    root, record_path, record, _, _ = audit_files(tmp_path)
    result = project_evidence.audit(record_path, root)
    assert result["readiness"] == "PARTIAL"
    assert result["review_status"] == "NOT_RUN"
    assert result["semantic_verified"] is False
    visible = result["visible_block"]
    for required in ("Selection criterion", "Search boundary", "Stop reason and basis",
                     "Source snapshot identity", "Implementation revision: unknown / not verified",
                     "Current runtime: unknown / not verified", "Next owner", "ACK: unknown"):
        assert required in visible
    assert "source.md:1-1" in visible


@pytest.mark.parametrize("field,value", [
    ("stop_reason", ""),
    ("stop_reason", "done"),
])
def test_missing_or_placeholder_stop_reason_fails_closed(tmp_path, field, value):
    root, record_path, record, _, _ = audit_files(tmp_path)
    record["searched"][field] = value
    record_path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(project_evidence.AuditError, match="stop_reason"):
        project_evidence.audit(record_path, root)


def test_missing_runtime_boundary_fails_closed(tmp_path):
    root, record_path, record, _, _ = audit_files(tmp_path)
    del record["source_context"]["current_runtime"]
    record_path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(project_evidence.AuditError, match="current_runtime"):
        project_evidence.audit(record_path, root)


def test_known_revision_requires_hash_bound_source_locator(tmp_path):
    root, record_path, record, _, _ = audit_files(tmp_path)
    record["source_context"]["implementation_revision"] = {
        "status": "known", "value": "rev-1", "evidence": [{"path": "source.md"}]
    }
    record_path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(project_evidence.AuditError, match="implementation_revision evidence"):
        project_evidence.audit(record_path, root)


def test_visible_block_renders_known_version_and_confirmed_ack_locators(tmp_path):
    root, record_path, record, _, source_span = audit_files(tmp_path)
    record["source_context"]["implementation_revision"] = {
        "status": "known", "value": "rev-1", "evidence": [source_span]
    }
    record["source_context"]["current_runtime"] = {
        "status": "known", "value": "runtime-1", "evidence": [source_span]
    }
    record["handoff"] = {"next_owner": "consumer-A", "ack_status": "confirmed",
                         "ack_evidence": [source_span]}
    record_path.write_text(json.dumps(record), encoding="utf-8")
    visible = project_evidence.audit(record_path, root)["visible_block"]
    assert "Implementation revision: rev-1; evidence: source.md:1-1" in visible
    assert "Current runtime: runtime-1; evidence: source.md:1-1" in visible
    assert "consumer ACK: confirmed; evidence: source.md:1-1" in visible


def test_source_excerpt_preserves_literal_unknown_text(tmp_path):
    root, _, _, _, _ = audit_files(tmp_path)
    source = root / "unknown.md"
    source.write_text("The recorded value is unknown.\n", encoding="utf-8")
    span = {"path": "unknown.md", "sha256": digest(source), "line_start": 1, "line_end": 1,
            "excerpt": "unknown"}
    assert project_evidence.check_span(root, span, "quoted source") == "unknown.md"


def test_self_declared_readiness_field_is_rejected_by_record_contract(tmp_path):
    root, record_path, record, _, _ = audit_files(tmp_path)
    record["readiness"] = "READY"
    record_path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(project_evidence.AuditError, match="Unexpected audit record fields"):
        project_evidence.audit(record_path, root)


def test_matching_structural_r14_record_can_unlock_readiness_without_semantic_claim(tmp_path):
    root, record_path, record, output_span, source_span = audit_files(tmp_path)
    result = project_evidence.audit(record_path, root)
    visible_path = root / "visible.md"
    visible_path.write_bytes(result["visible_block"].encode("utf-8"))
    visible_span = {"path": "visible.md", "sha256": digest(visible_path), "line_start": 1, "line_end": 1,
                    "excerpt": result["visible_block"].splitlines()[0]}
    review = review_for(result, record, visible_span, source_span)
    review_path = root / "review.json"
    review_path.write_text(json.dumps(review), encoding="utf-8")
    verified = project_evidence.audit(record_path, root, review_path, "visible.md")
    assert verified["readiness"] == "READY"
    assert verified["review_record_is_structural_only"] is True
    assert verified["semantic_verified"] is False


def test_review_for_different_rendered_output_is_rejected(tmp_path):
    root, record_path, record, output_span, source_span = audit_files(tmp_path)
    first = project_evidence.audit(record_path, root)
    visible_path = root / "visible.md"
    visible_path.write_bytes(first["visible_block"].encode("utf-8"))
    visible_span = {"path": "visible.md", "sha256": digest(visible_path), "line_start": 1, "line_end": 1,
                    "excerpt": first["visible_block"].splitlines()[0]}
    review = review_for(first, record, visible_span, source_span)
    record["narrative"] = "Changed after review."
    record_path.write_text(json.dumps(record), encoding="utf-8")
    review_path = root / "review.json"
    review_path.write_text(json.dumps(review), encoding="utf-8")
    with pytest.raises(project_evidence.AuditError, match="Persisted rendered artifact"):
        project_evidence.audit(record_path, root, review_path, "visible.md")


def test_review_cannot_cite_raw_input_as_the_rendered_output(tmp_path):
    root, record_path, record, output_span, source_span = audit_files(tmp_path)
    result = project_evidence.audit(record_path, root)
    visible_path = root / "visible.md"
    visible_path.write_bytes(result["visible_block"].encode("utf-8"))
    review = review_for(result, record, output_span, source_span)
    review_path = root / "review.json"
    review_path.write_text(json.dumps(review), encoding="utf-8")
    with pytest.raises(project_evidence.AuditError, match="does not point to the bound artifact"):
        project_evidence.audit(record_path, root, review_path, "visible.md")


def test_review_can_cite_a_record_referenced_secondary_source(tmp_path):
    root, record_path, record, _, _ = audit_files(tmp_path)
    build = root / "signed-build.txt"
    build.write_text("Signed build revision is rev-1; deployment is not stated.\n", encoding="utf-8")
    build_span = {"path": "signed-build.txt", "sha256": digest(build), "line_start": 1, "line_end": 1,
                  "excerpt": "Signed build revision is rev-1; deployment is not stated."}
    record["source_context"]["implementation_revision"] = {
        "status": "known", "value": "rev-1", "evidence": [build_span]
    }
    record_path.write_text(json.dumps(record), encoding="utf-8")
    result = project_evidence.audit(record_path, root)
    visible_path = root / "visible.md"
    visible_path.write_bytes(result["visible_block"].encode("utf-8"))
    visible_span = {"path": "visible.md", "sha256": digest(visible_path), "line_start": 1, "line_end": 1,
                    "excerpt": result["visible_block"].splitlines()[0]}
    review = review_for(result, record, visible_span, build_span)
    review_path = root / "review.json"
    review_path.write_text(json.dumps(review), encoding="utf-8")
    verified = project_evidence.audit(record_path, root, review_path, "visible.md")
    assert verified["readiness"] == "READY"
    assert verified["semantic_verified"] is False


def test_review_rejects_unreferenced_source_even_inside_standalone_root(tmp_path):
    root, record_path, record, _, source_span = audit_files(tmp_path)
    unrelated = root / "unreferenced.md"
    unrelated.write_text("Unreferenced evidence must not be used.\n", encoding="utf-8")
    unrelated_span = {"path": "unreferenced.md", "sha256": digest(unrelated), "line_start": 1,
                      "line_end": 1, "excerpt": "Unreferenced evidence must not be used."}
    result = project_evidence.audit(record_path, root)
    visible_path = root / "visible.md"
    visible_path.write_bytes(result["visible_block"].encode("utf-8"))
    visible_span = {"path": "visible.md", "sha256": digest(visible_path), "line_start": 1, "line_end": 1,
                    "excerpt": result["visible_block"].splitlines()[0]}
    review = review_for(result, record, visible_span, unrelated_span)
    review_path = root / "review.json"
    review_path.write_text(json.dumps(review), encoding="utf-8")
    with pytest.raises(project_evidence.AuditError, match="case's declared evidence allowlist"):
        project_evidence.audit(record_path, root, review_path, "visible.md")


def bundle_source(tmp_path):
    root = tmp_path / "candidate"
    for relative, contents in {
        "plugin.json": json.dumps({"version": "0.3.8"}),
        ".codex-plugin/plugin.json": json.dumps({"version": "0.3.8"}),
        "packaging/runtime-files.json": json.dumps({"schema_version": 1, "runtime_files": [
            "skills/sid-reading-companion/SKILL.md", "skills/sid-reading-companion/scripts/project_evidence.py"]}),
        "skills/sid-reading-companion/SKILL.md": "# Skill 0.3.8\n",
        "skills/sid-reading-companion/scripts/project_evidence.py": "# Runtime helper 0.3.8\n",
        "evaluation/project-evidence/0.3.8/cases/one/input.md": "Run case one only.\n",
        "evaluation/project-evidence/0.3.8/cases/one/source.md": "Case one source.\n",
        "evaluation/project-evidence/0.3.8/cases/one/signed-build.txt": "Signed build revision is rev-1; deployment is not stated.\n",
        "evaluation/project-evidence/0.3.8/cases/two/input.md": "Other case prompt.\n",
        "evaluation/project-evidence/0.3.8/rubric.json": "{\"gold\": \"evaluator only\"}\n",
    }.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
    spec_path = root / "evaluation/project-evidence/0.3.8/case-specs/one.json"
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    spec_path.write_text(json.dumps({
        "profile_version": project_evidence.PROFILE_VERSION,
        "case_id": "one",
        "input": "evaluation/project-evidence/0.3.8/cases/one/input.md",
        "sources": [
            {"path": "evaluation/project-evidence/0.3.8/cases/one/source.md"},
            {"path": "evaluation/project-evidence/0.3.8/cases/one/signed-build.txt"},
        ],
        "runtime_context": ["skills/sid-reading-companion/SKILL.md",
                            "skills/sid-reading-companion/scripts/project_evidence.py"],
    }), encoding="utf-8")
    return root, spec_path


def test_exporter_only_copies_case_allowlist_and_checker_detects_stale_source(tmp_path):
    root, spec_path = bundle_source(tmp_path)
    bundle = tmp_path / "bundle-one"
    result = project_evidence.export_case_bundle(root, spec_path, bundle)
    assert result["ok"] is True
    paths = {entry["path"] for entry in json.loads((bundle / "bundle-manifest.json").read_text())["files"]}
    assert "evaluation/project-evidence/0.3.8/cases/one/input.md" in paths
    assert "evaluation/project-evidence/0.3.8/cases/two/input.md" not in paths
    assert "evaluation/project-evidence/0.3.8/rubric.json" not in paths
    assert project_evidence.check_bundle(bundle, source_root=root)["source_current_checked"] is True
    (root / "skills/sid-reading-companion/SKILL.md").write_text("# Mutated\n", encoding="utf-8")
    with pytest.raises(project_evidence.AuditError, match="Stale release context/source capture"):
        project_evidence.check_bundle(bundle, source_root=root)


def test_end_to_end_bundle_keeps_input_immutable_and_outputs_external(tmp_path, capsys):
    source_root, spec_path = bundle_source(tmp_path)
    bundle = tmp_path / "immutable-bundle-one"
    assert project_evidence.main([
        "export", "--source-root", str(source_root), "--case-spec", str(spec_path),
        "--output", str(bundle),
    ]) == 0
    assert json.loads(capsys.readouterr().out)["ok"] is True
    output_root = tmp_path / "runner-output-one"
    output_root.mkdir()
    source_relative = "evaluation/project-evidence/0.3.8/cases/one/source.md"
    source_file = bundle / source_relative
    source_hash = digest(source_file)
    source_excerpt = "Case one source."
    source_span = {"path": source_relative, "sha256": source_hash, "line_start": 1, "line_end": 1,
                   "excerpt": source_excerpt}
    build_relative = "evaluation/project-evidence/0.3.8/cases/one/signed-build.txt"
    build_file = bundle / build_relative
    build_span = {"path": build_relative, "sha256": digest(build_file), "line_start": 1, "line_end": 1,
                  "excerpt": "Signed build revision is rev-1; deployment is not stated."}
    answer = output_root / "answer.md"
    answer.write_text("Direct evidence was selected for the target.\n", encoding="utf-8")
    record = {
        "contract_version": project_evidence.PROFILE_VERSION,
        "case_id": "one",
        "artifact": {"path": "answer.md", "sha256": digest(answer)},
        "selection": {"selection_id": "S1", "purpose": "Summarize the case source", "scope": "case one source",
                      "basis": "ai_selection", "universe_ref": "one source file in the bundle",
                      "criterion": "Directly addresses the task", "members": [
                          {"ref": "source.md#1", "origin": "source", "source_locators": [source_span],
                           "inclusion_reason": "The source addresses the requested component."}],
                      "exclusions_or_not_evaluated": "Other case files are not in the bundle.",
                      "completeness": "complete_in_verified_scope", "count": 1, "count_basis": "derived_after_selection"},
        "searched": {"boundary": "One source file in case one", "inspected": [source_relative],
                     "not_examined": ["Sources outside this bundle"],
                     "stop_reason": "The supplied source addresses the task and no other source was supplied.",
                     "stop_basis": [source_span]},
        "source_context": {"source_snapshot": {"source_id": "CASE-ONE", "path": source_relative,
                              "sha256": source_hash, "document_version": "1", "document_date": None},
                           "implementation_revision": {"status": "known", "value": "rev-1", "evidence": [build_span]},
                           "current_runtime": {"status": "unknown", "value": None, "evidence": []}},
        "handoff": {"next_owner": "reviewer", "ack_status": "unknown", "ack_evidence": []},
    }
    record_path = output_root / "record.json"
    record_path.write_text(json.dumps(record), encoding="utf-8")
    assert project_evidence.main([
        "render", str(record_path), "--root", str(bundle), "--output-root", str(output_root),
        "--output", "visible.md",
    ]) == 0
    rendered = (output_root / "visible.md").read_text(encoding="utf-8")
    assert "Stop reason and basis" in rendered
    assert f"Implementation revision: rev-1; evidence: {build_relative}:1-1" in rendered
    first = project_evidence.audit(record_path, bundle, output_root=output_root)
    visible_path = output_root / "visible.md"
    visible_span = {"path": "visible.md", "sha256": digest(visible_path), "line_start": 1, "line_end": 1,
                    "excerpt": first["visible_block"].splitlines()[0]}
    review = review_for(first, record, visible_span, source_span)
    review["checks"]["implementation_and_runtime_boundary"]["source_spans"] = [build_span]
    review_path = output_root / "review.json"
    review_path.write_text(json.dumps(review), encoding="utf-8")
    assert project_evidence.main([
        "validate", str(record_path), "--root", str(bundle), "--output-root", str(output_root),
        "--review", "review.json", "--visible", "visible.md",
    ]) == 0
    final = json.loads(capsys.readouterr().out)
    assert final["readiness"] == "READY"
    assert final["semantic_verified"] is False
    assert project_evidence.main(["check-bundle", str(bundle), "--source-root", str(source_root)]) == 0
    assert json.loads(capsys.readouterr().out)["source_current_checked"] is True
    assert {path.name for path in output_root.iterdir()} == {"answer.md", "record.json", "visible.md", "review.json"}
    runtime_relative = "skills/sid-reading-companion/SKILL.md"
    runtime_path = bundle / runtime_relative
    runtime_excerpt = runtime_path.read_text(encoding="utf-8").splitlines()[0]
    review["checks"]["implementation_and_runtime_boundary"]["source_spans"] = [{
        "path": runtime_relative, "sha256": digest(runtime_path), "line_start": 1, "line_end": 1,
        "excerpt": runtime_excerpt,
    }]
    review_path.write_text(json.dumps(review), encoding="utf-8")
    assert project_evidence.main([
        "validate", str(record_path), "--root", str(bundle), "--output-root", str(output_root),
        "--review", "review.json", "--visible", "visible.md",
    ]) == 1
    assert "case's declared evidence allowlist" in capsys.readouterr().err
    record["selection"]["members"][0]["source_locators"] = [{
        "path": runtime_relative, "sha256": digest(runtime_path), "line_start": 1, "line_end": 1,
        "excerpt": runtime_excerpt,
    }]
    record_path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(project_evidence.AuditError, match="case's declared evidence allowlist"):
        project_evidence.audit(record_path, bundle, output_root=output_root)


def test_immutable_bundle_rejects_any_unmanifested_file(tmp_path):
    source_root, spec_path = bundle_source(tmp_path)
    bundle = tmp_path / "immutable-bundle"
    project_evidence.export_case_bundle(source_root, spec_path, bundle)
    (bundle / "neighbor-prompt.md").write_text("other case", encoding="utf-8")
    with pytest.raises(project_evidence.AuditError, match="Unexpected file in immutable case bundle"):
        project_evidence.check_bundle(bundle)


def test_exporter_rejects_path_traversal_and_does_not_overwrite(tmp_path):
    root, spec_path = bundle_source(tmp_path)
    spec_data = json.loads(spec_path.read_text(encoding="utf-8"))
    spec_data["sources"] = [{"path": "../two/input.md"}]
    spec_path.write_text(json.dumps(spec_data), encoding="utf-8")
    with pytest.raises(project_evidence.AuditError, match="Unsafe relative path"):
        project_evidence.export_case_bundle(root, spec_path, tmp_path / "unsafe")


def test_renderer_refuses_existing_regular_file_and_preserves_bytes(tmp_path):
    root, record_path, _, _, _ = audit_files(tmp_path)
    target = root / "visible.md"
    original = b"user-owned output\x00preserve"
    target.write_bytes(original)
    with pytest.raises(project_evidence.AuditError, match="Refusing to overwrite"):
        project_evidence.write_new_output(root, "visible.md", "replacement")
    assert target.read_bytes() == original


def test_renderer_refuses_dangling_symlink_without_touching_target(tmp_path):
    root, _, _, _, _ = audit_files(tmp_path)
    dangling = root / "visible.md"
    try:
        dangling.symlink_to(root / "does-not-exist.md")
    except (OSError, NotImplementedError) as error:
        pytest.skip(f"Symlink creation unavailable: {error}")
    with pytest.raises(project_evidence.AuditError, match="Refusing to overwrite"):
        project_evidence.write_new_output(root, "visible.md", "replacement")
    assert dangling.is_symlink()
    assert not (root / "does-not-exist.md").exists()


def test_render_validation_failure_preserves_preexisting_output(tmp_path, capsys):
    root, record_path, record, _, _ = audit_files(tmp_path)
    record["searched"]["stop_reason"] = "done"
    record_path.write_text(json.dumps(record), encoding="utf-8")
    target = root / "visible.md"
    original = b"pre-existing output\n"
    target.write_bytes(original)
    result = project_evidence.main([
        "render", str(record_path), "--root", str(root), "--output-root", str(root),
        "--output", "visible.md",
    ])
    assert result == 1
    assert target.read_bytes() == original
    assert '"ok": false' in capsys.readouterr().err


def test_release_context_lock_matches_current_0_3_8_sources():
    import importlib.util
    checker_path = ROOT / "tools/validate_project_evidence_release_context.py"
    checker_spec = importlib.util.spec_from_file_location("project_evidence_release_context", checker_path)
    checker = importlib.util.module_from_spec(checker_spec)
    checker_spec.loader.exec_module(checker)
    result = checker.validate(ROOT)
    assert result["candidate_version"] == "0.3.8"
    assert result["model_runs_verified_by_this_tool"] is False
    assert result["capture_state_at_freeze"]["model_runs"] == "NOT_RUN"
    assert result["semantic_verified"] is False
