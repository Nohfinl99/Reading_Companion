# CiteGuard knowledge package 0.1

Nguồn nghiên cứu: Choi, Guo, Fung & Wang (ACL 2026), [Faithful Citation Attribution for LLMs via Retrieval-Augmented Validation](https://aclanthology.org/2026.acl-long.282/), DOI `10.18653/v1/2026.acl-long.282`. [Manifest](citeguard-source.json) ghi mức truy cập thật. Các unit revision 1 dưới đây do SID phân ranh giới trong phạm vi đã đọc; không phải enumeration của tác giả. Phần kiến thức ngắn dùng tiếng Anh để giữ thuật ngữ gốc; lời áp dụng tiếng Việt thuộc CE.

## Units

| ID | Nội dung nguồn được tóm lược | Locator trang in / PDF 1-based |
|---|---|---|
| CG-01 | Attribution matches references. Exact accuracy and agreement with annotated alternatives are distinct metrics. | §2.1, 6243 / 3; Table 5, 6247 / 7 |
| CG-02 | Retrieve source context; distinguish within-paper search from corpus snippet search. Accessible indexed content is required. | §2.2, 6243 / 3 |
| CG-03 | Iterative retrieval excludes previously selected papers; further suitable references may be unavailable. | §2.3, 6243 / 3 |
| CG-04 | CiteME accuracy: GPT-4o 45.1%, DeepSeek-R1 68.1%, human 69.2%. Model results average five runs. | Table 2, 6245 / 5 |
| CG-05 | Action ablation supports context and snippet retrieval contributions within the reported setup. | §5.2; Table 7, 6247 / 7 |
| CG-06 | Full-paper reading can improve accuracy while consuming more tokens; retrieval and long context trade off. | §5.3; Table 8, 6247 / 7 |
| CG-07 | Retrieval coverage constrains results; backend portability does not imply equal performance. | §5.8, 6248 / 8; Limitations, 6249 / 9 |

## Transfer proposal — chưa đo hiệu quả trên SID

H1: truy vết claim tới đoạn nguồn và giữ ngữ cảnh có thể giảm lỗi gán nguồn trong tác vụ đọc. H2: gọi package theo nhu cầu có thể tiết kiệm chi phí so với nạp mọi tài liệu mỗi lượt. Đây là giả thuyết thiết kế của SID; dùng baseline/candidate cùng đầu vào, nguồn, model/tools và tiêu chí để đo trước khi kết luận.

Selection: chọn các unit phục vụ quyết định tích hợp retrieval, citation và đánh giá; không tuyên bố bao phủ toàn bài. Chưa trích related work, mọi ví dụ và appendices. Kiến thức nghiên cứu được xử lý như historical/source-reported; giá/API/model ranking hiện tại phải kiểm riêng qua R07. [Relations](citeguard-relations.json) là diễn giải có nhãn của SID; không tự chuyển thành learning prerequisites.

Hướng dẫn áp dụng và gate nằm ở [CE01–CE06](../citation-evidence.md). Không có search engine hoặc citation validator được cài bởi file này.
