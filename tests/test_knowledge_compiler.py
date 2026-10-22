"""Unit tests for skills/sid-reading-companion/scripts/knowledge_compiler.py.

Implemented from specs/spec_compiler_ia.md (agent B2). Each test function name
carries its spec case ID (KC-01 ... KC-58). Negative cases assert both the
exception type (InvalidPlan) and the exact error message from the code.
The module under test is loaded in place from the repo tree: registry() reads
references/reading-protocols.md relative to the module file, so the script
must NOT be copied elsewhere for the registry-dependent cases.
"""
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "skills" / "sid-reading-companion" / "scripts"
KC_PATH = SCRIPTS_DIR / "knowledge_compiler.py"


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


kc = _load_module("knowledge_compiler", KC_PATH)
InvalidPlan = kc.InvalidPlan

MASTER_M05 = {"file": "references/master-instruction.md", "section_ids": ["M05"]}
KC_ALL = {
    "file": "references/knowledge-compiler.md",
    "section_ids": ["KC01", "KC02", "KC03", "KC04", "KC05"],
}


def protocols_ref(section_ids):
    return {"file": "references/reading-protocols.md", "section_ids": section_ids}


def make_node(**overrides):
    """Base valid compiler node (spec section 4.1)."""
    node = {
        "id": "K1",
        "title": "Agent chọn tool theo ý định",
        "knowledge_level": "L2",
        "source_status": "read",
        "locator": "p.550",
        "in_scope": True,
        "relevance": "high",
        "prerequisites": [],
        "relations": [],
    }
    node.update(overrides)
    return node


def make_request(**overrides):
    """Base valid compiler request (spec section 4.2)."""
    request = {
        "task": "explain",
        "mode": "deep",
        "target_ids": ["K1"],
        "nodes": [make_node()],
    }
    request.update(overrides)
    return request


def demo_record(**overrides):
    """Base valid demonstration record (spec section 4.3)."""
    record = {
        "node_id": "K1",
        "support": "none",
        "result": "independent",
        "response": "Câu trả lời nguyên văn của người học.",
    }
    record.update(overrides)
    return record


def assert_invalid(callable_, message):
    with pytest.raises(InvalidPlan) as excinfo:
        callable_()
    assert str(excinfo.value) == message


# ---------------------------------------------------------------- registry()

def test_kc_01_registry_canonical_nine_artifacts():
    registry = kc.registry()
    assert set(registry) == {f"RA-0{i}" for i in range(1, 10)}
    ra05 = registry["RA-05"]
    assert ra05["required"] == [
        "unit_ids", "content", "conditions",
        "knowledge_levels", "citations", "relations",
    ]
    assert ra05["format"] == "markdown_or_json"
    assert ra05["default"] is True
    assert len(registry["RA-09"]["tasks"]) == 7
    assert registry["RA-01"]["format"] == "outline_table_or_diagram"


def _load_compiler_copy(tmp_path, protocols_text):
    """Copy the compiler into a scratch skill tree with a custom protocols file."""
    skill = tmp_path / "skill"
    (skill / "scripts").mkdir(parents=True)
    (skill / "references").mkdir(parents=True)
    shutil.copy(KC_PATH, skill / "scripts" / "knowledge_compiler.py")
    (skill / "references" / "reading-protocols.md").write_text(
        protocols_text, encoding="utf-8"
    )
    return _load_module("knowledge_compiler_copy", skill / "scripts" / "knowledge_compiler.py")


def _registry_block(artifacts_json):
    return (
        "<!-- ARTIFACT_REGISTRY_START -->\n```json\n"
        + json.dumps({"version": "0.3.0", "artifacts": artifacts_json})
        + "\n```\n<!-- ARTIFACT_REGISTRY_END -->\n"
    )


def _assert_copy_invalid(mod, message):
    # The copied module defines its own InvalidPlan class object, distinct
    # from the original module's, so assert against the copy's class.
    with pytest.raises(mod.InvalidPlan) as excinfo:
        mod.registry()
    assert str(excinfo.value) == message


def test_kc_02_registry_block_missing(tmp_path):
    mod = _load_compiler_copy(tmp_path, "# Protocols without a registry block\n")
    _assert_copy_invalid(
        mod, "Canonical artifact registry missing/duplicate; no legacy fallback"
    )


def test_kc_02_registry_block_duplicated(tmp_path):
    block = _registry_block([{"id": "RA-01"}])
    mod = _load_compiler_copy(tmp_path, block + "\n" + block)
    _assert_copy_invalid(
        mod, "Canonical artifact registry missing/duplicate; no legacy fallback"
    )


def test_kc_03_registry_duplicate_artifact_id(tmp_path):
    mod = _load_compiler_copy(
        tmp_path, _registry_block([{"id": "RA-01"}, {"id": "RA-01"}])
    )
    _assert_copy_invalid(mod, "Duplicate artifact ID")


# ------------------------------------------------------------ reference_plan()

def test_kc_04_reference_plan_assess():
    assert kc.reference_plan("assess", "deep") == [
        MASTER_M05,
        protocols_ref(["R04", "R06"]),
    ]


def test_kc_05_reference_plan_explain():
    assert kc.reference_plan("explain", "deep") == [
        MASTER_M05,
        KC_ALL,
        protocols_ref(["R01", "R06"]),
    ]


