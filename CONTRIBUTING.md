# Contributing

Skills here follow the open [Agent Skills spec](https://agentskills.io/specification), so one `SKILL.md` works unchanged in Claude Code, Codex, Cursor, and every other agent the [`skills` CLI](https://github.com/vercel-labs/skills) supports.

## Add a skill

1. Copy the template (it's named `.template.md` on purpose so installers don't treat it as a skill):
   ```bash
   mkdir -p skills/<skill-name>
   cp template/SKILL.template.md skills/<skill-name>/SKILL.md
   ```
2. Edit `skills/<skill-name>/SKILL.md`:
   - `name` must equal the directory name: lowercase letters, numbers, single hyphens, ≤64 chars.
   - `description` is a single line starting with **"Use when …"**. Describe the *situations and keywords* that should trigger the skill — not what it contains. Agents read this to decide whether to load the skill; if it summarizes the content, they'll act on the summary and never read the body.
   - Keep `SKILL.md` under 500 lines. Put heavy reference material in `references/` and link to it.
   - Keep the **How to apply this skill** section: inputs to gather → what to compute/assess → what to report. That's what turns a doc into a skill.
3. Validate:
   ```bash
   bash scripts/validate.sh
   npx skills add . --list      # your skill should be listed
   ```
4. Add a row to the catalog table in `README.md`.
5. Open a PR with the title `feat(skills): add <skill-name>`.

## House rules

- Numbers, benchmarks, and formulas are the point. State the source or the year if you know it; don't round or "improve" someone else's stat.
- One skill, one job. If a doc covers two playbooks, split it.
- Plain fenced code blocks (no language tag) for formulas — they're not code.
- No vendor pitches. Naming a tool that's part of a real workflow is fine.
