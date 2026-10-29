# Luna rerun — 2026-10-29

[Roadmap](../../../docs/citeguard/roadmap.md) quy định thứ tự kiểm và điều kiện cập nhật GitHub. Input và rubric được lưu trước lượt chạy. Raw outputs thuộc runner; review records thuộc primary reviewer.

- `inputs.json`: chỉ input/context, không expected answer.
- `rubric.json`: tiêu chí riêng của reviewer, runner được chỉ dẫn không đọc.
- `source-audit.json`: kiểm nguồn/version/locator và visual scope.
- `raw/`: output Luna nguyên bản, không ghi đè sau grading.
- `run-manifest.json`: execution context và fingerprints.
- `review.json`: nhận xét và evidence của primary reviewer.
- `verification.json`: kết quả kiểm cơ học thực sự đã chạy.

Đây là delegated model prompt run, không installed-plugin host run. Việc tách runner/reviewer giảm vòng tự chấm cùng tác giả; cùng workspace không bảo đảm isolation hoặc independent external validation. Nhiều case trong một lượt không chứng minh reliability tổng thể.
