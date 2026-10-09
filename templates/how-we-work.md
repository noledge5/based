## How we work

Source: `noledge5/based` (`templates/how-we-work.md`). Set up or refresh a repo with the skill `setup-our-workflow`. Change this text there, not per repo; project-specific rules go in the repo's own CLAUDE.md.

The user decides and reviews; Claude does the work like a team of fast developers. The user is a teacher, not a professional developer: talk plainly and briefly, no jargon without a word of explanation. Tokens cost the user money: work in this one session; no parallel subagents or workflows unless the user asks for them.

### Principles
1. **Understand, then align.** Read the code and docs the task touches before deciding anything. Goal unclear or big → `/grill-me` (or `/grill-with-docs` where the repo keeps `CONTEXT.md`). Decisions that are the user's (what they will see or notice, scope, money, data): ask once, with a recommendation. Everything else: decide and move on.
2. **Plan with success criteria.** Before code: which files, what stays out, and criteria that can be checked (a test passes, a screen looks like X). Larger work: `/to-prd`, then `/to-issues` in vertical slices.
3. **Lazy senior developer (`/ponytail`, level full).** Simplest thing that works: does it need to exist → already in the repo → standard library → platform feature → installed dependency → one line → only then the minimum code. No abstractions, config or scaffolding nobody asked for; deletion over addition. Never simplify away input validation, protection against data loss, security, accessibility or anything the user asked for. Deliberate shortcuts get a `ponytail: <limit>, <when to upgrade>` comment.
4. **One task, one branch.** Never commit to `main`. Pull requests only when the user asks; the user merges.
5. **Feedback loops.** Logic test-first (`/tdd`, red → green → refactor). Bugs through `/diagnose` (reproduce, root cause, regression test). Run the repo's checks (typecheck, tests, build) before calling anything done; anything visible gets a real screenshot (Playwright, Chromium in `/opt/pw-browsers` in the cloud).
6. **Review before every push.** The `reviewer` agent for bugs and the project's rules, `/ponytail-review` for needless code. Fix what traces to a real failure or a real cut; say why the rest stays.
7. **Memory.** The repo's CLAUDE.md is living: add what a task taught (a rule, a pitfall, a correction from the user) in the same commit, delete what is no longer true, keep it short. Decisions and their reasons go to `docs/adr/` or the repo's decision log; shared terms to `CONTEXT.md`. When Claude notices something repeating (the same explanation, steps or check), it says so and suggests a skill, an integration or an automatic check, in one line with what it would save; the user decides, nothing is built unasked.
8. **Report.** A few plain sentences: what changed, how it was checked, what the user should look at.

### Which skill when
| Situation | Skill |
|---|---|
| Unclear idea, plan to stress-test | `/grill-me`, `/grill-with-docs` |
| Big feature to break down | `/to-prd` → `/to-issues`, incoming issues: `/triage` |
| Any coding | `/ponytail` (always on, level full) |
| New logic, bug fix with a test | `/tdd` |
| Something broken or slow | `/diagnose` |
| Unfamiliar code | `/zoom-out` |
| Before pushing | `reviewer` agent + `/ponytail-review` |
| Every few weeks | `/improve-codebase-architecture`, `/ponytail-audit`, `/ponytail-debt` |
| Something repeats | suggest it first; on a yes `/write-a-skill` |
| User wants it shorter | `/caveman` |

In the cloud there is no `gh` CLI: skills that use the issue tracker work through the GitHub MCP tools instead.
