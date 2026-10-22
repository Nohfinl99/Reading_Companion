"""Test cho checkpoint.py — theo spec_checkpoint_session.md, case CP-01…CP-81.

Quy ước: mỗi test chứa ID của spec trong tên; case âm assert cả loại exception
(InvalidCheckpoint) lẫn thông điệp lỗi chính xác (so khớp toàn bộ chuỗi).
"""
import json
from copy import deepcopy
from datetime import datetime, timedelta, timezone

import pytest


def assert_raises(exc_type, message, fn, *args, **kwargs):
    with pytest.raises(exc_type) as excinfo:
        fn(*args, **kwargs)
    assert str(excinfo.value) == message


def future_iso(days=1):
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


# ===========================================================================
# 2.1 validate_currency — CP-01…CP-19
# ===========================================================================

def test_cp_19_currency_confirmed_record_passes(cp, fx):
    record = fx.curr()
    assert cp.validate_currency(record) is record


def test_cp_01_currency_invalid_sensitivity(cp, fx):
    record = fx.curr()
    record["sensitivity"] = "live"
    assert_raises(cp.InvalidCheckpoint, "Invalid currency sensitivity",
                  cp.validate_currency, record)


def test_cp_02_currency_invalid_status(cp, fx):
    record = fx.curr()
    record["status"] = "verified"
    assert_raises(cp.InvalidCheckpoint, "Invalid currency status",
                  cp.validate_currency, record)


@pytest.mark.parametrize("key", ["rationale", "original_claim",
                                 "current_conclusion", "applicability"])
def test_cp_03_currency_text_fields_required(cp, fx, key):
    record = fx.curr()
    record[key] = "  "
    assert_raises(cp.InvalidCheckpoint, f"currency needs {key}",
                  cp.validate_currency, record)


def test_cp_03_currency_text_field_missing(cp, fx):
    record = fx.curr()
    del record["rationale"]
    assert_raises(cp.InvalidCheckpoint, "currency needs rationale",
                  cp.validate_currency, record)


def test_cp_04_currency_assessed_at_in_future(cp, fx):
    record = fx.curr()
    record["assessed_at"] = future_iso(1)
    assert_raises(cp.InvalidCheckpoint, "assessed_at cannot be in the future",
                  cp.validate_currency, record)


def test_cp_05_currency_assessed_at_garbage(cp, fx):
    record = fx.curr()
    record["assessed_at"] = "abc"
    assert_raises(cp.InvalidCheckpoint, "Invalid assessed_at timestamp",
                  cp.validate_currency, record)


def test_cp_05_currency_assessed_at_without_timezone(cp, fx):
    record = fx.curr()
    record["assessed_at"] = "2026-01-02T00:00:00"
    assert_raises(cp.InvalidCheckpoint, "assessed_at needs timezone",
                  cp.validate_currency, record)


def test_cp_05_currency_assessed_at_without_timezone_safety_pin(cp, fx):
    # Safety pin độc lập cho CP-05: input thiếu timezone (không phải input
    # rác) phải bị chặn bằng đúng thông điệp chẩn đoán của guard chuyên biệt.
    record = fx.curr()
    record["assessed_at"] = "2026-01-02T00:00:00"
    assert_raises(cp.InvalidCheckpoint, "assessed_at needs timezone",
                  cp.validate_currency, record)


def test_cp_06_currency_verified_after_assessed(cp, fx):
    record = fx.curr()
    record["verified_at"] = "2026-01-02T12:00:00+07:00"
    assert_raises(cp.InvalidCheckpoint, "verified_at must not follow assessed_at",
                  cp.validate_currency, record)


def test_cp_07_currency_evidence_must_be_list(cp, fx):
    record = fx.curr()
    record["evidence"] = {"url": "https://example.org/doc"}
    assert_raises(cp.InvalidCheckpoint, "currency evidence must be a list",
                  cp.validate_currency, record)


@pytest.mark.parametrize("url", ["ftp://example.org/doc", "example.org/doc"])
def test_cp_08_currency_evidence_bad_url(cp, fx, url):
    record = fx.curr()
    record["evidence"][0]["url"] = url
    assert_raises(cp.InvalidCheckpoint, "Invalid currency evidence URL",
                  cp.validate_currency, record)


@pytest.mark.parametrize("key", ["title", "finding"])
def test_cp_09_currency_evidence_text_required(cp, fx, key):
    record = fx.curr()
    record["evidence"][0][key] = ""
    assert_raises(cp.InvalidCheckpoint, f"Evidence needs {key}",
                  cp.validate_currency, record)


def test_cp_10_currency_evidence_checked_after_assessed(cp, fx):
    record = fx.curr()
    record["evidence"][0]["checked_at"] = "2026-01-03T00:00:00+07:00"
    assert_raises(cp.InvalidCheckpoint,
                  "Evidence checked_at must not follow assessed_at",
                  cp.validate_currency, record)


def test_cp_10_currency_evidence_checked_after_verified(cp, fx):
    record = fx.curr()
    record["evidence"][0]["checked_at"] = "2026-01-01T18:00:00+07:00"
    assert_raises(cp.InvalidCheckpoint,
                  "Evidence checked_at must not follow verified_at",
                  cp.validate_currency, record)


def test_cp_11_currency_confirmed_needs_verified_at(cp, fx):
    record = fx.curr()
    record["verified_at"] = None
    assert_raises(cp.InvalidCheckpoint,
                  "Verified currency needs timestamp and evidence",
                  cp.validate_currency, record)


def test_cp_11_currency_confirmed_needs_evidence(cp, fx):
    record = fx.curr()
    record["evidence"] = []
    assert_raises(cp.InvalidCheckpoint,
                  "Verified currency needs timestamp and evidence",
                  cp.validate_currency, record)


def test_cp_12_currency_changed_with_evidence_passes(cp, fx):
    record = fx.curr()
    record["status"] = "changed"
    assert cp.validate_currency(record) is record


def test_cp_12_currency_changed_needs_evidence(cp, fx):
    record = fx.curr()
    record["status"] = "changed"
    record["evidence"] = []
    assert_raises(cp.InvalidCheckpoint,
                  "Verified currency needs timestamp and evidence",
                  cp.validate_currency, record)


def _reduced_record(fx, **over):
    record = fx.curr()
    record.update({"verified_at": None, "evidence": [], "review_after": None})
    record.update(over)
    return record


def test_cp_13_currency_not_checked_passes(cp, fx):
    record = _reduced_record(fx, status="not_checked")
    assert cp.validate_currency(record) is record


def test_cp_13_currency_not_checked_with_evidence(cp, fx):
    record = _reduced_record(fx, status="not_checked",
                             evidence=fx.curr()["evidence"])
    # evidence hợp lệ về format nhưng not_checked cấm có evidence; checked_at
    # của evidence cũng phải không mâu thuẫn với verified_at=None.
    assert_raises(cp.InvalidCheckpoint, "not_checked cannot claim verification",
                  cp.validate_currency, record)


def test_cp_13_currency_not_checked_with_verified_at(cp, fx):
    record = _reduced_record(fx, status="not_checked",
                             verified_at="2026-01-01T12:00:00+07:00")
    assert_raises(cp.InvalidCheckpoint, "not_checked cannot claim verification",
                  cp.validate_currency, record)


