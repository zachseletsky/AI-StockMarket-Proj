"""
Used to update raw data based on date of last data update


"""

import datetime
import json
import os
from pathlib import Path
import subprocess
import yfinance as yf

metadata_path = "data-lake/metadata/raw/"
method_path = "data-pipelines/"
init_date = "2015-01-01"


def update_alpaca_news() -> None:
    # format today
    today = datetime.datetime.today().date()
    fToday = f"{today.year}-{today.month:02}-{today.day:02}"
    # open metadata json file
    fp = Path(os.path.join(metadata_path, "news/news-metadata.json"))
    f = fp.open()
    # load json data
    jsonData = json.load(fp=f)
    f.close()
    data = jsonData["data"]

    # load method path
    news_method_path = Path(os.path.join(method_path, "download_alpaca_news.py"))

    update_count = 0

    for i in range(len(data)):
        metadata = data[i]
        symbol = metadata["symbol"]
        last_update = metadata["last_update"]
        if last_update == fToday:
            continue

        if last_update == "":
            last_update = init_date

        args = [symbol, last_update, fToday]
        print(args)
        subprocess.run(
            [
                "python",
                news_method_path,
                "--symbol",
                args[0],
                "--start",
                args[1],
                "--end",
                args[2],
            ],
            check=True,
        )

        # print("Success")
        metadata["last_update"] = fToday
        data[i] = metadata
        update_count += 1

    jsonData["data"] = data
    with fp.open("w") as f:
        json.dump(jsonData, f, indent=2)

    print("News Data updated: " + str(update_count))


def fetch_yahoo_data(ticker: str, start: str, end: str, interval: str = "1d"):
    data = yf.download(ticker, start=start, end=end, interval=interval)
    if data.empty:
        raise ValueError(f"No data returned for {ticker}.")

    out_dir = f"data-lake/raw/equities/{ticker}"
    os.makedirs(out_dir, exist_ok=True)
    out_path = f"{out_dir}/{start}_{end}_{interval}.csv"
    data.to_csv(out_path)
    print(f"[✓] Saved {ticker} data to {out_path}")


def update_equity_data() -> None:
    # format today
    today = datetime.datetime.today().date()
    fToday = f"{today.year}-{today.month:02}-{today.day:02}"
    # open metadata json file
    fp = Path(os.path.join(metadata_path, "equities/equities-metadata.json"))
    f = fp.open()
    # load json data
    jsonData = json.load(fp=f)
    f.close()
    data = jsonData["data"]

    update_count = 0
    # load method path
    for i in range(len(data)):
        metadata = data[i]
        symbol = metadata["symbol"]
        last_update = metadata["last_update"]
        if last_update == fToday:
            continue
        if last_update == "":
            last_update = init_date

        fetch_yahoo_data(symbol, last_update, fToday)

        metadata["last_update"] = fToday
        data[i] = metadata
        update_count += 1

    jsonData["data"] = data
    with fp.open("w") as f:
        json.dump(jsonData, f, indent=2)

    print("Equtity Data updated: " + str(update_count))


if __name__ == "__main__":
    update_alpaca_news()
    update_equity_data()
