"""Validate repository packaging and local documentation links (not semantics)."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []
def require(ok: bool, message: str) -> None:
    if not ok: errors.append(message)
root_manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
compat_manifest = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
root_ui = root_manifest.get("extensions", {}).get("com.openai", {}).get("interface", {})
compat_ui = compat_manifest.get("interface", {})
require(root_manifest.get("name") == compat_manifest.get("name"), "Manifest names differ")
require(root_manifest.get("version") == compat_manifest.get("version"), "Manifest versions differ")
require(root_manifest.get("name") == "sid-reading-companion", "Unexpected technical plugin identity")
require(root_ui.get("displayName") == compat_ui.get("displayName"), "Manifest display names differ")
require(root_ui.get("defaultPrompt") == compat_ui.get("defaultPrompt"), "Manifest default prompts differ")
skill_path = ROOT / root_manifest.get("skills", "skills") / "sid-reading-companion/SKILL.md"
require(skill_path.is_file(), "Skill entry point is missing")
required = ["references/master-instruction.md", "references/knowledge-compiler.md", "references/reading-protocols.md", "references/stack-contracts.md", "references/case-benchmark.md", "scripts/checkpoint.py", "scripts/ia_map.py", "scripts/knowledge_compiler.py", "scripts/reading_session.py"]
for rel in required: require((skill_path.parent / rel).is_file(), f"Required plugin file missing: {rel}")
for doc in ROOT.rglob("*.md"):
    if any(part in {".git", "__pycache__"} for part in doc.parts): continue
    text = doc.read_text(encoding="utf-8")
    for match in re.finditer(r"!?(?:\[[^\]]*\])\(([^)]+)\)", text):
        target = match.group(1).strip().split()[0].strip("<>")
        if not target or target.startswith(("http://", "https://", "mailto:", "data:")) or target.startswith("#"): continue
        local = target.split("#", 1)[0].split("?", 1)[0]
        if not local: continue
        resolved = (doc.parent / local).resolve()
        try: resolved.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f"Link escapes repository: {doc.relative_to(ROOT)} -> {target}")
            continue
        if not resolved.exists(): errors.append(f"Broken local link: {doc.relative_to(ROOT)} -> {target}")
if errors:
    print("Repository validation failed:", file=sys.stderr)
    for error in errors: print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)
print(f"Repository structure and local Markdown links passed; plugin version {root_manifest['version']}.")
