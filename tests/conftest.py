"""Fixture dùng chung cho test của checkpoint.py và reading_session.py.

Đặc tả gốc: specs/spec_checkpoint_session.md (mục 4 — FX-*).
Hai helper được nạp bằng importlib.util.spec_from_file_location theo đường dẫn
tương đối từ repo root; checkpoint.py tự nạp reading_session.py theo vị trí
của nó, nên chỉ cần nạp checkpoint trước rồi lấy module session từ đó.
Mọi file nguồn/state đều nằm trong tmp_path; sha256 luôn tính lúc dựng fixture.
"""
import importlib.util
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "sid-reading-companion" / "scripts"


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


checkpoint = _load("sid_checkpoint_under_test", "checkpoint.py")
reading_session = checkpoint.reading_session


@pytest.fixture()
def cp():
    return checkpoint


@pytest.fixture()
def rs():
    return reading_session


# --- FX-SRC-BOOK (mục 4.1): đúng 5 dòng -------------------------------------
BOOK_LINES = [
    "# Chương 1 — Mở đầu",
    "X may improve Y under condition Z.",
    "Ngoại lệ: khi thiếu Z thì không áp dụng.",
    "# Chương 2 — Cơ chế",
    "Cơ chế A hỗ trợ cơ chế B.",
]
# Biến thể 7 dòng cho FX-INDEX-3CH (RS-13)
BOOK7_LINES = BOOK_LINES + ["# Chương 3 — Mở rộng", "Nội dung chương 3."]

Q01 = {"id": "Q01", "prompt": "Vì sao Z là điều kiện cần?"}


def loc(chapter_id, start, end, source_id="S01"):
    return {"source_id": source_id, "chapter_id": chapter_id,
            "line_start": start, "line_end": end}


