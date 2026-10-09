# based

How we work with Claude, and the skills that go with it.

**Start a new repository:** tell the session *"Set up our workflow from noledge5/based."* It copies the rules into that repo's `CLAUDE.md`, plus the skills, the reviewer agent and the automatic checks. *"Refresh our workflow"* brings in later changes.

- [`templates/how-we-work.md`](templates/how-we-work.md): the rules
- [`templates/agents/reviewer.md`](templates/agents/reviewer.md), [`templates/hooks/`](templates/hooks/): reviewer and checks

## Skills

- **[setup-our-workflow](skills/setup-our-workflow/SKILL.md)**: bring all of this into a repository, or refresh it.
- **[ponytail](skills/ponytail/SKILL.md)**: the simplest solution that works. Also [ponytail-review](skills/ponytail-review/SKILL.md) (needless code in a diff), [ponytail-audit](skills/ponytail-audit/SKILL.md) (whole repo), [ponytail-debt](skills/ponytail-debt/SKILL.md) (list of deliberate shortcuts).
- **[grill-me](skills/grill-me/SKILL.md)**, **[grill-with-docs](skills/grill-with-docs/SKILL.md)**: questions until the plan is clear.
- **[to-prd](skills/to-prd/SKILL.md)**, **[to-issues](skills/to-issues/SKILL.md)**, **[triage](skills/triage/SKILL.md)**: big work into issues; they need **[setup-matt-pocock-skills](skills/setup-matt-pocock-skills/SKILL.md)** once per repo.
- **[tdd](skills/tdd/SKILL.md)**: test first. **[diagnose](skills/diagnose/SKILL.md)**: find the root cause of a bug.
- **[zoom-out](skills/zoom-out/SKILL.md)**: explain unfamiliar code. **[improve-codebase-architecture](skills/improve-codebase-architecture/SKILL.md)**: tidy the structure now and then.
- **[write-a-skill](skills/write-a-skill/SKILL.md)**: make a new skill. **[caveman](skills/caveman/SKILL.md)**: very short answers.

## Credits

Started as a fork of [mattpocock/skills](https://github.com/mattpocock/skills) (MIT, see `LICENSE`). Ponytail skills from [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) (MIT, see `skills/ponytail/LICENSE`).
