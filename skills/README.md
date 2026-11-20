# Agent skills

> **Fork addition** — this README was added by this fork; it is not part of the original skills tree.

## Attribution

The skills in this directory were authored by **Josh Preston (@mrjoshuap)** and contributors
(including Cursor Agent and the mrjoshuap-engineering bot) for the
[mrjoshuap-hq/mediacms](https://github.com/mrjoshuap-hq/mediacms) fork, and are imported here
**verbatim** from its `mediacms-next` branch (commit `a8c0ce1`, 2026-11-19) with the author's
knowledge — he described this skills setup in his review of mediacms-io/mediacms#1620.
MediaCMS is licensed AGPLv3; these files carry the same license as the repository they
live in. All credit for their content belongs to the original authors.

## Index

### Domain skills — apply to MediaCMS work on this fork

| Skill | Covers |
|---|---|
| `dev-stack` | Docker Compose dev stack: up/down, image builds, rebuilds, service restarts |
| `dev-manage` | `manage.py` and DB tasks inside the web container |
| `dev-api` | REST API smoke tests against a running dev instance |
| `test-ci` | Backend/frontend tests, CI, pre-commit, flake8/Jest failures |
| `i18n` | Translations (React frontend + Django admin), RTL checks |
| `media-pipeline` | Encoding, HLS, storage paths, nginx media auth, MediaAction auditing |
| `rbac-permissions` | Roles/permissions across docs, backend, frontend; `CAN_*` gates |
| `admin-portal` | Jazzmin admin portal: dashboard, sidebar, changelists, themes |
| `auth-identity` | django-allauth, login options, OAuth/social, SAML |
| `issue-triage` | Issue triage and minimal-impact fix planning |

### This fork's governance — applies here

| Skill | Covers |
|---|---|
| `fork-maintainer` | This fork's workflow: branch/PR flow against fork main, the no-upstream-PR policy, PR template disclosure/attestation ownership, commit trailers, AGENTS.md parity with upstream PR #1620 |

### Imported fork-governance skills — reference only on this fork

The four skills below document the **source fork's** (mrjoshuap-hq) process (branch targets,
release channels, plan archives). They are kept for reference and credit; their rules do **not**
apply here. On this fork, the workflow rules in `AGENTS.md`, this repository's PR conventions,
and `skills/fork-maintainer/` govern.

| Skill | Documents (source fork) |
|---|---|
| `maintainer` | mrjoshuap-hq branch targets, upstream PR rules, labels, AI disclosure |
| `merge-hygiene` | Merging branches into that fork's `mediacms-next` |
| `fork-docs-release` | That fork's docs channels and GHCR releases |
| `plan-history` | That fork's `.agent/` plan archive (its CI wiring is not imported) |
