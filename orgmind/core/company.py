class Company:

    def __init__(self, config):

        # -----------------------------
        # Time
        # -----------------------------
        self.month = 1

        # -----------------------------
        # Core Metrics
        # -----------------------------
        self.revenue = config.INITIAL_REVENUE
        self.cash = config.INITIAL_CASH
        self.users = config.INITIAL_USERS

        # Track previous metrics for growth calculations
        self.prev_users = self.users
        self.prev_revenue = self.revenue

        # -----------------------------
        # Startup Cost Structure
        # -----------------------------
        self.engineers = 3
        self.marketing_budget = 2000
        self.infra_cost = 1000
        self.operations_cost = 2000

        self.burn_rate = 0

        # -----------------------------
        # Product Metrics
        # -----------------------------
        self.product_quality = config.INITIAL_PRODUCT_QUALITY
        self.reputation = config.INITIAL_REPUTATION
        self.technical_debt = 0.0

        # -----------------------------
        # Company Value
        # -----------------------------
        self.valuation = 0
        self.total_shares = 1_000_000
        self.founder_ownership = 1.0
        self.last_funding_round = None
        self.months_since_funding = 12

        # -----------------------------
        # Public Market Data
        # -----------------------------
        self.is_public = False
        self.share_price = 0
        self.market_cap = 0

        # -----------------------------
        # Revenue Model
        # -----------------------------
        self.arpu = 18

        # -----------------------------
        # Company Status
        # -----------------------------
        self.bankrupt = False

        # -----------------------------
        # Initial Burn Calculation
        # -----------------------------
        self.burn_rate = self.calculate_burn()

    # -----------------------------
    # Burn Rate Calculation
    # -----------------------------
    def calculate_burn(self):

        engineering_cost = self.engineers * 4000
        marketing_cost = self.marketing_budget
        infra_cost = self.infra_cost
        ops_cost = self.operations_cost

        burn = (
            engineering_cost
            + marketing_cost
            + infra_cost
            + ops_cost
        )

        burn = max(0, burn)

        return burn

    # -----------------------------
    # Runway Calculation
    # -----------------------------
    def runway(self):

        if self.burn_rate <= 0:
            return float("inf")

        runway = self.cash / self.burn_rate

        return round(runway, 2)

    # -----------------------------
    # Company Summary
    # -----------------------------
    def summary(self):

        return {
            "month": self.month,
            "revenue": self.revenue,
            "cash": self.cash,
            "users": self.users,

            "burn_rate": self.burn_rate,
            "runway_months": self.runway(),

            "engineers": self.engineers,
            "marketing_budget": self.marketing_budget,
            "infra_cost": self.infra_cost,
            "operations_cost": self.operations_cost,

            "product_quality": self.product_quality,
            "reputation": self.reputation,
            "technical_debt": self.technical_debt,

            "valuation": self.valuation,
            "founder_ownership": round(self.founder_ownership, 2),
            "last_funding_round": self.last_funding_round,
            "months_since_funding": self.months_since_funding,

            "is_public": self.is_public,
            "share_price": self.share_price,
            "market_cap": self.market_cap,
        }