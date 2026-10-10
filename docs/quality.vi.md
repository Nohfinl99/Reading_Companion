# Kiểm tra chất lượng và bằng chứng

[English version](quality.en.md) · [README](../README.md)

## Các lớp kiểm tra

| Lớp | Câu hỏi được trả lời | Nơi chạy/định nghĩa | Không chứng minh |
|---|---|---|---|
| Manifest và cấu trúc | JSON hợp lệ, file bắt buộc có, liên kết Markdown cục bộ tồn tại? | GitHub Actions và `tools/validate_repository.py` | Nội dung sách đúng hoặc package đã được host nạp |
| Helper smoke checks | Script Python biên dịch được và CLI có thể hiển thị `--help`? | GitHub Actions, Python 3.10–3.12 | Helper hiểu sách hoặc xác minh nguồn ngoài |
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
python -m compileall -q tools skills/sid-reading-companion/scripts
python skills/sid-reading-companion/scripts/ia_map.py --help
python skills/sid-reading-companion/scripts/knowledge_compiler.py --help
python skills/sid-reading-companion/scripts/checkpoint.py --help
python skills/sid-reading-companion/scripts/reading_session.py --help
```

Workflow [`validate.yml`](../.github/workflows/validate.yml) chạy các nhóm lệnh tương ứng trong ma trận Python 3.10, 3.11 và 3.12.

## Quy tắc báo cáo kết quả

1. Báo rõ artifact/version, môi trường, input, output và lớp kiểm tra.
2. Chỉ gọi một case đạt khi input, output và grading thực đều có; lưu bằng chứng có thể truy nguyên.
3. Dùng `NOT_RUN` cho lớp chưa thực hiện; `OUTPUT_CAPTURED_UNGRADED` không phải kết quả đạt.
4. Tách structural/helper, semantic review, render, installed-host và learner outcome.
5. Không dùng benchmark giả định hoặc self-review của cùng lượt chạy làm kết quả độc lập.

Các quy tắc case và evidence chi tiết nằm trong [benchmark specification](../skills/sid-reading-companion/references/case-benchmark.md). Hướng dẫn này mô tả cách kiểm; nó không công bố benchmark thành công hay chất lượng nội dung sách.
