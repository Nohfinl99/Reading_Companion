# Dùng Reading Companion

Gửi file nguồn hoặc dán một đoạn trích, rồi nói rõ **mục tiêu, phạm vi và mode**. Ví dụ: muốn hiểu lập luận ở mục 2.1, chỉ đọc mục đó, dùng `combined`. Nếu nguồn chưa truy cập được, em cần phần nguồn tương ứng trước khi giải thích hoặc kiểm claim.

| Mode | Anh sẽ nhận được |
|---|---|
| `deep` | Giải thích nghĩa, nền cần thiết và mạch lập luận; ở style standard, kết thúc bằng một câu hỏi rồi chờ anh trả lời. |
| `extract` | Các đơn vị tri thức đủ nghĩa, nguồn/vị trí và điều kiện áp dụng; không quiz, không chấm mức hiểu. |
| `combined` | Đọc sâu cùng phần trích xuất bổ sung, dùng chung ID và tránh lặp; ở style standard, giữ nhịp một câu hỏi rồi chờ. |

## Prompt bắt đầu nên dùng

Đính kèm nguồn rồi gửi:

> Em dùng Reading Companion đọc tài liệu anh gửi ở mode **combined**, style **standard**. Mục tiêu: hiểu vì sao tác giả kết luận [X] và lưu lại kiến thức để dùng cho [việc Y]. Phạm vi: [chương/mục/trang hoặc đoạn đã dán]. Bắt đầu từ một cụm đủ nghĩa: giải thích nền cần thiết, nối tiền đề → kết luận, giữ điều kiện và ngoại lệ; bổ sung các unit có nguồn/vị trí mà không chép lại lời giải thích. Phân biệt lời tác giả, diễn giải và ví dụ mới do AI tạo. Cuối cụm hỏi một câu, chưa đưa đáp án, rồi chờ anh.

Nếu chỉ cần kho kiến thức:

> Em trích xuất đoạn/file này ở mode **extract** để anh dùng cho [mục tiêu], trong phạm vi [X]. Giữ nguồn/vị trí, điều kiện, ngoại lệ và phần chưa rõ; không quiz. Chia unit theo nội dung đủ nghĩa, không ép số lượng. Nêu phần đã xử lý và phần còn thiếu nguồn.

Anh có thể đổi style bằng “đọc nhanh”, “đọc nhẹ” hoặc “đọc phản biện”. Style không tự đổi mode; `extract` luôn không quiz. Với claim nhạy theo thời gian đang được giải thích hoặc áp dụng, em đối chiếu hiện tại khi có công cụ và nguồn phù hợp, giữ riêng lời sách cùng ngày/phạm vi kiểm; chưa kiểm được thì nói rõ.

## Kiểm claim với nguồn theo CiteGuard

Không cần nhớ các mã CE. Cung cấp claim và tài liệu thực cần kiểm:

> Em dùng cách đối chiếu CiteGuard để kiểm các claim sau với **tài liệu anh vừa gửi**, chỉ trong [phạm vi]. Claim: [C1…]. Đọc đúng đoạn nguồn và ngữ cảnh; trả bảng gồm claim, nguồn/vị trí, đoạn bằng chứng ngắn, mức hỗ trợ, điều kiện quyết định, phần diễn giải/giả định và điều chưa biết. Phân biệt được hỗ trợ đầy đủ, một phần, không được hỗ trợ và chưa kết luận được; thiếu truy cập không đồng nghĩa claim sai. Không tìm ngoài tài liệu ở lượt này. Sau khi áp dụng kết quả vào [bản giải thích/bảng unit], rà lại bản cuối với nguồn, giữ mode, câu hỏi đang chờ và mức hỗ trợ học tập của phiên. Nêu phần dùng được và khoảng trống còn lại.

Kiểm này trả lời “nguồn có hỗ trợ claim không”; xác minh sự thật ngoài tài liệu là yêu cầu riêng. “Mức hỗ trợ claim” cũng khác mức gợi ý anh đã nhận khi trả lời câu hỏi học tập. Nếu cần hồ sơ rà soát kỹ thuật, thêm: “Xuất record **G-CITATION-REVIEW** với evidence cho CR01–CR06 và các điểm chưa kiểm; phân biệt tự rà của AI với kiểm độc lập.”

