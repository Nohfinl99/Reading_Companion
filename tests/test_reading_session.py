"""Test cho reading_session.py — theo spec_checkpoint_session.md, RS-01…RS-60.

Quy ước: mỗi test chứa ID của spec trong tên; case âm assert cả loại exception
(InvalidSession) lẫn thông điệp lỗi chính xác. validate(session, sources,
units, pending) nhận sources là dict {source_id: [dòng]} (FX-SRC-LINES).
"""
from copy import deepcopy
from datetime import datetime, timedelta, timezone

import pytest

from conftest import BOOK_LINES, BOOK7_LINES, Q01, loc


def assert_raises(exc_type, message, fn, *args, **kwargs):
    with pytest.raises(exc_type) as excinfo:
        fn(*args, **kwargs)
    assert str(excinfo.value) == message


UNITS = [{"id": "K01"}, {"id": "K02"}]


def future_iso(days=1):
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


# ===========================================================================
# 2B.1 validate — khung session và chapter index — RS-01…RS-10
# ===========================================================================

@pytest.mark.parametrize("bad", [[], "session", 3])
def test_rs_01_validate_session_must_be_object(rs, fx, bad):
    assert_raises(rs.InvalidSession, "reading_session must be an object",
                  rs.validate, bad, fx.lines(), [], None)


def test_rs_02_validate_nav1_passes(rs, fx):
    session = fx.session_nav1()
    assert rs.validate(session, fx.lines(), [], None) is session


def test_rs_02_validate_missing_field(rs, fx):
    session = fx.session_nav1()
    del session["visited"]
    assert_raises(rs.InvalidSession, "Unsupported session version/fields",
                  rs.validate, session, fx.lines(), [], None)


def test_rs_02_validate_extra_field(rs, fx):
    session = fx.session_nav1()
    session["extra"] = 1
    assert_raises(rs.InvalidSession, "Unsupported session version/fields",
                  rs.validate, session, fx.lines(), [], None)


@pytest.mark.parametrize("version", [2, "1"])
def test_rs_02_validate_bad_version(rs, fx, version):
    session = fx.session_nav1()
    session["version"] = version
    assert_raises(rs.InvalidSession, "Unsupported session version/fields",
                  rs.validate, session, fx.lines(), [], None)


def test_rs_03_validate_invalid_reading_style(rs, fx):
    session = fx.session_nav1()
    session["reading_style"] = "fast"
    assert_raises(rs.InvalidSession, "Invalid reading style",
                  rs.validate, session, fx.lines(), [], None)


def test_rs_04_validate_index_extra_field(rs, fx):
    session = fx.session_nav1()
    session["chapter_index"]["extra"] = 1
    assert_raises(rs.InvalidSession, "Invalid chapter index",
                  rs.validate, session, fx.lines(), [], None)


@pytest.mark.parametrize("over,message", [
    ({"status": "full"}, "Invalid index status/scope"),
    ({"scope": " "}, "Invalid index status/scope"),
    ({"chapters": {}}, "chapters must be a list"),
])
def test_rs_04_validate_index_invalid(rs, fx, over, message):
    session = fx.session_nav1()
    session["chapter_index"].update(over)
    assert_raises(rs.InvalidSession, message,
                  rs.validate, session, fx.lines(), [], None)


def test_rs_05_validate_unknown_with_chapters(rs, fx):
    session = fx.session_empty()
    session["chapter_index"]["status"] = "unknown"
    assert_raises(rs.InvalidSession, "Unknown index cannot assert chapters",
                  rs.validate, session, fx.lines(), [], None)


def test_rs_05_validate_complete_without_chapters(rs, fx):
    session = fx.session_empty()
    session["chapter_index"]["chapters"] = []
    assert_raises(rs.InvalidSession, "Complete index cannot be empty",
                  rs.validate, session, fx.lines(), [], None)


def test_rs_05_validate_unknown_empty_passes(rs, fx):
    session = fx.session_empty(
        {"status": "unknown", "scope": "Chưa rõ", "chapters": []})
    assert rs.validate(session, fx.lines(), [], None) is session


def test_rs_06_validate_chapter_extra_field(rs, fx):
    session = fx.session_nav1()
    session["chapter_index"]["chapters"][0]["extra"] = 1
    assert_raises(rs.InvalidSession, "Invalid chapter fields",
                  rs.validate, session, fx.lines(), [], None)


@pytest.mark.parametrize("over,message", [
    ({"title": " "}, "Duplicate/empty chapter"),
    ({"ordinal": 0}, "Invalid chapter ordinal"),
    ({"ordinal": "1"}, "Invalid chapter ordinal"),
])
def test_rs_06_validate_chapter_invalid(rs, fx, over, message):
    session = fx.session_nav1()
    session["chapter_index"]["chapters"][0].update(over)
    assert_raises(rs.InvalidSession, message,
                  rs.validate, session, fx.lines(), [], None)


def test_rs_06_validate_duplicate_chapter_id(rs, fx):
    session = fx.session_nav1()
    chapter = deepcopy(session["chapter_index"]["chapters"][1])
    chapter["id"] = "CH1"
    chapter["locator"] = loc("CH1", 4, 5)
    session["chapter_index"]["chapters"][1] = chapter
    assert_raises(rs.InvalidSession, "Duplicate/empty chapter",
                  rs.validate, session, fx.lines(), [], None)


def test_rs_06_validate_duplicate_chapter_ordinal(rs, fx):
    session = fx.session_nav1()
    session["chapter_index"]["chapters"][1]["ordinal"] = 1
    assert_raises(rs.InvalidSession, "Duplicate chapter ordinal",
                  rs.validate, session, fx.lines(), [], None)


def test_rs_07_validate_chapter_locator_mismatch(rs, fx):
    session = fx.session_nav1()
    session["chapter_index"]["chapters"][0]["locator"] = loc("CHX", 1, 3)
    assert_raises(rs.InvalidSession, "Chapter locator mismatch",
                  rs.validate, session, fx.lines(), [], None)


def test_rs_07_validate_heading_not_at_start(rs, fx):
    session = fx.session_nav1()
    session["chapter_index"]["chapters"][0]["heading_excerpt"] = "Không có"
    assert_raises(rs.InvalidSession, "Chapter heading not at start locator",
                  rs.validate, session, fx.lines(), [], None)


def test_rs_07_validate_unordered_chapters(rs, fx):
    session = fx.session_nav1()
    chapters = session["chapter_index"]["chapters"]
    session["chapter_index"]["chapters"] = [chapters[1], chapters[0]]
    assert_raises(rs.InvalidSession, "Unordered/overlapping chapter index",
                  rs.validate, session, fx.lines(), [], None)


def test_rs_07_validate_overlapping_chapters(rs, fx):
    session = fx.session_nav1()
    chapter = session["chapter_index"]["chapters"][1]
    chapter["locator"] = loc("CH2", 3, 5)
    chapter["heading_excerpt"] = "Ngoại lệ"
    assert_raises(rs.InvalidSession, "Unordered/overlapping chapter index",
                  rs.validate, session, fx.lines(), [], None)


