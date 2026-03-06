import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import base64
import io


def _fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def _build_kpi_cards(state):

    cards = [
        ("Revenue / Month", f"${state['revenue']:,.0f}", "Monthly recurring revenue"),
        ("Users", f"{state['users']:,}", "Total platform users"),
        ("Cash", f"${state['cash']:,.0f}", f"{state['runway_months']:.1f} months runway"),
        ("Valuation", f"${state['valuation']:,.0f}", state.get("last_funding_round", "No funding")),
        ("Product Quality", f"{state['product_quality']:.1f}/10", f"Reputation {state['reputation']:.1f}"),
        ("Engineers", f"{state['engineers']}", "Team size"),
        ("Market Cap", f"${state.get('market_cap',0):,.0f}", "Public" if state.get("is_public") else "Private"),
        ("Share Price", f"${state.get('share_price',0):.2f}", "Per share"),
        ("Burn Multiple", f"{state['burn_rate']/max(1,state['revenue']):.2f}x", "Healthy < 1.5"),
    ]

    html = ""

    for title, value, sub in cards:

        html += f"""
        <div class="card">
            <h3>{title}</h3>
            <div class="value">{value}</div>
            <div class="sub">{sub}</div>
        </div>
        """

    return html


def _build_funding_timeline(history):

    html = ""

    for i, h in enumerate(history):

        if h.get("last_funding_round") and h.get("months_since_funding") == 0:

            html += f"""
            <div class="event">
                <span class="badge funding">Month {h['month']}</span>
                💰 <strong>{h['last_funding_round']}</strong>
                — valuation ${h['valuation']:,.0f}
            </div>
            """

        # Safe IPO detection (avoid negative index)
        if i > 0 and h.get("is_public") and not history[i - 1].get("is_public", False):

            html += f"""
            <div class="event">
                <span class="badge ipo">Month {h['month']}</span>
                🚀 <strong>IPO</strong>
                — share price ${h.get('share_price',0):.2f}
            </div>
            """

    if html == "":
        html = "<p>No major events recorded</p>"

    return html


def generate_report(history, filename="report.html"):

    months = [h["month"] for h in history]

    final_state = history[-1]

    charts = {}

    # --------------------------
    # Users
    # --------------------------

    fig, ax = plt.subplots()

    ax.plot(months, [h["users"] for h in history], linewidth=2)

    ax.set_title("User Growth")

    charts["users"] = _fig_to_base64(fig)

    # --------------------------
    # Revenue vs Burn
    # --------------------------

    fig, ax = plt.subplots()

    ax.plot(months, [h["revenue"] for h in history], label="Revenue", linewidth=2)

    ax.plot(months, [h["burn_rate"] for h in history], label="Burn", linestyle="--")

    ax.legend()

    ax.set_title("Revenue vs Burn Rate")

    charts["revenue"] = _fig_to_base64(fig)

    # --------------------------
    # Cash
    # --------------------------

    fig, ax = plt.subplots()

    ax.plot(months, [h["cash"] for h in history], linewidth=2)

    ax.set_title("Cash Position")

    charts["cash"] = _fig_to_base64(fig)

    # --------------------------
    # Product Quality
    # --------------------------

    fig, ax = plt.subplots()

    ax.plot(months, [h["product_quality"] for h in history], label="Quality")

    ax.plot(months, [h["reputation"] for h in history], label="Reputation")

    ax.legend()

    ax.set_title("Product Quality & Reputation")

    charts["quality"] = _fig_to_base64(fig)

    # --------------------------
    # Valuation
    # --------------------------

    fig, ax = plt.subplots()

    ax.plot(months, [h["valuation"] for h in history], linewidth=2)

    ax.set_title("Valuation Over Time")

    charts["valuation"] = _fig_to_base64(fig)

    # --------------------------
    # Team Growth
    # --------------------------

    fig, ax = plt.subplots()

    ax.step(months, [h["engineers"] for h in history], where="post")

    ax.set_title("Engineering Team Growth")

    charts["team"] = _fig_to_base64(fig)

    # --------------------------
    # HTML
    # --------------------------

    html = f"""
<html>

<head>

<title>Startup Simulation Report</title>

<style>

body {{
font-family: Arial;
background: #0f0f1a;
color: white;
padding: 20px;
}}

.grid {{
display: grid;
grid-template-columns: repeat(3,1fr);
gap: 15px;
}}

.grid2 {{
display: grid;
grid-template-columns: repeat(2,1fr);
gap: 15px;
margin-top:20px;
}}

.card {{
background:#1e1e2e;
padding:15px;
border-radius:10px;
}}

.value {{
font-size:24px;
font-weight:bold;
}}

.sub {{
font-size:12px;
color:#aaa;
}}

.chart {{
background:#1e1e2e;
padding:10px;
border-radius:10px;
}}

.timeline {{
margin-top:20px;
background:#1e1e2e;
padding:15px;
border-radius:10px;
}}

.event {{
padding:5px 0;
}}

.badge {{
padding:3px 8px;
border-radius:8px;
margin-right:10px;
}}

.funding {{background:#184d2f;}}

.ipo {{background:#1a3a4f;}}

</style>

</head>

<body>

<h1>🚀 Startup Simulation Report</h1>

<h2>Final KPIs</h2>

<div class="grid">

{_build_kpi_cards(final_state)}

</div>

<h2>Growth Charts</h2>

<div class="grid2">

<div class="chart"><img src="data:image/png;base64,{charts['users']}"></div>

<div class="chart"><img src="data:image/png;base64,{charts['revenue']}"></div>

<div class="chart"><img src="data:image/png;base64,{charts['cash']}"></div>

<div class="chart"><img src="data:image/png;base64,{charts['quality']}"></div>

<div class="chart"><img src="data:image/png;base64,{charts['valuation']}"></div>

<div class="chart"><img src="data:image/png;base64,{charts['team']}"></div>

</div>

<h2>Key Events Timeline</h2>

<div class="timeline">

{_build_funding_timeline(history)}

</div>

</body>

</html>
"""

    # 🔴 FIX: Windows encoding crash
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"📊 Performance report generated: {filename}")