"""Check that the 0.3.8 project-evidence runner context matches its frozen candidate."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.8"
PROFILE_VERSION = "project-evidence-audit-0.3.8"
SUITE = Path("evaluation/project-evidence/0.3.8")
LOCK = SUITE / "release-context.json"
CONTEXT = [
    "plugin.json",
    ".codex-plugin/plugin.json",
    "skills/sid-reading-companion/SKILL.md",
    "skills/sid-reading-companion/references/master-instruction.md",
    "skills/sid-reading-companion/references/knowledge-compiler.md",
    "skills/sid-reading-companion/references/stack-contracts.md",
    "skills/sid-reading-companion/references/citation-evidence.md",
    "skills/sid-reading-companion/references/reading-protocols.md",
    "skills/sid-reading-companion/references/project-evidence.md",
    "skills/sid-reading-companion/references/project-evidence-profile.json",
    "skills/sid-reading-companion/references/project-evidence-record.schema.json",
    "skills/sid-reading-companion/scripts/project_evidence.py",
    "docs/project-evidence.vi.md",
    "docs/project-evidence.en.md",
]
SPEC_DIR = SUITE / "case-specs"
RUBRIC = SUITE / "rubric.json"
CHECKER = Path("tools/validate_project_evidence_release_context.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def freeze(root=ROOT):
    """Create the initial immutable current-candidate hash lock; never overwrite it."""
    root = Path(root).resolve()
    require(not (root / LOCK).exists(), "Release-context lock already exists; do not silently repin it")
    manifest = load_json(root / "plugin.json")
    overlay = load_json(root / ".codex-plugin/plugin.json")
    require(manifest.get("version") == overlay.get("version") == VERSION,
            "Both plugin manifests must declare current candidate version 0.3.8")
    require(overlay["interface"]["defaultPrompt"] ==
            manifest["extensions"]["com.openai"]["interface"]["defaultPrompt"],
            "Plugin overlay defaultPrompt differs from the source manifest")
    require(set(CONTEXT).issubset(set(load_json(root / "packaging/runtime-files.json")["runtime_files"])),
            "Candidate runtime context is not fully packaged")
    eval_root = root / SUITE
    evaluation_files = {}
    for path in sorted(eval_root.rglob("*")):
        if (path.is_file() and path.name != LOCK.name and "__pycache__" not in path.parts
                and path.suffix.lower() in {".json", ".md", ".txt"}):
            evaluation_files[path.relative_to(root).as_posix()] = sha256(path)
    lock = {
        "lock_schema_version": 2,
        "lock_version": "project-evidence-release-context-0.3.8",
        "candidate_version": VERSION,
        "profile_version": PROFILE_VERSION,
        "checker_sha256": sha256(root / CHECKER),
        "files": {relative: sha256(root / relative) for relative in CONTEXT},
        "evaluation_files": evaluation_files,
        "case_count": 5,
        "capture_state_at_freeze": {
            "model_runs": "NOT_RUN",
            "semantic_review": "NOT_RUN",
            "host_activation": "NOT_RUN",
        },
        "purpose": "Fresh 0.3.8 candidate context; separate from immutable 0.3.7 historical capture.",
    }
    target = root / LOCK
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(lock, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "lock_path": LOCK.as_posix(), "runtime_context_files": len(lock["files"]),
            "evaluation_files": len(evaluation_files), "capture_state_at_freeze": lock["capture_state_at_freeze"],
            "model_runs_verified_by_this_tool": False}


def validate(root=ROOT, *, bundles=()):
    root = Path(root).resolve()
    manifest = load_json(root / "plugin.json")
    overlay = load_json(root / ".codex-plugin/plugin.json")
    require(manifest.get("version") == overlay.get("version") == VERSION,
            "Both plugin manifests must declare current candidate version 0.3.8")
    defaults = manifest["extensions"]["com.openai"]["interface"]["defaultPrompt"]
    require(overlay["interface"]["defaultPrompt"] == defaults,
            "Plugin overlay defaultPrompt differs from the source manifest")

    runtime_list = set(load_json(root / "packaging/runtime-files.json")["runtime_files"])
    require(set(CONTEXT).issubset(runtime_list), "Candidate runtime context is not fully packaged")
    lock = load_json(root / LOCK)
    require(lock.get("lock_schema_version") == 2 and
            lock.get("candidate_version") == VERSION and lock.get("profile_version") == PROFILE_VERSION,
            "Release-context lock version mismatch")
    require(lock.get("capture_state_at_freeze") == {
        "model_runs": "NOT_RUN", "semantic_review": "NOT_RUN", "host_activation": "NOT_RUN"
    }, "Invalid candidate freeze-time status record")
    require(lock.get("checker_sha256") == sha256(root / CHECKER),
            "Stale candidate release-context checker capture")
    expected_files = lock.get("files")
    require(isinstance(expected_files, dict) and set(expected_files) == set(CONTEXT),
            "Release-context lock must pin every mandatory runtime context file")
    current = {}
    for relative in CONTEXT:
        path = root / relative
        require(path.is_file() and not path.is_symlink(), f"Missing/symlink current candidate file: {relative}")
        digest = sha256(path)
        require(expected_files[relative] == digest, f"Stale current candidate capture: {relative}")
        current[relative] = digest

    case_files = lock.get("evaluation_files")
    require(isinstance(case_files, dict) and case_files, "Release-context lock has no frozen evaluation files")
    eval_root = root / SUITE
    current_evaluation_files = {
        path.relative_to(root).as_posix()
        for path in eval_root.rglob("*")
        if path.is_file() and path.name != LOCK.name and "__pycache__" not in path.parts
        and path.suffix.lower() in {".json", ".md", ".txt"}
    }
    require(current_evaluation_files == set(case_files),
            "Frozen evaluation file set changed; added or removed case/rubric files require a new candidate")
    for relative, expected in case_files.items():
        path = root / relative
        require(path.is_file() and not path.is_symlink(), f"Missing/symlink evaluation file: {relative}")
        require(sha256(path) == expected, f"Stale frozen case/rubric file: {relative}")

    specs = sorted((root / SPEC_DIR).glob("*.json"))
    require(len(specs) == lock.get("case_count") == 5, "Expected exactly five frozen one-case specifications")
    case_ids = set()
    case_inputs = {}
    for path in specs:
        spec = load_json(path)
        require(spec.get("profile_version") == PROFILE_VERSION, f"Wrong profile version in {path.name}")
        case_id = spec.get("case_id")
        require(isinstance(case_id, str) and case_id not in case_ids, "Duplicate/invalid case ID")
        case_ids.add(case_id)
        input_path = spec.get("input")
        require(isinstance(input_path, str) and input_path.startswith(f"{SUITE.as_posix()}/cases/{case_id}/"),
                f"Case input escapes its own case directory: {case_id}")
        case_inputs[case_id] = input_path.removeprefix(SUITE.as_posix() + "/")
        source_entries = spec.get("sources")
        require(isinstance(source_entries, list) and source_entries, f"Case has no source allowlist: {case_id}")
        for item in source_entries:
            source = item.get("path") if isinstance(item, dict) else None
            require(isinstance(source, str) and source.startswith(f"{SUITE.as_posix()}/cases/{case_id}/"),
                    f"Case source escapes its own case directory: {case_id}")
        require(spec.get("runtime_context") == CONTEXT,
                f"Runtime context is incomplete or differs from frozen candidate: {case_id}")
        serialized = json.dumps(spec, ensure_ascii=False)
        require("rubric.json" not in serialized and "case-specs/" not in serialized,
                f"Runner case spec references evaluator or another case: {case_id}")

    rubric = load_json(root / RUBRIC)
    rubric_cases = rubric.get("cases", [])
    require(isinstance(rubric_cases, list) and all(isinstance(case, dict) for case in rubric_cases),
            "Rubric cases must be a list of objects")
    rubric_ids = {case.get("id") for case in rubric_cases}
    require(rubric.get("frozen_before_model_outputs") is True and rubric_ids == case_ids,
            "Frozen rubric cases do not match the runner case set")
    for case in rubric_cases:
        require(case.get("input") == case_inputs[case["id"]],
                f"Rubric input path does not match its case spec/directory: {case['id']}")
    require(rubric.get("status") == "NOT_RUN", "Model output status must remain NOT_RUN until real runs are captured")

    bundle_results = []
    if bundles:
        helper_path = root / "skills/sid-reading-companion/scripts/project_evidence.py"
        spec = importlib.util.spec_from_file_location("project_evidence_runtime", helper_path)
        helper = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = helper
        spec.loader.exec_module(helper)
        for bundle in bundles:
            bundle_results.append(helper.check_bundle(Path(bundle), source_root=root))
    return {
        "ok": True,
        "candidate_version": VERSION,
        "runtime_context_files": len(current),
        "evaluation_files": len(case_files),
        "case_count": len(case_ids),
        "capture_state_at_freeze": lock["capture_state_at_freeze"],
        "model_runs_verified_by_this_tool": False,
        "semantic_review_verified_by_this_tool": False,
        "bundle_checks": bundle_results,
        "evidence_layer": "mechanical_helper",
        "semantic_verified": False,
        "host_activation_verified_by_this_tool": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--bundle", action="append", type=Path, default=[])
    parser.add_argument("--freeze", action="store_true", help="Create the initial lock if no lock exists; never repins")
    args = parser.parse_args(argv)
    try:
        require(not (args.freeze and args.bundle), "--freeze cannot be combined with --bundle")
        result = freeze(args.root) if args.freeze else validate(args.root, bundles=args.bundle)
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as error:
        print(json.dumps({"ok": False, "error": str(error), "semantic_verified": False}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
