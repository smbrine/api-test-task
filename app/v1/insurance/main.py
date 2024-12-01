"""
Insurance main module
"""

import datetime
from fastapi import APIRouter, HTTPException
from starlette.responses import JSONResponse

from app.v1.insurance import schemas
from db.main import sessionmanager
from db import models

router = APIRouter(prefix="/insurance")


@router.get("/price")
async def handle_get_v1_insurance_price(
    declared_value: float,
    cargo_type: str = "Other",
    date: str = datetime.date.today().strftime("%Y-%m-%d"),
) -> JSONResponse:
    """
    Calculate the insurance price for a specified cargo type, value, and date.

    :param declared_value: The declared value of the cargo.\n
    :param cargo_type: The type of cargo. Defaults to 'Other'.\n
    :param date: The date for which to calculate the insurance.\n

    :return float: The calculated insurance price for the cargo.
    """
    try:
        parsed_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError as e:
        raise HTTPException(400, "Invalid date format") from e
    async with sessionmanager.session() as session:
        if (
            rate_period_in_db := await models.RatePeriod.get_rates_for_date(
                session, parsed_date
            )
        ) is None:
            raise HTTPException(
                404,
                f"Could not find rate for {cargo_type} at {parsed_date}",
            )
        for detail in rate_period_in_db.rate_details:
            if detail.cargo_type == cargo_type:
                return JSONResponse(
                    {"insurance_cost": detail.rate * declared_value}, 200
                )
    raise HTTPException(500, "Could not correctly process request")


@router.get("/rate")
async def handle_get_v1_insurance_rate(
    date: str = datetime.date.today().strftime("%Y-%m-%d"),
):
    try:
        parsed_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError as e:
        raise HTTPException(400, "Invalid date format") from e
    async with sessionmanager.session() as session:
        if (
            rate_period_in_db := await models.RatePeriod.get_rates_for_date(
                session, parsed_date
            )
        ) is None:
            raise HTTPException(
                404, f"Could not find rate for {parsed_date}"
            )
        return JSONResponse(
            {
                "rates": [
                    {"cargo_type": d.cargo_type, "rate": d.rate}
                    for d in rate_period_in_db.rate_details
                ]
            },
            200,
        )


@router.patch("/rate")
async def handle_patch_v1_insurance_rate(
    payload: schemas.UpdateInsuranceRatePayload,
):
    async with sessionmanager.session() as session:
        await models.RatePeriod.update_rate(
            session, payload.date, payload.cargo_type, payload.rate
        )
    return JSONResponse({"message": "ok"}, 200)


@router.post("/rate")
async def handle_post_v1_insurance_rate(
    payload: schemas.AddInsuranceRatePayload,
):
    async with sessionmanager.session() as session:
        try:
            await models.RatePeriod.create_rate_period_with_details(
                session, payload.date, payload.rates
            )
        except ValueError as e:
            raise HTTPException(409) from e
    return JSONResponse({"message": "ok"}, 200)


@router.delete("/rate", status_code=204)
async def handle_delete_v1_insurance_rate(
    payload: schemas.DeleteInsuranceRatePayload,
):
    async with sessionmanager.session() as session:
        await models.RatePeriod.remove_rates(
            session, payload.date, payload.cargo_types
        )
