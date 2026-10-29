# Datenbasierte Aktienprognose mit Kaufempfehlung

Rohdaten-Beschaffung für das Projekt (Yahoo Finance + Polymarket).

## Setup
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Nutzung
Ticker und Suchbegriffe in `src/config.py` anpassen, dann:
```bash
python src/main.py               # alles
python src/fetch_yahoo.py        # nur Yahoo Finance
python src/fetch_polymarket.py   # nur Polymarket
```

## Ausgabe (`data/raw/`, nicht im Git)
| Datei | Inhalt |
|---|---|
| `prices_<TICKER>.csv` | Kurshistorie (OHLCV) |
| `fundamentals.csv` | KGV, PEG, ROE, Beta, Analystenkursziel usw. |
| `polymarket_markets.csv` | Märkte + aktuelle Wahrscheinlichkeit |
| `polymarket_price_history.csv` | Wahrscheinlichkeits-Zeitreihen |

## Hinweise
- `yfinance` ist eine inoffizielle Schnittstelle; Felder können fehlen (`None`) oder sich ändern.
- Yahoo liefert `freeCashflow`, nicht exakt "Levered Free Cashflow" – im Bericht als Näherung kennzeichnen.
- Polymarket-APIs sind öffentlich und lesend ohne Key nutzbar; Nutzungsbedingungen beachten.
