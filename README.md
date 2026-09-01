# GTM Skills

Practical go-to-market playbooks — ABM, outbound, cold email operations, list building, deliverability, signals — packaged as **agent skills** you can install into Claude Code, Codex, Cursor, and 70+ other AI agents with one command.

Each skill is a `SKILL.md` that follows the open [Agent Skills spec](https://agentskills.io): the agent reads the description to know *when* to use it, then loads the full playbook — formulas, benchmarks, worked examples, scripts, and a short "how to apply" workflow — only when the task calls for it.

Written and curated from operator experience running GTM systems at [martechs.io](https://martechs.io). Numbers and benchmarks are kept as documented; treat them as a starting point, not gospel.

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

### Signals

| Skill | Use when |
|---|---|
| [`champion-move-detection`](skills/champion-move-detection/SKILL.md) | Running a monthly sweep for customer champions and heavy users who changed jobs — live-LinkedIn verification with wrong-person and stale-headline guards, one MQL per move, churn flags on the account they left. Never sends. |
| [`closed-won-replication-play`](skills/closed-won-replication-play/SKILL.md) | A deal just closed won — find lookalike companies not yet in the CRM, draft outreach from the deal owner with an anonymized win reference, and queue one batch review task. Nothing sends without approval. |

### Cold email operations

The full cold outbound stack, in the order you'd run it. New to cold email? Start with [`cold-email-kickoff`](skills/cold-email-kickoff/SKILL.md).

#### Track 1 — Strategy (before you send anything)

| Skill | What it does |
|---|---|
| [`cold-email-kickoff`](skills/cold-email-kickoff/SKILL.md) | single "start here" orchestrator (recommended entry point) |
| [`icp-onboarding`](skills/icp-onboarding/SKILL.md) | conversational intake that produces a `client-profile.yaml` (scrapes website first) |
| [`lead-magnet-brainstorm`](skills/lead-magnet-brainstorm/SKILL.md) | figure out what to offer for free in your cold emails |
| [`campaign-strategy`](skills/campaign-strategy/SKILL.md) | generates 15–25 campaign ideas with AI strategies + value props |
| [`campaign-copywriting`](skills/campaign-copywriting/SKILL.md) | stepwise copy writer (direction → subject → body → final YAML) |

#### Track 2 — Infrastructure

| Skill | What it does |
|---|---|
| [`zapmail-domain-setup-public`](skills/zapmail-domain-setup-public/SKILL.md) | buy `.com`/`.co` domains on Dynadot, provision inboxes on Zapmail |
| [`smartlead-inbox-manager`](skills/smartlead-inbox-manager/SKILL.md) | warmup settings, signatures, active/insurance tagging |
| [`email-deliverability-audit`](skills/email-deliverability-audit/SKILL.md) | diagnostic tool (SPF/DKIM/DMARC, spam placement, 1% rule) |
| [`deliverability-incident-response`](skills/deliverability-incident-response/SKILL.md) | triage playbook for spam, bounces, blacklists, warmup blocks |

#### Track 3 — List building

| Skill | What it does |
|---|---|
| [`list-builder`](skills/list-builder/SKILL.md) | the meta skill for any list request: sweep every source, AI-qualify, snowball, then pull uncapped contacts |
| [`list-expander`](skills/list-expander/SKILL.md) | turn ~10 known-good seed companies into a full qualified TAM |
| [`prospeo-full-export`](skills/prospeo-full-export/SKILL.md) | title-first lead search export (paginated, 25K+) |
| [`prospeo-search-api`](skills/prospeo-search-api/SKILL.md) | Prospeo filter and API reference |
| [`blitz-list-builder`](skills/blitz-list-builder/SKILL.md) | domain-first contact discovery |
| [`google-maps-list-builder`](skills/google-maps-list-builder/SKILL.md) | scrape Google Maps for local SMB lists |
| [`disco-like`](skills/disco-like/SKILL.md) | lookalike company discovery (seed domains or ICP text) |
| [`competitor-engagers`](skills/competitor-engagers/SKILL.md) | find people engaging with competitor LinkedIn posts |
| [`icp-prompt-builder`](skills/icp-prompt-builder/SKILL.md) | required qualification step after every list-building skill |
| [`list-quality-scorecard`](skills/list-quality-scorecard/SKILL.md) | grade a lead CSV across 8 dimensions before uploading |

#### Track 4 — Copy & send

| Skill | What it does |
|---|---|
| [`cold-email-starter-kit`](skills/cold-email-starter-kit/SKILL.md) | the 14-step end-to-end tutorial (alternative to kickoff) |
| [`spam-word-checker`](skills/spam-word-checker/SKILL.md) | scan copy for deliverability-killing phrases |
| [`smartlead-spintax`](skills/smartlead-spintax/SKILL.md) | add spintax variations to emails |
| [`smartlead-api`](skills/smartlead-api/SKILL.md) | Smartlead API reference |
| [`smartlead-campaign-upload-public`](skills/smartlead-campaign-upload-public/SKILL.md) | DRAFT-upload leads.csv + variants.yaml to Smartlead (you hit Start manually) |

#### Track 5 — Iterate & automate

| Skill | What it does |
|---|---|
| [`positive-reply-scoring`](skills/positive-reply-scoring/SKILL.md) | the metric that matters (positive replies / total sent) |
| [`experiment-design`](skills/experiment-design/SKILL.md) | single-variable experiment framework |
| [`auto-research-public`](skills/auto-research-public/SKILL.md) | autonomous campaign launcher (scrape → ICP → leads → personalize → upload) |
| [`personalization-subagent-pattern`](skills/personalization-subagent-pattern/SKILL.md) | reusable pattern for per-lead Claude sub-agent personalization |
| [`deliverability-test-public`](skills/deliverability-test-public/SKILL.md) | compare reply/bounce by inbox type |
| [`cold-email-weekly-rhythm`](skills/cold-email-weekly-rhythm/SKILL.md) | Monday/Wednesday/Friday operational playbook |

#### Track 6 — Signal playbooks

One playbook produces one copy-ready field for every row of a list. Each ships three ways: as a skill run from your agent, as a Clay **table** (`clay-table.md`, browser-built), and as a Clay **workflow** (`clay-workflow.md`, built with the `clay` CLI). The table/workflow files are written against the real Clay action catalog but have not been run in a live workspace — build one, run 5 rows, fix the file.

| Playbook | Output | What it says |
|---|---|---|
| [`clay-playbooks`](skills/clay-playbooks/SKILL.md) | index + build harnesses | start here: conventions, credit gates, table and CLI harnesses |
| [`playbook-new-in-role`](skills/playbook-new-in-role/SKILL.md) | `new_in_role_line` | they just took this seat |
| [`playbook-linkedin-engagement`](skills/playbook-linkedin-engagement/SKILL.md) | engager rows | they engage with a competitor's or customer's posts |
| [`playbook-social-posts`](skills/playbook-social-posts/SKILL.md) | `social_post_text` | they posted something you can speak to |
| [`playbook-warm-intros`](skills/playbook-warm-intros/SKILL.md) | `warm_intro_line` | they are already one hop from you |
| [`playbook-fundraising`](skills/playbook-fundraising/SKILL.md) | `funding_line` | they raised, so they are buying |
| [`playbook-hiring-surge`](skills/playbook-hiring-surge/SKILL.md) | `hiring_surge_line` | they are growing the team you sell to |
| [`playbook-job-posting-language`](skills/playbook-job-posting-language/SKILL.md) | `job_posting_line_safe` | their own job post names your problem |
| [`playbook-ad-library`](skills/playbook-ad-library/SKILL.md) | `ad_library_line` | they are spending on paid social right now |
| [`playbook-pricing-page`](skills/playbook-pricing-page/SKILL.md) | pricing record | how they price, read off their own page |
| [`playbook-case-study-page`](skills/playbook-case-study-page/SKILL.md) | `case_study_line` | who they brag about serving |
| [`playbook-tech-on-website`](skills/playbook-tech-on-website/SKILL.md) | `tech_confirmed` | what they run, verified against the live site |
| [`playbook-google-site-search`](skills/playbook-google-site-search/SKILL.md) | `site_keyword_line` | does their site mention X |
| [`playbook-company-name-cleaning`](skills/playbook-company-name-cleaning/SKILL.md) | `company_clean` | "Irby Utilities, LLC" becomes "Irby" |
| [`playbook-first-name-cleaning`](skills/playbook-first-name-cleaning/SKILL.md) | `first_name_clean` | "Dr Ruba" becomes "Ruba" |
| [`playbook-social-link-finding`](skills/playbook-social-link-finding/SKILL.md) | profile URLs | domain to verified social profiles |
| [`playbook-lookalikes`](skills/playbook-lookalikes/SKILL.md) | company list | more companies like your best customer |
| [`playbook-name-to-other-prospects`](skills/playbook-name-to-other-prospects/SKILL.md) | `other_prospects` | "is this you or Jeff?" |
| [`playbook-ai-specificity`](skills/playbook-ai-specificity/SKILL.md) | `specificity_line` | make a generic offer feel written for them |
| [`playbook-creative-ideas`](skills/playbook-creative-ideas/SKILL.md) | 3 bullets | the "I had a few ideas" email |

## Running the scripts

Many cold-email skills ship TypeScript scripts under `scripts/`. They run with `tsx` and read API keys from a `.env` file:

```bash
npm install -g tsx
cp .env.example .env        # fill in only the keys for the skills you use
npx tsx skills/<skill>/scripts/<script>.ts --help
```

`list-builder` imports shared helpers from `list-expander/scripts/lib.ts`, so install both. The minimum viable key set for a first campaign is **Dynadot + Zapmail + Prospeo + Smartlead**; every key and which skills need it is documented in [`.env.example`](.env.example).

## Using a skill well

Skills are reference-plus-workflow. When one activates, the agent will:

1. Ask for the inputs it needs (spend, account counts, a domain, a CSV…).
2. Apply the formulas, rules, and scripts exactly as written.
3. Report results against the benchmarks and give a recommendation — or hand you a DRAFT to approve.

Give it real inputs and it gives you a real answer. Nothing in this library sends email or creates outreach without a human approving it.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Short version: copy `template/SKILL.template.md` to `skills/<name>/SKILL.md`, fill it in, run `bash scripts/validate.sh`, add a catalog row, open a PR.

## License

[MIT](LICENSE) © 2026 Uday Kang / martechs.io. Third-party notices: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
