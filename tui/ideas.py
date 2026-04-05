"""Idea generation engine — mines the wiki and market data for actionable ideas.

Scans all wiki pages, parses markdown heuristically, detects patterns
(thesis drift, stale outcomes, research gaps, risk flags), and enriches
with live market data to produce a ranked list of actionable ideas.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class IdeaType(Enum):
    THESIS_DRIFT = "drift"
    OUTCOME_TRACKER = "outcome"
    RESEARCH_GAP = "gap"
    RISK_MONITOR = "risk"
    SUGGESTED_ACTION = "action"
    STALE_PLAYBOOK = "playbook"


IDEA_TYPE_LABELS = {
    IdeaType.THESIS_DRIFT: "DRIFT",
    IdeaType.OUTCOME_TRACKER: "OUTCOMES",
    IdeaType.RESEARCH_GAP: "GAPS",
    IdeaType.RISK_MONITOR: "RISKS",
    IdeaType.SUGGESTED_ACTION: "ACTIONS",
    IdeaType.STALE_PLAYBOOK: "ACTIONS",
}

# Priority order for tie-breaking (lower index = higher priority)
_TYPE_PRIORITY = [
    IdeaType.RISK_MONITOR,
    IdeaType.THESIS_DRIFT,
    IdeaType.OUTCOME_TRACKER,
    IdeaType.SUGGESTED_ACTION,
    IdeaType.RESEARCH_GAP,
    IdeaType.STALE_PLAYBOOK,
]


@dataclass
class Idea:
    idea_type: IdeaType
    priority: float
    title: str
    subtitle: str = ""
    ticker: str | None = None
    wiki_refs: list = field(default_factory=list)
    market_data: dict | None = None
    detail: dict = field(default_factory=dict)
    actions: list = field(default_factory=list)

    def sort_key(self):
        type_rank = _TYPE_PRIORITY.index(self.idea_type) if self.idea_type in _TYPE_PRIORITY else 99
        return (-self.priority, type_rank)


# ── Markdown parsers ──────────────────────────────────────────────────────


def _split_sections(content: str) -> dict[str, str]:
    """Split markdown content by ## headings into {heading: body} dict."""
    sections = {}
    current_heading = "_preamble"
    current_lines = []
    for line in content.split("\n"):
        if line.startswith("## "):
            sections[current_heading] = "\n".join(current_lines).strip()
            current_heading = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)
    sections[current_heading] = "\n".join(current_lines).strip()
    return sections


def _extract_meta(content: str, key: str) -> str | None:
    """Extract a **Key:** Value line from markdown content."""
    m = re.search(rf"\*\*{re.escape(key)}:\*\*\s*(.+)", content)
    return m.group(1).strip() if m else None


def _extract_links(text: str) -> list[str]:
    """Extract markdown link targets from text."""
    return re.findall(r"\[([^\]]*)\]\(([^)]+)\)", text)


def _parse_bullets(text: str) -> list[str]:
    """Extract bullet point items from a section body."""
    results = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("- "):
            results.append(stripped[2:].strip())
    return results


def parse_entity(content: str) -> dict:
    """Parse an entity page into structured data."""
    sections = _split_sections(content)
    preamble = sections.get("_preamble", "")

    ticker = _extract_meta(preamble, "Ticker")
    last_updated = _extract_meta(preamble, "Last Updated")
    sector = _extract_meta(preamble, "Sector")

    thesis = sections.get("Current Thesis", "")
    risks = _parse_bullets(sections.get("Risks", ""))
    related_text = sections.get("Related", "")
    related_slugs = [target.split("/")[-1].replace(".md", "") for _, target in _extract_links(related_text)]

    # Extract prior analysis links
    prior_text = sections.get("Prior Analyses", "")
    prior_links = _extract_links(prior_text)

    return {
        "ticker": ticker,
        "sector": sector,
        "last_updated": last_updated,
        "thesis": thesis,
        "risks": risks,
        "related_slugs": related_slugs,
        "prior_analyses": prior_links,
        "overview": sections.get("Overview", ""),
    }