def test_kc_06_reference_plan_extract_deep_vs_combined():
    assert kc.reference_plan("extract", "deep") == [
        MASTER_M05,
        KC_ALL,
        protocols_ref(["R02", "R07", "R09", "R06"]),
    ]
    assert kc.reference_plan("extract", "combined") == [
        MASTER_M05,
        KC_ALL,
        protocols_ref(["R01", "R02", "R07", "R09", "R06"]),
    ]


def test_kc_07_reference_plan_compare_map_continue():
    assert kc.reference_plan("compare", "deep") == [
        MASTER_M05, KC_ALL, protocols_ref(["R03", "R09", "R06", "R07"]),
    ]
    assert kc.reference_plan("map", "deep") == [
        MASTER_M05, KC_ALL, protocols_ref(["R08", "R09"]),
    ]
    assert kc.reference_plan("continue", "deep") == [
        MASTER_M05, KC_ALL, protocols_ref(["R11", "R12", "R07"]),
    ]


def test_kc_08_reference_plan_transfer_includes_r13():
    plan = kc.reference_plan("transfer", "deep")
    assert plan == [MASTER_M05, KC_ALL, protocols_ref(["R09", "R13", "R04", "R06"])]
    sections = plan[-1]["section_ids"]
    # KC-08 closed: R13 added to the transfer reference plan per NohFinl's decision, 2026-10-23.
    assert "R13" in sections


def test_kc_09_reference_plan_validated_content():
    assert kc.reference_plan("explain", "deep", validated_content=True) == [
        MASTER_M05,
        protocols_ref(["R09", "R07", "R06"]),
    ]
    assert kc.reference_plan(
        "map", "deep", validated_content=True, ia_views=["conceptual"]
    ) == [
        MASTER_M05,
        protocols_ref(["R08", "R09", "R07", "R06"]),
    ]


def test_kc_10_reference_plan_portable():
    assert kc.reference_plan("explain", "deep", portable=True)[-1] == protocols_ref(
        ["R01", "R06", "R12"]
    )
    assert kc.reference_plan("continue", "deep", portable=True)[-1] == protocols_ref(
        ["R11", "R12", "R07"]
    )
    assert kc.reference_plan("assess", "deep", portable=True)[-1] == protocols_ref(
        ["R04", "R06", "R12"]
    )


def test_kc_11_reference_plan_inherits_route_guards():
    assert_invalid(lambda: kc.reference_plan("bogus", "deep"), "Invalid task/mode")
    assert_invalid(lambda: kc.reference_plan("explain", "quick"), "Invalid task/mode")
    assert_invalid(
        lambda: kc.reference_plan("explain", "deep", ia_views=["conceptual"]),
        "IA views require map task; assess/other fast paths stay unchanged",
    )


# ---------------------------------------------------------------- event_plan()

NAV_EVENTS = ["next", "back", "jump", "return", "read", "pause", "resume", "style", "progress"]


@pytest.mark.parametrize("event", NAV_EVENTS)
def test_kc_12_event_plan_navigation_fast_path(event):
    plan = kc.event_plan(event, "deep")
    assert plan["reference_plan"] == [MASTER_M05, protocols_ref(["R10", "R11"])]
    assert plan["content_recompile"] is False
    assert plan["retrieval_verified"] is False
    assert plan["state_mutated"] is False
    assert plan["event"] == event
    assert plan["mode"] == "deep"


def test_kc_13_event_plan_term_and_connect():
    term = kc.event_plan("term", "deep")
    assert term["reference_plan"] == [MASTER_M05, protocols_ref(["R06"])]
    connect = kc.event_plan("connect", "deep")
    assert connect["reference_plan"] == [
        MASTER_M05,
        protocols_ref(["R10", "R07"]),
        {"file": "references/knowledge-compiler.md", "section_ids": ["KC01", "KC03"]},
    ]


@pytest.mark.parametrize("event", ["quick", "chill", "challenger"])
@pytest.mark.parametrize(
    "mode,expected_sections",
    [
        ("extract", ["R10", "R02", "R06"]),
        ("deep", ["R10", "R01", "R06"]),
        ("combined", ["R10", "R01", "R06"]),
    ],
)
def test_kc_14_event_plan_style_branches(event, mode, expected_sections):
    plan = kc.event_plan(event, mode)
    assert plan["reference_plan"][1] == protocols_ref(expected_sections)
    assert plan["reference_plan"][2] == {
        "file": "references/knowledge-compiler.md",
        "section_ids": ["KC01", "KC04"],
    }


def test_kc_15_event_plan_unknown_event_and_invalid_mode():
    assert_invalid(lambda: kc.event_plan("shuffle", "deep"), "Unknown reading event")
    assert_invalid(lambda: kc.event_plan("next", "standard"), "Invalid event mode")
    # Mode is checked before the event name.
    assert_invalid(lambda: kc.event_plan("shuffle", "standard"), "Invalid event mode")


# ----------------------------------------------------------- select_artifacts()

@pytest.mark.parametrize(
    "task,expected_ids",
    [
        ("extract", ["RA-05"]),
        ("compare", ["RA-04"]),
        ("map", ["RA-01"]),
        ("transfer", ["RA-07"]),
        ("assess", ["RA-08"]),
        ("explain", []),
        ("continue", []),
    ],
)
def test_kc_16_select_artifacts_defaults(task, expected_ids):
    selected = kc.select_artifacts(task)
    assert [row["id"] for row in selected] == expected_ids
    for row in selected:
        assert set(row) == {"id", "required", "format"}
    if task == "extract":
        assert selected[0]["required"] == [
            "unit_ids", "content", "conditions",
            "knowledge_levels", "citations", "relations",
        ]
        assert selected[0]["format"] == "markdown_or_json"


