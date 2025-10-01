# scripts/scrape_senators.py
import argparse
from app.scrapers.aph import fetch_senators, to_dataframe, export_excel

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", help="State code (e.g., WA, NSW, VIC). If omitted, fetch AU (limited by MAX_BATCH).")
    ap.add_argument("--out", default="senators.xlsx")
    args = ap.parse_args()

    rows = fetch_senators(state=args.state)
    df = to_dataframe(rows)
    p = export_excel(df, args.out)
    print(f"Saved {len(df)} records to {p}")

if __name__ == "__main__":
    main()
