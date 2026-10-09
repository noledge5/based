# noledge5/based

Our base repository: how we work together, and the skills that go with it. Other repositories pull from here with the skill `setup-our-workflow`.

- `templates/how-we-work.md`: how we work together. The single source; it is copied into every repo's CLAUDE.md. Change it here.
- `templates/agents/reviewer.md`, `templates/hooks/`: the reviewer agent and the check hooks every repo gets (hooks adapted to its commands).
- `skills/<name>/`: every skill in one flat folder, linked into `.claude/skills/` so sessions here can use them. A new skill needs that link, a line in `README.md` and, if every repo should get it, an entry in the list in `skills/setup-our-workflow/SKILL.md`.
- Sources (both MIT): `ponytail*` from DietrichGebert/ponytail (licence in `skills/ponytail/LICENSE`; update by copying newer `SKILL.md` files); the other skills from Matt Pocock's mattpocock/skills (licence in `LICENSE`).

@templates/how-we-work.md
