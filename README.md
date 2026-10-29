# Reading Companion

<img src="assets/logo.svg" alt="Reading Companion" width="96" />

![Plugin version](https://img.shields.io/badge/Plugin-0.3.7-15324F)
[Tiếng Việt](README.vi.md) · [Usage guide](docs/usage.en.md) · [Changes](CHANGELOG.md)

Reading Companion is a Vietnamese-first plugin for source-grounded deep reading, knowledge extraction and portable reading checkpoints. Technical identity: `sid-reading-companion`. It contains one skill and four optional Python helpers.

Version 0.3.7 unifies source/account continuity guards, requires complete evidence-linked citation gate records for new reviews, and adds repository tools for reproducible packaging and handoff-bundle checks. See the [correction plan and evidence boundaries](docs/citeguard/correction-plan.md).

## Start reading

Attach the actual source and give the goal, scope and mode:

> Read section 2 in combined mode, standard style. Explain the author's argument and conditions, extract reusable units with locators, then ask one question and wait for my answer.

| Mode | Behavior |
|---|---|
| `deep` | Explain source meaning and argument flow; standard style asks one question and waits. |
| `extract` | Produce sourced units, conditions and relations; no quiz. |
| `combined` | Share source/unit IDs between explanation and extraction; preserve pending questions. |

Style changes presentation; it does not change mode. A hint remains recorded as assistance. Opening a chapter or creating a card does not establish mastery.

## Check a claim

> Compare claim [C] with the attached source, within [range]. Show the exact source/locator, support level, critical conditions and gaps. Apply the result to my reading artifact, then review the final artifact without changing mode or answering my pending question.

Citation attribution, source support and external truth are separate questions. The CiteGuard Knowledge Package and CE01–CE06 instructions guide the host; they do not install corpus search or a citation-verification service.

## Continue in another chat

Request a handoff containing source/version/hash, unit IDs/revisions, cursor, pending/paused question, assistance history and gaps. Bring the source, checkpoint and generated sidecars to the next chat. Keep evaluator criteria/answers separate from the learner view while a question is pending.

The plugin has no account memory. `checkpoint.py export` exports checkpoint content, not all sidecars. The optional repository bundle checker detects missing/stale files; the host must actually run it before reporting that structural check as complete.

## Architecture and source ownership

`SKILL → M04 → source/units → reading or citation protocol → R14/SC05 → R12 handoff`

- Controller M01–M07 owns routing and scope.
- Knowledge Compiler owns sources, unit boundaries/count and relations.
- Reading protocols own explanations, Q/support, state and handoff.
- SC00–SC05 define exchanged artifacts; CE06 uses the existing G-CITATION-REVIEW gate.
- Four helpers check plans/maps/checkpoints/session state. Meaning and claim support require source-grounded review by the host/reviewer.

## Verification and build

From a repository checkout, using Python 3.10–3.12:

```sh
python tools/validate_repository.py
python tools/validate_citation_evidence.py
python tools/validate_luna_rerun.py
python -m pytest -q
python tools/build_plugin.py --root . --output ../reading-companion.zip --source-commit <commit-sha>
```

The runtime allowlist is `packaging/runtime-files.json`. Build from the pinned source; test the staged package and compare readback after updating the account plugin. Retained backend legacy files are separate from canonical runtime files.

Historical Luna runs retain original raw outputs and rubric results, including the incomplete SC05 record observed in CE-T01. Historical behavioral PASS does not prove schema compliance. New gate records must pass the strict validator and a separate meaning review. Helpers do not establish host activation, general citation accuracy, cost improvement or learning gain. Current evidence is reported in the [correction plan](docs/citeguard/correction-plan.md).

Repository-only tooling: [tools and tests](https://github.com/Nohfinl99/Reading_Companion/tree/feat/sid-v5-citeguard-reading) · [historical run evidence](https://github.com/Nohfinl99/Reading_Companion/tree/709d19bc27c65270a487a5aa0a6eb6fde67d74f7/evaluation/citeguard).

## License

[MIT](LICENSE). Research claims retain their original source attribution. Private books and SID course source files are not distributed in the runtime package.
