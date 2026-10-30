"""Deterministic runtime package builder and verifier checks."""
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))
builder = importlib.import_module("build_plugin")
spec = importlib.util.spec_from_file_location("plugin_verify", TOOLS / "verify_plugin_package.py")
verifier = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = verifier
spec.loader.exec_module(verifier)


def synthetic_root(tmp_path):
    root = tmp_path / "source"
    root.mkdir()
    for rel in builder.load_allowlist(ROOT):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if rel in {"plugin.json", ".codex-plugin/plugin.json"}:
            value = {"name": "sid-reading-companion", "version": "9.8.7", "interface": {"displayName": "Reading Companion"}}
            if rel == "plugin.json":
                value = {"name": "sid-reading-companion", "version": "9.8.7",
                         "extensions": {"com.openai": {"interface": {"displayName": "Reading Companion"}}}}
            path.write_text(json.dumps(value), encoding="utf-8")
        elif rel.endswith("SKILL.md"):
            path.write_text("# Skill\n[README](../../README.md)\n", encoding="utf-8")
        elif rel.endswith("README.md"):
            path.write_text("# Readme\n", encoding="utf-8")
        elif rel.endswith(".md"):
            path.write_text("# Document\n", encoding="utf-8")
        else:
            path.write_text("synthetic runtime data\n", encoding="utf-8")
    config = root / "packaging/runtime-files.json"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text((ROOT / "packaging/runtime-files.json").read_text(encoding="utf-8"), encoding="utf-8")
    return root


def make_archive(tmp_path):
    source = synthetic_root(tmp_path)
    archive = tmp_path / "release.zip"
    manifest = tmp_path / "release.json"
    built = builder.build_package(source, archive, "0123456789abcdef", manifest)
    return source, archive, manifest, built


def test_build_is_deterministic_and_verifies_archive(tmp_path):
    source, archive, manifest, result = make_archive(tmp_path)
    other = tmp_path / "second.zip"
    builder.build_package(source, other, "0123456789abcdef", tmp_path / "second.json")
    assert archive.read_bytes() == other.read_bytes()
    assert result["plugin_version"] == "9.8.7"
    assert verifier.verify_package(archive, manifest)["ok"]
    with zipfile.ZipFile(archive) as zf:
        assert all(name.startswith("sid-reading-companion/") for name in zf.namelist())
        assert all(not name.endswith((".pyc", ".log")) for name in zf.namelist())
        assert all(zf.getinfo(name).date_time == (1980, 1, 1, 0, 0, 0) for name in zf.namelist())


def test_build_manifest_contains_normalized_file_hashes(tmp_path):
    source, archive, manifest, result = make_archive(tmp_path)
    (source / "README.md").write_bytes(b"\xef\xbb\xbf# Readme\r\nText\r")
    second = tmp_path / "normalized.zip"
    normalized = builder.build_package(source, second, "0123456789abcdef", tmp_path / "normalized.json")
    with zipfile.ZipFile(second) as zf:
        content = zf.read("sid-reading-companion/README.md")
    assert content == b"# Readme\nText\n"
    assert hashlib.sha256(content).hexdigest() == normalized["files"]["README.md"]["sha256"]
    assert len(content) == normalized["files"]["README.md"]["size_bytes"]
    assert normalized["source_commit"] == "0123456789abcdef"
    assert normalized["source_identity"].startswith("caller-declared")
    assert normalized["hash_scheme"].startswith("SHA-256 over UTF-8")
    assert "cross-zlib-version" in normalized["build_profile"]["reproducibility_scope"]


def test_verifier_rejects_archive_tampering(tmp_path):
    _, archive, manifest, _ = make_archive(tmp_path)
    archive.write_bytes(archive.read_bytes() + b"tamper")
    with pytest.raises(builder.PackageError, match="Archive SHA-256"):
        verifier.verify_package(archive, manifest)


def test_builder_rejects_missing_allowlisted_file(tmp_path):
    source = synthetic_root(tmp_path)
    (source / "LICENSE").unlink()
    with pytest.raises(builder.PackageError, match="Missing runtime file"):
        builder.build_package(source, tmp_path / "out.zip", "0123456789abcdef")


def test_builder_rejects_path_traversal_in_allowlist(tmp_path):
    source = synthetic_root(tmp_path)
    path = source / "packaging/runtime-files.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["runtime_files"].append("../outside.txt")
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(builder.PackageError, match="Unsafe runtime path"):
        builder.build_package(source, tmp_path / "out.zip", "0123456789abcdef")


@pytest.mark.parametrize("unsafe", ["C:/outside/file.txt", "C:relative.txt", "//server/share/file.txt"])
def test_builder_rejects_windows_drive_and_unc_paths(tmp_path, unsafe):
    source = synthetic_root(tmp_path)
    path = source / "packaging/runtime-files.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["runtime_files"].append(unsafe)
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(builder.PackageError, match="Unsafe runtime path"):
        builder.build_package(source, tmp_path / "out.zip", "0123456789abcdef")


def test_verifier_rejects_broken_local_markdown_link(tmp_path):
    _, archive, manifest, _ = make_archive(tmp_path)
    changed = tmp_path / "changed.zip"
    with zipfile.ZipFile(archive) as source, zipfile.ZipFile(changed, "w") as target:
        for item in source.infolist():
            data = source.read(item.filename)
            if item.filename == "sid-reading-companion/README.md":
                data = b"[missing](missing-page.md)\n"
            target.writestr(item, data)
    changed.replace(archive)
    # Recompute archive hash so the Markdown link check is reached.
    data = json.loads(manifest.read_text(encoding="utf-8"))
    data["archive_sha256"] = hashlib.sha256(archive.read_bytes()).hexdigest()
    data["files"]["README.md"] = {"sha256": hashlib.sha256(b"[missing](missing-page.md)\n").hexdigest(),
                                   "size_bytes": len(b"[missing](missing-page.md)\n")}
    manifest.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(builder.PackageError, match="Broken package Markdown link"):
        verifier.verify_package(archive, manifest)


def test_verifier_rejects_second_skill_entry_point(tmp_path):
    source = synthetic_root(tmp_path)
    config_path = source / "packaging/runtime-files.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["runtime_files"].append("skills/another-skill/SKILL.md")
    config_path.write_text(json.dumps(config), encoding="utf-8")
    extra = source / "skills/another-skill/SKILL.md"
    extra.parent.mkdir(parents=True)
    extra.write_text("# Extra skill\n", encoding="utf-8")
    archive = tmp_path / "two-skills.zip"
    manifest = tmp_path / "two-skills.json"
    builder.build_package(source, archive, "0123456789abcdef", manifest)
    with pytest.raises(builder.PackageError, match="exactly one discovered skill"):
        verifier.verify_package(archive, manifest)


def test_builder_refuses_output_inside_source_and_overwrite(tmp_path):
    source = synthetic_root(tmp_path)
    with pytest.raises(builder.PackageError, match="outside the source root"):
        builder.build_package(source, source / "nested.zip", "0123456789abcdef")
    target = tmp_path / "exists.zip"
    target.write_bytes(b"existing")
    with pytest.raises(builder.PackageError, match="Refusing to overwrite"):
        builder.build_package(source, target, "0123456789abcdef")
