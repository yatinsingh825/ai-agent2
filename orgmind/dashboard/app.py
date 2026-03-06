"""
OrgMind — Startup Simulation Dashboard
Drop this file into orgmind/dashboard/app.py
Run with: python -m streamlit run dashboard/app.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import subprocess
import threading
import time
import json
import os
import sys
from datetime import datetime

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OrgMind · Startup Simulator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg:       #08090f;
    --surface:  #10121c;
    --border:   #1e2235;
    --accent:   #7c3aed;
    --accent2:  #06b6d4;
    --accent3:  #f59e0b;
    --green:    #10b981;
    --red:      #ef4444;
    --text:     #e2e8f0;
    --muted:    #64748b;
}

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* Metric cards */
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
}
.metric-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    font-family: 'Space Mono', monospace;
    margin-bottom: 6px;
}
.metric-value {
    font-size: 1.7rem;
    font-weight: 800;
    color: var(--text);
    line-height: 1;
}
.metric-sub {
    font-size: 0.75rem;
    color: var(--muted);
    margin-top: 4px;
    font-family: 'Space Mono', monospace;
}
.metric-delta-pos { color: var(--green); font-size: 0.8rem; }
.metric-delta-neg { color: var(--red); font-size: 0.8rem; }

/* Section headers */
.section-header {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--muted);
    font-family: 'Space Mono', monospace;
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
    margin: 28px 0 16px 0;
}

/* Event badge */
.event-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    margin: 2px;
}
.badge-funding  { background: #1a4731; color: #4ade80; border: 1px solid #166534; }
.badge-ipo      { background: #1e3a5f; color: #60a5fa; border: 1px solid #1d4ed8; }
.badge-seriesb  { background: #3b1f5e; color: #c084fc; border: 1px solid #7c3aed; }
.badge-bridge   { background: #292524; color: #fb923c; border: 1px solid #92400e; }

/* Log terminal */
.log-terminal {
    background: #000;
    border: 1px solid #1e2235;
    border-radius: 8px;
    padding: 16px;
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: #4ade80;
    max-height: 400px;
    overflow-y: auto;
    white-space: pre-wrap;
}

/* Timeline */
.timeline-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid var(--border);
}
.timeline-month {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: var(--muted);
    min-width: 60px;
    padding-top: 2px;
}
.timeline-content { flex: 1; font-size: 0.85rem; }

/* Hero banner */
.hero {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 32px 40px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.hero::after {
    content: 'ORGMIND';
    position: absolute;
    right: -20px; top: 50%;
    transform: translateY(-50%);
    font-size: 8rem;
    font-weight: 800;
    color: rgba(255,255,255,0.03);
    font-family: 'Syne', sans-serif;
    pointer-events: none;
}
.hero h1 {
    font-size: 2rem;
    font-weight: 800;
    margin: 0 0 8px 0;
    background: linear-gradient(90deg, #7c3aed, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero p {
    color: var(--muted);
    margin: 0;
    font-size: 0.9rem;
    font-family: 'Space Mono', monospace;
}

/* Run button override */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #06b6d4) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    padding: 12px 28px !important;
    font-size: 0.85rem !important;
    width: 100% !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }
</style>
""", unsafe_allow_html=True)

# ── Plotly theme ───────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#10121c",
    plot_bgcolor="#10121c",
    font=dict(family="Space Mono, monospace", color="#94a3b8", size=11),
    margin=dict(l=16, r=16, t=36, b=16),
    xaxis=dict(gridcolor="#1e2235", linecolor="#1e2235", tickcolor="#1e2235"),
    yaxis=dict(gridcolor="#1e2235", linecolor="#1e2235", tickcolor="#1e2235"),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1e2235"),
)

COLORS = {
    "purple": "#7c3aed", "cyan": "#06b6d4", "amber": "#f59e0b",
    "green": "#10b981", "red": "#ef4444", "pink": "#ec4899",
    "blue": "#3b82f6", "orange": "#f97316",
}

# ── Helpers ────────────────────────────────────────────────────────────────────
def fmt_money(v):
    if v >= 1_000_000: return f"${v/1_000_000:.2f}M"
    if v >= 1_000:     return f"${v/1_000:.1f}K"
    return f"${v:.0f}"

def fmt_num(v):
    if v >= 1_000_000: return f"{v/1_000_000:.2f}M"
    if v >= 1_000:     return f"{v/1_000:.1f}K"
    return str(int(v))