def test_rs_08_locator_helper_ok(rs, fx):
    assert rs.locator(loc("CH1", 1, 3), fx.lines()) is None


def test_rs_08_locator_must_be_object(rs, fx):
    assert_raises(rs.InvalidSession, "Locator must be an object",
                  rs.locator, "CH1", fx.lines())


def test_rs_08_locator_extra_field(rs, fx):
    bad = loc("CH1", 1, 3)
    bad["extra"] = 1
    assert_raises(rs.InvalidSession, "Invalid locator fields",
                  rs.locator, bad, fx.lines())


def test_rs_08_locator_unknown_source(rs, fx):
    assert_raises(rs.InvalidSession, "Unknown locator source/chapter",
                  rs.locator, loc("CH1", 1, 3, "S99"), fx.lines())


def test_rs_08_locator_invalid_lines(rs, fx):
    assert_raises(rs.InvalidSession, "Invalid locator lines",
                  rs.locator, loc("CH1", 1, 6), fx.lines())


def test_rs_09_validate_cursor_chapter_missing(rs, fx):
    session = fx.session_nav1()
    session["cursor"] = loc("CH99", 1, 2)
    assert_raises(rs.InvalidSession, "Locator chapter missing from index",
                  rs.validate, session, fx.lines(), [], None)


def test_rs_09_validate_cursor_outside_chapter(rs, fx):
    session = fx.session_nav1()
    session["cursor"] = loc("CH1", 4, 4)
    assert_raises(rs.InvalidSession, "Locator outside chapter",
                  rs.validate, session, fx.lines(), [], None)


@pytest.mark.parametrize("key", ["navigation_history", "visited",
                                 "paused_questions", "connections"])
def test_rs_10_validate_session_lists_required(rs, fx, key):
    session = fx.session_nav1()
    session[key] = {}
    assert_raises(rs.InvalidSession, f"{key} must be a list",
                  rs.validate, session, fx.lines(), [], None)


# ===========================================================================
# 2B.2 validate — history, visited, paused, context, connections — RS-11…RS-22
# ===========================================================================

def test_rs_11_validate_duplicate_visited(rs, fx):
    session = fx.session_nav1()
    session["visited"].append(deepcopy(session["visited"][0]))
    assert_raises(rs.InvalidSession, "Duplicate visited locator",
                  rs.validate, session, fx.lines(), [], None)


def test_rs_11_validate_visited_lacks_history(rs, fx):
    session = fx.session_nav1()
    session["visited"].append(loc("CH2", 4, 4))
    assert_raises(rs.InvalidSession, "Visited locator lacks access history",
                  rs.validate, session, fx.lines(), [], None)


def test_rs_12_validate_event_extra_field(rs, fx):
    session = fx.session_nav2()
    session["navigation_history"][0]["extra"] = 1
    assert_raises(rs.InvalidSession, "Invalid navigation event",
                  rs.validate, session, fx.lines(), [], None)


@pytest.mark.parametrize("over", [{"action": "skip"}, {"resume_note": " "}])
def test_rs_12_validate_event_invalid_action_or_note(rs, fx, over):
    session = fx.session_nav2()
    session["navigation_history"][0].update(over)
    assert_raises(rs.InvalidSession, "Invalid navigation action/note",
                  rs.validate, session, fx.lines(), [], None)


def test_rs_12_validate_history_must_be_continuous(rs, fx):
    session = fx.session_nav2()
    session["navigation_history"][1]["from"] = loc("CH1", 1, 2)
    assert_raises(rs.InvalidSession,
                  "Navigation history must form a continuous path",
                  rs.validate, session, fx.lines(), [], None)


def _session_3ch(fx, events, visited, cursor):
    session = fx.session_empty(fx.index3())
    session["navigation_history"] = events
    session["visited"] = visited
    session["cursor"] = cursor
    return session


def test_rs_13_validate_next_skips_chapter(rs, fx):
    first = loc("CH1", 1, 1)
    target = loc("CH3", 6, 6)
    events = [{"action": "read", "from": None, "to": deepcopy(first),
               "resume_note": "Đọc."},
              {"action": "next", "from": deepcopy(first), "to": deepcopy(target),
               "resume_note": "Tiếp."}]
    session = _session_3ch(fx, events, [first, target], target)
    assert_raises(rs.InvalidSession, "Navigation skipped an unverified chapter",
                  rs.validate, session, fx.lines(BOOK7_LINES), [], None)


def test_rs_13_validate_back_mislabeled_as_next(rs, fx):
    ch1 = loc("CH1", 1, 1)
    ch2 = loc("CH2", 4, 4)
    events = [{"action": "read", "from": None, "to": deepcopy(ch1),
               "resume_note": "Đọc."},
              {"action": "next", "from": deepcopy(ch1), "to": deepcopy(ch2),
               "resume_note": "Tiếp."},
              {"action": "next", "from": deepcopy(ch2), "to": deepcopy(ch1),
               "resume_note": "Lại."}]
    session = fx.session_nav2()
    session["navigation_history"] = events
    session["cursor"] = deepcopy(ch1)
    assert_raises(rs.InvalidSession, "Navigation skipped an unverified chapter",
                  rs.validate, session, fx.lines(), [], None)


def test_rs_13_validate_adjacent_needs_same_source(rs, fx):
    lines = {"S01": list(BOOK_LINES), "S02": list(BOOK_LINES)}
    index = {"status": "complete", "scope": "Hai nguồn", "chapters": [
        {"id": "CH1", "title": "Mở đầu", "ordinal": 1,
         "locator": loc("CH1", 1, 3), "heading_excerpt": "# Chương 1 — Mở đầu"},
        {"id": "CH2", "title": "Mở đầu B", "ordinal": 2,
         "locator": loc("CH2", 1, 3, "S02"),
         "heading_excerpt": "# Chương 1 — Mở đầu"}]}
    first = loc("CH1", 1, 1)
    target = loc("CH2", 1, 1, "S02")
    session = fx.session_empty(index)
    session["navigation_history"] = [
        {"action": "read", "from": None, "to": deepcopy(first),
         "resume_note": "Đọc."},
        {"action": "next", "from": deepcopy(first), "to": deepcopy(target),
         "resume_note": "Tiếp."}]
    session["visited"] = [deepcopy(first), deepcopy(target)]
    session["cursor"] = deepcopy(target)
    assert_raises(rs.InvalidSession, "Adjacent navigation needs same source",
                  rs.validate, session, lines, [], None)


def test_rs_14_validate_history_target_must_be_visited(rs, fx):
    session = fx.session_nav1()
    session["visited"] = []
    assert_raises(rs.InvalidSession, "History target must be a visited locator",
                  rs.validate, session, fx.lines(), [], None)


