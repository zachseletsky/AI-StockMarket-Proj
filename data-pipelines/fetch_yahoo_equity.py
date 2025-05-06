"""Fetch daily Yahoo! equity data and store it in data‑lake/raw.

Part of the AI‑StockMarket‑Proj ETL pipeline.
"""

import yfinance as yf
import os
import argparse


def fetch_yahoo_data(ticker: str, start: str, end: str, interval: str = "1d"):
    data = yf.download(ticker, start=start, end=end, interval=interval)
    if data.empty:
        raise ValueError(f"No data returned for {ticker}.")

    out_dir = f"data-lake/raw/equities/{ticker}"
    os.makedirs(out_dir, exist_ok=True)
    out_path = f"{out_dir}/{start}_{end}_{interval}.csv"
    data.to_csv(out_path)
    print(f"[✓] Saved {ticker} data to {out_path}")


def cli() -> None:
    while True:
        ticker = input("\nEnter Ticker: ").strip()
        start_date = input("Enter Start Date (YYYY-MM-DD): ").strip()
        end_date = input("Enter End Date (YYYY-MM-DD): ").strip()
        fetch_yahoo_data(ticker, start_date, end_date)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download YFinance OHLCV for one ticker"
    )
    parser.add_argument("--symbol", required=True, help="Ticker symbol (e.g. MSFT)")
    parser.add_argument("--start", required=True, help="Start Date (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="End Date (YYYY-MM-DD)")
    args = parser.parse_args()

    # set date range
    start_str = args.start.strip()
    end_str = args.end.strip()

    fetch_yahoo_data(ticker=args.symbol, start=start_str, end=end_str)


if __name__ == "__main__":
    main()
