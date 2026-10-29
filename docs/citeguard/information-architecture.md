# Information Architecture pack

Thiết kế của SID cho dự án này, dựa trên các phân biệt trong bài IA của khóa SID. Không gán taxonomy hay hierarchy dưới đây cho tác giả CiteGuard. Mục tiêu: người đọc tìm đúng nguồn, maintainer sửa đúng owner, reviewer truy được bằng chứng.

## Taxonomy — phân theo trách nhiệm artifact

| Nhóm | Điều kiện đưa vào | Owner / nơi chuẩn |
|---|---|---|
| Product orientation | Giải thích cho người mới dùng hoặc contributor | README VI/EN, docs map |
| Runtime instruction | Quy định AI phải làm khi nào và chuyển tiếp ra sao | SKILL, M04, CE01–CE06, R14 |
| Research knowledge | Mệnh đề được quy nguồn, không điều khiển tool | references/knowledge/citeguard.* |
| Project design | Framing, IA, SID mapping và quyết định chuyển giao | docs/citeguard/ |
| Evaluation evidence | Case, output, reviewer, logs và giới hạn | evaluation/citeguard/ |
| Mechanical assurance | Kiểm schema/links/fingerprints/guard thực thi | tools/, tests/, CI |

Tiêu chí duy nhất là trách nhiệm chính. Một artifact có thể link nhóm khác, nhưng không nhân bản instruction để duy trì hai owner.

## Hierarchy — đường dẫn thật và navigation

```text
README.vi.md / README.md
  docs/README.md
    docs/citeguard/README.md
      framing.md
      information-architecture.md
      sid-v5-mapping.md
      revision-notes.md
  skills/sid-reading-companion/
    SKILL.md → references/master-instruction.md (M04)
    references/citation-evidence.md (CE01–CE06)
      knowledge/citeguard.md
      knowledge/citeguard-source.json
      knowledge/citeguard-relations.json
    references/reading-protocols.md (R14)
  evaluation/citeguard/
    README.md → cases.json / outputs/ / self-review.json / mechanical-report.json
  tools/validate_citation_evidence.py
  tests/test_citation_evidence.py
```

Đây là hierarchy tài liệu dự án, không mục lục bài nghiên cứu hoặc thứ tự mastery của người học. Runtime path cũ giữ nguyên; thêm liên kết theo nhu cầu, không chuyển file để đẹp sơ đồ.

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

Người mới: framing → quick start → một walkthrough. Maintainer: CE → owner matrix → cases → revision. Reviewer: source manifest → output → self-review → mechanical report. Đây là đường đọc đề xuất theo vai trò, không bằng chứng một người đã hiểu hay đạt level.