def test_rs_14_validate_cursor_must_match_history(rs, fx):
    session = fx.session_nav1()
    session["cursor"] = loc("CH1", 1, 2)
    assert_raises(rs.InvalidSession, "Cursor must match navigation history",
                  rs.validate, session, fx.lines(), [], None)


def test_rs_14_validate_cursor_with_empty_history(rs, fx):
    session = fx.session_empty()
    session["cursor"] = loc("CH1", 1, 1)
    assert_raises(rs.InvalidSession, "Cursor must match navigation history",
                  rs.validate, session, fx.lines(), [], None)


def _validate_session(rs, fx, session, pending=None, units=UNITS):
    return rs.validate(session, fx.lines(), units, pending)


def test_rs_15_validate_paused_row_extra_field(rs, fx):
    session = fx.session_paused()
    session["paused_questions"][0]["extra"] = 1
    assert_raises(rs.InvalidSession, "Invalid paused question",
                  _validate_session, rs, fx, session)


def test_rs_15_validate_paused_question_extra_key(rs, fx):
    session = fx.session_paused()
    session["paused_questions"][0]["question"]["answer"] = "…"
    assert_raises(rs.InvalidSession, "Question must contain only id/prompt",
                  _validate_session, rs, fx, session)


def test_rs_15_validate_paused_question_empty_prompt(rs, fx):
    session = fx.session_paused()
    session["paused_questions"][0]["question"]["prompt"] = " "
    assert_raises(rs.InvalidSession, "Empty question",
                  _validate_session, rs, fx, session)


def test_rs_16_validate_paused_duplicate_id(rs, fx):
    session = fx.session_paused()
    session["paused_questions"].append(
        deepcopy(session["paused_questions"][0]))
    assert_raises(rs.InvalidSession, "Duplicate active/paused question",
                  _validate_session, rs, fx, session)


def test_rs_16_validate_paused_id_clashes_with_pending(rs, fx):
    session = fx.session_paused()
    assert_raises(rs.InvalidSession, "Duplicate active/paused question",
                  _validate_session, rs, fx, session, deepcopy(Q01))


def test_rs_16_validate_paused_bad_reason(rs, fx):
    session = fx.session_paused()
    session["paused_questions"][0]["reason"] = "later"
    assert_raises(rs.InvalidSession, "Invalid pause note/reason",
                  _validate_session, rs, fx, session)


def test_rs_16_validate_paused_bad_support(rs, fx):
    session = fx.session_paused()
    session["paused_questions"][0]["support"] = "full"
    assert_raises(rs.InvalidSession, "Invalid question support",
                  _validate_session, rs, fx, session)


def test_rs_17_validate_pending_context_without_pending(rs, fx):
    session = fx.session_pending()
    assert_raises(rs.InvalidSession, "Invalid pending context",
                  _validate_session, rs, fx, session, None)


def test_rs_17_validate_pending_context_extra_field(rs, fx):
    session = fx.session_pending()
    session["pending_context"]["extra"] = 1
    assert_raises(rs.InvalidSession, "Invalid pending context",
                  _validate_session, rs, fx, session, deepcopy(Q01))


@pytest.mark.parametrize("over", [{"support": "full"}, {"resume_note": " "}])
def test_rs_17_validate_pending_context_invalid(rs, fx, over):
    session = fx.session_pending()
    session["pending_context"].update(over)
    assert_raises(rs.InvalidSession, "Invalid pending support/note",
                  _validate_session, rs, fx, session, deepcopy(Q01))


def _session_with_conn(fx, conn):
    session = fx.session_nav1()
    session["connections"] = [conn]
    return session


def test_rs_18_validate_connection_ok(rs, fx):
    session = _session_with_conn(fx, fx.conn_book())
    assert _validate_session(rs, fx, session) is session


def test_rs_18_validate_connection_extra_field(rs, fx):
    conn = fx.conn_book()
    conn["extra"] = 1
    session = _session_with_conn(fx, conn)
    assert_raises(rs.InvalidSession, "Invalid connection fields",
                  _validate_session, rs, fx, session)


def test_rs_18_validate_connection_duplicate_id(rs, fx):
    session = fx.session_nav1()
    session["connections"] = [fx.conn_book(), fx.conn_book()]
    assert_raises(rs.InvalidSession, "Duplicate/empty connection ID",
                  _validate_session, rs, fx, session)


@pytest.mark.parametrize("over", [{"from": "K99"}, {"to": "K01"}])
def test_rs_18_validate_connection_broken_unit(rs, fx, over):
    conn = fx.conn_book()
    conn.update(over)
    if over.get("to") == "K01":
        conn["from"] = "K01"
    session = _session_with_conn(fx, conn)
    assert_raises(rs.InvalidSession, "Broken connection unit",
                  _validate_session, rs, fx, session)


@pytest.mark.parametrize("over,message", [
    ({"type": "causes"}, "Invalid connection type"),
    ({"basis": "guess"}, "Invalid connection basis"),
])
def test_rs_18_validate_connection_invalid_enums(rs, fx, over, message):
    conn = fx.conn_book()
    conn.update(over)
    session = _session_with_conn(fx, conn)
    assert_raises(rs.InvalidSession, message,
                  _validate_session, rs, fx, session)


@pytest.mark.parametrize("over,message", [
    ({"purpose": " "}, "Connection needs purpose/rationale"),
    ({"rationale": " "}, "Connection needs purpose/rationale"),
    ({"evidence": []}, "Connection evidence required"),
])
def test_rs_19_validate_connection_missing_parts(rs, fx, over, message):
    conn = fx.conn_book()
    conn.update(over)
    session = _session_with_conn(fx, conn)
    assert_raises(rs.InvalidSession, message,
                  _validate_session, rs, fx, session)


def test_rs_19_validate_connection_bad_evidence_kind(rs, fx):
    conn = fx.conn_book()
    conn["evidence"][0]["kind"] = "web"
    session = _session_with_conn(fx, conn)
    assert_raises(rs.InvalidSession, "Invalid connection evidence",
                  _validate_session, rs, fx, session)


def test_rs_19_validate_connection_empty_finding(rs, fx):
    conn = fx.conn_book()
    conn["evidence"][0]["finding"] = " "
    session = _session_with_conn(fx, conn)
    assert_raises(rs.InvalidSession, "Evidence finding required",
                  _validate_session, rs, fx, session)


def test_rs_20_validate_book_evidence_extra_field(rs, fx):
    conn = fx.conn_book()
    conn["evidence"][0]["extra"] = 1
    session = _session_with_conn(fx, conn)
    assert_raises(rs.InvalidSession, "Invalid book evidence fields",
                  _validate_session, rs, fx, session)


