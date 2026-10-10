# Stack contracts — draft PS1

## SC00 — Envelope và persistence

Hợp đồng này là dữ liệu trao đổi giữa stack, không một checkpoint schema mới. Mỗi invocation nhận `{frame, source_manifest, prior_artifacts, session_state, task_input}`; chỉ truyền phần cần dùng. Output `{artifact_ref, readiness, gaps, gate_records, next_owner, state_delta}`. Readiness READY/PARTIAL/BLOCKED/PROVISIONAL là trạng thái xử lý artifact, không learner result. pending/paused Q là trạng thái hội thoại riêng do R10/R11 sở hữu; READY không giải phóng điểm chờ.

Frame: goal, task, mode deep/extract/combined hoặc unselected, style, scope, requested_output, success_criteria, decisions_known, decisions_missing. Nếu mode unselected, M02 chờ lựa chọn trước D/K; thao tác đọc nguồn/định khung vẫn được làm.

SourceManifest: source_id, version/edition hoặc unknown, path/access_method, sha256 khi có file, access read/identified/missing, requested_scope, accessed_ranges, analyzed_ranges, missing_ranges, media_gaps. Locator thực có source/version và dòng/chương/page marker; marker không tự là trang in. Readiness không tự nâng access. Gap chỉ rõ claim/target bị ảnh hưởng và phần độc lập còn dùng được.

Các records SelectionRecord/ArgumentRecord/ExampleLink/QuestionContract/GateRecord lưu trong Markdown hoặc JSON sidecar bên cạnh state; không thêm field vào pending_question, unit hoặc reading_session mà helper chưa hỗ trợ. Sidecar header: contract_version PS1, source_id/hash/version, state_revision, unit_revisions, artifact_refs. Trước reuse so hash và revision; stale thì chặn phần phụ thuộc và tái kiểm. Các ID SC00–SC05 là contract IDs; C01–C10 trong B05 vẫn là capability IDs, không cùng namespace.

State cũ thiếu sidecar vẫn đọc được; không suy provenance đã kiểm. Không sidecar thì phát handoff trong chat và ghi chưa lưu. Audit trace là decision facts, không suy luận riêng tư.

Revision state chỉ tăng do navigation/style/pause/resume: đối chiếu source hash, unit revisions, Q ID và lịch sử support trước khi rebind sidecar sang state revision mới; giữ provenance/criterion cũ và log rebind, không đánh stale content chỉ vì cursor đổi. Source/unit/target đổi thật thì tái kiểm phần phụ thuộc. Không rebind để xóa support hoặc claim đã chuẩn bị criterion trước Q.

Tách learner-visible handoff với evaluator sidecar chứa criterion/đáp án. Khi Q còn pending, learner-visible chỉ target/source refs/Q/support/gaps; không in criterion hoặc lời giải cùng bàn giao. Có file thì giữ criterion trong evaluator sidecar riêng và ghi path để agent tiếp theo đọc, không embed vào nội dung học. Không có persistence riêng thì công khai chưa bàn giao criterion; vẫn giữ Q/support, và nếu không khôi phục được criterion gốc ở phiên sau thì unresolved hoặc task mới rõ, không tạo đáp án để hoàn thiện handoff.

## SC01 — SelectionRecord (danh sách được chọn)

Mỗi danh sách chọn lọc/tổng hợp/ưu tiên, kể cả không có số trong tiêu đề, có:

`selection_id; purpose; scope; basis author_explicit/ai_selection/user_selection/mixed; universe_ref hoặc unknown; criterion; members[{ref, origin, source_locators, inclusion_reason}]; exclusions_or_not_evaluated; completeness complete_in_verified_scope/partial/unknown; count; count_basis author_stated/derived_after_selection/user_limit/unknown; author_count_locator hoặc null`.

`count_basis=unknown` chỉ dùng khi mô tả artifact lịch sử thiếu trace; count lúc đó là số mục quan sát được, không chứng minh quá trình chia/chọn đã diễn ra theo thứ tự nào. Ghi criterion/boundary/stopping rationale chưa biết và readiness PARTIAL; không certify lựa chọn lịch sử hoặc gọi derived_after_selection chỉ từ việc thấy một bảng có N hàng. Khi tổ chức lại mới, dùng criterion mới và count_basis mới, tách khỏi record lịch sử.

