<p align="center">
  <img src="assets/logo.svg" alt="Reading Companion logo" width="112" height="112" />
</p>

<h1 align="center">Reading Companion</h1>

<p align="center"><strong>A source-grounded AI companion for deep reading, knowledge extraction and learning progress</strong></p>
<p align="center"><em>Vietnamese-first reading and knowledge compilation, with bilingual project documentation.</em></p>

<p align="center">
  <a href="plugin.json"><img src="https://img.shields.io/badge/Plugin-0.3.3-15324F?style=flat-square" alt="Plugin version 0.3.3" /></a>
  <a href="https://github.com/Nohfinl99/Reading_Companion/actions/workflows/validate.yml"><img src="https://github.com/Nohfinl99/Reading_Companion/actions/workflows/validate.yml/badge.svg?branch=main" alt="GitHub Actions validation status" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-2E8B57?style=flat-square" alt="MIT License" /></a>
  <img src="https://img.shields.io/badge/Language-Vietnamese%20first-7357A5?style=flat-square" alt="Vietnamese-first" />
</p>

<p align="center"><a href="README.md">Đọc bằng tiếng Việt</a></p>

Reading Companion turns a selected portion of a book or document into an explanation, traceable knowledge units and a next learning step. Readers choose the goal, scope and reading mode; the Companion preserves argument flow, locators, application conditions and evidence limits.

> **Core principle:** distinguish what the source says from what AI infers, selects or creates.

## Contents

1. [Quick start](#quick-start)
2. [Choose a reading mode](#reading-modes)
3. [Workflow and architecture](#workflow)
4. [Sources and learning state](#source-and-learning-state)
5. [Quick extraction example](#quick-extract)
6. [Quality and limits](#quality)
7. [Documentation map](#documentation)
8. [Contributing and license](#contributing)

<a id="quick-start"></a>
## 1. Quick start

Open Reading Companion in a compatible host, provide or attach the material, then state the **goal**, **scope** and **mode**. If no mode is selected, ask the Companion to recommend one and explain why. This repository contains the plugin package, not a standalone web application; installation/loading steps depend on the host.

```text
Read chapter 2 deeply, from “Problem Framing” through “Opportunity Mapping”.
Explain the argument flow, attach locators to each point and stop with a question for me to answer.
```

Or:

```text
Extract applicable ideas from the selected section. State the selection criteria and locators.
Distinguish author-specified counts from your own selection; identify any source gaps.
```

## 2. Choose a reading mode

<a id="reading-modes"></a>
| Mode | Use it when | Main output |
|---|---|---|
| `deep` | You want to understand concepts, conditions and arguments | Sourced explanation, relationships between ideas and a learning question when appropriate |
| `extract` | You want a knowledge set from a defined scope | Knowledge Units, locators, conditions, relations and selection provenance |
| `combined` | You want understanding and reusable artifacts together | Explanation and units share IDs; pending questions remain pending |

Mode identifies the task. Styles such as `standard`, `quick`, `chill` or `challenger` adjust presentation only; they do not change the mode or relax source checks.

## 3. Workflow and architecture

<a id="workflow"></a>
Each request takes the route it needs: frame goal/scope → check source access and locators → route to a stack → apply relevant gates → present the result and its limits. Session navigation or assessment of a pending answer can use existing state without recompiling the book.

See the [system architecture](docs/architecture.en.md) for responsibilities across the controller, Knowledge Compiler, reading protocols, data contracts, helpers and CI. The diagram describes available routes, not a mandatory pipeline for every turn.

## 4. Sources and learning state

<a id="source-and-learning-state"></a>
- Locators and reading scope bound claims; inaccessible source material must be identified.
- Knowledge Unit counts follow the content and selected scope, not a fixed quota. If AI selects a list, it states the criteria, origin and what was excluded or unchecked.
- New examples explicitly connect to the relevant unit and argument; an illustrative example does not prove effectiveness.
- AI-created headings or counts must not be presented as author-defined structure.
- A question remains `WAIT_RESPONSE` until the learner answers or asks to move on. Do not fabricate responses, mastery, checkpoints or memory.

Field details and owners are in the [principle map](docs/principles.en.md) and [Stack contracts](skills/sid-reading-companion/references/stack-contracts.md).

## 5. Quick extraction example

<a id="quick-extract"></a>
The [*AI Engineering* Extract · Quick conversation](https://chatgpt.com/share/6ac9b71a-81cc-83ec-a8bf-4b2d2ae85cc8) illustrates how reading content can be connected to an application guide.

<p align="center">
  <img src="assets/quick-extract-workflow.svg" alt="Select scope, label AI-curated ideas, connect them to an application, and state evidence limits" width="900" />
</p>

In the example, the set of 10 principles is explicitly labeled as **selected and synthesized by AI**, not an official numbered list from the author. The application workflow and benchmark percentages in the conversation are illustrative; the percentages are hypothetical, not Reading Companion results. The conversation also does not establish that the entire book was reviewed.

## 6. Quality and limits

<a id="quality"></a>
GitHub Actions checks manifests, repository structure and documentation links, helper syntax and CLI interfaces on Python 3.10–3.12. These checks do not replace semantic review, tests on an installed plugin host or measurement of learning outcomes. A benchmark is not reported as passed without actual input, output and grading results.

See [checks and evidence](docs/quality.en.md) and the [benchmark specification](skills/sid-reading-companion/references/case-benchmark.md).

## 7. Documentation map

<a id="documentation"></a>
| If you need… | Read… |
|---|---|
| Architecture and workflow | [Architecture](docs/architecture.en.md) |
| Principle-to-owner traceability | [Principle map](docs/principles.en.md) |
| CI, benchmark and evidence limits | [Quality guide](docs/quality.en.md) |
| All Vietnamese/English pages | [Documentation map](docs/README.md) |
| Runtime routing, behavior and gates | [Master instruction](skills/sid-reading-companion/references/master-instruction.md) |
| Sources, units and execution plans | [Knowledge compiler](skills/sid-reading-companion/references/knowledge-compiler.md) |
| Stacks and session state | [Reading protocols](skills/sid-reading-companion/references/reading-protocols.md) |
| Schemas, provenance and question state | [Stack contracts](skills/sid-reading-companion/references/stack-contracts.md) |

```text
docs/                         Human-facing architecture, principles and quality guides (VI/EN)
skills/sid-reading-companion/ Runtime entry, canonical references and optional helpers
tools/                        Repository validation
assets/                       Product logo and explanatory illustration
.github/                      CI and contribution templates
```

## 8. Contributing and license

<a id="contributing"></a>
Read the [contribution guide](CONTRIBUTING.md); changes should preserve routing, provenance, IDs, contracts and pending-question state. See the [changelog](CHANGELOG.md). The repository is distributed under the [MIT License](LICENSE).

Technical plugin ID: `sid-reading-companion` · Display name: **Reading Companion** · Version: **0.3.3**.