def test_rs_20_validate_book_evidence_excerpt_not_found(rs, fx):
    conn = fx.conn_book()
    conn["evidence"][0]["excerpt"] = "đoạn bịa không có trong nguồn"
    session = _session_with_conn(fx, conn)
    assert_raises(rs.InvalidSession, "Connection excerpt not found",
                  _validate_session, rs, fx, session)


def test_rs_21_validate_external_evidence_ok(rs, fx):
    session = _session_with_conn(fx, fx.conn_ext())
    assert _validate_session(rs, fx, session) is session


def test_rs_21_validate_external_evidence_extra_field(rs, fx):
    conn = fx.conn_ext()
    conn["evidence"][0]["extra"] = 1
    session = _session_with_conn(fx, conn)
    assert_raises(rs.InvalidSession, "Invalid external evidence fields",
                  _validate_session, rs, fx, session)


def test_rs_21_validate_external_evidence_bad_url(rs, fx):
    conn = fx.conn_ext()
    conn["evidence"][0]["url"] = "ftp://example.org/doc"
    session = _session_with_conn(fx, conn)
    assert_raises(rs.InvalidSession, "Invalid external evidence URL/title",
                  _validate_session, rs, fx, session)


def test_rs_21_validate_external_evidence_future_time(rs, fx):
    conn = fx.conn_ext()
    conn["evidence"][0]["checked_at"] = future_iso(1)
    session = _session_with_conn(fx, conn)
    assert_raises(rs.InvalidSession, "Invalid/future evidence time",
                  _validate_session, rs, fx, session)


def test_rs_21_validate_external_evidence_bad_timestamp(rs, fx):
    conn = fx.conn_ext()
    conn["evidence"][0]["checked_at"] = "abc"
    session = _session_with_conn(fx, conn)
    assert_raises(rs.InvalidSession, "Invalid evidence timestamp",
                  _validate_session, rs, fx, session)


def test_rs_22_validate_full_session_passes(rs, fx):
    session = fx.session_paused()
    session["pending_context"] = {"cursor": loc("CH1", 1, 1),
                                  "resume_note": "Đang chờ trả lời.",
                                  "support": "none"}
    session["connections"] = [fx.conn_book(), fx.conn_ext()]
    pending = {"id": "Q02", "prompt": "Câu hỏi tiếp theo?"}
    assert _validate_session(rs, fx, session, pending) is session


# ===========================================================================
# 2B.3 enable, pause, operate, progress — RS-23…RS-44
# ===========================================================================

def test_rs_23_enable_creates_session(rs, fx):
    state = fx.state()
    index = fx.index2()
    out = rs.enable(state, index)
    assert out["revision"] == state["revision"] + 1
    session = out["reading_session"]
    assert session["version"] == 1
    assert session["reading_style"] == "standard"
    assert session["chapter_index"] == index
    assert session["cursor"] is None and session["return_position"] is None
    assert session["pending_context"] is None
    for key in ("navigation_history", "visited", "paused_questions",
                "connections"):
        assert session[key] == []
    assert "reading_session" not in state
    index["chapters"].clear()
    assert len(session["chapter_index"]["chapters"]) == 2


def test_rs_24_enable_twice_rejected(rs, fx):
    state = fx.state_session()
    assert_raises(rs.InvalidSession, "Reading session already enabled",
                  rs.enable, state, fx.index2())


def test_rs_25_pause_with_context(rs, fx):
    state = fx.state_pending(support="none")
    rs.pause(state, "Ghi chú khác")
    session = state["reading_session"]
    assert state["pending_question"] is None
    assert session["pending_context"] is None
    assert session["paused_questions"] == [{
        "question": Q01, "cursor": loc("CH1", 1, 1),
        "resume_note": "Đang chờ trả lời.", "support": "none",
        "reason": "user_pause"}]


def test_rs_26_pause_without_context_defaults_unknown(rs, fx):
    state = fx.state_pending(with_context=False)
    rs.pause(state, "Ghi chú mới")
    row = state["reading_session"]["paused_questions"][0]
    assert row["support"] == "unknown"
    assert row["resume_note"] == "Ghi chú mới"
    assert row["cursor"] == loc("CH1", 1, 1)


def test_rs_27_pause_without_pending_is_noop(rs, fx):
    state = fx.state_session(fx.session_empty())
    snapshot = deepcopy(state)
    rs.pause(state, "Ghi chú")
    assert state == snapshot


def test_rs_28_operate_requires_enabled_session(rs, fx):
    state = fx.state()
    assert_raises(rs.InvalidSession, "Enable reading session first",
                  rs.operate, state, "style", value="chill")


def test_rs_29_operate_requires_note(rs, fx):
    state = fx.state_session()
    assert_raises(rs.InvalidSession, "Resume note required",
                  rs.operate, state, "style", value="chill", note="  ")


def test_rs_30_operate_unknown_action(rs, fx):
    state = fx.state_session()
    assert_raises(rs.InvalidSession, "Unknown session action",
                  rs.operate, state, "teleport")


def test_rs_31_operate_style_changes_and_bumps_revision(rs, fx):
    state = fx.state_session()
    out = rs.operate(state, "style", value="chill")
    assert out["reading_session"]["reading_style"] == "chill"
    assert out["revision"] == state["revision"] + 1


def test_rs_31_operate_style_same_value_no_revision_bump(rs, fx):
    state = fx.state_session()
    out = rs.operate(state, "style", value="standard")
    assert out == state
    assert out["revision"] == state["revision"]


def test_rs_31_operate_style_invalid(rs, fx):
    state = fx.state_session()
    assert_raises(rs.InvalidSession, "Invalid reading style",
                  rs.operate, state, "style", value="fast")


def test_rs_32_operate_pause_with_pending(rs, fx):
    state = fx.state_pending(support="hint")
    out = rs.operate(state, "pause", note="Tạm dừng")
    session = out["reading_session"]
    assert out["pending_question"] is None
    assert len(session["paused_questions"]) == 1
    assert session["paused_questions"][0]["reason"] == "user_pause"
    assert out["revision"] == state["revision"] + 1


def test_rs_32_operate_pause_without_pending(rs, fx):
    state = fx.state_session(fx.session_empty())
    assert_raises(rs.InvalidSession, "No pending question",
                  rs.operate, state, "pause")


def test_rs_33_operate_resume_restores_question(rs, fx):
    state = fx.state_paused(support="hint")
    out = rs.operate(state, "resume", value="Q01")
    session = out["reading_session"]
    assert out["pending_question"] == Q01
    assert session["pending_context"] == {
        "cursor": loc("CH1", 1, 1),
        "resume_note": "Tạm dừng để chuyển chương.", "support": "hint"}
    assert session["paused_questions"] == []
    assert out["revision"] == state["revision"] + 1


def test_rs_34_operate_resume_blocked_by_active_pending(rs, fx):
    state = fx.state_pending()
    assert_raises(rs.InvalidSession,
                  "Resolve/pause active question before resuming another",
                  rs.operate, state, "resume", value="Q01")


