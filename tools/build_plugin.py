#!/usr/bin/env python3
"""Build a deterministic runtime-only SID Reading Companion ZIP package."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import stat
import zipfile

ARCHIVE_ROOT = "sid-reading-companion"
FIXED_TIME = (1980, 1, 1, 0, 0, 0)


class PackageError(ValueError):
    pass


def _safe_relative(value: str) -> str:
    path = PurePosixPath(value)
    if (not value or path.is_absolute() or PureWindowsPath(value).drive or "\\" in value or
            value != path.as_posix() or any(part in {"", ".", ".."} for part in path.parts)):
        raise PackageError(f"Unsafe runtime path: {value!r}")
    return path.as_posix()


def load_allowlist(root: Path) -> list[str]:
    config_path = root / "packaging" / "runtime-files.json"
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        paths = config["runtime_files"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise PackageError(f"Cannot read runtime allowlist: {exc}") from exc
    if config.get("schema_version") != 1 or not isinstance(paths, list) or not paths:
        raise PackageError("Invalid runtime allowlist schema")
    normalized = [_safe_relative(item) for item in paths]
    if len(normalized) != len(set(normalized)):
        raise PackageError("Runtime allowlist contains duplicate paths")
    return sorted(normalized)


def _normalized_file(root: Path, rel: str) -> bytes:
    path = root.joinpath(*PurePosixPath(rel).parts)
    current = root
    for component in PurePosixPath(rel).parts:
        current = current / component
        try:
            mode = current.lstat().st_mode
        except OSError as exc:
            raise PackageError(f"Missing runtime file: {rel}") from exc
        if stat.S_ISLNK(mode):
            raise PackageError(f"Runtime path cannot contain symlinks: {rel}")
    if not stat.S_ISREG(mode):
        raise PackageError(f"Runtime path must be a regular file: {rel}")
    try:
        return path.read_bytes().decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    except UnicodeDecodeError as exc:
        raise PackageError(f"Runtime file is not UTF-8 text: {rel}") from exc


def build_package(root: Path, output: Path, source_commit: str,
                  manifest_path: Path | None = None) -> dict:
    root = root.resolve()
    output = output.resolve()
    if output == root or root in output.parents:
        raise PackageError("Archive output must be outside the source root")
    if output.exists():
        raise PackageError(f"Refusing to overwrite existing archive: {output}")
    manifest_path = (manifest_path or output.with_suffix(".manifest.json")).resolve()
    if manifest_path == output or manifest_path == root or root in manifest_path.parents:
        raise PackageError("Manifest output must be a separate file outside the source root")
    if manifest_path.exists():
        raise PackageError(f"Refusing to overwrite existing manifest: {manifest_path}")
    if not re.fullmatch(r"[0-9a-fA-F]{7,64}", source_commit):
        raise PackageError("source_commit must be a hexadecimal Git SHA (7–64 characters)")
    paths = load_allowlist(root)
    files = {rel: _normalized_file(root, rel) for rel in paths}
    try:
        plugin = json.loads(files["plugin.json"].decode("utf-8"))
    except (KeyError, ValueError) as exc:
        raise PackageError("Runtime plugin.json is missing or invalid") from exc
    version = plugin.get("version")
    if not isinstance(version, str) or not version.strip():
        raise PackageError("plugin.json needs a version")

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for rel in sorted(files):
            info = zipfile.ZipInfo(f"{ARCHIVE_ROOT}/{rel}", FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.flag_bits |= 0x800
            archive.writestr(info, files[rel], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    manifest = {
        "schema_version": 1,
        "archive": output.name,
        "archive_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "source_commit": source_commit.lower(),
        "source_identity": "caller-declared; builder does not verify the checkout or commit",
        "plugin_version": version,
        "hash_scheme": "SHA-256 over UTF-8 text after removing an optional UTF-8 BOM and normalizing all line endings to LF",
        "build_profile": {
            "archive_root": ARCHIVE_ROOT,
            "zip_timestamp": "1980-01-01T00:00:00",
            "file_mode": "0644",
            "compression": "ZIP_DEFLATED level 9",
            "reproducibility_scope": "byte-identical for the same inputs and Python/zlib implementation; cross-zlib-version byte identity is not guaranteed",
        },
        "files": {rel: {"sha256": hashlib.sha256(files[rel]).hexdigest(), "size_bytes": len(files[rel])}
                  for rel in sorted(files)},
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    try:
        manifest = build_package(args.root, args.output, args.source_commit, args.manifest)
    except PackageError as exc:
        parser.error(str(exc))
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
