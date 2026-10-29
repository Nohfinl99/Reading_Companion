# Helper compatibility — 0.3.7

GitHub source và package dùng chung implementation helper. Bản này hợp nhất các guard continuity từng chỉ có trên plugin tài khoản: giữ lịch sử assessment, không xóa Q chưa được resolve bằng response đã chấm, và không biến support legacy unknown thành none.

Giữ nguyên checkpoint schema/version, CLI và bốn helper. Kiểm cấu trúc không thay kiểm nghĩa. Development utilities kiểm SC05 và bundle nằm trong repository; không mặc định có trên host và không tự chạy khi chỉ gọi skill.

Lưu state, nguồn/hash và sidecar trước khi nối phiên. Checkpoint export không tự gom mọi sidecar. Gate mới phải ràng buộc artifact/revision và evidence; historical review không tự thành evidence cho candidate mới. Xem [hướng dẫn](../../../docs/usage.vi.md) và [phương án sửa](../../../docs/citeguard/correction-plan.md).