def metric_card(label, value, sub="", delta=None):
    delta_html = ""
    if delta is not None:
        cls = "metric-delta-pos" if delta >= 0 else "metric-delta-neg"
        sign = "▲" if delta >= 0 else "▼"
        delta_html = f'<div class="{cls}">{sign} {abs(delta):.1f}%</div>'
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-sub">{sub}</div>
        {delta_html}
    </div>"""

# ── Data loading ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=5)
def load_latest_simulation():
    """Try MongoDB first, fallback to local JSON cache."""
    try:
        from pymongo import MongoClient
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        db = client["orgmind"]
        sims = list(db.simulations.find().sort("created_at", -1).limit(1))
        if sims:
            sim = sims[0]
            history = list(db.kpi_history.find(
                {"simulation_id": str(sim["_id"])}).sort("month", 1))
            return sim, history
    except Exception:
        pass

    # Fallback: local JSON
    cache_path = os.path.join(os.path.dirname(__file__), "..", "simulation_cache.json")
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("simulation", {}), data.get("history", [])

    return None, []

def load_all_simulations():
    """Load multiple simulation summaries for comparison."""
    try:
        from pymongo import MongoClient
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        db = client["orgmind"]
        return list(db.simulations.find().sort("created_at", -1).limit(10))
    except Exception:
        return []

# ── Chart builders ─────────────────────────────────────────────────────────────
def chart_growth_overview(df):
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Users", "Revenue / Month", "Cash Position", "Burn Multiple"),
        vertical_spacing=0.12, horizontal_spacing=0.08,
    )
    kw = dict(mode="lines", line=dict(width=2.5))

    fig.add_trace(go.Scatter(x=df["month"], y=df["users"], name="Users",
        fill="tozeroy", fillcolor="rgba(124,58,237,0.08)",
        line=dict(color=COLORS["purple"], width=2.5)), row=1, col=1)

    fig.add_trace(go.Scatter(x=df["month"], y=df["revenue"], name="Revenue",
        fill="tozeroy", fillcolor="rgba(6,182,212,0.08)",
        line=dict(color=COLORS["cyan"], width=2.5)), row=1, col=2)

    fig.add_trace(go.Scatter(x=df["month"], y=df["cash"], name="Cash",
        fill="tozeroy", fillcolor="rgba(16,185,129,0.08)",
        line=dict(color=COLORS["green"], width=2.5)), row=2, col=1)

    if "burn_rate" in df.columns and "revenue" in df.columns:
        burn_mult = df["burn_rate"] / df["revenue"].replace(0, 1)
        colors_bm = [COLORS["green"] if v < 1.2 else COLORS["red"] for v in burn_mult]
        fig.add_trace(go.Bar(x=df["month"], y=burn_mult, name="Burn Multiple",
            marker_color=colors_bm, showlegend=False), row=2, col=2)
        fig.add_hline(y=1.2, line_dash="dash", line_color="#ef4444",
                      annotation_text="1.2x danger", row=2, col=2)

    fig.update_layout(**PLOTLY_LAYOUT, height=480, showlegend=False,
                      title_text="Growth Overview", title_font_size=13)
    fig.update_annotations(font_size=11, font_color="#64748b")
    return fig


def chart_revenue_vs_burn(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["month"], y=df["revenue"],
        name="Revenue", fill="tozeroy",
        fillcolor="rgba(16,185,129,0.1)",
        line=dict(color=COLORS["green"], width=2.5)))
    fig.add_trace(go.Scatter(
        x=df["month"], y=df["burn_rate"],
        name="Burn Rate", line=dict(color=COLORS["red"], width=2, dash="dash")))
    fig.update_layout(**PLOTLY_LAYOUT, height=300,
                      title_text="Revenue vs Burn Rate",
                      yaxis_tickprefix="$")
    return fig


def chart_valuation(df, events):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["month"], y=df["valuation"],
        fill="tozeroy", fillcolor="rgba(245,158,11,0.08)",
        line=dict(color=COLORS["amber"], width=2.5),
        name="Valuation"))

    color_map = {
        "Pre-Seed Bridge": COLORS["orange"],
        "Seed": COLORS["green"],
        "Series A": COLORS["cyan"],
        "Series B": COLORS["purple"],
        "IPO": COLORS["pink"],
    }
    for ev in events:
        col = color_map.get(ev["type"], "#fff")
        fig.add_vline(x=ev["month"], line_dash="dot", line_color=col,
                      annotation_text=f"  {ev['type']}", annotation_font_color=col,
                      annotation_font_size=10)

    fig.update_layout(**PLOTLY_LAYOUT, height=300,
                      title_text="Valuation Over Time",
                      yaxis_tickprefix="$")
    return fig


def chart_quality_reputation(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["month"], y=df["product_quality"],
        name="Product Quality", line=dict(color=COLORS["cyan"], width=2.5)))
    fig.add_trace(go.Scatter(
        x=df["month"], y=df["reputation"],
        name="Reputation", line=dict(color=COLORS["pink"], width=2.5)))
    if "technical_debt" in df.columns:
        fig.add_trace(go.Bar(
            x=df["month"], y=df["technical_debt"] * 10,
            name="Tech Debt ×10", marker_color="rgba(239,68,68,0.3)",
            yaxis="y2"))
    fig.update_layout(
        **PLOTLY_LAYOUT, height=300,
        title_text="Product Quality & Reputation",
        yaxis=dict(range=[0, 11], gridcolor="#1e2235", title="Score /10"),
        yaxis2=dict(overlaying="y", side="right", showgrid=False,
                    title="", range=[0, 11]),
        legend=dict(orientation="h", y=1.12))
    return fig


def chart_team(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["month"], y=df["engineers"],
        name="Engineers", fill="tozeroy",
        fillcolor="rgba(59,130,246,0.1)",
        line=dict(color=COLORS["blue"], width=2.5, shape="hv")))
    if "marketing_budget" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["month"], y=df["marketing_budget"],
            name="Marketing $", yaxis="y2",
            line=dict(color=COLORS["amber"], width=1.5, dash="dot")))
    fig.update_layout(
        **PLOTLY_LAYOUT, height=280,
        title_text="Team Growth",
        yaxis=dict(gridcolor="#1e2235", title="Engineers"),
        yaxis2=dict(overlaying="y", side="right", showgrid=False,
                    title="Mktg Budget $"),
        legend=dict(orientation="h", y=1.12))
    return fig


def chart_stock(df):
    pub = df[df.get("is_public", False) == True] if "is_public" in df.columns else pd.DataFrame()
    if pub.empty:
        return None

    fig = go.Figure()
    if all(c in pub.columns for c in ["stock_open", "stock_high", "stock_low", "stock_close"]):
        fig.add_trace(go.Candlestick(
            x=pub["month"],
            open=pub["stock_open"], high=pub["stock_high"],
            low=pub["stock_low"], close=pub["stock_close"],
            increasing_line_color=COLORS["green"],
            decreasing_line_color=COLORS["red"],
            name="Stock"))
    else:
        fig.add_trace(go.Scatter(
            x=pub["month"], y=pub["share_price"],
            line=dict(color=COLORS["green"], width=2.5),
            fill="tozeroy", fillcolor="rgba(16,185,129,0.08)",
            name="Share Price"))

    fig.update_layout(**PLOTLY_LAYOUT, height=280,
                      title_text="Stock Price (Post-IPO)",
                      yaxis_tickprefix="$",
                      xaxis_rangeslider_visible=False)
    return fig


def chart_runway(df):
    colors = []
    for v in df["runway_months"]:
        if v < 3:   colors.append(COLORS["red"])
        elif v < 6: colors.append(COLORS["amber"])
        else:       colors.append(COLORS["green"])

    fig = go.Figure(go.Bar(
        x=df["month"], y=df["runway_months"],
        marker_color=colors, name="Runway"))
    fig.add_hline(y=6, line_dash="dash", line_color=COLORS["amber"],
                  annotation_text="6mo warning")
    fig.add_hline(y=3, line_dash="dash", line_color=COLORS["red"],
                  annotation_text="3mo critical")
    fig.update_layout(**PLOTLY_LAYOUT, height=260,
                      title_text="Runway (Months)",
                      yaxis_title="Months")
    return fig


# ── Simulation runner ─────────────────────────────────────────────────────────
def run_simulation_subprocess():
    """Run main.py from orgmind root and stream output."""
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    proc = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    lines = []
    for line in proc.stdout:
        lines.append(line.rstrip())
        yield line.rstrip()
    proc.wait()


# ── Extract events from history ────────────────────────────────────────────────
def extract_events(history):
    events = []
    prev_round = None
    prev_public = False
    for h in history:
        rnd = h.get("last_funding_round")
        msi = h.get("months_since_funding", 99)
        pub = h.get("is_public", False)
        m   = h.get("month", 0)

        if rnd and msi == 0 and rnd != prev_round:
            events.append({"month": m, "type": rnd,
                           "detail": f"Raised ${h.get('cash',0):,.0f} total cash"})
            prev_round = rnd

        if pub and not prev_public:
            events.append({"month": m, "type": "IPO",
                           "detail": f"IPO @ ${h.get('share_price',0):.2f}/share"})
        prev_public = pub
    return events


# ── Main layout ────────────────────────────────────────────────────────────────
def main():
    # ── Sidebar ────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style="padding: 16px 0 24px 0;">
            <div style="font-family:'Space Mono',monospace; font-size:0.65rem;
                        color:#64748b; letter-spacing:0.15em; margin-bottom:4px;">
                ORGMIND
            </div>
            <div style="font-size:1.3rem; font-weight:800; color:#e2e8f0;">
                Startup Simulator
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div class="metric-label">Navigation</div>', unsafe_allow_html=True)

        page = st.radio("", [
            "📊 Dashboard",
            "🚀 Run Simulation",
            "📈 Compare Runs",
            "📋 Event Timeline",
        ], label_visibility="collapsed")

        st.markdown("---")
        st.markdown('<div class="metric-label">System</div>', unsafe_allow_html=True)

        # DB status
        try:
            from pymongo import MongoClient
            MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=1000).admin.command("ping")
            st.markdown("🟢 MongoDB connected")
        except Exception:
            st.markdown("🟡 MongoDB offline — using cache")

        st.markdown(f"🕐 {datetime.now().strftime('%H:%M:%S')}")

    # ── Load data ──────────────────────────────────────────────────────────────
    sim, history = load_latest_simulation()
    df = pd.DataFrame(history) if history else pd.DataFrame()
    events = extract_events(history) if history else []
    has_data = not df.empty

    # ══════════════════════════════════════════════════════════════════════════
    if page == "📊 Dashboard":
        # Hero
        sim_id = sim.get("simulation_id", sim.get("_id", "—")) if sim else "—"
        st.markdown(f"""
        <div class="hero">
            <h1>OrgMind Dashboard</h1>
            <p>Simulation ID: {str(sim_id)[:24]}... &nbsp;|&nbsp; 
               {len(history)} months recorded &nbsp;|&nbsp;
               Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        """, unsafe_allow_html=True)

        if not has_data:
            st.info("No simulation data found. Run a simulation first using the **Run Simulation** tab.")
            return

        final = df.iloc[-1]

        # ── KPI cards row 1 ────────────────────────────────────────────────────
        st.markdown('<div class="section-header">Key Performance Indicators</div>',
                    unsafe_allow_html=True)
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.markdown(metric_card("Monthly Revenue",
                fmt_money(final.get("revenue", 0)),
                f"from $10K start",
                ((final.get("revenue",0) / 10000) - 1) * 100), unsafe_allow_html=True)
        with c2:
            st.markdown(metric_card("Users",
                fmt_num(final.get("users", 0)),
                f"from 1,000 start",
                ((final.get("users",0) / 1000) - 1) * 100), unsafe_allow_html=True)
        with c3:
            st.markdown(metric_card("Cash",
                fmt_money(final.get("cash", 0)),
                f"{final.get('runway_months',0):.1f} mo runway"), unsafe_allow_html=True)
        with c4:
            mc = final.get("market_cap", final.get("valuation", 0))
            st.markdown(metric_card("Valuation",
                fmt_money(mc),
                final.get("last_funding_round", "Pre-revenue")), unsafe_allow_html=True)
        with c5:
            bm = final.get("burn_rate", 0) / max(1, final.get("revenue", 1))
            bm_color = "🟢" if bm < 1.2 else "🔴"
            st.markdown(metric_card("Burn Multiple",
                f"{bm:.2f}x",
                f"{bm_color} {'efficient' if bm < 1.2 else 'warning'}"), unsafe_allow_html=True)

        # KPI cards row 2
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.markdown(metric_card("Engineers",
                str(int(final.get("engineers", 0))),
                f"team members"), unsafe_allow_html=True)
        with c2:
            st.markdown(metric_card("Product Quality",
                f"{final.get('product_quality',0):.1f}/10",
                f"Reputation: {final.get('reputation',0):.1f}"), unsafe_allow_html=True)
        with c3:
            sp = final.get("share_price", 0)
            is_pub = final.get("is_public", False)
            st.markdown(metric_card("Share Price",
                f"${sp:.2f}" if is_pub else "Private",
                "Public" if is_pub else "Pre-IPO"), unsafe_allow_html=True)
        with c4:
            st.markdown(metric_card("Founder Ownership",
                f"{final.get('founder_ownership',1)*100:.0f}%",
                f"After {final.get('last_funding_round','none')}"), unsafe_allow_html=True)
        with c5:
            td = final.get("technical_debt", 0)
            td_color = "🟢" if td < 0.2 else ("🟡" if td < 0.5 else "🔴")
            st.markdown(metric_card("Tech Debt",
                f"{td:.2f}",
                f"{td_color} {'low' if td < 0.2 else 'medium' if td < 0.5 else 'critical'}"),
                unsafe_allow_html=True)

        # ── Funding events strip ───────────────────────────────────────────────
        if events:
            st.markdown('<div class="section-header">Funding Journey</div>',
                        unsafe_allow_html=True)
            badge_cls = {
                "Pre-Seed Bridge": "badge-bridge",
                "Seed": "badge-funding",
                "Series A": "badge-funding",
                "Series B": "badge-seriesb",
                "IPO": "badge-ipo",
            }
            badges = ""
            for ev in events:
                cls = badge_cls.get(ev["type"], "badge-funding")
                badges += f'<span class="event-badge {cls}">Mo.{ev["month"]} · {ev["type"]}</span> '
            st.markdown(badges, unsafe_allow_html=True)

        # ── Charts ─────────────────────────────────────────────────────────────
        st.markdown('<div class="section-header">Growth Overview</div>',
                    unsafe_allow_html=True)
        st.plotly_chart(chart_growth_overview(df), use_container_width=True)

        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown('<div class="section-header">Revenue vs Burn</div>',
                        unsafe_allow_html=True)
            st.plotly_chart(chart_revenue_vs_burn(df), use_container_width=True)
        with col_r:
            st.markdown('<div class="section-header">Valuation Timeline</div>',
                        unsafe_allow_html=True)
            st.plotly_chart(chart_valuation(df, events), use_container_width=True)

        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown('<div class="section-header">Quality & Reputation</div>',
                        unsafe_allow_html=True)
            st.plotly_chart(chart_quality_reputation(df), use_container_width=True)
        with col_r:
            st.markdown('<div class="section-header">Team Growth</div>',
                        unsafe_allow_html=True)
            st.plotly_chart(chart_team(df), use_container_width=True)

        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown('<div class="section-header">Runway</div>',
                        unsafe_allow_html=True)
            st.plotly_chart(chart_runway(df), use_container_width=True)
        with col_r:
            sc = chart_stock(df)
            if sc:
                st.markdown('<div class="section-header">Stock Price</div>',
                            unsafe_allow_html=True)
                st.plotly_chart(sc, use_container_width=True)

        # ── Raw data expander ──────────────────────────────────────────────────
        with st.expander("📄 Raw KPI History"):
            display_cols = ["month", "revenue", "cash", "users", "burn_rate",
                            "runway_months", "engineers", "product_quality",
                            "reputation", "technical_debt", "valuation",
                            "founder_ownership", "last_funding_round", "is_public"]
            show_cols = [c for c in display_cols if c in df.columns]
            st.dataframe(
                df[show_cols].style.format({
                    "revenue": "${:,.0f}", "cash": "${:,.0f}",
                    "burn_rate": "${:,.0f}", "valuation": "${:,.0f}",
                    "runway_months": "{:.1f}", "product_quality": "{:.2f}",
                    "reputation": "{:.2f}", "technical_debt": "{:.3f}",
                    "founder_ownership": "{:.0%}",
                }),
                use_container_width=True, height=300
            )

    # ══════════════════════════════════════════════════════════════════════════
    elif page == "🚀 Run Simulation":
        st.markdown("""
        <div class="hero">
            <h1>Run Simulation</h1>
            <p>Launch a new 25-month startup lifecycle simulation using your AI agents.</p>
        </div>
        """, unsafe_allow_html=True)

        col_info, col_btn = st.columns([3, 1])
        with col_info:
            st.markdown("""
            <div style="background:#10121c; border:1px solid #1e2235; border-radius:12px; padding:20px;">
                <div class="metric-label">What happens during simulation</div>
                <div style="margin-top:12px; font-size:0.85rem; color:#94a3b8; line-height:1.8;">
                    🤖 <b>CEO Agent</b> — proposes monthly strategy based on market events<br>
                    💰 <b>Finance Agent</b> — approves/reduces budget based on runway &amp; burn multiple<br>
                    🔧 <b>CTO Agent</b> — recommends technical investment and quality improvements<br>
                    📊 <b>KPI Engine</b> — simulates users, revenue, churn, tech debt<br>
                    🏦 <b>Funding Engine</b> — triggers Bridge → Seed → Series A → Series B → IPO
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_btn:
            run_clicked = st.button("▶ LAUNCH SIMULATION")

        st.markdown('<div class="section-header">Simulation Output</div>',
                    unsafe_allow_html=True)

        if run_clicked:
            log_placeholder = st.empty()
            progress_bar = st.progress(0)
            status = st.empty()

            all_lines = []
            month_count = 0

            status.markdown("🔄 Starting simulation...")

            try:
                for line in run_simulation_subprocess():
                    all_lines.append(line)

                    # Track month progress
                    if "Month " in line and "=" * 10 in line:
                        try:
                            m = int(line.strip().split("Month")[-1].strip().split()[0])
                            month_count = m
                            progress_bar.progress(min(m / 25, 1.0))
                            status.markdown(f"📅 Simulating Month **{m}** / 25...")
                        except Exception:
                            pass

                    # Show last 60 lines in terminal
                    terminal_lines = all_lines[-60:]
                    log_text = "\n".join(terminal_lines)
                    log_placeholder.markdown(
                        f'<div class="log-terminal">{log_text}</div>',
                        unsafe_allow_html=True)

                progress_bar.progress(1.0)
                status.markdown("✅ Simulation complete! Switch to **Dashboard** to view results.")

                # Invalidate cache so dashboard reloads
                load_latest_simulation.clear()

            except Exception as e:
                status.markdown(f"❌ Error: {e}")
                st.error(f"Could not run simulation: {e}\n\nMake sure you're running from the orgmind/ directory.")
        else:
            st.markdown(
                '<div class="log-terminal">Waiting for simulation to start...\n'
                'Click ▶ LAUNCH SIMULATION above.</div>',
                unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    elif page == "📈 Compare Runs":
        st.markdown("""
        <div class="hero">
            <h1>Compare Runs</h1>
            <p>Side-by-side analysis of multiple simulation outcomes.</p>
        </div>
        """, unsafe_allow_html=True)

        all_sims = load_all_simulations()

        if not all_sims:
            st.info("No simulation data found. Run multiple simulations to compare them.")
            return

        # Summary table
        st.markdown('<div class="section-header">Simulation Summary</div>',
                    unsafe_allow_html=True)

        rows = []
        for s in all_sims:
            final_state = s.get("final_state", {})
            rows.append({
                "Sim ID": str(s.get("simulation_id", s.get("_id", "?")))[:12],
                "Revenue": fmt_money(final_state.get("revenue", 0)),
                "Users": fmt_num(final_state.get("users", 0)),
                "Cash": fmt_money(final_state.get("cash", 0)),
                "Valuation": fmt_money(final_state.get("valuation", 0)),
                "Engineers": int(final_state.get("engineers", 0)),
                "Last Round": final_state.get("last_funding_round", "None"),
                "IPO": "✅" if final_state.get("is_public") else "❌",
                "Stock": f"${final_state.get('share_price', 0):.2f}",
                "Burn Multiple": f"{final_state.get('burn_rate',0)/max(1,final_state.get('revenue',1)):.2f}x",
            })

        st.dataframe(pd.DataFrame(rows), use_container_width=True, height=300)

        # Multi-run revenue comparison
        if len(all_sims) > 1:
            st.markdown('<div class="section-header">Revenue Trajectory Comparison</div>',
                        unsafe_allow_html=True)

            try:
                from pymongo import MongoClient
                client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
                db = client["orgmind"]

                fig = go.Figure()
                palette = [COLORS["purple"], COLORS["cyan"], COLORS["amber"],
                           COLORS["green"], COLORS["pink"]]

                for i, s in enumerate(all_sims[:5]):
                    sid = str(s.get("_id", ""))
                    hist = list(db.kpi_history.find(
                        {"simulation_id": sid}).sort("month", 1))
                    if hist:
                        h_df = pd.DataFrame(hist)
                        label = f"Run {i+1} · {str(s.get('simulation_id', sid))[:8]}"
                        fig.add_trace(go.Scatter(
                            x=h_df["month"], y=h_df["revenue"],
                            name=label,
                            line=dict(color=palette[i % len(palette)], width=2)))

                fig.update_layout(**PLOTLY_LAYOUT, height=380,
                                  title_text="Revenue Comparison Across Runs",
                                  yaxis_tickprefix="$")
                st.plotly_chart(fig, use_container_width=True)

            except Exception:
                st.info("Connect MongoDB to enable multi-run comparison charts.")

    # ══════════════════════════════════════════════════════════════════════════
    elif page == "📋 Event Timeline":
        st.markdown("""
        <div class="hero">
            <h1>Event Timeline</h1>
            <p>Month-by-month breakdown of key decisions and market events.</p>
        </div>
        """, unsafe_allow_html=True)

        if not has_data:
            st.info("No simulation data found.")
            return

        # Funding timeline
        if events:
            st.markdown('<div class="section-header">Funding Milestones</div>',
                        unsafe_allow_html=True)
            badge_cls = {
                "Pre-Seed Bridge": "badge-bridge",
                "Seed": "badge-funding",
                "Series A": "badge-funding",
                "Series B": "badge-seriesb",
                "IPO": "badge-ipo",
            }
            icons = {
                "Pre-Seed Bridge": "🌉", "Seed": "🌱",
                "Series A": "💰", "Series B": "🚀", "IPO": "📈",
            }
            for ev in events:
                cls = badge_cls.get(ev["type"], "badge-funding")
                icon = icons.get(ev["type"], "•")
                st.markdown(f"""
                <div class="timeline-item">
                    <div class="timeline-month">Month {ev['month']}</div>
                    <div class="timeline-content">
                        {icon} <span class="event-badge {cls}">{ev['type']}</span>
                        &nbsp; {ev.get('detail', '')}
                    </div>
                </div>""", unsafe_allow_html=True)

        # Month-by-month KPI table
        st.markdown('<div class="section-header">KPI Progression</div>',
                    unsafe_allow_html=True)

        for _, row in df.iterrows():
            m = int(row.get("month", 0))
            rev = row.get("revenue", 0)
            users = row.get("users", 0)
            cash = row.get("cash", 0)
            rwy = row.get("runway_months", 0)
            pq = row.get("product_quality", 0)
            rep = row.get("reputation", 0)
            td = row.get("technical_debt", 0)

            # Color runway
            rwy_color = COLORS["green"] if rwy >= 6 else (
                COLORS["amber"] if rwy >= 3 else COLORS["red"])
            td_color = COLORS["green"] if td < 0.2 else (
                COLORS["amber"] if td < 0.5 else COLORS["red"])

            st.markdown(f"""
            <div style="background:#10121c; border:1px solid #1e2235;
                        border-radius:8px; padding:12px 16px; margin-bottom:6px;
                        font-family:'Space Mono',monospace; font-size:0.72rem;">
                <span style="color:#7c3aed; font-weight:700; min-width:70px; display:inline-block;">
                    Mo.{m:02d}</span>
                <span style="color:#10b981; min-width:90px; display:inline-block;">
                    {fmt_money(rev)}</span>
                <span style="color:#06b6d4; min-width:80px; display:inline-block;">
                    {fmt_num(users)} users</span>
                <span style="color:#94a3b8; min-width:90px; display:inline-block;">
                    {fmt_money(cash)}</span>
                <span style="color:{rwy_color}; min-width:70px; display:inline-block;">
                    {rwy:.1f}mo rwy</span>
                <span style="color:#e2e8f0; min-width:70px; display:inline-block;">
                    PQ:{pq:.1f}</span>
                <span style="color:#ec4899; min-width:70px; display:inline-block;">
                    Rep:{rep:.1f}</span>
                <span style="color:{td_color};">TD:{td:.2f}</span>
            </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()