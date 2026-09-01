# GTM Skills

Practical go-to-market playbooks — ABM measurement, outbound, paid media, attribution, sales process — packaged as **agent skills** you can install into Claude Code, Codex, Cursor, and 70+ other coding/AI agents with one command.

Each skill is a `SKILL.md` that follows the open [Agent Skills spec](https://agentskills.io): the agent reads the description to know *when* to use it, then loads the full playbook — formulas, benchmarks, worked examples, and a short "how to apply" workflow — only when the task calls for it.

Written from operator experience running GTM systems at [martechs.io](https://martechs.io). Numbers and benchmarks are kept as originally documented; treat them as a starting point, not gospel.

## Install

```bash
# Pick skills interactively, for whichever agents you have installed
npx skills add automatewithuday/GTM-Skills

# One skill, one agent, no prompts
npx skills add automatewithuday/GTM-Skills --skill abm-measurement -a claude-code -y

# Everything, globally (available in every project)
npx skills add automatewithuday/GTM-Skills --skill '*' -g -y

# List what's available without installing
npx skills add automatewithuday/GTM-Skills --list
```

**Claude Code** — also installable as a plugin:

```bash
claude plugin marketplace add automatewithuday/GTM-Skills
claude plugin install gtm-skills@gtm-skills
```

Skills trigger automatically when your request matches their description, or invoke one directly with `/abm-measurement`.

**Codex** — reads skills from `.agents/skills/` (project) or `~/.agents/skills/` (global), which `npx skills add … -a codex` writes to. Invoke with `$abm-measurement` or let Codex pick it up from context.

**Manual** — copy any `skills/<name>/` folder into your agent's skills directory (`.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, …).

## Catalog

### ABM

| Skill | Use when |
|---|---|
| [`abm-measurement`](skills/abm-measurement/SKILL.md) | Measuring, reporting on, or auditing an ABM program — stage metrics, attribution models, ROI/CAC/velocity formulas, benchmarks, and a measurement-maturity check. |
| [`abm-retargeting`](skills/abm-retargeting/SKILL.md) | Planning or fixing retargeting for ABM accounts — engagement tiers, frequency caps and creative rotation, a day-by-day multi-channel play, LinkedIn/Meta/Google audience setup, and the HubSpot → LinkedIn sync loop. |
| [`abm-target-accounts`](skills/abm-target-accounts/SKILL.md) | Building or sizing a target account list — how many accounts a revenue target needs, lookalikes and ICP scoring (Clay, BuiltWith, Apollo), A–D tiers, HubSpot stage lists and automation, LinkedIn sync, and what a 90-day vs mature program looks like. |

### Outbound & Prospecting

| Skill | Use when |
|---|---|
| [`closed-won-replication-play`](skills/closed-won-replication-play/SKILL.md) | A deal just closed won — find lookalike companies not yet in the CRM, draft outreach from the deal owner with an anonymized win reference, and queue one batch review task. Nothing sends without approval. |
| [`campaign-strategy`](skills/campaign-strategy/SKILL.md) | Planning cold outbound for a client — deep website/case-study research, 15–20+ campaign ideas from broad to niche with list filters, AI-personalization strategy, and value prop; sourcing vs enriching; required campaign types; front-end offers. |
| [`campaign-copywriting`](skills/campaign-copywriting/SKILL.md) | Writing cold email campaigns — a 4-step confirm-then-write flow, hard rules, subject/first-line strategies, AI-personalization decision framework, follow-up templates, QA checklist and 0–100 scoring rubric. |

### Signals

| Skill | Use when |
|---|---|
| [`champion-move-detection`](skills/champion-move-detection/SKILL.md) | Running a monthly sweep for customer champions and heavy users who changed jobs — live-LinkedIn verification with wrong-person and stale-headline guards, one MQL per move, churn flags on the account they left. Never sends. |

*More skills are being added — paid media, attribution & analytics, sales process, messaging.*

## Using a skill well

Skills are reference-plus-workflow, not scripts. When one activates, the agent will:

1. Ask for the inputs it needs (spend, account counts, pipeline, etc.).
2. Apply the formulas and frameworks exactly as written.
3. Report results against the benchmarks and give a recommendation.

Give it real numbers and it gives you a real answer.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Short version: copy `template/SKILL.template.md` to `skills/<name>/SKILL.md`, fill it in, run `bash scripts/validate.sh`, add a catalog row, open a PR.

## License

[MIT](LICENSE) © 2026 Uday Kang / martechs.io
