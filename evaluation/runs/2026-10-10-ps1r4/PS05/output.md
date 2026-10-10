learner_view

Cầu nối: Mình kiểm ví dụ này theo K01/A01: chỉ được kết luận “B hơn A theo cùng một tiêu chí” khi hai phương án được so ở cùng mốc thời gian và cùng điều kiện. Ví dụ này dùng để thấy ranh giới của phép so sánh, không chứng minh phương án nào thật sự tốt hơn.

**Kết luận kiểm ví dụ**

Ví dụ hiện tại **chưa hợp lệ** theo K01/A01.

- A: doanh thu 100 ở tháng 1
- B: doanh thu 120 ở tháng 2
- Kết luận đang nêu: “B tốt hơn 20% vì K01”

Điểm gãy nằm ở **mốc thời gian khác nhau**. Theo nguồn, “một khác biệt do đổi mốc thời gian không chứng minh phương án tốt hơn trên cùng tiêu chí”. Vì vậy, chênh lệch 120 so với 100 có thể là do tháng khác, điều kiện khác, mùa vụ khác, hoặc dữ kiện chưa biết; chưa thể gọi là B tốt hơn 20% theo K01.

**Sửa có điều kiện**

Nếu muốn kết luận “B tốt hơn 20%”, ví dụ cần đổi thành một trong các bản sau:

1. **Cùng mốc thời gian**
   - A doanh thu 100 trong tháng 1
   - B doanh thu 120 trong tháng 1
   - Các điều kiện so sánh khác giữ như nhau
   - Khi đó có thể nói: trong phạm vi dữ kiện đã cho, B cao hơn A 20% theo tiêu chí doanh thu.

2. **Giữ dữ kiện tháng 1/tháng 2 nhưng sửa kết luận**
   - A doanh thu 100 tháng 1
   - B doanh thu 120 tháng 2
   - Kết luận đúng hơn là: B có doanh thu cao hơn A trên hai mốc thời gian khác nhau, nhưng chưa đủ căn cứ để nói B tốt hơn 20% theo K01.

Các điểm mình chọn kiểm ở đây là những điểm trực tiếp quyết định tính hợp lệ của ví dụ theo unit trước: mốc thời gian, điều kiện so sánh, tiêu chí chung, và giới hạn kết luận. Đây là danh sách mình chọn từ case context theo tiêu chí “điểm nào làm kết luận ví dụ đúng hoặc sai”; không phải danh sách đầy đủ mọi điều có thể bàn về doanh thu.

AUDIT APPENDIX

**Applied Records**

SC03 ExampleLink

```json
{
  "example_id": "EX01",
  "kind": "worked_example",
  "origin": "user_provided",
  "target_unit_ids": ["K01"],
  "argument_ref": "A01",
  "scenario": "A doanh thu 100 tháng 1; B doanh thu 120 tháng 2; kết luận B tốt hơn 20% vì K01.",
  "mappings": [
    {
      "scenario_element": "A doanh thu 100 tháng 1",
      "unit_id": "K01",
      "argument_element": "premise: phương án cần được so ở cùng mốc thời gian và điều kiện",
      "correspondence": "A có mốc thời gian tháng 1"
    },
    {
      "scenario_element": "B doanh thu 120 tháng 2",
      "unit_id": "K01",
      "argument_element": "premise: phương án cần được so ở cùng mốc thời gian và điều kiện",
      "correspondence": "B có mốc thời gian tháng 2, khác mốc với A"
    },
    {
      "scenario_element": "kết luận B tốt hơn 20%",
      "unit_id": "K01",
      "argument_element": "conclusion: chênh lệch chỉ có ý nghĩa khi cùng mốc thời gian và điều kiện",
      "correspondence": "Kết luận vượt quá điều kiện cho phép vì mốc thời gian khác nhau"
    }
  ],
  "changed_conditions": ["Mốc thời gian giữa A và B khác nhau"],
  "preserved_conditions": ["Cùng tiêu chí doanh thu được nêu"],
  "assumptions": ["Không có dữ kiện bổ sung về điều kiện nguồn lực, mùa vụ, hay bối cảnh tháng 1/tháng 2"],
  "source_limits": "Nguồn chỉ cho phép kết luận về chênh lệch có ý nghĩa khi cùng mốc thời gian và điều kiện.",
  "conclusion_or_question": "Ví dụ hiện tại không hợp lệ theo K01/A01; có thể sửa bằng cách đưa A và B về cùng mốc thời gian hoặc hạ kết luận xuống mức mô tả dữ kiện.",
  "breaks_or_counterexample": "Khác biệt do đổi mốc thời gian không chứng minh phương án tốt hơn trên cùng tiêu chí.",
  "learner_bridge": {
    "prior_point": "K01: cùng mốc thời gian và điều kiện; A01: khác mốc không chứng minh hơn",
    "target_ids": ["K01"],
    "purpose": "Kiểm ranh giới áp dụng của phép so sánh",
    "permitted_inference": "Có thể nói B có số doanh thu lớn hơn trong dữ kiện nêu; không thể nói B tốt hơn 20% theo K01 khi khác mốc thời gian.",
    "not_established": "Không chứng minh B thật sự tốt hơn A hoặc phù hợp hơn A."
  },
  "evidence_status": "hypothetical"
}
```