def test_kc_17_select_artifacts_explicit():
    assert kc.select_artifacts("explain", "RA-02") == [
        {
            "id": "RA-02",
            "required": ["definition", "conditions", "locator"],
            "format": "markdown",
        }
    ]
    ra09 = kc.select_artifacts("continue", "RA-09")
    assert len(ra09) == 1
    assert ra09[0]["format"] == "markdown_or_file"


def test_kc_18_select_artifacts_invalid():
    assert_invalid(lambda: kc.select_artifacts("explain", "RA-99"), "Unknown artifact")
    assert_invalid(lambda: kc.select_artifacts("explain", 5), "Unknown artifact")
    assert_invalid(
        lambda: kc.select_artifacts("extract", "RA-04"),
        "Artifact incompatible with task",
    )
    assert_invalid(lambda: kc.select_artifacts("bogus"), "Unknown task")


def test_kc_19_select_artifacts_portable_adds_ra09():
    assert [r["id"] for r in kc.select_artifacts("map", portable=True)] == ["RA-01", "RA-09"]
    assert [
        r["id"] for r in kc.select_artifacts("explain", "RA-02", portable=True)
    ] == ["RA-02", "RA-09"]
    assert [
        r["id"] for r in kc.select_artifacts("continue", "RA-09", portable=True)
    ] == ["RA-09"]


# ---------------------------------------------------------------------- route()

def test_kc_20_route_rejects_invalid_task_mode():
    # NOTE: route()'s message differs from compile_plan()'s (no "; clarify first").
    assert_invalid(lambda: kc.route("bogus", "deep"), "Invalid task/mode")
    assert_invalid(lambda: kc.route("explain", "quick"), "Invalid task/mode")


def test_kc_21_route_explain_full_stages():
    assert kc.route("explain", "deep") == [
        "SOURCE_CHECK", "SOURCE_SEGMENT_CHECK", "TERMINOLOGY_CONTEXT", "COMPILE",
        "DEEP_READ", "VIETNAMESE_DRAFT", "BILINGUAL_REVIEW", "CURRENCY_REVIEW",
        "SELECT_ARTIFACT", "BUILD_ARTIFACT", "VALIDATE", "HUMANIZE",
        "LANGUAGE_PRESERVATION_CHECK", "STYLE_CHECK", "RENDER",
    ]


def test_kc_22_route_map_skips_language_and_currency():
    stages = kc.route("map", "deep")
    assert stages == [
        "SOURCE_CHECK", "COMPILE", "MAP", "SELECT_ARTIFACT", "BUILD_ARTIFACT",
        "VALIDATE", "HUMANIZE", "LANGUAGE_PRESERVATION_CHECK", "STYLE_CHECK",
        "RENDER",
    ]
    assert "CURRENCY_REVIEW" not in stages
    assert "VIETNAMESE_DRAFT" not in stages


def test_kc_23_route_assess_and_extract_guard():
    expected = [
        "ASSESS", "FEEDBACK_LANGUAGE_REVIEW", "VALIDATE", "HUMANIZE",
        "LANGUAGE_PRESERVATION_CHECK", "STYLE_CHECK", "RENDER",
    ]
    assert kc.route("assess", "deep") == expected
    assert kc.route("assess", "combined") == expected
    assert_invalid(
        lambda: kc.route("assess", "extract"),
        "Assessment requires an explicitly chosen learning mode",
    )


# KC-24: spec errata 2026-10-22 — the validated_content route uses
# 'CURRENCY_REUSE_CHECK' (code is authoritative; see ERRATA under KC-24 in
# specs/spec_compiler_ia.md). Former xfail removed per approved decision.
def test_kc_24_route_validated_content():
    assert kc.route("explain", "deep", validated_content=True) == [
        "SELECT_ARTIFACT", "BUILD_ARTIFACT", "CURRENCY_REUSE_CHECK", "VALIDATE",
        "HUMANIZE", "LANGUAGE_PRESERVATION_CHECK", "STYLE_CHECK", "RENDER",
    ]


def test_kc_25_route_map_with_ia_views():
    stages = kc.route("map", "deep", ia_views=["conceptual"])
    assert stages == [
        "SOURCE_CHECK", "SOURCE_SEGMENT_CHECK", "TERMINOLOGY_CONTEXT", "COMPILE",
        "MAP", "IA_RELATIONS", "IA_SELECT_VIEW", "SELECT_ARTIFACT",
        "VIETNAMESE_DRAFT", "BILINGUAL_REVIEW", "CURRENCY_REVIEW", "BUILD_ARTIFACT",
        "IA_SEMANTIC_CHECK", "IA_STRUCTURE_CHECK", "VALIDATE", "HUMANIZE",
        "LANGUAGE_PRESERVATION_CHECK", "STYLE_CHECK", "IA_DISPLAY_CHECK", "RENDER",
    ]
    validated = kc.route("map", "deep", validated_content=True, ia_views=["learning"])
    assert validated == [
        "IA_REUSE_CHECK", "IA_SELECT_VIEW", "SELECT_ARTIFACT", "BUILD_ARTIFACT",
        "CURRENCY_REUSE_CHECK", "IA_SEMANTIC_CHECK", "IA_STRUCTURE_CHECK",
        "VALIDATE", "HUMANIZE", "LANGUAGE_PRESERVATION_CHECK", "STYLE_CHECK",
        "IA_DISPLAY_CHECK", "RENDER",
    ]
    assert "COMPILE" not in validated