def parse_journal(content: str) -> dict:
    """Parse a journal entry into structured data."""
    sections = _split_sections(content)
    preamble = sections.get("_preamble", "")

    date = _extract_meta(preamble, "Date")
    skill = _extract_meta(preamble, "Skill Used")
    entity_text = _extract_meta(preamble, "Entity") or ""
    entity_links = _extract_links(entity_text)
    entity_slug = entity_links[0][1].split("/")[-1].replace(".md", "") if entity_links else None

    # Parse recommendation section
    rec_text = sections.get("Recommendation", "")
    direction = None
    for d in ("Long", "Short", "Buy", "Sell", "Hold"):
        if d.lower() in rec_text.lower():
            direction = d
            break

    target_match = re.search(r"[Tt]arget[:\s]*\$?([\d,.]+)", rec_text)
    target_price = float(target_match.group(1).replace(",", "")) if target_match else None

    conviction_match = re.search(r"[Cc]onviction[:\s]*([\w-]+)", rec_text)
    conviction = conviction_match.group(1) if conviction_match else None

    horizon_match = re.search(r"[Hh]orizon[:\s]*([\d]+)\s*(month|year|week|day)", rec_text)
    horizon_months = None
    if horizon_match:
        val, unit = int(horizon_match.group(1)), horizon_match.group(2)
        horizon_months = val * (12 if "year" in unit else 1 if "month" in unit else 1 / 4 if "week" in unit else 1 / 30)

    # Parse outcome section
    outcome_text = sections.get("Outcome", "")
    outcome_status = "Open"
    for status in ("Confirmed", "Invalidated", "Partially Confirmed"):
        if status.lower() in outcome_text.lower():
            outcome_status = status
            break

    thesis = sections.get("Thesis", "")
    risks = _parse_bullets(sections.get("Risks", ""))
    findings = _parse_bullets(sections.get("Key Findings", ""))

    return {
        "date": date,
        "skill": skill,
        "entity_slug": entity_slug,
        "thesis": thesis,
        "direction": direction,
        "target_price": target_price,
        "conviction": conviction,
        "horizon_months": horizon_months,
        "outcome_status": outcome_status,
        "risks": risks,
        "findings": findings,
    }


def parse_playbook(content: str) -> dict:
    """Parse a playbook page into structured data."""
    sections = _split_sections(content)
    preamble = sections.get("_preamble", "")

    last_updated = _extract_meta(preamble, "Last Updated")
    preferences = _parse_bullets(sections.get("Preferences", ""))
    when_to_apply = sections.get("When to Apply", "")

    return {
        "last_updated": last_updated,
        "preferences": preferences,
        "when_to_apply": when_to_apply,
    }


# ── Idea detectors ────────────────────────────────────────────────────────


def _days_since(date_str: str | None) -> int | None:
    """Parse a date string and return days since then, or None."""
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(date_str.strip()[:19], fmt)
            return (datetime.now() - dt).days
        except ValueError:
            continue
    return None


def _detect_thesis_drift(entities: dict, journals: list) -> list[Idea]:
    """Find entities where the thesis has a target price that may have drifted."""
    ideas = []
    for slug, entity in entities.items():
        ticker = entity.get("ticker")
        if not ticker:
            continue

        # Find the most recent journal entry with a target price for this entity
        relevant = [j for j in journals if j.get("entity_slug") == slug and j.get("target_price")]
        if not relevant:
            continue

        # Sort by date descending
        relevant.sort(key=lambda j: j.get("date", ""), reverse=True)
        latest = relevant[0]

        target = latest["target_price"]
        direction = latest.get("direction", "")
        date = latest.get("date", "?")
        thesis_excerpt = (latest.get("thesis") or entity.get("thesis", ""))[:100]

        ideas.append(Idea(
            idea_type=IdeaType.THESIS_DRIFT,
            priority=0.5,  # Will be recomputed with market data
            title=f"{ticker}: Check drift from ${target:,.0f} target",
            subtitle=f"Thesis from {date}",
            ticker=ticker,
            wiki_refs=[
                {"category": "entities", "slug": slug},
                {"category": "journal", "slug": latest.get("_slug", "")},
            ],
            detail={
                "target_price": target,
                "direction": direction,
                "conviction": latest.get("conviction"),
                "horizon_months": latest.get("horizon_months"),
                "thesis": thesis_excerpt,
                "date": date,
            },
            actions=[
                {"label": "View entity page", "type": "wiki", "target": ("entities", slug)},
                {"label": "View journal entry", "type": "wiki", "target": ("journal", latest.get("_slug", ""))},
                {"label": f"Re-run analysis for {ticker}", "type": "tool", "target": "dcf"},
            ],
        ))
    return ideas


