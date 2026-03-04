import random


def generate_candle(company, prev_price):

    if prev_price == 0:
        prev_price = company.share_price

    growth_factor = company.revenue / 10000
    reputation_factor = company.reputation / 10
    debt_penalty = company.technical_debt * 0.5

    movement = (
        growth_factor * 0.05
        + reputation_factor * 0.03
        - debt_penalty * 0.04
        + random.uniform(-0.05, 0.05)
    )

    close = max(1, prev_price * (1 + movement))

    high = close * random.uniform(1.01, 1.1)
    low = close * random.uniform(0.9, 0.99)

    open_price = prev_price

    candle = {
        "open": round(open_price, 2),
        "high": round(high, 2),
        "low": round(low, 2),
        "close": round(close, 2)
    }

    company.share_price = close
    company.market_cap = close * company.total_shares

    return candle