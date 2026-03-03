from datetime import datetime
from db.mongo_client import company_collection, decision_collection


def save_company_state(state):
    """
    Persist monthly company state snapshot.
    """
    state_record = {
        **state,
        "timestamp": datetime.utcnow()
    }

    company_collection.insert_one(state_record)


def save_decision_log(
    month,
    event,
    ceo,
    finance,
    cto,
    final
):
    """
    Persist full executive decision trace for the month.
    """

    decision_record = {
        "month": month,
        "market_event": event,
        "ceo_proposal": ceo,
        "finance_response": finance,
        "cto_response": cto,  # ✅ NEW
        "final_decision": final,
        "timestamp": datetime.utcnow()
    }

    decision_collection.insert_one(decision_record)