def test_kc_26_route_ia_views_validation():
    assert_invalid(
        lambda: kc.route("map", "deep", ia_views="conceptual"), "Invalid IA views"
    )
    assert_invalid(
        lambda: kc.route("map", "deep", ia_views=["foo"]), "Invalid IA views"
    )
    assert_invalid(
        lambda: kc.route("map", "deep", ia_views=["conceptual", "conceptual"]),
        "Invalid IA views",
    )
    assert_invalid(
        lambda: kc.route("explain", "deep", ia_views=["conceptual"]),
        "IA views require map task; assess/other fast paths stay unchanged",
    )


# ------------------------------------------- compile_plan(): request and nodes

def test_kc_27_compile_plan_request_and_task_mode():
    assert_invalid(lambda: kc.compile_plan(["explain"]), "Request must be an object")
    assert_invalid(
        lambda: kc.compile_plan({"task": "bogus", "mode": "deep"}),
        "Invalid task/mode; clarify first",
    )
    assert_invalid(
        lambda: kc.compile_plan({"task": "explain", "mode": "quick"}),
        "Invalid task/mode; clarify first",
    )
    assert_invalid(
        lambda: kc.compile_plan({"mode": "deep"}),
        "Invalid task/mode; clarify first",
    )


@pytest.mark.parametrize("level", ["L1", "L2", "L3", "L4"])
def test_kc_28_compile_plan_learner_level_echo(level):
    plan = kc.compile_plan(make_request(learner_level=level))
    assert plan["learner_level"] == level


def test_kc_28_compile_plan_learner_level_default_unknown():
    assert kc.compile_plan(make_request())["learner_level"] == "unknown"


def test_kc_28_compile_plan_invalid_level_and_boolean_flags():
    assert_invalid(
        lambda: kc.compile_plan(make_request(learner_level="L5")),
        "Invalid learner level",
    )
    assert_invalid(
        lambda: kc.compile_plan(make_request(portable_requested=1)),
        "portable_requested must be boolean",
    )
    assert_invalid(
        lambda: kc.compile_plan(make_request(portable_requested="true")),
        "portable_requested must be boolean",
    )
    assert_invalid(
        lambda: kc.compile_plan(make_request(validated_content=1)),
        "validated_content must be boolean",
    )


def test_kc_29_compile_plan_inherits_artifact_and_route_errors():
    assert_invalid(
        lambda: kc.compile_plan(make_request(requested_artifact="RA-99")),
        "Unknown artifact",
    )
    assert_invalid(
        lambda: kc.compile_plan(make_request(requested_artifact="RA-04")),
        "Artifact incompatible with task",
    )
    assert_invalid(
        lambda: kc.compile_plan({"task": "assess", "mode": "extract"}),
        "Assessment requires an explicitly chosen learning mode",
    )
    assert_invalid(
        lambda: kc.compile_plan(make_request(ia_views=["conceptual"])),
        "IA views require map task; assess/other fast paths stay unchanged",
    )


def _bulk_nodes(count):
    return [make_node(id=f"K{i:03d}") for i in range(count)]


def test_kc_30_compile_plan_node_batch_limit():
    plan = kc.compile_plan({"task": "explain", "mode": "deep", "nodes": _bulk_nodes(256)})
    assert plan["status"] == "READY"
    assert len(plan["order"]) == 256
    assert_invalid(
        lambda: kc.compile_plan(
            {"task": "explain", "mode": "deep", "nodes": _bulk_nodes(257)}
        ),
        "nodes must be a list of at most 256 per batch",
    )
    assert_invalid(
        lambda: kc.compile_plan({"task": "explain", "mode": "deep", "nodes": {}}),
        "nodes must be a list of at most 256 per batch",
    )


def test_kc_31_compile_plan_node_object_and_id():
    assert_invalid(
        lambda: kc.compile_plan(make_request(nodes=["K1"])),
        "Node must be an object",
    )
    node_no_id = make_node()
    del node_no_id["id"]
    assert_invalid(
        lambda: kc.compile_plan(make_request(nodes=[node_no_id])),
        "Missing/duplicate node ID",
    )
    assert_invalid(
        lambda: kc.compile_plan(make_request(nodes=[make_node(id="  ")])),
        "Missing/duplicate node ID",
    )
    assert_invalid(
        lambda: kc.compile_plan(make_request(nodes=[make_node(), make_node()])),
        "Missing/duplicate node ID",
    )


def test_kc_32_compile_plan_node_title_level_status():
    node_no_title = make_node()
    del node_no_title["title"]
    assert_invalid(
        lambda: kc.compile_plan(make_request(nodes=[node_no_title])),
        "Missing node title",
    )
    assert_invalid(
        lambda: kc.compile_plan(make_request(nodes=[make_node(title=" ")])),
        "Missing node title",
    )
    assert_invalid(
        lambda: kc.compile_plan(make_request(nodes=[make_node(knowledge_level="L0")])),
        "Invalid knowledge level",
    )
    assert_invalid(
        lambda: kc.compile_plan(make_request(nodes=[make_node(source_status="unknown")])),
        "Invalid source status",
    )


