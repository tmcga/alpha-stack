# Startup Fundraise Deck

Prompt library for building investor pitch decks for venture-backed startups.

## Role Context

```
You are a startup advisor who has seen thousands of pitch decks and knows what
separates the ones that get term sheets from the ones that get polite passes.
The best decks tell a story that makes the investment feel inevitable — the market
is massive, the team is uniquely positioned, the timing is now, and the traction
proves the thesis. Every slide must earn its place.
```

---

## 1. Series A/B Investor Deck

```
Build a [15-20] slide investor deck for [company name] raising [Series A/B].

Company info:
- What we do: [one sentence]
- Revenue/ARR: $[X]M, growing [X]% [MoM/YoY]
- Customers: [N] ([notable logos if any])
- Team: [X] employees, [founder backgrounds in 1 line each]
- Raising: $[X]M at $[X]M pre-money
- Prior funding: $[X]M raised from [investors]

Slide structure:
1. **Title slide**: Company name, one-line tagline, round info
2. **The problem**: What pain exists? Who has it? How big is the pain?
3. **The solution**: What you built. Show, don't tell — screenshot or demo flow
4. **Why now**: Market shift, technology unlock, or regulatory change enabling this
5. **Market size**: TAM → SAM → SOM with credible methodology (not top-down hand-waving)
6. **Business model**: How you make money. Unit economics.
7. **Traction**: The hockey stick. Revenue chart, customer growth, engagement metrics
8. **Product**: Feature differentiation. What you have that competitors don't
9. **Competition**: Honest competitive landscape — 2x2 matrix or feature comparison
10. **Go-to-market**: How you acquire customers. CAC, channels, sales motion
11. **Team**: Founders + key hires. Why THIS team for THIS problem?
12. **Financials**: 3-year projection with key assumptions visible
    - Run tool: `python3 tools/vc_returns.py` for fund return modeling
13. **The ask**: Amount raising, use of funds, milestones this capital unlocks
14. **Appendix**: Detailed financials, customer references, technical architecture

For each slide: headline (the takeaway, not the topic), 3-5 supporting points, one visual suggestion.
```

## 2. Pre-Seed / Seed Deck

```
Build a [10-12] slide deck for a [pre-seed/seed] raise for [company name].

At this stage, the deck is about **vision, team, and early signal** — not metrics.

Company info:
- What we're building: [one sentence]
- Stage: [idea / prototype / beta / early revenue]
- Traction signal: [waitlist, LOIs, pilot customers, usage data]
- Team: [founder backgrounds — emphasize domain expertise and unfair advantage]
- Raising: $[X]M

Slide structure:
1. **Title**: Name + tagline
2. **Personal story**: Why do YOU care about this problem? (authenticity > polish)
3. **The problem**: Vivid, specific, felt by a real person
4. **The insight**: What do you know that others don't?
5. **The solution**: What you're building (keep it simple)
6. **Early signal**: Any traction, LOIs, waitlist, or design partners
7. **Market**: Big enough to matter. One slide, credible sources
8. **Business model**: Simple explanation of how you'll make money
9. **Team**: Why you'll win. Domain expertise, relevant experience, hustle evidence
10. **The ask**: Round size, use of funds, 12-18 month milestones
```

---

See also: `/vc`, `/investment-memo`, `/fpa`
