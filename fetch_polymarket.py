"""Rohdaten von Polymarket (öffentliche Gamma- und CLOB-API, kein API-Key nötig).

Ablauf:
  1. Events/Märkte per Suchbegriff finden (Gamma API)
  2. Aktuelle Wahrscheinlichkeiten ("Yes"-Preis) speichern
  3. Preisverlauf je Markt holen (CLOB API) -> Zeitreihe für den News-Faktor

Ausgabe:
  data/raw/polymarket_markets.csv
  data/raw/polymarket_price_history.csv
"""
import json
import time
from datetime import datetime, timezone

import pandas as pd
import requests

from config import POLYMARKET_MAX_EVENTS_PER_QUERY, POLYMARKET_QUERIES, RAW_DIR

GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
TIMEOUT = 20
PAUSE = 0.3  # Sekunden zwischen Requests (höflich bleiben)


def _get(url: str, params: dict | None = None):
    r = requests.get(url, params=params, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def _parse_json_field(value):
    """Gamma liefert outcomes/outcomePrices/clobTokenIds oft als JSON-String."""
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return []
    return value or []


def search_events(query: str) -> list[dict]:
    data = _get(
        f"{GAMMA}/public-search",
        {"q": query, "limit_per_type": POLYMARKET_MAX_EVENTS_PER_QUERY, "events_status": "active"},
    )
    return data.get("events", [])


def flatten_markets(events: list[dict], query: str) -> list[dict]:
    rows = []
    for ev in events:
        for m in ev.get("markets", []):
            outcomes = _parse_json_field(m.get("outcomes"))
            prices = _parse_json_field(m.get("outcomePrices"))
            tokens = _parse_json_field(m.get("clobTokenIds"))
            if not outcomes or not prices:
                continue
            yes_idx = outcomes.index("Yes") if "Yes" in outcomes else 0
            rows.append(
                {
                    "query": query,
                    "event_title": ev.get("title"),
                    "market_id": m.get("id"),
                    "question": m.get("question"),
                    "prob_yes": float(prices[yes_idx]),
                    "token_id_yes": tokens[yes_idx] if len(tokens) > yes_idx else None,
                    "volume": m.get("volume"),
                    "liquidity": m.get("liquidity"),
                    "end_date": m.get("endDate"),
                    "closed": m.get("closed"),
                    "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
                }
            )
    return rows


def fetch_price_history(token_id: str, interval: str = "max", fidelity: int = 1440) -> pd.DataFrame:
    """fidelity = Minuten pro Datenpunkt (1440 = täglich)."""
    data = _get(f"{CLOB}/prices-history", {"market": token_id, "interval": interval, "fidelity": fidelity})
    hist = data.get("history", [])
    df = pd.DataFrame(hist)  # Spalten: t (Unix-Sekunden), p (Preis = Wahrscheinlichkeit)
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["t"], unit="s", utc=True)
    df = df.rename(columns={"p": "prob_yes"}).drop(columns=["t"])
    df["token_id_yes"] = token_id
    return df


def main() -> None:
    all_rows = []
    for q in POLYMARKET_QUERIES:
        print(f"[Polymarket] Suche: {q!r}")
        try:
            all_rows += flatten_markets(search_events(q), q)
        except Exception as e:
            print(f"[ERROR] Suche {q!r}: {e}")
        time.sleep(PAUSE)

    if not all_rows:
        print("[Polymarket] Keine Märkte gefunden.")
        return

    markets = pd.DataFrame(all_rows).drop_duplicates(subset="market_id")
    markets.to_csv(RAW_DIR / "polymarket_markets.csv", index=False)
    print(f"[Polymarket] {len(markets)} Märkte gespeichert")

    histories = []
    for _, row in markets.dropna(subset=["token_id_yes"]).iterrows():
        try:
            h = fetch_price_history(row["token_id_yes"])
            if not h.empty:
                h["market_id"] = row["market_id"]
                h["question"] = row["question"]
                histories.append(h)
        except Exception as e:
            print(f"[WARN] Verlauf für Markt {row['market_id']}: {e}")
        time.sleep(PAUSE)

    if histories:
        pd.concat(histories, ignore_index=True).to_csv(
            RAW_DIR / "polymarket_price_history.csv", index=False
        )
        print(f"[Polymarket] Preisverläufe für {len(histories)} Märkte gespeichert")


if __name__ == "__main__":
    main()
