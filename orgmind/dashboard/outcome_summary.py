"""
OrgMind — Outcome Summary Screen
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOW TO INTEGRATE into dashboard/app.py (v2):
─────────────────────────────────────────────
1. At the top of app.py, add:
       from dashboard.outcome_summary import render_outcome_summary

2. In page_sim(), find the tabs line:
       t_war, t_charts, t_stock, t_timeline, t_new = st.tabs([...])
   Replace with:
       t_war, t_charts, t_stock, t_timeline, t_summary, t_new = st.tabs([
           "💬  War Room", "📊  Analytics", "📈  Stock Market",
           "📋  Timeline", "🏆  Final Report", "↺  New Sim"
       ])

3. Add a new tab block after t_timeline:
       with t_summary:
           render_outcome_summary(
               history   = st.session_state.get("kpi_history", []),
               candles   = st.session_state.get("candles", []),
               events    = st.session_state.get("funding_events", []),
               final     = st.session_state.get("final_state"),
               cfg       = st.session_state.get("company_config", {}),
               running   = st.session_state.get("sim_running", False),
           )
"""

import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import math

# ── colour palette (same as app.py v2) ───────────────────────────────────────
C = dict(
    purple="#7c3aed", cyan="#06b6d4", green="#10b981",
    amber="#f59e0b",  red="#ef4444",  pink="#ec4899",
    blue="#3b82f6",   orange="#f97316",
)

def _fm(v):
    if not v: return "$0"
    if v >= 1_000_000: return f"${v/1_000_000:.2f}M"
    if v >= 1_000:     return f"${v/1_000:.1f}K"
    return f"${int(v)}"

def _fn(v):
    if not v: return "0"
    if v >= 1_000_000: return f"{v/1_000_000:.1f}M"
    if v >= 1_000:     return f"{v/1_000:.1f}K"
    return str(int(v))

def _base(height=220, title=""):
    return dict(
        paper_bgcolor="#080c14", plot_bgcolor="#080c14",
        font=dict(family="JetBrains Mono, monospace", color="#4b5563", size=10),
        margin=dict(l=48, r=16, t=34, b=24),
        height=height,
        title_text=title, title_font_color="#374151", title_font_size=11,
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#111827", font_size=9),
        xaxis=dict(gridcolor="#111827", linecolor="#111827",
                   tickfont=dict(size=9, color="#374151")),
        yaxis=dict(gridcolor="#111827", linecolor="#111827",
                   tickfont=dict(size=9, color="#374151")),
    )


# ══════════════════════════════════════════════════════════════════════════════
# GRADING
# ══════════════════════════════════════════════════════════════════════════════

