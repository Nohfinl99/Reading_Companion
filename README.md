<p align="center">
  <img src="assets/logo.svg" alt="Reading Companion logo" width="112" height="112" />
</p>

<h1 align="center">Reading Companion</h1>

<p align="center"><strong>Trợ lý AI đọc sâu, trích xuất tri thức có nguồn và theo dõi tiến trình học tập</strong></p>
<p align="center"><em>A Vietnamese-first, source-grounded reading and knowledge-compilation plugin.</em></p>

<p align="center">
  <a href="plugin.json"><img src="https://img.shields.io/badge/Plugin-0.3.3-15324F?style=flat-square" alt="Plugin version 0.3.3" /></a>
  <a href="https://github.com/Nohfinl99/Reading_Companion/actions/workflows/validate.yml"><img src="https://github.com/Nohfinl99/Reading_Companion/actions/workflows/validate.yml/badge.svg?branch=main" alt="GitHub Actions validation status" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-2E8B57?style=flat-square" alt="MIT License" /></a>
  <img src="https://img.shields.io/badge/Language-Vietnamese%20first-7357A5?style=flat-square" alt="Vietnamese-first" />
</p>

<p align="center"><a href="README.en.md">Read in English</a></p>

Reading Companion biến một phạm vi sách hoặc tài liệu thành lời giải thích, đơn vị tri thức và bước học tiếp theo có thể truy ngược về nguồn. Người đọc chọn mục tiêu, phạm vi và cách đọc; Companion giữ mạch lập luận, locator, điều kiện áp dụng và giới hạn bằng chứng.

> **Nguyên tắc cốt lõi:** phân biệt điều tài liệu nói với điều AI suy luận, chọn hoặc biên soạn.

## Mục lục