def _detect_stale_outcomes(journals: list) -> list[Idea]:
    """Find journal entries with Open outcome status past their time horizon."""
    ideas = []
    for j in journals:
        if j.get("outcome_status") != "Open":
            continue
        if not j.get("target_price") and not j.get("direction"):
            continue

        days = _days_since(j.get("date"))
        if days is None:
            continue

        horizon = j.get("horizon_months")
        # Flag if older than 30 days, or past horizon
        if horizon and days < horizon * 30 * 0.8:
            continue  # Not yet near horizon
        if not horizon and days < 30:
            continue

        ticker = None
        entity_slug = j.get("entity_slug")
        direction = j.get("direction", "?")
        target = j.get("target_price")

        title_parts = [direction]
        if target:
            title_parts.append(f"${target:,.0f} target")
        title_parts.append(f"({days}d ago)")

        ideas.append(Idea(
            idea_type=IdeaType.OUTCOME_TRACKER,
            priority=min(1.0, 0.4 + days / 365),
            title=f"{entity_slug or '?'}: {' '.join(title_parts)}",
            subtitle=f"Outcome still Open — check if thesis played out",
            ticker=ticker,
            wiki_refs=[{"category": "journal", "slug": j.get("_slug", "")}],
            detail={
                "direction": direction,
                "target_price": target,
                "conviction": j.get("conviction"),
                "date": j.get("date"),
                "days_elapsed": days,
                "horizon_months": horizon,
                "thesis": (j.get("thesis") or "")[:100],
            },
            actions=[
                {"label": "View journal entry", "type": "wiki", "target": ("journal", j.get("_slug", ""))},
                {"label": "Update outcome status", "type": "wiki", "target": ("journal", j.get("_slug", ""))},
            ],
        ))
    return ideas


def _detect_research_gaps(entities: dict, all_pages: list) -> list[Idea]:
    """Find stale entities, missing related entities, and unanalyzed entities."""
    ideas = []
    existing_entity_slugs = set(entities.keys())

    for slug, entity in entities.items():
        # Stale entity: not modified in 60+ days
        days = _days_since(entity.get("last_updated"))
        modified_days = None
        for p in all_pages:
            if p.get("category") == "entities" and p.get("slug") == slug:
                modified_days = _days_since(p.get("modified"))
                break

        age = days or modified_days
        if age and age > 60:
            ideas.append(Idea(
                idea_type=IdeaType.RESEARCH_GAP,
                priority=min(1.0, 0.3 + age / 365),
                title=f"{slug}: {age}d since last update",
                subtitle="Entity page may be stale",
                ticker=entity.get("ticker"),
                wiki_refs=[{"category": "entities", "slug": slug}],
                detail={"days_stale": age, "last_updated": entity.get("last_updated")},
                actions=[
                    {"label": "View entity page", "type": "wiki", "target": ("entities", slug)},
                    {"label": "Run fresh analysis", "type": "tool", "target": "dcf"},
                ],
            ))

        # Missing related entities
        for related_slug in entity.get("related_slugs", []):
            if related_slug and related_slug not in existing_entity_slugs:
                ideas.append(Idea(
                    idea_type=IdeaType.RESEARCH_GAP,
                    priority=0.3,
                    title=f"{related_slug}: No entity page",
                    subtitle=f"Referenced by {slug} but not in wiki",
                    wiki_refs=[{"category": "entities", "slug": slug}],
                    detail={"referenced_by": slug, "missing_slug": related_slug},
                    actions=[
                        {"label": f"Create {related_slug} entity page", "type": "wiki", "target": ("entities", related_slug)},
                    ],
                ))

    return ideas


