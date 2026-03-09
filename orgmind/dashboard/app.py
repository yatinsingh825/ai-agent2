"""
OrgMind — Startup Simulation Dashboard v2
Drop into orgmind/dashboard/app.py and run:
    cd orgmind
    streamlit run dashboard/app.py

IMPORTANT: main.py is imported directly — run this dashboard INSTEAD of main.py.
The simulation runs inside the dashboard itself.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os, threading, time, queue, uuid
from datetime import datetime
from dashboard.outcome_summary import render_outcome_summary

# ── Add orgmind root to path so we can import all your modules ────────────────
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OrgMind · Startup Simulator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&display=swap');

html, body, [class*="css"] {
  font-family: 'JetBrains Mono', monospace !important;
  background-color: #04050a !important;
  color: #e2e8f0 !important;
}
#MainMenu, footer, header, .stDeployButton { visibility: hidden !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none !important; }
.stApp { background: #04050a; }
div[data-testid="stVerticalBlock"] { gap: 0 !important; }

/* Inputs */
.stTextInput input, .stTextArea textarea, .stNumberInput input {
  background: #0c1220 !important; border: 1px solid #1e2d45 !important;
  color: #e2e8f0 !important; border-radius: 8px !important;
  font-family: 'JetBrains Mono', monospace !important; font-size: 13px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: #7c3aed !important; box-shadow: 0 0 0 2px rgba(124,58,237,.15) !important;
}

/* Selectbox */
div[data-baseweb="select"] > div {
  background: #0c1220 !important; border-color: #1e2d45 !important;
  color: #e2e8f0 !important; font-family: 'JetBrains Mono', monospace !important;
}
div[data-baseweb="popover"] { background: #0c1220 !important; }
li[role="option"] { background: #0c1220 !important; color: #e2e8f0 !important; font-family: 'JetBrains Mono', monospace !important; }
li[role="option"]:hover { background: #1e2d45 !important; }

/* Slider */
.stSlider > div > div { background: #1e2d45 !important; }
.stSlider > div > div > div { background: #7c3aed !important; }
[data-testid="stTickBarMin"], [data-testid="stTickBarMax"] { color: #4b5563 !important; font-size: 10px !important; }

/* Buttons */
.stButton > button {
  background: linear-gradient(135deg, #7c3aed, #0ea5e9) !important;
  color: #fff !important; border: none !important; border-radius: 8px !important;
  font-family: 'JetBrains Mono', monospace !important; font-weight: 700 !important;
  letter-spacing: .08em !important; font-size: 11px !important;
  padding: 9px 18px !important; text-transform: uppercase !important;
  transition: all .2s !important;
}
.stButton > button:hover { opacity: .85 !important; transform: translateY(-1px) !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  background: #080c14 !important; border-bottom: 1px solid #111827 !important;
  padding: 0 16px !important; gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important; color: #4b5563 !important;
  font-family: 'JetBrains Mono', monospace !important; font-size: 11px !important;
  letter-spacing: .08em !important; padding: 10px 18px !important;
  border-radius: 0 !important; border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
  color: #7c3aed !important; border-bottom: 2px solid #7c3aed !important;
  background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] { padding: 0 !important; background: #04050a !important; }

/* Progress */
.stProgress > div > div { background: linear-gradient(90deg, #7c3aed, #06b6d4) !important; }
.stProgress > div { background: #111827 !important; }

/* Expander */
[data-testid="stExpander"] {
  border: 1px solid #111827 !important; border-radius: 8px !important;
  background: #080c14 !important;
}
details summary { font-family: 'JetBrains Mono', monospace !important; font-size: 11px !important; color: #4b5563 !important; }

/* Dataframe */
[data-testid="stDataFrame"] { border: 1px solid #111827 !important; border-radius: 8px !important; }
.stDataFrame thead th { background: #0c1220 !important; color: #4b5563 !important; font-family: 'JetBrains Mono', monospace !important; font-size: 10px !important; }
.stDataFrame tbody td { font-family: 'JetBrains Mono', monospace !important; font-size: 11px !important; color: #cbd5e1 !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #04050a; }
::-webkit-scrollbar-thumb { background: #1e2d45; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def fm(v):
    if not v: return "$0"
    if v >= 1_000_000: return f"${v/1_000_000:.2f}M"
    if v >= 1_000: return f"${v/1_000:.1f}K"
    return f"${int(v)}"

def fn(v):
    if not v: return "0"
    if v >= 1_000_000: return f"{v/1_000_000:.1f}M"
    if v >= 1_000: return f"{v/1_000:.1f}K"
    return str(int(v))

# Shared plotly base (NO xaxis/yaxis to avoid conflict with dual-axis charts)
def base_layout(height=240, title="", yprefix=""):
    return dict(
        paper_bgcolor="#080c14", plot_bgcolor="#080c14",
        font=dict(family="JetBrains Mono, monospace", color="#4b5563", size=10),
        margin=dict(l=52, r=16, t=36, b=28),
        height=height,
        title_text=title, title_font_color="#374151", title_font_size=11,
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#111827", font_size=9),
        xaxis=dict(gridcolor="#111827", linecolor="#111827", tickcolor="#111827",
                   tickfont=dict(size=9, color="#374151")),
        yaxis=dict(gridcolor="#111827", linecolor="#111827", tickcolor="#111827",
                   tickfont=dict(size=9, color="#374151"),
                   tickprefix=yprefix),
    )

def dual_layout(height=240, title=""):
    """Layout for charts with yaxis2 — must NOT include yaxis in base."""
    return dict(
        paper_bgcolor="#080c14", plot_bgcolor="#080c14",
        font=dict(family="JetBrains Mono, monospace", color="#4b5563", size=10),
        margin=dict(l=52, r=52, t=36, b=28),
        height=height,
        title_text=title, title_font_color="#374151", title_font_size=11,
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#111827",
                    font_size=9, orientation="h", y=1.08),
        xaxis=dict(gridcolor="#111827", linecolor="#111827",
                   tickfont=dict(size=9, color="#374151")),
        yaxis=dict(gridcolor="#111827", linecolor="#111827",
                   tickfont=dict(size=9, color="#374151")),
        yaxis2=dict(overlaying="y", side="right", showgrid=False,
                    tickfont=dict(size=9, color="#374151")),
    )

C = dict(
    purple="#7c3aed", cyan="#06b6d4", green="#10b981",
    amber="#f59e0b", red="#ef4444", pink="#ec4899",
    blue="#3b82f6", orange="#f97316",
)

AGENT_META = {
    "SYSTEM":  ("#f59e0b", "🏢"),
    "CEO":     ("#a78bfa", "👔"),
    "FINANCE": ("#34d399", "💼"),
    "CTO":     ("#60a5fa", "⚙️"),
    "HR":      ("#f97316", "👷"),
}

def kpi_card(label, value, sub="", color="#7c3aed"):
    return f"""
