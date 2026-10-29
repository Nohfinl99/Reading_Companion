# Evaluation evidence — CiteGuard source candidate

Ngày 2026-10-29, Asia/Bangkok. Những output trong thư mục này được tác giả AI viết và tự đối chiếu trong phiên phát triển. Không có lời đáp learner thật, independent reviewer hay captured installed-host run. Model identity không được suy đoán từ tên ứng dụng; host/config ngoài thông tin phiên là unknown.

## Latest source-snapshot evidence / Bằng chứng mới

Source candidate 0.3.7 có [capture và primary review riêng](sync-0.3.7/README.md): [artifact model sinh](sync-0.3.7/artifact.md), [strict SC05 sidecar](sync-0.3.7/sidecar.json), [manifest](sync-0.3.7/run-manifest.json), [review](sync-0.3.7/review.json) và [release checks](sync-0.3.7/release-checks.json). Một case và một scope repair không là độ chính xác tổng quát. [Artifact catalogue](../../docs/artifacts.vi.md) tách ví dụ tài liệu, model output, helper và host evidence.

## Inputs, outputs, review — authored walkthrough lịch sử

- [Synthetic source](fixture.txt): tài liệu minh họa tự viết, không trích sách riêng.
- [Case specifications](cases.json): input và expected behavior được giữ riêng với outputs.
- [CE-T01: áp dụng đủ sáu phase](outputs/CE-T01.md): source→unit→support→reading→review.
- [CE-T02](outputs/CE-T02.md), [CE-T03](outputs/CE-T03.md), [CE-T04](outputs/CE-T04.md): thiếu nguồn, relevance/support và citation thay thế.
- [CE-T05](outputs/CE-T05.md), [CE-T06](outputs/CE-T06.md): số liệu và dữ liệu chứa chỉ dẫn không đáng tin.
- [CE-T07](outputs/CE-T07.md), [CE-T08](outputs/CE-T08.md): không kích hoạt CE khi không phù hợp; giữ Q/support.
- [Self-review records](self-review.json): SC05-shaped GateRecords, exact source/output spans và fingerprints; đây là self-review, không benchmark accuracy.
- [Mechanical report](mechanical-report.json): kết quả commands thực và giới hạn môi trường.

## How to reproduce structural checks

```bash
python -m pip install 'pytest>=8,<10' 'pyyaml>=6,<7'
python tools/validate_repository.py
python tools/validate_citation_evidence.py
python -m pytest -q
```

Validator chỉ kiểm IDs, endpoint, fingerprints, locator/excerpt và hồ sơ gate có đủ evidence fields. Nó không hiểu ngữ nghĩa, không chứng minh claim được nguồn hỗ trợ và không thực thi prompt trên host. Hash được tính trên UTF-8 với newline LF để cùng fixture có thể kiểm trên Windows/Linux.

## Read the results correctly

CE-T02 cố ý không có nguồn: target BLOCKED và review PARTIAL là hành vi kỳ vọng. CE-T07 không áp dụng CE nên NOT_RUN; không biến thành PASS để đủ tỷ lệ. Các ca còn lại có author self-review cho artifact thực trong outputs. Không công bố “8/8 citation accuracy”, learning gain hoặc independent semantic PASS.

RTC-COE design self-check: CE01–CE06 đều có sáu nhãn R/T/Context/Constraints/Output/Evaluation, một tác vụ chính, input→output→transition và criterion quan sát được. Tác giả tự đánh mỗi thành phần 3/3 cho độ rõ thiết kế v2 (18/18 mỗi phase), sau v1 5/18; điểm này không đo performance. Source correctness cho Knowledge Package được kiểm riêng với paper và access/media gaps còn giữ trong manifest.

## Next evidence layers

Lượt kiểm lại 0.3.6 có runner Luna riêng, rubric đóng băng và primary review được lưu tại [roadmap lịch sử](../../docs/citeguard/roadmap.md) và [attempt 3 lịch sử](luna-rerun-2026-10-29-r3/README.md). Các author walkthrough ở trên giữ nguyên lịch sử; không đổi nhãn chúng thành model-run evidence. Dùng `python tools/validate_luna_rerun.py` để kiểm provenance/byte fingerprints của ba attempt; validator không chấm nghĩa và công bố lỗi completeness SC05 cũ riêng.

Với capture 0.3.7, chạy `python tools/validate_sync_evidence.py --root . --require-current-context` và strict sidecar validator theo [quality guide](../../docs/quality.vi.md). [Artifact index](../../ARTIFACTS.md) chỉ đến output minh họa, hồ sơ kiểm và package/verification files của từng CI run. File được upload không tự chứng minh PASS; đọc trạng thái đúng job/run.

Host retrieval/activation NOT_RUN; independent semantic review NOT_RUN; baseline/candidate quality/cost comparison NOT_RUN; learner outcome NOT_RUN. Để chạy host, dùng cùng cases/source/config, lưu raw output trước grading, không thay expected behavior theo output. Khi so baseline/candidate, đổi thứ tự hoặc blind reviewer nếu có thể; báo rõ reviewer và điều còn thiếu theo B01.
