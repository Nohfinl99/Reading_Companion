# Đối chiếu claim với Fixture S

## Kết luận

Fixture S **không hỗ trợ** claim “Method B làm mọi claim đúng sự thật hơn 20%”. Fixture chỉ cho biết B khôi phục 60% tài liệu tham khảo, còn baseline A khôi phục 40%, trên cùng corpus và cùng quy tắc chấm. Phép đo là **khôi phục tài liệu tham khảo**, không phải độ đúng sự thật của từng claim.

Chênh lệch quan sát được là **20 điểm phần trăm** về tỷ lệ khôi phục tham khảo (60% − 40%). Có thể mô tả tỷ lệ khôi phục của B cao hơn A 50% theo mức tương đối (20/40), nhưng không thể đổi phép đo đó thành “20% đúng sự thật hơn”. Cả hai cách diễn đạt chỉ nói về metric khôi phục tham khảo trong setup mô phỏng này.

## Áp dụng vào một artifact đọc ngắn

**Ví dụ minh họa do AI tạo:** Một bản tóm tắt gắn đúng tài liệu tham khảo cho một câu. Điều đó cho thấy sự gắn nguồn đã khớp theo tiêu chí tương ứng; tự nó chưa chứng minh câu đó đúng sự thật. Tương tự, ngay cả khi một phương pháp khôi phục được nhiều tham khảo hơn, metric ấy không xác lập rằng mọi câu có tham khảo đều đúng.

Cầu nối: hãy tách câu hỏi “có khôi phục đúng tham khảo không?” khỏi câu hỏi “tham khảo có hỗ trợ mệnh đề, và mệnh đề có đúng không?”. Fixture S chỉ trả lời câu hỏi đầu ở mức tỷ lệ tổng hợp; nó không cung cấp kiểm tra từng cặp mệnh đề–nguồn.

## Rà soát CE06 (tự rà, không độc lập)

| Check | Kết quả | Căn cứ / giới hạn |
|---|---|---|
| CR01 — Nguồn | PASS | Dùng đúng các dòng 2–5 của Fixture S; phạm vi là setup mô phỏng. |
| CR02 — Mức hỗ trợ | PASS | 60% và 40% là tỷ lệ khôi phục tham khảo; dòng 4 loại trừ phép diễn giải thành độ đúng sự thật của mọi claim. |
| CR03 — Ranh giới nhận thức | PASS | Ví dụ được ghi rõ là minh họa do AI tạo, không phải kết quả thử nghiệm. Không xác minh ngoài fixture. |
| CR04 — Cấu trúc và provenance | PASS | Artifact ngắn, nêu phạm vi, metric và phần chưa được đo; không lập danh sách chọn lọc hay tuyên bố bao phủ nguồn. |
| CR05 — Trạng thái đọc | N/A | Tác vụ extract đơn, không có câu hỏi người học hoặc trạng thái học cần cập nhật. |
| CR06 — Bản cuối | PASS | Đã đối chiếu các con số và giới hạn trong bản cuối với Fixture S; không có sửa đổi sau lượt rà này. |

**Phạm vi rà:** tự rà nội dung artifact với fixture được cung cấp. Đây không phải review độc lập. Kiểm cơ học sidecar có thể chạy riêng; kiểm host và kết quả người học chưa chạy.
