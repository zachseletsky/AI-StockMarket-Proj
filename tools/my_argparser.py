"""
  My arg parser. I use the same cli for most files, so I decided to
    create a class for better reuse and modifications of code in the
    future
"""

import argparse


class My_Argparser:
    def __init__(self, desc="Generic Stock Argparser"):
        self.parser = argparse.ArgumentParser(description=desc)
        self.parser.add_argument(
            "--symbol", required=True, help="Ticker symbol (e.g. MSFT)"
        )
        self.parser.add_argument(
            "--start", required=True, help="Start Date (YYYY-MM-DD)"
        )
        self.parser.add_argument("--end", required=True, help="End Date (YYYY-MM-DD)")

    def get_args(self):
        return self.parser.parse_args()
