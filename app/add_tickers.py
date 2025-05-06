"""
Used to add new tickers to metadata to allow update_raw_data.py to get new data for em


"""

import json
from pathlib import Path
import argparse
import subprocess

metadata_path = "data-lake/metadata"
metadata_raw_path = metadata_path + "/raw/"

metadata_proc_path = metadata_path + "/processed/"
metadata_tag = "-metadata.json"

file_order = ["equities", "news", "merged"]


def add_ticker(ticker: str) -> None:
    ticker = ticker.strip()
    # setup paths
    md_raw_equities_path = Path(metadata_raw_path + "equities" + metadata_tag)
    md_raw_news_path = Path(metadata_raw_path + "news" + metadata_tag)
    md_proc_merg_path = Path(metadata_proc_path + "merged" + metadata_tag)
    # eventually add paths to more data types here
    paths = [md_raw_equities_path, md_raw_news_path, md_proc_merg_path]

    # load files
    md_files = []
    for path in paths:
        with path.open() as fp:
            md_files.append(json.load(fp))

    # load data from files
    md_data = []
    for md_file in md_files:
        md_data.append(md_file["data"])

    # update data
    file_count = 0
    for data in md_data:
        exists = False
        # confirm ticker does not already exist
        for entry in data:
            if entry["symbol"] == ticker:
                print(
                    "Ticker $"
                    + ticker
                    + "$ already exists in metadata file: "
                    + file_order[file_count]
                )
                exists = True
                break
        # add ticker to data if it doesnt already exist
        if not exists:
            data.append({"symbol": ticker, "last_update": ""})
            md_files[file_count]["data"] = data
            # save data back to file
            with paths[file_count].open("w") as fp:
                json.dump(md_files[file_count], fp, indent=2)
        # increment file count
        file_count += 1


def main() -> None:
    # instantiate argparser
    parser = argparse.ArgumentParser(description="Enter Symbols to add to index")
    # nargs=+ enables multiple tickers to be included in the arg call
    parser.add_argument(
        "--symbols", required=True, nargs="+", help="Ticker symbol (e.g. MSFT)"
    )
    parser.add_argument(
        "-u",
        "--update",
        action="store_true",
        default=False,
        required=False,
        help="Request update to data-lake including new ticker",
    )
    # get args
    args = parser.parse_args()

    tickers: list[str] = args.symbols
    update: bool = args.update

    for ticker in tickers:
        if not ticker or len(ticker) > 4:
            # raise Exception("Invalid ticker: " + ticker)
            print("Invalid Ticker: " + ticker + "\nSkipping to next Ticker")
            continue
        # add ticker to metadata
        add_ticker(ticker)

    # if requested, run update_raw_data.py to update data
    if update:
        subprocess.run(["python", "app/update_raw_data.py"])


if __name__ == "__main__":
    main()