def test_rs_34_operate_resume_unknown_question(rs, fx):
    state = fx.state_paused()
    assert_raises(rs.InvalidSession, "Paused question not found",
                  rs.operate, state, "resume", value="Q99")


def test_rs_35_operate_connect_appends_record(rs, fx):
    state = fx.state_session()
    out = rs.operate(state, "connect", value={"id": "C09"})
    assert out["reading_session"]["connections"] == [{"id": "C09"}]
    assert out["revision"] == state["revision"] + 1


def test_rs_35_operate_connect_requires_dict(rs, fx):
    state = fx.state_session()
    assert_raises(rs.InvalidSession, "Connection record required",
                  rs.operate, state, "connect", value="C09")


def test_rs_36_operate_next_moves_cursor(rs, fx):
    state = fx.state_session(fx.session_nav1())
    out = rs.operate(state, "next", note="Đi tiếp")
    session = out["reading_session"]
    assert session["cursor"] == loc("CH2", 4, 4)
    assert session["return_position"] == loc("CH1", 1, 1)
    assert len(session["navigation_history"]) == 2
    event = session["navigation_history"][-1]
    assert event == {"action": "next", "from": loc("CH1", 1, 1),
                     "to": loc("CH2", 4, 4), "resume_note": "Đi tiếp"}
    assert loc("CH2", 4, 4) in session["visited"]
    assert out["revision"] == state["revision"] + 1


def test_rs_36_operate_next_pauses_pending_with_navigation_reason(rs, fx):
    book = fx.book()
    session = fx.session_pending(support="none")
    state = fx.state_session(session, book)
    state["pending_question"] = deepcopy(Q01)
    out = rs.operate(state, "next", note="Đi tiếp")
    session = out["reading_session"]
    assert out["pending_question"] is None
    assert session["paused_questions"][0]["reason"] == "navigation"
    assert session["paused_questions"][0]["question"] == Q01


def test_rs_37_operate_next_at_last_chapter(rs, fx):
    state = fx.state_session(fx.session_nav2())
    assert_raises(rs.InvalidSession,
                  "Adjacent chapter unavailable or boundary reached",
                  rs.operate, state, "next")


def test_rs_37_operate_back_at_first_chapter(rs, fx):
    state = fx.state_session(fx.session_nav1())
    assert_raises(rs.InvalidSession,
                  "Adjacent chapter unavailable or boundary reached",
                  rs.operate, state, "back")


def test_rs_37_operate_next_requires_cursor(rs, fx):
    state = fx.state_session(fx.session_empty())
    assert_raises(rs.InvalidSession, "Reading cursor required",
                  rs.operate, state, "next")


def test_rs_37_operate_navigation_requires_index(rs, fx):
    empty_index = {"status": "unknown", "scope": "Chưa rõ", "chapters": []}
    state = fx.state_session(fx.session_empty(empty_index))
    assert_raises(rs.InvalidSession, "Chapter index unavailable",
                  rs.operate, state, "next")


def test_rs_38_operate_jump_to_chapter(rs, fx):
    state = fx.state_session(fx.session_nav1())
    out = rs.operate(state, "jump", value="CH2", note="Nhảy")
    session = out["reading_session"]
    assert session["cursor"] == loc("CH2", 4, 4)
    assert session["navigation_history"][-1]["action"] == "jump"


def test_rs_38_operate_jump_to_current_is_noop(rs, fx):
    state = fx.state_session(fx.session_nav1())
    out = rs.operate(state, "jump", value="CH1", note="Nhảy")
    assert out == state
    assert out["revision"] == state["revision"]


def test_rs_38_operate_jump_unknown_chapter(rs, fx):
    state = fx.state_session(fx.session_nav1())
    assert_raises(rs.InvalidSession, "Requested chapter unavailable",
                  rs.operate, state, "jump", value="CH99")


def test_rs_39_operate_return_goes_back(rs, fx):
    state = fx.state_session(fx.session_nav1())
    moved = rs.operate(state, "next", note="Đi tiếp")
    back = rs.operate(moved, "return", note="Quay lại")
    session = back["reading_session"]
    assert session["cursor"] == loc("CH1", 1, 1)
    assert session["navigation_history"][-1]["action"] == "return"


def test_rs_39_operate_return_without_position(rs, fx):
    state = fx.state_session(fx.session_nav1())
    assert_raises(rs.InvalidSession, "No return position",
                  rs.operate, state, "return")


def test_rs_40_operate_read_moves_to_locator(rs, fx):
    state = fx.state_session(fx.session_empty())
    out = rs.operate(state, "read", value=loc("CH1", 2, 2), note="Mở đoạn")
    session = out["reading_session"]
    assert session["cursor"] == loc("CH1", 2, 2)
    event = session["navigation_history"][-1]
    assert event["action"] == "read" and event["from"] is None
    assert out["revision"] == state["revision"] + 1


def test_rs_40_operate_read_requires_locator_dict(rs, fx):
    state = fx.state_session(fx.session_empty())
    assert_raises(rs.InvalidSession, "Target locator required",
                  rs.operate, state, "read", value="CH1")


def test_rs_41_operate_does_not_mutate_input(rs, fx):
    state = fx.state_pending(support="none")
    snapshot = deepcopy(state)
    rs.operate(state, "next", note="Đi tiếp")
    rs.operate(state, "style", value="chill")
    assert state == snapshot


def test_rs_42_progress_without_session(rs, fx):
    state = fx.state(scope="Chương 1")
    result = rs.progress(state)
    assert result["cursor"] is None
    assert result["reading_style"] == "standard"
    assert result["accessed_chapters"] == []
    assert result["chapter_count_in_verified_scope"] is None
    assert result["scope"] == "Chương 1"
    assert result["paused_questions"] == []
    assert result["pending_question"] is None


def test_rs_43_progress_complete_index_counts_chapters(rs, fx):
    state = fx.state_session(fx.session_nav1())
    assert rs.progress(state)["chapter_count_in_verified_scope"] == 2


def test_rs_43_progress_partial_index_count_is_none(rs, fx):
    index = fx.index2()
    index["status"] = "partial"
    state = fx.state_session(fx.session_empty(index))
    assert rs.progress(state)["chapter_count_in_verified_scope"] is None


def test_rs_44_progress_filters_and_sorts(rs, fx):
    rows = [{"source_id": "S01", "section": "A", "status": "analyzed",
             "unit_ids": ["K01"]},
            {"source_id": "S01", "section": "B", "status": "merged",
             "unit_ids": ["K01"]},
            {"source_id": "S01", "section": "C", "status": "unprocessed",
             "unit_ids": []},
            {"source_id": "S01", "section": "D", "status": "missing_source",
             "unit_ids": []}]
    state = fx.state_session(fx.session_nav2(), coverage=rows,
                             assessments=[{"question_id": "Q01", "response": "x",
                                           "support": "none",
                                           "result": "independent"}])
    snapshot = deepcopy(state)
    result = rs.progress(state)
    assert result["accessed_chapters"] == ["CH1", "CH2"]
    assert result["processed_sections"] == rows[:2]
    assert result["remaining_recorded_sections"] == rows[2:]
    assert result["progress_basis"] == (
        "accessed locators / existing coverage / observed task responses; "
        "no book or mastery percentage")
    result["observed_assessments"].append({"question_id": "QX"})
    assert state == snapshot