def test_kc_33_compile_plan_node_locator_rules():
    # Available source (read) passes with a locator.
    assert kc.compile_plan(make_request())["status"] == "READY"
    # A missing-source node passes node-level checks; its failure is a
    # traversal-level block (see KC-44), not an exception.
    plan = kc.compile_plan(
        make_request(nodes=[make_node(source_status="missing", locator="")])
    )
    assert plan["status"] == "BLOCKED"
    assert_invalid(
        lambda: kc.compile_plan(make_request(nodes=[make_node(locator=123)])),
        "locator must be text",
    )
    assert_invalid(
        lambda: kc.compile_plan(make_request(nodes=[make_node(locator="")])),
        "Available source requires locator",
    )
    assert_invalid(
        lambda: kc.compile_plan(
            make_request(nodes=[make_node(source_status="identified", locator="  ")])
        ),
        "Available source requires locator",
    )


def test_kc_34_compile_plan_node_in_scope_and_relevance():
    assert_invalid(
        lambda: kc.compile_plan(make_request(nodes=[make_node(in_scope=1)])),
        "in_scope must be boolean",
    )
    assert_invalid(
        lambda: kc.compile_plan(make_request(nodes=[make_node(in_scope="true")])),
        "in_scope must be boolean",
    )
    node_no_scope = make_node()
    del node_no_scope["in_scope"]
    assert_invalid(
        lambda: kc.compile_plan(make_request(nodes=[node_no_scope])),
        "in_scope must be boolean",
    )
    assert_invalid(
        lambda: kc.compile_plan(make_request(nodes=[make_node(relevance="critical")])),
        "Invalid relevance",
    )


def test_kc_35_compile_plan_node_prerequisites_shape():
    nodes = [make_node(prerequisites=["K2"]), make_node(id="K2")]
    plan = kc.compile_plan(make_request(nodes=nodes))
    assert plan["order"] == ["K2", "K1"]
    assert kc.compile_plan(make_request())["status"] == "READY"  # prerequisites []
    node_missing = make_node()
    del node_missing["prerequisites"]
    assert_invalid(
        lambda: kc.compile_plan(make_request(nodes=[node_missing])),
        "Invalid prerequisites",
    )
    assert_invalid(
        lambda: kc.compile_plan(make_request(nodes=[make_node(prerequisites="K2")])),
        "Invalid prerequisites",
    )
    assert_invalid(
        lambda: kc.compile_plan(make_request(nodes=[make_node(prerequisites=[""])])),
        "Invalid prerequisites",
    )
    assert_invalid(
        lambda: kc.compile_plan(make_request(nodes=[make_node(prerequisites=[3])])),
        "Invalid prerequisites",
    )


def test_kc_36_compile_plan_node_relations():
    nodes = [
        make_node(relations=[{"type": "supports", "target": "K2"}]),
        make_node(id="K2"),
    ]
    assert kc.compile_plan(make_request(nodes=nodes))["status"] == "READY"
    assert_invalid(
        lambda: kc.compile_plan(make_request(nodes=[make_node(relations={})])),
        "relations must be a list",
    )
    assert_invalid(
        lambda: kc.compile_plan(
            make_request(nodes=[make_node(relations=[{"type": "causes", "target": "K2"}])])
        ),
        "Invalid semantic relation",
    )
    assert_invalid(
        lambda: kc.compile_plan(
            make_request(nodes=[make_node(relations=[{"type": "supports"}])])
        ),
        "Invalid semantic relation",
    )
    assert_invalid(
        lambda: kc.compile_plan(
            make_request(nodes=[make_node(relations=[{"type": "supports", "target": 5}])])
        ),
        "Invalid semantic relation",
    )
    assert_invalid(
        lambda: kc.compile_plan(
            make_request(
                nodes=[make_node(relations=[{"type": "supports", "target": "K99"}])]
            )
        ),
        "Unknown semantic relation target",
    )


# --------------------------------- compile_plan(): demonstrations and targets

def test_kc_37_compile_plan_demonstrations_shape():
    assert_invalid(
        lambda: kc.compile_plan(make_request(demonstrations={})),
        "demonstrations must be a list",
    )
    assert_invalid(
        lambda: kc.compile_plan(
            make_request(demonstrations=[demo_record(node_id="K99")])
        ),
        "Unknown demonstration node",
    )
    assert_invalid(
        lambda: kc.compile_plan(make_request(demonstrations=["not-a-record"])),
        "Unknown demonstration node",
    )


def test_kc_38_compile_plan_demonstration_must_be_independent_raw():
    plan = kc.compile_plan(make_request(demonstrations=[demo_record()]))
    assert plan["status"] == "READY"
    message = "Demonstration must contain an independent raw response"
    assert_invalid(
        lambda: kc.compile_plan(
            make_request(demonstrations=[demo_record(support="hint")])
        ),
        message,
    )
    assert_invalid(
        lambda: kc.compile_plan(
            make_request(demonstrations=[demo_record(result="assisted")])
        ),
        message,
    )
    assert_invalid(
        lambda: kc.compile_plan(
            make_request(demonstrations=[demo_record(response="")])
        ),
        message,
    )
    assert_invalid(
        lambda: kc.compile_plan(
            make_request(demonstrations=[demo_record(response="  ")])
        ),
        message,
    )
    record_no_response = demo_record()
    del record_no_response["response"]
    assert_invalid(
        lambda: kc.compile_plan(make_request(demonstrations=[record_no_response])),
        message,
    )


def test_kc_39_compile_plan_demonstrated_ids_need_records():
    plan = kc.compile_plan(
        make_request(demonstrations=[demo_record()], demonstrated_ids=["K1"])
    )
    assert plan["status"] == "READY"
    assert_invalid(
        lambda: kc.compile_plan(make_request(demonstrated_ids=["K1"])),
        "Unsubstantiated demonstrated_ids",
    )
    assert_invalid(
        lambda: kc.compile_plan(make_request(demonstrated_ids="K1")),
        "Unsubstantiated demonstrated_ids",
    )


