"""Synthetic bundle continuity/containment tests, never learner evidence."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

PATH = Path(__file__).resolve().parents[1] / "tools/validate_handoff_bundle.py"
SPEC = importlib.util.spec_from_file_location("sid_handoff_bundle_test", PATH)
hb = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(hb)
PRIVATE = "SYNTHETIC_PRIVATE_CRITERION_Z"


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


@pytest.fixture()
def bundle(tmp_path, fx, cp):
    state = fx.state_pending(support="hint")
    state["units"] = [fx.unit_k01()]
    cp.validate(state)
    state_path = tmp_path / "state.json"
    write_json(state_path, state)
    learner = tmp_path / "handoff.md"
    cp.export(state_path, learner)
    evaluator = tmp_path / "criterion.json"
    write_json(evaluator, {"criterion": [{"claim": PRIVATE, "source_locator": "S01:2-3", "critical_condition": "Z"}]})
    source = {"source_id": "S01", "path": "book.txt", "sha256": state["sources"][0]["sha256"],
              "version": "synthetic edition 1", "availability": "available"}
    deps = {"sources": [{k: source[k] for k in ("source_id", "sha256", "version")}],
            "units": [{"unit_id": "K01", "revision": 1}],
            "question": {"question_id": "Q01", "prompt_sha256": hashlib.sha256(state["pending_question"]["prompt"].encode()).hexdigest(), "support": "hint"}}
    manifest = {"bundle_version": 1,
                "state": {"path": "state.json", "sha256": hb.sha256(state_path), "revision": state["revision"]},
                "sources": [source], "artifacts": []}
    for aid, path, audience in (("learner", learner, "learner"), ("criterion", evaluator, "evaluator")):
        manifest["artifacts"].append({"artifact_id": aid, "path": path.name, "sha256": hb.sha256(path),
            "contract_version": "PS1", "artifact_revision": 1, "state_revision": state["revision"],
            "audience": audience, "depends_on": deepcopy(deps)})
    manifest_path = tmp_path / "manifest.json"
    value = SimpleNamespace(root=tmp_path, state=state, state_path=state_path, manifest=manifest,
                            path=manifest_path, learner=learner, evaluator=evaluator)
    value.save_manifest = lambda: write_json(manifest_path, manifest)

    def save_state():
        write_json(state_path, value.state)
        manifest["state"].update(sha256=hb.sha256(state_path), revision=value.state["revision"])
        value.save_manifest()
    value.save_state = save_state
    value.save_manifest()
    return value


def check(bundle, **kwargs):
    bundle.save_manifest()
    return hb.validate_bundle(bundle.path, **kwargs)


def code(report):
    return report["errors"][0]["code"] if report["errors"] else None


def test_export_validate_pause_restore_resume_roundtrip(bundle, cp, rs):
    before = {p.name: p.read_bytes() for p in bundle.root.iterdir() if p.is_file()}
    result = hb.validate_bundle(bundle.path)
    assert result["status"] == "VALID" and result["checkpoint_validated"]
    assert not result["semantic_verified"] and not result["host_verified"]
    assert before == {p.name: p.read_bytes() for p in bundle.root.iterdir() if p.is_file()}
    assert PRIVATE not in bundle.learner.read_text(encoding="utf-8")
    pending = deepcopy(bundle.state["pending_question"])
    paused = rs.operate(bundle.state, "pause", note="Synthetic pause")
    candidate = bundle.root / "candidate.json"
    write_json(candidate, paused)
    cp.save(bundle.state_path, candidate)
    restored = cp.read_json(bundle.state_path)
    resumed = rs.operate(restored, "resume", value="Q01", note="Synthetic resume")
    write_json(candidate, resumed)
    cp.save(bundle.state_path, candidate)
    assert resumed["pending_question"] == pending
    assert resumed["reading_session"]["pending_context"]["support"] == "hint"
    assert resumed["assessments"] == []
    bundle.state = resumed
    bundle.save_state()
    for artifact in bundle.manifest["artifacts"]:
        artifact["state_revision"] = resumed["revision"]
    assert check(bundle)["status"] == "VALID"


def test_changed_source_is_stale_and_never_rewritten(bundle):
    book = bundle.root / "book.txt"
    book.write_text("changed synthetic source", encoding="utf-8")
    assert code(check(bundle)) == "STALE_SOURCE"
    assert book.read_text(encoding="utf-8") == "changed synthetic source"


@pytest.mark.parametrize("declared_missing", [True, False])
def test_missing_source_is_gap_only_when_explicit(bundle, declared_missing):
    (bundle.root / "book.txt").unlink()
    if declared_missing:
        bundle.manifest["sources"][0]["availability"] = "missing"
    result = check(bundle)
    if declared_missing:
        assert result["status"] == "PARTIAL" and not result["checkpoint_validated"]
        assert {g["code"] for g in result["gaps"]} >= {"SOURCE_MISSING", "DEPENDENT_SOURCE_MISSING"}
    else:
        assert code(result) == "SOURCE_DECLARED_AVAILABLE_BUT_MISSING"


def test_cannot_hide_changed_source_as_missing(bundle):
    bundle.manifest["sources"][0]["availability"] = "missing"
    assert code(check(bundle)) == "SOURCE_DECLARED_MISSING_BUT_PRESENT"


def test_missing_sidecar_is_invalid(bundle):
    bundle.evaluator.unlink()
    assert code(check(bundle)) == "ARTIFACT_MISSING"


def test_stale_unit_revision_invalidates_dependent_sidecars(bundle):
    bundle.state["units"][0]["revision"] += 1
    bundle.state["revision"] += 1
    bundle.save_state()
    assert code(check(bundle)) == "STALE_UNIT_DEPENDENCY"


@pytest.mark.parametrize("field,value", [("sha256", "0" * 64), ("version", "different edition")])
def test_source_dependency_identity_includes_hash_and_version(bundle, field, value):
    bundle.manifest["artifacts"][0]["depends_on"]["sources"][0][field] = value
    assert code(check(bundle)) == "STALE_SOURCE_DEPENDENCY"


@pytest.mark.parametrize("mutation", ["id", "prompt", "support"])
def test_q_identity_and_support_cannot_be_substituted(bundle, mutation):
    if mutation == "support":
        bundle.state["reading_session"]["pending_context"]["support"] = "none"
    else:
        bundle.state["pending_question"][mutation] = "Q02" if mutation == "id" else "Different synthetic question"
    bundle.save_state()
    assert code(check(bundle)) == "QUESTION_IDENTITY_OR_SUPPORT_MISMATCH"


def test_private_artifact_rejected_from_learner_manifest(bundle):
    assert code(check(bundle, audience="learner")) == "EVALUATOR_ARTIFACT_IN_LEARNER_MANIFEST"
    bundle.manifest["artifacts"] = bundle.manifest["artifacts"][:1]
    assert check(bundle, audience="learner")["status"] == "VALID"


def test_evaluator_json_key_cannot_hide_in_learner_artifact_or_diagnostics(bundle, capsys):
    path = bundle.root / "bad-learner.json"
    write_json(path, {"nested": [{"criterion": PRIVATE}]})
    item = bundle.manifest["artifacts"][0]
    item.update(path=path.name, sha256=hb.sha256(path))
    bundle.save_manifest()
    assert hb.main([str(bundle.path)]) == 1
    diagnostic = capsys.readouterr().out
    assert "EVALUATOR_KEY_IN_LEARNER_ARTIFACT" in diagnostic
    assert PRIVATE not in diagnostic


def test_manifest_cannot_inline_evaluator_payload(bundle):
    bundle.manifest["criterion"] = PRIVATE
    result = check(bundle)
    assert code(result) == "INVALID_MANIFEST_FIELDS"
    assert PRIVATE not in json.dumps(result)


@pytest.mark.parametrize("unsafe", ["../outside.json", "/tmp/outside.json", "C:/outside.json", "a\\..\\outside.json", "a/../x", "a//x", "x:stream"])
def test_cross_platform_path_traversal_is_rejected(bundle, unsafe):
    bundle.manifest["artifacts"][0]["path"] = unsafe
    assert code(check(bundle)) == "UNSAFE_PATH"


def test_symlink_cannot_escape_bundle(bundle, tmp_path):
    outside = tmp_path.parent / (tmp_path.name + "-outside.json")
    outside.write_text("{}", encoding="utf-8")
    link = bundle.root / "linked.json"
    try:
        link.symlink_to(outside)
    except OSError as exc:
        if getattr(exc, "winerror", None) == 1314:
            pytest.skip("Windows account lacks symlink privilege")
        raise
    bundle.manifest["artifacts"][0]["path"] = link.name
    assert code(check(bundle)) == "PATH_ESCAPES_BUNDLE"


def test_duplicate_resolved_paths_cannot_change_audience(bundle):
    bundle.manifest["artifacts"][1].update(path=bundle.learner.name, sha256=hb.sha256(bundle.learner))
    assert code(check(bundle)) == "DUPLICATE_BUNDLE_PATH"


def test_navigation_only_old_revision_is_rebind_candidate_never_auto_mutated(bundle, rs):
    previous_path = bundle.root / "previous.json"
    write_json(previous_path, bundle.state)
    bundle.state = rs.operate(bundle.state, "next", note="Synthetic navigation")
    bundle.save_state()
    before = {p.name: p.read_bytes() for p in bundle.root.iterdir() if p.is_file()}
    result = hb.validate_bundle(bundle.path, previous_state="previous.json")
    assert result["status"] == "PARTIAL" and result["rebind_candidates"] == [0, 1]
    assert result["rebind_status"] == "CANDIDATE_ONLY" and not result["writes_performed"]
    assert before == {p.name: p.read_bytes() for p in bundle.root.iterdir() if p.is_file()}


def test_old_revision_without_previous_snapshot_never_certifies_rebind(bundle, rs):
    bundle.state = rs.operate(bundle.state, "style", value="chill")
    bundle.save_state()
    result = check(bundle)
    assert result["status"] == "PARTIAL" and result["rebind_candidates"] == []


def test_changed_content_is_not_rebind_candidate_even_when_dependency_labels_updated(bundle):
    write_json(bundle.root / "previous.json", bundle.state)
    bundle.state["units"][0].update(revision=2, title="Changed synthetic title")
    bundle.state["revision"] += 1
    bundle.save_state()
    for item in bundle.manifest["artifacts"]:
        item["depends_on"]["units"][0]["revision"] = 2
    result = check(bundle, previous_state="previous.json")
    assert result["status"] == "PARTIAL" and result["rebind_candidates"] == []
    assert result["rebind_status"] == "NOT_CERTIFIED"


def test_missing_previous_snapshot_remains_unverified(bundle):
    result = check(bundle, previous_state="not-there.json")
    assert result["status"] == "PARTIAL" and result["rebind_candidates"] == []


def test_previous_snapshot_cannot_make_checkpoint_open_external_sources(bundle, rs, cp, monkeypatch):
    previous = deepcopy(bundle.state)
    previous["sources"][0]["path"] = str(bundle.root.parent / "outside-book.txt")
    write_json(bundle.root / "previous.json", previous)
    bundle.state = rs.operate(bundle.state, "style", value="chill")
    bundle.save_state()
    calls = []
    def transition(old, new):
        calls.append(True)
        cp.validate_transition(old, new)
    monkeypatch.setattr(hb, "checkpoint_module", lambda: SimpleNamespace(validate=cp.validate, validate_transition=transition))
    result = check(bundle, previous_state="previous.json")
    assert result["status"] == "PARTIAL" and not result["rebind_candidates"]
    assert calls == []


def test_partial_cli_uses_distinct_exit_without_printing_private_content(bundle, capsys):
    (bundle.root / "book.txt").unlink()
    bundle.manifest["sources"][0]["availability"] = "missing"
    bundle.save_manifest()
    assert hb.main([str(bundle.path)]) == 2
    diagnostic = capsys.readouterr().out
    assert '"status": "PARTIAL"' in diagnostic and PRIVATE not in diagnostic


def test_future_artifact_state_revision_cannot_be_rebound(bundle):
    bundle.manifest["artifacts"][0]["state_revision"] += 1
    assert code(check(bundle)) == "ARTIFACT_FUTURE_STATE_REVISION"


@pytest.mark.parametrize("target,expected", [("state", "STATE_HASH_MISMATCH"), ("artifact", "ARTIFACT_HASH_MISMATCH")])
def test_tampered_bytes_fail_hash_identity(bundle, target, expected):
    path = bundle.state_path if target == "state" else bundle.evaluator
    path.write_bytes(path.read_bytes() + b"\n")
    assert code(check(bundle)) == expected


def test_checkpoint_cannot_read_source_outside_manifest_root(bundle):
    bundle.state["sources"][0]["path"] = str(bundle.root.parent / "outside-book.txt")
    bundle.save_state()
    assert code(check(bundle)) == "STATE_SOURCE_PATH_MISMATCH"


def test_malformed_session_returns_code_without_echoing_private_data(bundle):
    bundle.state["reading_session"] = PRIVATE
    bundle.save_state()
    result = check(bundle)
    assert result["status"] == "INVALID"
    assert PRIVATE not in json.dumps(result)


def test_duplicate_json_keys_are_rejected(bundle):
    bundle.path.write_text('{"bundle_version":1,"bundle_version":1}', encoding="utf-8")
    assert code(hb.validate_bundle(bundle.path)) == "DUPLICATE_JSON_KEY"
