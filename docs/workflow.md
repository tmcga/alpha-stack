# The Alpha Stack Workflow

## Source > Diligence > Model > Stress > Decide > Monitor

Every analysis in Alpha Stack follows six phases. This is the finance equivalent of a software sprint — but instead of shipping code, you are producing investment decisions.

---

## Phase 1: Source

**What it means:** Identify the opportunity — a deal, trade idea, allocation shift, or client need.

**What Claude does:**
- Gather context from the user (company, market, event, thesis)
- Frame the analytical question
- Identify what data is needed and what is missing
- Activate the relevant skill and load the role context

**Outputs:** A clearly framed question with explicit scope and data requirements.

**Key question:** "What are we trying to decide, and what information do we need?"

---

## Phase 2: Diligence

**What it means:** Deep research — comparable analysis, channel checks, credit review, regulatory scan.

**What Claude does:**
- Structured analysis using the skill's prompt templates
- Cross-reference with other desk perspectives when relevant
- Build the qualitative case: competitive dynamics, management quality, regulatory risk
- Identify the key debates and variant perceptions

**Outputs:** A research brief with the bull case, bear case, and key debates identified.

**Key question:** "What does the market think, and where might it be wrong?"

---

## Phase 3: Model

**What it means:** Build the quantitative framework — DCF, LBO, risk model, portfolio optimization.

**What Claude does:**
- Run the relevant Python tools with user-provided inputs
- Construct sensitivity tables across key variables
- Build scenario analyses (base, bull, bear)
- Calculate risk-adjusted metrics (Sharpe, Kelly fraction, probability-weighted returns)

**Tools invoked:** DCF, LBO, WACC, Black-Scholes, Kelly, Black-Litterman, Monte Carlo — depending on the skill.

**Outputs:** Quantitative model with sensitivity tables and scenario analysis.

**Key question:** "What does the math say, and which assumptions drive the answer?"

---

## Phase 4: Stress

**What it means:** Challenge every assumption — pre-mortem, counterargument, tail risk, regime change.

**What Claude does:**
- Pre-mortem analysis: "Assume this investment lost money. Why?"
- Identify the top 3 thesis-killing risks
- Run tail-risk scenarios (Monte Carlo, extreme sensitivity)
- Test correlation assumptions under stress
- Ask: "Who is on the other side of this trade, and why?"

**Outputs:** Risk memo with thesis-killing scenarios ranked by probability and severity.

**Key question:** "What would make us wrong, and how bad would it be?"

---

## Phase 5: Decide

**What it means:** Investment committee memo — recommendation with explicit conviction level.

**What Claude does:**
- Synthesize Source through Stress into a clear recommendation
- State the thesis in one sentence
- Provide recommended sizing (using Kelly or portfolio constraints)
- Define entry point, target, and stop-loss
- Assign a conviction level (high/medium/low) with justification

**Outputs:** Investment recommendation memo.

**Key question:** "Given everything we know, what should we do and how much?"

---

## Phase 6: Monitor

**What it means:** Track the position — catalysts, thesis drift, stop-loss triggers, rebalancing.

**What Claude does:**
- Define the catalyst calendar (earnings, regulatory decisions, deal milestones)
- Set thesis-drift criteria (what changes would invalidate the thesis)
- Establish exit rules (price targets, stop-losses, time-based exits)
- Define rebalancing triggers for portfolio-level decisions

**Outputs:** Monitoring framework with explicit triggers and review schedule.

**Key question:** "How will we know if we're right, wrong, or if the thesis has changed?"

---

## How the Workflow Maps to Finance Verticals

### Deal Execution (Banking / PE)
Source (target identification) > Diligence (CIM, data room review) > Model (DCF, LBO, merger model) > Stress (downside cases, regulatory risk) > Decide (bid recommendation, fairness opinion) > Monitor (post-close integration)

### Portfolio Management (Trading / AM / HF)
Source (idea generation, screening) > Diligence (variant perception, fundamental analysis) > Model (Kelly sizing, factor exposure, Black-Litterman) > Stress (drawdown scenarios, correlation breaks) > Decide (position initiation with size and stops) > Monitor (P&L attribution, thesis drift, exit triggers)

### Investment Analysis (Cross-desk)
Source (event or catalyst identification) > Diligence (cross-reference guide — same event, multiple desks) > Model (valuation from relevant angle) > Stress (what kills this idea?) > Decide (recommendation with conviction) > Monitor (catalyst timeline tracking)

### Wealth Advisory
Source (client goals, life events) > Diligence (current portfolio review, tax situation) > Model (Monte Carlo, asset allocation, estate planning) > Stress (sequence-of-returns risk, longevity risk) > Decide (allocation recommendation, withdrawal strategy) > Monitor (rebalancing triggers, life event updates)
