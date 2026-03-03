import random

EVENTS = [
    {
        "name": "Competitor Launch",
        "impact": {"reputation": -0.5}
    },
    {
        "name": "Viral Social Media Trend",
        "impact": {"users": 0.10}
    },
    {
        "name": "Tech Infrastructure Issue",
        "impact": {"product_quality": -0.7}
    },
    {
        "name": "Positive Press Coverage",
        "impact": {"reputation": 0.8}
    },
]

def generate_event():
    return random.choice(EVENTS)