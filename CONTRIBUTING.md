# Hướng dẫn đóng góp

Cảm ơn bạn đã quan tâm đến Reading Companion. Thay đổi cần giữ hành vi định tuyến, provenance nguồn, hợp đồng dữ liệu và trạng thái học tập có căn cứ.

## Quy tắc đóng góp

- Gắn nội dung đọc với locator thực tế khi nguồn hỗ trợ locator; nếu nguồn không truy cập được, ghi rõ giới hạn.
- Giữ mode `deep`, `extract`, `combined` và phân biệt mode với style.
- Giữ IDs, source revision, checkpoint, câu hỏi đang chờ và trạng thái hỗ trợ; không suy đoán state chưa lưu.
- Sửa quy tắc tại file canonical sở hữu nó. Các file khác nên tham chiếu, không tạo hợp đồng song song.
- Phân biệt case specification, output đã chạy, grading, review nghĩa và kết quả học. Ghi `NOT_RUN` khi thiếu dữ kiện của lớp đó.

## Quy trình

1. Fork repository và tạo nhánh thay đổi.
2. Sửa file canonical và cập nhật liên kết/tài liệu bị ảnh hưởng.
3. Chạy các kiểm tra repository trong README và workflow GitHub Actions.
4. Với benchmark, lưu nguyên input/output, metadata và hash; ghi trạng thái grading riêng. Không suy ra benchmark đạt từ việc helper hoặc JSON hợp lệ.
5. Trong pull request, nêu vấn đề, file/section đã đổi, checks đã chạy, checks chưa chạy và giới hạn còn lại.

```bash
git clone https://github.com/Nohfinl99/Reading_Companion.git
cd Reading_Companion
python tools/validate_repository.py
```
