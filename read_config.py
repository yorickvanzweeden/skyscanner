import itertools
import json
from datetime import timedelta

from schemas import LegConfig, LegOption, Offer


def get_permutations(leg: LegConfig) -> list[LegOption]:
    # Get all days between start and end date (inclusive)
    days = [leg.start_date + timedelta(days=x) for x in range((leg.end_date - leg.start_date).days + 1)]

    # Get all permutations of start and end airports using itertools
    combinations = itertools.product(leg.start_airport, leg.end_airport, days)

    # Convert to list of LegOption objects
    return [LegOption(start_airport=comb[0], end_airport=comb[1], fly_date=comb[2]) for comb in combinations]


def read_config() -> list[LegOption]:
    with open("config.json") as f:
        data = json.load(f)

    legs = [LegConfig.model_validate(leg) for leg in data["legs"]]
    leg_options = [get_permutations(leg) for leg in legs]

    return [leg for leg_option in leg_options for leg in leg_option]


def load_data() -> list[Offer]:
    leg_options = [Offer(**leg.model_dump()) for leg in read_config()]

    try:
        with open("data.json") as f:
            data = json.load(f)
        offers = [Offer(**offer) for offer in data]
        if len(offers) != len(leg_options):
            offers_simple = [(o.start_airport, o.end_airport, o.fly_date) for o in offers]
            options_simple = [(o.start_airport, o.end_airport, o.fly_date) for o in leg_options]
            missing_indices = [i for i, o in enumerate(options_simple) if o not in offers_simple]
            offers += [leg_options[i] for i in missing_indices]
            with open("data.json", "w") as f:
                json.dump(
                    [json.loads(offer.model_dump_json()) for offer in offers],
                    f,
                    indent=4,
                )
        return offers
    except FileNotFoundError:
        with open("data.json", "w") as f:
            json.dump(
                [json.loads(offer.model_dump_json()) for offer in leg_options],
                f,
                indent=4,
            )
        return leg_options


def save_data(data: list[Offer]) -> None:
    with open("data.json", "w") as f:
        json.dump([json.loads(offer.model_dump_json()) for offer in data], f, indent=4)
