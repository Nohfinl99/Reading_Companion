# Ví dụ đầu ra / Illustrative outputs

[Danh mục tiếng Việt](../artifacts.vi.md) · [English catalogue](../artifacts.en.md)

Các ví dụ dưới đây là **synthetic documentation examples do AI soạn**, không phải output được capture từ model run, response của người học hoặc kết quả benchmark. Chúng minh họa từng dạng trình bày độc lập; không tạo một phiên có chín bước hay một tỷ lệ PASS. Không có file checkpoint/criterion nào được khẳng định đã lưu. Nội dung tiếng Việt; English readers can use the linked catalogue for contracts and evidence limits.

Chỉ gửi example phù hợp với yêu cầu hiện tại cho người đọc. Không gửi toàn bộ trang này như learner handoff khi một Q đang chờ; RA-08 là scoring demo độc lập, không tiếp tục hoặc giải Q của RA-07. Extract examples không quiz. JSON/checkpoint/SC records thực phải theo [R09/R11](../../skills/sid-reading-companion/references/reading-protocols.md) và [SC00–SC05](../../skills/sid-reading-companion/references/stack-contracts.md); các khối trình bày ở đây không phải serializer hay valid-state fixture.

## Source

Nguồn chung **S** là [synthetic fixture S đã lưu](../../evaluation/citeguard/sync-0.3.7/fixture.txt), năm dòng sau; `S:2–3` luôn trỏ file đó, không phải một bài nghiên cứu thật:

```text
1 Synthetic fixture S; not a real research result.
2 Method B recovered 60% of references and baseline A recovered 40%.
3 The comparison used the same corpus and scoring rule.
4 This test measured reference recovery, not the truth of every claim.
5 Findings apply only to the simulated setup described above.
```

Các ID K01/K02/A01 dưới đây chỉ dùng trong bộ ví dụ tài liệu này, revision minh họa 1; chúng không tuyên bố đã có trong checkpoint của người dùng. `knowledge level` là loại tác vụ trong ví dụ, không là trình độ người học đã đo.

## RA-01

**Knowledge Map — mode extract.** Mục tiêu: thấy hai phần cần giữ khi đọc kết quả mô phỏng. Source access: đọc trực tiếp năm dòng S được chép ở trên; scope chỉ fixture này.

| Node | Ý nghĩa | Source locator |
|---|---|---|
| K01 rev1 | B=60%, A=40%, cùng corpus/quy tắc chấm | S:2–3 |
| K02 rev1 | Metric là reference recovery; chưa đo độ đúng của mọi claim; chỉ setup mô phỏng | S:4–5 |

Quan hệ đề xuất có căn cứ: **K02 limits K01** — K02 giới hạn việc diễn giải và chuyển giao con số ở K01 (`source_interpretation`, S:2–5). Đây là conceptual relation, không phải prerequisite hay thứ tự mastery. Gap: fixture không cung cấp corpus hoặc chi tiết scoring rule; chưa lập map của nghiên cứu ngoài fixture. Không có quiz.

## RA-02

**Concept Card — K02 rev1.**

> **Reference recovery trong fixture S:** metric báo tỷ lệ tham khảo được khôi phục; fixture không nêu chi tiết quy tắc chấm. Phép so B/A dùng chung corpus và scoring rule. Nó chưa đo độ đúng của mọi claim, và kết quả chỉ thuộc setup mô phỏng. Nguồn: S:2–5. Điều chưa biết: cách lập corpus và chấm từng reference.

Đây là card giải nghĩa có điều kiện, chưa phải một lần kiểm recall. Không gắn citation nghiên cứu thật cho fixture synthetic.

## RA-03

**Argument Map — A01; target K01/K02 rev1.**

| Thành phần | Mệnh đề | Basis / locator |
|---|---|---|
| P1 | B=60%, A=40% về reference recovery trong cùng corpus/scoring | `source_explicit`, S:2–3 |
| P2 | Thử nghiệm không đo độ đúng của mọi claim và chỉ áp dụng trong setup mô phỏng | `source_explicit`, S:4–5 |
| C1 | Chênh lệch recovery là 20 điểm phần trăm trong setup này | `source_interpretation`: phép trừ từ P1, S:2–3 |
| C2 | Con số trên chưa xác lập thay đổi về độ đúng của mọi claim | `source_interpretation` từ P2, S:4–5 |

