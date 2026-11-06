"""
Zalando SE — Environmental & ESG Performance Dashboard (FY2016–FY2025)
SAM 503 · Lab 4 · Streamlit app

Audience : Sustainability analysts monitoring ESG metrics
Purpose  : Inform the Sustainability Director, who reports findings, risks and
           progress to the Board of Directors.
Data     : Zalando Annual Report 2025 (ESRS sustainability statement, limited
           assurance by KPMG) + Zalando Sustainability Progress Reports 2020–2023.
Run      : streamlit run app.py
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Page setup & palette (categorical order is fixed: S1 blue, S2 orange, S3 aqua)
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Zalando ESG Dashboard", page_icon="🌿", layout="wide")

DATA = Path(__file__).parent / "data"
C = {
    "s1": "#2a78d6", "s2": "#eb6834", "s3": "#1baf7a", "s4": "#eda100",
    "muted": "#8a8984", "grid": "#e6e5e0", "ink": "#0b0b0b", "ink2": "#52514e",
    "good": "#008300", "warn": "#c98500", "bad": "#e34948", "band": "rgba(138,137,132,0.12)",
}
BREAK_YEAR = 2023.5  # methodology break: legacy (≤2023) vs ESRS restated (≥2024)

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.6rem;}
      div[data-testid="stMetricValue"] {font-size: 1.55rem;}
      .note {color:#52514e; font-size:0.85rem;}
      .pill {display:inline-block;padding:2px 10px;border-radius:12px;font-size:0.8rem;
             font-weight:600;margin-right:6px}
      .ok {background:#e3f2e3;color:#1f5e1f} .wa {background:#fdf0d5;color:#7a5200}
      .ba {background:#fbe3e3;color:#8a1c1c}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
@st.cache_data
def load():
    ts = pd.read_csv(DATA / "zalando_timeseries.csv")
    s3 = pd.read_csv(DATA / "zalando_scope3_categories.csv", dtype={"category": str})
    energy = pd.read_csv(DATA / "zalando_energy_mix.csv")
    waste = pd.read_csv(DATA / "zalando_waste.csv")
    targets = pd.read_csv(DATA / "zalando_targets.csv")
    sg = pd.read_csv(DATA / "zalando_social_governance.csv")
    return ts, s3, energy, waste, targets, sg


ts, s3, energy, waste, targets, sg = load()


def base_layout(fig, title, ytitle, height=360):
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color=C["ink"])),
        height=height, margin=dict(l=10, r=10, t=50, b=70),
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter, Arial, sans-serif", color=C["ink2"], size=12),
        legend=dict(orientation="h", yanchor="top", y=-0.16, xanchor="left", x=0),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=False, linecolor=C["grid"], dtick=1, range=[yr[0] - 0.5, yr[1] + 0.5])
    fig.update_yaxes(title=ytitle, gridcolor=C["grid"], zeroline=False, rangemode="tozero")
    return fig


def add_break(fig, show):
    if show and yr[1] > BREAK_YEAR:
        fig.add_vrect(x0=BREAK_YEAR, x1=yr[1] + 0.5, fillcolor=C["band"], line_width=0)
        fig.add_vline(x=BREAK_YEAR, line_dash="dot", line_color=C["muted"])
        fig.add_annotation(x=BREAK_YEAR, y=1.02, yref="paper", text="legacy ← | → ESRS",
                           showarrow=False, xanchor="center", font=dict(size=11, color=C["ink2"]))
    return fig


def fmt(x, d=0):
    return f"{x:,.{d}f}"


# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Filters")
    yr = st.slider("Year range", 2016, 2025, (2016, 2025))
    show_break = st.toggle("Highlight methodology break (2024+)", value=True)
    scope2_basis = st.radio("Scope 2 basis", ["Market-based", "Location-based"], horizontal=True)
    st.divider()
    st.markdown(
        "**Company:** Zalando SE  \n**Sector:** Online fashion & lifestyle retail (NACE G)  \n"
        "**Reporting:** CSRD / ESRS (FY2024–25), Sustainability Progress Reports (FY2017–23)  \n"
        "**Assurance:** Limited — KPMG AG"
    )
    st.caption("Built for SAM 503 Lab 4 · Data compiled Nov 2026")

view = ts[(ts.year >= yr[0]) & (ts.year <= yr[1])].copy()
s2col = "scope2_mb_t" if scope2_basis == "Market-based" else "scope2_lb_t"
cur, prev = ts[ts.year == 2025].iloc[0], ts[ts.year == 2024].iloc[0]

# ---------------------------------------------------------------------------
# Header + KPI row
# ---------------------------------------------------------------------------
st.title("Zalando SE — ESG Performance Dashboard")
st.markdown(
    '<span class="note">For sustainability analysts → Sustainability Director → Board. '
    "FY2016–FY2025 (10 years). 2025 includes ABOUT YOU from 11 July 2025.</span>",
    unsafe_allow_html=True,
)

k = st.columns(6)
k[0].metric("Total GHG 2025 (S1+S2MB+S3)", f"{cur.total_mb_t/1e6:,.2f} Mt",
            f"{(cur.total_mb_t/prev.total_mb_t-1)*100:+.1f}% vs 2024", delta_color="inverse")
k[1].metric("GHG intensity", f"{cur.intensity_t_per_m_eur:,.1f} t/€m",
            f"{(cur.intensity_t_per_m_eur/prev.intensity_t_per_m_eur-1)*100:+.1f}%", delta_color="inverse")
k[2].metric("Scope 1+2 SBT progress", "−17.0%", "target −55% by 2033", delta_color="off")
k[3].metric("Renewable electricity", "100%", "since 2020", delta_color="off")
k[4].metric("Waste diverted from disposal", "97.8%", f"{(41663.7/42615.4-32142.9/33340.1)*100:+.1f} pp")
k[5].metric("Recordable accident rate", "50.8 /1m h", f"{50.8-43.5:+.1f}", delta_color="inverse")

tabs = st.tabs(["🧭 Board summary", "🌍 Carbon", "🎯 Targets", "⚡ Energy & water",
                "♻️ Waste", "👥 Social & governance", "🔎 Data quality & sources"])

# ---------------------------------------------------------------------------
# 1. Board summary — decisions, story, urgent areas, recommendations
# ---------------------------------------------------------------------------
with tabs[0]:
    left, right = st.columns([1.15, 1])
    with left:
        st.subheader("Key ESG questions this dashboard answers")
        q = pd.DataFrame({
            "Question": [
                "1. Is Zalando on track for its science-based targets?",
                "2. Is growth decoupling from emissions?",
                "3. Where are the emission hotspots?",
                "4. Are own operations circular (energy, waste, water)?",
                "5. Are workers safe and fairly paid?",
                "6. Can the Board trust the trend lines?",
            ],
            "Short answer": [
                "On track for 2033 linear pathway (S1+2 −17%, S3 cat.1+4 −10.6% vs 2022), but missed 2025 supplier-SBT (74% vs 90%) and private-label targets.",
                "Not yet: revenue +16.8% and total GHG +20.2% in 2025 → intensity +2.9%.",
                "Purchased goods (79.6%) and upstream logistics (12.1%) = 91.7% of the footprint.",
                "Mostly: 100% renewable power, 97.8% waste diverted — but natural-gas use +12% and landfill 3.4× vs 2024.",
                "Mixed: adjusted pay gap 1.4%, but accident rate +17% and turnover 18%.",
                "Only within a method era: Scope 3 restated −39% for 2024; ESRS ≠ SBT boundary.",
            ],
        })
        st.markdown("\n".join(["| Question | Short answer |", "|---|---|"] +
                               [f"| {a} | {b} |" for a, b in zip(q.Question, q["Short answer"])]))

        st.subheader("The story the data tells")
        st.markdown(
            "- **Own operations are largely decarbonised.** Scope 1+2 fell 81% vs 2017 on an "
            "operational-control basis and electricity has been 100% renewable since 2020 — "
            "but they are **< 1%** of the footprint.\n"
            "- **The value chain is the climate problem.** Scope 3 is **99.5%** of emissions; "
            "product manufacturing alone is ~2.0 Mt CO₂e.\n"
            "- **Growth is outpacing efficiency.** The ABOUT YOU acquisition and 11% more orders "
            "pushed absolute emissions up 20% in 2025, while intensity per €m revenue rose 2.9%.\n"
            "- **Accounting changes dominate the 10-year chart.** The drop from 4.8 Mt (2023) to "
            "2.1 Mt (2024) is a **methodology restatement, not a real reduction**."
        )
    with right:
        st.subheader("Areas needing urgent attention")
        st.markdown(
            '<span class="pill ba">HIGH</span> **Supplier SBT engagement missed** — 74.1% vs 90% '
            "target; brand partners only 72.9%.<br>"
            '<span class="pill ba">HIGH</span> **No climate transition plan (E1-1)** — timeline '
            "“undefined”; a gap investors and ESRS will scrutinise.<br>"
            '<span class="pill wa">MED</span> **Logistics safety** — recordable accidents 984 → 1,135; '
            "rate 43.5 → 50.8 per 1m hours.<br>"
            '<span class="pill wa">MED</span> **Growth & ABOUT YOU integration** — Scope 1 +24%, landfill '
            "105 → 364 t; ABOUT YOU not yet inside SBT boundary.<br>"
            '<span class="pill ok">LOW</span> **Disclosure gaps** — training hours, engagement score, '
            "% suppliers audited not reported.",
            unsafe_allow_html=True,
        )
        st.subheader("Recommendations")
        st.markdown(
            "1. **Make supplier SBTs a sourcing gate** for the top brand partners (Cat. 1 = 2.0 Mt) and "
            "co-fund renewable energy at Tier 1–2 wet-processing mills.\n"
            "2. **Publish a time-bound transition plan** in FY2026 that brings ABOUT YOU into the 2033 "
            "SBT boundary and quantifies levers (materials −10%, energy −60%, circularity −5%).\n"
            "3. **Finish heat-pump retrofits and fleet electrification** at fulfilment centres to reverse "
            "the 2025 rise in natural-gas use.\n"
            "4. **Launch a logistics H&S programme** with a public accident-rate target.\n"
            "5. **Report on a consistent restated series** (re-baseline 2022–2025) so the Board can see "
            "real, like-for-like trends."
        )

# ---------------------------------------------------------------------------
# 2. Carbon
# ---------------------------------------------------------------------------
with tabs[1]:
    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=view.year, y=view.scope1_t, name="Scope 1", mode="lines+markers",
                                 line=dict(color=C["s1"], width=2), marker=dict(size=8)))
        fig.add_trace(go.Scatter(x=view.year, y=view[s2col], name=f"Scope 2 ({scope2_basis})",
                                 mode="lines+markers", line=dict(color=C["s2"], width=2),
                                 marker=dict(size=8), connectgaps=False))
        base_layout(fig, "Own operations: Scope 1 & 2", "tCO₂e")
        st.plotly_chart(add_break(fig, show_break), use_container_width=True)
    with c2:
        fig = go.Figure(go.Bar(x=view.year, y=view.scope3_t / 1e6, name="Scope 3",
                               marker=dict(color=C["s3"], cornerradius=4),
                               hovertemplate="%{x}: %{y:.2f} Mt<extra></extra>"))
        base_layout(fig, "Value chain: Scope 3 (Mt CO₂e)", "Mt CO₂e")
        st.plotly_chart(add_break(fig, show_break), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        d = s3.sort_values("t_2025")
        fig = go.Figure()
        fig.add_trace(go.Bar(y="Cat " + d.category + " · " + d.name, x=d.t_2024 / 1000, name="2024 (restated)",
                             orientation="h", marker=dict(color=C["muted"], cornerradius=4)))
        fig.add_trace(go.Bar(y="Cat " + d.category + " · " + d.name, x=d.t_2025 / 1000, name="2025",
                             orientation="h", marker=dict(color=C["s3"], cornerradius=4),
                             text=[f"{v/1000:,.1f}" for v in d.t_2025], textposition="outside"))
        base_layout(fig, "Scope 3 hotspots by GHG Protocol category", "", height=420)
        fig.update_layout(barmode="group", hovermode="y unified", bargap=0.25, bargroupgap=0.1)
        fig.update_xaxes(title="kt CO₂e", dtick=None, showgrid=True, gridcolor=C["grid"],
                         range=[0, d.t_2025.max() / 1000 * 1.25])
        fig.update_traces(cliponaxis=False)
        fig.update_yaxes(title=None, rangemode=None)
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        fig = go.Figure(go.Scatter(x=view.year, y=view.intensity_t_per_m_eur, mode="lines+markers",
                                   line=dict(color=C["s1"], width=2), marker=dict(size=8),
                                   name="Intensity"))
        base_layout(fig, "GHG intensity (S1+S2MB+S3) per € m revenue", "tCO₂e / € m", height=420)
        st.plotly_chart(add_break(fig, show_break), use_container_width=True)
    share = s3.t_2025 / s3.t_2025.sum()
    st.caption(f"2025: Cat. 1 = {share.iloc[0]:.1%} and Cat. 4 = {share.iloc[3]:.1%} of Scope 3. "
               "2017–2023 values use the legacy method (operational control); 2024–2025 use the ESRS "
               "boundary and the 2025 restated product-emissions method — do not compare across the break.")

# ---------------------------------------------------------------------------
# 3. Targets
# ---------------------------------------------------------------------------
with tabs[2]:
    st.subheader("Science-based targets — progress vs linear pathway")
    t = targets.copy()
    rows = []
    for _, r in t.iterrows():
        if pd.notna(r.base_year) and r.target_type in ("Near-term SBT", "Near-term SBT (WB2C)"):
            years_elapsed = 2025 - r.base_year
            expected = r.target_reduction * years_elapsed / (r.target_year - r.base_year)
            rows.append((r.metric, r.progress_2025, expected, r.target_reduction))
    c1, c2 = st.columns([1, 1])
    with c1:
        fig = go.Figure()
        names = [x[0] for x in rows]
        fig.add_trace(go.Bar(y=names, x=[x[3] * 100 for x in rows], orientation="h",
                             name="2033 target", marker=dict(color=C["grid"], cornerradius=4)))
        fig.add_trace(go.Bar(y=names, x=[x[1] * 100 for x in rows], orientation="h",
                             name="Achieved by 2025", marker=dict(color=C["s1"], cornerradius=4)))
        fig.add_trace(go.Scatter(y=names, x=[x[2] * 100 for x in rows], mode="markers",
                                 name="Linear pathway 2025", marker=dict(symbol="line-ns-open", size=26,
                                 color=C["ink"], line=dict(width=3))))
        base_layout(fig, "Reduction vs 2022 baseline (%)", "", height=300)
        fig.update_layout(barmode="overlay", hovermode="y unified")
        fig.update_xaxes(title="% reduction", dtick=10, range=[0, 60])
        fig.update_yaxes(rangemode=None)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        yrs = list(range(2022, 2034))
        base = 6342
        path = [base * (1 - 0.55 * (y - 2022) / 11) for y in yrs]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=yrs, y=path, name="SBT linear path (−55% by 2033)", mode="lines",
                                 line=dict(color=C["muted"], dash="dash", width=2)))
        fig.add_trace(go.Scatter(x=[2022, 2025], y=[base, base * (1 - 0.17)], name="Actual (SBT boundary)",
                                 mode="lines+markers", line=dict(color=C["s1"], width=2), marker=dict(size=9)))
        fig.add_trace(go.Scatter(x=[2033], y=[base * 0.45], name="2033 target", mode="markers",
                                 marker=dict(symbol="star", size=14, color=C["good"])))
        base_layout(fig, "Scope 1+2 (MB) pathway — SBT boundary, excl. ABOUT YOU",
                    "tCO₂e", height=300)
        fig.update_xaxes(range=[2021.5, 2033.5])
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("All targets")
    tt = t[["metric", "target_type", "base_year", "target_year", "target_reduction", "progress_2025",
            "status_note"]].copy()
    tt["target_reduction"] = (tt.target_reduction * 100).round(1).astype(str) + "%"
    tt["progress_2025"] = (tt.progress_2025 * 100).round(1).astype(str) + "%"
    tt["base_year"] = tt.base_year.fillna(0).astype(int).astype(str).replace("0", "—")
    tt.columns = ["Metric", "Target type", "Base year", "Target year", "Target reduction",
                  "2025 progress", "Note"]
    st.dataframe(tt, hide_index=True, use_container_width=True)
    st.caption("Source: Zalando AR2025, E1-4 (pp.164–166). Target boundary = operational control, "
               "excluding ABOUT YOU; this differs from the ESRS E1-6 inventory on the Carbon tab.")

# ---------------------------------------------------------------------------
# 4. Energy & water
# ---------------------------------------------------------------------------
with tabs[3]:
    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure(go.Scatter(x=view.year, y=view.energy_mwh / 1000, mode="lines+markers",
                                   line=dict(color=C["s1"], width=2), marker=dict(size=8),
                                   name="Total energy"))
        base_layout(fig, "Total energy consumption (GWh)", "GWh")
        st.plotly_chart(add_break(fig, show_break), use_container_width=True)
    with c2:
        e = energy.copy()
        fig = go.Figure()
        for col, nm, colr in (("mwh_2024", "2024", C["muted"]), ("mwh_2025", "2025", C["s1"])):
            fig.add_trace(go.Bar(y=e.source, x=e[col] / 1000, name=nm, orientation="h",
                                 marker=dict(color=colr, cornerradius=4)))
        base_layout(fig, "Energy mix by source (GWh)", "")
        fig.update_layout(barmode="group", hovermode="y unified")
        fig.update_xaxes(title=None, dtick=None, range=None)
        fig.update_yaxes(rangemode=None, autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)
    w = st.columns(4)
    w[0].metric("Renewable share of total energy", "73.2%", "+3.9 pp")
    w[1].metric("Energy intensity", "16.1 MWh/€m", "-0.6", delta_color="inverse")
    w[2].metric("Water withdrawal", "278,409 m³", "+21.4%", delta_color="inverse")
    w[3].metric("Water intensity", "2.3 m³/€m", "+0.1", delta_color="inverse")
    st.caption("Water reporting starts with ESRS (FY2024). Only the Łódź fulfilment centre is in a "
               "high water-risk area (2,171 m³ consumption). Water is low-materiality for own operations; "
               "the real water risk sits in Tier 2 wet processing (Scope 3).")

# ---------------------------------------------------------------------------
# 5. Waste
# ---------------------------------------------------------------------------
with tabs[4]:
    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure(go.Bar(x=view.year, y=view.waste_t / 1000, name="Operational waste",
                               marker=dict(color=C["s4"], cornerradius=4)))
        base_layout(fig, "Operational waste generated (kt)", "kt")
        st.plotly_chart(add_break(fig, show_break), use_container_width=True)
    with c2:
        wd = waste[waste.group == "Disposal"]
        fig = go.Figure()
        for col, nm, colr in (("t_2024", "2024", C["muted"]), ("t_2025", "2025", C["bad"])):
            fig.add_trace(go.Bar(x=wd.route, y=wd[col], name=nm, marker=dict(color=colr, cornerradius=4)))
        base_layout(fig, "Waste directed to disposal (t) — small but rising landfill", "tonnes")
        fig.update_layout(barmode="group")
        fig.update_xaxes(dtick=None, range=None)
        st.plotly_chart(fig, use_container_width=True)
    m = st.columns(4)
    m[0].metric("Total waste 2025", "42,615 t", "+27.8%", delta_color="inverse")
    m[1].metric("Recycled", "40,571 t", "95.2% of total", delta_color="off")
    m[2].metric("Landfilled", "364 t", "3.4× 2024", delta_color="inverse")
    m[3].metric("Hazardous", "53.6 t", "-32%")
    st.caption("Waste is mainly cardboard/paper from fulfilment centres. Source: AR2025 E5-5 p.185; "
               "2018–2023 from Sustainability Progress Reports.")

# ---------------------------------------------------------------------------
# 6. Social & governance
# ---------------------------------------------------------------------------
with tabs[5]:
    c1, c2 = st.columns([1.1, 1])
    with c1:
        st.subheader("Social & governance KPIs (FY2025 vs FY2024)")
        tbl = sg.copy()
        tbl["Change"] = tbl.v_2025 - tbl.v_2024
        tbl = tbl.rename(columns={"pillar": "Pillar", "kpi": "KPI", "v_2025": "2025", "v_2024": "2024",
                                  "unit": "Unit", "source": "Source"})
        st.dataframe(tbl[["Pillar", "KPI", "2025", "2024", "Change", "Unit", "Source"]],
                     hide_index=True, use_container_width=True, height=460)
    with c2:
        fig = go.Figure()
        cats = ["Pay gap<br>unadjusted", "Pay gap<br>adjusted", "Women<br>workforce", "Women<br>top mgmt",
                "Women<br>superv. board"]
        v24 = [15.4, 1.4, 47.5, 36.9, 55.6]
        v25 = [14.5, 1.4, 47.3, 37.4, 55.6]
        fig.add_trace(go.Bar(x=cats, y=v24, name="2024", marker=dict(color=C["muted"], cornerradius=4)))
        fig.add_trace(go.Bar(x=cats, y=v25, name="2025", marker=dict(color=C["s1"], cornerradius=4),
                             text=[f"{v}%" for v in v25], textposition="outside"))
        base_layout(fig, "Gender equity (%)", "%", height=300)
        fig.update_layout(barmode="group")
        fig.update_xaxes(dtick=None, range=None)
        st.plotly_chart(fig, use_container_width=True)

        hs = pd.DataFrame({"year": [2024, 2025], "rate": [43.5, 50.8], "lta": [12.7, 9.9]})
        fig = go.Figure()
        fig.add_trace(go.Bar(x=["Recordable<br>accidents", "Logistics<br>lost-time"], y=[43.5, 12.7], name="2024",
                             marker=dict(color=C["muted"], cornerradius=4)))
        fig.add_trace(go.Bar(x=["Recordable<br>accidents", "Logistics<br>lost-time"], y=[50.8, 9.9], name="2025",
                             marker=dict(color=C["s2"], cornerradius=4), text=["50.8", "9.9"],
                             textposition="outside"))
        base_layout(fig, "Health & safety (rate per 1m hours worked)", "per 1m hours", height=280)
        fig.update_layout(barmode="group")
        fig.update_xaxes(dtick=None, range=None)
        st.plotly_chart(fig, use_container_width=True)

    fig = go.Figure(go.Scatter(x=view.year, y=view.employees, mode="lines+markers",
                               line=dict(color=C["s1"], width=2), marker=dict(size=8), name="Employees"))
    base_layout(fig, "Employees (as reported in annual key figures)", "employees", height=280)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Governance: two-tier board — 9-member supervisory board (6 shareholder + 3 employee "
               "representatives); 5 of 6 shareholder reps independent; ESG modifier in management LTI "
               "(50% GHG targets, 50% D&I); 0 confirmed corruption incidents.")

# ---------------------------------------------------------------------------
# 7. Data quality & sources
# ---------------------------------------------------------------------------
with tabs[6]:
    st.subheader("How far can each number be trusted?")
    dq = pd.DataFrame({
        "Data": ["Scope 1 & 2 (2024–25)", "Scope 3 (2024–25)", "Scope 3 (2017–23)", "Energy, waste, water",
                 "Workforce & pay", "Governance", "Financials"],
        "Quality score (Lab 1)": [90, 80, 55, 100, 85, 100, 100],
        "Why": [
            "ESRS E1-6, limited assurance (KPMG); ABOUT YOU only from Jul-2025",
            "<1% primary data; 2024 restated −39.3% for new Higg-MSI/footwear method",
            "Legacy method, not restated — use only for direction within that era",
            "ESRS E1-5/E3-4/E5-5, limited assurance; water consumption estimated (10% of withdrawal)",
            "Company-specific definitions (turnover incl. involuntary; rate per 1m hours)",
            "Corporate governance statement & remuneration report",
            "Audited consolidated financial statements",
        ],
    })
    fig = go.Figure(go.Bar(y=dq.Data, x=dq["Quality score (Lab 1)"], orientation="h",
                           marker=dict(color=[C["good"] if v >= 80 else C["warn"] if v >= 60 else C["bad"]
                                              for v in dq["Quality score (Lab 1)"]], cornerradius=4),
                           text=dq["Quality score (Lab 1)"], textposition="outside"))
    base_layout(fig, "Data quality score (0–100; ≥80 high, 60–79 acceptable, <60 caution)", "", height=320)
    fig.update_xaxes(range=[0, 110], dtick=20)
    fig.update_yaxes(rangemode=None, autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(dq, hide_index=True, use_container_width=True)

    st.subheader("Full 10-year dataset")
    st.dataframe(ts, hide_index=True, use_container_width=True)
    st.download_button("Download time series (CSV)", ts.to_csv(index=False).encode(),
                       "zalando_esg_timeseries.csv", "text/csv")
    st.markdown(
        "**Sources**  \n"
        "- Zalando SE Annual Report 2025 — Sustainability statement (ESRS E1, E3, E5, S1, S2, G1), key figures, "
        "remuneration report.  \n"
        "- Zalando SE Sustainability Progress Reports 2020, 2022, 2023 (FY2017–FY2023 GHG, energy, waste).  \n"
        "- Revenue, adjusted EBIT and employee counts FY2016–FY2023 transcribed from Zalando annual reports "
        "(verify against originals before external use)."
    )
