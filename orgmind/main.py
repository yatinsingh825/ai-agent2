import config
from core.company import Company
from market.events import generate_event
from agents.ceo import CEOAgent
from agents.finance import FinanceAgent
from agents.cto import CTOAgent
from core.kpi_engine import apply_decision
from core.decision_engine import negotiate_decision
from db.repository import save_company_state, save_decision_log


def run_simulation():

    company = Company(config)

    ceo = CEOAgent()
    finance = FinanceAgent()
    cto = CTOAgent()   # ✅ NEW

    for _ in range(6):

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

        # 3️⃣ CTO evaluates (NEW)
        cto_feedback = cto.evaluate(state, ceo_decision)
        print("CTO Response:", cto_feedback)

        # 4️⃣ Negotiated final decision (NOW 3 AGENTS)
        final_decision = negotiate_decision(
            company,
            ceo_decision,
            finance_feedback,
            cto_feedback
        )

        print("Final Negotiated Decision:", final_decision)

        # ✅ SAVE BEFORE state changes (correct persistence logic)
        save_company_state(company.summary())

        save_decision_log(
            company.month,
            event["name"],
            ceo_decision,
            finance_feedback,
            cto_feedback,          # ✅ ADDED
            final_decision
        )

        # 5️⃣ Apply decision to company state
        apply_decision(company, final_decision, event)

    print("\nFinal Company State:")
    print(company.summary())


if __name__ == "__main__":
    run_simulation()