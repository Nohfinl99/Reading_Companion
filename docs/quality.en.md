# Quality Checks and Evidence

[Tiếng Việt](quality.vi.md) · [README](../README.en.md)

## Evidence layers

| Layer | Question answered | Run/definition | Does not establish |
|---|---|---|---|
| Manifest and structure | Is JSON valid, are required files present, and do local Markdown links resolve? | GitHub Actions and `tools/validate_repository.py` | Book-content correctness or host activation |
| Helper smoke checks | Do Python helpers compile and expose their `--help` interfaces? | GitHub Actions on Python 3.10–3.12 | Book comprehension or external-source verification |
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
python -m compileall -q tools skills/sid-reading-companion/scripts
python skills/sid-reading-companion/scripts/ia_map.py --help
python skills/sid-reading-companion/scripts/knowledge_compiler.py --help
python skills/sid-reading-companion/scripts/checkpoint.py --help
python skills/sid-reading-companion/scripts/reading_session.py --help
```

The [`validate.yml`](../.github/workflows/validate.yml) workflow runs the corresponding groups across Python 3.10, 3.11 and 3.12.

## Reporting rules

1. Identify the artifact/version, environment, input, output and evidence layer.
2. Report a case as passed only when actual input, output and grading are available; retain traceable evidence.
3. Use `NOT_RUN` for an unexecuted layer; `OUTPUT_CAPTURED_UNGRADED` is not a pass.
4. Keep structural/helper, semantic review, rendering, installed-host and learner-outcome results separate.
5. Do not present a hypothetical benchmark or same-run self-review as an independent result.

Detailed cases and evidence rules are in the [benchmark specification](../skills/sid-reading-companion/references/case-benchmark.md). This guide describes the checks; it does not claim a successful benchmark or certify book interpretations.
