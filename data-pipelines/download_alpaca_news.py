"""
download_alpaca_news.py
=======================

Pull **all** historical Alpaca-Benzinga headlines (2015 → now) for a single
ticker symbol and save them to CSV, while staying below the free-tier
200-request/minute limit.

The script uses the **new** Alpaca SDK (`alpaca-py >= 0.17`) and expects
your API credentials in a local `.env` file:

    APCA_API_KEY_ID=PKXXXXXXXXXXXX
    APCA_API_SECRET_KEY=SKXXXXXXXXXXXX
    APCA_API_BASE_URL=https://paper-api.alpaca.markets   # or omit for live

Install dependencies:

    pip install alpaca-py python-dotenv pandas tqdm

------------------------------------------------------------------------------
Implementation notes
------------------------------------------------------------------------------
*   **Rate-limit guard** – a lightweight decorator sleeps just enough to keep
    aggregate call frequency ≤ 180 req/min (leaves head-room for other code).
*   **Pagination** – Alpaca returns at most 50 headlines per page; we loop
    on `next_page_token` until history is exhausted.
*   **CSV schema** – `id,symbols,created_at,headline,author,url`
"""

from __future__ import annotations

import argparse
import csv
from typing import TextIO
from typing import Iterable
import time
from datetime import datetime
from datetime import timezone
from datetime import timedelta
from pathlib import Path
from typing import Callable
from typing import Tuple

from alpaca.data.historical.news import NewsClient
from alpaca.data.models.news import News
from alpaca.data.requests import NewsRequest
from dotenv import load_dotenv
from tqdm import tqdm

import os
import sys

data_output_path = "data-lake/raw/news/"

last_time: float = time.time()


# ────────────────────────────────────────────────────────────────────────────
# Rate-limit decorator
# ────────────────────────────────────────────────────────────────────────────
def ratelimited(max_calls_per_minute: int = 200) -> Callable:
    """
    Purpose
    -------
    Throttle decorated function so total invocations never exceed
    *max_calls_per_minute*.

    Result
    ------
    Wrapped function sleeps as needed before each call.

    Parameters
    ----------
    max_calls_per_minute : int
        Upper bound for API calls in any 60-second rolling window.
    """
    period = 60.0 / max_calls_per_minute

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            global last_time
            elapsed = time.time() - last_time
            if elapsed < period:
                time.sleep(period - elapsed)
            result = func(*args, **kwargs)
            last_time = time.time()
            return result

        return wrapper

    return decorator


# ────────────────────────────────────────────────────────────────────────────
# Helper functions
# ────────────────────────────────────────────────────────────────────────────
@ratelimited(max_calls_per_minute=180)
def fetch_page(client: NewsClient, req: NewsRequest) -> Tuple[list[News], str | None]:
    """
    Purpose
    -------
    Request one page of headlines from Alpaca.

    Result
    ------
    Returns a tuple *(articles, next_page_token)*.

    Parameters
    ----------
    client : NewsClient
        Authenticated Alpaca NewsClient.
    req : NewsRequest
        Request object (symbol list, date range, limit, page token).
    """
    resp = client.get_news(req)

    # print("resp: " + str(resp))
    # print("\ntoken: " + str(resp.next_page_token))
    return resp.data["news"], resp.next_page_token


def iso8601(dt: datetime) -> str:
    """Return UTC ISO-8601 string with trailing 'Z'."""
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def daterange_chunks(start: datetime, end: datetime, delta: timedelta):
    current = start
    while current < end:
        yield (current, min(current + delta, end))
        current += delta


# --------------------------------- helpers -------------------------------- #
def first_key(d: dict, *candidates):
    """Return the first present key in *candidates* or raise KeyError."""
    for k in candidates:
        if k in d:
            return d[k]
    raise KeyError(f"None of {candidates} in dict")


# -------------------------------------------------------------------------- #


