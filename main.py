"""Startet beide Rohdaten-Abrufe nacheinander."""
import fetch_polymarket
import fetch_yahoo

if __name__ == "__main__":
    fetch_yahoo.main()
    fetch_polymarket.main()
    print("Fertig. Rohdaten liegen in data/raw/")