def _detect_risk_flags(entities: dict, journals: list) -> list[Idea]:
    """Extract risks from journals and flag repeated or high-frequency risks."""
    # Group risks by entity
    entity_risks: dict[str, list[dict]] = {}
    for j in journals:
        slug = j.get("entity_slug")
        if not slug:
            continue
        for risk in j.get("risks", []):
            entity_risks.setdefault(slug, []).append({
                "text": risk,
                "date": j.get("date"),
                "journal_slug": j.get("_slug", ""),
            })

    ideas = []
    for slug, risks in entity_risks.items():
        if len(risks) < 2:
            continue  # Only flag when multiple analyses mention risks

        entity = entities.get(slug, {})
        ticker = entity.get("ticker")

        # Deduplicate by rough text similarity (first 50 chars)
        seen = {}
        for r in risks:
            key = r["text"][:50].lower()
            seen.setdefault(key, []).append(r)

        for key, occurrences in seen.items():
            if len(occurrences) < 2:
                continue
            ideas.append(Idea(
                idea_type=IdeaType.RISK_MONITOR,
                priority=min(1.0, 0.5 + len(occurrences) * 0.15),
                title=f"{slug}: Recurring risk ({len(occurrences)}x)",
                subtitle=occurrences[0]["text"][:60],
                ticker=ticker,
                wiki_refs=[
                    {"category": "entities", "slug": slug},
                    *[{"category": "journal", "slug": o["journal_slug"]} for o in occurrences],
                ],
                detail={
                    "risk_text": occurrences[0]["text"],
                    "frequency": len(occurrences),
                    "sources": [{"date": o["date"], "slug": o["journal_slug"]} for o in occurrences],
                },
                actions=[
                    {"label": "View entity page", "type": "wiki", "target": ("entities", slug)},
                    {"label": "View latest analysis", "type": "wiki",
                     "target": ("journal", occurrences[-1]["journal_slug"])},
                ],
            ))
    return ideas


def _detect_suggested_actions(entities: dict, journals: list) -> list[Idea]:
    """Suggest specific tool re-runs or page updates."""
    ideas = []

    # Entities with journal entries older than 45 days and a tool tag
    entity_latest_journal: dict[str, dict] = {}
    for j in journals:
        slug = j.get("entity_slug")
        if not slug:
            continue
        existing = entity_latest_journal.get(slug)
        if not existing or (j.get("date", "") > existing.get("date", "")):
            entity_latest_journal[slug] = j

    for slug, latest in entity_latest_journal.items():
        days = _days_since(latest.get("date"))
        if days is None or days < 45:
            continue

        entity = entities.get(slug, {})
        ticker = entity.get("ticker")
        skill = latest.get("skill", "")

        # Map skill to tool suggestion
        tool_map = {
            "/lbo": "lbo", "/equity-research": "dcf", "/long-short": "dcf",
            "/derivatives": "black_scholes", "/credit": "zscore",
            "/portfolio": "portfolio_risk", "/risk": "portfolio_risk",
        }
        suggested_tool = tool_map.get(skill, "dcf")

        ideas.append(Idea(
            idea_type=IdeaType.SUGGESTED_ACTION,
            priority=min(1.0, 0.3 + days / 180),
            title=f"{slug}: Refresh analysis ({days}d old)",
            subtitle=f"Last ran {skill or 'analysis'} on {latest.get('date', '?')}",
            ticker=ticker,
            wiki_refs=[
                {"category": "entities", "slug": slug},
                {"category": "journal", "slug": latest.get("_slug", "")},
            ],
            detail={"days_since": days, "skill": skill, "suggested_tool": suggested_tool},
            actions=[
                {"label": f"Run {suggested_tool.upper()}", "type": "tool", "target": suggested_tool},
                {"label": "View entity page", "type": "wiki", "target": ("entities", slug)},
            ],
        ))
    return ideas


def _detect_stale_playbooks(playbooks: dict, all_pages: list) -> list[Idea]:
    """Find playbooks not updated in 90+ days."""
    ideas = []
    for slug, pb in playbooks.items():
        days = _days_since(pb.get("last_updated"))
        if days is None:
            # Try file modified date
            for p in all_pages:
                if p.get("category") == "playbooks" and p.get("slug") == slug:
                    days = _days_since(p.get("modified"))
                    break
        if days is None or days < 90:
            continue

        ideas.append(Idea(
            idea_type=IdeaType.STALE_PLAYBOOK,
            priority=min(1.0, 0.2 + days / 365),
            title=f"Playbook '{slug}' stale ({days}d)",
            subtitle="Methodology may need updating",
            wiki_refs=[{"category": "playbooks", "slug": slug}],
            detail={"days_stale": days, "last_updated": pb.get("last_updated")},
            actions=[
                {"label": "View playbook", "type": "wiki", "target": ("playbooks", slug)},
            ],
        ))
    return ideas


# ── Main pipeline ─────────────────────────────────────────────────────────


