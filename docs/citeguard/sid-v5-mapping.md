# SID V5 design provenance

Nguồn do maintainer cung cấp trong workspace, được đọc ngày 2026-10-29 (Asia/Bangkok). Chỉ xuất mapping và fingerprint; không đưa toàn bộ tài liệu khóa học, đường dẫn máy cá nhân hay proposal riêng vào public repo. Fingerprint nhận diện bản được dùng, không tạo public access tới file gốc.

| Nguồn / SHA-256 | Phần dùng | Ứng dụng cụ thể |
|---|---|---|
| SID-Master-Instruction-V5.md / `ad20e89fb234ed9a0c5a483520d6b7e516f75aba830a275cefa5e66259cacd83` | Mode 4; Mode 5A/5B; phần 3; phần 7 | Sáu phase RTC-COE; mỗi phase một task/input/output/criterion; prototype→review→revision; mini-review sau CE02/CE04 |
| bai-02-prompt-stack-cognitive-interface.md / `1de39293a3f5711d27ca1e68464b3a1ea83432506a3afa9f5621b5e9b2b5b259` | §2.2–3 | Output phase trước làm input phase sau; context và constraints tách riêng |
| bai-04-information-architect-representation.md / `04d1907deff5c4c4dcfda9e267e32b2b9fb620d0010f798bab83232327c34619` | §3–6 | Phân taxonomy/hierarchy/ontology; matrix phase×artifact; chọn representation theo mục tiêu |
| bai-07-validation-epistemic-control.md / `79166d6a1da770090e3b37952cb5247415a6ba6f008f7cd93ecc8026ff034157` | §4–9 | Epistemic labels, self-critique, assumptions/gaps/contradictions và confidence có lý do |
| bai-08-synthesis-frameworking-transfer.md / `cbdafd1a490c6ddb5c8a43cae484fe685a0a4c64bffb7fa4a79a7c4c9bf7ed48` | §6–9 | Biến nội dung thành workflow thực, asset dùng được và phép kiểm transfer |

V5 là nguồn phương pháp thiết kế, không thay controller của Reading Companion. Không nhập rubric chấm project/assignment vào learner assessment. Ngưỡng điểm thiết kế không chứng minh host readiness. Các quyền, mode, Q/support và source rules vẫn thuộc M01–M07, R01–R15, SC00–SC05.

## RTC-COE evaluation rule

Mỗi phase được tự kiểm sáu thành phần: R/T/Context/Constraints/Output/Evaluation. Thang 0–3 của V5 áp dụng cho độ rõ thiết kế prompt, không là xác suất đúng nội dung. Báo điểm phải kèm nhận xét và evidence; tổng điểm không bù hard fail source/state. Self-review cùng tác giả không là kiểm định độc lập.
