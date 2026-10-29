# Information Architecture pack

[Bản đồ tài liệu](../README.md) · [CiteGuard project pack](README.md) · [Danh mục artifact](../artifacts.vi.md)

Thiết kế của SID cho dự án này, dựa trên các phân biệt trong bài IA của khóa SID. Không gán taxonomy hay hierarchy dưới đây cho tác giả CiteGuard. Mục tiêu: người đọc tìm đúng nguồn, maintainer sửa đúng owner, reviewer truy được bằng chứng.

## Taxonomy — phân theo trách nhiệm artifact

| Nhóm | Điều kiện đưa vào | Owner / nơi chuẩn |
|---|---|---|
| Product orientation | Giải thích cho người mới dùng hoặc contributor | README VI/EN, docs map |
| Output guide | Giúp chọn và nhận biết artifact, dẫn ví dụ và contract | ARTIFACTS.md, docs/artifacts.*, docs/examples/outputs.md |
| Runtime instruction | Quy định AI phải làm khi nào và chuyển tiếp ra sao | SKILL, M04, CE01–CE06, R14 |
| Research knowledge | Mệnh đề được quy nguồn, không điều khiển tool | references/knowledge/citeguard.* |
| Project design | Framing, IA, SID mapping và quyết định chuyển giao | docs/citeguard/ |
| Evaluation evidence | Case, output, reviewer, logs và giới hạn | evaluation/citeguard/ |
| Mechanical assurance | Kiểm schema/links/fingerprints/guard thực thi | tools/, tests/, CI |
| Package and release | Xác định file phân phối, source identity và parity | packaging/runtime-files.json, build/verify tools, release checks |

Tiêu chí duy nhất là trách nhiệm chính. Một artifact có thể link nhóm khác, nhưng không nhân bản instruction để duy trì hai owner.

## Hierarchy — đường dẫn thật và navigation

```text
Reading_Companion/
  README.vi.md / README.md           orientation and usage
  ARTIFACTS.md                      output/documentation entry point
  CONTRIBUTING.md                   contributor entry → docs map
  docs/
    README.md                       goal-based documentation map
    usage.vi.md / usage.en.md
    artifacts.vi.md / artifacts.en.md → canonical RA/SC + examples/outputs.md
    architecture.* / principles.* / quality.*
    citeguard/
      README.md → framing / IA / SID mapping / revision notes
      correction-plan.md            current 0.3.7 correction scope
      roadmap.md                    historical 0.3.6 rerun plan
  skills/sid-reading-companion/
    SKILL.md → references/master-instruction.md (M04)
    references/citation-evidence.md (CE01–CE06) → R14 / SC05
    references/knowledge/citeguard.*
  evaluation/citeguard/
    README.md → cases / outputs / authored self-review
    luna-rerun-2026-10-29*           historical immutable runs
    sync-0.3.7/                     captured artifact / sidecar / review / checks
  packaging/runtime-files.json     runtime allowlist
  tools/                           validators / bundle checker / build / verify
  tests/                           structural and regression cases
  .github/workflows/validate.yml    CI checks and package job
```

Đây là view chọn lọc của đường dẫn dự án; dấu thụt lề thể hiện file/thư mục, các mũi tên thể hiện liên kết. Đây không phải mục lục bài nghiên cứu hoặc thứ tự mastery của người học. Runtime path cũ giữ nguyên; thêm liên kết theo nhu cầu, không chuyển file để đẹp sơ đồ. Cách tổ chức này là lựa chọn IA của SID, không phải chuẩn IA chung do GitHub quy định.

## Conceptual decomposition

```text
Citation work in reading
  Source identity
    version / access / locator / missing context
  Knowledge representation
    proposition / condition / exception
    unit revision / typed relation / provenance
  Application
    target claim / retrieved candidate / support decision
    learner-visible explanation / transfer boundary
  Assurance
    final-delta review / evidence layer / repair owner
```

## Functional decomposition

Frame → source/context → units/IA → claim support → reading artifact → review.
CE02 và CE04 kết thúc bằng mini-review; lỗi nguồn quay KC01, lỗi unit quay KC02, lỗi quan hệ quay KC03. Nguồn thiếu chặn nhánh phụ thuộc; phần độc lập vẫn dùng. Navigation và assessment cũ dùng route hiện có.

## Stakeholder view

| Người dùng | Cần làm được | Rủi ro chính | Artifact phục vụ |
|---|---|---|---|
| Người đọc | Biết tài liệu thực sự hỗ trợ gì | Nhầm truy xuất với chứng minh | Claim–evidence table, điều kiện, gap |
| Maintainer | Sửa đúng nơi, giữ tương thích | Instruction trùng/đổi state ngầm | Owner map và revision notes |
| Contributor | Tìm prompt/data/test cần sửa | Sửa bản dịch thay canonical runtime | Docs hierarchy và mapping |
| Reviewer | Kiểm nguồn, output, gate và scope | PASS tự khai bị hiểu là benchmark độc lập | Case/output/review/log riêng |

## Ontology and relations

Source/version có accessed ranges; Unit/revision dựa trên source locator; Claim dựa trên Unit/SC02; Artifact/revision thể hiện Claim; GateRecord kiểm Artifact với source/output spans. `supports` cần đọc thành mệnh đề; `references` không là prerequisite; file dependency không là learning prerequisite. Handoff giữ refs/revisions, không suy tài khoản đã nhớ.

## Matrix — phase × artifact × gate

| Phase | Input → output chính | Gate / điểm kiểm | Owner |
|---|---|---|---|
| CE01 | User/state → Frame | G-FRAME | M02 |
| CE02 | Frame/source → Manifest/spans | G-SOURCE; mini-review 1 | KC01/R07 |
| CE03 | Ranges → Units/map | G-UNITS/G-MAP/G-SELECTION | KC02/KC03 |
| CE04 | Claim/spans → Support table | G-MEANING; mini-review 2 | CE04 |
| CE05 | Support → Reading artifact | Gates theo mode/example/state | R01/R02/R13 |
| CE06 | Artifact/refs → Review | G-CITATION-REVIEW CR01–CR06 | R14 |

## Lộ trình đọc tài liệu đề xuất

Người mới: usage → danh mục artifact → ví dụ đầu ra → framing/quick start khi cần CiteGuard. Maintainer: architecture → owner matrix → canonical CE/R/SC → quality/build checks. Reviewer: correction record → source manifest → captured artifact/sidecar → review → release checks; lịch sử Luna được đọc riêng. Đây là đường đọc đề xuất theo vai trò, không bằng chứng một người đã hiểu hay đạt level.

Tại lần rà soát 2026-10-29, source 0.3.7 ở PR #11 và `main` 0.3.5 chưa đồng bộ. Docs, ZIP, account-plugin readback và installed-host activation có scope riêng; xác nhận từng lớp bằng commit/release và hồ sơ tương ứng. Human docs ngoài runtime allowlist có thể đổi mà không thay package đã phát hành. Khi sửa file có trong allowlist, cần build/verify và kiểm parity lại.
