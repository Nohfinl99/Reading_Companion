Trong fixture mô phỏng S, Method B đạt 60% thu hồi tài liệu tham khảo, so với baseline 40% trong cùng corpus và quy tắc chấm. Chênh lệch là 20 điểm phần trăm (tương đương 50% tương đối so với mức 40%), nhưng đây chỉ là reference recovery của mô phỏng. Fixture nói rõ thử nghiệm không đo tính đúng sự thật của mọi claim; không thể kết luận Method B làm mọi claim đúng hơn 20%.

CE: dòng 2–5 hỗ trợ so sánh thu hồi tài liệu trong điều kiện mô phỏng, không hỗ trợ suy rộng về factual accuracy. Phạm vi đọc là fixture được cấp, không phải nghiên cứu ngoài.

GateRecord — G-CITATION-REVIEW (SC05)
- record_id: SC05-CE-T01; target: diễn giải kết quả Method B; status: PARTIAL; readiness: PARTIAL
- source_spans: fixture.txt, dòng 2–5. output_spans: đoạn diễn giải và CE ở trên.
- checks:
  - CR01 Source — PASS: locator dòng 2–5 đã đọc trong fixture mô phỏng; không khẳng định truy cập nguồn khác.
  - CR02 Support — PASS: giữ đúng 60%, 40%, cùng thiết lập và giới hạn không đo factual correctness.
  - CR03 Epistemic boundary — PASS: không biến recovery thành độ đúng claim hoặc hiệu quả phổ quát.
  - CR04 IA and provenance — PASS: không tạo unit, selection hay quan hệ mới.
  - CR05 Reading state — PASS: giữ mode extract; không tạo quiz hay thay đổi state.
  - CR06 Final delta — PASS: câu trả lời cuối khớp các dòng nguồn nêu trên; không có sửa đổi nghĩa sau rà soát.
- unresolved: chỉ fixture tổng hợp được cấp; không có bằng chứng thực nghiệm ngoài fixture.
- repair_owner: CE04/R14 nếu mở rộng claim; không cần sửa cho phạm vi hiện tại.
- reviewer: assistant_authored_self_review; đây không phải review độc lập. Mechanical/host/independent review: NOT_RUN; learner outcome: NOT_APPLICABLE.
