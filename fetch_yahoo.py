"""Rohdaten von Yahoo Finance (inoffizielle API via yfinance).

Liefert pro Ticker:
  1. Kurshistorie (OHLCV)       -> data/raw/prices_<TICKER>.csv
  2. Fundamentalkennzahlen      -> data/raw/fundamentals.csv  (eine Zeile je Ticker)
"""
from datetime import datetime, timezone

import pandas as pd
import yfinance as yf

from config import (
    FUNDAMENTAL_FIELDS,
    HISTORY_INTERVAL,
    HISTORY_PERIOD,
    RAW_DIR,
    TICKERS,
)


def fetch_prices(ticker: str) -> pd.DataFrame:
    df = yf.Ticker(ticker).history(
        period=HISTORY_PERIOD, interval=HISTORY_INTERVAL, auto_adjust=False
    )
    if df.empty:
        print(f"[WARN] Keine Kursdaten für {ticker}")
        return df
    df = df.reset_index()
    df["ticker"] = ticker
    return df


def fetch_fundamentals(ticker: str) -> dict:
    info = yf.Ticker(ticker).info or {}
    row = {"ticker": ticker}
    for yahoo_key, name in FUNDAMENTAL_FIELDS.items():
        row[name] = info.get(yahoo_key)          # None, wenn nicht vorhanden
    row["fetched_at_utc"] = datetime.now(timezone.utc).isoformat()
    return row


def main() -> None:
    fundamentals = []
    for t in TICKERS:
        print(f"[Yahoo] {t} ...")
        try:
            prices = fetch_prices(t)
            if not prices.empty:
                prices.to_csv(RAW_DIR / f"prices_{t}.csv", index=False)
            fundamentals.append(fetch_fundamentals(t))
        except Exception as e:  # Rate-Limits/Netzfehler sollen nicht alles abbrechen
            print(f"[ERROR] {t}: {e}")

    if fundamentals:
        pd.DataFrame(fundamentals).to_csv(RAW_DIR / "fundamentals.csv", index=False)
        print(f"[Yahoo] fundamentals.csv gespeichert ({len(fundamentals)} Ticker)")


if __name__ == "__main__":
    main()
