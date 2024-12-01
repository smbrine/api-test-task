"""
App's main module
"""

import contextlib
import datetime
import json
import os
import pathlib
import sys
from datetime import date

import uvicorn
from fastapi import FastAPI

from app import settings
from app.utils import generate_rates
from app.v1 import router as v1_router
from db import models
from db.main import sessionmanager
from app.utils import args


@contextlib.asynccontextmanager
async def lifespan(fastapi_app: FastAPI):

    async with sessionmanager.engine(
        settings.POSTGRES_ENDPOINT,
        settings.DEBUG
    ):
        yield


app = FastAPI(root_path="/api", lifespan=lifespan, version=settings.APP_VERSION)

app.include_router(v1_router)


async def main() -> int:
    raw_start_from = args.generate_rates_from or "2024-01-01"
    try:
        start_from = datetime.datetime.strptime(
            raw_start_from, "%Y-%m-%d"
        ).date()
    except ValueError:
        start_from = datetime.date(2024, 1, 1)

    if args.generate_rates:
        with open("rates.json", "w", encoding="utf-8") as f:
            json.dump(generate_rates(start_from), f, ensure_ascii=False)

    rates_path = pathlib.Path("rates.json")

    if rates_path.exists():
        with open(rates_path, "r", encoding="utf-8") as f:
            raw_rates = json.load(f)
    else:
        raw_rates = generate_rates(start_from)

    if args.upload_rates:
        async with sessionmanager.engine(
        settings.POSTGRES_ENDPOINT,
        settings.DEBUG
        ):
            async with sessionmanager.session() as session:
                for date_str, rates in raw_rates.items():
                    applicable_date = date.fromisoformat(date_str)
                    rate_details = [
                        {
                            "rate": rate["rate"],
                            "cargo_type": rate["cargo_type"],
                        }
                        for rate in rates
                    ]

                    try:
                        await models.RatePeriod.create_rate_period_with_details(
                            session, applicable_date, rate_details
                        )
                    except ValueError:
                        pass
    if args.exit_on_upload:
        exit(0)
    return 0


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
    uvicorn.run(
        "app.main:app",
        host=settings.BIND_HOST,
        port=settings.BIND_PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )
