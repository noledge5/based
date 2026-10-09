---
name: setup-our-workflow
description: Set up or refresh our way of working in the current repository from noledge5/based - the "How we work" section in CLAUDE.md, the skills, the reviewer agent and the check hooks. Use when the user says "set up our workflow", "bring in our skills", "refresh our workflow", or starts work in a repository that has no "How we work" section yet.
---

# Set up our workflow in a repository

The source is the repository `noledge5/based`. Everything is copied into the target repository, so it works there without this repo.

## 1. Get the source
- If `noledge5/based` is not in the session: attach it (`add_repo`, owner `noledge5`, repo `based`, access `read`) and clone it, e.g. to `/home/user/based`. If a clone exists, `git -C <clone> pull` on `main`.
- Work on the target repo's task branch (never `main`).

## 2. CLAUDE.md
- No CLAUDE.md yet: write one first, short: what the project is, structure, commands (install, dev, check, test, build), project rules. Look at the code; ask the user only what the code cannot tell.
- Put the content of `templates/how-we-work.md` between the markers `<!-- how-we-work:start -->` and `<!-- how-we-work:end -->` at the end of CLAUDE.md. On a refresh, replace only what is between the markers; everything else in CLAUDE.md belongs to the project and stays.

## 3. Skills
Copy these folders from `skills/<name>/` into the target's `.claude/skills/<name>/` (real copies, no symlinks; overwrite on refresh):

`ponytail`, `ponytail-review`, `ponytail-audit`, `ponytail-debt`, `grill-me`, `grill-with-docs`, `tdd`, `diagnose`, `zoom-out`, `to-prd`, `to-issues`, `triage`, `improve-codebase-architecture`, `write-a-skill`, `caveman`, `setup-matt-pocock-skills`, `setup-our-workflow`.

Skills the repo has of its own (other names) stay untouched. `to-prd`, `to-issues` and `triage` need the issue-tracker config: run `setup-matt-pocock-skills` the first time the repo uses them, not before.

## 4. Reviewer agent
Copy `templates/agents/reviewer.md` to `.claude/agents/reviewer.md`. If the repo already has a reviewer with project-specific checks, keep it and only add what is missing from the template.

## 5. Hooks
- Copy `templates/hooks/*.sh` to `.claude/hooks/` and adapt them to the repo: the install line, `CHECK` (the fast check, a few seconds at most, with the file pattern it applies to) and `TESTS`. Drop a hook the repo has no command for. Time the commands.
- Merge the `hooks` from `templates/hooks/settings.json` into `.claude/settings.json`, keeping every existing key.
- Test each script by hand with sample input: a clean file passes, a deliberate error is caught with exit 2 (then remove it), the stop hook stays quiet with `stop_hook_active: true`.

## 6. Finish
- Commit and push the task branch. Writing `.claude/` may be blocked in Auto mode: then ask the user to switch the mode to "Accept edits" and approve.
- Tell the user in two or three plain sentences what is now set up, and that new sessions get it once the branch is merged into `main`.