<div style="background:#080c14;border:1px solid #111827;border-radius:10px;
            padding:16px 14px 14px;position:relative;overflow:hidden;min-height:90px;
            box-sizing:border-box;">
  <div style="position:absolute;top:0;left:0;right:0;height:2px;
              background:linear-gradient(90deg,{color}90,transparent);"></div>
  <div style="font-size:8px;text-transform:uppercase;letter-spacing:.1em;
              color:#374151;margin-bottom:7px;white-space:nowrap;overflow:hidden;
              text-overflow:ellipsis;">{label}</div>
  <div style="font-size:19px;font-weight:700;color:#e2e8f0;line-height:1.1;
              word-break:break-all;">{value}</div>
  <div style="font-size:9px;color:#4b5563;margin-top:5px;white-space:nowrap;
              overflow:hidden;text-overflow:ellipsis;">{sub}</div>
</div>"""

def chat_bubble(role, msg, color, icon):
    msg_safe = str(msg).replace("<", "&lt;").replace(">", "&gt;")
    return f"""
<div style="display:flex;gap:12px;margin-bottom:16px;align-items:flex-start;">
  <div style="width:36px;height:36px;border-radius:9px;background:{color}18;
              border:1.5px solid {color}50;display:flex;align-items:center;
              justify-content:center;font-size:17px;flex-shrink:0;margin-top:2px;">{icon}</div>
  <div style="flex:1;min-width:0;">
    <div style="font-size:9px;color:{color};font-weight:700;letter-spacing:.1em;
                margin-bottom:5px;text-transform:uppercase;">{role}</div>
    <div style="background:{color}0d;border:1px solid {color}28;
                border-radius:4px 12px 12px 12px;padding:11px 15px;
                font-size:12.5px;line-height:1.75;color:#cbd5e1;
                white-space:pre-wrap;word-break:break-word;
                overflow-wrap:break-word;">{msg_safe}</div>
  </div>
