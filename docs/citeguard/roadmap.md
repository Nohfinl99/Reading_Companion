# Roadmap chạy lại: kiểm nguồn → Luna → reviewer → GitHub

Ngày 2026-10-29, Asia/Bangkok. Baseline source candidate: `1473b1b928e590bdfffcda3d52d6f548ee8de51e`, draft PR #11. Đây là roadmap cho lượt kiểm lại, không phải kết quả đã chạy.

| Bước | Người thực hiện | Đầu vào → đầu ra | Gate chuyển tiếp |
|---|---|---|---|
| 1. Kiểm nguồn | Primary reviewer | PDF ACL gốc + SID V5 + package → source-audit.json | DOI/title/authors/version khớp; bảy unit và hai relations có locator; nêu rõ access/visual scope |
| 2. Đóng băng run | Primary reviewer | Candidate, input, fixture và rubric → fingerprints | Input không chứa expected answer; rubric được lưu trước khi Luna chạy; snapshot rõ phạm vi |
| 3. Luna thực hiện | gpt-6-luna được yêu cầu | Prompt CE + 10 input độc lập → raw outputs + run manifest | Lưu nguyên output trước grading; không đọc rubric/output cũ, không sửa runtime hoặc tự tuyên bố đạt independent review |
| 4. Reviewer chấm | Primary reviewer | Raw outputs + rubric + source → review records | Từng tiêu chí bắt buộc phải có output evidence; thiếu source giữ unresolved; không hợp thức hóa kết quả bằng sửa raw output |
| 5. Regression | Primary reviewer | Repo và run records → logs + report | Links/JSON/YAML, evidence fingerprints, CLI/compile và pytest Linux đạt; giữ các lớp evidence riêng |
| 6. Publication | Primary reviewer | Diff đã kiểm → cập nhật nhánh PR hiện có | Chỉ cập nhật khi source gate, run review và regression trong phạm vi đạt; kiểm lại head tránh ghi đè thay đổi khác |

Nếu phát hiện FAIL: lưu bản thô và finding; sửa đúng owner; thêm ca hồi quy nếu cần; chạy lại phần ảnh hưởng với run ID mới. Không sửa expected behavior để theo output. Không gọi PARTIAL hoặc NOT_RUN là PASS.

## Phạm vi và tiêu chí nghiệm thu

Luna chạy tám ca synthetic có sẵn và hai ca đọc/apply Knowledge Package. Mỗi ca là một invocation logic độc lập; đây là một lượt model với mười case, không mười lần lặp thống kê độc lập. Reviewer khác runner nhưng không blind với toàn bộ dự án; không phải kiểm định bên ngoài tổ chức.

Review cần đúng nguồn/metric/conditions, không bịa quyền truy cập hoặc tool, giữ mode/Q/support và chọn CE đúng tình huống. Ca thiếu PDF phải từ chối kết luận claim; ca Progress không được dựng state hoặc chạy CE. Những kết quả đó có thể đạt tiêu chí hành vi dù target vẫn BLOCKED hoặc gate không áp dụng.

Không kiểm installed-host activation, hiệu quả học dài hạn hoặc chất lượng/chi phí so baseline model. Không gửi tài liệu riêng hoặc gọi API trả phí. Không merge PR hoặc cập nhật account plugin trong roadmap này. Hồ sơ chạy mới nằm ở [luna-rerun-2026-10-29](../../evaluation/citeguard/luna-rerun-2026-10-29/README.md).