Links: P1 **supports** C1; P2 **limits** phạm vi diễn giải C1 và **supports** C2. Conditions: cùng corpus/scoring, metric recovery, setup mô phỏng. Exceptions: fixture không nêu thêm; không suy “không có ngoại lệ”. Gaps: chưa có dữ liệu từng claim hoặc điều kiện ngoài mô phỏng. Bản dùng thật cần ArgumentRecord SC02 gắn source/version và artifact refs; bảng này chỉ minh họa cấu trúc.

## RA-04

**Comparison Matrix — mode extract.** Câu hỏi so sánh: hai phương pháp được báo mức recovery nào trong cùng thiết lập?

| Option | Recovery được báo | Compatible context | Locator | Phép đo độ đúng của từng claim |
|---|---|---|---|---|
| Baseline A | 40% | Cùng corpus/scoring của fixture S | S:2–3 | Không được đo, S:4 |
| Method B | 60% | Cùng corpus/scoring của fixture S | S:2–3 | Không được đo, S:4 |

Theo tiêu chí recovery, chênh lệch được báo là 20 điểm phần trăm; chưa có so sánh chi phí, reliability hay corpus khác. Scope S:1–5. Đây không phải ranking tổng quát của hai hệ thống.

## RA-05

**Knowledge Library — mode extract; Markdown illustration.** Kho mẫu giữ hai unit đủ nghĩa trong fixture S; không có learner assessment.

| ID / revision | Content | Conditions | Knowledge level của task | Citation |
|---|---|---|---|---|
| K01 / 1 | B khôi phục 60% tham khảo, baseline A 40% | Cùng corpus/scoring; chỉ setup mô phỏng | L1: nhận diện kết quả được báo | S:2–3; phạm vi S:5 |
| K02 / 1 | Kết quả đo reference recovery, chưa đo độ đúng của mọi claim | Chưa chuyển sang factual truth hoặc bối cảnh khác | L2: phân tích giới hạn cách diễn giải | S:4–5 |

Relations: `K02 limits K01`, basis `source_interpretation`, proposition và locator như RA-01. Prerequisites: chưa có quan hệ tiên quyết được xác lập; không đổi relation này thành prerequisite. Metadata thiếu: corpus/scoring chi tiết. Khi lưu JSON thật, dùng R11 và excerpt có thật từ file UTF-8; bảng này chưa phải checkpoint JSON. Extract giữ nguyên không quiz.

## RA-06

**Recall Card — checked-unit reference K01 rev1 trong bộ ví dụ; mode extract.** “Checked” ở đây chỉ nói phép đối chiếu với fixture khi soạn tài liệu, không phải học viên đã nhớ hoặc gate đã được capture.

> **K01 — Kết quả có điều kiện:** B=60%, A=40% reference recovery, cùng corpus và scoring trong mô phỏng S. Chênh lệch 20 điểm phần trăm. Chưa đo factual truth hoặc điều kiện ngoài setup này. [S:2–5]

Thẻ bổ sung không thay K01/K02 đầy đủ và không tự sinh câu hỏi.

## RA-07

**Transfer Exercise — learner-view template; chỉ dùng khi user yêu cầu transfer trong deep/combined.** Đây chưa là Q đã phát; bản dùng thật cần ExampleLink SC03 và criterion SC04 được chuẩn bị trước, giữ ở evaluator sidecar. Không có criterion/đáp án của câu hỏi này trong template; chưa có G-Q capture hoặc saved pending state.

Target: vận dụng phân biệt metric/phạm vi từ K01/K02 vào tình huống mới. Outcome mong muốn của task: nêu được kết luận được dữ kiện hỗ trợ và giới hạn của nó. Source limits: S:2–5 chỉ mô tả một setup recovery, không kiểm factual truth hay tình huống mới bên dưới.

> **Tình huống mới do AI tạo:** Một công cụ C tìm lại được 90/100 reference trong một bộ đề mới. Mỗi reference được tìm đúng theo danh sách gốc; nội dung các claim chưa được đối chiếu với tài liệu. Nhóm viết báo cáo dự định kết luận “90% claim của chúng tôi đúng sự thật”.
>
> Từ dữ kiện này, em sẽ chấp nhận kết luận nào và yêu cầu thêm bằng chứng gì trước khi dùng kết luận của nhóm?

Một câu hỏi độc lập; chờ response khi phát thật, không gắn lời giải/criterion bên dưới. Tình huống là hypothetical, chưa phải observed test.

