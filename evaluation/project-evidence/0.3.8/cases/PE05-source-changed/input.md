# Case PE05 — source changed since the handoff

Task: Continue a project evidence handoff for `service/search`. A prior handoff is bound to the old-source hash in `prior-handoff.json`; the only supplied current source has a different hash. A reading snapshot contains a pending question with `support: hint`. Stop reuse that depends on the changed source, keep the pending question and support as supplied, and state the reimport/compare task. Handoff owner is `source-maintainer`; consumer ACK is unknown.

Produce one structured audit record under the 0.3.8 profile and render its mandatory visible block. The project-evidence helper is not a learner-state mutator; do not modify the supplied snapshot or claim the old PASS remains current.
