# Project evidence audit candidate 0.3.8

This is a new evaluation cycle with a new design hypothesis and rubric, frozen before candidate outputs. All included case sources are synthetic and public-safe. No private project snapshots, source maps or historical raw outputs are included.

Each file under `cases/` is a separate runner input/source context. Freeze each case independently with `skills/sid-reading-companion/scripts/project_evidence.py export` using only its corresponding case spec. Give a delegated runner only that exported bundle path in a fresh context. The exporter does not sandbox the runner's other tools or filesystem; the isolation claim is limited to the exact bundle contents and the one-bundle handoff procedure. Keep `rubric.json` outside every runner bundle.

Candidate outputs and review records are not present yet. Status is `NOT_RUN`; case specs and rubric are frozen before outputs. Old project-evidence v2 pilot artifacts remain historical and unchanged.