def _grade(final, history, events, candles):
    """
    Score the simulation across 6 dimensions (0-100 each).
    Returns overall letter grade, score, breakdown dict, and achievements list.
    """
    if not final:
        return "?", 0, {}, []

    scores = {}

    # 1. Growth (users & revenue trajectory)
    initial_rev   = history[0].get("revenue", 1) if history else 1
    initial_users = history[0].get("users", 1) if history else 1
    rev_mult   = final.get("revenue", 0) / max(initial_rev, 1)
    user_mult  = final.get("users", 0)  / max(initial_users, 1)
    growth_raw = (min(rev_mult, 30) / 30 * 50) + (min(user_mult, 18) / 18 * 50)
    scores["Growth"] = min(100, round(growth_raw))

    # 2. Financial health (burn multiple + runway)
    bm  = final.get("burn_rate", 1) / max(final.get("revenue", 1), 1)
    rwy = final.get("runway_months", 0)
    bm_score  = max(0, 100 - (bm - 0.3) * 60)   # perfect at 0.3x, 0 at ~1.97x
    rwy_score = min(100, rwy / 24 * 100)          # 24+ months = 100
    scores["Finance"] = round((bm_score + rwy_score) / 2)

    # 3. Product (quality + reputation + low debt)
    pq   = final.get("product_quality", 0) / 10 * 100
    rep  = final.get("reputation", 0) / 10 * 100
    debt = max(0, 100 - final.get("technical_debt", 0) * 200)
    scores["Product"] = round((pq * 0.4 + rep * 0.4 + debt * 0.2))

    # 4. Funding journey
    round_scores = {None: 0, "Pre-Seed Bridge": 15, "Seed": 35,
                    "Series A": 65, "Series B": 85, "Series C": 95}
    last_round = final.get("last_funding_round")
    funding_score = round_scores.get(last_round, 0)
    if final.get("is_public"):
        funding_score = 100
    scores["Funding"] = funding_score

    # 5. Team (engineers vs revenue ratio, no explosion)
    eng = final.get("engineers", 1)
    rev_per_eng = final.get("revenue", 0) / max(eng, 1)
    team_eff = min(100, rev_per_eng / 200)    # $20K rev/eng = 100%
    scores["Team"] = round(team_eff)

    # 6. Stock performance (if public)
    if candles and len(candles) > 1:
        ipo_price   = candles[0].get("open", 1)
        final_price = candles[-1].get("close", 0)
        stock_ret   = (final_price - ipo_price) / max(ipo_price, 0.01)
        stock_score = min(100, max(0, 50 + stock_ret * 50))
    else:
        stock_score = 20   # not yet public
    scores["Stock"] = round(stock_score)

    overall = round(sum(scores.values()) / len(scores))

    # Letter grade
    if overall >= 85:   grade = "A+"
    elif overall >= 75: grade = "A"
    elif overall >= 65: grade = "B+"
    elif overall >= 55: grade = "B"
    elif overall >= 45: grade = "C"
    elif overall >= 35: grade = "D"
    else:               grade = "F"

    # ── Achievements ─────────────────────────────────────────────────────────
    achievements = []

    if final.get("is_public"):
        achievements.append(("🚀", "IPO Completed", "Took the company public"))
    if final.get("revenue", 0) >= 100_000:
        achievements.append(("💰", "$100K MRR", "Crossed six figures monthly revenue"))
    if final.get("revenue", 0) >= 200_000:
        achievements.append(("💎", "$200K MRR", "Crossed $200K monthly revenue"))
    if final.get("users", 0) >= 10_000:
        achievements.append(("👥", "10K Users", "Reached five-digit user base"))
    if final.get("cash", 0) >= 1_000_000:
        achievements.append(("🏦", "$1M Cash", "Seven figures in the bank"))
    if bm <= 0.5:
        achievements.append(("⚡", "Efficient Burner", "Burn multiple below 0.5x"))
    if final.get("product_quality", 0) >= 9.0:
        achievements.append(("⭐", "World-Class Product", "Quality score 9.0+"))
    if final.get("technical_debt", 0) == 0:
        achievements.append(("🧹", "Zero Tech Debt", "Kept codebase pristine"))
    if final.get("founder_ownership", 0) >= 0.7:
        achievements.append(("👑", "Founder Control", "Kept 70%+ ownership"))
    last_round = final.get("last_funding_round")
    if last_round == "Series B":
        achievements.append(("🦄", "Series B Club", "Closed a Series B round"))
    if candles and len(candles) > 1:
        ret = (candles[-1]["close"] - candles[0]["open"]) / max(candles[0]["open"], 0.01)
        if ret >= 1.0:
            achievements.append(("📈", "2× Bagger", "Stock doubled from IPO price"))
        if ret >= 0.5:
            achievements.append(("📊", "Strong IPO", "Stock up 50%+ from IPO"))

    # ── What went wrong ───────────────────────────────────────────────────────
    warnings = []
    if bm > 1.5:
        warnings.append(("🔥", "High Burn", f"Burn multiple was {bm:.2f}× — capital inefficient"))
    if final.get("runway_months", 99) < 6:
        warnings.append(("⚠️", "Low Runway", f"Only {final.get('runway_months',0):.1f} months runway at end"))
    if final.get("technical_debt", 0) > 0.4:
        warnings.append(("🕷️", "Tech Debt", f"Debt reached {final.get('technical_debt',0):.2f} — slowing velocity"))
    if final.get("engineers", 0) > 15:
        warnings.append(("👷", "Overhiring", f"{final.get('engineers',0)} engineers may be excessive"))
    if final.get("reputation", 0) < 6:
        warnings.append(("📉", "Reputation Risk", "Reputation below 6.0 — churn risk high"))
    if not final.get("is_public") and final.get("valuation", 0) > 900_000:
        warnings.append(("🏦", "IPO Missed", "Qualified for IPO but didn't trigger — check conditions"))

    return grade, overall, scores, achievements, warnings