# ===========================================================================
# 2B.4 guard_transition — RS-45…RS-60
# ===========================================================================

def _assessment(question_id="Q01", response="Câu trả lời thật",
                support="hint", result="assisted"):
    return {"question_id": question_id, "response": response,
            "support": support, "result": result}


def test_rs_45_guard_transition_without_sessions(rs, fx):
    book = fx.book()
    old = fx.state(book)
    new = fx.state(book)
    new["revision"] = 2
    assert rs.guard_transition(old, new) is None


def test_rs_46_guard_transition_enable_ok(rs, fx):
    old = fx.state()
    new = rs.enable(old, fx.index2())
    assert rs.guard_transition(old, new) is None


def test_rs_47_guard_transition_enable_must_preserve_fields(rs, fx):
    old = fx.state()
    new = rs.enable(old, fx.index2())
    new["goal"] = "Mục tiêu khác"
    assert_raises(rs.InvalidSession, "Enable must preserve existing checkpoint",
                  rs.guard_transition, old, new)


def test_rs_47_guard_transition_enable_cannot_invent_history(rs, fx):
    old = fx.state()
    new = rs.enable(old, fx.index2())
    new["reading_session"]["navigation_history"] = [
        {"action": "read", "from": None, "to": loc("CH1", 1, 1),
         "resume_note": "Bịa"}]
    assert_raises(rs.InvalidSession, "Enable cannot invent session history",
                  rs.guard_transition, old, new)


def test_rs_48_guard_transition_session_cannot_disappear(rs, fx):
    book = fx.book()
    old = fx.state_session(fx.session_nav1(), book)
    new = fx.state(book)
    assert_raises(rs.InvalidSession, "Reading session cannot disappear",
                  rs.guard_transition, old, new)


def test_rs_49_guard_transition_index_immutable(rs, fx):
    book = fx.book()
    old = fx.state_session(fx.session_nav1(), book)
    new = fx.state_session(fx.session_nav1(), book)
    new["reading_session"]["chapter_index"]["scope"] = "Phạm vi khác"
    assert_raises(rs.InvalidSession,
                  "Index replacement requires a new session/reimport",
                  rs.guard_transition, old, new)


def test_rs_50_guard_transition_history_cannot_shrink(rs, fx):
    book = fx.book()
    old = fx.state_session(fx.session_nav2(), book)
    new = fx.state_session(fx.session_nav2(), book)
    new["reading_session"]["navigation_history"] = \
        new["reading_session"]["navigation_history"][:1]
    assert_raises(rs.InvalidSession,
                  "Navigation history cannot disappear/change",
                  rs.guard_transition, old, new)


def test_rs_50_guard_transition_history_cannot_be_edited(rs, fx):
    book = fx.book()
    old = fx.state_session(fx.session_nav2(), book)
    new = fx.state_session(fx.session_nav2(), book)
    new["reading_session"]["navigation_history"][0]["resume_note"] = "Bị sửa"
    assert_raises(rs.InvalidSession,
                  "Navigation history cannot disappear/change",
                  rs.guard_transition, old, new)


def test_rs_50_guard_transition_visited_cannot_disappear(rs, fx):
    book = fx.book()
    old = fx.state_session(fx.session_nav2(), book)
    new = fx.state_session(fx.session_nav2(), book)
    new["reading_session"]["visited"] = new["reading_session"]["visited"][:1]
    assert_raises(rs.InvalidSession, "Visited locators cannot disappear",
                  rs.guard_transition, old, new)


def test_rs_50_guard_transition_connections_cannot_disappear(rs, fx):
    book = fx.book()
    session_old = fx.session_nav1()
    session_old["connections"] = [fx.conn_book()]
    old = fx.state_session(session_old, book)
    new = fx.state_session(fx.session_nav1(), book)
    assert_raises(rs.InvalidSession,
                  "Connection records cannot disappear/change",
                  rs.guard_transition, old, new)


def test_rs_50_guard_transition_appending_is_ok(rs, fx):
    book = fx.book()
    old = fx.state_session(fx.session_nav1(), book)
    new = fx.state_session(fx.session_nav2(), book)
    assert rs.guard_transition(old, new) is None


def test_rs_51_guard_transition_cursor_needs_navigation_event(rs, fx):
    book = fx.book()
    old = fx.state_session(fx.session_nav1(), book)
    new = fx.state_session(fx.session_nav1(), book)
    new["reading_session"]["cursor"] = loc("CH1", 1, 2)
    assert_raises(rs.InvalidSession, "Cursor movement needs navigation event",
                  rs.guard_transition, old, new)


def test_rs_52_guard_transition_navigation_cannot_mutate_content(rs, fx):
    book = fx.book()
    old = fx.state_session(fx.session_nav1(), book, units=[fx.unit_k01()])
    new = fx.state_session(fx.session_nav2(), book,
                           units=[fx.unit_k01(), fx.unit_k02()])
    assert_raises(rs.InvalidSession,
                  "Navigation cannot mutate content/coverage/assessment/mode",
                  rs.guard_transition, old, new)


def test_rs_52_guard_transition_cursor_must_match_final_event(rs, fx):
    book = fx.book()
    old = fx.state_session(fx.session_nav1(), book)
    new = fx.state_session(fx.session_nav2(), book)
    new["reading_session"]["cursor"] = loc("CH1", 1, 1)
    assert_raises(rs.InvalidSession,
                  "Navigation cursor must match final event",
                  rs.guard_transition, old, new)


def test_rs_53_guard_transition_assessments_immutable(rs, fx):
    book = fx.book()
    old = fx.state_session(fx.session_nav1(), book,
                           assessments=[_assessment(response="Gốc")])
    new = fx.state_session(fx.session_nav1(), book,
                           assessments=[_assessment(response="Bị sửa")])
    assert_raises(rs.InvalidSession,
                  "Observed assessments cannot disappear/change",
                  rs.guard_transition, old, new)


def test_rs_53_guard_transition_append_assessment_ok(rs, fx):
    book = fx.book()
    old = fx.state_session(fx.session_nav1(), book,
                           assessments=[_assessment(response="Gốc")])
    new = fx.state_session(
        fx.session_nav1(), book,
        assessments=[_assessment(response="Gốc"),
                     _assessment(question_id="Q02", response="Mới")])
    assert rs.guard_transition(old, new) is None


