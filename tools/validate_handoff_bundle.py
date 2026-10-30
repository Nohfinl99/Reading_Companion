"""Read-only development checker for a state + sidecar handoff bundle.

This is not a runtime helper, restore writer, semantic evaluator or access-control
boundary. See specs/handoff-bundle-v1.md for the deliberately limited contract.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re

ROOT = Path(__file__).resolve().parents[1]
HASH = re.compile(r"[0-9a-f]{64}\Z")
SUPPORT = {"unknown", "none", "hint", "worked_example"}
PRIVATE_KEYS = {"criterion", "criteria", "answer", "answers", "expected_answer",
                "solution", "solutions", "rubric", "gold", "evaluator_sidecar"}


class BundleError(ValueError):
    """Only fixed diagnostic codes are exposed; never echo sidecar contents."""


def require(condition, code):
    if not condition:
        raise BundleError(code)


def fields(value, keys, code="INVALID_RECORD_FIELDS"):
    require(isinstance(value, dict) and set(value) == set(keys.split()), code)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def revision(value):
    return type(value) is int and value >= 1


def digest(value):
    return isinstance(value, str) and HASH.fullmatch(value) is not None


def sha256(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            result.update(chunk)
    return result.hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def load_json(path):
    require(path.stat().st_size <= 4 * 1024 * 1024, "JSON_TOO_LARGE")
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    except (UnicodeError, json.JSONDecodeError, RecursionError):
        raise BundleError("INVALID_JSON") from None


def contained(root, relative):
    require(text(relative), "INVALID_RELATIVE_PATH")
    # Check Windows syntax on Linux too; reject ADS, UNC, traversal and aliases.
    require("\\" not in relative and ":" not in relative and
            not any(ord(c) < 32 for c in relative), "UNSAFE_PATH")
    require(not PurePosixPath(relative).is_absolute() and
            not PureWindowsPath(relative).drive and
            all(part not in {"", ".", ".."} for part in relative.split("/")), "UNSAFE_PATH")
    path = (root / relative).resolve()
    require(path.is_relative_to(root), "PATH_ESCAPES_BUNDLE")
    return path


def checkpoint_module():
    path = ROOT / "skills/sid-reading-companion/scripts/checkpoint.py"
    spec = importlib.util.spec_from_file_location("sid_bundle_checkpoint", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def question_map(state):
    """Normalize pending/paused placement, keeping exact prompt and support."""
    session = state.get("reading_session") or {}
    result = {}
    pending = state.get("pending_question")
    rows = [(row.get("question"), row.get("support"))
            for row in session.get("paused_questions", [])]
    if pending is not None:
        rows.append((pending, (session.get("pending_context") or {}).get("support", "unknown")))
    for question, support in rows:
        require(isinstance(question, dict) and text(question.get("id")) and
                text(question.get("prompt")) and support in SUPPORT, "INVALID_QUESTION_STATE")
        require(question["id"] not in result, "DUPLICATE_QUESTION_ID")
        result[question["id"]] = {
            "prompt_sha256": hashlib.sha256(question["prompt"].encode("utf-8")).hexdigest(),
            "support": support}
    return result


def private_json_key(value):
    if isinstance(value, dict):
        return any(str(k).lower() in PRIVATE_KEYS or private_json_key(v) for k, v in value.items())
    if isinstance(value, list):
        return any(private_json_key(v) for v in value)
    return False


def safe_rebind(previous, state, cp):
    """A candidate only: the caller must preserve originals and perform review."""
    try:
        before = {k: v for k, v in previous.items() if k not in {"revision", "reading_session", "pending_question"}}
        after = {k: v for k, v in state.items() if k not in {"revision", "reading_session", "pending_question"}}
        # Compare source pointers before checkpoint validation can open them.
        if before != after or question_map(previous) != question_map(state):
            return False
        cp.validate_transition(previous, state)
        old_session, new_session = previous.get("reading_session"), state.get("reading_session")
        if old_session is not None:
            if new_session is None:
                return False
            for key in ("chapter_index", "connections"):
                if old_session[key] != new_session[key]:
                    return False
        return True
    except (ValueError, KeyError, TypeError, AttributeError, OSError):
        return False


def validate_bundle(manifest_path, *, root=None, audience="evaluator", previous_state=None):
    """Return stable codes; never mutate a bundle or print criterion/answers."""
    report = {"ok": False, "status": "INVALID", "errors": [], "gaps": [],
              "rebind_candidates": [], "rebind_status": "NOT_REQUESTED", "checkpoint_validated": False,
              "semantic_verified": False, "host_verified": False,
              "evaluator_content_semantically_checked": False,
              "learner_prose_leakage_verified": False, "writes_performed": False}
    try:
        require(audience in {"learner", "evaluator"}, "INVALID_AUDIENCE")
        manifest_path = Path(manifest_path).absolute()
        root = Path(root).resolve() if root is not None else manifest_path.parent.resolve()
        require(manifest_path.resolve().is_relative_to(root), "MANIFEST_ESCAPES_BUNDLE")
        manifest = load_json(manifest_path)
        fields(manifest, "bundle_version state sources artifacts", "INVALID_MANIFEST_FIELDS")
        require(type(manifest["bundle_version"]) is int and manifest["bundle_version"] == 1,
                "UNSUPPORTED_BUNDLE_VERSION")
        entry = manifest["state"]
        fields(entry, "path sha256 revision")
        require(digest(entry["sha256"]) and revision(entry["revision"]), "INVALID_STATE_REFERENCE")
        state_path = contained(root, entry["path"])
        require(state_path.is_file(), "STATE_MISSING")
        require(sha256(state_path) == entry["sha256"], "STATE_HASH_MISMATCH")
        state = load_json(state_path)
        require(isinstance(state, dict) and state.get("revision") == entry["revision"], "STATE_REVISION_MISMATCH")
        require(isinstance(state.get("sources"), list) and isinstance(state.get("units"), list), "INVALID_STATE_INDEX")
        require(isinstance(manifest["sources"], list) and isinstance(manifest["artifacts"], list), "INVALID_MANIFEST_LIST")
        sources, used_paths = {}, {state_path, manifest_path.resolve()}
        for item in manifest["sources"]:
            fields(item, "source_id path sha256 version availability")
            require(text(item["source_id"]) and text(item["version"]) and digest(item["sha256"]), "INVALID_SOURCE_REFERENCE")
            require(item["source_id"] not in sources, "DUPLICATE_SOURCE_ID")
            require(item["availability"] in {"available", "missing"}, "INVALID_SOURCE_AVAILABILITY")
            path = contained(root, item["path"])
            require(path not in used_paths, "DUPLICATE_BUNDLE_PATH")
            used_paths.add(path)
            if item["availability"] == "available":
                require(path.is_file(), "SOURCE_DECLARED_AVAILABLE_BUT_MISSING")
                require(sha256(path) == item["sha256"], "STALE_SOURCE")
            else:
                require(not path.exists(), "SOURCE_DECLARED_MISSING_BUT_PRESENT")
                report["gaps"].append({"code": "SOURCE_MISSING", "source_index": len(sources)})
            sources[item["source_id"]] = (item, path)
        state_sources = {}
        for item in state["sources"]:
            require(isinstance(item, dict) and text(item.get("id")) and item["id"] not in state_sources,
                    "INVALID_STATE_SOURCE_INDEX")
            state_sources[item["id"]] = item
        require(set(sources) == set(state_sources) and bool(sources), "SOURCE_INDEX_MISMATCH")
        for sid, (item, path) in sources.items():
            existing = state_sources[sid]
            require(existing.get("sha256") == item["sha256"], "STATE_SOURCE_HASH_MISMATCH")
            require(text(existing.get("path")) and Path(existing["path"]).is_absolute() and
                    Path(existing["path"]).resolve() == path, "STATE_SOURCE_PATH_MISMATCH")
        units = {}
        for item in state["units"]:
            require(isinstance(item, dict) and text(item.get("id")) and revision(item.get("revision")) and
                    item["id"] not in units, "INVALID_STATE_UNIT_INDEX")
            units[item["id"]] = item["revision"]
        questions = question_map(state)
        cp = checkpoint_module()
        available = all(item["availability"] == "available" for item, _ in sources.values())
        if available:
            try:
                cp.validate(state)
            except (ValueError, KeyError, TypeError):
                raise BundleError("CHECKPOINT_INVALID") from None
            report["checkpoint_validated"] = True
        else:
            report["gaps"].append({"code": "CHECKPOINT_FULL_VALIDATION_NOT_RUN"})
        previous, rebind_ok = None, False
        if previous_state is not None:
            report["rebind_status"] = "NOT_CERTIFIED"
            prior_path = contained(root, str(previous_state))
            if prior_path.is_file() and available:
                previous = load_json(prior_path)
                rebind_ok = safe_rebind(previous, state, cp)
                report["previous_state_sha256"] = sha256(prior_path)
            else:
                report["gaps"].append({"code": "PREVIOUS_STATE_UNAVAILABLE"})
        ids = set()
        for index, item in enumerate(manifest["artifacts"]):
            fields(item, "artifact_id path sha256 contract_version artifact_revision state_revision audience depends_on")
            require(text(item["artifact_id"]) and item["artifact_id"] not in ids, "INVALID_OR_DUPLICATE_ARTIFACT_ID")
            ids.add(item["artifact_id"])
            require(digest(item["sha256"]) and item["contract_version"] == "PS1" and
                    revision(item["artifact_revision"]) and revision(item["state_revision"]), "INVALID_ARTIFACT_REFERENCE")
            require(item["audience"] in {"learner", "evaluator"}, "INVALID_ARTIFACT_AUDIENCE")
            require(audience != "learner" or item["audience"] == "learner", "EVALUATOR_ARTIFACT_IN_LEARNER_MANIFEST")
            path = contained(root, item["path"])
            require(path not in used_paths, "DUPLICATE_BUNDLE_PATH")
            used_paths.add(path)
            require(path.is_file(), "ARTIFACT_MISSING")
            require(sha256(path) == item["sha256"], "ARTIFACT_HASH_MISMATCH")
            if item["audience"] == "learner" and path.suffix.lower() == ".json":
                require(not private_json_key(load_json(path)), "EVALUATOR_KEY_IN_LEARNER_ARTIFACT")
            deps = item["depends_on"]
            fields(deps, "sources units question")
            require(isinstance(deps["sources"], list) and isinstance(deps["units"], list), "INVALID_DEPENDENCY_LIST")
            source_ids, unit_ids = set(), set()
            for dep in deps["sources"]:
                fields(dep, "source_id sha256 version")
                require(text(dep["source_id"]) and dep["source_id"] not in source_ids, "INVALID_SOURCE_DEPENDENCY")
                source_ids.add(dep["source_id"])
                require(dep["source_id"] in sources, "UNKNOWN_SOURCE_DEPENDENCY")
                source = sources[dep["source_id"]][0]
                require(dep["sha256"] == source["sha256"] and dep["version"] == source["version"], "STALE_SOURCE_DEPENDENCY")
                if source["availability"] == "missing":
                    report["gaps"].append({"code": "DEPENDENT_SOURCE_MISSING", "artifact_index": index})
            for dep in deps["units"]:
                fields(dep, "unit_id revision")
                require(text(dep["unit_id"]) and dep["unit_id"] not in unit_ids, "INVALID_UNIT_DEPENDENCY")
                unit_ids.add(dep["unit_id"])
                require(dep["unit_id"] in units and type(dep["revision"]) is int and
                        dep["revision"] == units[dep["unit_id"]], "STALE_UNIT_DEPENDENCY")
            if deps["question"] is not None:
                dep = deps["question"]
                fields(dep, "question_id prompt_sha256 support")
                require(text(dep["question_id"]) and digest(dep["prompt_sha256"]) and dep["support"] in SUPPORT,
                        "INVALID_QUESTION_DEPENDENCY")
                require(dep["question_id"] in questions and questions[dep["question_id"]] ==
                        {k: dep[k] for k in ("prompt_sha256", "support")}, "QUESTION_IDENTITY_OR_SUPPORT_MISMATCH")
            require(item["state_revision"] <= state["revision"], "ARTIFACT_FUTURE_STATE_REVISION")
            if item["state_revision"] != state["revision"]:
                report["gaps"].append({"code": "ARTIFACT_STATE_REVISION_STALE", "artifact_index": index})
                if rebind_ok and previous.get("revision") == item["state_revision"]:
                    report["rebind_candidates"].append(index)
                    report["rebind_status"] = "CANDIDATE_ONLY"
        report["status"] = "PARTIAL" if report["gaps"] else "VALID"
        report["ok"] = report["status"] == "VALID"
    except BundleError as exc:
        report["errors"].append({"code": str(exc)})
    except (OSError, ValueError, KeyError, TypeError, AttributeError, RuntimeError, RecursionError, OverflowError):
        report["errors"].append({"code": "BUNDLE_UNREADABLE_OR_MALFORMED"})
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--audience", choices=("learner", "evaluator"), default="evaluator")
    parser.add_argument("--previous-state", help="Bundle-relative previous snapshot; reports candidates only")
    args = parser.parse_args(argv)
    result = validate_bundle(args.manifest, root=args.root, audience=args.audience, previous_state=args.previous_state)
    print(json.dumps(result, indent=2))
    return {"VALID": 0, "PARTIAL": 2, "INVALID": 1}[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
