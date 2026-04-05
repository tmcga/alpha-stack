# Wiki: Building Your Finance Knowledge Base

The wiki is Alpha Stack's institutional memory. Every company you research, every thesis you form, every methodology preference you express — it all gets filed, cross-referenced, and made available for future analyses.

---

## Company Profile

You're an analyst who has been using Alpha Stack for several weeks. You've run multiple analyses and want them to compound rather than disappear into chat history.

## Getting Started

### Initialize the Wiki

```
/wiki

Initialize my knowledge base.
```

This creates `~/.alpha-stack/wiki/` with directories for entities, playbooks, journal entries, and raw sources.

### Ingest an Analysis

After completing an LBO analysis of CyberVault Systems:

```
/wiki

Ingest the following into my knowledge base:

Company: CyberVault Systems (cybersecurity, B2B SaaS)
Analysis: LBO at 12x entry, 13x exit over 5 years
Key financials: $500M revenue, $125M EBITDA (25% margin, expanding to 30%)
Debt: 5.5x leverage, 7.5% blended rate
Returns: 22% IRR base case, 2.8x MOIC
Key risks: customer concentration (top 3 = 60%), integration complexity
Thesis: margin expansion from on-prem to cloud transition
Recommendation: Proceed to IC with high conviction
```

The wiki will create an entity page for CyberVault, a journal entry with the LBO findings, and cross-reference them.

### Query Prior Knowledge

Three months later, CyberVault comes up in another context:

```
/wiki

What do I know about CyberVault Systems? What was my thesis and what were the key risks?
```

The wiki synthesizes your prior analysis without re-deriving anything.

### Track Methodology Preferences

```
/wiki

Update my playbook: for B2B SaaS LBOs, I typically use 5.0-6.0x entry leverage,
assume 200-300bps of annual margin expansion from cloud transition,
and require 20%+ base case IRR for IC approval.
```

These preferences get filed to `playbooks/` and inform future analyses.

### Health Check

```
/wiki

Run a health check on my knowledge base.
```

The lint operation finds orphan pages, stale entries, missing cross-references, and suggests improvements.

---

## Try It

```
/wiki

Initialize my knowledge base and then ingest this: I just finished analyzing Apple
(AAPL). Revenue $394B, services segment growing 14%, gross margin 46% on services
vs 36% hardware. My thesis is that the services mix shift drives P/E expansion from
28x to 32x over 18 months. Main risk is EU antitrust regulation forcing App Store
fee reductions. Secondary risk is China macro weakness hitting hardware sales.
Price target: $245 (18% upside from current $208). Conviction: medium-high.
```
