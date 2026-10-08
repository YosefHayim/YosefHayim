# Agent instructions

## Local CI

Run `act workflow_dispatch -W .github/workflows/ci.yml` before opening a PR.
The CI workflow checks script syntax only. Do not run the profile updater locally with its push step enabled.
