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

## Application notes — SID recommendations

Các ghi chú này hướng dẫn dùng bảy unit, không thêm phát hiện thực nghiệm hoặc thay nghĩa/revision của nghiên cứu đã tóm lược. Ví dụ dưới đây do SID tạo; hiệu quả trên Reading Companion chưa được đo.

| Unit | Điều kiện cần giữ khi dùng | Ví dụ áp dụng / phản ví dụ |
|---|---|---|
| CG-01 | Giữ riêng metric tìm reference và mức hỗ trợ proposition | Đúng reference chưa đủ kết luận mọi claim đúng sự thật. |
| CG-02 | Chỉ tìm trong nguồn/tập tài liệu thực truy cập và index được | Không gọi snippet-search chỉ vì host có tìm web theo title. |
| CG-03 | Iteration bị giới hạn bởi candidates và coverage | Không hứa luôn tìm được citation thay thế sau nhiều lượt. |
| CG-04 | Giữ dataset, thiết lập và metric báo cáo; model trung bình năm run | Không dùng số nghiên cứu như accuracy của Reading Companion. |
| CG-05 | Ablation là so sánh trong setup báo cáo; thay backend/task cần đo lại | Thử baseline/candidate cùng input trước khi kết luận thêm retrieval cải thiện SID. |
| CG-06 | Đánh đổi full context/retrieval phụ thuộc setup và token budget | Không áp một hệ số tiết kiệm token cố định cho mọi sách/host. |
| CG-07 | Giữ access/coverage và portability khác equal performance | Nguồn thiếu làm claim unresolved; không mặc định claim sai. |

Khi cần nội dung sâu hơn, mở đúng source locator và bổ sung definition/evidence/conditions/limitations trong artifact có revision. Không lấy bảng này thay source spans của tài liệu người dùng. Ví dụ ứng dụng thuộc Recommendation/Hypothesis, không phải kết quả học tập đã quan sát.