## Audit bằng chứng cho một dự án

Đây là route riêng khi anh yêu cầu tra cứu/chọn/đối chiếu/bàn giao evidence dự án; không tự bật trong một lượt đọc sách. Khi dùng, helper 0.3.8 sẽ render block bắt buộc từ audit record; reviewer vẫn phải đánh giá ý nghĩa và căn cứ của stop reason. Xem [hướng dẫn đầy đủ](project-evidence.vi.md).

## Điều khiển phiên

| Anh nói | Cách xử lý |
|---|---|
| “Chương tiếp” / `Next` | Chuyển theo mục lục đã xác minh; giữ câu hỏi chưa trả lời ở trạng thái tạm gác. |
| “Quay lại” / `Back` | Quay vị trí trước theo lịch sử có thật. |
| “Tạm dừng, giữ câu hỏi này” / `Pause` | Giữ câu hỏi, vị trí, ghi chú nối lại và mức hỗ trợ đã nhận. |
| “Tiếp câu hỏi đã tạm gác” | Nhắc lại ngữ cảnh và tiếp câu hỏi đó; không tự chấm hoặc giảm mức hỗ trợ. |
| “Tiến độ” / `Progress` | Đọc state/snapshot thật: vị trí, phần đã xử lý, câu hỏi đang chờ/tạm gác, khoảng trống và bước tiếp. |

Mở một chương chưa có nghĩa đã đọc xong; tạo thẻ chưa có nghĩa đã hiểu. Thiếu mục lục/lịch sử thì em không đoán chương kế. Thiếu state hoặc handoff thật thì chưa thể xác định tiến độ hay câu hỏi đang chờ.

## Mang phiên sang chat khác

Trước khi rời phiên, yêu cầu:

> Em tạo handoff có thể gửi sang chat mới: giữ mục tiêu, mode/style/phạm vi, nguồn và phiên bản/hash nếu có, ID/revision của unit, vị trí, coverage, đánh giá từ câu trả lời thật, câu hỏi đang chờ/tạm gác và mức hỗ trợ đã nhận, khoảng trống và bước tiếp. Liệt kê các file thực đã lưu. Gửi kèm các sidecar đã phát sinh (bằng chứng, lập luận, ví dụ, tiêu chí câu hỏi, đối chiếu thời sự); giữ đáp án/tiêu chí chấm ngoài bản handoff người học nhìn thấy khi câu hỏi còn chờ. Nếu chưa lưu file, đưa bản bàn giao trong chat và nói rõ.

Ở chat mới, gửi lại nguồn, handoff và sidecar, rồi nói:

> Em nối phiên từ gói anh gửi. Kiểm nguồn và revision trước; giữ mode, câu hỏi đang chờ/tạm gác và support, không dựng thêm tiến độ. Chỉ ra phần thiếu rồi tiếp [vị trí/câu hỏi cụ thể].

Plugin không có memory tài khoản ngầm. Handoff tóm tắt không thay nguồn cho nội dung mới; checkpoint không tự xuất mọi sidecar. Nguồn đổi thì cần đối chiếu/reimport trước khi cập nhật state liên quan. Tên action `search_text_snippet` trong nghiên cứu không tự cài công cụ tìm kiếm lên host; chỉ dùng công cụ thực có hoặc tìm trong file được cấp. Lưu source hoặc release cập nhật chưa chứng minh host đã nạp bản mới.

Hợp đồng chi tiết: [controller](../skills/sid-reading-companion/references/master-instruction.md), [mode, phiên và handoff](../skills/sid-reading-companion/references/reading-protocols.md), [citation/evidence](../skills/sid-reading-companion/references/citation-evidence.md), [sidecar](../skills/sid-reading-companion/references/stack-contracts.md).

## Kiểm kỹ thuật khi có repository

Record mới dùng JSON sidecar đầy đủ SC05, gắn artifact/hash/revision; validator cấu trúc không kiểm nghĩa. Công cụ development không tự có trên host. [Hồ sơ đồng bộ 0.3.7](citeguard/correction-plan.md).
