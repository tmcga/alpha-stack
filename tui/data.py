"""Market data layer — wraps yfinance + fetch.py for the TUI.

Provides async-friendly wrappers that the dashboard and widgets call.
All functions return plain dicts suitable for display.
"""

from datetime import datetime

try:
    import yfinance as yf
    _HAS_YF = True
except ImportError:
    _HAS_YF = False


def _safe_attr(obj, *attrs):
    """Try multiple attribute/key access patterns for yfinance compatibility."""
    for attr in attrs:
        try:
            val = getattr(obj, attr, None)
            if val is not None:
                return val
        except Exception:
            pass
        try:
            val = obj[attr]
            if val is not None:
                return val
        except (KeyError, TypeError, IndexError):
            pass
    return None


def get_quote(ticker: str) -> dict:
    """Get a real-time quote for a single ticker."""
    if not _HAS_YF:
        return {"error": "yfinance not installed"}
    try:
        t = yf.Ticker(ticker)
        info = t.fast_info
        hist = t.history(period="5d")

        # Extract price — try fast_info first, fall back to history
        price = _safe_attr(info, "last_price", "lastPrice", "regularMarketPrice")
        if price is None and len(hist) > 0:
            price = float(hist["Close"].iloc[-1])

        # Previous close for change calculation
        prev = None
        if len(hist) > 1:
            prev = float(hist["Close"].iloc[-2])
        elif price is not None:
            prev = _safe_attr(info, "previous_close", "regularMarketPreviousClose")

        change = round(price - prev, 2) if price is not None and prev is not None else 0
        change_pct = round(change / prev * 100, 2) if prev else 0

        return {
            "ticker": ticker.upper(),
            "price": round(price, 2) if price is not None else None,
            "change": change,
            "change_pct": change_pct,
            "volume": _safe_attr(info, "last_volume", "lastVolume"),
            "market_cap": _safe_attr(info, "market_cap", "marketCap"),
            "currency": _safe_attr(info, "currency") or "USD",
            "updated": datetime.now().strftime("%H:%M:%S"),
        }
    except Exception as e:
        return {"ticker": ticker.upper(), "error": str(e)}


def get_quotes(tickers: list[str]) -> list[dict]:
    """Get quotes for multiple tickers."""
    return [get_quote(t) for t in tickers]


def get_index_snapshot() -> list[dict]:
    """Get a snapshot of major market indices."""
    indices = ["^GSPC", "^DJI", "^IXIC", "^VIX", "^TNX", "^TYX"]
    names = {
        "^GSPC": "S&P 500",
        "^DJI": "DOW 30",
        "^IXIC": "NASDAQ",
        "^VIX": "VIX",
        "^TNX": "10Y YIELD",
        "^TYX": "30Y YIELD",
    }
    results = []
    for idx in indices:
        q = get_quote(idx)
        q["name"] = names.get(idx, idx)
        results.append(q)
    return results


def get_price_history(ticker: str, period: str = "1mo") -> dict:
    """Get price history for charting."""
    if not _HAS_YF:
        return {"error": "yfinance not installed"}
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period=period)
        if hist.empty:
            return {"ticker": ticker, "error": "No data"}
        return {
            "ticker": ticker.upper(),
            "period": period,
            "dates": [d.strftime("%Y-%m-%d") for d in hist.index],
            "close": [round(p, 2) for p in hist["Close"].tolist()],
            "high": round(hist["Close"].max(), 2),
            "low": round(hist["Close"].min(), 2),
            "count": len(hist),
        }
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}


def get_company_info(ticker: str) -> dict:
    """Get company fundamentals."""
    if not _HAS_YF:
        return {"error": "yfinance not installed"}
    try:
        t = yf.Ticker(ticker)
        info = t.info
        return {
            "ticker": ticker.upper(),
            "name": info.get("longName") or info.get("shortName", ticker),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "market_cap": info.get("marketCap"),
            "enterprise_value": info.get("enterpriseValue"),
            "revenue": info.get("totalRevenue"),
            "ebitda": info.get("ebitda"),
            "net_income": info.get("netIncomeToCommon"),
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "ev_ebitda": info.get("enterpriseToEbitda"),
            "profit_margin": info.get("profitMargins"),
            "revenue_growth": info.get("revenueGrowth"),
            "dividend_yield": info.get("dividendYield"),
            "beta": info.get("beta"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "description": (info.get("longBusinessSummary") or "")[:500],
        }
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}


def is_available() -> bool:
    return _HAS_YF
