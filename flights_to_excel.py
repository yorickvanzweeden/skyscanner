import json

import pandas as pd

from schemas import LegConfig, Offer

with open("data.json") as f:
    data = json.load(f)

with open("config.json") as f:
    config = json.load(f)

timezones = {
    "AUH": "Asia/Dubai",
    "DXB": "Asia/Dubai",
    "AMS": "Europe/Amsterdam",
    "EIN": "Europe/Amsterdam",
    "FRA": "Europe/Berlin",
    "MNL": "Asia/Manila",
    "CEB": "Asia/Manila",
    "CRK": "Asia/Manila",
    "DVO": "Asia/Manila",
    "ILO": "Asia/Manila",
    "KLO": "Asia/Manila",
    "PPS": "Asia/Manila",
    "BCD": "Asia/Manila",
    "SGN": "Asia/Ho_Chi_Minh",
    "HAN": "Asia/Ho_Chi_Minh",
    "PNH": "Asia/Phnom_Penh",
    "KUL": "Asia/Kuala_Lumpur",
    "PEN": "Asia/Kuala_Lumpur",
    "BKK": "Asia/Bangkok",
    "HKT": "Asia/Bangkok",
    "HDY": "Asia/Bangkok",
    "KBV": "Asia/Bangkok",
    "SIN": "Asia/Singapore",
    "BKI": "Asia/Kuala_Lumpur",
}

names = {
    "AUH": "AUH (Abu Dhabi)",
    "DXB": "DBX (Dubai)",
    "AMS": "AMS (Amsterdam)",
    "EIN": "EIN (Eindhoven)",
    "FRA": "FRA (Frankfurt)",
    "MNL": "MNL (Manila)",
    "CEB": "CEB (Cebu)",
    "CRK": "CRK (Clark)",
    "DVO": "DVO (Davao)",
    "ILO": "ILO (Iloilo)",
    "KLO": "KLO (Kalibo)",
    "PPS": "PPS (Puerto Princesa)",
    "BCD": "BCD (Bacolod)",
    "SGN": "SGN (Ho Chi Minh City)",
    "HAN": "HAN (Hanoi)",
    "PNH": "PNH (Phnom Penh)",
    "KUL": "KUL (Kuala Lumpur)",
    "PEN": "PEN (Penang)",
    "BKK": "BKK (Bangkok)",
    "HKT": "HKT (Phuket)",
    "HDY": "HDY (Hat Yai)",
    "KBV": "KBV (Krabi)",
    "SIN": "SIN (Singapore)",
    "BKI": "BKI (Kota Kinabalu)",
}

offers = [Offer(**offer) for offer in data]
df = pd.DataFrame([offer.model_dump() for offer in offers])
legs = [LegConfig(**leg_config) for leg_config in config["legs"]]

# Set start time to correct timezone
df["start_time2"] = df.apply(
    lambda x: x["start_time"].tz_localize(None).tz_localize(timezones[x["start_airport"]]),
    axis=1,
)
df["end_time2"] = df.apply(
    lambda x: x["end_time"].tz_localize(None).tz_localize(timezones[x["end_airport"]]),
    axis=1,
)

# Calculate duration
df["duration"] = df["end_time2"] - df["start_time2"]

# Filter out flights that are too long (> 1 day)
df = df[df["duration"] < pd.Timedelta(hours=22)]

# Format as HH:MM
df["duration"] = df["duration"].apply(
    lambda x: f" {int(x.total_seconds() // 3600)}:{int(x.total_seconds() // 60) % 60}"
)

# Set link
df["link"] = df.apply(
    lambda x: f"https://www.skyscanner.nl/transport/vluchten/{x['start_airport']}/{x['end_airport']}/"
    f"{x['fly_date'].strftime('%y%m%d')}/?adults=2&adultsv2=2&cabinclass=economy&"
    "children=0&childrenv2=&inboundaltsenabled=false&infants=0&originentityid=27536561&"
    "outboundaltsenabled=false&preferdirects=false&ref=home&rtn=0",
    axis=1,
)

# Format start/end time as HH:MM
df["start_time"] = df["start_time"].dt.strftime("%H:%M")
df["end_time"] = df["end_time"].dt.strftime("%H:%M")

# Subset columns
df = df[
    [
        "start_airport",
        "end_airport",
        "fly_date",
        "start_time",
        "end_time",
        "duration",
        "price",
        "stops",
        "link",
    ]
]

with pd.ExcelWriter("output.xlsx") as writer:
    for leg in legs:
        subset = df[df["start_airport"].isin(leg.start_airport) & df["end_airport"].isin(leg.end_airport)].copy()
        # User friendly names
        subset["start_airport"] = subset["start_airport"].apply(lambda x: names[x])
        subset["end_airport"] = subset["end_airport"].apply(lambda x: names[x])

        # Sort by duration
        subset = subset.sort_values(by=["duration"])

        # Remove index
        subset.set_index("start_airport")

        # Write to excel
        sheet_name = "-".join(leg.start_airport) + " --- " + "-".join(leg.end_airport)
        subset.to_excel(writer, sheet_name=sheet_name, index=False)
        worksheet = writer.sheets[sheet_name]
        for column_cells in worksheet.columns:
            length = max(len(str(cell.value)) for cell in column_cells)
            worksheet.column_dimensions[str(column_cells[0].column_letter)].width = min(length + 5, 50)
