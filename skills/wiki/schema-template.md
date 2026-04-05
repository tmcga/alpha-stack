# Alpha Stack Wiki Schema

This file defines how your personal finance knowledge base is structured. The LLM reads this to maintain consistency across all wiki operations. You and the LLM co-evolve this over time.

---

## Page Types

### Entities (`entities/`)

One page per company, sector, person, or fund you analyze.

- **Filename:** `{ticker}.md` for public companies, `{name-slug}.md` for everything else
- **Required sections:** Overview, Key Metrics, Prior Analyses, Observations, Related
- **Update policy:** Merge new information — never overwrite prior observations. Append with date stamps so the evolution of your understanding is visible.

### Playbooks (`playbooks/`)

Your preferred methodologies, assumptions, and frameworks.

- **Filename:** `{domain}-{topic}.md` (e.g., `dcf-assumptions.md`, `lbo-defaults.md`, `sector-tech.md`)
- **Purpose:** Capture YOUR preferences — "I typically use 10% WACC for mid-cap tech" or "For SaaS companies I weight revenue multiples 60%, DCF 40%"
- **Update policy:** Evolve over time as your methodology matures. Note when and why preferences changed.

### Journal (`journal/`)

Chronological analysis records — the learning loop.

- **Filename:** `{entity}-{topic}-{YYYY-MM-DD}.md` (e.g., `aapl-earnings-q1-2026-04-05.md`)
- **Required sections:** Date, Context, Thesis, Key Findings, Recommendation, Outcome (updated later)
- **Purpose:** Record predictions, track outcomes, extract lessons. This is where institutional memory compounds.

### Raw (`raw/`)

Source documents provided by the user. Immutable.

- The LLM reads but **NEVER** modifies files in this directory
- Users place earnings transcripts, research reports, articles, data files here

---

## Cross-Reference Convention

Link between wiki pages using relative markdown links:
- Entity to journal: `See [Q1 2026 analysis](../journal/aapl-earnings-q1-2026-04-05.md)`
- Journal to entity: `Company: [AAPL](../entities/aapl.md)`
- Playbook to entities: `Applied to [MSFT](../entities/msft.md), [GOOGL](../entities/googl.md)`

Every entity page should link to its journal entries. Every journal entry should link back to its entity.

---

## Index Convention

`index.md` is organized by category headers with one-line summaries:

```
## Entities
- [aapl](entities/aapl.md) — Apple Inc: hardware/services, last analyzed 2026-01
- [msft](entities/msft.md) — Microsoft: cloud/enterprise, last analyzed 2026-03

## Playbooks
- [dcf-assumptions](playbooks/dcf-assumptions.md) — Default DCF parameters and methodology notes

## Journal
- [aapl-earnings-q1-2026-04-05](journal/aapl-earnings-q1-2026-04-05.md) — AAPL Q1 2026 earnings analysis
```

---

## Log Convention

`log.md` is append-only. One line per action:

```
- 2026-04-05 14:23 | create | entities/aapl.md — Apple Inc entity page
- 2026-04-05 14:25 | update | entities/aapl.md — Added Q1 2026 earnings data
- 2026-04-05 14:30 | query  | "What is my AAPL thesis?" — returned journal entries
- 2026-04-05 15:00 | lint   | 2 orphan pages, 1 stale page
```

---

## User Preferences

_This section evolves as the LLM learns your style. Update it when you discover a consistent preference._

- **Preferred WACC range:**
- **Default terminal growth rate:**
- **Valuation methodology weighting:**
- **Sector coverage focus:**
- **Risk tolerance:**
- **Output format preferences:**
- **Typical analysis depth:**