def test_cp_14_currency_stable_core_passes(cp, fx):
    record = _reduced_record(fx, status="stable_core", sensitivity="stable")
    assert cp.validate_currency(record) is record


def test_cp_14_currency_stable_core_needs_stable_sensitivity(cp, fx):
    record = _reduced_record(fx, status="stable_core", sensitivity="dynamic")
    assert_raises(cp.InvalidCheckpoint, "stable_core needs stable sensitivity",
                  cp.validate_currency, record)


def test_cp_15_currency_historical_passes(cp, fx):
    record = _reduced_record(fx, status="historical", sensitivity="historical")
    assert cp.validate_currency(record) is record


def test_cp_15_currency_historical_needs_historical_sensitivity(cp, fx):
    record = _reduced_record(fx, status="historical", sensitivity="dynamic")
    assert_raises(cp.InvalidCheckpoint,
                  "historical needs historical sensitivity",
                  cp.validate_currency, record)


def test_cp_16_currency_review_after_must_follow_assessed(cp, fx):
    record = fx.curr()
    record["review_after"] = record["assessed_at"]
    assert_raises(cp.InvalidCheckpoint, "review_after must follow assessed_at",
                  cp.validate_currency, record)


def test_cp_16_currency_review_after_absent_passes(cp, fx):
    record = fx.curr()
    record["review_after"] = None
    assert cp.validate_currency(record) is record


@pytest.mark.parametrize("bad", [[], "record", 3])
def test_cp_17_currency_record_must_be_object(cp, bad):
    assert_raises(cp.InvalidCheckpoint, "currency must be an object",
                  cp.validate_currency, bad)


def test_cp_18_currency_due(cp, fx):
    record = fx.curr()
    record["review_after"] = "2026-01-03T00:00:00+07:00"
    now = datetime(2026, 1, 4, tzinfo=timezone.utc)
    assert cp.currency_due(record, now) is True
    before = datetime(2026, 1, 2, tzinfo=timezone.utc)
    assert cp.currency_due(record, before) is False
    record["review_after"] = None
    assert cp.currency_due(record, now) is False


# ===========================================================================
# 2.2 validate — khung state, sources, units — CP-20…CP-46
# ===========================================================================

@pytest.mark.parametrize("bad", [[], "state", 3])
def test_cp_20_validate_state_must_be_object(cp, bad):
    assert_raises(cp.InvalidCheckpoint, "State must be an object",
                  cp.validate, bad)


@pytest.mark.parametrize("version", [2, None])
def test_cp_21_validate_unsupported_schema_version(cp, fx, version):
    state = fx.state()
    if version is None:
        del state["schema_version"]
    else:
        state["schema_version"] = version
    assert_raises(cp.InvalidCheckpoint, "Unsupported schema_version",
                  cp.validate, state)


@pytest.mark.parametrize("revision", [0, "1", True])
def test_cp_22_validate_invalid_revision(cp, fx, revision):
    state = fx.state(revision=revision)
    assert_raises(cp.InvalidCheckpoint, "Invalid revision", cp.validate, state)


def test_cp_23_validate_invalid_mode(cp, fx):
    state = fx.state(mode="fast")
    assert_raises(cp.InvalidCheckpoint, "Invalid mode", cp.validate, state)


@pytest.mark.parametrize("key,value", [("scope", 5), ("goal", None)])
def test_cp_24_validate_scope_goal_must_be_text(cp, fx, key, value):
    state = fx.state()
    state[key] = value
    assert_raises(cp.InvalidCheckpoint, f"{key} must be text", cp.validate, state)


@pytest.mark.parametrize("key", ["sources", "units", "coverage",
                                 "assessments", "limitations"])
def test_cp_25_validate_lists_required(cp, fx, key):
    state = fx.state()
    state[key] = {}
    assert_raises(cp.InvalidCheckpoint, f"{key} must be a list",
                  cp.validate, state)


def test_cp_26_validate_limitations_must_be_text(cp, fx):
    state = fx.state(limitations=[123])
    assert_raises(cp.InvalidCheckpoint, "Limitations must be text",
                  cp.validate, state)


def test_cp_27_validate_at_least_one_source(cp, fx):
    state = fx.state(sources=[])
    assert_raises(cp.InvalidCheckpoint, "At least one source required",
                  cp.validate, state)


@pytest.mark.parametrize("sid", ["src1", "1S"])
def test_cp_28_validate_invalid_source_id(cp, fx, sid):
    book = fx.book()
    state = fx.state(book)
    state["sources"][0]["id"] = sid
    assert_raises(cp.InvalidCheckpoint, "Invalid source ID", cp.validate, state)


def test_cp_28_validate_duplicate_source_id(cp, fx):
    book = fx.book()
    state = fx.state(book)
    state["sources"].append(deepcopy(state["sources"][0]))
    assert_raises(cp.InvalidCheckpoint, "Duplicate source ID",
                  cp.validate, state)


def test_cp_29_validate_source_relative_path(cp, fx):
    state = fx.state()
    state["sources"][0]["path"] = "book.txt"
    assert_raises(cp.InvalidCheckpoint, "Source unavailable: S01",
                  cp.validate, state)


def test_cp_29_validate_source_missing_file(cp, fx):
    state = fx.state()
    state["sources"][0]["path"] = str(fx.tmp / "khong-ton-tai.txt")
    assert_raises(cp.InvalidCheckpoint, "Source unavailable: S01",
                  cp.validate, state)


def test_cp_30_validate_source_hash_changed(cp, fx):
    book = fx.book()
    state = fx.state(book)
    book.write_text(book.read_text(encoding="utf-8").replace("Z.", "W."),
                    encoding="utf-8")
    assert_raises(cp.InvalidCheckpoint, "Source changed: S01; reimport required",
                  cp.validate, state)


def test_cp_31_validate_empty_source(cp, fx):
    empty = fx.empty_book()
    state = fx.state(empty)
    assert_raises(cp.InvalidCheckpoint, "Empty source: S01", cp.validate, state)


def test_cp_32_validate_invalid_unit_id(cp, fx):
    unit = fx.unit_k01()
    unit["id"] = "U01"
    state = fx.state(units=[unit])
    assert_raises(cp.InvalidCheckpoint, "Invalid unit ID", cp.validate, state)


def test_cp_32_validate_duplicate_unit_id(cp, fx):
    state = fx.state(units=[fx.unit_k01(), fx.unit_k01()])
    assert_raises(cp.InvalidCheckpoint, "Duplicate unit ID", cp.validate, state)


@pytest.mark.parametrize("revision", [0, "1"])
def test_cp_33_validate_invalid_unit_revision(cp, fx, revision):
    unit = fx.unit_k01()
    unit["revision"] = revision
    state = fx.state(units=[unit])
    assert_raises(cp.InvalidCheckpoint, "Invalid unit revision",
                  cp.validate, state)


@pytest.mark.parametrize("key,message", [("title", "Empty title"),
                                         ("content", "Empty content")])
def test_cp_34_validate_unit_text_required(cp, fx, key, message):
    unit = fx.unit_k01()
    unit[key] = "   "
    state = fx.state(units=[unit])
    assert_raises(cp.InvalidCheckpoint, message, cp.validate, state)


def test_cp_35_validate_invalid_unit_kind(cp, fx):
    unit = fx.unit_k01()
    unit["kind"] = "note"
    state = fx.state(units=[unit])
    assert_raises(cp.InvalidCheckpoint, "Invalid kind", cp.validate, state)


