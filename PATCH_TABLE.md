# Patch table — Reading Companion 0.3.3

Source: public repository `Nohfinl99/Reading_Companion`, branch `main`, snapshot commit `a068c628a8f6bc5e19fb989f6e38f3ce9e243bd9`. The 0.3.3 overlay archive was merged on top of that repository snapshot.

| File or group | Change | Reason / effect |
|---|---|---|
| `plugin.json`, `.codex-plugin/plugin.json` | Integrated version 0.3.3 manifests | Keep identity, presentation and prompts aligned with the account plugin release. |
| `skills/sid-reading-companion/SKILL.md` | Integrated updated entry point and references | Routes to the canonical controller, stack contracts, protocols and benchmark. |
| `references/master-instruction.md` | Reworded workflow and ownership; removed SID Master/session references and training-level comparisons | Makes controller rules product-specific and describes routing without implying a fixed six-stage pipeline. Stable M-section anchors remain for internal links. |
| `references/knowledge-compiler.md` | Integrated 0.3.3 source, unit-boundary and list-provenance rules | Counts units from selected scope/content and exposes selection criteria/origins. |
| `references/reading-protocols.md` | Integrated updated task stacks; rewrote R00 in direct product language and updated heading version | Keeps modes, pending questions, source links, examples and handoff consistent without training-framework wording. |
| `references/stack-contracts.md` | Added canonical data contracts | Gives one owner for selection, argument/example links, question criteria and gate states. |
| `references/case-benchmark.md` | Integrated benchmark specifications | Separates requirements/cases/evidence and forbids inferring results from design or helper checks. |
| `README.md` | Rebuilt architecture, mode guidance, setup and limits | Removes stale six-phase claims, missing file paths and unsupported automatic-verification claims. |
| `CONTRIBUTING.md` | Corrected clone URL and validation guidance | Names the actual repository and distinguishes smoke checks from semantic evaluation. |
| `.github/workflows/validate.yml` | Adds repository validator and Python syntax compilation | CI checks package paths/manifests/relative Markdown links and helper CLI syntax; it does not grade benchmark meaning. |
| `tools/validate_repository.py` | Added deterministic repository checks | Verifies paired manifest identity/presentation, required plugin files and local Markdown targets. |
| `evaluation/README.md`, `evaluation/runs/2026-10-10-ps1r4/` | Added raw input/output evidence and hashes for PS01–PS07 | Keeps actual model outputs separate from the benchmark specification and labels them ungraded. |
| `CHANGELOG.md` | Added version notes | Records scope and limits of this repository package. |
| `VALIDATION_REPORT.md`, `UPLOAD_GUIDE.md` | Added checks/evidence status and manual GitHub instructions | Separates passing structure/smoke checks from `NOT_RUN` semantic/host outcomes and leaves all GitHub writes to the owner. |

Unchanged: plugin technical name/ID, skill name, mode names, helper scripts, source/checkpoint IDs, state schemas, license and asset. No GitHub commit or push was performed.
