# Prototype, revision and publication review

## Prototype v1 — bản nháp giữ để đối chiếu

```text
Đóng vai reviewer. Đọc claim và nguồn, tìm citation phù hợp,
áp dụng vào Reading Companion rồi kiểm xem kết quả đã tốt chưa.
```

Đây là prototype tác giả viết trong phiên phát triển, không phải prompt được chạy trên host độc lập.

Self-check ban đầu: Role=2, Task=1, Context=1, Constraints=0, Output=1, Evaluation=0; tổng 5/18. Tác vụ trộn, không có source/state contract, không có điều kiện PASS quan sát được. Không dùng điểm này để chấm learner.

## Revision v2 — canonical CE01–CE06

| Lỗi phát hiện ở v1 | Sửa trong v2 | Phép kiểm hồi quy |
|---|---|---|
| “Tốt” không có criterion | CR01–CR06 và SC05 source/output spans | Thiếu evidence bị validator từ chối |
| Citation liên quan bị coi là hỗ trợ | CE04 đối chiếu proposition/conditions | CE-T03, CE-T04 |
| Không chốt access và scope | CE01–CE02 + mini-review 1 | CE-T02 |
| Không giữ mode/Q/support | CE00/CE05/CR05 | CE-T07, CE-T08 |
| Lưu knowledge bị hiểu thành tool/memory mới | Trigger, capability boundary, lớp evidence | CE-T01 và self-review |

V2 được viết và tự rà soát với synthetic fixtures trong [hồ sơ kiểm](../../evaluation/citeguard/README.md). Full prompt chỉ có ở [canonical runtime reference](../../skills/sid-reading-companion/references/citation-evidence.md), không sao chép một bản khác ở docs.

## Source publication gate — PUB-REVIEW

Gate bảo trì dự án sau khi áp dụng CE, tách khỏi learner runtime. Rà đúng diff hiện tại: identity/metadata không mất; runtime routing tới đúng file; knowledge/interpretation/transfer phân biệt; source locator/copyright/privacy; IA/navigation/links; tests và evidence labels; source artifacts không chứa đường dẫn máy/credentials/private course/PDF. Kết quả nằm trong mechanical report và self-review, không tự khai publication hoặc host PASS.

Checklist cuối: source package đầy đủ, JSON/YAML parse, links tồn tại, IDs/edges hợp lệ, outputs có thật, source/output fingerprints khớp, gates thiếu evidence không PASS, helper/state regression đã chạy đúng môi trường. Bất kỳ sửa nào sau report phải chạy lại checks bị ảnh hưởng.

## Remaining validation

- Host activation/retrieval: NOT_RUN trước khi chạy bản mới trên host.
- Independent semantic review: NOT_RUN trong self-review này.
- Baseline/candidate quality and cost comparison: NOT_RUN; chưa có measured gain.
- Learner outcomes/delayed retention: NOT_RUN; không tạo learner response giả.

Đưa source lên nhánh review/draft PR có thể thực hiện sau gate source. Merge và account-plugin release là hành động riêng; tài liệu này không xác nhận hai bước đó.
