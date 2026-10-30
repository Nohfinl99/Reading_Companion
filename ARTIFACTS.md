# Artifact index / Mục lục đầu ra

Trang này là lối vào cho người xem GitHub. Contract runtime vẫn thuộc R09 và SC00–SC05; đây là bản đồ mô tả và bằng chứng, không phải schema mới.

## Tôi cần tìm gì? / Find by goal

| Mục tiêu | Đi tới | Loại bằng chứng |
|---|---|---|
| Xem chín output RA-01–RA-09 | [Catalog tiếng Việt](docs/artifacts.vi.md) / [English](docs/artifacts.en.md) | Contract + mô tả; không là chín ca đã chạy |
| Xem hình dạng output cho người đọc | [Ví dụ minh họa](docs/examples/outputs.md) | Synthetic do AI tạo, không phải learner/model run |
| Hiểu cách sắp xếp file và chủ sở hữu | [Docs hub](docs/README.md), [IA view](docs/citeguard/information-architecture.md) | Kiến trúc tài liệu của dự án |
| Đối chiếu trường/schema chuẩn | [R09 registry](skills/sid-reading-companion/references/reading-protocols.md), [SC contracts](skills/sid-reading-companion/references/stack-contracts.md) | Nguồn canonical; xem section R09 và SC00–SC05 |
| Xem output model đã thực sự tạo | [Capture 0.3.7](evaluation/citeguard/sync-0.3.7/README.md), [artifact](evaluation/citeguard/sync-0.3.7/artifact.md), [SC05 sidecar](evaluation/citeguard/sync-0.3.7/sidecar.json) | Một delegated synthetic case; có primary review và một repair |
| Xem cách bàn giao state/sidecar | [Bundle spec](specs/handoff-bundle-v1.md), [roundtrip helper tests](tests/test_handoff_bundle.py) | Specification + synthetic helper evidence; chưa host/new-chat proof |
| Xem nguồn của package plugin | [Runtime allowlist](packaging/runtime-files.json), [builder](tools/build_plugin.py), [verifier](tools/verify_plugin_package.py) | Bốn helper, một skill; package khác bundle phiên đọc |
| Tải package hoặc kết quả kiểm | [GitHub Actions](https://github.com/Nohfinl99/Reading_Companion/actions/workflows/validate.yml), [workflow](.github/workflows/validate.yml) | Artifact của từng CI run, cần xem trạng thái run và commit |

## Các file được giữ từ CI

Workflow giữ hai nhóm bằng `actions/upload-artifact`:

- `reading-companion-runtime-<sha>`: runtime ZIP và manifest hash/source commit từ job Python 3.12 thành công.
- `reading-companion-verification-py<version>-<sha>`: JUnit XML nếu test đã chạy, cùng capture/sidecar/review/context của synthetic case 0.3.7. Kiểm trạng thái job riêng; file được upload không tự chứng minh test PASS.

Thời gian giữ cấu hình là 30 ngày, chịu giới hạn repository. Cần đăng nhập và quyền đọc để tải workflow artifact; đây chưa phải GitHub Release/tag và không là kho lưu vĩnh viễn. Xem [GitHub Docs về workflow artifacts](https://docs.github.com/en/actions/tutorials/store-and-share-data) và [download](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/download-workflow-artifacts).

Không upload sách riêng hoặc state người học thật. Gói verification chứa fixture tổng hợp và rubric phát triển, không dùng như learner handoff khi còn Q pending.

## Đồng bộ và giới hạn

Plugin tài khoản đã lưu bản 0.3.7 và 27 canonical files đã được đọc lại đối chiếu. [Hồ sơ đồng bộ](evaluation/citeguard/sync-0.3.7/release-checks.json) ghi source commit, CI và readback; không chứng minh host đã nạp hoặc hoạt động xuyên phiên.

[Bản rà IA/artifact](evaluation/citeguard/sync-0.3.7/ia-audit.json) ghi lần kiểm đồng bộ và trạng thái artifact của run được quan sát; dùng đúng run/commit trong hồ sơ.

Bản 0.3.7 nằm trên [PR #11](https://github.com/Nohfinl99/Reading_Companion/pull/11); `main` vẫn là 0.3.5 tại thời điểm rà IA ngày 2026-10-29. Những cải thiện docs/CI này không đổi runtime allowlist payload, nên không tạo một release plugin mới chỉ cho bản đồ tài liệu. Trạng thái PR/main cần đọc lại khi dùng về sau.

Readiness phải báo theo lớp: contract → ví dụ synthetic → helper → model output → host → learner outcome. Không có phép nâng PASS tự động giữa các lớp.
