# Case PE01 — same-title report from the wrong root

Task: Select evidence for the user's requested component, `core/orchestrator`, under source root `workspace-A`. A report with the same title exists under `workspace-B` with a later document date. Use only the supplied files in this case bundle.

Create one JSON audit record following `project-evidence-profile.json`. Do not invent implementation revision or current runtime when the supplied sources do not establish them. Select only evidence that applies to the requested root/component, explain the excluded candidate, bound the searched scope, and state a stop reason with evidence basis. Mark next owner `reviewer-Q`; ACK was not supplied. Then run the packaged `project_evidence.py` helper to validate and render the mandatory visible block. Your final answer must include that rendered block. Keep any separate R14 semantic review `NOT_RUN`; do not self-certify.
