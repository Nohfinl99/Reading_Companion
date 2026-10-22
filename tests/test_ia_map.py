"""Unit tests for skills/sid-reading-companion/scripts/ia_map.py.

Implemented from specs/spec_compiler_ia.md (agent B2). Each test function
name carries its spec case ID (IA-01 ... IA-35). Negative cases assert both
the exception type (InvalidMap) and the exact error message from the code.
The module under test is loaded in place from the repo tree.
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "skills" / "sid-reading-companion" / "scripts"
IA_PATH = SCRIPTS_DIR / "ia_map.py"


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ia = _load_module("ia_map", IA_PATH)
InvalidMap = ia.InvalidMap


def make_ia_node(**overrides):
    """Base valid IA node (spec section 4.4)."""
    node = {
        "id": "A",
        "label_vi": "Agent",
        "definition": "Thành phần quyết định hành động theo mục tiêu.",
        "source_status": "read",
        "source_locators": ["p.549"],
        "knowledge_level": "L1",
        "in_scope": True,
    }
    node.update(overrides)
    return node


def node_b(**overrides):
    base = {
        "id": "B",
        "label_vi": "Bộ công cụ",
        "definition": "Tập công cụ khả dụng trong phạm vi đang xét.",
    }
    base.update(overrides)
    return make_ia_node(**base)


def base_edge(**overrides):
    """Base conceptual edge of the minimal map (spec section 4.5)."""
    edge = {
        "id": "E1",
        "from": "A",
        "to": "B",
        "label_vi": "hỗ trợ",
        "relation_type": "supports",
        "basis": "source_explicit",
        "source_locators": ["p.550"],
    }
    edge.update(overrides)
    return edge


def learning_edge(**overrides):
    """Base learning_order edge (spec section 4.5)."""
    edge = {
        "id": "E2",
        "from": "A",
        "to": "B",
        "label_vi": "học trước",
        "relation_type": "learning_prerequisite",
        "basis": "source_explicit",
        "reason": "Cần hiểu A trước khi học B",
        "source_locators": ["p.549"],
    }
    edge.update(overrides)
    return edge


def make_map(**overrides):
    """Base valid IA map (spec section 4.5)."""
    data = {
        "goal": "Hiểu quan hệ giữa agent và bộ công cụ",
        "views": ["conceptual"],
        "nodes": [make_ia_node(), node_b()],
        "relations": [base_edge()],
        "learning_order": [],
    }
    data.update(overrides)
    return data


def assert_invalid(callable_, message):
    with pytest.raises(InvalidMap) as excinfo:
        callable_()
    assert str(excinfo.value) == message


# ------------------------------------------------------------------- acyclic()

def test_ia_01_acyclic_dag():
    assert ia.acyclic({"A", "B"}, []) is True
    assert ia.acyclic({"A", "B"}, [{"from": "A", "to": "B"}]) is True
    diamond = [
        {"from": "A", "to": "B"}, {"from": "A", "to": "C"},
        {"from": "B", "to": "D"}, {"from": "C", "to": "D"},
    ]
    assert ia.acyclic({"A", "B", "C", "D"}, diamond) is True
    chain = [
        {"from": "A", "to": "B"}, {"from": "B", "to": "C"},
        {"from": "C", "to": "D"},
    ]
    assert ia.acyclic({"A", "B", "C", "D"}, chain) is True


def test_ia_02_acyclic_detects_cycles():
    two = [{"from": "A", "to": "B"}, {"from": "B", "to": "A"}]
    assert ia.acyclic({"A", "B"}, two) is False
    three = [
        {"from": "A", "to": "B"}, {"from": "B", "to": "C"},
        {"from": "C", "to": "A"},
    ]
    assert ia.acyclic({"A", "B", "C"}, three) is False
    branch = [
        {"from": "A", "to": "B"}, {"from": "C", "to": "D"},
        {"from": "D", "to": "C"},
    ]
    assert ia.acyclic({"A", "B", "C", "D"}, branch) is False


def test_ia_03_acyclic_self_loop():
    assert ia.acyclic({"A"}, [{"from": "A", "to": "A"}]) is False


# --------------------------------------------------------------------- label()

def test_ia_04_label_escapes_mermaid_specials():
    assert ia.label('a#b&c"d<e>f|g') == "a#35;b#38;c#quot;d#60;e#62;f#124;g"
    assert ia.label("#") == "#35;"
    assert ia.label("&") == "#38;"
    assert ia.label('"') == "#quot;"
    assert ia.label("<") == "#60;"
    assert ia.label(">") == "#62;"
    assert ia.label("|") == "#124;"


def test_ia_05_label_newlines_become_spaces():
    assert ia.label("x\ny\rz") == "x y z"
    assert ia.label("a\r\nb") == "a  b"


def test_ia_06_label_keeps_unicode_and_plain_text():
    assert ia.label("Tiếng Việt — đệ quy") == "Tiếng Việt — đệ quy"
    assert ia.label("") == ""
    # Pre-existing entities are escaped again (current behavior).
    assert ia.label("#35;") == "#35;35;"


# ------------------------------------------------------- compile_map(): basics

def test_ia_07_compile_map_minimal_conceptual():
    result = ia.compile_map(make_map())
    assert result["views"] == {
        "conceptual": (
            "flowchart LR\n"
            '    A["Agent"]\n'
            '    B["Bộ công cụ"]\n'
            '    A -->|"hỗ trợ"| B'
        )
    }
    assert result["edges"] == {"conceptual": [base_edge()], "learning": []}
    assert result["unresolved"] == []
    assert result["warnings"] == [
        "Select a focused subset if the diagram is hard to read."
    ]
    assert result["semantic_verified"] is False
    assert result["source_locators_verified"] is False
    assert result["mermaid_render_verified"] is False
    assert result["learner_evidence"] is False


def test_ia_08_compile_map_object_and_goal():
    assert_invalid(lambda: ia.compile_map([1, 2]), "Map must be an object")
    data = make_map()
    del data["goal"]
    assert_invalid(lambda: ia.compile_map(data), "Missing learning goal")
    assert_invalid(
        lambda: ia.compile_map(make_map(goal="  ")), "Missing learning goal"
    )


def test_ia_09_compile_map_views_validation():
    data = make_map()
    del data["views"]
    assert_invalid(lambda: ia.compile_map(data), "Invalid views")
    assert_invalid(lambda: ia.compile_map(make_map(views=[])), "Invalid views")
    assert_invalid(
        lambda: ia.compile_map(make_map(views="conceptual")), "Invalid views"
    )
    assert_invalid(lambda: ia.compile_map(make_map(views=["foo"])), "Invalid views")
    assert_invalid(
        lambda: ia.compile_map(make_map(views=["conceptual", "conceptual"])),
        "Invalid views",
    )


def test_ia_10_compile_map_node_batch_limits():
    nodes = [make_ia_node(id=f"N{i:03d}") for i in range(1, 257)]
    result = ia.compile_map(make_map(nodes=nodes, relations=[]))
    assert "conceptual" in result["views"]
    nodes_257 = [make_ia_node(id=f"N{i:03d}") for i in range(1, 258)]
    assert_invalid(
        lambda: ia.compile_map(make_map(nodes=nodes_257, relations=[])),
        "Invalid node batch",
    )
    data = make_map()
    del data["nodes"]
    assert_invalid(lambda: ia.compile_map(data), "Invalid node batch")
    assert_invalid(
        lambda: ia.compile_map(make_map(nodes=[], relations=[])),
        "Invalid node batch",
    )
    assert_invalid(
        lambda: ia.compile_map(make_map(nodes={}, relations=[])),
        "Invalid node batch",
    )


def test_ia_11_compile_map_node_must_be_object():
    assert_invalid(
        lambda: ia.compile_map(make_map(nodes=["A"], relations=[])),
        "Invalid node",
    )


@pytest.mark.parametrize("bad_id", ["1A", "A-B", "A B", ""])
def test_ia_12_compile_map_node_id_shape(bad_id):
    assert_invalid(
        lambda: ia.compile_map(
            make_map(nodes=[make_ia_node(id=bad_id)], relations=[])
        ),
        "Invalid/duplicate node ID",
    )


def test_ia_12_compile_map_node_id_duplicate_and_missing():
    nodes = [make_ia_node(), make_ia_node()]
    assert_invalid(
        lambda: ia.compile_map(make_map(nodes=nodes, relations=[])),
        "Invalid/duplicate node ID",
    )
    node_no_id = make_ia_node()
    del node_no_id["id"]
    assert_invalid(
        lambda: ia.compile_map(make_map(nodes=[node_no_id], relations=[])),
        "Invalid/duplicate node ID",
    )


@pytest.mark.parametrize("ok_id", ["Ending", "EndNode"])
def test_ia_13_compile_map_end_like_ids_allowed(ok_id):
    result = ia.compile_map(
        make_map(nodes=[make_ia_node(id=ok_id)], relations=[])
    )
    assert "conceptual" in result["views"]


@pytest.mark.parametrize("bad_id", ["end", "End", "END"])
def test_ia_13_compile_map_reserved_end_id(bad_id):
    assert_invalid(
        lambda: ia.compile_map(
            make_map(nodes=[make_ia_node(id=bad_id)], relations=[])
        ),
        "Reserved Mermaid node ID",
    )


def test_ia_14_compile_map_label_and_definition_required():
    node = make_ia_node()
    del node["label_vi"]
    assert_invalid(
        lambda: ia.compile_map(make_map(nodes=[node], relations=[])),
        "Missing label/definition",
    )
    assert_invalid(
        lambda: ia.compile_map(
            make_map(nodes=[make_ia_node(label_vi=" ")], relations=[])
        ),
        "Missing label/definition",
    )
    node = make_ia_node()
    del node["definition"]
    assert_invalid(
        lambda: ia.compile_map(make_map(nodes=[node], relations=[])),
        "Missing label/definition",
    )
    assert_invalid(
        lambda: ia.compile_map(
            make_map(nodes=[make_ia_node(definition="")], relations=[])
        ),
        "Missing label/definition",
    )


@pytest.mark.parametrize(
    "node_overrides",
    [
        {"source_status": "identified"},
        {"source_status": "missing"},
        {"source_locators": []},
        {"source_locators": [""]},
        {"source_locators": "p.10"},
    ],
)
def test_ia_15_compile_map_node_requires_read_source_with_locators(node_overrides):
    assert_invalid(
        lambda: ia.compile_map(
            make_map(nodes=[make_ia_node(**node_overrides)], relations=[])
        ),
        "Diagram claim requires read source with locators",
    )


def test_ia_15_compile_map_node_missing_locators_field():
    node = make_ia_node()
    del node["source_locators"]
    assert_invalid(
        lambda: ia.compile_map(make_map(nodes=[node], relations=[])),
        "Diagram claim requires read source with locators",
    )


def test_ia_16_compile_map_node_knowledge_level():
    assert_invalid(
        lambda: ia.compile_map(
            make_map(nodes=[make_ia_node(knowledge_level="L5")], relations=[])
        ),
        "Invalid knowledge task level",
    )
    node = make_ia_node()
    del node["knowledge_level"]
    assert_invalid(
        lambda: ia.compile_map(make_map(nodes=[node], relations=[])),
        "Invalid knowledge task level",
    )


@pytest.mark.parametrize("bad_scope", [False, 1])
def test_ia_17_compile_map_node_in_scope_must_be_true(bad_scope):
    assert_invalid(
        lambda: ia.compile_map(
            make_map(nodes=[make_ia_node(in_scope=bad_scope)], relations=[])
        ),
        "Node outside selected scope",
    )


def test_ia_17_compile_map_node_in_scope_missing():
    node = make_ia_node()
    del node["in_scope"]
    assert_invalid(
        lambda: ia.compile_map(make_map(nodes=[node], relations=[])),
        "Node outside selected scope",
    )


# ------------------------------------------------------- compile_map(): edges

def test_ia_18_compile_map_edge_list_and_object_shape():
    assert_invalid(
        lambda: ia.compile_map(make_map(relations={})), "Invalid edge list"
    )
    assert_invalid(
        lambda: ia.compile_map(make_map(learning_order="x")), "Invalid edge list"
    )
    assert_invalid(
        lambda: ia.compile_map(make_map(relations=["E1"])), "Invalid edge"
    )


def test_ia_19_compile_map_edge_id_required_unique_across_fields():
    edge_no_id = base_edge()
    del edge_no_id["id"]
    assert_invalid(
        lambda: ia.compile_map(make_map(relations=[edge_no_id])),
        "Duplicate/missing edge ID",
    )
    assert_invalid(
        lambda: ia.compile_map(make_map(relations=[base_edge(id="")])),
        "Duplicate/missing edge ID",
    )
    dup = base_edge(id="E1", **{"from": "B", "to": "A"})
    assert_invalid(
        lambda: ia.compile_map(make_map(relations=[base_edge(), dup])),
        "Duplicate/missing edge ID",
    )
    # Same ID across relations and learning_order is still a duplicate.
    assert_invalid(
        lambda: ia.compile_map(make_map(learning_order=[learning_edge(id="E1")])),
        "Duplicate/missing edge ID",
    )


def test_ia_20_compile_map_edge_endpoints_must_exist():
    assert_invalid(
        lambda: ia.compile_map(make_map(relations=[base_edge(to="Z")])),
        "Unknown edge endpoint",
    )
    assert_invalid(
        lambda: ia.compile_map(make_map(relations=[base_edge(**{"from": "Z"})])),
        "Unknown edge endpoint",
    )
    edge_no_from = base_edge()
    del edge_no_from["from"]
    assert_invalid(
        lambda: ia.compile_map(make_map(relations=[edge_no_from])),
        "Unknown edge endpoint",
    )


def test_ia_21_compile_map_edge_label_and_basis():
    edge_no_label = base_edge()
    del edge_no_label["label_vi"]
    assert_invalid(
        lambda: ia.compile_map(make_map(relations=[edge_no_label])),
        "Missing edge label",
    )
    assert_invalid(
        lambda: ia.compile_map(make_map(relations=[base_edge(label_vi=" ")])),
        "Missing edge label",
    )
    edge_no_basis = base_edge()
    del edge_no_basis["basis"]
    assert_invalid(
        lambda: ia.compile_map(make_map(relations=[edge_no_basis])),
        "Missing/invalid edge basis",
    )
    assert_invalid(
        lambda: ia.compile_map(make_map(relations=[base_edge(basis="guess")])),
        "Missing/invalid edge basis",
    )


@pytest.mark.parametrize(
    "relation_type",
    ["is_a", "part_of", "supports", "contrasts", "limits",
     "references", "conflicts", "depends_on"],
)
def test_ia_22_compile_map_conceptual_relation_types(relation_type):
    result = ia.compile_map(
        make_map(relations=[base_edge(relation_type=relation_type)])
    )
    assert len(result["edges"]["conceptual"]) == 1


@pytest.mark.parametrize("relation_type", ["causes", "suggested_order"])
def test_ia_22_compile_map_conceptual_relation_rejected(relation_type):
    assert_invalid(
        lambda: ia.compile_map(
            make_map(relations=[base_edge(relation_type=relation_type)])
        ),
        "Invalid conceptual relation",
    )


def test_ia_23_compile_map_pedagogical_edge_not_in_relations():
    assert_invalid(
        lambda: ia.compile_map(
            make_map(relations=[base_edge(basis="pedagogical_proposal")])
        ),
        "Pedagogical edges belong in learning_order",
    )


def test_ia_24_compile_map_learning_edge_valid_forms():
    result = ia.compile_map(
        make_map(views=["learning"], relations=[], learning_order=[learning_edge()])
    )
    assert len(result["edges"]["learning"]) == 1
    suggested = learning_edge(
        id="E3", relation_type="suggested_order",
        basis="pedagogical_proposal", source_locators=[],
    )
    result = ia.compile_map(
        make_map(views=["learning"], relations=[], learning_order=[suggested])
    )
    assert len(result["edges"]["learning"]) == 1


def test_ia_24_compile_map_learning_edge_rejections():
    assert_invalid(
        lambda: ia.compile_map(
            make_map(learning_order=[learning_edge(relation_type="supports")])
        ),
        "Invalid learning relation",
    )
    edge_no_reason = learning_edge()
    del edge_no_reason["reason"]
    assert_invalid(
        lambda: ia.compile_map(make_map(learning_order=[edge_no_reason])),
        "Learning relation needs reason",
    )
    assert_invalid(
        lambda: ia.compile_map(
            make_map(learning_order=[learning_edge(reason=" ")])
        ),
        "Learning relation needs reason",
    )
    assert_invalid(
        lambda: ia.compile_map(
            make_map(
                learning_order=[
                    learning_edge(relation_type="suggested_order",
                                  basis="source_explicit")
                ]
            )
        ),
        "Suggested order must be labelled proposal",
    )


@pytest.mark.parametrize(
    "locators", ["p.10", ["p.10", ""], [5]]
)
def test_ia_25_compile_map_edge_locators_shape(locators):
    assert_invalid(
        lambda: ia.compile_map(
            make_map(relations=[base_edge(source_locators=locators)])
        ),
        "Invalid edge locators",
    )


def test_ia_26_compile_map_source_based_edge_requires_locator():
    edge_no_locators = base_edge()
    del edge_no_locators["source_locators"]
    assert_invalid(
        lambda: ia.compile_map(make_map(relations=[edge_no_locators])),
        "Source-based edge requires locator",
    )
    assert_invalid(
        lambda: ia.compile_map(
            make_map(
                relations=[
                    base_edge(basis="source_interpretation", source_locators=[])
                ]
            )
        ),
        "Source-based edge requires locator",
    )


def test_ia_26_compile_map_non_source_edge_may_omit_locators():
    suggested = learning_edge(
        relation_type="suggested_order", basis="pedagogical_proposal",
        source_locators=[],
    )
    result = ia.compile_map(
        make_map(views=["learning"], relations=[], learning_order=[suggested])
    )
    assert len(result["edges"]["learning"]) == 1


def test_ia_27_compile_map_unresolved_edge_separated():
    unresolved_edge = base_edge(
        id="E2", **{"from": "B", "to": "A"},
        relation_type="references", basis="unresolved",
    )
    del unresolved_edge["source_locators"]
    result = ia.compile_map(make_map(relations=[base_edge(), unresolved_edge]))
    assert len(result["unresolved"]) == 1
    recorded = result["unresolved"][0]
    assert recorded["view"] == "conceptual"
    assert recorded["id"] == "E2"
    assert recorded["relation_type"] == "references"
    assert [e["id"] for e in result["edges"]["conceptual"]] == ["E1"]
    assert result["views"]["conceptual"].count("-->|") == 1


def test_ia_28_compile_map_learning_cycle_rejected():
    edges = [
        learning_edge(id="E2"),
        learning_edge(id="E3", **{"from": "B", "to": "A"}),
    ]
    assert_invalid(
        lambda: ia.compile_map(
            make_map(views=["learning"], relations=[], learning_order=edges)
        ),
        "Learning-order cycle; review affected branch before rendering",
    )


def test_ia_29_compile_map_conceptual_references_cycle_allowed():
    edges = [
        base_edge(relation_type="references"),
        base_edge(id="E2", **{"from": "B", "to": "A"},
                  relation_type="references"),
    ]
    result = ia.compile_map(make_map(relations=edges))
    assert len(result["edges"]["conceptual"]) == 2
    diagram = result["views"]["conceptual"]
    assert 'A -->|"hỗ trợ"| B' in diagram
    assert 'B -->|"hỗ trợ"| A' in diagram


def test_ia_30_compile_map_edge_qualifier_by_basis():
    interpreted = base_edge(basis="source_interpretation")
    result = ia.compile_map(make_map(relations=[interpreted]))
    assert '-->|"diễn giải: hỗ trợ"|' in result["views"]["conceptual"]
    suggested = learning_edge(
        relation_type="suggested_order", basis="pedagogical_proposal",
        source_locators=[],
    )
    result = ia.compile_map(
        make_map(views=["learning"], relations=[], learning_order=[suggested])
    )
    assert '-->|"đề xuất: học trước"|' in result["views"]["learning"]


def test_ia_31_compile_map_labels_escaped_in_diagram():
    nodes = [make_ia_node(label_vi="A|B"), node_b()]
    result = ia.compile_map(make_map(nodes=nodes))
    assert '    A["A#124;B"]' in result["views"]["conceptual"]
    nodes = [make_ia_node(label_vi='Mô hình "X"'), node_b()]
    result = ia.compile_map(make_map(nodes=nodes))
    assert "#quot;X#quot;" in result["views"]["conceptual"]
    result = ia.compile_map(make_map(relations=[base_edge(label_vi="a#b")]))
    assert "a#35;b" in result["views"]["conceptual"]


def test_ia_32_compile_map_both_edge_fields_always_validated():
    # Valid learning edge is projected even when the learning view is not asked.
    result = ia.compile_map(make_map(learning_order=[learning_edge()]))
    assert [e["id"] for e in result["edges"]["learning"]] == ["E2"]
    assert set(result["views"]) == {"conceptual"}
    # An invalid learning edge fails even when the learning view is not asked.
    edge_no_reason = learning_edge()
    del edge_no_reason["reason"]
    assert_invalid(
        lambda: ia.compile_map(make_map(learning_order=[edge_no_reason])),
        "Learning relation needs reason",
    )


def test_ia_33_compile_map_all_nodes_in_every_view():
    nodes = [make_ia_node(), node_b(), make_ia_node(id="C", label_vi="Chu trình")]
    result = ia.compile_map(
        make_map(views=["conceptual", "learning"], nodes=nodes,
                 relations=[], learning_order=[])
    )
    assert set(result["views"]) == {"conceptual", "learning"}
    for diagram in result["views"].values():
        assert 'A["Agent"]' in diagram
        assert 'B["Bộ công cụ"]' in diagram
        assert 'C["Chu trình"]' in diagram


# ------------------------------------------------------------------------ CLI

def _run_ia_cli(input_path, output_path):
    return subprocess.run(
        [sys.executable, str(IA_PATH), "--input", str(input_path),
         "--output", str(output_path)],
        capture_output=True, text=True,
    )


def test_ia_34_cli_success(tmp_path):
    src = tmp_path / "map.json"
    out = tmp_path / "result.json"
    src.write_text(json.dumps(make_map(), ensure_ascii=False), encoding="utf-8")
    result = _run_ia_cli(src, out)
    assert result.returncode == 0
    assert json.loads(result.stdout) == {"ok": True, "semantic_verified": False}
    payload = json.loads(out.read_text(encoding="utf-8"))
    for key in ("views", "edges", "unresolved", "warnings"):
        assert key in payload


def test_ia_35_cli_refuses_existing_output(tmp_path):
    src = tmp_path / "map.json"
    out = tmp_path / "result.json"
    src.write_text(json.dumps(make_map(), ensure_ascii=False), encoding="utf-8")
    out.write_text("{}", encoding="utf-8")
    result = _run_ia_cli(src, out)
    assert result.returncode == 1
    assert json.loads(result.stdout) == {
        "ok": False, "error": "Output must be a new file",
    }


def test_ia_35_cli_refuses_output_equal_to_input(tmp_path):
    src = tmp_path / "map.json"
    src.write_text(json.dumps(make_map(), ensure_ascii=False), encoding="utf-8")
    result = _run_ia_cli(src, src)
    assert result.returncode == 1
    assert json.loads(result.stdout) == {
        "ok": False, "error": "Output must be a new file",
    }


def test_ia_35_cli_business_error_missing_goal(tmp_path):
    src = tmp_path / "map.json"
    out = tmp_path / "result.json"
    bad = make_map()
    del bad["goal"]
    src.write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")
    result = _run_ia_cli(src, out)
    assert result.returncode == 1
    assert json.loads(result.stdout) == {
        "ok": False, "error": "Missing learning goal",
    }


def test_ia_35_cli_malformed_json(tmp_path):
    src = tmp_path / "map.json"
    out = tmp_path / "result.json"
    src.write_text("{not json", encoding="utf-8")
    result = _run_ia_cli(src, out)
    assert result.returncode == 1
    assert json.loads(result.stdout)["ok"] is False


# ------------------------------------------------------- Red Team regression
# IA-A02: a learning_order cycle used to slip through whenever the learning
# view was not requested, even though learning edges are always emitted.

def test_ia_a02_learning_cycle_rejected_without_learning_view():
    edges = [
        learning_edge(id="E2"),
        learning_edge(id="E3", **{"from": "B", "to": "A"}),
    ]
    assert_invalid(
        lambda: ia.compile_map(make_map(relations=[], learning_order=edges)),
        "Learning-order cycle; review affected branch before rendering",
    )


def test_ia_a02_learning_cycle_rejected_with_partial_views():
    edges = [
        learning_edge(id="E2"),
        learning_edge(id="E3", **{"from": "B", "to": "A"}),
    ]
    assert_invalid(
        lambda: ia.compile_map(
            make_map(views=["conceptual"], relations=[], learning_order=edges)
        ),
        "Learning-order cycle; review affected branch before rendering",
    )


# IA-A03: node IDs that are Mermaid keywords used to be accepted and broke
# the emitted diagram syntax; only "end" was reserved.

@pytest.mark.parametrize(
    "bad_id",
    ["subgraph", "flowchart", "graph", "class", "classDef", "style", "click",
     "Subgraph", "CLASS"],
)
def test_ia_a03_reserved_mermaid_keyword_ids(bad_id):
    assert_invalid(
        lambda: ia.compile_map(make_map(nodes=[make_ia_node(id=bad_id), node_b()])),
        "Reserved Mermaid node ID",
    )
