# Case PE03 — implementation revision known, current runtime unknown

Task: Summarize the evidence about `service/catalog`. A signed build record supplies an implementation revision, but no current-runtime record is provided. Keep those facts separate from the source snapshot. Bound completeness to the supplied source and hand off to `ops-team`; ACK is absent.

Produce one JSON audit record under the 0.3.8 project-evidence profile and render it with the packaged helper. Include the mandatory visible block. Do not infer that the build is deployed or that the runtime is current.
