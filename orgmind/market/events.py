import random

EVENTS = [
    {
        "name": "Positive Press Coverage",
        "impact": {"reputation": 0.8},
        "weight": 30
    },
    {
        "name": "Viral Social Media Trend",
        "impact": {"users": 0.10},
        "weight": 25
    },
    {
        "name": "Competitor Launch",
        "impact": {"reputation": -0.5},
        "weight": 25
    },
    {
        "name": "Tech Infrastructure Issue",
        "impact": {"product_quality": -0.7},
        "weight": 20
    },
]


def generate_event():

    weights = [event["weight"] for event in EVENTS]

    chosen_event = random.choices(
        EVENTS,
        weights=weights,
        k=1
    )[0]

    return chosen_event