@pytest.mark.parametrize("conditions", ["Z", [1]])
def test_cp_36_validate_invalid_conditions(cp, fx, conditions):
    unit = fx.unit_k01()
    unit["conditions"] = conditions
    state = fx.state(units=[unit])
    assert_raises(cp.InvalidCheckpoint, "Invalid conditions",
                  cp.validate, state)


def test_cp_37_validate_related_ok(cp, fx):
    unit = fx.unit_k01()
    unit["related"] = ["K02"]
    state = fx.state(units=[unit, fx.unit_k02()])
    assert cp.validate(state) is state


@pytest.mark.parametrize("related", [["K99"], ["K01"]])
def test_cp_37_validate_broken_related(cp, fx, related):
    unit = fx.unit_k01()
    unit["related"] = related
    state = fx.state(units=[unit, fx.unit_k02()])
    assert_raises(cp.InvalidCheckpoint, "Broken related ID", cp.validate, state)


def test_cp_38_validate_knowledge_level_ok_and_absent(cp, fx):
    unit = fx.unit_k01()
    unit["knowledge_level"] = "L2"
    state = fx.state(units=[unit])
    assert cp.validate(state) is state
    state2 = fx.state(units=[fx.unit_k01()])
    assert cp.validate(state2) is state2


def test_cp_38_validate_invalid_knowledge_level(cp, fx):
    unit = fx.unit_k01()
    unit["knowledge_level"] = "L5"
    state = fx.state(units=[unit])
    assert_raises(cp.InvalidCheckpoint, "Invalid knowledge_level",
                  cp.validate, state)


@pytest.mark.parametrize("prerequisites", [["K99"], ["K01"]])
def test_cp_39_validate_broken_prerequisite(cp, fx, prerequisites):
    unit = fx.unit_k01()
    unit["prerequisites"] = prerequisites
    state = fx.state(units=[unit, fx.unit_k02()])
    assert_raises(cp.InvalidCheckpoint, "Broken prerequisite ID",
                  cp.validate, state)


def test_cp_39_validate_prerequisite_ok(cp, fx):
    unit = fx.unit_k01()
    unit["prerequisites"] = ["K02"]
    state = fx.state(units=[unit, fx.unit_k02()])
    assert cp.validate(state) is state


def test_cp_40_validate_relations_not_a_list(cp, fx):
    unit = fx.unit_k01()
    unit["relations"] = {"type": "supports", "target": "K02"}
    state = fx.state(units=[unit, fx.unit_k02()])
    assert_raises(cp.InvalidCheckpoint, "relations must be a list",
                  cp.validate, state)


@pytest.mark.parametrize("edge", [{"type": "causes", "target": "K02"},
                                  {"type": "supports", "target": "K99"}])
def test_cp_40_validate_invalid_typed_relation(cp, fx, edge):
    unit = fx.unit_k01()
    unit["relations"] = [edge]
    state = fx.state(units=[unit, fx.unit_k02()])
    assert_raises(cp.InvalidCheckpoint, "Invalid typed relation",
                  cp.validate, state)


def test_cp_40_validate_relation_ok(cp, fx):
    unit = fx.unit_k01()
    unit["relations"] = [{"type": "supports", "target": "K02"}]
    state = fx.state(units=[unit, fx.unit_k02()])
    assert cp.validate(state) is state


def test_cp_41_validate_citations_must_be_list(cp, fx):
    unit = fx.unit_k01()
    unit["citations"] = {}
    state = fx.state(units=[unit])
    assert_raises(cp.InvalidCheckpoint, "citations must be a list",
                  cp.validate, state)


def test_cp_41_validate_grounded_unit_requires_citation(cp, fx):
    unit = fx.unit_k01()
    unit["citations"] = []
    state = fx.state(units=[unit])
    assert_raises(cp.InvalidCheckpoint, "Grounded unit requires citation",
                  cp.validate, state)


def test_cp_41_validate_new_example_may_omit_citations(cp, fx):
    unit = fx.unit_k01()
    unit["kind"] = "new_example"
    unit["citations"] = []
    state = fx.state(units=[unit])
    assert cp.validate(state) is state


def test_cp_42_validate_citation_unknown_source(cp, fx):
    unit = fx.unit_k01()
    unit["citations"][0]["source_id"] = "S99"
    state = fx.state(units=[unit])
    assert_raises(cp.InvalidCheckpoint, "Unknown source ID", cp.validate, state)


@pytest.mark.parametrize("start,end", [(0, 2), (2, 6), (3, 2)])
def test_cp_43_validate_invalid_line_range(cp, fx, start, end):
    unit = fx.unit_k01()
    unit["citations"][0]["line_start"] = start
    unit["citations"][0]["line_end"] = end
    state = fx.state(units=[unit])
    assert_raises(cp.InvalidCheckpoint, "Invalid line range",
                  cp.validate, state)


def test_cp_44_validate_empty_excerpt(cp, fx):
    unit = fx.unit_k01()
    unit["citations"][0]["excerpt"] = " "
    state = fx.state(units=[unit])
    assert_raises(cp.InvalidCheckpoint, "Empty excerpt", cp.validate, state)


@pytest.mark.parametrize("start,end", [(2, 2), (3, 3)])
def test_cp_44_validate_excerpt_not_found(cp, fx, start, end):
    unit = fx.unit_k01()
    unit["citations"][0]["line_start"] = start
    unit["citations"][0]["line_end"] = end
    if (start, end) == (2, 2):
        unit["citations"][0]["excerpt"] = "câu không có trong sách"
    state = fx.state(units=[unit])
    assert_raises(cp.InvalidCheckpoint, "Excerpt not found in cited lines",
                  cp.validate, state)


def test_cp_45_validate_current_source_ok(cp, fx):
    state = fx.state(units=[fx.unit_curr()])
    assert cp.validate(state) is state


def test_cp_45_validate_current_source_url_required(cp, fx):
    unit = fx.unit_curr()
    del unit["url"]
    state = fx.state(units=[unit])
    assert_raises(cp.InvalidCheckpoint, "Current source URL required",
                  cp.validate, state)


def test_cp_45_validate_current_source_bad_url(cp, fx):
    unit = fx.unit_curr()
    unit["url"] = "ftp://example.org/a"
    state = fx.state(units=[unit])
    assert_raises(cp.InvalidCheckpoint, "Invalid current source URL",
                  cp.validate, state)


@pytest.mark.parametrize("checked_at", ["2026-01-01T00:00:00", "abc"])
def test_cp_45_validate_current_source_bad_checked_at(cp, fx, checked_at):
    unit = fx.unit_curr()
    unit["checked_at"] = checked_at
    state = fx.state(units=[unit])
    assert_raises(cp.InvalidCheckpoint, "Invalid checked_at timestamp",
                  cp.validate, state)


def test_cp_46_validate_unit_currency_guard_propagates(cp, fx):
    unit = fx.unit_k01()
    record = _reduced_record(fx, status="not_checked",
                             evidence=fx.curr()["evidence"])
    unit["currency"] = record
    state = fx.state(units=[unit])
    assert_raises(cp.InvalidCheckpoint, "not_checked cannot claim verification",
                  cp.validate, state)


