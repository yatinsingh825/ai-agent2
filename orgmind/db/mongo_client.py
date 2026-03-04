from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client["orgmind_db"]

company_collection = db["company_states"]
decision_collection = db["monthly_decisions"]
stock_collection = db["stock_candles"]