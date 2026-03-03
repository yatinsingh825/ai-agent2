class Company:
    def __init__(self, config):
        self.month = 1
        self.revenue = config.INITIAL_REVENUE
        self.cash = config.INITIAL_CASH
        self.users = config.INITIAL_USERS
        self.burn_rate = config.INITIAL_BURN
        self.product_quality = config.INITIAL_PRODUCT_QUALITY
        self.reputation = config.INITIAL_REPUTATION
        self.technical_debt = 0.0

    def runway(self):
        if self.burn_rate == 0:
            return float("inf")
        return round(self.cash / self.burn_rate, 2)

    def summary(self):
        return {
            "month": self.month,
            "revenue": self.revenue,
            "cash": self.cash,
            "users": self.users,
            "burn_rate": self.burn_rate,
            "runway_months": self.runway(),
            "product_quality": self.product_quality,
            "reputation": self.reputation,
            "technical_debt": self.technical_debt,
        }