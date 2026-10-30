# Contributing / Đóng góp

**Languages / Ngôn ngữ:** Tiếng Việt · English

## Tiếng Việt

Cảm ơn bạn đã đóng góp cho Reading Companion. Thay đổi cần giữ nguyên identity plugin, định tuyến, provenance nguồn, hợp đồng dữ liệu và trạng thái học có căn cứ. Bắt đầu từ [bản đồ tài liệu](docs/README.md), [danh mục artifact](docs/artifacts.vi.md) hoặc [ví dụ đầu ra](docs/examples/outputs.md).

### Nguyên tắc

- Sửa quy tắc tại file canonical sở hữu nó; tài liệu khác liên kết thay vì tạo hợp đồng song song.
- Giữ `deep`, `extract`, `combined`; mode và style là hai lựa chọn riêng.
- Không suy đoán nguồn, locator, ID/revision, checkpoint, câu trả lời hoặc mức độ mastery.
- Với tài liệu song ngữ, cập nhật bản tiếng Việt trước và bản tiếng Anh tương ứng trong cùng thay đổi; giữ nguyên technical identifiers.
- Phân biệt case specification, output, grading, semantic review, host test và learner outcome; dùng `NOT_RUN` khi chưa có bằng chứng.
- Phân biệt tài liệu repository với file runtime trong [allowlist](packaging/runtime-files.json). Chỉnh IA ở trang ngoài allowlist không tự cập nhật plugin; sửa file runtime cần build/verify và kiểm parity đúng release.

### Quy trình đề xuất

1. Fork repository và tạo branch riêng.
2. Xác định file canonical và các liên kết phụ thuộc trước khi sửa.
3. Cập nhật tài liệu VI/EN tương ứng, sơ đồ và liên kết nếu có.
4. Chạy các lệnh trong [quality guide](docs/quality.vi.md).
5. Trong pull request, nêu vấn đề, file đổi, kiểm tra đã chạy/chưa chạy và giới hạn còn lại.

```bash
git clone https://github.com/Nohfinl99/Reading_Companion.git
cd Reading_Companion
python tools/validate_repository.py
python -m compileall -q tools skills/sid-reading-companion/scripts
```

## English

Thank you for contributing to Reading Companion. Changes should preserve plugin identity, routing, source provenance, data contracts and evidence-backed learning state. Start with the [documentation map](docs/README.md), [artifact catalogue](docs/artifacts.en.md) or [output examples](docs/examples/outputs.md).

### Principles

- Change a rule in its canonical owner; other documents should link to it instead of creating competing contracts.
- Preserve `deep`, `extract` and `combined`; mode and style are separate choices.
- Do not infer sources, locators, IDs/revisions, checkpoints, answers or mastery.
- For bilingual docs, update the Vietnamese editorial source and its English counterpart in the same change; keep technical identifiers unchanged.
- Distinguish case specifications, outputs, grading, semantic review, host tests and learner outcomes; use `NOT_RUN` when evidence is absent.
- Distinguish repository documentation from runtime files in the [allowlist](packaging/runtime-files.json). IA edits outside that list do not update the plugin; runtime edits require build/verification and parity checks for the exact release.

### Suggested workflow

1. Fork the repository and create a dedicated branch.
2. Identify canonical owners and dependent links before editing.
3. Update the paired VI/EN documents, diagrams and links together.
4. Run the checks in the [quality guide](docs/quality.en.md).
5. In the pull request, describe the problem, changed files, checks run/not run and remaining limits.

```bash
git clone https://github.com/Nohfinl99/Reading_Companion.git
cd Reading_Companion
python tools/validate_repository.py
python -m compileall -q tools skills/sid-reading-companion/scripts
```