def test_kc_40_compile_plan_target_ids_shape():
    assert_invalid(
        lambda: kc.compile_plan(make_request(target_ids="K1")),
        "Invalid target_ids",
    )
    assert_invalid(
        lambda: kc.compile_plan(make_request(target_ids=[1])),
        "Invalid target_ids",
    )
    assert_invalid(
        lambda: kc.compile_plan(make_request(target_ids=["K1", "K1"])),
        "Duplicate target IDs",
    )


def test_kc_41_compile_plan_default_target_selection():
    nodes = [
        make_node(id="K1", relevance="high"),
        make_node(id="K2", relevance="medium"),
        make_node(id="K3", relevance="low"),
        make_node(id="K4", relevance="high", in_scope=False),
        make_node(id="K5", relevance="high", source_status="identified"),
    ]
    request = {"task": "explain", "mode": "deep", "nodes": nodes}
    plan = kc.compile_plan(request)
    assert plan["target_ids"] == ["K1", "K2"]


# -------------------------------------- compile_plan(): traversal and status

def test_kc_42_compile_plan_diamond_post_order():
    nodes = [
        make_node(id="T", prerequisites=["A", "B"]),
        make_node(id="A", prerequisites=["C"]),
        make_node(id="B", prerequisites=["C"]),
        make_node(id="C"),
    ]
    plan = kc.compile_plan(make_request(nodes=nodes, target_ids=["T"]))
    assert plan["status"] == "READY"
    assert plan["order"] == ["C", "A", "B", "T"]
    assert plan["bridges"] == ["C", "A", "B"]
    assert plan["blocked"] == []
    assert plan["cycles"] == []
    assert set(plan["knowledge_levels"]) == {"T", "A", "B", "C"}
    assert set(plan["prerequisite_metadata"]) == {"T", "A", "B", "C"}


def test_kc_43_compile_plan_prerequisite_cycle_blocks_only_its_target():
    nodes = [
        make_node(id="K1", prerequisites=["K2"]),
        make_node(id="K2", prerequisites=["K1"]),
        make_node(id="K3"),
    ]
    plan = kc.compile_plan(make_request(nodes=nodes, target_ids=["K1", "K3"]))
    assert plan["status"] == "PARTIAL"
    assert plan["blocked"] == [
        {
            "target": "K1",
            "type": "prerequisite_cycle",
            "node": "K1",
            "cycle": ["K1", "K2", "K1"],
        }
    ]
    assert plan["cycles"] == [["K1", "K2", "K1"]]
    assert plan["order"] == ["K3"]


def test_kc_44_compile_plan_missing_source_blocked():
    plan = kc.compile_plan(
        make_request(nodes=[make_node(source_status="missing", locator="")])
    )
    assert plan["status"] == "BLOCKED"
    assert plan["order"] == []
    assert plan["blocked"] == [
        {"target": "K1", "type": "source_not_read", "node": "K1"}
    ]


def test_kc_45_compile_plan_prerequisite_outside_scope():
    nodes = [make_node(id="T", prerequisites=["P"]), make_node(id="P", in_scope=False)]
    plan = kc.compile_plan(make_request(nodes=nodes, target_ids=["T"]))
    assert plan["blocked"] == [{"target": "T", "type": "outside_scope", "node": "P"}]
    assert plan["status"] == "BLOCKED"


def test_kc_45_compile_plan_prerequisite_node_missing():
    nodes = [make_node(id="T", prerequisites=["K99"])]
    plan = kc.compile_plan(make_request(nodes=nodes, target_ids=["T"]))
    assert plan["blocked"] == [
        {"target": "T", "type": "missing_prerequisite_node", "node": "K99"}
    ]
    assert plan["status"] == "BLOCKED"


def test_kc_46_compile_plan_demonstrated_prerequisite_skipped():
    nodes = [make_node(id="T", prerequisites=["D"]), make_node(id="D")]
    demos = [demo_record(node_id="D")]
    plan = kc.compile_plan(
        make_request(nodes=nodes, target_ids=["T"], demonstrations=demos)
    )
    assert plan["status"] == "READY"
    assert plan["order"] == ["T"]
    assert plan["skipped_demonstrated"] == ["D"]
    assert plan["bridges"] == []


def test_kc_46_compile_plan_demonstrated_target_not_skipped():
    nodes = [make_node(id="T", prerequisites=["D"]), make_node(id="D")]
    demos = [demo_record(node_id="D")]
    plan = kc.compile_plan(
        make_request(nodes=nodes, target_ids=["D"], demonstrations=demos)
    )
    assert plan["order"] == ["D"]
    assert plan["skipped_demonstrated"] == []


def test_kc_47_compile_plan_extract_keeps_prerequisites_as_metadata():
    nodes = [make_node(id="K1", prerequisites=["K99"])]
    request = {
        "task": "extract",
        "mode": "extract",
        "target_ids": ["K1"],
        "nodes": nodes,
    }
    plan = kc.compile_plan(request)
    assert plan["status"] == "READY"
    assert plan["order"] == ["K1"]
    assert plan["blocked"] == []
    assert plan["prerequisite_metadata"] == {"K1": ["K99"]}