</div>"""

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
DEFAULTS = {
    "page": "setup",
    "setup_step": 0,
    "company_config": {},
    "sim_running": False,
    "sim_log": [],
    "kpi_history": [],
    "candles": [],
    "funding_events": [],
    "final_state": None,
    "current_month": 0,
    "msg_queue": None,
    "sim_thread": None,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
# SIMULATION THREAD — imports your actual modules directly
# ══════════════════════════════════════════════════════════════════════════════
def run_simulation_thread(cfg, q):
    """
    Runs the full OrgMind simulation by importing your actual modules.
    Mirrors main.py exactly, but pushes events to a queue instead of print().
    """
    try:
        import importlib
        import config as base_config
        importlib.reload(base_config)  # force reload so stale cache doesn't persist between sims

        # Safely patch config — UI values override config.py defaults
        base_config.INITIAL_REVENUE = cfg.get("initial_revenue",
            getattr(base_config, "INITIAL_REVENUE", 10000))
        base_config.INITIAL_CASH    = cfg.get("initial_cash",
            getattr(base_config, "INITIAL_CASH", 50000))
        base_config.INITIAL_USERS   = cfg.get("initial_users",
            getattr(base_config, "INITIAL_USERS", 1000))
        # Ensure all attrs Company() needs exist (defensive)
        for attr, default in [("INITIAL_BURN", 8000),
                               ("INITIAL_PRODUCT_QUALITY", 6.0),
                               ("INITIAL_REPUTATION", 5.0)]:
            if not hasattr(base_config, attr):
                setattr(base_config, attr, default)

        from core.company         import Company
        from market.events        import generate_event
        from agents.ceo           import CEOAgent
        from agents.finance       import FinanceAgent
        from agents.cto           import CTOAgent
        from core.kpi_engine      import apply_decision
        from core.decision_engine import negotiate_decision
        from finance.valuation_engine import calculate_valuation
        from finance.funding_engine   import attempt_funding
        from market.ipo_engine        import attempt_ipo
        from market.stock_engine      import generate_candle

        # Try DB — silently skip if unavailable
        save_state = save_decision = save_candle = lambda *a, **kw: None
        try:
            from db.repository import save_company_state, save_decision_log, save_stock_candle
            save_state    = save_company_state
            save_decision = save_decision_log
            save_candle   = save_stock_candle
        except Exception:
            pass

        company = Company(base_config)
        ceo     = CEOAgent()
        finance = FinanceAgent()
        cto     = CTOAgent()
        sim_id  = str(uuid.uuid4())
        months  = cfg.get("months", 25)

        q.put({"type": "system",
               "msg": f"🏢 Simulation started — {cfg.get('name','Company')} · {cfg.get('industry','SaaS')}\n"
                      f"Founder: {cfg.get('founder','Anonymous')} · {months} months · Risk: {cfg.get('risk','balanced').title()}"})

        for _ in range(months):
            q.put({"type": "month", "month": company.month})

            state = company.summary()
            event = generate_event()

            q.put({"type": "kpi", "data": state})
            q.put({"type": "system", "msg": f"📅 Month {company.month} — Market Event: \"{event['name']}\""})

            # ── CEO ──
            ceo_decision = ceo.propose(state, event["name"])
            strategy  = ceo_decision.get("strategy", "?")
            budget    = ceo_decision.get("budget_change", 0)
            ug        = ceo_decision.get("user_growth", 0)
            rg        = ceo_decision.get("revenue_growth", 0)
            conf      = ceo_decision.get("confidence", 0)
            q.put({"type": "chat", "role": "CEO",
                   "msg": f"Strategy: \"{strategy}\"\n\n"
                          f"Budget Request: ${budget:,}  ·  User Growth Target: {ug*100:.0f}%  ·  Revenue Target: +{rg*100:.0f}%\n"
                          f"Confidence: {conf*100:.0f}%"})

            # ── FINANCE ──
            finance_feedback = finance.evaluate(state, ceo_decision)
            approved = finance_feedback.get("approved_budget_change", 0)
            bm       = finance_feedback.get("burn_multiple", 0)
            comment  = finance_feedback.get("comment", "")
            q.put({"type": "chat", "role": "FINANCE",
                   "msg": f"Approved Budget: ${approved:,}  ·  Burn Multiple: {bm:.2f}×\n\n{comment}"})

            # ── CTO ──
            cto_feedback = cto.evaluate(state, ceo_decision)
            rec    = cto_feedback.get("recommended_budget_change", 0)
            impact = cto_feedback.get("tech_impact", {})
            pq_ch  = impact.get("product_quality_change", 0)
            td_ch  = impact.get("technical_debt_change", 0)
            q.put({"type": "chat", "role": "CTO",
                   "msg": f"Tech Budget Recommendation: ${rec:,}\n\n"
                          f"Product Quality: {'+' if pq_ch >= 0 else ''}{pq_ch:.2f}  ·  "
                          f"Tech Debt: {'+' if td_ch >= 0 else ''}{td_ch:.2f}"})

            # ── NEGOTIATE ──
            final_decision = negotiate_decision(company, ceo_decision, finance_feedback, cto_feedback)
            q.put({"type": "system",
                   "msg": f"✅ Decision: \"{final_decision.get('strategy','?')}\"  ·  "
                          f"Budget: ${final_decision.get('budget_change',0):,}"})

            # ── SAVE PRE-DECISION ──
            save_state(sim_id, company.summary())
            save_decision(sim_id, company.month, event["name"],
                          ceo_decision, finance_feedback, cto_feedback, final_decision)

            # ── APPLY ──
            prev_engineers = company.engineers
            apply_decision(company, final_decision, event)

            # ── BANKRUPTCY ──
            if company.bankrupt:
                q.put({"type": "system", "msg": "💀 BANKRUPTCY DECLARED — simulation ended."})
                break

            # ── HIRING ──
            if company.engineers > prev_engineers:
                hired = company.engineers - prev_engineers
                q.put({"type": "chat", "role": "HR",
                       "msg": f"Hired {hired} engineer(s). Team is now {company.engineers} strong.\n"
                              f"Monthly burn increases by ${hired * 4000:,}."})

            # ── VALUATION ──
            valuation = calculate_valuation(company)
            company.valuation = valuation

            # ── IPO ──
            ipo_result = attempt_ipo(company)
            if ipo_result:
                q.put({"type": "system",
                       "msg": f"🚀 IPO COMPLETED!  Price: ${ipo_result.get('ipo_price',0):.2f}/share  ·  "
                              f"Market Cap: {fm(ipo_result.get('market_cap',0))}"})
                q.put({"type": "funding", "event": {
                    "month": company.month, "type": "IPO", "raised": 0}})

            # ── STOCK CANDLE ──
            if company.is_public:
                candle = generate_candle(company, company.share_price)
                candle["month"] = company.month
                q.put({"type": "candle", "data": candle})
                save_candle(sim_id, company.month, candle, company.market_cap)

            # ── FUNDING ──
            if (company.users > 1500
                    and company.product_quality > 6
                    and company.months_since_funding > 6):
                funding_result = attempt_funding(company)
                if funding_result:
                    rnd    = funding_result.get("round", "?")
                    raised = funding_result.get("raised", 0)
                    new_val = funding_result.get("valuation", 0)
                    dil    = funding_result.get("dilution", 0)
                    q.put({"type": "system",
                           "msg": f"💰 {rnd} CLOSED!  Raised: {fm(raised)}  ·  "
                                  f"New Valuation: {fm(new_val)}  ·  Dilution: {dil*100:.0f}%"})
                    q.put({"type": "funding", "event": {
                        "month": company.month, "type": rnd, "raised": raised}})

            company.month += 1

        # ── FINAL ──
        final = company.summary()
        q.put({"type": "kpi", "data": final})
        q.put({"type": "final_state", "data": final})
        q.put({"type": "system",
               "msg": f"🏁 SIMULATION COMPLETE — Month {company.month}\n"
                      f"Revenue: {fm(final['revenue'])}  ·  Users: {fn(final['users'])}  ·  "
                      f"Valuation: {fm(final['valuation'])}  ·  "
                      f"Cash: {fm(final['cash'])}  ·  {'PUBLIC 📈' if final['is_public'] else 'Private'}"})

    except Exception as e:
        import traceback
        q.put({"type": "system", "msg": f"❌ Simulation error: {e}\n\n{traceback.format_exc()}"})
    finally:
        q.put({"type": "done"})


def drain_queue():
    """Pull events from queue into session state. Called every rerun."""
    q = st.session_state.get("msg_queue")
    if not q:
        return
    drained = 0
    while drained < 80:
        try:
            evt = q.get_nowait()
        except queue.Empty:
            break
        drained += 1
        t = evt["type"]

        if t == "done":
            st.session_state["sim_running"] = False

        elif t == "month":
            st.session_state["current_month"] = evt["month"]

        elif t == "system":
            st.session_state["sim_log"].append({"role": "SYSTEM", "msg": evt["msg"]})

        elif t == "chat":
            st.session_state["sim_log"].append({"role": evt["role"], "msg": evt["msg"]})

        elif t == "kpi":
            d = evt["data"]
            st.session_state["kpi_history"].append(d)
            # Detect funding round from KPI snapshot
            rnd = d.get("last_funding_round")
            msi = d.get("months_since_funding", 99)
            fe  = st.session_state["funding_events"]
            if rnd and msi == 0:
                if not fe or fe[-1].get("type") != rnd:
                    fe.append({"month": d["month"], "type": rnd, "raised": 0})

        elif t == "candle":
            st.session_state["candles"].append(evt["data"])

        elif t == "funding":
            fe = st.session_state["funding_events"]
            ev = evt["event"]
            # Deduplicate
            if not any(x["type"] == ev["type"] and x["month"] == ev["month"] for x in fe):
                fe.append(ev)

        elif t == "final_state":
            st.session_state["final_state"] = evt["data"]


def launch_simulation(cfg):
    """Reset state and start the simulation thread."""
    for k in ["sim_log","kpi_history","candles","funding_events"]:
        st.session_state[k] = []
    st.session_state["final_state"]    = None
    st.session_state["current_month"]  = 0
    st.session_state["sim_running"]    = True
    st.session_state["page"]           = "sim"

    q = queue.Queue()
    st.session_state["msg_queue"] = q

    t = threading.Thread(target=run_simulation_thread, args=(cfg, q), daemon=True)
    t.start()
    st.session_state["sim_thread"] = t
    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: COMPANY SETUP
# ══════════════════════════════════════════════════════════════════════════════
def page_setup():
    st.markdown("""
    <style>
    @keyframes fadeUp { from{opacity:0;transform:translateY(14px)} to{opacity:1;transform:translateY(0)} }
    .setup-anim { animation: fadeUp .45s ease; }
    </style>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 2.4, 1])
    with mid:
        # ── Logo ──────────────────────────────────────────────────────────────
        st.markdown("""
        <div class="setup-anim" style="text-align:center;padding:36px 0 28px;">
          <div style="font-size:8px;letter-spacing:.5em;color:#111827;margin-bottom:6px;">ORGMIND SIMULATOR</div>
          <div style="font-size:36px;font-weight:900;
                      background:linear-gradient(135deg,#a78bfa,#38bdf8);
                      -webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1.05;">
            BUILD YOUR STARTUP
          </div>
          <div style="font-size:10px;color:#1f2937;margin-top:8px;letter-spacing:.12em;">
            POWERED BY YOUR AI AGENTS · OLLAMA · MONGODB
          </div>
        </div>
        """, unsafe_allow_html=True)

        step = st.session_state["setup_step"]
        cfg  = st.session_state.get("company_config", {})

        # ── Step pills ────────────────────────────────────────────────────────
        step_labels = ["Identity", "Financials", "Strategy"]
        cols = st.columns(3)
        for i, (col, label) in enumerate(zip(cols, step_labels)):
            with col:
                active_col = "#7c3aed" if i <= step else "#111827"
                text_col   = "#7c3aed" if i == step else "#1f2937"
                st.markdown(f"""
                <div style="text-align:center;">
                  <div style="height:3px;border-radius:2px;background:{active_col};
                              transition:background .3s;margin-bottom:5px;"></div>
                  <div style="font-size:9px;color:{text_col};letter-spacing:.1em;">{label.upper()}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        # ── Card ──────────────────────────────────────────────────────────────
        st.markdown("""<div style="background:#080c14;border:1px solid #111827;
                                    border-radius:16px;padding:28px;">""",
                    unsafe_allow_html=True)

        # ── STEP 0: Identity ──────────────────────────────────────────────────
        if step == 0:
            st.markdown("<div style='font-size:10px;color:#374151;letter-spacing:.1em;margin-bottom:16px;'>01 · COMPANY IDENTITY</div>", unsafe_allow_html=True)
            cfg["name"]     = st.text_input("Company Name", value=cfg.get("name",""), placeholder="e.g. NexaFlow, Orbit Labs…")
            industries = ["SaaS","Fintech","HealthTech","EdTech","E-Commerce","AI/ML","Gaming","CleanTech","Logistics","PropTech"]
            idx = industries.index(cfg.get("industry","SaaS")) if cfg.get("industry","SaaS") in industries else 0
            cfg["industry"] = st.selectbox("Industry", industries, index=idx)
            cfg["founder"]  = st.text_input("Founder Name", value=cfg.get("founder",""), placeholder="Your name")
            cfg["vision"]   = st.text_area("Company Vision", value=cfg.get("vision",""),
                                            placeholder="What problem are you solving?", height=76)

        # ── STEP 1: Financials ────────────────────────────────────────────────
        elif step == 1:
            st.markdown("<div style='font-size:10px;color:#374151;letter-spacing:.1em;margin-bottom:16px;'>02 · STARTING FINANCIALS</div>", unsafe_allow_html=True)

            def option_row(label, options_dict, state_key, default, color):
                st.markdown(f"<div style='font-size:9px;color:#374151;letter-spacing:.1em;margin-bottom:7px;'>{label}</div>", unsafe_allow_html=True)
                cols = st.columns(len(options_dict))
                for col, (lbl, val) in zip(cols, options_dict.items()):
                    with col:
                        sel = cfg.get(state_key, default) == val
                        bg  = f"{color}22" if sel else "transparent"
                        bdr = color if sel else "#1e2d45"
                        tc  = color if sel else "#374151"
                        if st.button(lbl, key=f"{state_key}_{val}"):
                            cfg[state_key] = val
                            st.session_state["company_config"] = cfg
                            st.rerun()
                        # Visual override via HTML (button itself triggers logic)
                        st.markdown(f"""<style>
                        button[kind="secondary"][data-testid*="{state_key}_{val}"] {{
                          background: {bg} !important; border-color: {bdr} !important; color: {tc} !important;
                        }}</style>""", unsafe_allow_html=True)
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

            option_row("STARTING CASH", {"$25K":25000,"$50K":50000,"$100K":100000,"$200K":200000}, "initial_cash", 50000, C["green"])
            option_row("INITIAL USERS", {"500":500,"1,000":1000,"2,000":2000,"5,000":5000}, "initial_users", 1000, C["cyan"])
            option_row("MONTHLY REVENUE (MRR)", {"$5K":5000,"$10K":10000,"$25K":25000,"$50K":50000}, "initial_revenue", 10000, C["amber"])
            option_row("STARTING ENGINEERS", {"2 eng":2,"3 eng":3,"5 eng":5,"8 eng":8}, "engineers", 3, C["purple"])

        # ── STEP 2: Strategy ──────────────────────────────────────────────────
        elif step == 2:
            st.markdown("<div style='font-size:10px;color:#374151;letter-spacing:.1em;margin-bottom:16px;'>03 · FOUNDER STRATEGY</div>", unsafe_allow_html=True)

            risk_options = [
                ("conservative", "🐢  Conservative", "Lower variance, steady compounding, safer runway"),
                ("balanced",     "⚖️  Balanced",      "Realistic risk/reward — mirrors default main.py"),
                ("aggressive",   "🚀  Aggressive",    "High variance, explosive growth potential"),
            ]
            for rid, rlabel, rdesc in risk_options:
                sel = cfg.get("risk","balanced") == rid
                bdr = "#7c3aed" if sel else "#111827"
                bg  = "#1e1340" if sel else "#080c14"
                tc  = "#a78bfa" if sel else "#4b5563"
                if st.button(f"{rlabel}", key=f"risk_{rid}"):
                    cfg["risk"] = rid
                    st.session_state["company_config"] = cfg
                    st.rerun()
                st.markdown(f"""
                <div style="border:1.5px solid {bdr};background:{bg};border-radius:9px;
                            padding:10px 14px;margin-top:-8px;margin-bottom:8px;">
                  <div style="font-size:10px;color:#1f2937;">{rdesc}</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            cfg["months"] = st.slider("Simulation Length (months)", 12, 36, cfg.get("months", 25))

            # Preview card
            st.markdown(f"""
            <div style="background:#04050a;border:1px solid #111827;border-radius:9px;
                        padding:14px;margin-top:14px;font-size:11px;line-height:1.9;color:#374151;">
              <div style="color:#7c3aed;font-weight:700;margin-bottom:5px;font-size:10px;letter-spacing:.08em;">
                📋 SIMULATION PREVIEW
              </div>
              <b style="color:#e2e8f0;">{cfg.get('name','Unnamed')}</b> · {cfg.get('industry','SaaS')}
              &nbsp;·&nbsp; Founder: <b style="color:#e2e8f0;">{cfg.get('founder','Anonymous')}</b><br>
              Cash: <span style="color:#10b981;">{fm(cfg.get('initial_cash',50000))}</span>
              &nbsp;·&nbsp; Users: <span style="color:#60a5fa;">{fn(cfg.get('initial_users',1000))}</span>
              &nbsp;·&nbsp; MRR: <span style="color:#f59e0b;">{fm(cfg.get('initial_revenue',10000))}</span>
              &nbsp;·&nbsp; Team: <span style="color:#a78bfa;">{cfg.get('engineers',3)} engineers</span><br>
              Risk: <span style="color:#e2e8f0;">{cfg.get('risk','balanced').title()}</span>
              &nbsp;·&nbsp; Duration: <span style="color:#e2e8f0;">{cfg.get('months',25)} months</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)   # close card
        st.session_state["company_config"] = cfg

        # ── Nav buttons ───────────────────────────────────────────────────────
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        b1, b2 = st.columns([1, 2])
        with b1:
            if step > 0:
                if st.button("← Back"):
                    st.session_state["setup_step"] = step - 1
                    st.rerun()
        with b2:
            if step < 2:
                if st.button("Continue →"):
                    st.session_state["setup_step"] = step + 1
                    st.rerun()
            else:
                if st.button("🚀  Launch Simulation"):
                    st.session_state["setup_step"] = 0
                    launch_simulation(cfg)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SIMULATION DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def page_sim():
    st.markdown("""
    <style>
    @keyframes slideIn { from{opacity:0;transform:translateX(-8px)} to{opacity:1;transform:translateX(0)} }
    @keyframes blink   { 0%,100%{opacity:1} 50%{opacity:.2} }
    @keyframes ticker  { from{transform:translateX(0)} to{transform:translateX(-50%)} }
    @keyframes glow    { 0%,100%{box-shadow:0 0 8px #10b98130} 50%{box-shadow:0 0 24px #10b98170} }
    </style>
    """, unsafe_allow_html=True)

    drain_queue()

    cfg             = st.session_state.get("company_config", {})
    history         = st.session_state.get("kpi_history", [])
    candles         = st.session_state.get("candles", [])
    sim_log         = st.session_state.get("sim_log", [])
    funding_events  = st.session_state.get("funding_events", [])
    running         = st.session_state.get("sim_running", False)
    cur_month       = st.session_state.get("current_month", 0)
    total_months    = cfg.get("months", 25)
    last            = history[-1] if history else {}
    prev            = history[-2] if len(history) > 1 else last

    # ── HEADER ────────────────────────────────────────────────────────────────
    public_badge = ""
    if last.get("is_public"):
        public_badge = f'<span style="padding:3px 9px;border-radius:20px;background:#052e16;border:1px solid #34d39940;font-size:9px;color:#34d399;animation:glow 2s infinite;">📈 PUBLIC · ${last.get("share_price",0):.2f}</span>'
    round_badge = ""
    if last.get("last_funding_round"):
        round_badge = f'<span style="padding:3px 9px;border-radius:20px;background:#1e1340;border:1px solid #7c3aed40;font-size:9px;color:#a78bfa;">{last["last_funding_round"]}</span>'
    live_dot = '<span style="width:7px;height:7px;border-radius:50%;background:#ef4444;display:inline-block;animation:blink 1s infinite;margin-left:4px;"></span>' if running else ''

    st.markdown(f"""
    <div style="display:flex;align-items:center;padding:10px 20px;
                background:#050709;border-bottom:1px solid #0a0f1a;
                flex-wrap:wrap;gap:10px;min-height:52px;">
      <div>
        <div style="font-size:7px;color:#1f2937;letter-spacing:.35em;line-height:1;">ORGMIND</div>
        <div style="font-size:16px;font-weight:900;color:#e2e8f0;line-height:1.2;">
          {cfg.get('name','STARTUP')}
        </div>
      </div>
      <div style="width:1px;height:28px;background:#111827;flex-shrink:0;"></div>
      <div style="font-size:10px;color:#374151;line-height:1.6;">
        <span style="color:#7c3aed;font-weight:700;">MONTH {cur_month}</span>
        <span style="color:#1f2937;"> / {total_months}</span>
        &nbsp;·&nbsp;{cfg.get('industry','—')}
        &nbsp;·&nbsp;{cfg.get('founder','—')}
        {live_dot}
      </div>
      {round_badge}
      {public_badge}
    </div>
    """, unsafe_allow_html=True)

    # ── TICKER TAPE ───────────────────────────────────────────────────────────
    if last:
        bm = last.get("burn_rate",1) / max(1, last.get("revenue",1))
        rwy = last.get("runway_months", 99)
        rwy_col = C["red"] if rwy < 3 else C["amber"] if rwy < 6 else C["green"]
        items = [
            (cfg.get("name","ORGMD")[:6].upper(), f"${last.get('share_price',0):.2f}" if last.get("is_public") else "PRIVATE",
             C["green"] if last.get("is_public") else "#374151"),
            ("REV",    fm(last.get("revenue",0)),     C["green"]),
            ("USERS",  fn(last.get("users",0)),        C["purple"]),
            ("CASH",   fm(last.get("cash",0)),         C["blue"]),
            ("RUNWAY", f"{rwy:.1f}mo",                  rwy_col),
            ("BURN×",  f"{bm:.2f}",                    C["red"] if bm > 1.2 else C["green"]),
            ("VAL",    fm(last.get("valuation",0)),    C["amber"]),
            ("ENG",    str(last.get("engineers",0)),   "#94a3b8"),
            ("PQ",     f"{last.get('product_quality',0):.1f}", C["cyan"]),
            ("DEBT",   f"{last.get('technical_debt',0):.2f}",
             C["red"] if last.get("technical_debt",0) > 0.3 else "#374151"),
        ]
        doubled = items * 2
        tape = "".join(
            f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:24px;">'
            f'<span style="font-size:8px;color:#1f2937;letter-spacing:.1em;">{lab}</span>'
            f'<span style="font-size:11px;color:{col};font-weight:700;">{val}</span>'
            f'<span style="color:#0a0f1a;">|</span></span>'
            for lab, val, col in doubled
        )
        st.markdown(f"""
        <div style="overflow:hidden;white-space:nowrap;background:#030507;
                    border-bottom:1px solid #0a0f1a;padding:5px 0;">
          <span style="display:inline-flex;animation:ticker 24s linear infinite;">{tape}</span>
        </div>""", unsafe_allow_html=True)

    # ── PROGRESS ──────────────────────────────────────────────────────────────
    if running:
        st.progress(min(cur_month / max(total_months, 1), 1.0),
                    text=f"⚙️  Simulating Month {cur_month} of {total_months}…")

    # ── KPI CARDS ─────────────────────────────────────────────────────────────
    if last:
        bm  = last.get("burn_rate",1) / max(1, last.get("revenue",1))
        rwy = last.get("runway_months", 99)
        rev_delta = ((last.get("revenue",0) - prev.get("revenue",1)) / max(1, prev.get("revenue",1))) * 100

        # Row 1: Revenue, Users, Cash
        c1, c2, c3 = st.columns(3)
        rwy_col = C["red"] if rwy < 3 else C["amber"] if rwy < 6 else C["blue"]
        with c1: st.markdown(kpi_card("Monthly Revenue", fm(last.get("revenue",0)), f"{rev_delta:+.1f}% mo/mo", C["green"]), unsafe_allow_html=True)
        with c2: st.markdown(kpi_card("Active Users",    fn(last.get("users",0)), f"{last.get('engineers',0)} engineers on team", C["purple"]), unsafe_allow_html=True)
        with c3: st.markdown(kpi_card("Cash Position",   fm(last.get("cash",0)), f"{rwy:.1f} months runway", rwy_col), unsafe_allow_html=True)

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        # Row 2: Valuation, Burn Multiple, Product Quality
        c4, c5, c6 = st.columns(3)
        bm_col = C["green"] if bm < 1.2 else C["red"]
        td = last.get("technical_debt", 0)
        td_col = C["green"] if td < 0.2 else C["amber"] if td < 0.5 else C["red"]
        with c4: st.markdown(kpi_card("Valuation", fm(last.get("valuation",0)), last.get("last_funding_round","Pre-seed") or "Pre-seed", C["amber"]), unsafe_allow_html=True)
        with c5: st.markdown(kpi_card("Burn Multiple", f"{bm:.2f}×", "Efficient (<1.2x)" if bm < 1.2 else "High burn (>1.2x)", bm_col), unsafe_allow_html=True)
        with c6: st.markdown(kpi_card("Product Quality", f"{last.get('product_quality',0):.1f} / 10", f"Tech Debt: {td:.2f}", td_col), unsafe_allow_html=True)

    st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)

    # ── TABS ─────────────────────────────────────────────────────────────────
    t_war, t_charts, t_stock, t_timeline, t_summary, t_new = st.tabs([
    "💬  War Room", "📊  Analytics", "📈  Stock Market",
    "📋  Timeline", "🏆  Final Report", "↺  New Sim"
    ])

    # ══════════ WAR ROOM ══════════════════════════════════════════════════════
    with t_war:
        st.markdown("<div style='padding:12px 16px 0;'>", unsafe_allow_html=True)

        # Agent legend
        leg_cols = st.columns(5)
        for col, (role, (color, icon)) in zip(leg_cols, AGENT_META.items()):
            with col:
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:5px;
                            font-size:9px;color:{color};letter-spacing:.06em;padding:4px 0;">
                  {icon} {role}
                </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        # Build chat HTML
        bubbles = "".join(
            chat_bubble(e["role"], e["msg"], *AGENT_META.get(e["role"], ("#94a3b8","•")))
            for e in sim_log
        )
        typing_dots = ""
        if running:
            typing_dots = """
            <div style="display:flex;gap:5px;padding:6px 0 6px 44px;">
              <div style="width:6px;height:6px;border-radius:50%;background:#1e2d45;animation:blink 1.1s 0s infinite;"></div>
              <div style="width:6px;height:6px;border-radius:50%;background:#1e2d45;animation:blink 1.1s .2s infinite;"></div>
              <div style="width:6px;height:6px;border-radius:50%;background:#1e2d45;animation:blink 1.1s .4s infinite;"></div>
            </div>"""

        st.markdown(f"""
        <div id="war-room-chat"
             style="height:500px;overflow-y:auto;overflow-x:hidden;
                    padding:8px 4px 8px 0;scroll-behavior:smooth;">
          {bubbles}{typing_dots}
        </div>
        <script>
          (function() {{
            var el = document.getElementById('war-room-chat');
            if (el) el.scrollTop = el.scrollHeight;
          }})();
        </script>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ══════════ ANALYTICS ═════════════════════════════════════════════════════
    with t_charts:
        if not history:
            st.markdown('<div style="padding:40px;text-align:center;color:#1f2937;font-size:12px;">Waiting for simulation data…</div>', unsafe_allow_html=True)
        else:
            df = pd.DataFrame(history)
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

            # Row 1
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            cl, cr = st.columns(2)
            with cl:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df["month"], y=df["revenue"], name="Revenue",
                    fill="tozeroy", fillcolor="rgba(16,185,129,.07)",
                    line=dict(color=C["green"], width=2.5)))
                fig.add_trace(go.Scatter(x=df["month"], y=df["burn_rate"], name="Burn Rate",
                    line=dict(color=C["red"], width=2, dash="dot")))
                fig.update_layout(**base_layout(240, "Revenue vs Burn Rate", "$"))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            with cr:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df["month"], y=df["users"], name="Users",
                    fill="tozeroy", fillcolor="rgba(124,58,237,.07)",
                    line=dict(color=C["purple"], width=2.5)))
                fig.update_layout(**base_layout(240, "User Growth"))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

            # Row 2
            cl, cr = st.columns(2)
            with cl:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df["month"], y=df["valuation"], name="Valuation",
                    fill="tozeroy", fillcolor="rgba(245,158,11,.07)",
                    line=dict(color=C["amber"], width=2.5)))
                ev_colors = {"Pre-Seed Bridge":C["orange"],"Seed":C["green"],
                             "Series A":C["cyan"],"Series B":C["purple"],"IPO":C["pink"]}
                for ev in funding_events:
                    col_ev = ev_colors.get(ev["type"], "#fff")
                    fig.add_vline(x=ev["month"], line_dash="dot", line_color=col_ev,
                        annotation_text=f" {ev['type']}", annotation_font_color=col_ev,
                        annotation_font_size=9)
                fig.update_layout(**base_layout(240, "Valuation + Funding Events", "$"))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

            with cr:
                # Dual-axis chart — use dual_layout to avoid yaxis conflict
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df["month"], y=df["product_quality"],
                    name="Product Quality", line=dict(color=C["cyan"], width=2.5)))
                fig.add_trace(go.Scatter(x=df["month"], y=df["reputation"],
                    name="Reputation", line=dict(color=C["pink"], width=2)))
                if "technical_debt" in df.columns:
                    fig.add_trace(go.Bar(x=df["month"], y=df["technical_debt"] * 10,
                        name="Tech Debt ×10", marker_color="rgba(239,68,68,.22)", yaxis="y2"))
                layout = dual_layout(240, "Quality, Reputation & Tech Debt")
                layout["yaxis"]["range"]  = [0, 11]
                layout["yaxis2"]["range"] = [0, 11]
                fig.update_layout(**layout)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

            # Row 3
            cl, cm, cr = st.columns(3)
            with cl:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df["month"], y=df["cash"],
                    fill="tozeroy", fillcolor="rgba(59,130,246,.07)",
                    line=dict(color=C["blue"], width=2.5), name="Cash"))
                fig.update_layout(**base_layout(200, "Cash Position", "$"))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            with cm:
                rwy_colors = [C["red"] if v<3 else C["amber"] if v<6 else C["green"]
                              for v in df["runway_months"]]
                fig = go.Figure()
                fig.add_trace(go.Bar(x=df["month"], y=df["runway_months"],
                    marker_color=rwy_colors, name="Runway"))
                fig.add_hline(y=6, line_dash="dash", line_color=C["amber"], annotation_text="6mo")
                fig.add_hline(y=3, line_dash="dash", line_color=C["red"],   annotation_text="3mo")
                fig.update_layout(**base_layout(200, "Runway (Months)"))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            with cr:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df["month"], y=df["engineers"],
                    fill="tozeroy", fillcolor="rgba(16,185,129,.07)",
                    line=dict(color=C["green"], width=2.5, shape="hv"), name="Engineers"))
                fig.update_layout(**base_layout(200, "Team Growth"))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

            # Burn multiple bar
            if "burn_rate" in df.columns and "revenue" in df.columns:
                bm_vals   = (df["burn_rate"] / df["revenue"].replace(0,1)).round(2)
                bm_colors = [C["green"] if v<1.2 else C["amber"] if v<2 else C["red"] for v in bm_vals]
                fig = go.Figure()
                fig.add_trace(go.Bar(x=df["month"], y=bm_vals, marker_color=bm_colors, name="Burn Multiple"))
                fig.add_hline(y=1.2, line_dash="dash", line_color=C["red"], annotation_text="1.2× danger")
                layout = base_layout(170, "Burn Multiple by Month")
                layout["showlegend"] = False
                fig.update_layout(**layout)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

            with st.expander("📄 Raw KPI Data"):
                show = [c for c in ["month","revenue","cash","users","burn_rate","runway_months",
                    "engineers","product_quality","reputation","technical_debt",
                    "valuation","founder_ownership","last_funding_round","is_public"] if c in df.columns]
                st.dataframe(df[show].style.format({
                    "revenue":"${:,.0f}","cash":"${:,.0f}","burn_rate":"${:,.0f}",
                    "valuation":"${:,.0f}","runway_months":"{:.1f}",
                    "product_quality":"{:.2f}","reputation":"{:.2f}",
                    "technical_debt":"{:.3f}","founder_ownership":"{:.0%}",
                }), use_container_width=True, height=280)

    # ══════════ STOCK MARKET ══════════════════════════════════════════════════
    with t_stock:
        is_public   = last.get("is_public", False)
        share_price = last.get("share_price", 0)
        market_cap  = last.get("market_cap", 0)

        st.markdown("<div style='padding:16px;'>", unsafe_allow_html=True)
        s1,s2,s3,s4 = st.columns(4)
        with s1: st.markdown(kpi_card("Share Price",
            f"${share_price:.2f}" if is_public else "PRIVATE",
            "Listed on exchange" if is_public else "IPO needs $900K val + 4K users",
            C["green"] if is_public else "#374151"), unsafe_allow_html=True)
        with s2: st.markdown(kpi_card("Market Cap",
            fm(market_cap or last.get("valuation",0)),
            f"Founder owns {last.get('founder_ownership',1)*100:.0f}%", C["amber"]), unsafe_allow_html=True)
        with s3:
            sp_hist = [c.get("close",0) for c in candles]
            if len(sp_hist) > 1:
                pct = (sp_hist[-1] - sp_hist[0]) / max(sp_hist[0], .01) * 100
                st.markdown(kpi_card("Total Return", f"{pct:+.1f}%",
                    f"From IPO ${candles[0].get('open',0):.2f}",
                    C["green"] if pct >= 0 else C["red"]), unsafe_allow_html=True)
            else:
                st.markdown(kpi_card("Total Return","—","Awaiting IPO","#374151"), unsafe_allow_html=True)
        with s4: st.markdown(kpi_card("Candles Recorded", str(len(candles)), "Monthly OHLC", C["cyan"]), unsafe_allow_html=True)

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        if candles:
            months_x = [c.get("month", i+1) for i, c in enumerate(candles)]
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=months_x,
                open=[c["open"]  for c in candles],
                high=[c["high"]  for c in candles],
                low= [c["low"]   for c in candles],
                close=[c["close"] for c in candles],
                increasing_line_color=C["green"],  increasing_fillcolor=C["green"],
                decreasing_line_color=C["red"],    decreasing_fillcolor=C["red"],
                name="OHLC",
            ))
            fig.add_trace(go.Bar(
                x=months_x,
                y=[abs(c["close"]-c["open"]) for c in candles],
                marker_color=[C["green"] if c["close"]>=c["open"] else C["red"] for c in candles],
                opacity=.25, name="Range", yaxis="y2",
            ))
            layout = dual_layout(360, "Stock Price — Monthly OHLC")
            layout["xaxis"]["title"] = "Month"
            layout["yaxis"]["tickprefix"] = "$"
            layout["xaxis_rangeslider_visible"] = False
            fig.update_layout(**layout)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

            # OHLC table
            st.markdown("<div style='font-size:9px;color:#1f2937;letter-spacing:.12em;margin:8px 0 5px;'>OHLC HISTORY</div>", unsafe_allow_html=True)
            ohlc_df = pd.DataFrame([{
                "Month": c.get("month", i+1),
                "Open":  f"${c['open']:.2f}",
                "High":  f"${c['high']:.2f}",
                "Low":   f"${c['low']:.2f}",
                "Close": f"${c['close']:.2f}",
                "Change %": f"{((c['close']-c['open'])/max(c['open'],.01)*100):+.2f}%",
                "Dir": "▲" if c["close"] >= c["open"] else "▼",
            } for i,c in enumerate(reversed(candles[:12]))])
            st.dataframe(ohlc_df, use_container_width=True, hide_index=True, height=250)
        else:
            st.markdown("""
            <div style="height:280px;display:flex;flex-direction:column;align-items:center;
                        justify-content:center;color:#1f2937;gap:8px;font-size:12px;">
              <div style="font-size:32px;">📈</div>
              <div>IPO not yet completed</div>
              <div style="font-size:10px;color:#111827;">Valuation > $900K &amp; Users > 4,000 required</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ══════════ TIMELINE ══════════════════════════════════════════════════════
    with t_timeline:
        st.markdown("<div style='padding:16px;'>", unsafe_allow_html=True)

        if funding_events:
            st.markdown("<div style='font-size:9px;color:#1f2937;letter-spacing:.15em;margin-bottom:10px;'>💰 FUNDING JOURNEY</div>", unsafe_allow_html=True)
            ev_colors = {"Pre-Seed Bridge":C["orange"],"Seed":C["green"],
                         "Series A":C["cyan"],"Series B":C["purple"],"IPO":C["pink"]}
            ev_icons  = {"Pre-Seed Bridge":"🌉","Seed":"🌱","Series A":"💰","Series B":"🚀","IPO":"📈"}
            n = len(funding_events)
            W = max(400, n * 130)
            circles = "".join(
                f'<circle cx="{int((i+.5)*W/n)}" cy="22" r="13" fill="{ev_colors.get(e["type"],"#64748b")}22" stroke="{ev_colors.get(e["type"],"#64748b")}" stroke-width="1.5"/>'
                f'<text x="{int((i+.5)*W/n)}" y="26" text-anchor="middle" font-size="11" fill="{ev_colors.get(e["type"],"#64748b")}">{ev_icons.get(e["type"],"•")}</text>'
                f'<text x="{int((i+.5)*W/n)}" y="44" text-anchor="middle" font-size="7" fill="{ev_colors.get(e["type"],"#64748b")}" font-family="JetBrains Mono,monospace">{e["type"]}</text>'
                f'<text x="{int((i+.5)*W/n)}" y="55" text-anchor="middle" font-size="7" fill="#374151" font-family="JetBrains Mono,monospace">Mo.{e["month"]}</text>'
                for i, e in enumerate(funding_events)
            )
            st.markdown(f"""
            <div style="background:#080c14;border:1px solid #111827;border-radius:10px;
                        padding:12px;overflow-x:auto;margin-bottom:16px;">
              <svg width="100%" viewBox="0 0 {W} 64" preserveAspectRatio="xMidYMid meet">
                <line x1="0" y1="22" x2="{W}" y2="22" stroke="#111827" stroke-width="1.5" stroke-dasharray="4,4"/>
                {circles}
              </svg>
            </div>""", unsafe_allow_html=True)

        if history:
            st.markdown("<div style='font-size:9px;color:#1f2937;letter-spacing:.15em;margin-bottom:8px;'>📊 MONTH-BY-MONTH KPIs</div>", unsafe_allow_html=True)
            rows = ""
            for h in reversed(history):
                m   = h.get("month",0)
                rwy = h.get("runway_months",0)
                td  = h.get("technical_debt",0)
                rc  = C["red"] if rwy<3 else C["amber"] if rwy<6 else C["green"]
                dc  = C["red"] if td>.5 else C["amber"] if td>.2 else C["green"]
                badges = ""
                if h.get("last_funding_round"):
                    badges += f'<span style="font-size:8px;color:#f59e0b;margin-right:4px;">{h["last_funding_round"]}</span>'
                if h.get("is_public"):
                    badges += '<span style="font-size:8px;color:#34d399;">PUBLIC</span>'
                rows += f"""
                <div style="display:grid;grid-template-columns:38px repeat(8,1fr);font-size:10px;
                            padding:6px 12px;border-bottom:1px solid #04050a;color:#4b5563;
                            align-items:center;min-width:0;">
                  <span style="color:#7c3aed;font-weight:700;white-space:nowrap;">M{m}</span>
                  <span style="color:#10b981;white-space:nowrap;">{fm(h.get('revenue',0))}</span>
                  <span style="color:#a78bfa;white-space:nowrap;">{fn(h.get('users',0))}</span>
                  <span style="color:#60a5fa;white-space:nowrap;">{fm(h.get('cash',0))}</span>
                  <span style="color:{rc};white-space:nowrap;">{rwy:.1f}mo</span>
                  <span style="color:#06b6d4;">{h.get('product_quality',0):.1f}</span>
                  <span style="color:#ec4899;">{h.get('reputation',0):.1f}</span>
                  <span style="color:{dc};">{td:.2f}</span>
                  <span style="font-size:8px;overflow:hidden;text-overflow:ellipsis;">{badges}</span>
                </div>"""

            st.markdown(f"""
            <div style="background:#080c14;border:1px solid #111827;border-radius:10px;
                        overflow:hidden;max-height:440px;overflow-y:auto;">
              <div style="display:grid;grid-template-columns:38px repeat(8,1fr);font-size:8px;
                          padding:8px 12px;border-bottom:1px solid #111827;
                          color:#1f2937;letter-spacing:.1em;background:#0c1220;">
                <span>MO</span><span>REV</span><span>USERS</span><span>CASH</span>
                <span>RUNWAY</span><span>PQ</span><span>REP</span><span>DEBT</span><span>ROUND</span>
              </div>
              {rows}
            </div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with t_summary:
        render_outcome_summary(
            history = st.session_state.get("kpi_history", []),
            candles = st.session_state.get("candles", []),
            events  = st.session_state.get("funding_events", []),
            final   = st.session_state.get("final_state"),
            cfg     = st.session_state.get("company_config", {}),
            running = st.session_state.get("sim_running", False),
        )

    # ══════════ NEW SIMULATION ════════════════════════════════════════════════
    with t_new:
        st.markdown("<div style='padding:24px;'>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#080c14;border:1px solid #111827;border-radius:12px;
                    padding:22px;max-width:460px;margin-bottom:16px;">
          <div style="font-size:10px;color:#374151;letter-spacing:.1em;margin-bottom:8px;">
            START A NEW SIMULATION
          </div>
          <div style="font-size:12px;color:#1f2937;line-height:1.7;">
            Configure a new company with different parameters, risk profile,
            or industry and run a fresh 25-month simulation.
          </div>
        </div>""", unsafe_allow_html=True)

        if st.button("↺  Configure New Company"):
            st.session_state["sim_running"] = False
            st.session_state["page"]        = "setup"
            st.session_state["setup_step"]  = 0
            st.rerun()

        fs = st.session_state.get("final_state")
        if fs:
            st.markdown("<div style='font-size:9px;color:#1f2937;letter-spacing:.15em;margin:16px 0 8px;'>LAST SIM FINAL STATE</div>", unsafe_allow_html=True)
            r1,r2,r3 = st.columns(3)
            with r1: st.markdown(kpi_card("Final Revenue",   fm(fs.get("revenue",0)),   "", C["green"]),  unsafe_allow_html=True)
            with r2: st.markdown(kpi_card("Final Users",     fn(fs.get("users",0)),      "", C["purple"]), unsafe_allow_html=True)
            with r3: st.markdown(kpi_card("Final Valuation", fm(fs.get("valuation",0)),  fs.get("last_funding_round",""), C["amber"]), unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Auto-rerun while running ──────────────────────────────────────────────
    if running:
        time.sleep(0.35)
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
def main():
    page = st.session_state.get("page", "setup")
    if page == "setup":
        page_setup()
    else:
        page_sim()

main()