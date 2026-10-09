# noledge5/skills

Our base repository: Matt Pocock's skills (fork) plus our own way of working. Other repositories pull from here with the skill `setup-our-workflow`.

- `templates/how-we-work.md`: how we work together. The single source; it is copied into every repo's CLAUDE.md. Change it here.
- `templates/agents/reviewer.md`, `templates/hooks/`: the reviewer agent and the check hooks every repo gets (hooks adapted to its commands).
- `skills/engineering/ponytail*`: from DietrichGebert/ponytail (MIT, licence in `skills/engineering/ponytail/LICENSE`), copied in because the plugin does not load in cloud sessions. Update by copying the newer `SKILL.md` files.

@templates/how-we-work.md

## Maintaining this repo

Skills are organized into bucket folders under `skills/`:

- `engineering/` — daily code work
- `productivity/` — daily non-code workflow tools
- `misc/` — kept around but rarely used
- `personal/` — tied to my own setup, not promoted
- `deprecated/` — no longer used

Every skill in `engineering/`, `productivity/`, or `misc/` must have a reference in the top-level `README.md` and an entry in `.claude-plugin/plugin.json`. Skills in `personal/` and `deprecated/` must not appear in either.

Each skill entry in the top-level `README.md` must link the skill name to its `SKILL.md`.

Each bucket folder has a `README.md` that lists every skill in the bucket with a one-line description, with the skill name linked to its `SKILL.md`.

## Agent skills

### Issue tracker

Issues are tracked in this repo's GitHub Issues via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary — each canonical role uses its own name (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — one `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
