# Performance Attribution

Prompt library for portfolio performance attribution analysis. Covers Brinson-Fachler, factor-based, and multi-period attribution.

## Role Context

```
You are a performance analyst who explains where returns came from — and more
importantly, whether the return sources are repeatable. Good attribution separates
skill from luck, timing from selection, and intended bets from unintended exposures.
The portfolio manager needs to know what worked, what didn't, and what was accidental.
```

---

## 1. Brinson-Fachler Attribution

```
Run a Brinson-Fachler attribution for [fund name] for [period].

Portfolio and benchmark data:
| Sector | Port Weight | Port Return | Bench Weight | Bench Return |
|--------|-----------|------------|-------------|-------------|
| [Sector 1] | [X]% | [X]% | [X]% | [X]% |
| [Sector 2] | [X]% | [X]% | [X]% | [X]% |
| [Sector 3] | [X]% | [X]% | [X]% | [X]% |
| ... | | | | |

Run tool: `python3 tools/brinson.py`

Analyze the output:
1. **Total active return**: Portfolio return - Benchmark return
2. **Allocation effect**: Did sector bets add or destroy value?
3. **Selection effect**: Did stock picking within sectors add value?
4. **Interaction effect**: Combined impact of allocation and selection
5. **Top contributors**: Which 3 sectors drove the most active return?
6. **Top detractors**: Which sectors hurt performance most?
7. **Intentionality check**: Were the biggest contributors from intended bets or accidental exposures?
```

## 2. Factor Attribution

```
Decompose portfolio returns by factor exposure for [fund name].

Factor exposures (current):
| Factor | Portfolio Beta | Benchmark Beta | Active Exposure |
|--------|--------------|---------------|----------------|
| Market | [X] | 1.0 | [X] |
| Size (SMB) | [X] | [X] | [X] |
| Value (HML) | [X] | [X] | [X] |
| Momentum | [X] | [X] | [X] |
| Quality | [X] | [X] | [X] |
| Low Vol | [X] | [X] | [X] |

Period returns by factor:
| Factor | Factor Return | Active Exposure | Factor Contribution |
|--------|-------------|----------------|-------------------|
| Market | [X]% | | |
| Size | [X]% | | |
| Value | [X]% | | |
| Momentum | [X]% | | |
| Quality | [X]% | | |
| Low Vol | [X]% | | |

Calculate:
1. **Factor contribution** = Active Exposure × Factor Return (for each factor)
2. **Total factor return**: Sum of factor contributions
3. **Residual (alpha)**: Total active return - Factor return
4. **Key question**: Is the PM generating alpha, or just harvesting factor premia?
5. **Unintended exposures**: Any factor tilts the PM didn't intend?
```

## 3. Multi-Period Attribution

```
Perform multi-period attribution for [fund name] over [quarters/years].

Period-by-period results:
| Period | Port Return | Bench Return | Active Return |
|--------|-----------|-------------|--------------|
| [Q1] | [X]% | [X]% | [X]% |
| [Q2] | [X]% | [X]% | [X]% |
| [Q3] | [X]% | [X]% | [X]% |
| [Q4] | [X]% | [X]% | [X]% |

Analyze:
1. **Compounding effect**: Why cumulative active return ≠ sum of periodic active returns
2. **Consistency**: How many periods did the PM beat the benchmark?
3. **Hit rate by source**: Is allocation or selection more consistent?
4. **Drawdown attribution**: In down periods, what drove underperformance?
5. **Information ratio**: Annualized active return / Tracking error
   - Run tool: `python3 tools/portfolio_risk.py`
```

---

See also: `/risk`, `/portfolio`, `/long-short`
