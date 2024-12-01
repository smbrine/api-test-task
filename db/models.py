import typing as t
from datetime import date

from sqlalchemy import (
    Column,
    Date,
    Integer,
    Float,
    String,
    ForeignKey,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, joinedload

Base = declarative_base()


class RatePeriod(Base):
    __tablename__ = "rate_periods"
    id = Column(Integer, primary_key=True, autoincrement=True)
    applicable_date = Column(Date, nullable=False, unique=True)

    rate_details = relationship(
        "RateDetail",
        back_populates="rate_period",
        cascade="all, delete-orphan",
        uselist=True,
        lazy="joined",
    )

    @classmethod
    async def create_rate_period_with_details(
        cls,
        session: AsyncSession,
        applicable_date: date,
        rate_details: t.List[t.Dict[str, t.Union[str, float]]],
    ) -> None:
        """
        Create a RatePeriod with associated RateDetail records atomically.

        :param session: The database session.
        :param applicable_date: The date for the rate period.
        :param rate_details: A list of rate details.

        :raises ValueError: If the rate period for the date already exists.
        """
        # Check if a RatePeriod already exists for the date
        existing = await session.execute(
            select(cls).filter_by(applicable_date=applicable_date)
        )
        if existing.scalar():
            raise ValueError(
                f"RatePeriod for date {applicable_date} already exists."
            )

        rate_period = cls(applicable_date=applicable_date)
        session.add(rate_period)

        for detail in rate_details:
            rate_period.rate_details.append(RateDetail(**detail))

    @classmethod
    async def get_rates_for_date(
        cls, session: AsyncSession, applicable_date: date
    ):
        """
        Returns a list of rates for specified date

        :param session: Async database session
        :param applicable_date: Date to search for
        :return:
        """
        result = await session.execute(
            select(cls)
            .options(joinedload(cls.rate_details))
            .filter_by(applicable_date=applicable_date)
        )
        return result.scalars().unique().one_or_none()

    @classmethod
    async def update_rate(
        cls,
        session: AsyncSession,
        applicable_date: date,
        cargo_type: str,
        rate: float,
    ) -> None:
        """
        Updates a rate for specific cargo at specific date
        :param session: Async database session
        :param applicable_date: Date to update
        :param cargo_type: Cargo type to update
        :param rate: New rate
        """
        period_in_db = (
            (
                await session.execute(
                    select(cls)
                    .options(joinedload(cls.rate_details))
                    .filter_by(applicable_date=applicable_date)
                )
            )
            .unique()
            .scalar_one_or_none()
        )

        if not period_in_db:
            await cls.create_rate_period_with_details(
                session, applicable_date, [{cargo_type: rate}]
            )
            return

        for detail in period_in_db.rate_details:
            if detail.cargo_type == cargo_type:
                detail.rate = rate
                break
        else:
            new_detail = RateDetail(
                rate=rate,
                cargo_type=cargo_type,
                rate_period_id=period_in_db.id,
            )
            period_in_db.rate_details.append(new_detail)

    @classmethod
    async def remove_rates(
        cls,
        session: AsyncSession,
        applicable_date: date,
        cargo_types: t.Optional[t.List[str]] = None,
    ):
        """
        Removes specified rates or the whole date's record
        :param session: Async database session
        :param applicable_date: Date to remove
        :param cargo_types: Cargo types to remove
        """
        period_in_db = (
            (
                await session.execute(
                    select(cls)
                    .options(joinedload(cls.rate_details))
                    .filter_by(applicable_date=applicable_date)
                )
            )
            .unique()
            .scalar_one_or_none()
        )

        if not period_in_db:
            raise ValueError(
                f"No rate period found for "
                f"the given applicable_date: {applicable_date}"
            )

        if not cargo_types:
            return await session.delete(period_in_db)

        period_in_db.rate_details = [
            detail
            for detail in period_in_db.rate_details
            if detail.cargo_type not in cargo_types
        ]

        if not period_in_db.rate_details:
            await session.delete(period_in_db)


class RateDetail(Base):
    __tablename__ = "rate_details"
    id = Column(Integer, primary_key=True, autoincrement=True)
    rate = Column(Float, nullable=False)
    cargo_type = Column(String, nullable=False)
    rate_period_id = Column(
        Integer, ForeignKey("rate_periods.id"), nullable=False
    )

    rate_period = relationship("RatePeriod", back_populates="rate_details")