# ══════════════════════════════════════════════════════════════════════════════
# RADAR CHART
# ══════════════════════════════════════════════════════════════════════════════

def _radar_chart(scores):
    cats = list(scores.keys())
    vals = list(scores.values())
    cats_closed = cats + [cats[0]]
    vals_closed  = vals + [vals[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals_closed, theta=cats_closed,
        fill="toself",
        fillcolor="rgba(124,58,237,0.15)",
        line=dict(color="#7c3aed", width=2),
        name="Performance",
    ))
    fig.add_trace(go.Scatterpolar(
        r=[75] * len(cats_closed), theta=cats_closed,
        line=dict(color="#1e2d45", width=1, dash="dot"),
        name="Target (75)",
        showlegend=True,
    ))
    fig.update_layout(
        paper_bgcolor="#080c14",
        plot_bgcolor="#080c14",
        polar=dict(
            bgcolor="#080c14",
            radialaxis=dict(
                visible=True, range=[0, 100],
                gridcolor="#111827", linecolor="#111827",
                tickfont=dict(size=8, color="#374151"),
                tickvals=[25, 50, 75, 100],
            ),
            angularaxis=dict(
                gridcolor="#111827", linecolor="#1e2d45",
                tickfont=dict(size=10, color="#94a3b8"),
            ),
        ),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9, color="#4b5563")),
        margin=dict(l=40, r=40, t=30, b=30),
        height=300,
        font=dict(family="JetBrains Mono, monospace"),
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# MILESTONE TIMELINE
# ══════════════════════════════════════════════════════════════════════════════

def _milestone_chart(history, events):
    """Mini area chart with milestone markers overlaid."""
    if not history:
        return None

    df = pd.DataFrame(history)
    fig = go.Figure()

    # Revenue area
    fig.add_trace(go.Scatter(
        x=df["month"], y=df["revenue"],
        fill="tozeroy", fillcolor="rgba(124,58,237,0.06)",
        line=dict(color="#7c3aed", width=2),
        name="Revenue",
    ))

    # Funding markers
    ev_colors = {
        "Pre-Seed Bridge": C["orange"], "Seed": C["green"],
        "Series A": C["cyan"],          "Series B": C["purple"],
        "Series C": C["pink"],          "IPO": C["amber"],
    }
    for ev in events:
        col = ev_colors.get(ev["type"], "#fff")
        fig.add_vline(x=ev["month"], line_dash="dot", line_color=col,
                      annotation_text=f" {ev['type']}",
                      annotation_font_color=col, annotation_font_size=8)

    layout = _base(200, "Revenue Journey + Funding Milestones")
    layout["yaxis"]["tickprefix"] = "$"
    fig.update_layout(**layout)
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# STOCK SUMMARY CHART
# ══════════════════════════════════════════════════════════════════════════════

