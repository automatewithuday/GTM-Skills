# Core Copywriting Framework

Hard rules live in `SKILL.md`; everything here serves them.

## Philosophy

- **Research IS the personalization** - Custom signals prove you did your homework
- **Shorter & punchier** - Target 50-90 words; only extend to 125 if AI personalization justifies it
- **Earn replies, not just meetings** - Confirm situation before selling
- **One job per email** - Single sharp question or CTA
- **About THEM, not you** - 3:1 ratio of them:us sentences minimum
- **Light humor is good** - Relatable, peer-like humor works (e.g., "equipment older than some employees")
- **"From my experience" framing** - When making claims about what "most" people experience, frame as personal observation

---

## AI Personalization Decision Framework

Before writing any campaign, ask: **"Can AI-generated company context add value, or is it noise?"**

### When AI Company Context Works

AI personalization works when **the prospect's business context changes how your product helps them**:

1. **Variable use cases** - Your product can be applied in different ways depending on what they do
   - Scrunch: "As you're trying to get {{ai_product_type}} in front of {{ai_customer_type}}, AI search visibility matters"
   - Marketing agency: "For {{ai_customer_type}}, we'd focus on {{ai_channel_recommendation}}"

2. **Mission/focus alignment** - Your product frees them up to focus on their actual work
   - "Stop worrying about [your product category] so you can focus on {{ai_company_mission}}"
   - "While you're busy helping {{ai_customer_type}} with {{ai_value_prop}}, we handle [your thing]"

3. **Broad targeting** - Reaching across industries/company types where context varies
   - Facilities manager at a hospital vs. a hotel vs. a school = different messaging

### When AI Company Context Doesn't Work

Skip AI personalization when **the use case is identical regardless of their business**:

1. **Commodity products with fixed use cases** - Vacuums clean floors the same way everywhere
2. **Narrow, homogeneous targeting** - Only reaching hotels? They all use vacuums the same way
3. **The personalization would feel forced** - "As you're vacuuming floors for hotel guests..." adds nothing

### The "So You Can Focus On" Pattern

When AI context works, use this pattern to connect your product to their mission:

```
{{first_name}}, [situation recognition about your product].

[Value prop about your product].

So you can focus on {{ai_company_mission}} instead of worrying about [your product category].

Worth exploring?
```

**Example (Scrunch for SaaS company):**
```
{{first_name}}, noticed {{company_name}}'s organic traffic is down.

AI referral traffic is growing 40% monthly. We track where you show up across every LLM.

So you can focus on getting {{ai_product_type}} in front of {{ai_customer_type}} instead of guessing where buyers are researching.

Worth a look?
```

**Example (IT services for any company):**
```
{{first_name}}, noticed {{company_name}} doesn't have a dedicated IT team.

We handle IT support so growing companies don't need to hire in-house.

So you can focus on {{ai_company_mission}} instead of troubleshooting tech issues.

Worth a conversation?
```

### AI Variables for Company Context

- `{{ai_company_mission}}`: What they exist to do (from About page, LinkedIn description)
- `{{ai_customer_type}}`: Who they sell to (from website)
- `{{ai_product_type}}`: What they sell (from website)
- `{{ai_value_prop}}`: How they describe their value (from website)

### Decision Checklist (Before Adding AI Company Context)

- [ ] Targeting is broad enough that company context varies
- [ ] Your product's value changes based on what they do
- [ ] The AI variable adds genuine relevance, not just filler
- [ ] Removing it would make the email feel generic

**If any of these fail, keep copy static** and lean on situation recognition (new hire, traffic decline, hiring signal, etc.) instead of company context.

---

## The "3 Offers" Framework

Every offer in the world is one of:
1. **Save time** (efficiency, automation, fewer steps)
2. **Make money** (increase revenue, more deals, growth)
3. **Save money** (reduce costs, better ROI, consolidation)

Rotate through these across follow-up emails. If Email 1 was "save time," Email 2 should be "make money" or "save money."

---

## Variable Schema

### Core Variables (always try to include)
- `{{first_name}}`, `{{company_name}}`, `{{role_title}}`
- `{{company_domain}}`, `{{industry}}`

### High-Signal Variables (when available)
- `{{tenure_years}}`, `{{recent_post_topic}}`, `{{recent_post_date}}`
- `{{competitor}}`, `{{category_competitors}}`
- `{{stack_crm}}`, `{{stack_marketing}}`, `{{stack_data}}`
- `{{hiring_roles}}`, `{{open_roles_count}}`

### AI-Generated Variables (dynamic)
- `{{ai_customer_description}}`: "fitness enthusiasts who want to breathe better"
- `{{ai_customer_type}}`: "VPs of Finance" or "professional men looking for classic styles"
- `{{ai_generation}}`: Flexible contextual generation based on website/LinkedIn
- `{{ai_use_case}}`: Specific way they could use the product
- `{{ai_pain_point}}`: Problem they likely experience

### Case Study Variables
- `{{case_study_company}}`, `{{case_study_result}}`, `{{case_study_metric}}`
- `{{case_study_customer_type}}`, `{{case_study_timeframe}}`

