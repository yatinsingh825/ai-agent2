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
        "impact": {"reputation": -0.4},
        "weight": 22
    },
    {
        "name": "Tech Infrastructure Issue",
        "impact": {"product_quality": -0.7},
        "weight": 15
    },
    {
        "name": "Regulatory Tailwind",
        "impact": {"reputation": 0.4, "users": 0.05},
        "weight": 8
    }
]


def generate_event():
    """
    Select a market event using weighted probability.
    """

    total_weight = sum(event["weight"] for event in EVENTS)
    roll = random.uniform(0, total_weight)

    cumulative = 0

    for event in EVENTS:
        cumulative += event["weight"]

        if roll <= cumulative:
            return event

    # fallback (should never happen)
    return EVENTS[0]