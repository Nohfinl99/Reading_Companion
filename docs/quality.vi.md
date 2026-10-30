# Kiểm tra chất lượng và bằng chứng

[English version](quality.en.md) · [Bản đồ tài liệu](README.md) · [README](../README.vi.md)

## Các lớp kiểm tra

| Lớp | Câu hỏi được trả lời | Nơi chạy/định nghĩa | Không chứng minh |
|---|---|---|---|
| Manifest và cấu trúc | JSON hợp lệ, file bắt buộc có, liên kết Markdown cục bộ tồn tại? | GitHub Actions và `tools/validate_repository.py` | Nội dung sách đúng hoặc package đã được host nạp |
| Helper smoke checks | Script Python biên dịch được và CLI có thể hiển thị `--help`? | GitHub Actions, Python 3.10–3.12 | Helper hiểu sách hoặc xác minh nguồn ngoài |
| Regression cơ học | Các guard state, hợp đồng, bundle và packaging có giữ hành vi trong những ca đã kiểm? | `pytest`, tests trong repository | Tính đúng nghĩa ngoài ca đã chạy hoặc response thật của người học |
| Integrity và SC05 | Source snapshot, raw output, rubric, review và gate sidecar có khớp identity/revision/spans? | Citation/Luna/gate/sync validators | Gate tự khai PASS có nghĩa đúng hoặc một reviewer độc lập đã chấm |
| Package tái lập | ZIP có đúng allowlist, source commit, metadata, file hashes và layout? | `build_plugin.py`, `verify_plugin_package.py` | Plugin tài khoản hoặc host đã nhận đúng ZIP |
| Case specification | Mỗi yêu cầu có ca, evidence và tiêu chí riêng chưa? | [Case benchmark](../skills/sid-reading-companion/references/case-benchmark.md) | Kết quả của lần chạy chưa có input/output/chấm |
| Output review | Output cụ thể có đúng nguồn, nghĩa, mapping, state và tiêu chí không? | Cần input, output và grading/review được lưu riêng | Host behavior hoặc kết quả học nếu chưa thử |
| Host evaluation | Plugin đã được host nạp và gọi đúng capability chưa? | Chạy riêng trên host tương thích | Learning outcome |
| Learner outcome | Người học có hiểu/nhớ/chuyển giao sau thời gian thực không? | Thiết kế nghiên cứu và dữ liệu người học phù hợp | Không thể suy ra từ prompt, output đơn lẻ hoặc helper test |

## Lệnh kiểm tra cục bộ

Chạy từ root repository:

```bash
python -m json.tool plugin.json
python -m json.tool .codex-plugin/plugin.json
python tools/validate_repository.py
python tools/validate_citation_evidence.py
python tools/validate_luna_rerun.py
python tools/validate_gate_records.py evaluation/citeguard/sync-0.3.7/sidecar.json --root evaluation/citeguard/sync-0.3.7 --expected-artifact artifact.md=1
python tools/validate_sync_evidence.py --root . --require-current-context
python -m pytest -q
python -m compileall -q tools skills/sid-reading-companion/scripts
python skills/sid-reading-companion/scripts/ia_map.py --help
python skills/sid-reading-companion/scripts/knowledge_compiler.py --help
python skills/sid-reading-companion/scripts/checkpoint.py --help
python skills/sid-reading-companion/scripts/reading_session.py --help
```

`pytest` và YAML tests cần dependencies như bước cài đặt trong [`validate.yml`](../.github/workflows/validate.yml). Workflow chạy các nhóm lệnh trên trong ma trận Python 3.10, 3.11 và 3.12, rồi build/verify runtime package từ `$GITHUB_SHA`.

```bash
python tools/build_plugin.py --root . --output ../reading-companion.zip --source-commit <commit-sha>
python tools/verify_plugin_package.py ../reading-companion.zip --manifest ../reading-companion.manifest.json
```

Thay `<commit-sha>` bằng commit nguồn thực. [Allowlist](../packaging/runtime-files.json) xác định file runtime; `tools/`, `tests/`, hồ sơ evaluation và phần lớn human docs chỉ thuộc repository. ZIP/manifest là artifact đóng gói, khác artifact đọc được mô tả trong [danh mục đầu ra](artifacts.vi.md).

Đầu ra CI dự kiến có tên `reading-companion-runtime` cho ZIP/manifest và `reading-companion-verification` cho hồ sơ kiểm. Kiểm trang của đúng workflow run để biết upload có thành công và file còn được lưu hay không; tên dự kiến không xác nhận đã tải xuống được. Đây cũng không tự là GitHub Release hay plugin đã được host nạp.

## Tìm bằng chứng đúng phiên bản

Tại lần đối chiếu 2026-10-29, `main` còn 0.3.5, còn [PR #11](https://github.com/Nohfinl99/Reading_Companion/pull/11) chứa source 0.3.7. Dùng commit của run để đối chiếu; không gộp trạng thái hai nhánh.

- [Correction record 0.3.7](citeguard/correction-plan.md): thay đổi và giới hạn bằng chứng.
- [Capture/review mới](../evaluation/citeguard/sync-0.3.7/README.md) và [release checks](../evaluation/citeguard/sync-0.3.7/release-checks.json): dữ liệu gắn candidate; đọc run/commit ghi trong hồ sơ.
- [Luna R3 lịch sử](../evaluation/citeguard/luna-rerun-2026-10-29-r3/README.md): behavioral rubric cũ; SC05 thiếu fields được giữ lại, không dùng PASS cũ để chứng nhận candidate mới.

Readback plugin tài khoản cần so từng file canonical với package đã kiểm. Installed-host activation và chuỗi nhiều lượt/phiên mới cần capture riêng trên đúng release; chúng không được suy ra từ CI hoặc readback.

## Quy tắc báo cáo kết quả

1. Báo rõ artifact/version, môi trường, input, output và lớp kiểm tra.
2. Chỉ gọi một case đạt khi input, output và grading thực đều có; lưu bằng chứng có thể truy nguyên.
3. Dùng `NOT_RUN` cho lớp chưa thực hiện; `OUTPUT_CAPTURED_UNGRADED` không phải kết quả đạt.
4. Tách structural/helper, semantic review, render, installed-host và learner outcome.
5. Không dùng benchmark giả định hoặc self-review của cùng lượt chạy làm kết quả độc lập.

Các quy tắc case và evidence chi tiết nằm trong [benchmark specification](../skills/sid-reading-companion/references/case-benchmark.md). Hướng dẫn này mô tả cách kiểm; nó không công bố benchmark thành công hay chất lượng nội dung sách.

