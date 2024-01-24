import datetime
import random

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from read_config import load_data, save_data
from schemas import Offer

app = FastAPI()
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
storage = load_data()


@app.get("/legoption/")
async def read_leg_option() -> JSONResponse | Offer:
    """Fetch first uncalculated leg option"""
    non_calculated_leg_options = [option for option in storage if option.price is None]

    # Check if all options have a price --> if so, return 404
    if not non_calculated_leg_options:
        return JSONResponse(content="No non-calculated LegOptions found!", status_code=404)

    # Pick random LegOption that has not been calculated yet
    return random.choice(non_calculated_leg_options)


@app.get("/legoption_submit/")
async def create_leg_option(
    start_airport: str,
    end_airport: str,
    fly_date: datetime.datetime,
    price: float,
    stops: int,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
) -> int | JSONResponse:
    """Create leg option"""
    # Get item in storage
    items = [
        item
        for item in storage
        if item.start_airport == start_airport
        and item.end_airport == end_airport
        and item.fly_date.date() == fly_date.date()
    ]
    if len(items) == 0:
        return JSONResponse(content="LegOption doesn't exist", status_code=404)

    item = items[0]
    item.price = price
    item.stops = stops
    item.start_time = start_time
    item.end_time = end_time
    save_data(storage)
    return 200


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