## RA-08

**Learning Checkpoint — demo chấm synthetic độc lập, không phải response người học.** Không tiếp nối RA-07 và không ghi vào state/history thật.

- Question demo Q-DEMO-08: “Trong fixture S, recovery của B cao hơn A bao nhiêu điểm phần trăm?”
- Raw synthetic response: “Cao hơn 20 điểm phần trăm trong cùng corpus và quy tắc chấm.”
- Synthetic support: `hint` — giả định demo đã nhắc cách tính chênh lệch.
- Feedback demo: “Câu trả lời giữ đúng chênh lệch 60−40=20 điểm phần trăm và điều kiện S:2–3. Vì demo có hint, kết quả minh họa là `assisted`; nó không đo recall độc lập hoặc hiểu toàn chương.”
- Observed result: **không có learner observation**. `assisted` ở trên là giá trị của scoring demo, không phải record đã lưu hoặc kết quả người thật.

R04 thực chỉ chấm sau raw response thật và criterion chuẩn bị trước Q; thiếu response giữ unassessed. Skip không bị biến thành response đúng/sai.

## RA-09

**Session Handoff — layout template, chưa phải bundle hợp lệ hoặc file đã lưu.** Dùng [bundle spec](../../specs/handoff-bundle-v1.md) và [synthetic helper roundtrip tests](../../tests/test_handoff_bundle.py) để xem hợp đồng và phép kiểm thực ở lớp helper.

```text
reading-handoff/                    # cây đề xuất, chưa được tạo bởi ví dụ
  manifest.json                     # identity/hash/revision thực sau khi tạo
  state.json                        # R11; tạo/kiểm từ nguồn tại vị trí thật
  sources/fixture.txt               # copy nguồn được phép, hash byte thật
  learner/handoff.md                # goal/mode/scope/access/IDs/Q/support/gaps
  evaluator/question-contract.json  # chỉ nếu criterion gốc thực có
  evaluator/gates.json              # chỉ records thực có, audience=evaluator
```

Bản learner-view template:

> Goal: tiếp tục đọc đúng phạm vi đã có nguồn. Scope minh họa: S:1–5; source phải được gửi kèm hoặc nêu access gap. Processed IDs/cursor/mode/pending Q/support: lấy nguyên từ snapshot thật; ví dụ này chưa có snapshot nên các giá trị hiện chưa biết. Limitations: chưa lưu state hoặc sidecars, chưa kiểm bundle/restore/host. Next: nhận nguồn và snapshot thật, kiểm identity/revision, sau đó nối phiên theo Q/support đã có.

Không đặt đường dẫn tuyệt đối giả trong checkpoint. Sau khi copy nguồn, tạo/import có review tại đường dẫn thật và tính hash theo spec; bundle checker không tự relocate hoặc khôi phục session. Criterion/answer không nằm trong learner view khi Q pending. Plugin release ZIP không thay bundle này và không đồng bộ tài khoản học.

## Selection

Minh họa lời dẫn SC01 cho RA-01/RA-05: “Tôi chọn K01/K02 từ năm dòng fixture S để giữ kết quả được báo và giới hạn cách đọc, theo tiêu chí mệnh đề trực tiếp trả lời phép so recovery hoặc phạm vi áp dụng. Chủ thể chọn: AI khi soạn ví dụ; count=2 là số unit sau phân ranh giới. Corpus/scoring chi tiết chưa được nguồn cung cấp. Đây không phải enumeration của nghiên cứu thật.”

Lời dẫn có thể hiện cho người đọc; full SelectionRecord dùng SC01 khi cần audit/persistence. Nó không chứng minh vì sao một output lịch sử khác đã chọn đúng những mục đó.

## Actual captured example

Để xem output model thực đã giữ raw và review riêng, mở [artifact CE của Luna](../../evaluation/citeguard/sync-0.3.7/artifact.md), [SC05 sidecar](../../evaluation/citeguard/sync-0.3.7/sidecar.json), [run manifest](../../evaluation/citeguard/sync-0.3.7/run-manifest.json) và [primary review](../../evaluation/citeguard/sync-0.3.7/review.json). Đây là một case khác, chỉ ba frozen criteria, có một scope repair được giữ. Không đổi nhãn các ví dụ tài liệu phía trên thành kết quả của lượt chạy đó.
