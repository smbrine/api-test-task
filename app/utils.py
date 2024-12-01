import datetime
import random
import typing as t

from app import settings

import argparse

def create_args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate-rates", action="store_true")
    parser.add_argument("--upload-rates", action="store_true")
    parser.add_argument("--exit-on-upload", action="store_true")
    parser.add_argument("--generate-rates-from")
    return parser

# Parse arguments once and store them in a global variable
args = create_args_parser().parse_args()

def generate_rates(
    start_from: datetime.date = datetime.date(2000, 1, 1)
) -> t.Dict[str, t.List[t.Dict[str, object]]]:
    rate = {}
    for year in range(start_from.year, 2026):
        for month in range(1, 13):
            for day in range(1, 32):
                try:
                    parsed_date = datetime.date(year, month, day)
                except ValueError:
                    continue
                if parsed_date < start_from:
                    continue
                rate[parsed_date.strftime("%Y-%m-%d")] = [
                    {
                        "rate": random.randint(10, 400) / 10000,
                        "cargo_type": cargo_type,
                    }
                    for cargo_type in settings.CARGO_TYPES.split(";")
                ]

    return rate
