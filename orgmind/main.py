import config
import uuid

from core.company import Company
from market.events import generate_event

from agents.ceo import CEOAgent
from agents.finance import FinanceAgent
from agents.cto import CTOAgent

from core.kpi_engine import apply_decision
from core.decision_engine import negotiate_decision

from finance.valuation_engine import calculate_valuation
from finance.funding_engine import attempt_funding

from market.ipo_engine import attempt_ipo
from market.stock_engine import generate_candle

from analytics.performance_report import generate_report

from db.repository import (
    save_company_state,
    save_decision_log,
    save_stock_candle
)


simulation_id = str(uuid.uuid4())
print("Simulation ID:", simulation_id)


def run_simulation():

    company = Company(config)

    ceo = CEOAgent()
    finance = FinanceAgent()
    cto = CTOAgent()

    history = []

    for _ in range(25):

        print("\n==============================")
        print(f"Month {company.month}")
        print("==============================")

        # -----------------------------
        # Current State
        # -----------------------------
        state = company.summary()

        event = generate_event()

        print("Market Event:", event["name"])
        print("Current KPIs:", state)

        # -----------------------------
        # CEO Decision
        # -----------------------------
        ceo_decision = ceo.propose(state, event["name"])
        print("CEO Proposal:", ceo_decision)

        # -----------------------------
        # Finance Review
        # -----------------------------
        finance_feedback = finance.evaluate(state, ceo_decision)
        print("Finance Response:", finance_feedback)

        # -----------------------------
        # CTO Review
        # -----------------------------
        cto_feedback = cto.evaluate(state, ceo_decision)
        print("CTO Response:", cto_feedback)

        # -----------------------------
        # Negotiation Engine
        # -----------------------------
        final_decision = negotiate_decision(
            company,
            ceo_decision,
            finance_feedback,
            cto_feedback
        )

        print("Final Negotiated Decision:", final_decision)

        # -----------------------------
        # Save state
        # -----------------------------
        save_company_state(
            simulation_id,
            company.summary()
        )

        save_decision_log(
            simulation_id,
            company.month,
            event["name"],
            ceo_decision,
            finance_feedback,
            cto_feedback,
            final_decision
        )

        # -----------------------------
        # Apply Decision
        # -----------------------------
        apply_decision(
            company,
            final_decision,
            event
        )

        # -----------------------------
        # Bankruptcy Check
        # -----------------------------
        if company.bankrupt:

            print("💀 Company Bankrupt — Simulation Ending")
            break

        # -----------------------------
        # Valuation Update
        # -----------------------------
        valuation = calculate_valuation(company)

        company.valuation = valuation

        print("Valuation:", valuation)

        # -----------------------------
        # IPO Attempt
        # -----------------------------
        ipo_result = attempt_ipo(company)

        if ipo_result:

            print("🚀 IPO Completed:", ipo_result)

        # -----------------------------
        # Public Market Simulation
        # -----------------------------
        if company.is_public:

            candle = generate_candle(
                company,
                company.share_price
            )

            print("📈 Monthly Stock Candle:", candle)

            # Sync valuation with market cap (FIX)
            company.valuation = company.market_cap

            save_stock_candle(
                simulation_id,
                company.month,
                candle,
                company.market_cap
            )

        # -----------------------------
        # Funding Engine
        # -----------------------------
        funding_result = attempt_funding(company)

        if funding_result:

            print("💰 Funding Round Closed:", funding_result)

        else:

            print(
                f"   ↳ Funding not closed "
                f"(round={company.last_funding_round}, "
                f"months_since={company.months_since_funding}, "
                f"users={company.users}, "
                f"revenue={company.revenue})"
            )

        # -----------------------------
        # Save Monthly History
        # -----------------------------
        history.append(company.summary())

    # -----------------------------
    # Simulation End
    # -----------------------------
    print("\n==============================")
    print("Final Company State")
    print("==============================")

    final_state = company.summary()

    print(final_state)

    # -----------------------------
    # Generate Performance Report
    # -----------------------------
    try:

        generate_report(history)

    except Exception as e:

        print("⚠️ Failed to generate report:", e)


if __name__ == "__main__":

    run_simulation()