### Custom Signal Variables (campaign-specific)
- `{{g2_review_complaint}}`, `{{github_repo_found}}`, `{{pricing_page_insight}}`
- `{{chatgpt_ranking}}`, `{{bottom_funnel_keyword}}`, `{{negative_review}}`

**Formatting:** Always use `{{double_braces}}` in drafts.

---

## Email Structure

### Target Length
- **Primary target:** 50-90 words
- **Extended (with justification):** Up to 125 words
- Only extend when AI personalization or creative ideas add genuine value

### Structure Template

**Line 1: Situation Recognition (1 sentence)**
Describe THEIR exact situation. Be direct.
- ✅ "Saw you posted about {{ai_generation}}. Looks like it was {{days_ago}} days since the one before that."
- ✅ "Noticed you sell to {{ai_customer_type}}."
- ❌ "I hope this email finds you well!" (delete)

**Line 2: Value Prop + Proof (1-2 sentences MAX)**
What you do + metric. No fluff.
- ✅ "We helped companies like Lemlist double down on social with our scheduling tool."
- ✅ "We've attributed a 4.7x increase in upgrades after adding product videos."
- ❌ "We help companies scale their marketing efforts through innovative solutions..."

**Optional: The "Specifically" Line (1 sentence)**
Use when your service applies universally but their customers vary:
> "Specifically, it looks like you're trying to sell to {{ai_customer_type}}, and we can help with that."

**Line 3: Low-Effort CTA (1 sentence)**
Binary question or simple offer.
- ✅ "Worth a look?"
- ✅ "Could I send you access?"
- ✅ "Is this still the case?"
- ❌ "Would you be open to scheduling 15 minutes next Tuesday at 2pm?"

**Optional: PS Line**
For AI specificity or additional hook when body is kept short.

---

## Subject Line Strategy

### Approach A: 2-4 Words (Intrigue)
Best when using custom research signals.
- "question for {{first_name}}" (lowercase q)
- "{{company_name}} equipment"
- "Saw your post"
- "Competitor insights"

**Banned subject lines:**
- ❌ "Curious" - too generic
- ❌ "Quick question" - overused

**Test:** Can a colleague or potential customer send this? If yes, good.

### Approach B: Whole Offer in Subject + Preview
Best when data is limited or offer is self-selecting.
- Subject: "Ever chase renters to pay on time?"
- Preview: "We built a platform that rewards renters for paying on time..."

### Approach C: Problem Indicator
Best for problem sniffing campaigns.
- "Looked you up on ChatGPT"
- "Review from Karen"
- "Starter vs. Professional"

---

## Opener Patterns ("Poke the Bear")

### Classic
- Do you already have a reliable way to {{problem}}?
- How are you currently handling {{process}}?

### Status Pressure / FOMO
- Have you solved {{problem}} yet or is it still manual?
- Have you figured out how to do {{outcome}} without adding headcount?

### Soft Humility
- I may be wrong, but do you have something in place for {{area}}?
- Totally possible you solved this. How do you handle {{process}} today?

### Efficiency / Leverage
- How are you doing {{task}} without adding headcount?
- What's your process for {{task}} without manual work?

### Binary
- Is your process for {{area}} where you want it?
- Will your current setup scale 12 more months?

### Redirect (Fallback)
- Let me know if {{employee_1}} or {{employee_2}} would be better to speak about {{problem}}

---

## CTA Patterns

### Category 1: Confirmation (Earn Reply)
- "Is this still the case?"
- "Are you already doing X?"
- "Worth exploring?"
- "Just confirm [example] is accurate"

### Category 2: Value-Exchange (Why Meet)
- "...so I can understand the situation and plead your case to Google"
- "...to walk you through 3 custom ideas specific to {{company_name}}"
- "...so I can show you the engagers of your competitor's last 10 posts"

### Category 3: Resource Offer (Low Commitment)
- "Could I send you access to try it out?"
- "Would it be useful if I sent those over?"
- "Want to see a video of how this works?"

**The Test:** Can they reply in 5 words or less? If no, simplify.

---

## Creative Ideas Campaign

When suggesting specific ideas for their business, use the **constraint box** approach.

### The Critical Constraint
Define 3-5 specific features/capabilities you ACTUALLY offer. Only suggest ideas using those features.

**Bad (Unconstrained):**
```
• Build a referral program with gamification
• Create a podcast series
• Launch a TikTok influencer campaign

Problem: You don't do these things.
```

**Good (Constrained):**
```
Input: Our capabilities are:
1. SEO content writing
2. Paid social ads (Meta/LinkedIn)
3. Email nurture sequences

Output:
• SEO content series around [keyword cluster] based on competitor gaps
• Paid social campaign targeting [audience] using [platform feature]
• Email nurture for [segment] addressing [pain]

Result: All credible, all deliverable.
```

### Creative Ideas Format
```
{{first_name}}, I was back on your site today and had some [marketing/creative] ideas for you.

• [Action] using [Feature 1] targeting [specific thing], would help with [benefit]
• [Action] using [Feature 2] targeting [specific thing], would help with [benefit]
• [Action] using [Feature 3] targeting [specific thing], would help with [benefit]

Of course, I wrote this without knowing your current bottlenecks and goals.

If it's interesting, happy to share what's working in {{industry}}.
```

---