def test_rs_54_guard_transition_question_resolved_by_assessment(rs, fx):
    book = fx.book()
    old = fx.state_paused("hint", book)
    new = fx.state_session(fx.session_nav1(), book,
                           assessments=[_assessment(support="hint")])
    assert rs.guard_transition(old, new) is None


def test_rs_54_guard_transition_question_cannot_vanish(rs, fx):
    book = fx.book()
    old = fx.state_paused("hint", book)
    new = fx.state_session(fx.session_nav1(), book)
    assert_raises(rs.InvalidSession,
                  "Unanswered question cannot disappear/change",
                  rs.guard_transition, old, new)


@pytest.mark.parametrize("assessment", [
    _assessment(response=""),
    _assessment(question_id="Q99"),
])
def test_rs_54_guard_transition_resolution_needs_real_response(rs, fx,
                                                               assessment):
    book = fx.book()
    old = fx.state_paused("hint", book)
    new = fx.state_session(fx.session_nav1(), book, assessments=[assessment])
    assert_raises(rs.InvalidSession,
                  "Unanswered question cannot disappear/change",
                  rs.guard_transition, old, new)


def test_rs_55_guard_transition_paused_context_cannot_change(rs, fx):
    book = fx.book()
    old = fx.state_paused("hint", book)
    new = fx.state_paused("hint", book)
    new["reading_session"]["paused_questions"][0]["support"] = "none"
    assert_raises(rs.InvalidSession, "Paused question context cannot change",
                  rs.guard_transition, old, new)


def test_rs_55_guard_transition_resume_preserves_context(rs, fx):
    book = fx.book()
    old = fx.state_paused("hint", book)
    new = rs.operate(old, "resume", value="Q01")
    assert rs.guard_transition(old, new) is None


def test_rs_55_guard_transition_resume_context_mismatch(rs, fx):
    book = fx.book()
    old = fx.state_paused("hint", book)
    new = rs.operate(old, "resume", value="Q01")
    new["reading_session"]["pending_context"]["support"] = "none"
    assert_raises(rs.InvalidSession,
                  "Resumed question must preserve context/support",
                  rs.guard_transition, old, new)


def test_rs_56_guard_transition_paused_support_cannot_be_erased(rs, fx):
    book = fx.book()
    old = fx.state_paused("hint", book)
    new = fx.state_session(fx.session_nav1(), book,
                           assessments=[_assessment(support="none")])
    assert_raises(rs.InvalidSession,
                  "Assessment cannot erase paused question support",
                  rs.guard_transition, old, new)


def test_rs_56_guard_transition_paused_support_none_ok(rs, fx):
    book = fx.book()
    old = fx.state_paused("none", book)
    new = fx.state_session(fx.session_nav1(), book,
                           assessments=[_assessment(support="none",
                                                    result="independent")])
    assert rs.guard_transition(old, new) is None


def _paused_from_pending(rs, fx, support):
    """Dựng state mới: pending (context None) của old được pause sang paused."""
    book = fx.book()
    old = fx.state_pending(with_context=False, book=book)
    new = fx.state_session(fx.session_nav1(), book)
    new["reading_session"]["paused_questions"] = [{
        "question": deepcopy(Q01), "cursor": loc("CH1", 1, 1),
        "resume_note": "Tạm dừng", "support": support, "reason": "user_pause"}]
    return old, new


def test_rs_57_guard_transition_legacy_support_unknown_ok(rs, fx):
    old, new = _paused_from_pending(rs, fx, "unknown")
    assert rs.guard_transition(old, new) is None


def test_rs_57_guard_transition_legacy_support_must_stay_unknown(rs, fx):
    old, new = _paused_from_pending(rs, fx, "none")
    assert_raises(rs.InvalidSession,
                  "Legacy question support must remain unknown",
                  rs.guard_transition, old, new)


def test_rs_58_guard_transition_support_decrease_blocked(rs, fx):
    book = fx.book()
    old = fx.state_pending(support="hint", book=book)
    new = fx.state_pending(support="none", book=book)
    assert_raises(rs.InvalidSession, "Question support cannot decrease",
                  rs.guard_transition, old, new)


def test_rs_58_guard_transition_support_increase_ok(rs, fx):
    book = fx.book()
    old = fx.state_pending(support="none", book=book)
    new = fx.state_pending(support="hint", book=book)
    assert rs.guard_transition(old, new) is None


def test_rs_58_guard_transition_pending_context_cannot_disappear(rs, fx):
    book = fx.book()
    old = fx.state_pending(support="hint", book=book)
    new = fx.state_pending(support="hint", with_context=False, book=book)
    assert_raises(rs.InvalidSession,
                  "Pending context cannot disappear/change",
                  rs.guard_transition, old, new)


def test_rs_58_guard_transition_pending_context_note_locked(rs, fx):
    book = fx.book()
    old = fx.state_pending(support="hint", book=book)
    new = fx.state_pending(support="hint", book=book)
    new["reading_session"]["pending_context"]["resume_note"] = "Bị sửa"
    assert_raises(rs.InvalidSession,
                  "Pending context cannot disappear/change",
                  rs.guard_transition, old, new)


def test_rs_58_guard_transition_session_cursor_may_move_with_event(rs, fx):
    book = fx.book()
    old = fx.state_pending(support="none", book=book)
    new = fx.state_pending(support="none", book=book)
    session = new["reading_session"]
    target = loc("CH2", 4, 4)
    session["navigation_history"].append(
        {"action": "jump", "from": loc("CH1", 1, 1), "to": deepcopy(target),
         "resume_note": "Nhảy chương"})
    session["visited"].append(deepcopy(target))
    session["return_position"] = loc("CH1", 1, 1)
    session["cursor"] = deepcopy(target)
    # pending_context giữ nguyên cursor cũ — chỉ cursor của session đổi.
    assert rs.guard_transition(old, new) is None


def test_rs_59_guard_transition_pause_preserves_context(rs, fx):
    book = fx.book()
    old = fx.state_pending(support="hint", book=book)
    new = deepcopy(old)
    rs.pause(new, "Tạm dừng")
    assert rs.guard_transition(old, new) is None


def test_rs_59_guard_transition_pause_context_mismatch(rs, fx):
    book = fx.book()
    old = fx.state_pending(support="hint", book=book)
    new = deepcopy(old)
    rs.pause(new, "Tạm dừng")
    new["reading_session"]["paused_questions"][0]["support"] = "none"
    assert_raises(rs.InvalidSession, "Pause must preserve context/support",
                  rs.guard_transition, old, new)


def test_rs_60_guard_transition_pending_support_cannot_be_erased(rs, fx):
    book = fx.book()
    old = fx.state_pending(support="hint", book=book)
    new = fx.state_session(fx.session_nav1(), book,
                           assessments=[_assessment(support="none")])
    assert_raises(rs.InvalidSession,
                  "Assessment cannot erase question support",
                  rs.guard_transition, old, new)