Count là độ dài members sau chọn. Khi source thực nêu enumeration tương ứng, kiểm đúng loại mục và scope trước khi kết luận số do AI chọn; author-stated count được giữ, cách dịch tên nhóm và thứ tự/format AI thêm vẫn ghi riêng. Khi tác giả quy định số, giữ author_count và phạm vi/locator riêng nếu đang chọn subset; author_count khác selected_count được nêu rõ. Tiêu chí là điều kiện đưa vào/loại ra có thể kiểm, không chỉ “quan trọng”. Universe chưa xác minh thì completeness không complete. AI tự chọn nêu trong lời dẫn/tiêu đề: “Các ý tôi chọn từ phần đã đọc theo …”; user_limit là giới hạn trình bày, không giới hạn kho unit. mixed nêu origin từng mục. Pure navigation inventory lấy từ index đã kiểm, không cần bịa ranking criterion.

Mục AI chọn từ sách vẫn trỏ unit/locator nguồn đã đọc; origin ai_selection là chủ thể chọn, không xóa provenance nội dung. Mục AI đề xuất mới ghi rõ proposed trong inclusion_reason, căn cứ units nếu có và giới hạn nguồn; source_locators trống chỉ khi không claim nội dung sách/nguồn ngoài, không điền locator giả. User_selection giữ lời yêu cầu/ref của user và nguồn nội dung riêng nếu mục có source claim.

Biểu diễn tối thiểu ngay cạnh danh sách cho người đọc: “Tôi chọn [members] từ [scope] để [purpose], theo tiêu chí [điều kiện đưa vào/loại ra]; [origin/count_basis]; [phần không chọn/chưa kiểm]”. Mỗi mục có ref/locator nguồn nội dung; danh sách mixed ghi origin mỗi mục. Budget N do user yêu cầu chỉ giải thích số mục trình bày, chưa giải thích vì sao chọn đúng các mục đó: vẫn nêu criterion chọn thành viên. Có thể dùng một câu dẫn và bảng thay JSON đầy đủ; các field còn lại lưu sidecar/audit khi cần.

## SC02 — ArgumentRecord

`argument_id; target_unit_ids; source_locators; premises[{id, proposition, basis, locator}]; links[{from,to,type,basis,locator}]; conclusion; conditions; exceptions; gaps`.

Basis giữ source_explicit/source_interpretation/pedagogical_proposal/unresolved. Link phải đọc thành mệnh đề được; supports không tự causal. Với văn học, dùng observation → cách đọc → textual evidence/giới hạn thay cơ chế nhân quả. Chuỗi chưa đủ nguồn là gap, không điền cầu nối tưởng tượng.

## SC03 — ExampleLink

`example_id; kind illustration/worked_example/transfer_question; origin author_example/ai_created/user_provided; target_unit_ids; argument_ref; scenario; mappings[{scenario_element,unit_id,argument_element,correspondence}]; changed_conditions; preserved_conditions; assumptions; source_limits; conclusion_or_question; breaks_or_counterexample; learner_bridge{prior_point,target_ids,purpose,permitted_inference,not_established}; evidence_status hypothetical/author_reported/observed_test`.

Mỗi target tồn tại ở revision được ghi. Mapping phải giải thích tương ứng nghĩa, không chỉ gắn ID. Argument element trỏ premise/link/conclusion có thật. learner_bridge phải xuất hiện bằng lời ngắn ngay trước/sau ví dụ, không chỉ trong sidecar. Purpose xác định ví dụ giải thích distinction/mechanism/structure hay đề xuất phép kiểm; hypothetical chỉ minh họa, không chứng minh product efficacy.

