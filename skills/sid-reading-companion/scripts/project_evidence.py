"""Validate and render project evidence audit records; semantic truth stays with R14 review."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import shutil
import sys
import tempfile

SCRIPT = Path(__file__).resolve()
PROFILE_PATH = SCRIPT.parents[1] / "references" / "project-evidence-profile.json"
PROFILE_VERSION = "project-evidence-audit-0.3.8"
MAX_JSON_BYTES = 4 * 1024 * 1024
OUTPUT_FILES = {"answer.md", "record.json", "visible.md", "review.json"}
PLACEHOLDER_VALUES = {
    "", "done", "complete", "completed", "n/a", "na", "none", "no reason",
    "unknown", "tbd", "todo", "pending", "not checked", "checked",
    "đã xong", "xong", "đã kiểm xong", "không rõ", "chưa rõ", "n/a.",
}
STATUSES = {"PASS", "FAIL", "PARTIAL", "NOT_RUN"}


class AuditError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def require_object_fields(value, label: str, required, optional=()):
    require(isinstance(value, dict), f"{label} must be an object")
    missing = set(required) - set(value)
    extra = set(value) - set(required) - set(optional)
    require(not missing, f"Missing {label} fields: " + ", ".join(sorted(missing)))
    require(not extra, f"Unexpected {label} fields: " + ", ".join(sorted(extra)))


def _pairs_no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path):
    path = Path(path)
    require(path.stat().st_size <= MAX_JSON_BYTES, f"JSON file too large: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs_no_duplicates)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise AuditError(f"Invalid UTF-8 JSON: {path}") from error


def load_profile():
    profile = load_json(PROFILE_PATH)
    require(profile.get("profile_version") == PROFILE_VERSION, "Runtime audit profile version mismatch")
    require(profile.get("semantic_verified_by_helper") is False,
            "Audit profile must not claim semantic verification")
    schema_path = PROFILE_PATH.parent / profile.get("record_schema", "")
    schema = load_json(schema_path)
    require(schema.get("$id") == "urn:sid-reading-companion:project-evidence-audit:0.3.8",
            "Runtime audit JSON Schema identity mismatch")
    require(schema.get("required") == profile.get("required_record_fields"),
            "Profile and JSON Schema required fields differ")
    return profile


def raw_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_text(value, label: str) -> str:
    require(isinstance(value, str), f"{label} must be text")
    result = " ".join(value.split())
    folded = result.casefold().strip(" .:;!—–-_")
    require(bool(result) and folded not in PLACEHOLDER_VALUES, f"Missing or placeholder {label}")
    return result


def safe_relative(value, label: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"Missing {label}")
    value = value.replace("\\", "/")
    posix = PurePosixPath(value)
    require(not posix.is_absolute() and not PureWindowsPath(value).drive and
            all(part not in {"", ".", ".."} for part in posix.parts),
            f"Unsafe relative path in {label}")
    require(value == posix.as_posix(), f"Noncanonical path in {label}")
    return value


def contained_file(root: Path, relative: str) -> Path:
    relative = safe_relative(relative, "evidence path")
    root = Path(root).resolve()
    current = root
    for part in PurePosixPath(relative).parts:
        current = current / part
        require(not current.is_symlink(), f"Symlink not allowed in evidence path: {relative}")
    resolved = current.resolve()
    require(resolved.is_relative_to(root) and resolved.is_file(), f"Evidence file missing or outside root: {relative}")
    return resolved


def check_span(root: Path, span, label: str, expected_path: str | None = None,
               expected_hash: str | None = None, allowed_paths: set[str] | None = None):
    require_object_fields(span, f"{label} span", {"path", "sha256", "line_start", "line_end", "excerpt"})
    path_text = safe_relative(span.get("path"), f"{label} path")
    if allowed_paths is not None:
        require(path_text in allowed_paths, f"{label} points outside this case's declared evidence allowlist")
    if expected_path is not None:
        require(path_text == expected_path, f"{label} does not point to the bound artifact")
    path = contained_file(root, path_text)
    actual_hash = raw_sha256(path)
    wanted_hash = expected_hash or span.get("sha256")
    require(isinstance(wanted_hash, str) and actual_hash == wanted_hash,
            f"Stale {label} fingerprint")
    require(span.get("sha256") == actual_hash, f"{label} span fingerprint mismatch")
    lines = path.read_text(encoding="utf-8").splitlines()
    start, end = span.get("line_start"), span.get("line_end")
    require(type(start) is int and type(end) is int and 1 <= start <= end <= len(lines),
            f"Invalid {label} line range")
    excerpt = span.get("excerpt")
    require(isinstance(excerpt, str) and bool(excerpt.strip()) and len(excerpt) <= 16_384,
            f"Missing or oversized {label} excerpt")
    require(excerpt in "\n".join(lines[start - 1:end]), f"{label} excerpt not found at locator")
    return path_text


def validate_version_entry(value, label: str, root: Path, allowed_paths: set[str] | None):
    require_object_fields(value, label, {"status", "value", "evidence"})
    require(value.get("status") in {"known", "unknown"}, f"Invalid {label} status")
    if value["status"] == "known":
        normalized_text(value.get("value"), f"{label} value")
        require(isinstance(value.get("evidence"), list) and value["evidence"],
                f"Known {label} needs direct evidence locators")
        for index, span in enumerate(value["evidence"]):
            check_span(root, span, f"{label} evidence {index}", allowed_paths=allowed_paths)
    else:
        require(value.get("value") is None, f"Unknown {label} must have null value")
        require(value.get("evidence") == [], f"Unknown {label} must not claim a value locator")


def validate_audit_record(record, root: Path, output_root: Path | None = None):
    load_profile()
    required = {"contract_version", "case_id", "artifact", "selection", "searched", "source_context", "handoff"}
    require_object_fields(record, "audit record", required, {"narrative"})
    if "narrative" in record:
        require(isinstance(record["narrative"], str), "Narrative must be text")
    require(record["contract_version"] == PROFILE_VERSION, "Unsupported audit profile version")
    normalized_text(record["case_id"], "case_id")
    bundle_manifest = Path(root) / "bundle-manifest.json"
    allowed_sources = None
    if bundle_manifest.is_file():
        manifest = load_json(bundle_manifest)
        require(manifest.get("case_id") == record["case_id"], "Audit record case_id differs from its bundle")
        allowed_sources = set(manifest.get("allowed_source_paths", [])) | {manifest.get("input_path")}

    artifact = record["artifact"]
    require_object_fields(artifact, "artifact", {"path", "sha256"})
    artifact_path = safe_relative(artifact.get("path"), "artifact path")
    artifact_root = Path(output_root) if output_root is not None else Path(root)
    if allowed_sources is not None:
        require(output_root is not None, "Case-bundle output must be stored outside the immutable input bundle")
        require(artifact_path in OUTPUT_FILES, "Case-bundle artifact must use a declared output filename")
        input_root, artifact_root_resolved = Path(root).resolve(), artifact_root.resolve()
        require(not artifact_root_resolved.is_relative_to(input_root) and
                not input_root.is_relative_to(artifact_root_resolved),
                "Runner output root must be separate from the immutable input bundle")
    artifact_file = contained_file(artifact_root, artifact_path)
    artifact_hash = raw_sha256(artifact_file)
    require(artifact.get("sha256") == artifact_hash, "Artifact fingerprint mismatch")

    selection = record["selection"]
    require_object_fields(selection, "SC01 selection", {
        "selection_id", "purpose", "scope", "basis", "universe_ref", "criterion", "members",
        "exclusions_or_not_evaluated", "completeness", "count", "count_basis"})
    for field in ("selection_id", "purpose", "scope", "criterion", "exclusions_or_not_evaluated"):
        normalized_text(selection.get(field), f"selection.{field}")
    require(selection.get("basis") in {"author_explicit", "ai_selection", "user_selection", "mixed"},
            "Invalid SC01 selection basis")
    require(selection.get("completeness") in {"complete_in_verified_scope", "partial", "unknown"},
            "Invalid SC01 completeness")
    require(selection.get("count_basis") in {"author_stated", "derived_after_selection", "user_limit", "unknown"},
            "Invalid SC01 count_basis")
    require(type(selection.get("count")) is int and selection["count"] >= 0,
            "Invalid selected member count")
    members = selection.get("members")
    require(isinstance(members, list) and len(members) == selection["count"],
            "SC01 count does not equal members length")
    for index, member in enumerate(members):
        require_object_fields(member, f"SC01 member {index}", {"ref", "origin", "source_locators", "inclusion_reason"})
        for field in ("ref", "origin", "inclusion_reason"):
            normalized_text(member.get(field), f"selection.members[{index}].{field}")
        locators = member.get("source_locators")
        require(isinstance(locators, list), f"Invalid SC01 member {index} source_locators")
        if member["origin"] == "source":
            require(bool(locators), f"Source-backed SC01 member {index} needs a source locator")
        elif member["origin"] not in {"ai_proposed", "user_provided"}:
            raise AuditError(f"Invalid SC01 member origin: {member['origin']}")
        for span in locators:
            check_span(root, span, f"selection member {index} source", allowed_paths=allowed_sources)
    universe = selection.get("universe_ref")
    require(universe is None or (isinstance(universe, str) and bool(universe.strip())),
            "Invalid SC01 universe_ref; use null when unknown")
    if selection["completeness"] == "complete_in_verified_scope":
        require(isinstance(universe, str) and universe.strip().casefold() != "unknown",
                "Complete-in-scope selection requires a declared verified universe")

    searched = record["searched"]
    require_object_fields(searched, "searched scope", {"boundary", "inspected", "not_examined", "stop_reason", "stop_basis"})
    normalized_text(searched.get("boundary"), "searched boundary")
    inspected = searched.get("inspected")
    not_examined = searched.get("not_examined")
    require(isinstance(inspected, list) and isinstance(not_examined, list),
            "searched.inspected and searched.not_examined must be lists")
    for value in inspected + not_examined:
        normalized_text(value, "searched scope item")
    normalized_text(searched.get("stop_reason"), "searched stop_reason")
    basis = searched.get("stop_basis")
    require(isinstance(basis, list) and basis, "Missing searched stop_basis evidence")
    for index, span in enumerate(basis):
        check_span(root, span, f"stop_basis[{index}]", allowed_paths=allowed_sources)

    context = record["source_context"]
    require_object_fields(context, "source context", {"source_snapshot", "implementation_revision", "current_runtime"})
    snapshot = context.get("source_snapshot")
    require_object_fields(snapshot, "source snapshot", {"source_id", "path", "sha256", "document_version", "document_date"})
    snapshot_path = safe_relative(snapshot.get("path"), "source snapshot path")
    if allowed_sources is not None:
        require(snapshot_path in set(manifest.get("allowed_source_paths", [])),
                "Source snapshot must be one of this case's declared source files")
    snapshot_file = contained_file(root, snapshot_path)
    snapshot_hash = raw_sha256(snapshot_file)
    require(snapshot.get("sha256") == snapshot_hash, "Source snapshot fingerprint mismatch")
    normalized_text(snapshot.get("source_id"), "source snapshot source_id")
    for field in ("document_version", "document_date"):
        value = snapshot.get(field)
        require(value is None or isinstance(value, str), f"Invalid source snapshot {field}")
    validate_version_entry(context.get("implementation_revision"), "implementation_revision", root, allowed_sources)
    validate_version_entry(context.get("current_runtime"), "current_runtime", root, allowed_sources)

    handoff = record["handoff"]
    require_object_fields(handoff, "handoff", {"next_owner", "ack_status", "ack_evidence"})
    require(isinstance(handoff.get("next_owner"), str) and bool(handoff["next_owner"].strip()),
            "Missing handoff.next_owner; use a named owner or explicit unknown")
    require(handoff.get("ack_status") in {"confirmed", "unknown"}, "Invalid handoff ACK status")
    ack_evidence = handoff.get("ack_evidence")
    require(isinstance(ack_evidence, list), "Invalid handoff ACK evidence")
    if handoff["ack_status"] == "confirmed":
        require(ack_evidence, "Confirmed ACK requires evidence")
        for index, span in enumerate(ack_evidence):
            check_span(root, span, f"ack_evidence[{index}]", allowed_paths=allowed_sources)
    else:
        require(not ack_evidence, "Unknown ACK cannot include confirmation evidence")

    if allowed_sources is not None:
        review_source_paths = set(allowed_sources)
    else:
        review_source_paths = {snapshot_path}
        for member in members:
            review_source_paths.update(span["path"] for span in member["source_locators"])
        review_source_paths.update(span["path"] for span in searched["stop_basis"])
        for version_field in (context["implementation_revision"], context["current_runtime"]):
            review_source_paths.update(span["path"] for span in version_field["evidence"])
        review_source_paths.update(span["path"] for span in handoff["ack_evidence"])

    return {
        "artifact_path": artifact_path,
        "artifact_sha256": artifact_hash,
        "source_path": snapshot_path,
        "source_sha256": snapshot_hash,
        "review_source_paths": sorted(review_source_paths),
        "case_id": record["case_id"],
    }


def render_visible_block(record):
    selection = record["selection"]
    searched = record["searched"]
    context = record["source_context"]
    snapshot = context["source_snapshot"]
    impl = context["implementation_revision"]
    runtime = context["current_runtime"]
    handoff = record["handoff"]
    def locators(item):
        spans = item.get("source_locators", [])
        if not spans:
            return "no source locator"
        return ", ".join(f"{span['path']}:{span['line_start']}-{span['line_end']}" for span in spans)

    stop_locators = ", ".join(
        "{}:{}-{}".format(span["path"], span["line_start"], span["line_end"])
        for span in searched["stop_basis"])

    members = "; ".join(f"{item['ref']} ({item['origin']}; {locators(item)})" for item in selection["members"]) or "none"
    excluded = selection["exclusions_or_not_evaluated"]
    implementation = impl["value"] if impl["status"] == "known" else "unknown / not verified"
    current_runtime = runtime["value"] if runtime["status"] == "known" else "unknown / not verified"
    implementation_proof = locators({"source_locators": impl["evidence"]}) if impl["status"] == "known" else "no value locator claimed"
    runtime_proof = locators({"source_locators": runtime["evidence"]}) if runtime["status"] == "known" else "no value locator claimed"
    ack = "confirmed" if handoff["ack_status"] == "confirmed" else "unknown / not provided"
    ack_proof = locators({"source_locators": handoff["ack_evidence"]}) if handoff["ack_status"] == "confirmed" else "no confirmation locator"
    lines = [
        "## Project evidence audit (generated from the structured record)",
        f"- Objective/purpose: {selection['purpose']}",
        f"- Scope: {selection['scope']}",
        f"- Selection criterion: {selection['criterion']}",
        f"- Included: {members}",
        f"- Excluded or not examined: {excluded}",
        f"- Verified universe: {selection['universe_ref'] if selection['universe_ref'] is not None else 'unknown'}; completeness: {selection['completeness']} ({selection['count']} selected; count basis: {selection['count_basis']})",
        f"- Search boundary: {searched['boundary']}",
        f"- Inspected: {', '.join(searched['inspected']) or 'none listed'}",
        f"- Not examined: {', '.join(searched['not_examined']) or 'none listed'}",
        f"- Stop reason and basis: {searched['stop_reason']}",
        f"- Stop-basis locators: {stop_locators}",
        f"- Source snapshot identity: {snapshot['source_id']} | {snapshot['path']} | SHA-256 {snapshot['sha256']} | document version/date: {snapshot.get('document_version') or 'unknown'} / {snapshot.get('document_date') or 'unknown'}",
        f"- Implementation revision: {implementation}; evidence: {implementation_proof}",
        f"- Current runtime: {current_runtime}; evidence: {runtime_proof}",
        f"- Next owner: {handoff['next_owner']}; consumer ACK: {ack}; evidence: {ack_proof}",
        "- Semantic judgment: not made by this renderer; consult the separately hash-bound R14 review record.",
    ]
    if isinstance(record.get("narrative"), str) and record["narrative"].strip():
        lines.extend(["", "## Additional narrative", record["narrative"].strip()])
    return "\n".join(lines) + "\n"


def validate_review_record(review, binding, rendered_path: str, rendered_sha256: str,
                           evidence_root: Path, output_root: Path):
    load_profile()
    required = {"review_version", "input_artifact_sha256", "rendered_artifact", "source_sha256",
                "reviewer", "criterion", "reason", "status", "checks"}
    require_object_fields(review, "review record", required)
    require(review["review_version"] == "project-evidence-review-0.3.8", "Unsupported review record version")
    normalized_text(review["reviewer"], "reviewer")
    normalized_text(review["criterion"], "review criterion")
    normalized_text(review["reason"], "review reason")
    require(review["input_artifact_sha256"] == binding["artifact_sha256"],
            "Review record is not bound to this input artifact")
    require_object_fields(review["rendered_artifact"], "review rendered artifact", {"path", "sha256"})
    require(review["rendered_artifact"]["path"] == rendered_path and
            review["rendered_artifact"]["sha256"] == rendered_sha256,
            "Review record is not bound to this rendered visible block")
    require(review["source_sha256"] == binding["source_sha256"], "Review record is not bound to this source snapshot")
    require(review["status"] in STATUSES, "Invalid SC05 review status")
    checks = review["checks"]
    required_checks = {"selection_and_scope", "stop_reason", "source_snapshot_identity",
                       "implementation_and_runtime_boundary", "handoff_owner_and_ack"}
    require(isinstance(checks, dict) and set(checks) == required_checks,
            "Review checks must cover every required audit check")
    all_pass = True
    for check_id, item in checks.items():
        require_object_fields(item, f"review check {check_id}",
                              {"status", "reason", "output_spans", "source_spans"})
        require(item.get("status") in STATUSES, f"Invalid review check: {check_id}")
        normalized_text(item.get("reason"), f"review check {check_id} reason")
        out_spans, source_spans = item.get("output_spans"), item.get("source_spans")
        require(isinstance(out_spans, list) and isinstance(source_spans, list),
                f"Invalid review evidence lists: {check_id}")
        for span in out_spans:
            check_span(output_root, span, f"review output {check_id}",
                       expected_path=rendered_path, expected_hash=rendered_sha256)
        for span in source_spans:
            check_span(evidence_root, span, f"review source {check_id}",
                       allowed_paths=set(binding["review_source_paths"]))
        if item["status"] == "PASS":
            require(out_spans and source_spans, f"Passing review check lacks evidence: {check_id}")
        if item["status"] not in {"PASS", "NOT_RUN"}:
            all_pass = False
        if item["status"] == "NOT_RUN":
            all_pass = False
    if review["status"] == "PASS":
        require(all_pass and all(item["status"] == "PASS" for item in checks.values()),
                "Review cannot PASS while a required check is not PASS")
    return review["status"]


def audit(record_path: Path, root: Path, review_path: Path | None = None,
          visible_path: str | None = None, output_root: Path | None = None):
    evidence_root = Path(root).resolve()
    output_root = Path(output_root).resolve() if output_root is not None else evidence_root
    record = load_json(record_path)
    binding = validate_audit_record(record, evidence_root, output_root if output_root != evidence_root else None)
    visible = render_visible_block(record)
    rendered_sha = hashlib.sha256(visible.encode("utf-8")).hexdigest()
    review_status = "NOT_RUN"
    if review_path is not None:
        require(visible_path is not None, "A persisted rendered artifact path is required with an R14 review record")
        visible_path = safe_relative(visible_path, "rendered artifact path")
        if (evidence_root / "bundle-manifest.json").is_file():
            require(visible_path in OUTPUT_FILES, "Rendered case-bundle artifact must use a declared output filename")
        rendered_file = contained_file(output_root, visible_path)
        require(rendered_file.read_text(encoding="utf-8") == visible,
                "Persisted rendered artifact differs from deterministic helper output")
        review_file = Path(review_path)
        if not review_file.is_absolute():
            review_file = output_root / review_file
        review_status = validate_review_record(load_json(review_file), binding, visible_path,
                                               rendered_sha, evidence_root, output_root)
    readiness = "READY" if review_status == "PASS" else ("BLOCKED" if review_status == "FAIL" else "PARTIAL")
    return {
        "ok": True,
        "case_id": binding["case_id"],
        "readiness": readiness,
        "review_status": review_status,
        "rendered_sha256": rendered_sha,
        "rendered_path": visible_path,
        "artifact_sha256": binding["artifact_sha256"],
        "source_sha256": binding["source_sha256"],
        "evidence_layer": "mechanical_helper",
        "semantic_verified": False,
        "review_record_is_structural_only": review_path is not None,
        "visible_block": visible,
    }


def write_new_output(root: Path, relative: str, content: str):
    relative = safe_relative(relative, "rendered output path")
    root = Path(root).resolve()
    target = root.joinpath(*PurePosixPath(relative).parts)
    current = root
    for part in PurePosixPath(relative).parts[:-1]:
        current = current / part
        require(not current.is_symlink(), "Symlink not allowed in output path")
    require(target.parent.is_dir(), "Rendered output parent directory must exist")
    require(not target.is_symlink() and not target.exists(), "Refusing to overwrite existing output path")
    with target.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(content)


def _manifest_file(root: Path, relative: str, expected_hash: str | None = None):
    relative = safe_relative(relative, "bundle file path")
    path = contained_file(root, relative)
    digest = raw_sha256(path)
    if expected_hash is not None:
        require(digest == expected_hash, f"Source changed before bundle export: {relative}")
    return {"path": relative, "sha256": digest, "size_bytes": path.stat().st_size}


def export_case_bundle(source_root: Path, case_spec_path: Path, output: Path):
    source_root = Path(source_root).resolve()
    spec = load_json(case_spec_path)
    require(spec.get("profile_version") == PROFILE_VERSION, "Unsupported case bundle profile")
    case_id = normalized_text(spec.get("case_id"), "case_id")
    safe_case_id = re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", case_id)
    require(bool(safe_case_id), "Unsafe case_id")
    plugin = load_json(source_root / "plugin.json")
    overlay = load_json(source_root / ".codex-plugin" / "plugin.json")
    require(plugin.get("version") == "0.3.8" and overlay.get("version") == "0.3.8",
            "Both plugin manifests must be 0.3.8 before freezing a candidate bundle")
    require(isinstance(spec.get("input"), str), "Case must name one input file")
    source_entries = spec.get("sources")
    require(isinstance(source_entries, list) and source_entries,
            "Case must provide its exact source allowlist")
    context_paths = spec.get("runtime_context")
    require(isinstance(context_paths, list) and context_paths,
            "Case must name the runtime context snapshot files")
    allowlist = set(load_json(source_root / "packaging" / "runtime-files.json")["runtime_files"])
    normalized_context = [safe_relative(path, "runtime context path") for path in context_paths]
    require(set(normalized_context).issubset(allowlist), "Runtime context contains a non-packaged file")
    all_entries = [{"path": spec["input"]}] + source_entries + [{"path": path} for path in normalized_context]
    paths = [safe_relative(item.get("path"), "case path") for item in all_entries]
    require(len(paths) == len(set(paths)), "Duplicate path in per-case bundle allowlist")
    case_prefix = f"evaluation/project-evidence/0.3.8/cases/{case_id}/"
    case_files = [safe_relative(spec["input"], "case input")] + [
        safe_relative(item.get("path"), "case source") for item in source_entries]
    require(all(path.startswith(case_prefix) for path in case_files),
            "Case input/source must be contained in that case's own directory")
    require(all(Path(path).name.casefold() != "rubric.json" and "rubric" not in path.casefold()
                for path in case_files), "Evaluator rubric/material cannot be exported to a runner bundle")

    output = Path(output).absolute()
    require(not output.exists(), "Refusing to overwrite existing case bundle")
    parent = output.parent.resolve()
    require(parent.is_dir(), "Case bundle output parent must already exist")
    temp = Path(tempfile.mkdtemp(prefix=f".{case_id}-", dir=parent))
    files = []
    try:
        for item in all_entries:
            relative = safe_relative(item["path"], "case path")
            entry = _manifest_file(source_root, relative, item.get("sha256"))
            source = contained_file(source_root, relative)
            destination = temp.joinpath(*PurePosixPath(relative).parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
            files.append(entry)
        manifest = {
            "bundle_version": "project-evidence-case-bundle-0.3.8",
            "case_id": case_id,
            "profile_version": PROFILE_VERSION,
            "input_path": paths[0],
            "allowed_source_paths": [safe_relative(item["path"], "source path") for item in source_entries],
            "runtime_context_paths": normalized_context,
            "files": sorted(files, key=lambda item: item["path"]),
            "rubric_included": False,
            "isolation_claim": "exporter allowlist and one-bundle handoff only; does not sandbox agent tools or filesystem access",
        }
        (temp / "bundle-manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        temp.rename(output)
    except Exception:
        shutil.rmtree(temp, ignore_errors=True)
        raise
    return check_bundle(output)


def check_bundle(bundle: Path, source_root: Path | None = None):
    bundle = Path(bundle).resolve()
    manifest = load_json(bundle / "bundle-manifest.json")
    require(manifest.get("bundle_version") == "project-evidence-case-bundle-0.3.8",
            "Unsupported case bundle version")
    require(manifest.get("profile_version") == PROFILE_VERSION, "Bundle profile version mismatch")
    require(manifest.get("rubric_included") is False, "Evaluator rubric must not be in runner bundle")
    files = manifest.get("files")
    require(isinstance(files, list) and files, "Bundle file manifest is empty")
    declared = set()
    for entry in files:
        require(isinstance(entry, dict), "Invalid bundle manifest entry")
        relative = safe_relative(entry.get("path"), "bundle manifest path")
        require(relative not in declared, "Duplicate bundle manifest path")
        declared.add(relative)
        path = contained_file(bundle, relative)
        require(raw_sha256(path) == entry.get("sha256"), f"Captured bundle file changed: {relative}")
        if source_root is not None:
            current = contained_file(Path(source_root), relative)
            require(raw_sha256(current) == entry.get("sha256"), f"Stale release context/source capture: {relative}")
    expected = {manifest.get("input_path"), *manifest.get("allowed_source_paths", []),
                *manifest.get("runtime_context_paths", [])}
    require(expected == declared, "Bundle contains undeclared files or omits allowed files")
    for path in bundle.rglob("*"):
        require(not path.is_symlink(), "Symlinks are not allowed in a case bundle")
        if path.is_file() and path.name != "bundle-manifest.json":
            relative = path.relative_to(bundle).as_posix()
            require(relative in declared, f"Unexpected file in immutable case bundle: {relative}")
    return {"ok": True, "case_id": manifest["case_id"], "files": len(files),
            "bundle_sha256": raw_sha256(bundle / "bundle-manifest.json"),
            "rubric_included": False, "source_current_checked": source_root is not None,
            "isolation_claim": manifest["isolation_claim"], "semantic_verified": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    validate_parser = sub.add_parser("validate", help="Validate a structured audit and optional external review record")
    validate_parser.add_argument("record", type=Path)
    validate_parser.add_argument("--root", type=Path, required=True)
    validate_parser.add_argument("--output-root", type=Path,
                                 help="Separate directory for model outputs, rendered artifact and review file")
    validate_parser.add_argument("--review", type=Path)
    validate_parser.add_argument("--visible", help="Persisted renderer output path, required with --review")
    render_parser = sub.add_parser("render", help="Render the mandatory visible audit block")
    render_parser.add_argument("record", type=Path)
    render_parser.add_argument("--root", type=Path, required=True)
    render_parser.add_argument("--output-root", type=Path,
                               help="Separate directory for generated output; required for immutable case bundles")
    render_parser.add_argument("--output", type=Path)
    export_parser = sub.add_parser("export", help="Export exactly one case's allowlisted files")
    export_parser.add_argument("--source-root", type=Path, required=True)
    export_parser.add_argument("--case-spec", type=Path, required=True)
    export_parser.add_argument("--output", type=Path, required=True)
    bundle_parser = sub.add_parser("check-bundle", help="Check captured bundle and optionally current-source freshness")
    bundle_parser.add_argument("bundle", type=Path)
    bundle_parser.add_argument("--source-root", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command in {"validate", "render"}:
            if args.command == "render":
                output_root = args.output_root or args.root
                if (Path(args.root) / "bundle-manifest.json").is_file():
                    require(args.output_root is not None,
                            "Immutable case bundle requires a separate --output-root")
                result = audit(args.record, args.root, output_root=output_root)
                if args.output:
                    write_new_output(output_root, str(args.output), result["visible_block"])
                else:
                    sys.stdout.write(result["visible_block"])
            else:
                output_root = args.output_root or args.root
                result = audit(args.record, args.root, args.review, args.visible, output_root)
                result.pop("visible_block")
                print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        elif args.command == "export":
            print(json.dumps(export_case_bundle(args.source_root, args.case_spec, args.output),
                             ensure_ascii=False, sort_keys=True))
        else:
            print(json.dumps(check_bundle(args.bundle, args.source_root), ensure_ascii=False, sort_keys=True))
    except (AuditError, OSError, ValueError, KeyError, TypeError, RecursionError) as error:
        print(json.dumps({"ok": False, "error": str(error), "readiness": "PARTIAL",
                          "evidence_layer": "mechanical_helper", "semantic_verified": False},
                         ensure_ascii=False), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
