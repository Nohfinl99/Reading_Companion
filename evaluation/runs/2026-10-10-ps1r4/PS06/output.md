learner_view

Điểm em đang học là K01: khi so sánh hai phương án, kết luận chỉ có ý nghĩa nếu chúng được đặt ở cùng mốc thời gian và cùng điều kiện.

Cầu nối trước ví dụ: Ví dụ này dùng để minh họa vì sao “chênh lệch” chỉ đáng tin khi mốc thời gian và điều kiện được giữ nguyên. Em có thể suy từ ví dụ rằng khác biệt theo cùng một tiêu chí là hợp lệ trong phạm vi so sánh đó, nhưng không được suy rằng phương án “tốt hơn” nếu khác biệt đến từ việc đổi mốc hoặc đổi điều kiện.

**Ví dụ mới do AI tạo**

Một nhóm đang chọn giữa hai phương án học tiếng Anh trong tháng 11:

| Phương án | Mốc thời gian | Điều kiện | Tiêu chí chung | Kết quả |
|---|---:|---|---|---:|
| A: học với gia sư | Tháng 11 | 10 giờ học, cùng trình độ đầu vào, cùng bài kiểm tra cuối tháng | Điểm tăng sau 1 tháng | +12 điểm |
| B: học qua app | Tháng 11 | 10 giờ học, cùng trình độ đầu vào, cùng bài kiểm tra cuối tháng | Điểm tăng sau 1 tháng | +7 điểm |

Trong ví dụ này, kết luận “A hiệu quả hơn B theo tiêu chí điểm tăng sau 1 tháng” là hợp lệ trong phạm vi đã nêu, vì hai phương án được so ở cùng mốc thời gian, cùng lượng thời gian học, cùng trình độ đầu vào và cùng bài kiểm tra.

Counterexample: nếu A được đo sau 1 tháng còn B được đo sau 1 tuần, việc A tăng nhiều điểm hơn không chứng minh A tốt hơn B trên cùng tiêu chí. Khác biệt đó có thể đến từ mốc thời gian đo khác nhau, không phải từ bản thân phương án.

Danh sách tôi chọn trong ví dụ này: tôi chọn 1 worked example từ phạm vi K01/A01 để minh họa điều kiện so sánh hợp lệ, theo tiêu chí: ví dụ phải giữ cùng mốc thời gian, cùng điều kiện, dùng một tiêu chí chung, và có một đối chứng sai do đổi mốc thời gian. Đây là ví dụ AI tạo, không phải ví dụ tác giả nêu; phần không chọn là các tình huống đổi điều kiện nguồn lực hoặc cộng giá trị khác đơn vị vì chúng không phải trọng tâm của yêu cầu này.

AUDIT APPENDIX

SC03 ExampleLink applied:
- example_id: EX01
- kind: worked_example
- origin: ai_created
- evidence_status: hypothetical
- target_unit_ids: K01
- argument_ref: A01
- source evidence: CASE CONTEXT “Prior: K01 cùng mốc thời gian và điều kiện; A01 từ K01, khác mốc không chứng minh hơn.”
- scenario: chọn giữa học với gia sư và học qua app trong tháng 11.
- mappings:
  - “Tháng 11” maps to K01 condition “cùng mốc thời gian”.
  - “10 giờ học, cùng trình độ đầu vào, cùng bài kiểm tra” maps to K01 condition “cùng điều kiện”.
  - “Điểm tăng sau 1 tháng” maps to shared comparison criterion.
  - “+12 điểm vs +7 điểm” maps to meaningful difference only within the preserved comparison scope.
  - counterexample “A đo sau 1 tháng, B đo sau 1 tuần” maps to A01: khác mốc không chứng minh phương án hơn.
- preserved_conditions: same time window, same study hours, same initial level, same test, same criterion.
- changed_conditions: none in main worked example; counterexample changes measurement time.
- source_limits: example is hypothetical and does not prove real tutoring or app efficacy.
- learner_bridge visible: yes, immediately before example.

SC01 SelectionRecord applied:
- selection_id: SEL01
- purpose: choose one worked example to illustrate K01/A01.
- scope: CASE CONTEXT prior K01/A01 and requested worked_example.
- basis: ai_selection
- universe_ref: possible examples consistent with K01/A01 in CASE CONTEXT.
- criterion: keep same time, same conditions, one shared criterion, and include counterexample where time changes.
- members count: 1
- count_basis: derived_after_selection
- completeness: partial
- exclusions_or_not_evaluated: resource-condition example and mixed-unit-value example not used because request targets time/condition comparison.

Gate records:
- G-EXAMPLE: PASS
  - evidence: EX01 has target K01, argument A01, visible bridge, mapping, preserved conditions, limits, and hypothetical label.
- G-SELECTION: PASS
  - evidence: learner_view states selection purpose, scope, criterion, origin, count basis, and exclusions.
- G-MEANING: PASS
  - evidence: example preserves the source claim that comparison difference is meaningful only under same time and conditions; counterexample preserves “different time does not prove better.”
- G-Q: NOT_RUN
  - reason: no transfer question or pending answer was generated.

state_delta:
- pending_question: unchanged or none provided.
- learner_response: none generated.
- learning_outcome: none generated.
- new_artifact_refs: EX01, SEL01.