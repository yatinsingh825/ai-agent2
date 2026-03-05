from datetime import datetime
from db.mongo_client import company_collection, decision_collection, stock_collection


def save_company_state(simulation_id, state):

    record = {
        **state,
        "simulation_id": simulation_id,
        "timestamp": datetime.utcnow()
    }

    company_collection.insert_one(record)


def save_decision_log(
    simulation_id,
    month,
    event,
    ceo,
    finance,
    cto,
    final
):

    record = {
        "simulation_id": simulation_id,
        "month": month,
        "market_event": event,
        "ceo_proposal": ceo,
        "finance_response": finance,
        "cto_response": cto,
        "final_decision": final,
        "timestamp": datetime.utcnow()
    }

    decision_collection.insert_one(record)


def save_stock_candle(simulation_id, month, candle, market_cap):

    stock_collection.insert_one({
        "simulation_id": simulation_id,
        "month": month,
        "open": candle["open"],
        "high": candle["high"],
        "low": candle["low"],
        "close": candle["close"],
        "market_cap": market_cap,
        "timestamp": datetime.utcnow()
    })