def test_cp_46_validate_unit_currency_ok(cp, fx):
    unit = fx.unit_k01()
    unit["currency"] = fx.curr()
    state = fx.state(units=[unit])
    assert cp.validate(state) is state


# ===========================================================================
# 2.3 validate — coverage, assessments, pending_question — CP-47…CP-55
# ===========================================================================

def _coverage_row(**over):
    row = {"source_id": "S01", "section": "Dòng 2", "status": "unprocessed",
           "unit_ids": []}
    row.update(over)
    return row


def test_cp_47_validate_coverage_ok(cp, fx):
    state = fx.state(units=[fx.unit_k01()], coverage=[_coverage_row()])
    assert cp.validate(state) is state


@pytest.mark.parametrize("over,message", [
    ({"source_id": "S99"}, "Invalid coverage source"),
    ({"section": " "}, "Missing coverage section"),
    ({"status": "done"}, "Invalid coverage status"),
    ({"unit_ids": ["K99"]}, "Broken coverage unit"),
])
def test_cp_47_validate_coverage_invalid(cp, fx, over, message):
    state = fx.state(units=[fx.unit_k01()], coverage=[_coverage_row(**over)])
    assert_raises(cp.InvalidCheckpoint, message, cp.validate, state)


def test_cp_48_validate_coverage_analyzed_ok(cp, fx):
    row = _coverage_row(status="analyzed", unit_ids=["K01"])
    state = fx.state(units=[fx.unit_k01()], coverage=[row])
    assert cp.validate(state) is state


def test_cp_48_validate_coverage_analyzed_requires_units(cp, fx):
    row = _coverage_row(status="analyzed", unit_ids=[])
    state = fx.state(units=[fx.unit_k01()], coverage=[row])
    assert_raises(cp.InvalidCheckpoint, "Analyzed coverage requires units",
                  cp.validate, state)


def test_cp_48_validate_coverage_lacks_citation_to_source(cp, fx):
    book_a = fx.book()
    book_b = fx.write_book(name="book-b.txt")
    state = fx.state(book_a, units=[fx.unit_k01()])
    state["sources"].append({"id": "S02", "path": str(book_b),
                             "sha256": cp.sha256(book_b)})
    # K01 chỉ trích S01; row trỏ sang S02 → thiếu citation cùng source.
    row = _coverage_row(source_id="S02", status="analyzed", unit_ids=["K01"])
    state["coverage"] = [row]
    assert_raises(cp.InvalidCheckpoint,
                  "Coverage lacks a citation to its source",
                  cp.validate, state)


def test_cp_49_validate_coverage_merged_requires_reason(cp, fx):
    row = _coverage_row(status="merged", unit_ids=["K01"])
    state = fx.state(units=[fx.unit_k01()], coverage=[row])
    assert_raises(cp.InvalidCheckpoint, "Merged coverage requires reason",
                  cp.validate, state)


def test_cp_49_validate_coverage_merged_with_reason_ok(cp, fx):
    row = _coverage_row(status="merged", unit_ids=["K01"],
                        reason="Gộp vào K01 vì cùng ý")
    state = fx.state(units=[fx.unit_k01()], coverage=[row])
    assert cp.validate(state) is state


def _assessment(**over):
    row = {"question_id": "Q01", "response": "", "support": "none",
           "result": "unassessed"}
    row.update(over)
    return row


def test_cp_50_validate_assessment_ok(cp, fx):
    state = fx.state(assessments=[_assessment()])
    assert cp.validate(state) is state


@pytest.mark.parametrize("over,message", [
    ({"question_id": " "}, "Missing question ID"),
    ({"result": "passed"}, "Invalid assessment result"),
    ({"support": "full"}, "Invalid support"),
    ({"response": 5}, "response must be text"),
])
def test_cp_50_validate_assessment_invalid(cp, fx, over, message):
    state = fx.state(assessments=[_assessment(**over)])
    assert_raises(cp.InvalidCheckpoint, message, cp.validate, state)


@pytest.mark.parametrize("response", ["", "   "])
def test_cp_51_validate_assess_requires_response(cp, fx, response):
    state = fx.state(assessments=[_assessment(result="needs_work",
                                              response=response)])
    assert_raises(cp.InvalidCheckpoint, "Cannot assess without response",
                  cp.validate, state)


def test_cp_51_validate_assess_with_response_ok(cp, fx):
    state = fx.state(assessments=[_assessment(result="needs_work",
                                              response="Câu trả lời thật")])
    assert cp.validate(state) is state


@pytest.mark.parametrize("support", ["hint", "worked_example"])
def test_cp_52_validate_independent_requires_no_support(cp, fx, support):
    state = fx.state(assessments=[_assessment(result="independent",
                                              support=support,
                                              response="Câu trả lời thật")])
    assert_raises(cp.InvalidCheckpoint,
                  "Assisted answer cannot be independent",
                  cp.validate, state)


def test_cp_52_validate_independent_ok(cp, fx):
    state = fx.state(assessments=[_assessment(result="independent",
                                              support="none",
                                              response="Câu trả lời thật")])
    assert cp.validate(state) is state


def test_cp_53_validate_pending_ok(cp, fx):
    pending = {"id": "Q01", "prompt": "Vì sao Z là điều kiện cần?"}
    state = fx.state(pending_question=pending)
    assert cp.validate(state) is state


def test_cp_53_validate_pending_extra_key(cp, fx):
    pending = {"id": "Q01", "prompt": "…", "answer": "…"}
    state = fx.state(pending_question=pending)
    assert_raises(cp.InvalidCheckpoint,
                  "Pending question must contain only id/prompt",
                  cp.validate, state)


def test_cp_53_validate_pending_empty_prompt(cp, fx):
    pending = {"id": "Q01", "prompt": " "}
    state = fx.state(pending_question=pending)
    assert_raises(cp.InvalidCheckpoint, "Empty pending question",
                  cp.validate, state)


@pytest.mark.parametrize("mode", ["extract", "unselected"])
def test_cp_53_validate_pending_incompatible_mode(cp, fx, mode):
    pending = {"id": "Q01", "prompt": "Vì sao Z là điều kiện cần?"}
    state = fx.state(mode=mode, pending_question=pending)
    assert_raises(cp.InvalidCheckpoint, "Pending quiz incompatible with mode",
                  cp.validate, state)


def test_cp_54_validate_state_with_valid_session(cp, fx):
    state = fx.state_session(fx.session_empty())
    assert cp.validate(state) is state


def test_cp_54_validate_state_session_error_wrapped(cp, fx):
    session = fx.session_empty()
    session["reading_style"] = "weird"
    state = fx.state_session(session)
    assert_raises(cp.InvalidCheckpoint, "Invalid reading style",
                  cp.validate, state)


def test_cp_55_validate_state_min_passes(cp, fx):
    state = fx.state()
    assert cp.validate(state) is state


# ===========================================================================
# 2.4 validate_transition — CP-56…CP-61
# ===========================================================================

def _old_new(fx):
    book = fx.book()
    old = fx.state(book, units=[fx.unit_k01()])
    new = fx.state(book, units=[fx.unit_k01()])
    new["revision"] = 2
    return old, new


def test_cp_56_validate_transition_ok(cp, fx):
    old, new = _old_new(fx)
    assert cp.validate_transition(old, new) is None


