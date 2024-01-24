import datetime

from pydantic import BaseModel


class LegConfig(BaseModel):
    start_airport: list[str]
    end_airport: list[str]
    start_date: datetime.datetime
    end_date: datetime.datetime


class LegOption(BaseModel):
    start_airport: str
    end_airport: str
    fly_date: datetime.datetime


class MultiCityPlan(BaseModel):
    legs: list[LegOption]

    # Validate that the legs are in order
    @classmethod
    def model_validate(cls, v):  # type: ignore[no-untyped-def]
        legs = v["legs"]
        legs.sort(key=lambda x: x["fly_date"])
        return cls(legs=legs)

    # Validate that the legs do not fly on the same day
    @classmethod
    def validate(cls, v):  # type: ignore[no-untyped-def]
        fly_dates = [leg.fly_date for leg in v["legs"]]
        if len(fly_dates) != len(set(fly_dates)):
            raise ValueError("Legs cannot fly on the same day")
        return v


class Offer(LegOption):
    price: float | None = None
    stops: int | None = None
    start_time: datetime.datetime | None = None
    end_time: datetime.datetime | None = None