`target_unit_ids` chỉ trỏ các unit trong kho đã nhận/tạo; `argument_ref` trỏ ArgumentRecord. Chẳng hạn K01 là unit, A01 là argument thì target_unit_ids=[K01], argument_ref=A01; không đưa A01 vào danh sách unit hoặc dùng tên một flow thay ID unit. Nếu thiếu kho/revision để kiểm, ghi gap, không tự chứng nhận endpoint tồn tại. Với scenario/dữ kiện do AI dựng hoặc fixture giả định, evidence_status=hypothetical; observed_test chỉ khi có hồ sơ thử nghiệm thực của scenario được dẫn, không phải vì vừa kiểm văn bản ví dụ.

Ví dụ gốc giữ locator; AI-created ghi nhãn và không citation như lời tác giả. Nếu source không có lập luận cần thiết, giải nghĩa đơn giản có thể dùng ArgumentRecord tối thiểu (definition → distinction → implication) có căn cứ. Transfer question lưu criterion riêng trước Q, bản learner không lộ conclusion/criterion.

Với transfer_question, learner bridge chỉ nhắc bối cảnh/target/purpose đã học; mappings và permitted_inference có thể chứa lời giải nên giữ trong evaluator sidecar đến sau response/skip. Kiểm bản câu hỏi bằng G-Q trước phát; bridge không được giải task mới thay learner. Hint được yêu cầu thì ghi support tăng theo R04/R10, không gọi cùng task independent.

## SC04 — QuestionContract

`question_id; target_unit_ids/revisions; argument_ref hoặc null; prompt; criterion[{claim,source_locator,critical_condition}]; task recall/transfer/delayed_recall; prepared_before_question; support_context; validity/gaps`.

pending_question vẫn chỉ `{id,prompt}`. Criterion ở sidecar và không in cùng Q. Mất criterion/source thì đánh giá unresolved, không reverse-fit từ đáp án. Response chỉ từ user thật; lưu nguyên văn riêng với event/turn ref khi có. Unknown support giữ unknown ở session; không tự chuyển none. Skip không learner assessment. QuestionContract thiếu trong phiên cũ: chỉ khôi phục criterion gốc từ hồ sơ/nguồn có căn cứ và ghi provenance, không tạo criterion mới rồi khai đã chuẩn bị trước Q; nếu không khôi phục chắc được thì nêu gap và đề xuất task mới, không chấm ngầm theo tiêu chí đổi.

Record criterion cần dữ liệu thực `[{claim,source_locator,critical_condition}]`, không placeholder “held/retained elsewhere”. Khi audit được yêu cầu, xuất record đầy đủ trong evaluator_sidecar riêng khỏi learner_view để caller lưu; ghi chưa persist nếu không có file/tool. Chưa có record/source chuẩn bị thì G-Q chưa PASS, không khai saved hoặc validity verified. Nối Q chưa có response: lời nhắc chỉ target/bối cảnh/Q/support/gap; giải nghĩa lại đúng điều Q đang kiểm là hint, phải có yêu cầu hỗ trợ và ghi support, không gọi đó là lời nhắc trung tính.

## SC05 — GateRecord

`gate_id; artifact_ref/revision; applicable; reason; status PASS/FAIL/PARTIAL/NOT_RUN; source_spans; output_spans; checks; repair_owner; unresolved`.

PASS cần evidence và mọi check áp dụng đạt. Gate runtime R14 khác benchmark run B; output chưa tồn tại là NOT_RUN. Helper structural PASS không đổi semantic gate. Chưa chạy render/host/learner thì lớp tương ứng NOT_RUN. Status READY chỉ khi gate bắt buộc artifact đạt; PARTIAL cho phần độc lập đã kiểm; BLOCKED cho target phụ thuộc lỗi; PROVISIONAL cho outline identified.

GateRecord.status chỉ thuộc PASS/FAIL/PARTIAL/NOT_RUN. BLOCKED/READY/PROVISIONAL là readiness của artifact, không giá trị gate status. Target thiếu source có readiness=BLOCKED và G-MEANING=NOT_RUN khi chưa có nội dung để kiểm; không dùng readiness thay enum status. Delta dự kiến cũng chỉ dùng field/schema R10/R11; pending_question không thêm status/answer/hint, revision nếu phát sinh phải là số dựa trên revision thực, không chuỗi “prior+1”. Không có state/revision đủ thì ghi proposal/gap, không khẳng định đã lưu checkpoint.