def test_kc_48_compile_plan_identified_node_map_provisional():
    nodes = [make_node(source_status="identified")]
    request = {"task": "map", "mode": "deep", "target_ids": ["K1"], "nodes": nodes}
    plan = kc.compile_plan(request)
    assert plan["status"] == "PROVISIONAL"
    assert plan["order"] == ["K1"]
    assert plan["blocked"] == []


def test_kc_48_compile_plan_identified_node_explain_blocked():
    nodes = [make_node(source_status="identified")]
    plan = kc.compile_plan(make_request(nodes=nodes))
    assert plan["blocked"] == [
        {"target": "K1", "type": "source_not_read", "node": "K1"}
    ]
    assert plan["status"] == "BLOCKED"


def test_kc_49_compile_plan_self_prerequisite_cycle():
    nodes = [make_node(prerequisites=["K1"])]
    plan = kc.compile_plan(make_request(nodes=nodes))
    assert plan["blocked"] == [
        {
            "target": "K1",
            "type": "prerequisite_cycle",
            "node": "K1",
            "cycle": ["K1", "K1"],
        }
    ]
    assert plan["cycles"] == [["K1", "K1"]]
    assert plan["status"] == "BLOCKED"


def test_kc_50_compile_plan_blocked_target_drops_whole_subtree():
    nodes = [
        make_node(id="T", prerequisites=["A", "B"]),
        make_node(id="A"),
        make_node(id="B", source_status="missing", locator=""),
    ]
    plan = kc.compile_plan(make_request(nodes=nodes, target_ids=["T"]))
    assert plan["order"] == []
    assert len(plan["blocked"]) == 1
    assert plan["blocked"][0]["target"] == "T"
    assert plan["blocked"][0]["node"] == "B"
    assert plan["status"] == "BLOCKED"


def test_kc_51_compile_plan_status_priority():
    # (1) All targets pass -> READY.
    assert kc.compile_plan(make_request())["status"] == "READY"
    # (2) Identified target at map + read target -> PROVISIONAL.
    nodes = [
        make_node(id="K1", source_status="identified"),
        make_node(id="K2"),
    ]
    plan = kc.compile_plan(
        {"task": "map", "mode": "deep", "target_ids": ["K1", "K2"], "nodes": nodes}
    )
    assert plan["status"] == "PROVISIONAL"
    # (3) One blocked + one passing target -> PARTIAL.
    nodes = [
        make_node(id="K1", source_status="missing", locator=""),
        make_node(id="K2"),
    ]
    plan = kc.compile_plan(make_request(nodes=nodes, target_ids=["K1", "K2"]))
    assert plan["status"] == "PARTIAL"
    # (4) No target passes -> BLOCKED.
    plan = kc.compile_plan(
        make_request(nodes=[make_node(source_status="missing", locator="")])
    )
    assert plan["status"] == "BLOCKED"


def test_kc_52_compile_plan_empty_request():
    plan = kc.compile_plan({"task": "explain", "mode": "deep"})
    assert plan["status"] == "BLOCKED"
    assert plan["order"] == []
    assert plan["blocked"] == []
    assert plan["target_ids"] == []
    assert plan["artifact_plan"] == []


# -------------------------------- compile_plan(): fast path and output shape

FAST_PATH_MESSAGE = (
    "Fast path must use validated content or assessment context, "
    "not recompile nodes"
)


def test_kc_53_compile_plan_fast_path_rejects_new_nodes_or_targets():
    assert_invalid(
        lambda: kc.compile_plan(
            {"task": "assess", "mode": "deep", "nodes": [make_node()]}
        ),
        FAST_PATH_MESSAGE,
    )
    assert_invalid(
        lambda: kc.compile_plan(
            {"task": "assess", "mode": "deep", "nodes": [], "target_ids": ["K1"]}
        ),
        FAST_PATH_MESSAGE,
    )
    assert_invalid(
        lambda: kc.compile_plan(
            {
                "task": "explain",
                "mode": "deep",
                "validated_content": True,
                "nodes": [make_node()],
            }
        ),
        FAST_PATH_MESSAGE,
    )


def test_kc_54_compile_plan_fast_path_ready():
    plan = kc.compile_plan({"task": "assess", "mode": "deep"})
    assert plan["status"] == "READY"
    assert plan["order"] == []
    assert plan["stages"] == kc.route("assess", "deep")
    assert [row["id"] for row in plan["artifact_plan"]] == ["RA-08"]
    plan = kc.compile_plan({"task": "explain", "mode": "deep", "validated_content": True})
    assert plan["status"] == "READY"
    assert plan["stages"] == kc.route("explain", "deep", validated_content=True)
    assert plan["reference_plan"] == kc.reference_plan(
        "explain", "deep", validated_content=True
    )


def test_kc_55_compile_plan_node_validation_precedes_fast_path_check():
    node = make_node(knowledge_level="L0")
    assert_invalid(
        lambda: kc.compile_plan(
            {
                "task": "explain",
                "mode": "deep",
                "validated_content": True,
                "nodes": [node],
            }
        ),
        "Invalid knowledge level",
    )


def test_kc_56_compile_plan_output_invariants():
    plan = kc.compile_plan(make_request())
    assert set(plan) == {
        "status", "task", "mode", "target_ids", "order", "bridges",
        "skipped_demonstrated", "blocked", "cycles", "knowledge_levels",
        "prerequisite_metadata", "artifact_plan", "stages", "reference_plan",
        "learner_level", "semantic_verified", "source_locators_verified",
    }
    assert plan["semantic_verified"] is False
    assert plan["source_locators_verified"] is False
    assert plan["task"] == "explain"
    assert plan["mode"] == "deep"


