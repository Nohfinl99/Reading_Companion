# Development handoff bundle v1

`tools/validate_handoff_bundle.py` checks a locally prepared checkpoint and its
sidecar files together. This development utility is excluded from the runtime
package; the four existing helpers and checkpoint schema/API are unchanged.
It reads files only. It does not restore, rewrite paths, repair, rebind, export
private content, run a model, or judge semantic support/learner mastery.

## Manifest

Use UTF-8 JSON, unique keys, and the exact fields below. Unknown fields are
rejected, including inline criterion/answer payloads. SHA-256 means exact file
bytes, not normalized Markdown or reserialized JSON. Integers exclude booleans.

```json
{
  "bundle_version": 1,
  "state": {"path": "state.json", "sha256": "64 lowercase hex characters", "revision": 3},
  "sources": [{
    "source_id": "S01", "path": "book.txt", "sha256": "64 lowercase hex characters",
    "version": "edition 1 or explicit unknown", "availability": "available"
  }],
  "artifacts": [{
    "artifact_id": "handoff", "path": "learner/handoff.md",
    "sha256": "64 lowercase hex characters", "contract_version": "PS1",
    "artifact_revision": 1, "state_revision": 3, "audience": "learner",
    "depends_on": {
      "sources": [{"source_id": "S01", "sha256": "64 lowercase hex characters", "version": "edition 1 or explicit unknown"}],
      "units": [{"unit_id": "K01", "revision": 1}],
      "question": {"question_id": "Q01", "prompt_sha256": "64 lowercase hex characters", "support": "hint"}
    }
  }]
}
```

Replace hash placeholders with actual hashes. Source `availability` is
`available` or `missing`; `version` is explicit text. The manifest's source set
must equal the checkpoint's source set. The checkpoint retains its existing
absolute source paths: each must resolve to the corresponding contained bundle
source path. Relocation requires an explicit reviewed import/new session; this
checker never silently rewrites source identity.

Artifact `audience` is `learner` or `evaluator`; `contract_version` is `PS1`.
Artifact IDs and resolved paths are unique; artifacts cannot alias state,
manifest, sources, or each other. `artifact_revision` identifies the artifact
version; `state_revision` binds the snapshot it was prepared against. Declaring
a new revision/hash is a claim by the bundle author, not semantic verification.
Dependencies are explicit subsets; source dependencies bind both hash and
version; unit dependencies bind ID/revision. `question` is null when irrelevant.
Otherwise it binds exact Q ID, UTF-8 prompt hash and learner support
`unknown/none/hint/worked_example`. Placement may change from pending to paused
without changing that identity. The checker does not infer missing dependencies
or certify that every required QuestionContract/GateRecord was included.

Sidecar bytes are otherwise opaque. For example, the PS1 gate envelope supported
by a separate gate validator can be an evaluator artifact without changing that
envelope. This checker does not duplicate that validator or treat a hash as a
semantic PASS.

## Containment and separation

All manifest file paths use relative forward-slash paths. Reject absolute/drive/
UNC/ADS paths, backslashes, control characters, empty or dot segments, traversal,
and symlinks resolving outside the bundle root. Internal aliases are detected
by resolved path. No file is opened through a checkpoint source path before
matching it to a contained manifest source. This is a read-only consistency
check, not a hardened security sandbox or filesystem access-control mechanism.

The default evaluator/private manifest may reference both audiences. A learner
manifest is separately prepared and checked with `--audience learner`; it must
reference only learner artifacts. It must not embed private payloads. Keep
QuestionContract criterion/answer files only in evaluator artifacts and out of
the learner package. Explicit reserved evaluator keys in learner JSON artifacts
are rejected recursively. Markdown and natural-language leakage cannot be
certified mechanically; G-Q/CR05 still require review. Audience labels are
declarations, not proof of the content's meaning or host access permissions.

Diagnostics contain only fixed codes and list indices. They never echo payload,
criterion, Q prompt, source excerpt, or arbitrary supplied exception messages.

## Stale, missing, and safe continuation

- Missing declared sidecar, state/hash mismatch, changed source bytes, changed
  source/version dependency, stale unit revision, Q/support mismatch, and unsafe
  paths are `INVALID`. A declared available source that is absent is also invalid.
- A source explicitly declared `missing` must really be absent. The checker
  reports `PARTIAL`, names dependent artifact indices as gaps, and does not run
  the full checkpoint validator. It can carry state/provenance forward without
  claiming source validation, content mutation, assessment, or readiness.
- Artifacts bound to an older state revision are `PARTIAL`; future revisions are
  invalid. An optional previous snapshot may establish a **rebind candidate**.
  Both states must pass the existing checkpoint transition validator, revisions
  must advance by exactly one, all other top-level content/source/unit/coverage/
  assessment fields must be identical, Q IDs/prompts/support must be identical,
  and existing chapter index/connections must be unchanged. Navigation/style/
  pause/resume may differ subject to existing session guards. Unknown/missing
  previous evidence does not certify a candidate. Candidate status stays PARTIAL.
- A candidate never edits artifact metadata, clears gaps, or reuses semantic
  PASS automatically. The caller must preserve originals, review affected
  records, write a new bundle, and rerun checks. The checker has no restore writer;
  restore/import must target a new location and preserve the original on failure.

```text
python tools/validate_handoff_bundle.py /path/to/bundle/manifest.json
python tools/validate_handoff_bundle.py /path/to/bundle/learner-manifest.json --audience learner
python tools/validate_handoff_bundle.py /path/to/bundle/manifest.json --previous-state history/state-r2.json
```

`--root` optionally pins the containment root; the manifest itself must be inside
it. Previous-state paths are relative to that root. Exit codes are 0 VALID,
2 PARTIAL, 1 INVALID. VALID means declared files/dependencies passed these
mechanical checks; semantic support, complete dependency selection, authorship,
host activation and learner outcomes remain unverified. Synthetic tests in
`tests/test_handoff_bundle.py` cover the existing helper export/pause/resume
workflow and negative cases; they are not learner evidence.
