# Submitting content

Open a Mod submission issue or pull request containing the original editable source, manifest,
license/redistribution evidence, dependencies, size/hash from `tools/package.py`, and gameplay
evidence covering laps, pits, scoring and season continuation where relevant.
Use fictional/original material or document permission. Do not submit proprietary game assets.
ZIP binaries go in Releases after review, not regular Git history.

Read-only CI validates JSON and data folders with the trusted base-branch validator. It executes
no scripts from the submitted package, receives no secrets and has no write permission.
Maintainers separately review provenance, asset safety, compatibility and actual gameplay.
Approval is manual; Issues/PRs never publish themselves.

The trusted `publish.yml` workflow runs only from main on manual dispatch. Its only elevated
permission is contents:write for Releases and the catalog commit. It does not use
pull_request_target. Checkout is pinned to a commit verified against actions/checkout v4.
Review upstream changes and update that pin through an ordinary PR.
See [GitHub's secure use guidance](https://docs.github.com/en/actions/reference/security/secure-use).

For an initial local publication, run `pwsh tools/setup.ps1` after reviewing the source set and
ensuring `gh auth status` identifies the intended owner. It reuses only the named public
distribution repository, refuses a private one, retains existing assets, and verifies public
downloads before exposing a catalog.