def _stock_summary_chart(candles):
    if not candles:
        return None
    months_x = [c.get("month", i + 1) for i, c in enumerate(candles)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months_x,
        y=[c["close"] for c in candles],
        fill="tozeroy",
        fillcolor="rgba(16,185,129,0.07)",
        line=dict(color=C["green"], width=2.5),
        name="Close Price",
    ))
    # Shade high-low band
    fig.add_trace(go.Scatter(
        x=months_x + months_x[::-1],
        y=[c["high"] for c in candles] + [c["low"] for c in candles[::-1]],
        fill="toself", fillcolor="rgba(16,185,129,0.04)",
        line=dict(color="rgba(0,0,0,0)"),
        name="High-Low Band", showlegend=False,
    ))
    layout = _base(200, "Stock Price (Close + H/L Band)")
    layout["yaxis"]["tickprefix"] = "$"
    fig.update_layout(**layout)
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# MAIN RENDER
# ══════════════════════════════════════════════════════════════════════════════

def render_outcome_summary(history, candles, events, final, cfg, running):
    st.markdown("""
    <style>
    @keyframes fadeUp { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }
    .outcome-anim { animation: fadeUp .5s ease; }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div style='padding:16px;'>", unsafe_allow_html=True)

    # ── Waiting states ────────────────────────────────────────────────────────
    if running:
        st.markdown("""
        <div style="height:300px;display:flex;flex-direction:column;align-items:center;
                    justify-content:center;gap:12px;color:#1f2937;">
          <div style="font-size:28px;animation:pulse 1.5s infinite;">⚙️</div>
          <div style="font-size:11px;letter-spacing:.12em;color:#374151;">
            SIMULATION IN PROGRESS…
          </div>
          <div style="font-size:10px;color:#1f2937;">
            Final Report will appear here when simulation completes.
          </div>
        </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        return

    if not final:
        st.markdown("""
        <div style="height:300px;display:flex;flex-direction:column;align-items:center;
                    justify-content:center;gap:12px;">
          <div style="font-size:28px;">🏆</div>
          <div style="font-size:11px;letter-spacing:.12em;color:#374151;">
            AWAITING SIMULATION
          </div>
          <div style="font-size:10px;color:#1f2937;">
            Run a simulation to see your Final Report here.
          </div>
        </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # ── Grade + scores ────────────────────────────────────────────────────────
    grade, overall, scores, achievements, warnings = _grade(final, history, events, candles)

    grade_colors = {
        "A+": C["green"], "A": C["green"],
        "B+": C["cyan"],  "B": C["cyan"],
        "C":  C["amber"], "D": C["orange"], "F": C["red"],
    }
    grade_color = grade_colors.get(grade, "#94a3b8")

    grade_descriptions = {
        "A+": "Exceptional — top 5% outcome. Venture-scale success.",
        "A":  "Outstanding — strong growth, efficient capital deployment.",
        "B+": "Very Good — solid fundamentals with room to optimize.",
        "B":  "Good — sustainable business with healthy metrics.",
        "C":  "Average — functional but inefficient in key areas.",
        "D":  "Below average — significant structural issues.",
        "F":  "Failed — company did not achieve viability.",
    }

    # ── Hero grade card ───────────────────────────────────────────────────────
    company_name = cfg.get("name", "Your Company")
    months_run   = len(history)
    bm_final = final.get("burn_rate", 1) / max(final.get("revenue", 1), 1)

    st.markdown(f"""
    <div class="outcome-anim" style="background:linear-gradient(135deg,#0d0b1a,#0c1220,#070d18);
         border:1px solid #1e2d45;border-radius:16px;padding:28px 32px;
         display:flex;align-items:center;gap:32px;flex-wrap:wrap;margin-bottom:16px;
         position:relative;overflow:hidden;">
      <!-- big background grade -->
      <div style="position:absolute;right:-12px;top:-10px;font-size:140px;font-weight:900;
                  color:{grade_color}06;font-family:'JetBrains Mono',monospace;
                  pointer-events:none;line-height:1;">{grade}</div>

      <!-- grade circle -->
      <div style="flex-shrink:0;width:96px;height:96px;border-radius:50%;
                  background:{grade_color}18;border:3px solid {grade_color}60;
                  display:flex;flex-direction:column;align-items:center;justify-content:center;">
        <div style="font-size:32px;font-weight:900;color:{grade_color};line-height:1;">{grade}</div>
        <div style="font-size:9px;color:{grade_color}80;margin-top:2px;">{overall}/100</div>
      </div>

      <!-- text block -->
      <div style="flex:1;min-width:200px;">
        <div style="font-size:8px;letter-spacing:.3em;color:#1f2937;margin-bottom:4px;">
          FINAL REPORT · {months_run} MONTHS
        </div>
        <div style="font-size:22px;font-weight:900;color:#e2e8f0;line-height:1.2;margin-bottom:6px;">
          {company_name}
        </div>
        <div style="font-size:10px;color:#374151;line-height:1.5;">
          {cfg.get('industry','SaaS')} · Founder: {cfg.get('founder','Anonymous')} · 
          Risk: {cfg.get('risk','balanced').title()}
        </div>
        <div style="font-size:11px;color:{grade_color};margin-top:8px;font-style:italic;">
          "{grade_descriptions.get(grade,'')}"
        </div>
      </div>

      <!-- stat pills -->
      <div style="display:flex;flex-direction:column;gap:7px;flex-shrink:0;">
        {"".join(f'''<div style="display:flex;justify-content:space-between;gap:20px;
                background:#04050a;border:1px solid #111827;border-radius:7px;
                padding:7px 13px;font-family:'JetBrains Mono',monospace;">
          <span style="font-size:8px;color:#1f2937;letter-spacing:.1em;">{lab}</span>
          <span style="font-size:11px;color:{col};font-weight:700;">{val}</span>
        </div>''' for lab, val, col in [
            ("REVENUE",   _fm(final.get("revenue",0)),     C["green"]),
            ("USERS",     _fn(final.get("users",0)),       C["purple"]),
            ("VALUATION", _fm(final.get("valuation",0)),   C["amber"]),
            ("CASH",      _fm(final.get("cash",0)),        C["blue"]),
            ("BURN ×",    f"{bm_final:.2f}",               C["green"] if bm_final<1.2 else C["red"]),
            ("STATUS",    "📈 PUBLIC" if final.get("is_public") else "🔒 PRIVATE",
                          C["green"] if final.get("is_public") else "#374151"),
        ])}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Score breakdown + radar ───────────────────────────────────────────────
    col_radar, col_bars = st.columns([1, 1])

    with col_radar:
        st.plotly_chart(_radar_chart(scores), use_container_width=True,
                        config={"displayModeBar": False})

    with col_bars:
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        for dim, score in scores.items():
            bar_color = C["green"] if score >= 75 else C["amber"] if score >= 50 else C["red"]
            grade_label = "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 55 else "D" if score >= 40 else "F"
            st.markdown(f"""
            <div style="margin-bottom:11px;">
              <div style="display:flex;justify-content:space-between;align-items:center;
                          margin-bottom:5px;">
                <span style="font-size:9px;color:#4b5563;letter-spacing:.08em;">{dim.upper()}</span>
                <span style="font-size:10px;color:{bar_color};font-weight:700;">{score}/100</span>
              </div>
              <div style="height:5px;background:#0c1220;border-radius:3px;overflow:hidden;">
                <div style="height:100%;width:{score}%;background:linear-gradient(90deg,{bar_color}cc,{bar_color});
                            border-radius:3px;transition:width .6s ease;"></div>
              </div>
            </div>""", unsafe_allow_html=True)

    # ── Charts row ────────────────────────────────────────────────────────────
    cl, cr = st.columns(2)
    with cl:
        fig = _milestone_chart(history, events)
        if fig:
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with cr:
        if candles:
            fig = _stock_summary_chart(candles)
            if fig:
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown("""
            <div style="height:200px;display:flex;align-items:center;justify-content:center;
                        background:#080c14;border:1px solid #111827;border-radius:10px;
                        color:#1f2937;font-size:11px;">No stock data — company stayed private</div>
            """, unsafe_allow_html=True)

    # ── Achievements + Warnings ───────────────────────────────────────────────
    col_ach, col_warn = st.columns(2)

    with col_ach:
        st.markdown("""
        <div style="font-size:9px;color:#1f2937;letter-spacing:.15em;
                    margin-bottom:10px;margin-top:8px;">🏅 ACHIEVEMENTS</div>
        """, unsafe_allow_html=True)
        if achievements:
            cards = ""
            for icon, title, desc in achievements:
                cards += f"""
                <div style="display:flex;align-items:flex-start;gap:10px;
                            background:#080c14;border:1px solid #111827;border-radius:9px;
                            padding:11px 14px;margin-bottom:7px;">
                  <div style="font-size:18px;flex-shrink:0;margin-top:1px;">{icon}</div>
                  <div>
                    <div style="font-size:10px;font-weight:700;color:#e2e8f0;margin-bottom:2px;">{title}</div>
                    <div style="font-size:9px;color:#374151;">{desc}</div>
                  </div>
                </div>"""
            st.markdown(cards, unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size:10px;color:#1f2937;">No achievements unlocked yet.</div>', unsafe_allow_html=True)

    with col_warn:
        st.markdown("""
        <div style="font-size:9px;color:#1f2937;letter-spacing:.15em;
                    margin-bottom:10px;margin-top:8px;">⚠️ AREAS TO IMPROVE</div>
        """, unsafe_allow_html=True)
        if warnings:
            cards = ""
            for icon, title, desc in warnings:
                cards += f"""
                <div style="display:flex;align-items:flex-start;gap:10px;
                            background:#080c14;border:1px solid #ef444415;border-radius:9px;
                            padding:11px 14px;margin-bottom:7px;">
                  <div style="font-size:18px;flex-shrink:0;margin-top:1px;">{icon}</div>
                  <div>
                    <div style="font-size:10px;font-weight:700;color:#fca5a5;margin-bottom:2px;">{title}</div>
                    <div style="font-size:9px;color:#374151;">{desc}</div>
                  </div>
                </div>"""
            st.markdown(cards, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:#080c14;border:1px solid #052e16;border-radius:9px;
                        padding:14px;font-size:10px;color:#34d399;">
              ✅ No critical issues detected. Clean execution.
            </div>""", unsafe_allow_html=True)

    # ── Founder letter ────────────────────────────────────────────────────────
    st.markdown("""
    <div style="font-size:9px;color:#1f2937;letter-spacing:.15em;
                margin-bottom:10px;margin-top:16px;">📝 INVESTOR DEBRIEF</div>
    """, unsafe_allow_html=True)

    letter = _generate_debrief(final, scores, grade, cfg, history, events)
    st.markdown(f"""
    <div style="background:#080c14;border:1px solid #111827;border-radius:12px;
                padding:22px 26px;font-size:12px;line-height:1.9;color:#4b5563;
                font-family:'JetBrains Mono',monospace;white-space:pre-wrap;">
{letter}
    </div>""", unsafe_allow_html=True)

    # ── Recommended next steps ────────────────────────────────────────────────
    st.markdown("""
    <div style="font-size:9px;color:#1f2937;letter-spacing:.15em;
                margin-bottom:10px;margin-top:16px;">🗺️ WHAT SHOULD HAPPEN NEXT</div>
    """, unsafe_allow_html=True)

    next_steps = _next_steps(final, scores, events)
    cols_ns = st.columns(3)
    for i, (ns_icon, ns_title, ns_body) in enumerate(next_steps[:6]):
        with cols_ns[i % 3]:
            st.markdown(f"""
            <div style="background:#080c14;border:1px solid #111827;border-radius:10px;
                        padding:14px;margin-bottom:10px;min-height:100px;">
              <div style="font-size:18px;margin-bottom:7px;">{ns_icon}</div>
              <div style="font-size:10px;font-weight:700;color:#e2e8f0;margin-bottom:4px;">{ns_title}</div>
              <div style="font-size:9px;color:#374151;line-height:1.6;">{ns_body}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DEBRIEF TEXT GENERATOR
# ══════════════════════════════════════════════════════════════════════════════

def _generate_debrief(final, scores, grade, cfg, history, events):
    name     = cfg.get("name", "the company")
    founder  = cfg.get("founder", "the founder")
    months   = len(history)
    rev      = final.get("revenue", 0)
    users    = final.get("users", 0)
    cash     = final.get("cash", 0)
    val      = final.get("valuation", 0)
    rwy      = final.get("runway_months", 0)
    bm       = final.get("burn_rate", 1) / max(rev, 1)
    rnd      = final.get("last_funding_round", "none")
    pub      = final.get("is_public", False)
    eng      = final.get("engineers", 0)
    pq       = final.get("product_quality", 0)

    funding_count = len(events)
    ipo_event = next((e for e in events if e["type"] == "IPO"), None)

    lines = [
        f"To: {founder}",
        f"Re: {name} — {months}-Month Post-Mortem",
        "",
    ]

    # Opening assessment
    if grade in ("A+", "A"):
        lines.append(f"  {name} delivered a standout performance across {months} months of simulation.")
        lines.append(f"  The combination of {_fn(users)} users and {_fm(rev)}/mo revenue demonstrates")
        lines.append(f"  genuine product-market fit. Capital deployment was disciplined — a {bm:.2f}x")
        lines.append(f"  burn multiple is exceptional at this stage.")
    elif grade in ("B+", "B"):
        lines.append(f"  {name} showed solid fundamentals over {months} months. Revenue at {_fm(rev)}/mo")
        lines.append(f"  with {_fn(users)} active users indicates a functioning business. There are")
        lines.append(f"  clear optimization opportunities, particularly in capital efficiency.")
    else:
        lines.append(f"  {name} completed {months} months with mixed results. Some metrics are")
        lines.append(f"  encouraging — {_fn(users)} users and {_fm(rev)}/mo revenue — but structural")
        lines.append(f"  issues remain that would concern institutional investors.")

    lines.append("")

    # Funding narrative
    if ipo_event:
        lines.append(f"  The company successfully IPO'd in Month {ipo_event['month']}, a significant")
        lines.append(f"  milestone. Post-IPO valuation reached {_fm(val)} with {rwy:.1f} months runway.")
    elif rnd and rnd != "none":
        lines.append(f"  Funding progression reached {rnd} — {funding_count} round(s) total.")
        lines.append(f"  Current valuation of {_fm(val)} with {_fm(cash)} in the bank ({rwy:.1f}mo runway).")
    else:
        lines.append(f"  The company has not yet closed an institutional round.")
        lines.append(f"  At {_fm(val)} valuation this is achievable with continued execution.")

    lines.append("")

    # Strengths
    strength_lines = []
    if scores.get("Product", 0) >= 75:
        strength_lines.append(f"  + Product quality of {pq:.1f}/10 with strong reputation is a genuine moat.")
    if scores.get("Finance", 0) >= 75:
        strength_lines.append(f"  + {bm:.2f}x burn multiple demonstrates capital discipline rare at this stage.")
    if scores.get("Growth", 0) >= 75:
        strength_lines.append(f"  + Growth trajectory of {_fn(users)} users signals strong organic adoption.")
    if scores.get("Team", 0) >= 75:
        rev_per_eng = final.get("revenue", 0) / max(eng, 1)
        strength_lines.append(f"  + {_fm(rev_per_eng)}/engineer/mo revenue efficiency — lean and productive team.")

    if strength_lines:
        lines.append("  Strengths:")
        lines.extend(strength_lines)
        lines.append("")

    # Risks
    risk_lines = []
    if bm > 1.5:
        risk_lines.append(f"  - Burn multiple of {bm:.2f}x is a red flag for Series B investors.")
    if rwy < 6:
        risk_lines.append(f"  - {rwy:.1f} months runway creates existential pressure. Raise or cut now.")
    if final.get("technical_debt", 0) > 0.4:
        risk_lines.append(f"  - Technical debt at {final.get('technical_debt',0):.2f} will slow feature velocity.")
    if eng > 15:
        risk_lines.append(f"  - {eng} engineers may be ahead of revenue — monitor cost per employee.")

    if risk_lines:
        lines.append("  Risks:")
        lines.extend(risk_lines)
        lines.append("")

    lines.append(f"  Overall grade: {grade}  ({scores.get('Growth',0)}G · "
                 f"{scores.get('Finance',0)}F · {scores.get('Product',0)}P · "
                 f"{scores.get('Funding',0)}Fn · {scores.get('Team',0)}T · "
                 f"{scores.get('Stock',0)}S)")
    lines.append("")
    lines.append("  — OrgMind AI Board of Directors")

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# NEXT STEPS GENERATOR
# ══════════════════════════════════════════════════════════════════════════════

def _next_steps(final, scores, events):
    steps = []
    bm  = final.get("burn_rate", 1) / max(final.get("revenue", 1), 1)
    rwy = final.get("runway_months", 0)
    rnd = final.get("last_funding_round", "")
    pub = final.get("is_public", False)

    # Always relevant
    if not pub:
        if final.get("valuation", 0) > 900_000 and final.get("users", 0) > 4000:
            steps.append(("🚀", "Prepare for IPO",
                "You meet the valuation and user thresholds. File S-1, "
                "engage underwriters, and target a 6-month IPO timeline."))
        elif rnd == "Series A":
            steps.append(("💰", "Series B Raise",
                "With Series A closed, focus on 12mo of consistent growth "
                "then approach Tier-1 VCs at a 3-5× revenue multiple."))
        elif not rnd:
            steps.append(("🌱", "Close Seed Round",
                "Product quality and early traction justify a Seed raise. "
                "Target $500K–$1.5M to extend runway to 18+ months."))

    if bm > 1.2:
        steps.append(("✂️", "Cut Burn Rate",
            f"Burn multiple of {bm:.2f}× is too high. Freeze non-critical "
            "hires, renegotiate vendor contracts, shift to PLG acquisition."))

    if rwy < 9:
        steps.append(("⏱️", "Extend Runway",
            f"Only {rwy:.1f} months runway. Either raise bridge financing "
            "or cut monthly burn by 20% within 60 days."))

    if scores.get("Product", 0) < 60:
        steps.append(("🔧", "Product Sprint",
            "Quality metrics are below benchmark. Dedicate 2 engineers "
            "to a 6-week quality sprint before next growth push."))

    if scores.get("Growth", 0) < 60:
        steps.append(("📣", "Growth Acceleration",
            "User growth is below potential. Invest in content marketing, "
            "referral programs, and reduce onboarding friction."))

    if final.get("technical_debt", 0) > 0.3:
        steps.append(("🧹", "Pay Down Tech Debt",
            f"Debt at {final.get('technical_debt',0):.2f} will compound. "
            "Allocate 20% of engineering capacity to refactoring per sprint."))

    if pub and scores.get("Stock", 0) < 60:
        steps.append(("📊", "Investor Relations",
            "Stock underperforming post-IPO. Increase earnings call frequency, "
            "set conservative guidance, beat on revenue 3 quarters in a row."))

    if scores.get("Team", 0) >= 80 and final.get("engineers", 0) < 8:
        steps.append(("👷", "Scale Engineering",
            "Revenue per engineer is strong — you have headroom to hire. "
            "Add 2–3 senior engineers to accelerate feature delivery."))

    # Pad to at least 3
    if len(steps) < 3:
        steps.append(("🔁", "Run Another Scenario",
            "Try an aggressive risk profile or higher starting capital "
            "to see how variance affects outcomes."))
    if len(steps) < 3:
        steps.append(("📝", "Document Learnings",
            "Export this report and share with your team as a reference "
            "for the next planning cycle."))

    return steps[:6]