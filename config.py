"""Zentrale Einstellungen für die Rohdaten-Beschaffung."""
from pathlib import Path

# Aktien, die analysiert werden sollen (Yahoo-Finance-Ticker)
TICKERS = ["AAPL", "MSFT", "NVDA", "SAP.DE", "SIE.DE"]

# Zeitraum der Kurshistorie (Training früher, Test später -> genug Historie holen)
HISTORY_PERIOD = "10y"      # z.B. "5y", "10y", "max"
HISTORY_INTERVAL = "1d"     # "1d", "1wk", "1mo"

# Polymarket: Suchbegriffe für News-/Stimmungs-Faktor
POLYMARKET_QUERIES = ["stock market", "S&P 500", "Nasdaq", "Fed rate", "recession"]
POLYMARKET_MAX_EVENTS_PER_QUERY = 10

# Ausgabeordner
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Kennzahlen aus yfinance (Ticker.info) -> sprechender Name
# Entspricht der Liste im Abstract
FUNDAMENTAL_FIELDS = {
    "forwardPE": "forward_pe",
    "trailingPegRatio": "peg_ratio",
    "pegRatio": "peg_ratio_alt",
    "enterpriseToEbitda": "ev_ebitda",
    "priceToBook": "price_book",
    "priceToSalesTrailing12Months": "price_sales",
    "profitMargins": "profit_margin",
    "operatingMargins": "operating_margin",
    "returnOnEquity": "roe",
    "returnOnAssets": "roa",
    "revenueGrowth": "quarterly_revenue_growth",
    "earningsQuarterlyGrowth": "quarterly_earnings_growth",
    "debtToEquity": "total_debt_equity",
    "currentRatio": "current_ratio",
    "freeCashflow": "free_cashflow",          # Yahoo liefert hier den FCF; "levered" ggf. Näherung
    "dividendYield": "dividend_yield",
    "payoutRatio": "payout_ratio",
    "beta": "beta",
    "targetMeanPrice": "analyst_price_target",
    # Zusatzinfos für die Bewertung (Alter/Datenmenge)
    "currentPrice": "current_price",
    "marketCap": "market_cap",
    "sector": "sector",
    "longName": "name",
}