@pytest.mark.parametrize("revision", [3, 1])
def test_cp_56_validate_transition_revision_must_increment_by_one(cp, fx,
                                                                  revision):
    old, new = _old_new(fx)
    new["revision"] = revision
    assert_raises(cp.InvalidCheckpoint,
                  "State revision must increment by one",
                  cp.validate_transition, old, new)


def test_cp_57_validate_transition_source_identity_locked(cp, fx):
    old, new = _old_new(fx)
    book_b = fx.write_book(name="book-b.txt")
    new["sources"].append({"id": "S02", "path": str(book_b),
                           "sha256": cp.sha256(book_b)})
    assert_raises(cp.InvalidCheckpoint,
                  "Source identity cannot change; create a new session",
                  cp.validate_transition, old, new)


def test_cp_58_validate_transition_units_cannot_disappear(cp, fx):
    old, new = _old_new(fx)
    new["units"] = []
    assert_raises(cp.InvalidCheckpoint, "Existing units cannot disappear",
                  cp.validate_transition, old, new)


def test_cp_58_validate_transition_may_add_units(cp, fx):
    old, new = _old_new(fx)
    new["units"] = [fx.unit_k01(), fx.unit_k02()]
    assert cp.validate_transition(old, new) is None


def test_cp_59_validate_transition_changed_unit_needs_revision_bump(cp, fx):
    old, new = _old_new(fx)
    new["units"][0]["content"] = "Nội dung đã sửa."
    assert_raises(cp.InvalidCheckpoint, "Changed unit must increment revision",
                  cp.validate_transition, old, new)


def test_cp_59_validate_transition_changed_unit_revision_jump(cp, fx):
    old, new = _old_new(fx)
    new["units"][0]["content"] = "Nội dung đã sửa."
    new["units"][0]["revision"] = 3
    assert_raises(cp.InvalidCheckpoint, "Changed unit must increment revision",
                  cp.validate_transition, old, new)


def test_cp_59_validate_transition_changed_unit_with_bump_ok(cp, fx):
    old, new = _old_new(fx)
    new["units"][0]["content"] = "Nội dung đã sửa."
    new["units"][0]["revision"] = 2
    assert cp.validate_transition(old, new) is None


def test_cp_60_validate_transition_invalid_new_fails_validation_first(cp, fx):
    book = fx.book()
    old = fx.state(book, units=[fx.unit_k01()])
    new = fx.state(book, units=[fx.unit_k01()])
    new["revision"] = 2
    book.write_text(book.read_text(encoding="utf-8").replace("Z.", "W."),
                    encoding="utf-8")
    assert_raises(cp.InvalidCheckpoint, "Source changed: S01; reimport required",
                  cp.validate_transition, old, new)


def test_cp_61_validate_transition_session_guard_wrapped(cp, fx):
    book = fx.book()
    old = fx.state_session(fx.session_nav1(), book, units=[fx.unit_k01()])
    broken = fx.session_empty()
    new = fx.state_session(broken, book, units=[fx.unit_k01()])
    new["revision"] = 2
    assert_raises(cp.InvalidCheckpoint,
                  "Navigation history cannot disappear/change",
                  cp.validate_transition, old, new)


def test_cp_61_validate_transition_session_ok(cp, fx):
    book = fx.book()
    old = fx.state_session(fx.session_nav1(), book, units=[fx.unit_k01()])
    new = fx.state_session(fx.session_nav2(), book, units=[fx.unit_k01()])
    new["revision"] = 2
    assert cp.validate_transition(old, new) is None


# ===========================================================================
# 2.5 write_atomic, initialize, save, export — CP-62…CP-81
# ===========================================================================

def test_cp_62_write_atomic_refuses_symlink(cp, fx, tmp_path):
    real = tmp_path / "real.json"
    real.write_text("gốc", encoding="utf-8")
    link = tmp_path / "state.json"
    link.symlink_to(real)
    assert_raises(cp.InvalidCheckpoint, "Refuse symlink state target",
                  cp.write_atomic, link, {"a": 1})
    assert real.read_text(encoding="utf-8") == "gốc"


def test_cp_63_write_atomic_writes_json_with_trailing_newline(cp, fx, tmp_path):
    target = tmp_path / "a" / "b" / "state.json"
    state = {"goal": "Học điều kiện", "revision": 1}
    cp.write_atomic(target, state)
    text = target.read_text(encoding="utf-8")
    assert json.loads(text) == state
    assert text.endswith("\n")
    cp.write_atomic(target, {"goal": "Mới", "revision": 2})
    assert json.loads(target.read_text(encoding="utf-8"))["revision"] == 2


def test_cp_64_write_atomic_leaves_no_temp_files(cp, fx, tmp_path):
    target = tmp_path / "state.json"
    cp.write_atomic(target, {"a": 1})
    names = [p.name for p in tmp_path.iterdir()]
    assert names == ["state.json"]


def test_cp_65_initialize_creates_state(cp, fx, tmp_path):
    book = fx.book()
    target = tmp_path / "state.json"
    state = cp.initialize(book, target, "deep")
    assert state["schema_version"] == 1
    assert state["revision"] == 1
    assert state["mode"] == "deep"
    assert state["scope"] == "" and state["goal"] == ""
    assert state["sources"] == [{"id": "S01", "path": str(book.resolve()),
                                 "sha256": cp.sha256(book)}]
    assert state["units"] == [] and state["coverage"] == []
    assert state["assessments"] == [] and state["limitations"] == []
    assert state["pending_question"] is None
    assert target.is_file()
    assert cp.validate(state) is state


def test_cp_66_initialize_target_must_not_exist(cp, fx, tmp_path):
    book = fx.book()
    target = tmp_path / "state.json"
    target.write_text("{}", encoding="utf-8")
    assert_raises(cp.InvalidCheckpoint, "State target already exists",
                  cp.initialize, book, target, "deep")


def test_cp_66_initialize_target_broken_symlink(cp, fx, tmp_path):
    book = fx.book()
    target = tmp_path / "state.json"
    target.symlink_to(tmp_path / "khong-ton-tai.json")
    assert_raises(cp.InvalidCheckpoint, "State target already exists",
                  cp.initialize, book, target, "deep")


def test_cp_67_initialize_target_must_differ_from_source(cp, fx, tmp_path):
    ghost = tmp_path / "ghost.txt"
    assert_raises(cp.InvalidCheckpoint, "State target must differ from source",
                  cp.initialize, ghost, ghost, "deep")


def test_cp_68_initialize_source_unavailable(cp, fx, tmp_path):
    ghost = tmp_path / "ghost.txt"
    assert_raises(cp.InvalidCheckpoint, "Source file unavailable",
                  cp.initialize, ghost, tmp_path / "state.json", "deep")


def test_cp_69_initialize_empty_source_rejected(cp, fx, tmp_path):
    empty = fx.empty_book()
    target = tmp_path / "state.json"
    assert_raises(cp.InvalidCheckpoint, "Empty source: S01",
                  cp.initialize, empty, target, "deep")
    assert not target.exists()


def _write_state_file(cp, path, state):
    path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")


def test_cp_70_save_replaces_state(cp, fx, tmp_path):
    old, new = _old_new(fx)
    target = tmp_path / "state.json"
    candidate = tmp_path / "candidate.json"
    _write_state_file(cp, target, old)
    _write_state_file(cp, candidate, new)
    result = cp.save(target, candidate)
    assert result == new
    assert json.loads(target.read_text(encoding="utf-8")) == new


