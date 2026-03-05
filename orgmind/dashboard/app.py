import streamlit as st
import pandas as pd
from pymongo import MongoClient
import plotly.express as px

# -----------------------------
# Connect to MongoDB
# -----------------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["orgmind_db"]

company_collection = db["company_states"]

st.title("OrgMind AI Startup Simulator")

# -----------------------------
# Get available simulation runs
# -----------------------------
runs = company_collection.distinct("simulation_id")

if not runs:
    st.warning("No simulation runs found in database.")
    st.stop()

# -----------------------------
# Select Simulation Run
# -----------------------------
selected_run = st.selectbox("Select Simulation Run", runs)

# -----------------------------
# Query data for selected run
# -----------------------------
data = list(
    company_collection.find(
        {"simulation_id": selected_run},
        {"_id": 0}
    )
)

if not data:
    st.warning("No data available for this simulation.")
    st.stop()

df = pd.DataFrame(data)
df = df.sort_values("month")

# -----------------------------
# Latest company snapshot
# -----------------------------
st.subheader("Company Overview")

latest = df.iloc[-1]

col1, col2, col3 = st.columns(3)

col1.metric("Revenue", latest["revenue"])
col2.metric("Users", latest["users"])
col3.metric("Valuation", latest["valuation"])

col4, col5, col6 = st.columns(3)

col4.metric("Cash", latest["cash"])
col5.metric("Burn Rate", latest["burn_rate"])
col6.metric("Runway (months)", round(latest["runway_months"], 2))

# -----------------------------
# Revenue Growth
# -----------------------------
st.subheader("Revenue Growth")

fig = px.line(df, x="month", y="revenue", markers=True)
st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# User Growth
# -----------------------------
st.subheader("User Growth")

fig2 = px.line(df, x="month", y="users", markers=True)
st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# Burn Rate
# -----------------------------
st.subheader("Burn Rate")

fig3 = px.line(df, x="month", y="burn_rate", markers=True)
st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# Product Metrics
# -----------------------------
st.subheader("Product Metrics")

fig4 = px.line(df, x="month", y=["product_quality", "reputation"])
st.plotly_chart(fig4, use_container_width=True)