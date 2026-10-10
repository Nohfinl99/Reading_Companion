# Documentation map / Bản đồ tài liệu

**Languages / Ngôn ngữ:** [Tiếng Việt](../README.vi.md) · [English](../README.md)

This directory explains the product architecture for human readers. The paired Vietnamese and English pages are kept in parallel; technical identifiers and file paths remain unchanged. Runtime behavior and schemas are owned by the files under [`skills/sid-reading-companion/references/`](../skills/sid-reading-companion/references/master-instruction.md), not by translations in this directory.

Thư mục này giải thích kiến trúc sản phẩm cho người đọc. Các trang tiếng Việt và tiếng Anh được duy trì song song; technical identifiers và đường dẫn file được giữ nguyên. Hành vi runtime và schema do các file trong [`skills/sid-reading-companion/references/`](../skills/sid-reading-companion/references/master-instruction.md) sở hữu, không do bản dịch ở đây định nghĩa lại.

| Topic / Chủ đề | Tiếng Việt | English | Canonical source / Nguồn chuẩn |
|---|---|---|---|
| Architecture / Kiến trúc | [Tổng quan kiến trúc](architecture.vi.md) | [Architecture overview](architecture.en.md) | [Master instruction](../skills/sid-reading-companion/references/master-instruction.md) |
| Principles / Nguyên lý | [Bản đồ nguyên lý](principles.vi.md) | [Principle map](principles.en.md) | [Knowledge compiler](../skills/sid-reading-companion/references/knowledge-compiler.md), [stack contracts](../skills/sid-reading-companion/references/stack-contracts.md) |
| Quality / Chất lượng | [Kiểm tra và bằng chứng](quality.vi.md) | [Checks and evidence](quality.en.md) | [Case benchmark](../skills/sid-reading-companion/references/case-benchmark.md), [CI workflow](../.github/workflows/validate.yml) |

## Maintenance rule / Quy tắc duy trì

Edit the Vietnamese page first, preserve its technical identifiers and evidence limits, then update the English counterpart in the same change. Link to canonical contracts instead of copying schemas. Review both pages whenever a linked source changes.

Sửa bản tiếng Việt trước, giữ nguyên technical identifiers và giới hạn bằng chứng, sau đó cập nhật bản tiếng Anh trong cùng thay đổi. Liên kết đến hợp đồng chuẩn thay vì sao chép schema. Rà soát cả hai bản khi nguồn được liên kết thay đổi.
