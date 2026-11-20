---
name: fork-maintainer
description: Fork-only workflow rules for the greedychipmunk fork — branch and PR flow against fork main, the no-upstream-PR policy, PR template disclosure and attestation ownership, commit trailers, and AGENTS.md parity with upstream PR #1620. Use when opening or merging a pull request, choosing a branch base, syncing with upstream, or filling in the PR template.
---

# Fork maintainer

Fork-only supplement for the **greedychipmunk** fork (`greedychipmunk/mediacms`). The structure
and pattern are adapted from the imported `skills/maintainer` (credit: Josh Preston, @mrjoshuap);
the rules below are this fork's own. `AGENTS.md` stays authoritative — on a conflict between this
skill and `AGENTS.md`, stop, leave the authoritative file unchanged, and ask Dawson
(@dcblackhouse).

## Remotes and branches

- `origin` = upstream `mediacms-io/mediacms`; `fork` = `greedychipmunk/mediacms`.
- Local `main` tracks `fork/main`. Fork work branches off **fork `main`** and lands on **fork `main`**.
- Branch names carry a Conventional Commit type prefix: `feat/...`, `fix/...`, `docs/...`, `chore/...`.

## Fork flow

1. Branch off fork `main`.
2. Commit with Conventional Commit messages (types from `AGENTS.md`).
3. Open a pull request **against fork `main`** with a Conventional Commit title (CI enforces
   `semantic-pull-request`).
4. Once complete, merge it (Dawson's standing rule: fork PRs merge automatically), delete the
   branch, and sync local `main` (`git pull fork main`).

## Upstream policy

**Never open a pull request or post a comment on `mediacms-io/mediacms` unless Dawson explicitly
requests it.** Draft the text on the fork and let Dawson decide. Exceptions to date (explicit
requests): upstream #1620 (AGENTS.md — approved, minor fixes addressed) and #1640 (AI disclosure
templates — merged). When upstream work IS requested:

- Branch from upstream `main` (`origin/main`), not from fork `main`, and keep the change set as
  small as the task allows.
- Content that also exists on the fork (templates, AGENTS.md) is cherry-picked, not retyped, so
  the two stay byte-identical where they overlap.
- Reply to review feedback in-thread, verify every factual claim against the code before fixing,
  and mirror any AGENTS.md fixes back to fork `main` through a fork PR.

## PR template ownership

The PR template's **AI assistance disclosure** and **Attestation** checkboxes are Dawson's
statements. Agents never tick them:

- Leave every checkbox under disclosure and attestation unticked; Dawson ticks them.
- Fill the `Tool(s) and what they did` line honestly with what the agent actually did.
- End agent-produced GitHub artifacts (PR descriptions, comments, replies) with an AI disclosure
  line. On upstream use: `AI disclosure: drafted with an AI agent (Letta Code) and reviewed by
  @dcblackhouse.` — claim "reviewed by" only when Dawson actually reviewed that draft.

## Commits and authorship

- Conventional Commits from `AGENTS.md`; do not bump `package.json` or hand-edit `CHANGELOG.md`.
- Agent commits carry the Letta Code trailers (`Generated with Letta Code` +
  `Co-Authored-By: Letta Code <noreply@letta.com>`); author and committer stay Dawson's
  configured git identity.
- Imported work keeps the original authors credited: verbatim files, source provenance in the
  commit message, and a `Co-Authored-By` trailer for the original author (see the skills
  import, fork PR #5).
- `cms/local_settings.py` is gitignored — never commit it. `deploy/docker/local_settings.py` is a
  tracked upstream file — do not commit deployment-specific local modifications or secrets to it.
- Never force-push a shared branch; an agent may force-push (with lease) only its own pull
  request branch.

## AGENTS.md parity with upstream PR #1620

Fork `main`'s `AGENTS.md` mirrors the upstream PR #1620 content plus fork-only sections
("Agent skills"). Keep it that way:

- Review fixes for the PR branch are mirrored to fork `main` through a fork PR (see fork PRs #3, #4).
- Fork-only additions (the skills index) live on fork `main` only; the PR branch stays free of
  fork-only content.

## Skills precedence

- Domain skills (see `skills/README.md`) apply to MediaCMS work on this fork — consult the
  matching skill before working in its area.
- The imported fork-governance skills (`maintainer`, `merge-hygiene`, `fork-docs-release`,
  `plan-history`) document the **mrjoshuap-hq** fork's process. They are reference-only; their
  branch-target and label rules do not apply here.
- This skill governs this fork's workflow. `AGENTS.md` outranks it.

## Ask Dawson

Stop and ask before:

- Opening a pull request or posting a comment on `mediacms-io/mediacms` (or drafting one for him
  to post).
- Ticking any AI disclosure or attestation checkbox.
- Any non-trivial implementation — Dawson prefers a plan for review first; proceed directly only
  for work he has explicitly approved.
- Deleting or force-pushing anything outside the agent's own pull request branch.
- A conflict between this skill and `AGENTS.md` or a domain skill.

## Additional resources

- `AGENTS.md` (hard rules; authoritative)
- `skills/README.md` (attribution and index)
- `.github/pull_request_template.md` (disclosure + attestation; Dawson ticks the boxes)
- Upstream PR #1620 (AGENTS.md proposal), upstream PR #1640 (templates, merged)