def test_cp_71_save_refuses_symlink_target(cp, fx, tmp_path):
    old, new = _old_new(fx)
    real = tmp_path / "real.json"
    _write_state_file(cp, real, old)
    link = tmp_path / "state.json"
    link.symlink_to(real)
    candidate = tmp_path / "candidate.json"
    _write_state_file(cp, candidate, new)
    assert_raises(cp.InvalidCheckpoint, "Refuse symlink state target",
                  cp.save, link, candidate)


def test_cp_72_save_candidate_must_differ(cp, fx, tmp_path):
    old, _new = _old_new(fx)
    target = tmp_path / "state.json"
    _write_state_file(cp, target, old)
    assert_raises(cp.InvalidCheckpoint, "Candidate must differ from state",
                  cp.save, target, target)


def test_cp_73_save_must_not_overwrite_source(cp, fx, tmp_path):
    old, new = _old_new(fx)
    target = tmp_path / "state.json"
    _write_state_file(cp, target, old)
    new["sources"][0]["path"] = str(target)
    candidate = tmp_path / "candidate.json"
    _write_state_file(cp, candidate, new)
    assert_raises(cp.InvalidCheckpoint, "State must not overwrite source",
                  cp.save, target, candidate)


def test_cp_74_save_failure_keeps_original(cp, fx, tmp_path):
    old, new = _old_new(fx)
    new["revision"] = 3
    target = tmp_path / "state.json"
    candidate = tmp_path / "candidate.json"
    _write_state_file(cp, target, old)
    before = target.read_bytes()
    _write_state_file(cp, candidate, new)
    assert_raises(cp.InvalidCheckpoint,
                  "State revision must increment by one",
                  cp.save, target, candidate)
    assert target.read_bytes() == before


