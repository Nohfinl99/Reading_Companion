# Hướng dẫn Đóng góp (Contributing Guidelines)

Cảm ơn bạn đã quan tâm đóng góp cho **SID Reading Companion**! Dự án này được thiết kế theo chuẩn mã nguồn mở dành cho Agent Plugins, hướng đến trải nghiệm đọc sâu và hệ thống hóa tri thức chuẩn mực.

---

## 1. Nguyên tắc Cốt lõi (Core Principles)

1. **Source Grounding (Căn cứ nguồn thực tế)**: Không suy đoán, không tạo ảo giác (hallucination). Mọi tri thức trích xuất đều phải neo vào nguồn và số trang/locator cụ thể.
2. **Contract Preservation**: Các module controller (`master-instruction.md`), compiler (`knowledge-compiler.md`) và protocols (`reading-protocols.md`) tuân theo các invariant nghiêm ngặt. Bất kỳ thay đổi nào cũng cần đảm bảo tính tương thích ngược.
3. **Phân tách Rõ ràng**:
   - `skills/sid-reading-companion/references/`: Nơi chứa tài liệu quy tắc và prompt stacks canonical.
   - `skills/sid-reading-companion/scripts/`: Các công cụ Python thuần (pure Python, zero-external-dependency) để validate cấu trúc, graph DAG, và trạng thái checkpoint.

---

## 2. Quy trình Đóng góp (Workflow)

1. **Fork & Clone** kho lưu trữ về máy:
   ```bash
   git clone https://github.com/<your-username>/sid-reading-companion.git
   cd sid-reading-companion
   ```
2. **Tạo nhánh tính năng (Feature Branch)**:
   ```bash
   git checkout -b feature/ten-tinh-nang
   ```
3. **Kiểm tra hợp đồng cục bộ (Local Validation)**:
   Trước khi commit, hãy đảm bảo các script helper chạy bình thường:
   ```bash
   python skills/sid-reading-companion/scripts/ia_map.py --help
   python skills/sid-reading-companion/scripts/knowledge_compiler.py --help
   python skills/sid-reading-companion/scripts/checkpoint.py --help
   ```
4. **Tạo Pull Request**:
   - Điền đầy đủ thông tin vào `PULL_REQUEST_TEMPLATE`.
   - Mô tả rõ ràng lý do thay đổi và bằng chứng kiểm thử.