# ------------------------------------------------------------------------ CLI

def _run_kc_cli(input_path, output_path):
    return subprocess.run(
        [sys.executable, str(KC_PATH), "--input", str(input_path),
         "--output", str(output_path)],
        capture_output=True, text=True,
    )


def _write_json(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_kc_57_cli_success(tmp_path):
    src = tmp_path / "request.json"
    out = tmp_path / "plan.json"
    _write_json(src, make_request())
    before = src.read_bytes()
    result = _run_kc_cli(src, out)
    assert result.returncode == 0
    stdout = json.loads(result.stdout)
    assert stdout == {"ok": True, "status": "READY", "semantic_verified": False}
    plan = json.loads(out.read_text(encoding="utf-8"))
    assert plan["status"] == "READY"
    assert src.read_bytes() == before


def test_kc_57_cli_refuses_existing_output(tmp_path):
    src = tmp_path / "request.json"
    out = tmp_path / "plan.json"
    _write_json(src, make_request())
    out.write_text("already here", encoding="utf-8")
    result = _run_kc_cli(src, out)
    assert result.returncode == 1
    assert json.loads(result.stdout) == {"ok": False, "error": "Output must be a new file"}


def test_kc_57_cli_refuses_output_equal_to_input(tmp_path):
    src = tmp_path / "request.json"
    _write_json(src, make_request())
    result = _run_kc_cli(src, src)
    assert result.returncode == 1
    assert json.loads(result.stdout) == {"ok": False, "error": "Output must be a new file"}


def test_kc_57_cli_refuses_symlink_output(tmp_path):
    src = tmp_path / "request.json"
    real = tmp_path / "real.json"
    out = tmp_path / "plan.json"
    _write_json(src, make_request())
    real.write_text("{}", encoding="utf-8")
    out.symlink_to(real)
    result = _run_kc_cli(src, out)
    assert result.returncode == 1
    assert json.loads(result.stdout) == {"ok": False, "error": "Output must be a new file"}


def test_kc_58_cli_business_error(tmp_path):
    src = tmp_path / "request.json"
    out = tmp_path / "plan.json"
    _write_json(src, {"task": "bogus", "mode": "deep"})
    result = _run_kc_cli(src, out)
    assert result.returncode == 1
    assert json.loads(result.stdout) == {
        "ok": False,
        "error": "Invalid task/mode; clarify first",
    }


def test_kc_58_cli_malformed_json(tmp_path):
    src = tmp_path / "request.json"
    out = tmp_path / "plan.json"
    src.write_text("{not json", encoding="utf-8")
    result = _run_kc_cli(src, out)
    assert result.returncode == 1
    assert json.loads(result.stdout)["ok"] is False


def test_kc_58_cli_missing_input_file(tmp_path):
    result = _run_kc_cli(tmp_path / "does-not-exist.json", tmp_path / "plan.json")
    assert result.returncode == 1
    assert json.loads(result.stdout)["ok"] is False


# ------------------------------------------------------- Red Team regressions

def test_json_a02_cli_deeply_nested_json_fails_cleanly(tmp_path):
    src = tmp_path / "request.json"
    out = tmp_path / "plan.json"
    depth = 20_000
    src.write_text('{"a":' * depth + "1" + "}" * depth, encoding="utf-8")
    result = _run_kc_cli(src, out)
    assert result.returncode == 1
    assert json.loads(result.stdout) == {
        "ok": False,
        "error": "JSON input is nested too deeply",
    }
    assert "Traceback" not in result.stderr
    assert "RecursionError" not in result.stderr
    assert not out.exists()


def test_cp_a04_parse_json_rejects_duplicate_keys():
    assert_invalid(
        lambda: kc.parse_json('{"task": "explain", "task": "extract"}'),
        "Duplicate JSON key: task",
    )
    assert_invalid(
        lambda: kc.parse_json('{"outer": {"mode": "deep", "mode": "extract"}}'),
        "Duplicate JSON key: mode",
    )


def test_cp_a04_cli_rejects_duplicate_keys(tmp_path):
    src = tmp_path / "request.json"
    out = tmp_path / "plan.json"
    src.write_text(
        '{"task": "explain", "mode": "deep", "mode": "extract"}',
        encoding="utf-8",
    )
    result = _run_kc_cli(src, out)
    assert result.returncode == 1
    assert json.loads(result.stdout) == {
        "ok": False,
        "error": "Duplicate JSON key: mode",
    }
    assert not out.exists()


def test_cp_a05_read_json_file_rejects_oversize_input(monkeypatch, tmp_path):
    src = tmp_path / "request.json"
    src.write_text('{"task": "explain"}', encoding="utf-8")
    monkeypatch.setattr(kc, "MAX_JSON_BYTES", 4)
    assert_invalid(
        lambda: kc.read_json_file(src),
        "JSON input exceeds the 4-byte limit",
    )


def test_cp_a05_cli_rejects_oversize_input(tmp_path):
    src = tmp_path / "request.json"
    out = tmp_path / "plan.json"
    _write_json(src, make_request(padding="x" * kc.MAX_JSON_BYTES))
    result = _run_kc_cli(src, out)
    assert result.returncode == 1
    assert json.loads(result.stdout) == {
        "ok": False,
        "error": f"JSON input exceeds the {kc.MAX_JSON_BYTES}-byte limit",
    }
    assert not out.exists()
