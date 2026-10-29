# CE-T01 — assistant-authored application, self-review only

Transfer mapping: CG-01 giúp giữ đúng metric; CG-02 định hướng đọc thêm điều kiện; CG-07 nhắc giới hạn nguồn. Con số trong ví dụ vẫn thuộc fixture synthetic, không phải kết quả bài CiteGuard hoặc SID.

CE01 Frame: extract; giải thích kết quả trong simulation S; không đánh giá learner.
CE02 Source: fixture.txt dòng 2–5 đã đọc; chỉ corpus và scoring cố định; mini-review 1 giữ scope này.
CE03 Unit SYN-01 revision 1: kết quả reference recovery có điều kiện simulation; chọn unit vì trả trực tiếp câu hỏi; chưa chọn các dòng khác. Count=1 sau phân ranh giới, không phải enumeration tác giả.
CE04 Fact trong fixture: B=60%, baseline=40%; Interpretation: chênh lệch 20 điểm phần trăm trong cùng thiết lập. Không có phép đo factuality; mini-review 2 không thay metric.
CE05 Reading artifact: “Trong simulation S với corpus và scoring cố định, B khôi phục reference đạt 60%, baseline đạt 40%. Chênh lệch là 20 điểm phần trăm. Kết quả này chưa đo độ đúng sự thật của mọi claim.” [fixture.txt, dòng 2–5]
Bridge: điều kiện ở CE03 giới hạn cách đọc con số CE04; ví dụ synthetic này minh họa kiểm metric/conditions, không chứng minh SID tốt hơn. Không tạo quiz ở extract.
CE06 Final delta: giữ source, scope và metric từ CE04; GateRecord nằm trong self-review.json. Source spans và output spans cùng được giữ.
