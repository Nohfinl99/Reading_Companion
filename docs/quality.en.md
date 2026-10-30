# Quality Checks and Evidence

[Tiếng Việt](quality.vi.md) · [Documentation map](README.md) · [README](../README.md)

## Evidence layers

| Layer | Question answered | Run/definition | Does not establish |
|---|---|---|---|
| Manifest and structure | Is JSON valid, are required files present, and do local Markdown links resolve? | GitHub Actions and `tools/validate_repository.py` | Book-content correctness or host activation |
| Helper smoke checks | Do Python helpers compile and expose their `--help` interfaces? | GitHub Actions on Python 3.10–3.12 | Book comprehension or external-source verification |
| Mechanical regression | Do state guards, contracts, bundles and packaging preserve behavior in the tested cases? | Repository tests through `pytest` | Semantic correctness outside the cases run or authentic learner responses |
| Integrity and SC05 | Do source snapshots, raw outputs, rubrics, reviews and gate sidecars match identity/revision/spans? | Citation/Luna/gate/sync validators | Semantic correctness of a self-declared PASS or an independent review |
| Reproducible package | Does the ZIP match its allowlist, source commit, metadata, file hashes and layout? | `build_plugin.py`, `verify_plugin_package.py` | That the account plugin or host received that ZIP |
| Case specification | Does each requirement have its own case, evidence and criterion? | [Case benchmark](../skills/sid-reading-companion/references/case-benchmark.md) | Results for runs without captured input/output/grading |
| Output review | Does a particular output meet source, meaning, mapping, state and task criteria? | Requires separately recorded input, output and grading/review | Host behavior or learning outcomes without those tests |
| Host evaluation | Has the plugin been loaded and invoked correctly in a compatible host? | Run separately on the target host | Learner outcomes |
| Learner outcome | Does a learner understand, retain or transfer content over time? | Appropriate study design and learner data | Cannot be inferred from a prompt, one output or helper test |

## Local checks

Run from the repository root:

```bash
python -m json.tool plugin.json
python -m json.tool .codex-plugin/plugin.json
python tools/validate_repository.py
python tools/validate_citation_evidence.py
python tools/validate_luna_rerun.py
python tools/validate_gate_records.py evaluation/citeguard/sync-0.3.7/sidecar.json --root evaluation/citeguard/sync-0.3.7 --expected-artifact artifact.md=1
python tools/validate_sync_evidence.py --root . --require-current-context
python -m pytest -q
python -m compileall -q tools skills/sid-reading-companion/scripts
python skills/sid-reading-companion/scripts/ia_map.py --help
python skills/sid-reading-companion/scripts/knowledge_compiler.py --help
python skills/sid-reading-companion/scripts/checkpoint.py --help
python skills/sid-reading-companion/scripts/reading_session.py --help
```

`pytest` and YAML tests require the dependencies installed in [`validate.yml`](../.github/workflows/validate.yml). The workflow runs these groups across Python 3.10, 3.11 and 3.12, then builds/verifies the runtime package from `$GITHUB_SHA`.

```bash
python tools/build_plugin.py --root . --output ../reading-companion.zip --source-commit <commit-sha>
python tools/verify_plugin_package.py ../reading-companion.zip --manifest ../reading-companion.manifest.json
```

Replace `<commit-sha>` with the actual source commit. The [allowlist](../packaging/runtime-files.json) identifies runtime files; `tools/`, `tests/`, evaluation records and most human docs belong only to the repository. The ZIP/manifest are packaging artifacts, distinct from the reading artifacts in the [output catalogue](artifacts.en.md).

Planned CI outputs are named `reading-companion-runtime` for the ZIP/manifest and `reading-companion-verification` for verification records. Check the exact workflow run to confirm successful upload and retention; planned names do not establish download availability. They also do not by themselves constitute a GitHub Release or an activated plugin.

## Find evidence for the correct version

At the 2026-10-29 review, `main` still carried 0.3.5 while [PR #11](https://github.com/Nohfinl99/Reading_Companion/pull/11) carried the 0.3.7 source. Use the run's commit when comparing evidence; do not combine the status of both branches.

- [0.3.7 correction record](citeguard/correction-plan.md): changes and evidence limits.
- [New capture/review](../evaluation/citeguard/sync-0.3.7/README.md) and [release checks](../evaluation/citeguard/sync-0.3.7/release-checks.json): candidate-linked data; inspect the recorded run/commit.
- [Historical Luna R3](../evaluation/citeguard/luna-rerun-2026-10-29-r3/README.md): the old behavioral rubric; missing SC05 fields remain recorded, and its PASS cannot certify a new candidate.

Account-plugin readback requires comparing each canonical file with the tested package. Installed-host activation and a multi-turn/new-chat workflow require separate captures on the exact release; neither follows from CI or readback.

## Reporting rules

1. Identify the artifact/version, environment, input, output and evidence layer.
2. Report a case as passed only when actual input, output and grading are available; retain traceable evidence.
3. Use `NOT_RUN` for an unexecuted layer; `OUTPUT_CAPTURED_UNGRADED` is not a pass.
4. Keep structural/helper, semantic review, rendering, installed-host and learner-outcome results separate.
5. Do not present a hypothetical benchmark or same-run self-review as an independent result.

Detailed cases and evidence rules are in the [benchmark specification](../skills/sid-reading-companion/references/case-benchmark.md). This guide describes the checks; it does not claim a successful benchmark or certify book interpretations.

