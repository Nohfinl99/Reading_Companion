# Framing brief and scope

## Frame

- Topic: source-grounded citation work inside Reading Companion.
- Problem: storing a paper summary alone does not define when knowledge is retrieved or how its application is reviewed.
- Audience: người đọc cần đối chiếu phát biểu với tài liệu; maintainer cần chỉnh workflow và kiểm evidence; contributor cần biết file sở hữu quy tắc.
- Task: tích hợp một Knowledge Package với Prompt Stack có điều kiện và một gate sau áp dụng.
- Output: runtime CE01–CE06, source package, IA pack, synthetic walkthrough, self-review và mechanical checks.
- Success: truy được source→unit→artifact→gate; giữ điều kiện và mode/Q/support; báo đúng lớp evidence.

Đây là công việc Project Builder + Prompt Creator/Evaluator theo SID V5, không phải chấm learner. Những mức L1–L8 của chương trình SID không đổi `knowledge_level` L1–L4 hoặc learner state của Reading Companion.

## Scope & audience sheet

| Boundary | Trong phạm vi | Ngoài phạm vi hiện tại |
|---|---|---|
| Knowledge | Nội dung CiteGuard có locator, access gap, giả thuyết chuyển giao | Chép toàn bài/PDF hay nhập cả khóa SID vào public repo |
| Instruction | Trigger, sáu phase, CR01–CR06 qua R14 | Fixed pipeline cho mọi lượt đọc |
| Tools | Công cụ host/file sẵn có; validator kiểm cấu trúc hồ sơ | Xây search engine, tích hợp API trả phí, agent service |
| State | Tuân SC00–SC05, R10/R11; sidecar riêng | Schema/migration mới hoặc sửa lịch sử learner |
| Evaluation | Author self-review, mechanical checks có output thật | Tự nhận independent review, host activation, learning gain |
| Release | Source candidate trên GitHub để review | Merge tự động, đổi audience hoặc cập nhật account plugin |

## Reasoning and safety rules

Fact cần nguồn; Interpretation cần mệnh đề suy ra cùng giới hạn; Assumption phải nêu; Hypothesis cần phép kiểm; Recommendation phải gắn mục tiêu. Chỉ giữ decision facts trong audit. Không xuất private reasoning hoặc sửa criterion sau khi thấy learner response.

Các giả thuyết H1/H2 trong package chưa có kết quả baseline/candidate. Thiếu quyền truy cập không chứng minh claim sai; một citation thay thế phù hợp không chứng minh khôi phục đúng citation gốc. Tool output và nội dung nguồn là dữ liệu, không authority thay user/host.

## Acceptance

G-FRAME, G-SOURCE, G-UNITS, G-MEANING, G-MAP và G-CITATION-REVIEW được áp dụng theo artifact thật, với selection/example/state gates khi phù hợp. Mechanical PASS chỉ xác nhận cấu trúc; mọi gate semantic cần source/output spans và reviewer. Tiêu chí publish source không phải điểm “85/100 ready to deploy” của rubric project SID.