def generate_ideas() -> list[Idea]:
    """Scan the wiki and generate ideas (Phase 1+2, no network).

    Returns a sorted list of Idea objects. Call enrich_with_market_data()
    separately in an async worker to add live prices.
    """
    try:
        from wiki import wiki_list_pages, wiki_read_page, wiki_status
    except ImportError:
        return [_fallback_idea("Wiki tools not available — check your installation")]

    status = wiki_status()
    if not status.get("initialized"):
        return [_fallback_idea("Initialize your wiki to start generating ideas", "Run /wiki init")]

    # Phase 1: Read all pages
    all_pages = wiki_list_pages().get("pages", [])
    if not all_pages:
        return [_fallback_idea("Your wiki is empty", "Run an analysis and file it with /wiki")]

    entities = {}
    journals = []
    playbooks = {}

    for page in all_pages:
        cat, slug = page["category"], page["slug"]
        if cat == "raw":
            continue
        try:
            result = wiki_read_page(cat, slug)
            if "error" in result:
                continue
            content = result["content"]

            if cat == "entities":
                entities[slug] = parse_entity(content)
            elif cat == "journal":
                parsed = parse_journal(content)
                parsed["_slug"] = slug
                journals.append(parsed)
            elif cat == "playbooks":
                playbooks[slug] = parse_playbook(content)
        except Exception:
            continue  # Skip unparseable pages

    if not entities and not journals:
        return [_fallback_idea(
            "No entity or journal pages found",
            "Run an analysis and file it with /wiki to start generating ideas",
        )]

    # Phase 2: Run detectors
    ideas = []
    ideas.extend(_detect_thesis_drift(entities, journals))
    ideas.extend(_detect_stale_outcomes(journals))
    ideas.extend(_detect_research_gaps(entities, all_pages))
    ideas.extend(_detect_risk_flags(entities, journals))
    ideas.extend(_detect_suggested_actions(entities, journals))
    ideas.extend(_detect_stale_playbooks(playbooks, all_pages))

    if not ideas:
        return [_fallback_idea("No actionable ideas found", "Your wiki is up to date — keep analyzing")]

    ideas.sort(key=lambda i: i.sort_key())
    return ideas


def enrich_with_market_data(ideas: list[Idea]) -> list[Idea]:
    """Phase 3: Fetch market data and update ideas with live prices.

    Modifies ideas in-place and returns the re-sorted list.
    Call this in a background worker thread.
    """
    try:
        from tui.data import get_quote, is_available
        if not is_available():
            return ideas
    except ImportError:
        return ideas

    # Collect unique tickers
    tickers = {i.ticker for i in ideas if i.ticker}
    quotes = {}
    for ticker in tickers:
        try:
            q = get_quote(ticker)
            if "error" not in q and q.get("price"):
                quotes[ticker] = q
        except Exception:
            continue

    # Update ideas with market data
    for idea in ideas:
        if not idea.ticker or idea.ticker not in quotes:
            continue

        quote = quotes[idea.ticker]
        idea.market_data = quote
        current_price = quote["price"]

        if idea.idea_type == IdeaType.THESIS_DRIFT:
            target = idea.detail.get("target_price")
            if target and current_price:
                drift_pct = (current_price - target) / target
                idea.detail["current_price"] = current_price
                idea.detail["drift_pct"] = drift_pct
                idea.priority = min(1.0, abs(drift_pct) / 0.50)
                sign = "+" if drift_pct >= 0 else ""
                idea.title = f"{idea.ticker}: {sign}{drift_pct:.1%} from ${target:,.0f} target"

        elif idea.idea_type == IdeaType.OUTCOME_TRACKER:
            target = idea.detail.get("target_price")
            if target and current_price:
                pnl_pct = (current_price - target) / target
                idea.detail["current_price"] = current_price
                idea.detail["pnl_pct"] = pnl_pct
                idea.priority = min(1.0, 0.5 + abs(pnl_pct) * 0.5)

    ideas.sort(key=lambda i: i.sort_key())
    return ideas


def _fallback_idea(title: str, subtitle: str = "") -> Idea:
    """Create a single suggestion idea for empty/uninitialized states."""
    return Idea(
        idea_type=IdeaType.SUGGESTED_ACTION,
        priority=1.0,
        title=title,
        subtitle=subtitle,
        actions=[{"label": "Open Wiki Browser", "type": "screen", "target": "wiki"}],
    )
