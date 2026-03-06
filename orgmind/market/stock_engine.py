import random


def generate_candle(company, prev_price):

    if prev_price == 0:
        prev_price = company.share_price

    open_price = prev_price

    # --------------------------------
    # Market fundamentals influence
    # --------------------------------

    revenue_factor = company.revenue / 50000
    reputation_factor = company.reputation / 10
    debt_penalty = company.technical_debt * 0.4

    movement = (
        revenue_factor * 0.018
        + reputation_factor * 0.012
        - debt_penalty * 0.02
        + random.uniform(-0.015, 0.015)
    )

    # Clamp extreme moves (±18%)
    movement = max(-0.12, min(0.18, movement))

    close_price = max(0.5, open_price * (1 + movement))

    # --------------------------------
    # Realistic high/low ranges
    # --------------------------------

    high = round(max(open_price, close_price) * random.uniform(1.03, 1.15), 2)
    low = round(min(open_price, close_price) * random.uniform(0.90, 0.98), 2)

    candle = {
        "open": round(open_price, 2),
        "high": high,
        "low": low,
        "close": round(close_price, 2)
    }

    # Update company market values
    company.share_price = close_price
    company.market_cap = close_price * company.total_shares

    return candle