# Luna rerun — revision 3

Fresh context; same case inputs and rubric. Rechecks source binding, critical conditions and the canonical R10 missing-state boundary. Raw runner output is preserved before primary review.

Primary reviewer đã đối chiếu 10 output với 20 tiêu chí hành vi đã đóng băng: PASS trong phạm vi này. Xem [review.json](review.json), [run manifest](run-manifest.json), [verification](verification.json). Đây không phải citation accuracy tổng thể hay reliability estimate.

Luna tự ghi PARTIAL cho gate CE-T01 do thiếu evidence ngoài fixture. Raw PARTIAL được giữ; primary verdict chỉ kiểm diễn giải fixture đúng phạm vi, không biến nó thành bằng chứng host hoặc thực nghiệm. Ca CE-T07 thiếu state được xử lý là unknown; ca CE-T08 không tạo assessment hoặc mutation làm giảm support; persistence chưa thử.

Lịch sử không bị bỏ: [attempt 1](../luna-rerun-2026-10-29/review.json) và [attempt 2](../luna-rerun-2026-10-29-r2/review.json) vẫn FAIL. Source snapshots lịch sử được tái dựng/capture sau run rồi kiểm hash với input manifest, không giả là đã lưu trước run.

Run fingerprint dùng SHA-256 trên file bytes. `.gitattributes` giữ raw/context bytes; sau thay đổi context phải chạy lại thay vì tái dùng PASS cũ. `tools/validate_luna_rerun.py` kiểm provenance và tính bất biến, không hiểu nghĩa.
