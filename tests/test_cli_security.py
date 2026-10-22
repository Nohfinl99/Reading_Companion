"""CLI-level security regression tests for the three helper CLIs.

Covers the glue layer (``main()``) that the per-module unit suites do not:
Red Team findings IA-A01 (ia_map wrote through a dangling symlink),
JSON-A01..A03 (deep JSON crashed every CLI with a RecursionError traceback)
and CP-A04 (duplicate JSON keys silently accepted). All tests drive the
CLIs through subprocess against temporary files only.
"""
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "skills" / "sid-reading-companion" / "scripts"
IA_PATH = SCRIPTS_DIR / "ia_map.py"
KC_PATH = SCRIPTS_DIR / "knowledge_compiler.py"
CP_PATH = SCRIPTS_DIR / "checkpoint.py"

DEEP_JSON = '{"a":' * 20_000 + "1" + "}" * 20_000


def run_cli(script, *args):
    return subprocess.run(
        [sys.executable, str(script), *[str(a) for a in args]],
        capture_output=True, text=True,
    )


def assert_clean_failure(result):
    """A controlled CLI failure: rc 1, JSON {ok: false} on stdout, no traceback."""
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "Traceback" not in result.stderr
    assert "RecursionError" not in result.stderr
    return payload


def valid_map():
    node = {
        "label_vi": "Agent",
        "definition": "Thành phần quyết định hành động theo mục tiêu.",
        "source_status": "read",
        "source_locators": ["p.549"],
        "knowledge_level": "L1",
        "in_scope": True,
    }
    return {
        "goal": "Hiểu quan hệ giữa agent và bộ công cụ",
        "views": ["conceptual"],
        "nodes": [dict(node, id="A"), dict(node, id="B")],
        "relations": [{
            "id": "E1", "from": "A", "to": "B", "label_vi": "hỗ trợ",
            "relation_type": "supports", "basis": "source_explicit",
            "source_locators": ["p.550"],
        }],
        "learning_order": [],
    }


def write_map(tmp_path, data=None, raw=None):
    src = tmp_path / "map.json"
    src.write_text(raw if raw is not None else json.dumps(data or valid_map()),
                   encoding="utf-8")
    return src


# ------------------------------------------------------------- IA-A01

def test_cli_ia_map_refuses_dangling_symlink_output(tmp_path):
    src = write_map(tmp_path)
    victim = tmp_path / "victim.json"
    link = tmp_path / "out_link.json"
    link.symlink_to(victim)
    result = run_cli(IA_PATH, "--input", src, "--output", link)
    payload = assert_clean_failure(result)
    assert payload["error"] == "Output must be a new file"
    assert not victim.exists(), "ia_map wrote through a dangling symlink"
    assert link.is_symlink()


def test_cli_ia_map_refuses_symlink_output_to_existing_file(tmp_path):
    src = write_map(tmp_path)
    existing = tmp_path / "existing.json"
    existing.write_text("{}", encoding="utf-8")
    link = tmp_path / "out_link.json"
    link.symlink_to(existing)
    result = run_cli(IA_PATH, "--input", src, "--output", link)
    assert_clean_failure(result)
    assert existing.read_text(encoding="utf-8") == "{}"


# ------------------------------------------------------------- JSON-A01..A03

def test_cli_ia_map_deep_json_fails_cleanly(tmp_path):
    src = write_map(tmp_path, raw=DEEP_JSON)
    result = run_cli(IA_PATH, "--input", src, "--output", tmp_path / "out.json")
    assert_clean_failure(result)


def test_cli_knowledge_compiler_deep_json_fails_cleanly(tmp_path):
    src = tmp_path / "request.json"
    src.write_text(DEEP_JSON, encoding="utf-8")
    result = run_cli(KC_PATH, "--input", src, "--output", tmp_path / "out.json")
    assert_clean_failure(result)


def test_cli_checkpoint_deep_json_fails_cleanly(tmp_path):
    state = tmp_path / "state.json"
    state.write_text(DEEP_JSON, encoding="utf-8")
    result = run_cli(CP_PATH, "check", "--state", state)
    assert_clean_failure(result)


# ------------------------------------------------------------- CP-A04

def test_cli_ia_map_duplicate_key_rejected(tmp_path):
    raw = json.dumps(valid_map(), ensure_ascii=False)
    raw = '{"goal": "first value wins in a naive read", ' + raw[1:]
    src = write_map(tmp_path, raw=raw)
    result = run_cli(IA_PATH, "--input", src, "--output", tmp_path / "out.json")
    payload = assert_clean_failure(result)
    assert "uplicate" in payload["error"]


def test_cli_knowledge_compiler_duplicate_key_rejected(tmp_path):
    # Pre-fix, json.loads keeps the LAST "task" ("explain") and compiles fine.
    raw = ('{"task": "bogus", "task": "explain", "mode": "deep",'
           ' "nodes": [], "target_ids": []}')
    src = tmp_path / "request.json"
    src.write_text(raw, encoding="utf-8")
    result = run_cli(KC_PATH, "--input", src, "--output", tmp_path / "out.json")
    payload = assert_clean_failure(result)
    assert "uplicate" in payload["error"]


def test_cli_checkpoint_duplicate_key_rejected(tmp_path):
    book = tmp_path / "book.txt"
    book.write_text("Nội dung sách mẫu.\n", encoding="utf-8")
    state = tmp_path / "state.json"
    init = run_cli(CP_PATH, "init", "--source", book, "--state", state,
                   "--mode", "deep")
    assert init.returncode == 0
    # Pre-fix, json.loads keeps the LAST "revision" (the real one) and the
    # forged first value is silently ignored, so `check` passes.
    raw = state.read_text(encoding="utf-8")
    forged = '{"revision": 999, ' + raw[1:]
    forged_path = tmp_path / "forged_state.json"
    forged_path.write_text(forged, encoding="utf-8")
    result = run_cli(CP_PATH, "check", "--state", forged_path)
    payload = assert_clean_failure(result)
    assert "uplicate" in payload["error"]


# ------------------------------------------------------------- CP-A05 (ia_map cap)

def test_cli_ia_map_oversized_input_rejected(tmp_path):
    raw = json.dumps(valid_map()) + " " * 1_048_576
    src = write_map(tmp_path, raw=raw)
    result = run_cli(IA_PATH, "--input", src, "--output", tmp_path / "out.json")
    payload = assert_clean_failure(result)
    assert "size limit" in payload["error"]
