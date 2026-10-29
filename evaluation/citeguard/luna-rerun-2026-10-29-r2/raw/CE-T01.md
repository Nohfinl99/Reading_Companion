Method B đạt **60% reference recovery** so với baseline **40%** trong mô phỏng S, dùng corpus và quy tắc chấm cố định: chênh lệch là **20 điểm phần trăm** (fixture.txt, dòng 2–4). Kết quả chỉ nói về khả năng khôi phục reference trong mô phỏng; thí nghiệm không đo mọi claim có đúng sự thật hay không (dòng 5). Không suy rộng thành mức cải thiện cho mọi claim hay bối cảnh khác.

**GateRecord — G-CITATION-REVIEW**
- artifact_ref/revision: CE-T01.md / bản trả lời này
- applicable: yes; reason: user yêu cầu rà gate sau khi áp dụng kiểm chứng nguồn
- status: PASS (self-review của cùng lượt; không phải independent review)
- source_spans: evaluation/citeguard/fixture.txt:2–5
- output_spans: phần giải thích kết quả ở trên
- checks:
  - CR01 Source — PASS: file fixture được đọc; đúng locator dòng 2–5; nguồn tự ghi là synthetic, không phải bài nghiên cứu.
  - CR02 Support — PASS: 60%, 40%, corpus/quy tắc cố định và giới hạn đo lường khớp dòng 2–5; phép trừ cho 20 điểm phần trăm.
  - CR03 Epistemic boundary — PASS: kết quả mô phỏng được tách khỏi sự thật của mọi claim; không gán kết quả cho SID.
  - CR04 IA and provenance — PASS: chỉ diễn giải đúng các dòng được hỏi; không tuyên bố đây là enumeration của tác giả hay chọn subset.
  - CR05 Reading state — PASS: giữ mode extract; không có câu hỏi learner/support cần thay đổi.
  - CR06 Final delta — PASS: câu trả lời cuối giữ các điều kiện và giới hạn nguồn; không thêm claim hiệu quả tổng quát.
- repair_owner: none
- unresolved: không có independent review; gate này chỉ áp dụng cho câu trả lời và các dòng nguồn nêu trên. Không có kiểm tra host/render/learner outcome.
