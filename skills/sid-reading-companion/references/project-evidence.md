# Project evidence audit — 0.3.8

Use this route only when the user explicitly asks to audit, find, compare, select or hand off project evidence. Normal reading, extraction and progress turns do not enter this workflow.

## Owners and boundaries

- M04 routes to this reference for a project-evidence task. M07 owns plugin audit/update requests, not ordinary project evidence review.
- KC01 owns the task/source frame, actual access and locators. SC00 owns source provenance and handoff envelope. SC01 owns selection criterion, members, exclusions, universe and completeness. CE02 owns source spans; CE04 owns claim support. R12 owns continuity and handoff. R14/SC05 owns readiness and review records.
- The [JSON Schema](project-evidence-record.schema.json) and profile in [`project-evidence-profile.json`](project-evidence-profile.json) define an additive project-audit record. They do not alter checkpoint, reading-session, pending-question, unit or learner-state schemas.
- Keep the source snapshot's observed path/version/hash separate from implementation revision and current runtime. If the latter are not evidenced, explicitly mark them unknown.

## Required visible output

Have the model produce one structured audit record following [`project-evidence-record.schema.json`](project-evidence-record.schema.json) and the profile. Run the packaged standard-library helper [`project_evidence.py`](../scripts/project_evidence.py) to validate completeness and render the mandatory visible block. Do not replace that rendered block with free prose. Additional explanation may follow it.

The record must carry the SC01 criterion, included members and source locators, exclusions/not examined scope, universe/completeness/count basis, inspected and uninspected boundary, a stop reason with its evidence basis, source snapshot identity, implementation/current-runtime value or explicit unknown, and next owner plus ACK state. Missing or blank required fields fail closed. A generic completion word is a placeholder, not a stop rationale.

The helper checks declared structure, hashes and locators and deterministically renders fields. It does not decide whether evidence supports a claim or whether a stop reason is meaningful. Its output always reports `semantic_verified: false`; readiness stays PARTIAL until a separate reviewer record with criterion, reason and source/output spans is bound to the exact rendered artifact SHA-256 and source SHA-256. The review record is structural evidence of a supplied review, not cryptographic identity proof. R14 reviewer must make the semantic judgment.

## Per-case evaluation bundles

For model evaluation, freeze one case at a time with the helper's `export` command. The case spec lists one prompt, exact allowed source paths/hashes, and the captured runtime context. Keep rubric/gold material outside runner bundles. Hand the runner only the exported bundle for that case in a fresh context. Keep the exported bundle byte-for-byte unchanged while it runs; put `answer.md`, `record.json`, `visible.md` and `review.json` in a separate per-case output directory that is neither inside nor an ancestor of the bundle.

Example after exporting one case to `CASE_BUNDLE` and creating a separate empty `RUN_OUTPUT` directory:

```sh
python skills/sid-reading-companion/scripts/project_evidence.py check-bundle CASE_BUNDLE --source-root SOURCE_ROOT
python skills/sid-reading-companion/scripts/project_evidence.py render RUN_OUTPUT/record.json --root CASE_BUNDLE --output-root RUN_OUTPUT --output visible.md
# After a human R14 reviewer saves a hash-bound review.json in RUN_OUTPUT:
python skills/sid-reading-companion/scripts/project_evidence.py validate RUN_OUTPUT/record.json --root CASE_BUNDLE --output-root RUN_OUTPUT --review review.json --visible visible.md
python skills/sid-reading-companion/scripts/project_evidence.py check-bundle CASE_BUNDLE --source-root SOURCE_ROOT
```

`render` and `validate` never overwrite an existing output path. The renderer's content is independent of the review status, so the reviewer can bind the exact `visible.md` hash without a circular hash. `validate` reports readiness in separate JSON; it does not alter the rendered block.

The exporter enforces its path allowlist, rejects traversal/symlinks and overwrite, and captures hashes. This only bounds the exported bundle. It cannot sandbox the delegated agent's other tools or filesystem access; report actual tool-access controls as instruction-only unless the host supplies stronger isolation. A source/runtime mismatch makes the capture stale and requires a new bundle/run; preserve old evidence.

See the full bilingual [project evidence guide](../../../docs/project-evidence.vi.md) and [English guide](../../../docs/project-evidence.en.md) for the workflow. Public evaluation fixtures must be synthetic/sanitized; keep private project snapshots, raw outputs and source maps local.
