import config
from core.company import Company
from market.events import generate_event
from agents.ceo import CEOAgent
from agents.finance import FinanceAgent
from agents.cto import CTOAgent
from core.kpi_engine import apply_decision
from core.decision_engine import negotiate_decision
from db.repository import save_company_state, save_decision_log
from finance.valuation_engine import calculate_valuation
from finance.funding_engine import attempt_funding
from market.ipo_engine import attempt_ipo
from market.stock_engine import generate_candle
from db.repository import save_stock_candle


def run_simulation():

    company = Company(config)

    ceo = CEOAgent()
    finance = FinanceAgent()
    cto = CTOAgent()

    for _ in range(25):

        print("\n==============================")
        print(f"Month {company.month}")
        print("==============================")

        state = company.summary()
        event = generate_event()

        print("Market Event:", event["name"])
        print("Current KPIs:", state)

        # 1️⃣ CEO proposes
        ceo_decision = ceo.propose(state, event["name"])
        print("CEO Proposal:", ceo_decision)

        # 2️⃣ Finance evaluates
        finance_feedback = finance.evaluate(state, ceo_decision)
        print("Finance Response:", finance_feedback)

        # 3️⃣ CTO evaluates
        cto_feedback = cto.evaluate(state, ceo_decision)
        print("CTO Response:", cto_feedback)

        # 4️⃣ Negotiated final decision
        final_decision = negotiate_decision(
            company,
            ceo_decision,
            finance_feedback,
            cto_feedback
        )

        print("Final Negotiated Decision:", final_decision)

        # Save state BEFORE changes
        save_company_state(company.summary())

        save_decision_log(
            company.month,
            event["name"],
            ceo_decision,
            finance_feedback,
            cto_feedback,
            final_decision
        )

        # 5️⃣ Apply decision
        apply_decision(company, final_decision, event)

        # --------------------------
        # 💀 Bankruptcy Detection
        # --------------------------
        if company.cash < -50000:
            print("💀 Company Bankrupt — Simulation Ending")
            break

        # --------------------------
        # 🚀 Valuation Calculation
        # --------------------------
        valuation = calculate_valuation(company)
        print("Valuation:", valuation)

        # --------------------------
        # 🚀 IPO Attempt
        # --------------------------
        ipo_result = attempt_ipo(company)

        if ipo_result:
            print("🚀 IPO Completed:", ipo_result)

        # --------------------------
        # 📈 Public Market Simulation
        # --------------------------
        if company.is_public:

            candle = generate_candle(company, company.share_price)

            print("📈 Monthly Stock Candle:", candle)

            save_stock_candle(
                company.month,
                candle,
                company.market_cap
            )

        # --------------------------
        # 💰 Funding Logic
        # --------------------------
        if company.runway() < 2 and company.months_since_funding > 6:

            print("⚡ Funding consideration triggered.")

            funding_result = attempt_funding(company)

            if funding_result:
                print("💰 Funding Round Closed:", funding_result)

    print("\nFinal Company State:")
    print(company.summary())


if __name__ == "__main__":
    run_simulation()