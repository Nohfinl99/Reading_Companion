#!/usr/bin/env python3
"""Verify package hashes, runtime metadata, required files, and local Markdown links."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import PurePosixPath
import re
import zipfile
from urllib.parse import unquote, urlparse

from build_plugin import ARCHIVE_ROOT, PackageError, _safe_relative


def _markdown_targets(text: str):
    # Inline links/images and reference-style link destinations.
    pattern = re.compile(r"!?\[[^\]]*\]\(\s*<?([^\s)>]+)>?(?:\s+[^)]*)?\)|^\s*\[[^\]]+\]:\s*<?([^\s>]+)>?", re.MULTILINE)
    for match in pattern.finditer(text):
        yield match.group(1) or match.group(2)


def verify_package(archive_path, manifest_path):
    archive_path = archive_path.resolve()
    manifest_path = manifest_path.resolve()
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise PackageError(f"Cannot read package manifest: {exc}") from exc
    if manifest.get("schema_version") != 1 or not isinstance(manifest.get("files"), dict):
        raise PackageError("Invalid package manifest schema")
    digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    if digest != manifest.get("archive_sha256"):
        raise PackageError("Archive SHA-256 does not match manifest")
    try:
        with zipfile.ZipFile(archive_path) as zf:
            names = zf.namelist()
            if len(names) != len(set(names)):
                raise PackageError("Archive contains duplicate entries")
            expected = {f"{ARCHIVE_ROOT}/{p}" for p in manifest["files"]}
            if set(names) != expected:
                raise PackageError("Archive file list does not match manifest")
            content = {}
            for name in names:
                relative = name.removeprefix(f"{ARCHIVE_ROOT}/")
                _safe_relative(relative)
                data = zf.read(name)
                file_record = manifest["files"].get(relative)
                if (not isinstance(file_record, dict) or
                        hashlib.sha256(data).hexdigest() != file_record.get("sha256") or
                        len(data) != file_record.get("size_bytes")):
                    raise PackageError(f"File hash mismatch: {relative}")
                content[relative] = data
    except (OSError, zipfile.BadZipFile, KeyError) as exc:
        raise PackageError(f"Cannot read package archive: {exc}") from exc
    for required in ("plugin.json", "skills/sid-reading-companion/SKILL.md"):
        if required not in content:
            raise PackageError(f"Required runtime file missing: {required}")
    try:
        metadata = json.loads(content["plugin.json"].decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise PackageError("Packaged plugin.json is invalid") from exc
    if metadata.get("name") != "sid-reading-companion" or metadata.get("version") != manifest.get("plugin_version"):
        raise PackageError("Packaged plugin metadata does not match manifest")
    try:
        codex_metadata = json.loads(content[".codex-plugin/plugin.json"].decode("utf-8"))
    except (KeyError, ValueError, UnicodeDecodeError) as exc:
        raise PackageError("Packaged Codex plugin metadata is missing or invalid") from exc
    if codex_metadata.get("name") != metadata["name"] or codex_metadata.get("version") != metadata["version"]:
        raise PackageError("Packaged plugin metadata versions do not agree")
    interface = metadata.get("extensions", {}).get("com.openai", {}).get("interface")
    if not isinstance(interface, dict) or codex_metadata.get("interface") != interface:
        raise PackageError("Root and Codex plugin interfaces do not agree")
    if metadata.get("skills", "./skills") != "./skills":
        raise PackageError("Plugin skills path must be omitted or point to ./skills")
    skill_entries = [path for path in content if PurePosixPath(path).match("skills/*/SKILL.md")]
    if len(skill_entries) != 1:
        raise PackageError(f"Package must contain exactly one discovered skill entry point; found {len(skill_entries)}")
    if not isinstance(manifest.get("source_commit"), str) or not manifest["source_commit"]:
        raise PackageError("Manifest source_commit is missing")

    package_paths = set(content)
    for rel, data in content.items():
        if not rel.lower().endswith(".md"):
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise PackageError(f"Packaged Markdown is not UTF-8: {rel}") from exc
        for target in _markdown_targets(text):
            target = unquote(target)
            parsed = urlparse(target)
            if parsed.scheme or parsed.netloc or target.startswith("//"):
                continue
            raw_path = parsed.path
            if not raw_path:
                continue
            base = PurePosixPath(rel).parent
            resolved = PurePosixPath(raw_path) if raw_path.startswith("/") else base / raw_path
            stack = []
            for component in resolved.parts:
                if component in ("", ".", "/"):
                    continue
                if component == "..":
                    if not stack:
                        raise PackageError(f"Markdown link escapes package: {rel} -> {target}")
                    stack.pop()
                else:
                    stack.append(component)
            link_path = PurePosixPath(*stack).as_posix()
            if link_path not in package_paths:
                raise PackageError(f"Broken package Markdown link: {rel} -> {target}")
    return {"ok": True, "file_count": len(content), "plugin_version": metadata["version"], "archive_sha256": digest}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=__import__("pathlib").Path)
    parser.add_argument("--manifest", type=__import__("pathlib").Path, required=True)
    args = parser.parse_args()
    try:
        result = verify_package(args.archive, args.manifest)
    except PackageError as exc:
        parser.error(str(exc))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