def test_cp_75_save_candidate_invalid_json(cp, fx, tmp_path):
    old, _new = _old_new(fx)
    target = tmp_path / "state.json"
    _write_state_file(cp, target, old)
    candidate = tmp_path / "candidate.json"
    candidate.write_text("not json", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        cp.save(target, candidate)


def test_cp_76_export_creates_handoff(cp, fx, tmp_path):
    book = fx.book()
    state = fx.state(book, units=[fx.unit_k01(), fx.unit_curr()])
    target = tmp_path / "state.json"
    _write_state_file(cp, target, state)
    output = tmp_path / "handoff.md"
    cp.export(target, output)
    text = output.read_text(encoding="utf-8")
    assert "# SID — Bản bàn giao" in text
    assert "Chế độ: deep · Phiên bản: 1" in text
    assert "## Nguồn" in text
    assert str(book) in text and cp.sha256(book) in text
    assert "## K01 — Điều kiện Z (v1, book)" in text
    assert "- Điều kiện: Z" in text
    assert "- Nguồn: S01 dòng 2–2; X may improve Y under condition Z" in text
    assert "- Nguồn ngoài: https://example.org/a · Kiểm tra: 2026-01-01T00:00:00+07:00" in text
    assert "## Độ bao quát" in text
    assert "## Đánh giá quan sát được" in text
    assert "## Câu đang chờ" in text
    assert "## Phần thiếu và bước tiếp theo" in text
    assert text.rstrip("\n").endswith(
        "Phiên mới cần nguồn tương ứng; bản bàn giao không thay cho quyền truy cập sách.")


def test_cp_77_export_target_must_not_exist(cp, fx, tmp_path):
    state = fx.state(units=[fx.unit_k01()])
    target = tmp_path / "state.json"
    _write_state_file(cp, target, state)
    output = tmp_path / "handoff.md"
    output.write_text("đã có", encoding="utf-8")
    assert_raises(cp.InvalidCheckpoint, "Export target already exists",
                  cp.export, target, output)


def test_cp_77_export_target_symlink(cp, fx, tmp_path):
    state = fx.state(units=[fx.unit_k01()])
    target = tmp_path / "state.json"
    _write_state_file(cp, target, state)
    real = tmp_path / "real.md"
    real.write_text("gốc", encoding="utf-8")
    output = tmp_path / "handoff.md"
    output.symlink_to(real)
    assert_raises(cp.InvalidCheckpoint, "Export target already exists",
                  cp.export, target, output)


def test_cp_78_export_must_not_overwrite_source(cp, fx, tmp_path):
    book = fx.book()
    state = fx.state(book, units=[fx.unit_k01()])
    target = tmp_path / "state.json"
    _write_state_file(cp, target, state)
    assert_raises(cp.InvalidCheckpoint, "Cannot overwrite source",
                  cp.export, target, book)


def test_cp_78_export_must_not_overwrite_source_safety_pin(cp, fx, tmp_path):
    # Safety pin độc lập cho CP-78: export với output trùng file nguồn bị
    # từ chối VÀ file nguồn không đổi một byte sau lần gọi.
    book = fx.book()
    state = fx.state(book, units=[fx.unit_k01()])
    target = tmp_path / "state.json"
    _write_state_file(cp, target, state)
    before = book.read_bytes()
    with pytest.raises(cp.InvalidCheckpoint):
        cp.export(target, book)
    assert book.read_bytes() == before


def test_cp_79_export_currency_due_warning(cp, fx, tmp_path):
    record = fx.curr()
    record["review_after"] = (datetime.now(timezone.utc)
                              - timedelta(days=1)).isoformat()
    unit = fx.unit_k01()
    unit["currency"] = record
    state = fx.state(units=[unit])
    target = tmp_path / "state.json"
    _write_state_file(cp, target, state)
    output = tmp_path / "handoff.md"
    cp.export(target, output)
    text = output.read_text(encoding="utf-8")
    assert "- Kiểm thời sự: " in text
    assert ("- ĐẾN HẠN KIỂM LẠI: kết luận chỉ được xác minh tại thời điểm đã ghi; "
            "cần đọc lại nguồn trước khi dùng như thông tin hiện tại.") in text


def test_cp_79_export_currency_not_due_no_warning(cp, fx, tmp_path):
    record = fx.curr()
    record["review_after"] = (datetime.now(timezone.utc)
                              + timedelta(days=30)).isoformat()
    unit = fx.unit_k01()
    unit["currency"] = record
    state = fx.state(units=[unit])
    target = tmp_path / "state.json"
    _write_state_file(cp, target, state)
    output = tmp_path / "handoff.md"
    cp.export(target, output)
    text = output.read_text(encoding="utf-8")
    assert "- Kiểm thời sự: " in text
    assert "ĐẾN HẠN KIỂM LẠI" not in text


def test_cp_80_export_includes_session_sections(cp, fx, tmp_path):
    state = fx.state_session(fx.session_nav1(), units=[fx.unit_k01()])
    target = tmp_path / "state.json"
    _write_state_file(cp, target, state)
    output = tmp_path / "handoff.md"
    cp.export(target, output)
    text = output.read_text(encoding="utf-8")
    assert "## Phiên đọc và điểm quay lại" in text
    assert "## Tiến trình đọc / xử lý / phản hồi quan sát được" in text


def test_cp_80_export_without_session_omits_sections(cp, fx, tmp_path):
    state = fx.state(units=[fx.unit_k01()])
    target = tmp_path / "state.json"
    _write_state_file(cp, target, state)
    output = tmp_path / "handoff.md"
    cp.export(target, output)
    text = output.read_text(encoding="utf-8")
    assert "## Phiên đọc và điểm quay lại" not in text
    assert "## Tiến trình đọc / xử lý / phản hồi quan sát được" not in text


def test_cp_81_export_validates_state_first(cp, fx, tmp_path):
    book = fx.book()
    state = fx.state(book, units=[fx.unit_k01()])
    target = tmp_path / "state.json"
    _write_state_file(cp, target, state)
    book.write_text(book.read_text(encoding="utf-8").replace("Z.", "W."),
                    encoding="utf-8")
    output = tmp_path / "handoff.md"
    assert_raises(cp.InvalidCheckpoint, "Source changed: S01; reimport required",
                  cp.export, target, output)
    assert not output.exists()


# ===========================================================================
# RT regression — checkpoint hardening (Red Team CP-A01…CP-A05, CP-A03)
# ===========================================================================

def test_cp_a01_state_rejects_forged_semantic_field(cp, fx):
    """RT/CP-A01: trường tự phong ở cấp state phải bị khóa tập trường chặn."""
    state = fx.state(semantic_verified=True)
    assert_raises(cp.InvalidCheckpoint,
                  "Unexpected state field: semantic_verified",
                  cp.validate, state)


def test_cp_a01_source_rejects_forged_field(cp, fx):
    """RT/CP-A01: trường lạ trong source không được qua validate()."""
    state = fx.state()
    state["sources"][0]["mastery_claim"] = "achieved"
    assert_raises(cp.InvalidCheckpoint,
                  "Unexpected source field: mastery_claim",
                  cp.validate, state)


def test_cp_a01_unit_rejects_forged_mastery_field(cp, fx):
    """RT/CP-A01: unit không được mang trường fabricated_mastery qua validate()."""
    unit = fx.unit_k01()
    unit["fabricated_mastery"] = "L4"
    state = fx.state(units=[unit])
    assert_raises(cp.InvalidCheckpoint,
                  "Unexpected unit field: fabricated_mastery",
                  cp.validate, state)


def test_cp_a01_coverage_rejects_forged_field(cp, fx):
    """RT/CP-A01: coverage là một dict lồng chính và cũng bị khóa tập trường."""
    row = _coverage_row(semantic_verified=True)
    state = fx.state(units=[fx.unit_k01()], coverage=[row])
    assert_raises(cp.InvalidCheckpoint,
                  "Unexpected coverage field: semantic_verified",
                  cp.validate, state)


def test_cp_a01_assessment_rejects_forged_field(cp, fx):
    """RT/CP-A01: assessment không được tự phong mastery_claim."""
    row = _assessment(mastery_claim="achieved")
    state = fx.state(assessments=[row])
    assert_raises(cp.InvalidCheckpoint,
                  "Unexpected assessment field: mastery_claim",
                  cp.validate, state)


def test_cp_a01_currency_and_evidence_reject_forged_fields(cp, fx):
    """RT/CP-A01: currency và evidence của nó đều bị khóa tập trường."""
    record = fx.curr()
    record["mastery_claim"] = "achieved"
    assert_raises(cp.InvalidCheckpoint,
                  "Unexpected currency field: mastery_claim",
                  cp.validate_currency, record)

    record = fx.curr()
    record["evidence"][0]["semantic_verified"] = True
    assert_raises(cp.InvalidCheckpoint,
                  "Unexpected currency evidence field: semantic_verified",
                  cp.validate_currency, record)


def test_cp_a01_citation_and_relation_reject_forged_fields(cp, fx):
    """RT/CP-A01: citation/relation không được chứa trường ngoài schema."""
    unit = fx.unit_k01()
    unit["citations"][0]["verified_by"] = "helper"
    state = fx.state(units=[unit])
    assert_raises(cp.InvalidCheckpoint,
                  "Unexpected citation field: verified_by",
                  cp.validate, state)

    unit = fx.unit_k01()
    unit["relations"] = [{"type": "supports", "target": "K02",
                          "semantic_verified": True}]
    state = fx.state(units=[unit, fx.unit_k02()])
    assert_raises(cp.InvalidCheckpoint,
                  "Unexpected relation field: semantic_verified",
                  cp.validate, state)


def test_cp_a01_save_rejects_forged_unit_field(cp, fx, tmp_path):
    """RT/CP-A01: save() không được lưu giữ trường bịa đã chui vào candidate."""
    old, new = _old_new(fx)
    new["units"][0]["semantic_verified"] = True
    target = tmp_path / "state.json"
    candidate = tmp_path / "candidate.json"
    _write_state_file(cp, target, old)
    before = target.read_bytes()
    _write_state_file(cp, candidate, new)
    assert_raises(cp.InvalidCheckpoint,
                  "Unexpected unit field: semantic_verified",
                  cp.save, target, candidate)
    assert target.read_bytes() == before


def test_cp_a04_read_json_rejects_duplicate_top_level_key(cp, tmp_path):
    """RT/CP-A04: duplicate key ở cấp ngoài cùng phải là lỗi sạch."""
    path = tmp_path / "duplicate.json"
    path.write_text('{"revision": 3, "revision": 2}', encoding="utf-8")
    assert_raises(cp.InvalidCheckpoint, "Duplicate JSON key: revision",
                  cp.read_json, path)


def test_cp_a04_read_json_rejects_duplicate_nested_key(cp, tmp_path):
    """RT/CP-A04: object_pairs_hook phải bắt duplicate key ở object lồng."""
    path = tmp_path / "duplicate-nested.json"
    path.write_text('{"state": {"mode": "deep", "mode": "extract"}}',
                    encoding="utf-8")
    assert_raises(cp.InvalidCheckpoint, "Duplicate JSON key: mode",
                  cp.read_json, path)


def test_cp_a04_save_rejects_duplicate_revision_key(cp, fx, tmp_path):
    """RT/CP-A04: save() không được lặng lẽ lấy giá trị cuối của revision."""
    old, new = _old_new(fx)
    target = tmp_path / "state.json"
    candidate = tmp_path / "candidate.json"
    _write_state_file(cp, target, old)
    before = target.read_bytes()
    candidate_text = json.dumps(new, ensure_ascii=False).replace(
        '"revision": 2', '"revision": 3, "revision": 2', 1)
    candidate.write_text(candidate_text, encoding="utf-8")
    assert_raises(cp.InvalidCheckpoint, "Duplicate JSON key: revision",
                  cp.save, target, candidate)
    assert target.read_bytes() == before


@pytest.mark.parametrize("excerpt", ["X", "X may", "improve Y"])
def test_cp_a02_short_excerpt_rejected(cp, fx, excerpt):
    """RT/CP-A02: excerpt dưới 10 ký tự hoặc dưới 2 từ không đạt grounding."""
    unit = fx.unit_k01()
    unit["citations"][0]["excerpt"] = excerpt
    state = fx.state(units=[unit])
    assert_raises(cp.InvalidCheckpoint, "Excerpt too short for grounding",
                  cp.validate, state)


def test_cp_a02_excerpt_at_minimum_grounding_threshold_passes(cp, fx):
    """RT/CP-A02: excerpt đúng ngưỡng 10 ký tự và ít nhất 2 từ vẫn hợp lệ."""
    unit = fx.unit_k01()
    unit["citations"][0]["excerpt"] = "under cond"
    state = fx.state(units=[unit])
    assert cp.validate(state) is state


def test_cp_a05_read_json_rejects_file_over_cap(cp, tmp_path, monkeypatch):
    """RT/CP-A05: file JSON/state vượt MAX_JSON_BYTES bị từ chối sạch."""
    monkeypatch.setattr(cp, "MAX_JSON_BYTES", 32)
    path = tmp_path / "oversized.json"
    path.write_text('{"revision": 1, "padding": "0123456789"}',
                    encoding="utf-8")
    assert_raises(cp.InvalidCheckpoint,
                  "JSON file too large: maximum 32 bytes",
                  cp.read_json, path)


def test_cp_a05_read_json_cap_is_checked_before_decoding(cp, tmp_path,
                                                          monkeypatch):
    """RT/CP-A05: file vượt cap bị chặn trước khi decoder nạp/phân tích nó."""
    monkeypatch.setattr(cp, "MAX_JSON_BYTES", 8)
    path = tmp_path / "oversized-invalid.json"
    path.write_text("this is not json and it is too long", encoding="utf-8")
    assert_raises(cp.InvalidCheckpoint,
                  "JSON file too large: maximum 8 bytes",
                  cp.read_json, path)


def test_cp_a05_sha256_streams_file_in_chunks(cp, tmp_path, monkeypatch):
    """RT/CP-A05: sha256() đọc theo chunk, không gọi Path.read_bytes()."""
    from pathlib import Path

    data = b"a" * (cp._SHA256_CHUNK_BYTES + 123)
    path = tmp_path / "large-source.bin"
    path.write_bytes(data)
    original_read_bytes = Path.read_bytes

    def guarded_read_bytes(self, *args, **kwargs):
        if self == path:
            raise AssertionError("sha256 must not load the whole file at once")
        return original_read_bytes(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_bytes", guarded_read_bytes)
    import hashlib
    assert cp.sha256(path) == hashlib.sha256(data).hexdigest()


def test_cp_a03_source_outside_source_root_rejected(cp, fx, tmp_path):
    """RT/CP-A03: source resolve ra ngoài source_root khai báo phải FAIL."""
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    book = fx.book()
    state = fx.state(book, source_root=str(allowed))
    assert_raises(cp.InvalidCheckpoint, "Source outside source_root: S01",
                  cp.validate, state)


def test_cp_a03_source_inside_source_root_passes(cp, fx, tmp_path):
    """RT/CP-A03: source nằm trong source_root vẫn validate bình thường."""
    book = fx.book()
    state = fx.state(book, source_root=str(tmp_path))
    assert cp.validate(state) is state


def test_cp_a03_export_without_source_root_warns_sources_are_self_declared(
        cp, fx, tmp_path):
    """RT/CP-A03: export phải cảnh báo khi source chưa gắn gốc phạm vi."""
    state = fx.state(units=[fx.unit_k01()])
    target = tmp_path / "state.json"
    _write_state_file(cp, target, state)
    output = tmp_path / "handoff.md"
    cp.export(target, output)
    text = output.read_text(encoding="utf-8")
    assert ("state không khai báo source_root; các nguồn là tự khai "
            "và chưa được gắn với gốc phạm vi đã kiểm") in text


def test_cp_a03_export_with_source_root_omits_unbound_scope_warning(
        cp, fx, tmp_path):
    """RT/CP-A03: state đã gắn source_root thì không cần cảnh báo chưa gắn gốc."""
    book = fx.book()
    state = fx.state(book, units=[fx.unit_k01()], source_root=str(tmp_path))
    target = tmp_path / "state.json"
    _write_state_file(cp, target, state)
    output = tmp_path / "handoff.md"
    cp.export(target, output)
    text = output.read_text(encoding="utf-8")
    assert "chưa được gắn với gốc phạm vi đã kiểm" not in text


def _many_lines_book(fx, count=20000):
    lines = [f"Dòng đệm {i} cho nguồn dài." for i in range(1, count - 1)]
    lines.append("Dòng áp cuối giữ mốc kiểm tra.")
    lines.append("Dòng cuối cùng của nguồn dài.")
    return fx.write_book(lines, "many.txt"), count


def test_cp_a05_validate_reads_citation_near_end_of_long_source(cp, fx):
    """RT/CP-A05: validate() đọc theo luồng — trích dẫn ở cuối nguồn nhiều
    dòng (kể cả excerpt vắt qua hai dòng) vẫn kiểm đúng mà không cần nạp
    toàn bộ lines; mức RAM được đo riêng bằng script nghiệm thu."""
    book, count = _many_lines_book(fx)
    unit = fx.unit_k01()
    unit["citations"] = [{
        "source_id": "S01", "line_start": count - 1, "line_end": count,
        "excerpt": "giữ mốc kiểm tra.\nDòng cuối cùng của nguồn dài",
    }]
    state = fx.state(book, units=[unit])
    assert cp.validate(state) is state


def test_cp_a05_validate_rejects_excerpt_missing_near_end_of_long_source(cp, fx):
    """RT/CP-A05: excerpt không có ở khoảng dòng cuối của nguồn dài vẫn bị
    chặn với đúng thông điệp như bản nạp toàn bộ lines."""
    book, count = _many_lines_book(fx)
    unit = fx.unit_k01()
    unit["citations"] = [{
        "source_id": "S01", "line_start": count - 1, "line_end": count,
        "excerpt": "Đoạn trích hoàn toàn không tồn tại ở đây",
    }]
    state = fx.state(book, units=[unit])
    assert_raises(cp.InvalidCheckpoint, "Excerpt not found in cited lines",
                  cp.validate, state)


def test_cp_a05_validate_rejects_source_with_single_line_over_cap(cp, fx,
                                                                  tmp_path):
    """RT/CP-A05 (biến thể canonical): file mà một dòng đơn vượt
    MAX_LINE_BYTES (như file 256 MB toàn NUL không newline của Red Team)
    bị validate chặn sạch bằng thông điệp giới hạn dòng, thay vì dòng đó
    được nạp trọn vào RAM."""
    path = tmp_path / "one_long_line.txt"
    with path.open("w", encoding="utf-8") as stream:
        stream.write("Dòng mở đầu ngắn.\n")
        stream.write("x" * (cp.MAX_LINE_BYTES + 1))
    state = fx.state(path)
    assert_raises(cp.InvalidCheckpoint, "Source line exceeds maximum length",
                  cp.validate, state)


def test_cp_a05_validate_accepts_multiline_source_of_several_mb(cp, fx):
    """RT/CP-A05: file nhiều dòng với tổng dung lượng vài MB vẫn validate
    bình thường — cap độ dài dòng không gây hồi quy cho nguồn hợp lệ, và
    trích dẫn ở dòng cuối vẫn kiểm đúng."""
    lines = ["Dòng đệm " + "y" * 1000 + f" {i}" for i in range(1, 6000)]
    lines.append("Dòng cuối cùng của nguồn dài.")
    book = fx.write_book(lines, "several_mb.txt")
    assert book.stat().st_size > 5 * 1024 * 1024
    unit = fx.unit_k01()
    unit["citations"] = [{
        "source_id": "S01", "line_start": len(lines), "line_end": len(lines),
        "excerpt": "Dòng cuối cùng của nguồn dài",
    }]
    state = fx.state(book, units=[unit])
    assert cp.validate(state) is state
