import random


def generate_candle(company, prev_price):

    # -----------------------------
    # Starting Price
    # -----------------------------
    if prev_price == 0:
        prev_price = company.share_price

    open_price = prev_price

    # -----------------------------
    # Market Sentiment Factors
    # -----------------------------
    growth_factor = company.revenue / 10000
    reputation_factor = company.reputation / 10
    debt_penalty = company.technical_debt * 0.5

    movement = (
        growth_factor * 0.04
        + reputation_factor * 0.03
        - debt_penalty * 0.03
        + random.uniform(-0.05, 0.05)
    )

    # -----------------------------
    # Close Price
    # -----------------------------
    close_price = max(0.5, open_price * (1 + movement))

    # -----------------------------
    # High / Low Range
    # -----------------------------
    high = max(open_price, close_price) * random.uniform(1.0, 1.12)
    low = min(open_price, close_price) * random.uniform(0.88, 1.0)

    candle = {
        "open": round(open_price, 2),
        "high": round(high, 2),
        "low": round(low, 2),
        "close": round(close_price, 2)
    }

    # -----------------------------
    # Update Market Data
    # -----------------------------
    company.share_price = close_price
    company.market_cap = close_price * company.total_shares

    return candle