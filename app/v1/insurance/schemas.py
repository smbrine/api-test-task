import datetime
import typing as t

from pydantic import BaseModel


class Rate(BaseModel):
    cargo_type: str
    rate: float


class DeleteInsuranceRatePayload(BaseModel):
    date: datetime.date
    cargo_types: t.Optional[t.List[str]] = None


class UpdateInsuranceRatePayload(Rate):
    date: datetime.date


class AddInsuranceRatePayload(BaseModel):
    date: datetime.date
    rates: t.List[Rate]