SC01 SelectionRecord

```json
{
  "selection_id": "SEL01",
  "purpose": "Chọn các điểm quyết định tính hợp lệ của ví dụ áp dụng",
  "scope": "CASE CONTEXT: Prior K01/A01 và ví dụ đang kiểm",
  "basis": "ai_selection",
  "universe_ref": "Các điều kiện và giới hạn so sánh được nêu trong case context",
  "criterion": "Điểm nào quyết định kết luận 'B tốt hơn 20%' có theo được từ K01/A01 hay không",
  "members": [
    {
      "ref": "mốc thời gian",
      "origin": "ai_selection",
      "source_locators": ["CASE CONTEXT: Lập luận và giới hạn cho ví dụ", "CASE CONTEXT: Prior"],
      "inclusion_reason": "Nguồn nêu khác mốc thời gian không chứng minh phương án tốt hơn"
    },
    {
      "ref": "điều kiện so sánh",
      "origin": "ai_selection",
      "source_locators": ["CASE CONTEXT: Lập luận và giới hạn cho ví dụ"],
      "inclusion_reason": "K01 yêu cầu cùng điều kiện để chênh lệch có ý nghĩa"
    },
    {
      "ref": "tiêu chí chung",
      "origin": "ai_selection",
      "source_locators": ["CASE CONTEXT: Lập luận và giới hạn cho ví dụ"],
      "inclusion_reason": "Chênh lệch chỉ có nghĩa theo một tiêu chí chung"
    },
    {
      "ref": "giới hạn kết luận",
      "origin": "ai_selection",
      "source_locators": ["CASE CONTEXT: Lập luận và giới hạn cho ví dụ"],
      "inclusion_reason": "Kết luận phải giới hạn theo phạm vi so sánh"
    }
  ],
  "exclusions_or_not_evaluated": "Không đánh giá hiệu quả kinh doanh thực tế, mùa vụ, nguồn lực, hay dữ kiện ngoài case context",
  "completeness": "complete_in_verified_scope",
  "count": 4,
  "count_basis": "derived_after_selection",
  "author_count_locator": null
}
```

SC05 GateRecords

```json
[
  {
    "gate_id": "G-EXAMPLE",
    "artifact_ref": "EX01",
    "applicable": true,
    "reason": "User yêu cầu kiểm ví dụ áp dụng theo unit trước",
    "status": "PASS",
    "source_spans": [
      "Prior: K01 cùng mốc thời gian và điều kiện; A01 từ K01, khác mốc không chứng minh hơn",
      "Nếu hai phương án được đánh giá ở cùng mốc thời gian và điều kiện...",
      "Một khác biệt do đổi mốc thời gian không chứng minh phương án tốt hơn..."
    ],
    "output_spans": [
      "Ví dụ hiện tại chưa hợp lệ theo K01/A01",
      "Sửa có điều kiện"
    ],
    "checks": [
      "target K01 exists in prior",
      "argument A01 exists in prior",
      "mapping identifies month mismatch",
      "conclusion limited to available evidence",
      "AI did not add missing business data"
    ],
    "repair_owner": "R13",
    "unresolved": []
  },
  {
    "gate_id": "G-MEANING",
    "artifact_ref": "learner_view",
    "applicable": true,
    "reason": "Output interprets source conditions and conclusion",
    "status": "PASS",
    "source_spans": [
      "cùng mốc thời gian và điều kiện",
      "khác mốc không chứng minh hơn"
    ],
    "output_spans": [
      "Điểm gãy nằm ở mốc thời gian khác nhau",
      "chưa thể gọi là B tốt hơn 20% theo K01"
    ],
    "checks": [
      "No reversal of condition",
      "No unsupported conclusion that B is better",
      "Conditional fix preserves source constraint"
    ],
    "repair_owner": null,
    "unresolved": []
  },
  {
    "gate_id": "G-SELECTION",
    "artifact_ref": "SEL01",
    "applicable": true,
    "reason": "Learner view includes selected list of checked points",
    "status": "PASS",
    "source_spans": ["CASE CONTEXT"],
    "output_spans": ["Các điểm mình chọn kiểm ở đây..."],
    "checks": [
      "criterion stated",
      "origin stated",
      "scope stated",
      "count basis recorded in audit"
    ],
    "repair_owner": null,
    "unresolved": []
  },
  {
    "gate_id": "G-Q",
    "artifact_ref": "pending_question",
    "applicable": false,
    "reason": "No new learner question emitted and no learner response assessed",
    "status": "NOT_RUN",
    "source_spans": [],
    "output_spans": [],
    "checks": [],
    "repair_owner": null,
    "unresolved": []
  }
]
```

**State Delta / Transition**

```json
{
  "state_delta": {
    "pending_question": "unchanged_or_none",
    "new_artifact_refs": ["EX01", "SEL01"],
    "learner_assessment": "not_created",
    "mastery_or_learning_outcome": "not_created"
  },
  "transition": "READY",
  "next_owner": "R13/R14"
}
```