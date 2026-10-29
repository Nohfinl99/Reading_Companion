# Documentation map / Bản đồ tài liệu

**Languages / Ngôn ngữ:** [Tiếng Việt](../README.vi.md) · [English](../README.md)

This directory helps readers use the product, inspect its outputs and maintain its source. The paired Vietnamese and English pages are kept in parallel; technical identifiers and file paths remain unchanged. Runtime behavior and schemas are owned by the files under [`skills/sid-reading-companion/references/`](../skills/sid-reading-companion/references/master-instruction.md), not by translations in this directory.

Thư mục này giúp người đọc sử dụng sản phẩm, xem đầu ra và bảo trì source. Các trang tiếng Việt và tiếng Anh được duy trì song song; technical identifiers và đường dẫn file được giữ nguyên. Hành vi runtime và schema do các file trong [`skills/sid-reading-companion/references/`](../skills/sid-reading-companion/references/master-instruction.md) sở hữu, không do bản dịch ở đây định nghĩa lại.

| Topic / Chủ đề | Tiếng Việt | English | Canonical source / Nguồn chuẩn |
|---|---|---|---|
| Start reading / Bắt đầu đọc | [Hướng dẫn sử dụng](usage.vi.md) | [Usage guide](usage.en.md) | [Skill entry point](../skills/sid-reading-companion/SKILL.md) |
| Outputs / Đầu ra | [Danh mục artifact](artifacts.vi.md) | [Artifact catalogue](artifacts.en.md) | [RA-01–RA-09](../skills/sid-reading-companion/references/reading-protocols.md), [SC00–SC05](../skills/sid-reading-companion/references/stack-contracts.md) |
| Examples / Ví dụ | [Ví dụ đầu ra và giới hạn](examples/outputs.md) | [Output examples and limits](examples/outputs.md) | Each example identifies its source and evidence layer / Mỗi ví dụ ghi nguồn và lớp bằng chứng |
| Architecture / Kiến trúc | [Tổng quan kiến trúc](architecture.vi.md) | [Architecture overview](architecture.en.md) | [Master instruction](../skills/sid-reading-companion/references/master-instruction.md) |
| Principles / Nguyên lý | [Bản đồ nguyên lý](principles.vi.md) | [Principle map](principles.en.md) | [Knowledge compiler](../skills/sid-reading-companion/references/knowledge-compiler.md), [stack contracts](../skills/sid-reading-companion/references/stack-contracts.md) |
| Quality / Chất lượng | [Kiểm tra và bằng chứng](quality.vi.md) | [Checks and evidence](quality.en.md) | [Case benchmark](../skills/sid-reading-companion/references/case-benchmark.md), [CI workflow](../.github/workflows/validate.yml) |
| CiteGuard / SID V5 | [Project pack và IA](citeguard/README.md) | [Bilingual entry and evidence limits](citeguard/README.md) | [CE01–CE06](../skills/sid-reading-companion/references/citation-evidence.md), [self-review](../evaluation/citeguard/README.md) |
| Maintain and package / Bảo trì và đóng gói | [Đóng góp](../CONTRIBUTING.md), [kiểm chứng](quality.vi.md) | [Contributing](../CONTRIBUTING.md), [checks](quality.en.md) | [Runtime allowlist](../packaging/runtime-files.json), [CI workflow](../.github/workflows/validate.yml) |
| 0.3.7 evidence / Bằng chứng 0.3.7 | [Hồ sơ sửa và phần chưa chạy](citeguard/correction-plan.md) | [Correction record and untested scope](citeguard/correction-plan.md) | [Captured output and review](../evaluation/citeguard/sync-0.3.7/README.md), [release checks](../evaluation/citeguard/sync-0.3.7/release-checks.json) |

## Read by goal / Đọc theo mục tiêu

- Người dùng: usage → một ví dụ → artifact cần nhận. / Reader: usage → one example → the desired artifact.
- Contributor: architecture → principles → canonical owner → quality checks. / Contributor: architecture → principles → canonical owner → quality checks.
- Reviewer: correction record → captured input/output and review → release checks; xem riêng các lớp chưa chạy. / Reviewer: correction record → captured input/output and review → release checks; inspect untested layers separately.

The [root artifact index](../ARTIFACTS.md) is the repository entry point for these outputs. This is the project's navigation design; it is not a universal GitHub IA standard.

[Chỉ mục artifact ở root](../ARTIFACTS.md) là lối vào repository cho các đầu ra này. Đây là cách tổ chức tài liệu của dự án, không phải chuẩn IA chung của GitHub.

## Source and release scope / Phạm vi source và release

At the 2026-10-29 review, `main` still described 0.3.5 while [PR #11](https://github.com/Nohfinl99/Reading_Companion/pull/11) carried the 0.3.7 source. Read the selected branch/commit and its checks together. Account-plugin readback, installed-host activation and learner outcomes are separate evidence; a repository page or CI pass does not establish them.

Tại lần rà soát 2026-10-29, `main` vẫn mô tả 0.3.5, còn [PR #11](https://github.com/Nohfinl99/Reading_Companion/pull/11) chứa source 0.3.7. Đọc đúng branch/commit cùng kiểm tra của nó. Readback plugin tài khoản, activation trên host và kết quả học là các lớp bằng chứng riêng; trang repository hoặc CI PASS chưa xác nhận các lớp đó.

## Maintenance rule / Quy tắc duy trì

Edit the Vietnamese page first, preserve its technical identifiers and evidence limits, then update the English counterpart in the same change. Link to canonical contracts instead of copying schemas. Review both pages whenever a linked source changes.

Sửa bản tiếng Việt trước, giữ nguyên technical identifiers và giới hạn bằng chứng, sau đó cập nhật bản tiếng Anh trong cùng thay đổi. Liên kết đến hợp đồng chuẩn thay vì sao chép schema. Rà soát cả hai bản khi nguồn được liên kết thay đổi.

