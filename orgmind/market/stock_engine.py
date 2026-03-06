import random


def generate_candle(company, prev_price):

    if prev_price == 0:
        prev_price = company.share_price

    open_price = prev_price

    # Market fundamentals
    revenue_factor = company.revenue / 50000
    reputation_factor = company.reputation / 10
    debt_penalty = company.technical_debt * 0.4

    movement = (
        revenue_factor * 0.03
        + reputation_factor * 0.02
        - debt_penalty * 0.02
        + random.uniform(-0.04, 0.04)
    )

    close_price = max(0.5, open_price * (1 + movement))

    high = max(open_price, close_price) * random.uniform(1.0, 1.08)
    low = min(open_price, close_price) * random.uniform(0.92, 1.0)

    candle = {
        "open": round(open_price, 2),
        "high": round(high, 2),
        "low": round(low, 2),
        "close": round(close_price, 2)
    }

    company.share_price = close_price
    company.market_cap = close_price * company.total_shares

    return candle