1. [Bắt đầu nhanh](#quick-start)
2. [Chọn chế độ đọc](#reading-modes)
3. [Workflow và kiến trúc](#workflow)
4. [Nguồn và trạng thái học](#source-and-learning-state)
5. [Ví dụ trích xuất nhanh](#quick-extract)
6. [Chất lượng và giới hạn](#quality)
7. [Bản đồ tài liệu](#documentation)
8. [Đóng góp và giấy phép](#contributing)

<a id="quick-start"></a>
## 1. Bắt đầu nhanh

Mở Reading Companion trong host tương thích, cung cấp hoặc đính kèm tài liệu, rồi nêu **mục tiêu**, **phạm vi** và **mode**. Nếu chưa chọn mode, hãy yêu cầu Companion đề xuất và giải thích lý do. Repository này chứa package plugin, không phải ứng dụng web chạy độc lập; cách cài/nạp tùy host.

```text
Đọc sâu chương 2, từ mục “Problem Framing” đến hết “Opportunity Mapping”.
Giải thích mạch lập luận, gắn locator cho từng ý và dừng lại bằng một câu hỏi để tôi trả lời.
```

Hoặc:

```text
Trích xuất các ý có thể áp dụng trong phần đã chọn. Nêu tiêu chí lựa chọn và locator.
Phân biệt số lượng tác giả quy định với phần em tự chọn; nêu rõ phần nguồn còn thiếu.
```

## 2. Chọn chế độ đọc

<a id="reading-modes"></a>
| Mode | Dùng khi | Đầu ra trọng tâm |
|---|---|---|
| `deep` | Muốn hiểu khái niệm, điều kiện và lập luận | Giải thích có nguồn, quan hệ giữa các ý và câu hỏi học tập khi phù hợp |
| `extract` | Muốn tạo kho tri thức trong một phạm vi | Knowledge Units, locator, điều kiện, quan hệ và provenance của lựa chọn |
| `combined` | Muốn vừa hiểu vừa tạo artifact để xem lại | Explanation và units dùng chung ID; câu hỏi đang chờ được giữ nguyên |

Mode xác định loại tác vụ. Style như `standard`, `quick`, `chill` hoặc `challenger` chỉ điều chỉnh cách trình bày, không thay mode hay bỏ điều kiện kiểm nguồn.

## 3. Workflow và kiến trúc

<a id="workflow"></a>
Mỗi yêu cầu đi theo nhánh cần thiết: xác định goal/scope → kiểm tra quyền truy cập nguồn và locator → định tuyến stack → kiểm tra gate áp dụng → trình bày kết quả và giới hạn. Điều hướng phiên hoặc đánh giá câu trả lời đang chờ có thể dùng state hiện có mà không biên dịch lại sách.

Xem [kiến trúc hệ thống](docs/architecture.vi.md) để biết trách nhiệm của controller, Knowledge Compiler, reading protocols, data contracts, helper và CI. Sơ đồ không phải pipeline bắt buộc cho mọi lượt.

## 4. Nguồn và trạng thái học

<a id="source-and-learning-state"></a>
- Locator và phạm vi đọc giới hạn điều có thể kết luận; nguồn chưa truy cập được phải được nêu rõ.
- Số Knowledge Units phát sinh từ nội dung/phạm vi, không theo quota cố định. Nếu AI chọn danh sách, cần nêu tiêu chí, nguồn gốc và phần không chọn/chưa kiểm.
- Ví dụ mới phải nối rõ với unit và mạch lập luận liên quan; ví dụ minh họa không tự chứng minh hiệu quả.
- Tiêu đề hoặc con số do AI tạo không được trình bày như cấu trúc tác giả quy định.
- Câu hỏi đã đặt chờ câu trả lời thật (`WAIT_RESPONSE`) hoặc lệnh chuyển bước. Không tạo response, mastery, checkpoint hay memory giả.

Chi tiết field và chủ sở hữu nằm trong [bản đồ nguyên lý](docs/principles.vi.md) và [Stack contracts](skills/sid-reading-companion/references/stack-contracts.md).

## 5. Ví dụ trích xuất nhanh

<a id="quick-extract"></a>
Cuộc trò chuyện mẫu về [*AI Engineering* — Extract · Quick](https://chatgpt.com/share/6ac9b71a-81cc-83ec-a8bf-4b2d2ae85cc8) cho thấy cách nối nội dung đọc với hướng dẫn áp dụng.

<p align="center">
  <img src="assets/quick-extract-workflow.svg" alt="Chọn phạm vi, ghi rõ ý do AI tổng hợp, nối với ứng dụng và nêu giới hạn bằng chứng" width="900" />
</p>

Trong ví dụ, nhóm 10 nguyên lý được ghi là **do AI chọn và tổng hợp**, không phải danh sách đánh số chính thức của tác giả. Quy trình ứng dụng và các tỷ lệ benchmark trong chat là phần minh họa; các tỷ lệ được nêu giả định, không phải kết quả chạy Reading Companion. Nguồn chat cũng không xác nhận đã kiểm tra toàn bộ cuốn sách.

## 6. Chất lượng và giới hạn

<a id="quality"></a>
GitHub Actions kiểm tra manifest, cấu trúc/liên kết tài liệu, cú pháp helper và giao diện CLI trên Python 3.10–3.12. Những kiểm tra này không thay thế đánh giá ngữ nghĩa, thử nghiệm trên plugin host đã cài hoặc đo kết quả học tập. Không tuyên bố benchmark đạt nếu thiếu input, output và kết quả chấm thực.

Xem [các lớp kiểm tra và bằng chứng](docs/quality.vi.md) cùng [benchmark specification](skills/sid-reading-companion/references/case-benchmark.md).

## 7. Bản đồ tài liệu

<a id="documentation"></a>
| Bạn cần… | Tài liệu |
|---|---|
| Đọc kiến trúc và workflow | [Architecture](docs/architecture.vi.md) |
| Truy nguyên nguyên lý tới file sở hữu | [Principle map](docs/principles.vi.md) |
| Hiểu CI, benchmark và giới hạn bằng chứng | [Quality guide](docs/quality.vi.md) |
| Tìm các bản VI/EN | [Documentation map](docs/README.md) |
| Định tuyến, hành vi và gate runtime | [Master instruction](skills/sid-reading-companion/references/master-instruction.md) |
| Source, units và execution plan | [Knowledge compiler](skills/sid-reading-companion/references/knowledge-compiler.md) |
| Stack và trạng thái phiên | [Reading protocols](skills/sid-reading-companion/references/reading-protocols.md) |
| Schema, provenance và question state | [Stack contracts](skills/sid-reading-companion/references/stack-contracts.md) |

```text
docs/                         Human-facing architecture, principles and quality guides (VI/EN)
skills/sid-reading-companion/ Runtime entry, canonical references and optional helpers
tools/                        Repository validation
assets/                       Product logo and explanatory illustration
.github/                      CI and contribution templates
```

## 8. Đóng góp và giấy phép

<a id="contributing"></a>
Đọc [hướng dẫn đóng góp](CONTRIBUTING.md); thay đổi cần giữ định tuyến, provenance, IDs, contracts và trạng thái câu hỏi. Xem [CHANGELOG](CHANGELOG.md). Repository phát hành theo [MIT License](LICENSE).

Technical plugin ID: `sid-reading-companion` · Display name: **Reading Companion** · Version: **0.3.3**.
