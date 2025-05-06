"""
  merges news and equities data into single json file with objects
  in the following format:
  { "data":[
    {"TICK": {
      "data-date":"MM-DD-YYY",
      "open":#,
      "high":#,
      "low":#,
      "close":#,
      "volume":#,
      "headlines":["",""]
      }
    }
    ]
  }

  FYI: stock market hours 9am-4pm ET => 09:00-16:00 + 4hrs => 13:00-20:00 UTC
  so cutoff time is 20:00
  """

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from datetime import timedelta
from datetime import time
from datetime import date
import os
import argparse

# data directories
raw_dir = "data-lake/raw"
equities_dir = "/equities/"
news_dir = "/news/"
out_dir = "data-lake/processed/"


# ensures news data is aligned so news data from day x is associated with
#   news equity data from day x + 1. IE only headlines available at the
#   by the end of the trading day are associated with that trading day
#
#   Market closes at 4pm, so day x includes headlines from x-1 @4:00pm to day
#       x @3:59pm
def compare_times(d: date, t: time, cutoff: time) -> str:
    f_date: datetime = datetime.combine(d, time(0, 0, 0))
    if datetime.combine(d, t) - datetime.combine(d, cutoff) >= timedelta(0, 0):
        f_date += timedelta(days=1)
    if f_date.weekday() == 5:
        d += timedelta(days=1)
    if f_date.weekday() == 6:
        f_date += timedelta(days=1)

    r = f_date.date().isoformat()
    return r


def save_to_json(ticker: str, data: list) -> None:
    pathname = out_dir + ticker + "_data.json"
    if os.path.exists(pathname):
        with Path(pathname).open("r") as fp:
            curr_obj: dict = json.load(fp)
            curr_data: list = curr_obj["data"]

        curr_data.extend(data)
        curr_obj["data"] = curr_data
    else:
        curr_obj = {"TICK": ticker, "data": data}

    with Path(pathname).open("w") as fp:
        json.dump(curr_obj, fp, indent=2)


# Sorts news headlines by date only, where date x includes all news
# headlines released after close the day before (4:00pm ET x-1)
# until close the day of (4:00pm ET x).
def sort_news_dates(news_df: pd.DataFrame, data_df: pd.DataFrame) -> list:
    dates = data_df["date"]

    iso_dates = pd.DataFrame(data=pd.to_datetime(news_df["created_at"], utc=True))

    datetime_df = pd.DataFrame(
        {
            "date": iso_dates["created_at"].dt.date,
            "time": iso_dates["created_at"].dt.time,
            "headlines": news_df["headline"],
        }
    )
    # print("Data: \n" + datetime_df.to_string())
    cutoff_time = time(20, 0, 0)
    proper_dates = []
    date_headline_objs: dict = {}
    for _, r in datetime_df.iterrows():
        d = r.iloc[0]
        t = r.iloc[1]
        h = r.iloc[2]
        if type(h) is str:
            continue

        true_date = compare_times(d, t, cutoff_time)
        # print("tdate: " + true_date)

        if true_date in date_headline_objs.keys():
            # print("curr: " + str(date_headline_objs[true_date]))
            tHs = date_headline_objs[true_date]
            tHs.append(h)
            date_headline_objs[true_date] = tHs
        else:
            date_headline_objs[true_date] = [h]
            # print("dho: " + str(date_headline_objs[true_date]))
        proper_dates.append(true_date)

    list_of_dicts = []
    for i in range(len(dates)):
        row = data_df.iloc[i]
        print("row: \n" + str(row))
        date = row[0]
        open = row[1]
        high = row[2]
        low = row[3]
        close = row[4]
        vol = row[5]
        headlines: list[str] = []
        if date in date_headline_objs.keys():
            headlines = date_headline_objs[date]

        list_of_dicts.append(
            {
                "date": date,
                "o": open,
                "h": high,
                "l": low,
                "c": close,
                "v": vol,
                "headlines": headlines,
            }
        )

    return list_of_dicts


def load_dataframes(
    ticker: str, start: str, end: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    daterange = start + "_" + end

    news_path = raw_dir + news_dir + ticker + "/" + daterange + ".csv"
    equities_path = raw_dir + equities_dir + ticker + "/" + daterange + "_1d.csv"

    if not os.path.exists(news_path):
        raise Exception(
            "News Data does not exist. Filename " + news_path + " not found"
        )
    if not os.path.exists(equities_path):
        raise Exception(
            "Equities Data does not exist. Filename " + equities_path + " not found"
        )

    news_df = pd.read_csv(news_path)
    equities_df = pd.read_csv(equities_path)

    equities_df = equities_df.drop(index=[0, 1, 2])
    equities_df.columns = ["date", "close", "high", "low", "open", "volume"]

    return (news_df, equities_df)


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge news headlines and ohclv data")
    parser.add_argument("--symbol", required=True, help="Ticker symbol (e.g. MSFT)")
    parser.add_argument("--start", required=True, help="Start Date (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="End Date (YYYY-MM-DD)")

    args = parser.parse_args()
    ticker = args.symbol
    start_date = args.start
    end_date = args.end

    news_df, equities_df = load_dataframes(ticker, start_date, end_date)
    data = sort_news_dates(news_df, equities_df)
    save_to_json(ticker, data)


if __name__ == "__main__":
    main()