def dump_rows(rows: Iterable[list[str]], fh: TextIO) -> None:
    writer = csv.writer(fh)
    writer.writerows(rows)


def save_rows(news: list[News], fh: TextIO) -> int:
    """
    Parameters
    ----------
    news: list[News]

    Returns
    -------
    int
        List of formated lists of string values
        Number of rows written (for the progress bar).
    """
    news_rows = []

    for d in news:
        # print("\nDType: " + str(type(d)) + "\n D: \n" + str(d))
        news_rows.append(
            [
                d.id,
                d.created_at.isoformat().replace("+00:00", "Z"),
                d.headline.replace("\n", " ").replace(",", "-"),
                d.source,
                ";".join(d.symbols),
                d.updated_at,
                d.url,
            ]
        )

    dump_rows(news_rows, fh)

    return len(news)


# ────────────────────────────────────────────────────────────────────────────
# Main driver
# ────────────────────────────────────────────────────────────────────────────
def main() -> None:
    """
    Parse CLI args, iterate through pages from 2015-01-01 00:00Z to *now*,
    and write output CSV.  Progress shown via tqdm bar.
    """
    parser = argparse.ArgumentParser(
        description="Download Alpaca Benzinga headlines for one ticker"
    )
    parser.add_argument("--symbol", required=True, help="Ticker symbol (e.g. MSFT)")
    parser.add_argument("--start", required=True, help="Start Date (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="End Date (YYYY-MM-DD)")
    # parser.add_argument(
    #     "--out",
    #     required=True,
    #     type=Path,
    #     help="Destination CSV path (will be created)",
    # )
    args = parser.parse_args()

    load_dotenv(".env")  # reads .env

    API_KEY = os.getenv("APCA_API_KEY_ID")
    SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
    # BASE_URL =
    # os.getenv("APCA_API_BASE_URL", "https://paper-api.alpaca.markets")

    if not API_KEY or not SECRET_KEY:
        sys.exit("❌  Missing APCA_API_KEY_ID or APCA_API_SECRET_KEY in environment")

    client = NewsClient(
        api_key=API_KEY, secret_key=SECRET_KEY
    )  # picks up creds + base URL from env

    # start_dt = datetime(2015, 1, 1, tzinfo=timezone.utc)
    # end_dt = datetime.now(timezone.utc)

    # prepare CSV write-path
    full_path = Path(
        data_output_path
        + "/"
        + args.symbol
        + "/"
        + args.start
        + "_"
        + args.end
        + ".csv"
    )

    # set date range
    start_str = args.start.strip()
    end_str = args.end.strip()
    start_dt = datetime(
        int(start_str[0:4]),
        int(start_str[5:7]),
        int(start_str[8:10]),
        tzinfo=timezone.utc,
    )
    end_dt = datetime(
        int(end_str[0:4]), int(end_str[5:7]), int(end_str[8:10]), tzinfo=timezone.utc
    )

    full_path.touch(exist_ok=True)
    with full_path.open("w", newline="", encoding="utf-8") as fp:
        header = [
            ["id", "created_at", "headline", "source", "symbols", "updated_at", "url"]
        ]
        dump_rows(header, fp)

        pbar = tqdm(desc=f"News {args.symbol}", unit=" article")

        for chunk_start, chunk_end in daterange_chunks(
            start_dt, end_dt, timedelta(days=1)
        ):
            print(f"[INFO] Fetching {chunk_start.date()} to {chunk_end.date()}")
            req = NewsRequest(
                symbols=args.symbol,
                start=chunk_start,
                end=chunk_end,
                limit=50,  # server max
                sort="desc",
            )

            articles, _ = fetch_page(client, req)

            if articles:
                save_rows(articles, fp)
                pbar.update(len(articles))

            time.sleep(0.35)  # Stay well under 200 req/min

    print(f"✔ Saved {pbar.n} headlines → {full_path.name}")


# ────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
