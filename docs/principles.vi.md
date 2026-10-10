# Bản đồ nguyên lý và chủ sở hữu

[English version](principles.en.md) · [README](../README.vi.md)

Trang này giải thích các nguyên lý vận hành chính và chỉ đến file sở hữu quy tắc. Nó không tạo contract hoặc taxonomy runtime mới. Nếu có khác biệt, ưu tiên các file canonical trong `skills/sid-reading-companion/references/`.

| Nguyên lý | Cách hiểu trong sản phẩm | Chủ sở hữu chính | Bằng chứng có thể kiểm |
|---|---|---|---|
| Nguồn và phạm vi giới hạn kết luận | Không suy diễn phần chưa truy cập; giữ nguồn, revision, phạm vi, locator và gaps | [M01–M02](../skills/sid-reading-companion/references/master-instruction.md), [KC01](../skills/sid-reading-companion/references/knowledge-compiler.md), [SC00](../skills/sid-reading-companion/references/stack-contracts.md) | SourceManifest, accessed/analyzed/missing ranges, source spans |
| Định tuyến theo mục tiêu | Gọi một hoặc vài stack cần thiết; không ép mọi lượt qua pipeline cố định | [M03–M04](../skills/sid-reading-companion/references/master-instruction.md) | Trigger → primary path → required sections |
| Mode tách khỏi style | `deep`, `extract`, `combined` xác định loại tác vụ; style chỉ điều chỉnh cách trình bày | [M04](../skills/sid-reading-companion/references/master-instruction.md), [R10](../skills/sid-reading-companion/references/reading-protocols.md) | Frame/session mode và style giữ riêng |
| Unit theo phạm vi và nội dung | Không áp số lượng Knowledge Units cố định cho mọi sách hoặc tác vụ | [KC02](../skills/sid-reading-companion/references/knowledge-compiler.md) | Unit boundary, locator, coverage, gộp và phần chưa xử lý |
| Danh sách có provenance | Mỗi subset ghi chủ thể chọn, universe nếu biết, tiêu chí, nguồn và phần loại/chưa xét | [SC01](../skills/sid-reading-companion/references/stack-contracts.md) | SelectionRecord và lời dẫn nhìn thấy được cạnh danh sách |
| Lập luận và ví dụ giữ cầu nối | Ví dụ trỏ unit/argument thực, nêu điều kiện tương ứng và giới hạn kết luận | [SC02–SC03](../skills/sid-reading-companion/references/stack-contracts.md), [R13](../skills/sid-reading-companion/references/reading-protocols.md) | ArgumentRecord, ExampleLink, learner bridge hiển thị |
| Trạng thái học dựa trên sự kiện thật | Câu hỏi chờ, response, support và assessment không được tự tạo hoặc nâng cấp | [SC00/SC04](../skills/sid-reading-companion/references/stack-contracts.md), [R04/R10–R12](../skills/sid-reading-companion/references/reading-protocols.md) | Response thật, support, pending/paused Q, checkpoint revision |
| Gate gắn với bằng chứng | Structural pass không thay semantic review, host test hoặc learner result | [M05/M07](../skills/sid-reading-companion/references/master-instruction.md), [R14](../skills/sid-reading-companion/references/reading-protocols.md), [B01](../skills/sid-reading-companion/references/case-benchmark.md) | GateRecord status và evidence spans theo từng lớp |

## Quy tắc trình bày lựa chọn

Khi AI chọn mục từ một tập lớn hơn, hãy nói rõ mục đích, phạm vi, tiêu chí, chủ thể lựa chọn và phần không được chọn hoặc chưa kiểm. Một con số trong tiêu đề không chứng minh tác giả đã quy định số đó. Giữ số lượng tác giả nêu khi có locator xác nhận; tách riêng số mục được AI trình bày.

Khi tạo ví dụ mới, đặt câu nối ngay cạnh ví dụ: ví dụ minh họa unit nào, nối với bước nào trong mạch lập luận, giữ/thay điều kiện gì và kết luận nào không được chứng minh. Gắn nhãn ví dụ do AI tạo; không gán nguồn tác giả cho scenario giả định.

## Phân biệt nguồn và diễn giải

- `source_explicit`: nội dung được nguồn phát biểu trực tiếp.
- `source_interpretation`: cách đọc có căn cứ, nhưng không phải nguyên văn/nhãn tác giả.
- `pedagogical_proposal`: cách tổ chức, ví dụ hoặc hỗ trợ học do Companion đề xuất.
- `unresolved`: chưa đủ bằng chứng để khẳng định.

Đây là các provenance categories trong contract, không phải taxonomy để chấm năng lực người học. Xem field chính xác và các giá trị hợp lệ trong [SC02–SC03](../skills/sid-reading-companion/references/stack-contracts.md).

## Giới hạn bằng chứng hiện tại

CI trong repository kiểm tra package và helper. Nó không xác nhận mọi diễn giải sách. Bộ benchmark định nghĩa ca và bằng chứng cần thu; chỉ case có input, output và kết quả chấm thực mới có thể được báo đạt. Xem [hướng dẫn chất lượng](quality.vi.md) và [benchmark specification](../skills/sid-reading-companion/references/case-benchmark.md).
