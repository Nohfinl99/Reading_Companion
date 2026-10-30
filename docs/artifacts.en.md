# Reading Companion output catalogue

[Tiếng Việt](artifacts.vi.md) · [Synthetic examples in Vietnamese](examples/outputs.md) · [Documentation map](README.md)

This index covers all nine RA-01–RA-09 IDs in the [canonical R09 registry](../skills/sid-reading-companion/references/reading-protocols.md#r09--output-artifacts-oa1oa4). The new examples are AI-authored documentation illustrations, not captured or graded learning sessions. Catalogue completeness does not establish performance across nine capabilities. R09 owns required fields; this page introduces no second schema.

## Choose an output for the task

| ID / output | Goal and required input | Reader-facing result | Content / contract owner |
|---|---|---|---|
| RA-01 — Knowledge Map | Understand the structure of the accessed material; scope, source access, nodes/relations and locators | Outline, table or diagram with scope, node sources and gaps | KC03/KC04, R08; R09 |
| RA-02 — Concept Card | Clarify one concept; source passage and conditions | Definition, conditions/limits and locator; explanations need not always become cards | R01/R02; R09 |
| RA-03 — Argument Map | Understand how a conclusion follows; premises, evidence and conditions | Premises → conclusion with locators and relation bases | R01/R08; SC02, R09 |
| RA-04 — Comparison Matrix | Compare options against one question; options, criteria and compatible contexts | Shared criteria, compatible contexts, locators and a bounded conclusion | R03; R09 |
| RA-05 — Knowledge Library | Retain meaningful knowledge; decomposed units and sources | IDs, content, conditions, knowledge levels, citations, relations and metadata gaps | KC02/KC03, R02; R09/R11 |
| RA-06 — Recall Card | Revisit a checked unit and its critical conditions | A short supplementary card with locator and conditions; the full unit remains authoritative | R02; R09 |
| RA-07 — Transfer Exercise | Apply knowledge to a new situation when requested; target, source limits and sufficient scenario data | Outcome, new situation, source limits and one question without its answer | R13/R04; SC03/SC04, R09 |
| RA-08 — Learning Checkpoint | Give feedback after an actual response; question, raw response/skip, support and original criterion | Bounded feedback and observed result; skipping does not create an assessment | R04/R05; SC04, R09/R11 |
| RA-09 — Session Handoff | Continue or hand over a session; real goal, mode, scope, source access, processed IDs, pending and limitations | Source/state/Q/support/gaps with an explicit inventory of files actually saved | R12/R10/R11; SC00, R09 |

Session mode (`deep/extract/combined`) and style remain in control. Extract never adds a quiz. RA-07 becomes a question only for an appropriate request after preparing its criterion; it is not inserted into an extract turn. Creating a map, card or handoff does not resolve a pending Q.

## Examples and existing evidence

| Output | Documentation example | Other retained artifact/evidence | Remaining coverage gap |
|---|---|---|---|
| RA-01 | [Map](examples/outputs.md#ra-01) | [Helper map tests](../tests/test_ia_map.py), [compiler tests](../tests/test_knowledge_compiler.py) | No separate semantic review or host capture for this example |
| RA-02 | [Concept card](examples/outputs.md#ra-02) | [CiteGuard Knowledge](../skills/sid-reading-companion/references/knowledge/citeguard.md) is related sourced knowledge, not proof of a passed card output | No dedicated card run/review |
| RA-03 | [Argument map](examples/outputs.md#ra-03) | SC02 defines the contract; prose in CE captures is not automatically a complete ArgumentRecord set | No dedicated captured SC02/RA-03 run |
| RA-04 | [Comparison](examples/outputs.md#ra-04) | The [Luna-generated CE artifact](../evaluation/citeguard/sync-0.3.7/artifact.md) interprets 60/40 with source evidence; it does not test every comparison matrix | No separate matrix run/review |
| RA-05 | [Library](examples/outputs.md#ra-05) | [Knowledge manifest](../skills/sid-reading-companion/references/knowledge/citeguard-source.json); [unit fixtures](../tests/conftest.py) support helper tests | No separate model/host evaluation of the example library |
| RA-06 | [Recall card](examples/outputs.md#ra-06) | R02/R09 define its purpose and required data | No recall-card run or delayed-recall data |
| RA-07 | [Learner prompt](examples/outputs.md#ra-07) | SC03/SC04 define example/criterion contracts; the template is not a question issued in a session | No actual learner transfer response; a template does not certify G-Q |
| RA-08 | [Synthetic feedback demo](examples/outputs.md#ra-08) | [Checkpoint tests](../tests/test_checkpoint.py) use synthetic state and do not establish a real response's origin | No learner outcome; the demo must not enter learner history |
| RA-09 | [Handoff layout](examples/outputs.md#ra-09) | [Bundle spec](../specs/handoff-bundle-v1.md), [helper roundtrip tests](../tests/test_handoff_bundle.py) | No installed-host/new-chat handoff capture; the layout is not a saved bundle |

Helper tests check structure, state and transitions using fixtures generated during execution. The examples here are **authored documentation examples**, not observed model output. Actual CE model-run evidence includes the [artifact](../evaluation/citeguard/sync-0.3.7/artifact.md), [SC05 sidecar](../evaluation/citeguard/sync-0.3.7/sidecar.json), [manifest](../evaluation/citeguard/sync-0.3.7/run-manifest.json) and [primary review](../evaluation/citeguard/sync-0.3.7/review.json): one synthetic case, three criteria, with attempt1 and one repair preserved. This does not produce a “9/9” result. Host activation, new-chat persistence and learner outcomes require separate captures.

## Records and handoff files

[SC00–SC05](../skills/sid-reading-companion/references/stack-contracts.md) own shared records:

| Contract | Responsibility | Existing level / use |
|---|---|---|
| SC00 — Envelope | Source/hash/version, state revision, unit revisions, artifact refs and gaps | Canonical contract; the [bundle spec](../specs/handoff-bundle-v1.md) checks identity/dependencies with its own manifest, not full semantic validity |
| SC01 — SelectionRecord | Selector, scope/universe, criterion, members, count basis and exclusions | Contract; the [selection introduction](examples/outputs.md#selection) is illustrative, not observed selection history |
| SC02 — ArgumentRecord | Premises, typed links, conclusion, conditions, exceptions and locators | Contract and [argument example](examples/outputs.md#ra-03); no separately certified run record |
| SC03 — ExampleLink | Connect a scenario to units/arguments and bound its inferences | Contract; the [transfer example](examples/outputs.md#ra-07) is a learner view, not a claimed existing full sidecar |
| SC04 — QuestionContract | Criterion prepared before Q, target/revision, support context and validity | Criterion/answer stays in an evaluator sidecar, outside the pending learner prompt/handoff |
| SC05 — GateRecord | Artifact/revision, applicability, status, evidence spans, checks, owner and unresolved | An [actual new sidecar](../evaluation/citeguard/sync-0.3.7/sidecar.json) passes strict structural validation; semantic review remains separate |

Checkpoint JSON belongs to R11 and the four existing helpers. Do not add SC fields to `pending_question`, units or sessions unless their schemas support them. `checkpoint.py export` does not export every sidecar. Handoff requires the actual state, sources and sidecars with hash/revision checks; disclose unsaved files. The [bundle utility](../tools/validate_handoff_bundle.py) is a development checker; it does not restore/migrate a session or create account memory.

## Distinguish downloadable objects

- **Reading output/handoff:** knowledge and state from a particular reading session, with its own source access and evaluator separation.
- **Research/evaluation evidence:** attributed knowledge, synthetic fixtures, raw/model outputs and reviews. Paper metrics are not SID accuracy; evaluation records are not learner history.
- **Plugin release package:** runtime ZIP and release manifest built from the [allowlist](../packaging/runtime-files.json)/[builder](../tools/build_plugin.py), for distributing the plugin. They are not a checkpoint/handoff and do not contain a personal learning session.

See the root [artifact index](../ARTIFACTS.md) for source, evidence and package download rules. A description alone does not establish that a file was uploaded/downloaded or that the host activated a release.