def test_rs_60_guard_transition_pending_support_kept_ok(rs, fx):
    book = fx.book()
    old = fx.state_pending(support="hint", book=book)
    new = fx.state_session(fx.session_nav1(), book,
                           assessments=[_assessment(support="hint")])
    assert rs.guard_transition(old, new) is None


# ------------------------------------------------------- Red Team regressions

def test_cp_a04_parse_json_rejects_duplicate_keys(rs):
    assert_raises(rs.InvalidSession, "Duplicate JSON key: revision",
                  rs.parse_json, '{"revision": 3, "revision": 2}')
    assert_raises(rs.InvalidSession, "Duplicate JSON key: support",
                  rs.parse_json,
                  '{"outer": {"support": "hint", "support": "none"}}')


def test_cp_a05_read_json_rejects_oversize_input(rs, tmp_path, monkeypatch):
    path = tmp_path / "state.json"
    path.write_text('{"version": 1}', encoding="utf-8")
    monkeypatch.setattr(rs, "MAX_JSON_BYTES", 4)
    assert_raises(rs.InvalidSession, "JSON input exceeds the 4-byte limit",
                  rs.read_json, path)


@pytest.mark.parametrize("excerpt", ["C", "Cơ chế"])
def test_cp_a02_connection_excerpt_below_grounding_threshold(rs, fx, excerpt):
    # Both excerpts occur in the cited line; length/word count is the blocker.
    conn = fx.conn_book()
    conn["evidence"][0]["excerpt"] = excerpt
    session = _session_with_conn(fx, conn)
    assert_raises(rs.InvalidSession,
                  "Connection excerpt is too short to ground evidence",
                  _validate_session, rs, fx, session)


@pytest.mark.parametrize("old_support", ["none", "hint", "worked_example"])
def test_rs_a01_guard_transition_to_unknown_from_known_support_blocked(
        rs, fx, old_support):
    # RS-A01: "unknown" is loss of a known support state, not the top rank.
    book = fx.book()
    old = fx.state_pending(support=old_support, book=book)
    new = fx.state_pending(support="unknown", book=book)
    assert_raises(rs.InvalidSession, "Question support cannot decrease",
                  rs.guard_transition, old, new)


@pytest.mark.parametrize(("old_support", "new_support"), [
    ("unknown", "unknown"),
    # SUPERSESSION 2026-10-23 (issue #8): ("unknown","none") moved from
    # allowed to blocked — old expectation followed the RS-A01 rationale
    # in the docstring; superseded against SC04 (stack-contracts.md:55)
    # and R11 (reading-protocols.md:303). See CHANGELOG 'Continuity fix'.
    ("unknown", "hint"),
    ("unknown", "worked_example"),
    ("none", "hint"),
    ("hint", "worked_example"),
])
def test_rs_a01_guard_transition_support_gain_or_unknown_start_ok(
        rs, fx, old_support, new_support):
    book = fx.book()
    old = fx.state_pending(support=old_support, book=book)
    new = fx.state_pending(support=new_support, book=book)
    assert rs.guard_transition(old, new) is None


def test_rs_a01_guard_transition_unknown_to_none_blocked(rs, fx):
    # SUPERSESSION 2026-10-23 (issue #8): ("unknown","none") moved from
    # allowed to blocked — old expectation followed the RS-A01 rationale
    # in the docstring; superseded against SC04 (stack-contracts.md:55)
    # and R11 (reading-protocols.md:303). See CHANGELOG 'Continuity fix'.
    book = fx.book()
    old = fx.state_pending(support="unknown", book=book)
    new = fx.state_pending(support="none", book=book)
    assert_raises(rs.InvalidSession, "Question support cannot decrease",
                  rs.guard_transition, old, new)


@pytest.mark.parametrize("attached_support", ["none", "hint", "worked_example"])
def test_rs_a01_legacy_attach_context_known_support_blocked(
        rs, fx, attached_support):
    # Issue #8 (N2-B): a legacy question without context cannot be given
    # a known-support context while it stays pending.
    book = fx.book()
    old = fx.state_pending(with_context=False, book=book)
    new = fx.state_pending(support=attached_support, book=book)
    assert_raises(rs.InvalidSession,
                  "Legacy question support must remain unknown",
                  rs.guard_transition, old, new)


def test_rs_a01_legacy_attach_context_unknown_ok(rs, fx):
    book = fx.book()
    old = fx.state_pending(with_context=False, book=book)
    new = fx.state_pending(support="unknown", book=book)
    assert rs.guard_transition(old, new) is None


def test_rs_a01_legacy_direct_independent_blocked(rs, fx):
    # Issue #8 (B0): a legacy question cannot be resolved directly by an
    # independent assessment; its effective support is unknown.
    book = fx.book()
    old = fx.state_pending(with_context=False, book=book)
    new = fx.state_session(fx.session_nav1(), book,
                           assessments=[_assessment(support="none",
                                                    result="independent")])
    assert_raises(rs.InvalidSession,
                  "Assessment cannot erase question support",
                  rs.guard_transition, old, new)


@pytest.mark.parametrize(("context_support", "recorded_support"), [
    ("worked_example", "hint"),
    ("worked_example", "none"),
])
def test_rs_a01_assessment_support_downgrade_blocked(
        rs, fx, context_support, recorded_support):
    # Issue #8 (N1b): a resolving assessment may not record less support
    # than the question actually had.
    book = fx.book()
    old = fx.state_pending(support=context_support, book=book)
    new = fx.state_session(fx.session_nav1(), book,
                           assessments=[_assessment(
                               support=recorded_support)])
    assert_raises(rs.InvalidSession,
                  "Assessment cannot erase question support",
                  rs.guard_transition, old, new)


@pytest.mark.parametrize(("context_support", "recorded_support"), [
    ("worked_example", "worked_example"),
    ("hint", "worked_example"),
])
def test_rs_a01_assessment_support_equal_or_higher_ok(
        rs, fx, context_support, recorded_support):
    book = fx.book()
    old = fx.state_pending(support=context_support, book=book)
    new = fx.state_session(fx.session_nav1(), book,
                           assessments=[_assessment(
                               support=recorded_support)])
    assert rs.guard_transition(old, new) is None


def test_rs_a01_paused_assessment_support_downgrade_blocked(rs, fx):
    # Issue #8 (N1b, paused surface): same rule for paused questions.
    book = fx.book()
    old = fx.state_paused("worked_example", book)
    new = fx.state_session(fx.session_nav1(), book,
                           assessments=[_assessment(support="hint")])
    assert_raises(rs.InvalidSession,
                  "Assessment cannot erase paused question support",
                  rs.guard_transition, old, new)


def test_rs_a01_new_question_may_start_at_none(rs, fx):
    # R11 exception: a brand-new question with a clear criterion may
    # start with context support none.
    book = fx.book()
    old = fx.state_session(fx.session_nav1(), book)
    new = fx.state_pending(support="none", book=book)
    assert rs.guard_transition(old, new) is None