class Fx:
    """Nhà máy dựng fixture theo mục 4 của spec, gắn với tmp_path của từng test."""

    def __init__(self, tmp_path):
        self.tmp = Path(tmp_path)

    # -- file nguồn -----------------------------------------------------------
    def write_book(self, lines=BOOK_LINES, name="book.txt"):
        path = self.tmp / name
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    def book(self):
        return self.write_book()

    def book7(self):
        return self.write_book(BOOK7_LINES, "book7.txt")

    def empty_book(self):
        path = self.tmp / "empty.txt"
        path.write_text("  \n\n", encoding="utf-8")
        return path

    # -- FX-SRC-LINES (mục 4.4) ----------------------------------------------
    @staticmethod
    def lines(lines=BOOK_LINES):
        return {"S01": list(lines)}

    # -- FX-STATE-MIN (mục 4.2) ------------------------------------------------
    def state(self, book=None, **over):
        book = book if book is not None else self.book()
        state = {
            "schema_version": 1,
            "revision": 1,
            "mode": "deep",
            "scope": "",
            "goal": "",
            "sources": [{"id": "S01", "path": str(book),
                         "sha256": checkpoint.sha256(book)}],
            "units": [],
            "coverage": [],
            "assessments": [],
            "pending_question": None,
            "limitations": [],
        }
        state.update(over)
        return state

    # -- unit mẫu (mục 4.2) -----------------------------------------------------
    @staticmethod
    def unit_k01():
        return {"id": "K01", "revision": 1, "title": "Điều kiện Z", "kind": "book",
                "content": "X may improve Y under condition Z.", "conditions": ["Z"],
                "citations": [{"source_id": "S01", "line_start": 2, "line_end": 2,
                               "excerpt": "X may improve Y under condition Z"}],
                "related": []}

    @staticmethod
    def unit_k02():
        return {"id": "K02", "revision": 1, "title": "Cơ chế", "kind": "book",
                "content": "Cơ chế A hỗ trợ cơ chế B.", "conditions": [],
                "citations": [{"source_id": "S01", "line_start": 5, "line_end": 5,
                               "excerpt": "Cơ chế A hỗ trợ cơ chế B"}],
                "related": []}

    @staticmethod
    def unit_curr():
        return {"id": "K03", "revision": 1, "title": "Nguồn ngoài",
                "kind": "current_source", "content": "Thông tin hiện hành.",
                "conditions": [], "citations": [], "related": [],
                "url": "https://example.org/a",
                "checked_at": "2026-01-01T00:00:00+07:00"}

    # -- FX-CURR-CONFIRMED (mục 4.3) -------------------------------------------
    @staticmethod
    def curr():
        return {
            "sensitivity": "dynamic",
            "status": "confirmed",
            "rationale": "Giá/API thay đổi theo thời gian",
            "original_claim": "Sách nói X dùng API v1",
            "current_conclusion": "Hiện tại là API v2",
            "applicability": "Chỉ áp dụng cho bản hosted",
            "assessed_at": "2026-01-02T00:00:00+07:00",
            "verified_at": "2026-01-01T12:00:00+07:00",
            "evidence": [{"url": "https://example.org/doc",
                          "title": "Tài liệu chính thức",
                          "finding": "API v2 là hiện hành",
                          "checked_at": "2026-01-01T10:00:00+07:00"}],
            "review_after": "2026-02-01T00:00:00+07:00",
        }

    # -- FX-INDEX-2CH / FX-INDEX-3CH (mục 4.4) ----------------------------------
    @staticmethod
    def index2():
        return {
            "status": "complete",
            "scope": "FX-SRC-BOOK dòng 1–5",
            "chapters": [
                {"id": "CH1", "title": "Mở đầu", "ordinal": 1,
                 "locator": loc("CH1", 1, 3), "heading_excerpt": "# Chương 1 — Mở đầu"},
                {"id": "CH2", "title": "Cơ chế", "ordinal": 2,
                 "locator": loc("CH2", 4, 5), "heading_excerpt": "# Chương 2 — Cơ chế"},
            ],
        }

    @staticmethod
    def index3():
        index = Fx.index2()
        index["chapters"].append(
            {"id": "CH3", "title": "Mở rộng", "ordinal": 3,
             "locator": loc("CH3", 6, 7), "heading_excerpt": "# Chương 3 — Mở rộng"})
        return index

    # -- session mẫu (mục 4.5) ---------------------------------------------------
    def session_empty(self, index=None):
        return {"version": 1, "reading_style": "standard",
                "chapter_index": deepcopy(index) if index is not None else self.index2(),
                "cursor": None, "return_position": None, "navigation_history": [],
                "visited": [], "paused_questions": [], "pending_context": None,
                "connections": []}

    def session_nav1(self):
        session = self.session_empty()
        cursor = loc("CH1", 1, 1)
        session["cursor"] = deepcopy(cursor)
        session["navigation_history"] = [
            {"action": "read", "from": None, "to": deepcopy(cursor),
             "resume_note": "Bắt đầu đọc."}]
        session["visited"] = [deepcopy(cursor)]
        return session

    def session_nav2(self):
        session = self.session_nav1()
        old_cursor = deepcopy(session["cursor"])
        target = loc("CH2", 4, 4)
        session["return_position"] = old_cursor
        session["cursor"] = deepcopy(target)
        session["navigation_history"].append(
            {"action": "next", "from": old_cursor, "to": deepcopy(target),
             "resume_note": "Chuyển chương."})
        session["visited"].append(deepcopy(target))
        return session

    def session_pending(self, support="none", with_context=True):
        session = self.session_nav1()
        if with_context:
            session["pending_context"] = {
                "cursor": loc("CH1", 1, 1), "resume_note": "Đang chờ trả lời.",
                "support": support}
        return session

    def session_paused(self, support="hint"):
        session = self.session_nav1()
        session["paused_questions"] = [{
            "question": deepcopy(Q01), "cursor": loc("CH1", 1, 1),
            "resume_note": "Tạm dừng để chuyển chương.", "support": support,
            "reason": "user_pause"}]
        return session

    # -- state chứa session (FX-STATE-SESSION, mục 4.5) ---------------------------
    def state_session(self, session=None, book=None, **over):
        state = self.state(book, **over)
        state["reading_session"] = session if session is not None else self.session_nav1()
        return state

    def state_pending(self, support="none", with_context=True, book=None):
        state = self.state_session(self.session_pending(support, with_context), book)
        state["pending_question"] = deepcopy(Q01)
        return state

    def state_paused(self, support="hint", book=None):
        return self.state_session(self.session_paused(support), book)

    # -- connection mẫu (mục 4.5) --------------------------------------------------
    @staticmethod
    def conn_book():
        return {"id": "C01", "from": "K01", "to": "K02", "type": "supports",
                "basis": "source_explicit", "purpose": "Nối điều kiện với cơ chế",
                "rationale": "Dòng 5 mô tả cơ chế dựa trên điều kiện dòng 2",
                "evidence": [{"kind": "book", "locator": loc("CH2", 5, 5),
                              "excerpt": "Cơ chế A hỗ trợ cơ chế B",
                              "finding": "Nguồn nêu rõ quan hệ hỗ trợ"}]}

    @staticmethod
    def conn_ext():
        conn = Fx.conn_book()
        conn["id"] = "C02"
        conn["evidence"] = [{"kind": "external", "url": "https://example.org/doc",
                             "title": "Tài liệu chính thức",
                             "checked_at": "2026-01-01T10:00:00+07:00",
                             "finding": "Nguồn ngoài xác nhận quan hệ hỗ trợ"}]
        return conn


@pytest.fixture()
def fx(tmp_path):
    return Fx(tmp_path)
