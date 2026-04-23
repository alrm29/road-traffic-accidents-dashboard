"""
ROAD TRAFFIC ACCIDENTS — ETHIOPIA 2018–2023
An editorial, news-paper style data dashboard.
Pure Streamlit + Plotly. One signature animation.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="The Road Ledger · Ethiopia",
    page_icon="•",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ────────────────────────────────────────────────────────────────────────────
# DESIGN TOKENS — editorial / newsroom dark
# ────────────────────────────────────────────────────────────────────────────
INK       = "#0D0E10"   # paper-ink background
PAPER     = "#15161A"   # card surface
PAPER2    = "#1C1E23"   # secondary surface
RULE      = "#2A2D34"   # hair rule
CREAM     = "#EDE6D3"   # main cream text
CREAM_DIM = "#B8B2A3"
MUTED     = "#7A7567"
RED       = "#D94141"   # editorial red (Fatal / alert)
AMBER     = "#E8A33D"   # Serious
TEAL      = "#4FA3A8"   # Slight
NAVY      = "#3A5C82"
OLIVE     = "#8C9560"

SEV_COLORS = {
    "Slight Injury":  TEAL,
    "Serious Injury": AMBER,
    "Fatal Injury":   RED,
}
CAUSE_PALETTE = [RED, AMBER, TEAL, NAVY, OLIVE, "#B87A5A", "#9B6BA0", "#C0624B"]

# ────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS — editorial typography
# ────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,800;9..144,900&family=DM+Mono:wght@400;500&family=Inter:wght@300;400;500;600&display=swap');

* {{ box-sizing: border-box; }}
html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    background: {INK};
    color: {CREAM};
}}
.stApp {{ background: {INK}; }}
.block-container {{ padding: 1.4rem 2.4rem 4rem; max-width: 1460px; }}

/* Subtle paper-grain over whole app */
.stApp::before {{
    content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background-image:
      radial-gradient(rgba(237,230,211,0.018) 1px, transparent 1px);
    background-size: 3px 3px;
    mix-blend-mode: overlay;
}}

/* ── Sidebar masthead ── */
section[data-testid="stSidebar"] {{
    background: {PAPER};
    border-right: 1px solid {RULE};
}}
section[data-testid="stSidebar"] .block-container {{ padding-top: 1.5rem; }}
div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {{
    gap: 1px; display: flex; flex-direction: column;
}}
div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {{
    display: flex !important; align-items: center;
    padding: 10px 14px;
    border-radius: 0;
    cursor: pointer;
    font-size: 13px;
    font-family: 'Inter', sans-serif;
    font-weight: 400;
    color: {CREAM_DIM};
    border-left: 2px solid transparent;
    transition: all 0.15s ease;
}}
div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {{
    background: {PAPER2};
    color: {CREAM};
    border-left-color: {CREAM_DIM};
}}
div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) {{
    background: transparent;
    color: {RED};
    font-weight: 600;
    border-left: 2px solid {RED};
}}
div[data-testid="stSidebar"] .stRadio input[type="radio"] {{ display: none; }}

/* ── Headlines ── */
h1 {{
    font-family: 'Fraunces', serif !important;
    font-weight: 900 !important;
    font-size: 3.4rem !important;
    line-height: 1.02 !important;
    color: {CREAM} !important;
    letter-spacing: -0.035em !important;
    margin: 0 0 0.2rem 0 !important;
}}
h2 {{
    font-family: 'Fraunces', serif !important;
    font-weight: 800 !important;
    font-size: 1.9rem !important;
    color: {CREAM} !important;
    letter-spacing: -0.02em !important;
    margin-top: 0.8rem !important;
}}
h3 {{
    font-family: 'Fraunces', serif !important;
    font-weight: 600 !important;
    font-style: italic;
    font-size: 1.15rem !important;
    color: {CREAM_DIM} !important;
}}

/* ── Kicker — uppercase mono prefix ── */
.kicker {{
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: {RED};
    font-weight: 500;
    margin-bottom: 8px;
}}
.byline {{
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: {MUTED};
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 6px 0;
    border-top: 1px solid {RULE};
    border-bottom: 1px solid {RULE};
    margin: 14px 0 22px;
}}

/* ── Deck / dek: large italic intro paragraph ── */
.deck {{
    font-family: 'Fraunces', serif;
    font-weight: 400;
    font-style: italic;
    font-size: 1.25rem;
    line-height: 1.5;
    color: {CREAM_DIM};
    max-width: 68ch;
    margin: 0 0 28px 0;
}}

/* ── Pull quote ── */
.pullquote {{
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 1.45rem;
    line-height: 1.35;
    color: {CREAM};
    padding: 18px 24px;
    border-left: 3px solid {RED};
    background: linear-gradient(90deg, rgba(217,65,65,0.06), transparent 80%);
    margin: 20px 0;
    font-style: italic;
}}
.pullquote::before {{ content: "“"; font-size: 2.4rem; color: {RED}; line-height: 0; vertical-align: -0.4em; margin-right: 6px; }}

/* ── Statcards: editorial figure blocks ── */
[data-testid="metric-container"] {{
    background: {PAPER};
    border: 1px solid {RULE};
    border-radius: 2px;
    padding: 14px 16px !important;
    position: relative;
}}
[data-testid="metric-container"]::before {{
    content: "";
    position: absolute; top: 0; left: 0; width: 26px; height: 2px;
    background: {RED};
}}
[data-testid="stMetricValue"] {{
    font-family: 'Fraunces', serif !important;
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    color: {CREAM} !important;
    letter-spacing: -0.02em;
}}
[data-testid="stMetricLabel"] {{
    font-family: 'DM Mono', monospace !important;
    font-size: 10px !important;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: {MUTED} !important;
}}

/* ── Captions ── */
.stCaption, .stCaption p {{
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    color: {MUTED} !important;
    letter-spacing: 0.03em;
}}

/* ── Info / Expander ── */
.stInfo {{
    background: rgba(217,65,65,0.06) !important;
    border: 1px solid rgba(217,65,65,0.25) !important;
    border-left: 3px solid {RED} !important;
    border-radius: 2px !important;
    color: {CREAM_DIM} !important;
    font-size: 13px !important;
}}
.stExpander {{
    background: {PAPER} !important;
    border: 1px solid {RULE} !important;
    border-radius: 2px !important;
}}

/* ── Selects ── */
div[data-baseweb="select"] > div {{
    background: {PAPER2} !important;
    border: 1px solid {RULE} !important;
    color: {CREAM} !important;
    border-radius: 2px !important;
    font-size: 13px !important;
    font-family: 'Inter', sans-serif !important;
}}

/* Page subtitle — dateline */
.dateline {{
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: {MUTED};
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 4px;
}}

hr {{ border-color: {RULE} !important; margin: 1.4rem 0 !important; }}

/* Ticker strip */
.ticker {{
    display: flex; gap: 0; flex-wrap: wrap;
    border-top: 1px solid {RULE};
    border-bottom: 1px solid {RULE};
    padding: 10px 0;
    margin: 8px 0 22px 0;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}}
.ticker .tk {{
    padding: 0 18px;
    color: {CREAM_DIM};
    border-right: 1px solid {RULE};
}}
.ticker .tk:last-child {{ border-right: none; }}
.ticker .tk b {{ color: {CREAM}; font-weight: 600; }}
.ticker .tk .dot {{
    display: inline-block; width: 6px; height: 6px; border-radius: 50%;
    margin-right: 6px; vertical-align: middle;
}}

/* Story-end marker */
.endmark {{
    text-align: center;
    color: {MUTED};
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.3em;
    margin: 36px 0 10px;
}}
.endmark span {{ color: {RED}; font-size: 14px; margin: 0 8px; }}

/* Plot container polish */
.js-plotly-plot .plotly .modebar {{ right: 6px !important; top: 6px !important; }}
</style>
""", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("RTA_Dataset_cleaned.csv")
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()
    if "Type_of_vehicle" in df.columns:
        df["Type_of_vehicle"] = df["Type_of_vehicle"].str.replace(r"\?", "–", regex=True).str.strip()
    df["hour"] = pd.to_datetime(df["Time"], errors="coerce").dt.hour

    def time_bucket(h):
        if pd.isna(h):  return "Unknown"
        if h < 6:       return "Night (0–6)"
        if h < 12:      return "Morning (6–12)"
        if h < 17:      return "Afternoon (12–17)"
        if h < 21:      return "Evening (17–21)"
        return "Late Night (21–24)"

    df["time_period"] = df["hour"].apply(time_bucket)

    sev_map = {
        "fatal injury":   "Fatal Injury",
        "serious injury": "Serious Injury",
        "slight injury":  "Slight Injury",
    }
    df["severity_label"] = df["Accident_severity"].str.lower().map(sev_map).fillna(df["Accident_severity"].str.title())
    df["age_band_clean"] = df["Age_band_of_driver"].str.lower()
    return df

df = load_data()

# ────────────────────────────────────────────────────────────────────────────
# CONSTANTS & HELPERS
# ────────────────────────────────────────────────────────────────────────────
severity_order    = ["Slight Injury", "Serious Injury", "Fatal Injury"]
age_order         = ["under 18", "18-30", "31-50", "over 51", "unknown"]
exp_order         = ["below 1yr", "1-2yr", "2-5yr", "5-10yr", "above 10yr", "no licence"]
dow_order         = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
time_period_order = ["Night (0–6)", "Morning (6–12)", "Afternoon (12–17)", "Evening (17–21)", "Late Night (21–24)"]
edu_order         = ["illiterate", "writing & reading", "elementary school", "junior high school",
                     "high school", "above high school", "unknown"]

TOP_CAUSES = df["Cause_of_accident"].value_counts().head(6).index.tolist()
CAUSE_COLOR_MAP = {c.title(): CAUSE_PALETTE[i % len(CAUSE_PALETTE)] for i, c in enumerate(TOP_CAUSES)}


def get_options(col, drop_unknown=False):
    if col not in df.columns: return ["All"]
    vals = df[col].dropna().astype(str).str.strip()
    vals = vals[vals.str.lower() != "nan"]
    if drop_unknown:
        vals = vals[~vals.str.lower().isin(["unknown", "na"])]
    return ["All"] + sorted(vals.unique().tolist())


def severity_options():
    return ["All"] + sorted(df["severity_label"].dropna().unique().tolist())


def safe_mode(data, col):
    if col in data.columns and not data.empty:
        s = data[col].dropna().astype(str)
        s = s[~s.str.lower().isin(["nan", "na"])]
        if not s.empty:
            return s.mode().iloc[0]
    return "N/A"


def filter_df(data, gender="All", severity="All", year="All"):
    d = data
    if gender != "All":   d = d[d["Sex_of_driver"].astype(str) == gender]
    if severity != "All": d = d[d["severity_label"].astype(str) == severity]
    if year != "All":     d = d[d["Year"].astype(str) == str(year)]
    return d


def shorten(text, n=22):
    text = str(text)
    return text if len(text) <= n else text[:n - 1] + "…"


def fatal_rate_series(data, col):
    return (
        data.groupby(col)["severity_label"]
        .apply(lambda x: (x == "Fatal Injury").mean() * 100)
        .round(2).reset_index(name="Fatal Rate (%)")
    )


def editorial_layout(fig, height=420, title=None, subtitle=None):
    """Apply the newsroom chart style."""
    annotations = []
    if title:
        annotations.append(dict(
            x=0, y=1.14, xref="paper", yref="paper",
            text=f"<b>{title}</b>", showarrow=False, xanchor="left",
            font=dict(family="Fraunces, serif", size=17, color=CREAM),
        ))
    if subtitle:
        annotations.append(dict(
            x=0, y=1.06, xref="paper", yref="paper",
            text=subtitle, showarrow=False, xanchor="left",
            font=dict(family="DM Mono, monospace", size=10.5, color=MUTED),
        ))

    existing = list(fig.layout.annotations) if fig.layout.annotations else []
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        font=dict(family="Inter, sans-serif", color=CREAM_DIM, size=12),
        title=dict(text=""),
        annotations=existing + annotations,
        legend=dict(
            bgcolor="rgba(0,0,0,0)", bordercolor=RULE, borderwidth=1,
            font=dict(size=11, color=CREAM_DIM),
        ),
        legend_title_text="",
        margin=dict(l=12, r=16, t=78 if title else 24, b=24),
        xaxis=dict(gridcolor=RULE, zerolinecolor=RULE, tickfont=dict(size=11, color=CREAM_DIM),
                   title_font=dict(size=11, color=MUTED)),
        yaxis=dict(gridcolor=RULE, zerolinecolor=RULE, tickfont=dict(size=11, color=CREAM_DIM),
                   title_font=dict(size=11, color=MUTED)),
        colorway=[RED, AMBER, TEAL, NAVY, OLIVE, "#B87A5A", "#9B6BA0"],
    )
    return fig


# ────────────────────────────────────────────────────────────────────────────
# SIDEBAR — MASTHEAD
# ────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
        <div style='font-family:Fraunces,serif;font-weight:900;font-size:22px;
                    color:{CREAM};line-height:1;letter-spacing:-0.02em;
                    border-bottom:3px double {RED};padding-bottom:10px;margin-bottom:10px'>
            THE ROAD<br/>LEDGER
        </div>
        <div style='font-family:DM Mono,monospace;font-size:9.5px;color:{MUTED};
                    letter-spacing:0.2em;text-transform:uppercase;margin-bottom:18px'>
            Ethiopia · Vol. VI · 2018—2023
        </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "",
        ["Front Page",
         "Anatomy of a Crash",
         "The Cause Race",
         "Who & When",
         "On the Road",
         "The Driver",
         "Clock & Compass",
         "Collision Ledger"],
        label_visibility="collapsed",
    )

    st.markdown(f"""
        <div style='margin-top:28px;padding-top:14px;border-top:1px solid {RULE};
                    font-family:DM Mono,monospace;font-size:10px;color:{MUTED};
                    letter-spacing:0.1em;line-height:1.8'>
            FILED &nbsp; {len(df):,} records<br/>
            COLS &nbsp;&nbsp; 33 variables<br/>
            YEARS &nbsp; 6 · 2018–2023
        </div>
        <div style='margin-top:14px;font-family:DM Mono,monospace;font-size:10px;
                    color:{CREAM_DIM};line-height:2'>
          <span style='color:{TEAL}'>●</span> Slight &nbsp;&nbsp;
          <span style='color:{AMBER}'>●</span> Serious &nbsp;&nbsp;
          <span style='color:{RED}'>●</span> Fatal
        </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 1 — FRONT PAGE
# ════════════════════════════════════════════════════════════════════════════
if page == "Front Page":
    st.markdown("<div class='kicker'>Special Report · Road Safety</div>", unsafe_allow_html=True)
    st.markdown("<h1>12,316 Crashes.<br/>Six Years on Ethiopia's Roads.</h1>", unsafe_allow_html=True)
    st.markdown(
        "<div class='deck'>A forensic look at every recorded incident — who was driving, "
        "where it happened, and which minutes of the day most often end in tragedy.</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='byline'>By the Road Ledger Desk · Addis Ababa · Data from Ethiopian Police · "
        f"Analysis period {int(df['Year'].min())}—{int(df['Year'].max())}</div>",
        unsafe_allow_html=True,
    )

    year_vals = sorted(df["Year"].dropna().unique().tolist())
    sel_years = st.multiselect("Filter by year", year_vals, default=year_vals, key="home_years")
    home_df = df[df["Year"].isin(sel_years)] if sel_years else df

    total    = len(home_df)
    injuries = len(home_df[home_df["severity_label"].isin(["Slight Injury", "Serious Injury"])])
    serious  = len(home_df[home_df["severity_label"] == "Serious Injury"])
    fatals   = len(home_df[home_df["severity_label"] == "Fatal Injury"])
    fatal_pct = round((fatals / total) * 100, 2) if total else 0
    casualties_total = int(home_df["Number_of_casualties"].sum())
    top_cause = safe_mode(home_df, "Cause_of_accident").title()

    # Editorial ticker strip
    st.markdown(f"""
        <div class='ticker'>
          <div class='tk'><span class='dot' style='background:{CREAM}'></span><b>{total:,}</b> incidents</div>
          <div class='tk'><span class='dot' style='background:{TEAL}'></span><b>{injuries:,}</b> injuries</div>
          <div class='tk'><span class='dot' style='background:{AMBER}'></span><b>{serious:,}</b> serious</div>
          <div class='tk'><span class='dot' style='background:{RED}'></span><b>{fatals:,}</b> fatal ({fatal_pct}%)</div>
          <div class='tk'><span class='dot' style='background:{NAVY}'></span><b>{casualties_total:,}</b> casualties</div>
          <div class='tk'>Leading cause: <b>{top_cause}</b></div>
        </div>
    """, unsafe_allow_html=True)

    # ── Lead story chart: annotated area + severity split ────────────────────
    left, right = st.columns([1.35, 1])

    with left:
        by_year = home_df.groupby("Year").size().reset_index(name="count")
        by_year_sev = home_df.groupby(["Year", "severity_label"]).size().reset_index(name="count")

        if len(by_year) > 0:
            # Editorial stacked-area chart
            fig = go.Figure()
            for sev in severity_order:
                sub = by_year_sev[by_year_sev["severity_label"] == sev]
                sub = sub.set_index("Year").reindex(by_year["Year"], fill_value=0).reset_index()
                fig.add_trace(go.Scatter(
                    x=sub["Year"], y=sub["count"],
                    mode="lines",
                    name=sev,
                    stackgroup="one",
                    line=dict(width=0.5, color=SEV_COLORS[sev]),
                    fillcolor=SEV_COLORS[sev],
                    hovertemplate=f"<b>{sev}</b><br>%{{x}}: %{{y:,}}<extra></extra>",
                ))
            peak = by_year.loc[by_year["count"].idxmax()]
            fig.update_layout(
                xaxis=dict(tickmode="array", tickvals=by_year["Year"].tolist(),
                           tickfont=dict(size=12)),
                yaxis=dict(rangemode="tozero", title=""),
                legend=dict(orientation="h", y=-0.18, x=0),
                annotations=[dict(
                    x=peak["Year"], y=peak["count"],
                    text=f"<b>{int(peak['count']):,}</b><br><span style='font-size:9px'>PEAK</span>",
                    showarrow=True, arrowhead=0, ax=0, ay=-40, arrowcolor=RED,
                    font=dict(family="DM Mono, monospace", size=11, color=RED),
                    bgcolor=INK, bordercolor=RED, borderwidth=1, borderpad=4,
                )],
            )
            st.plotly_chart(
                editorial_layout(fig, 440,
                                 "Six years of crashes, stacked by severity",
                                 "THE CURVE · AREA CHART · DATA: ETHIOPIAN POLICE"),
                use_container_width=True,
                config={"displayModeBar": False},
            )

    with right:
        # Editorial proportion bar — severity share
        sev_counts = home_df["severity_label"].value_counts().reindex(severity_order).fillna(0)
        total_sev = sev_counts.sum()

        prop = go.Figure()
        cumul = 0
        for sev in severity_order:
            pct = (sev_counts[sev] / total_sev * 100) if total_sev else 0
            prop.add_trace(go.Bar(
                y=["Distribution"], x=[sev_counts[sev]],
                orientation="h",
                marker=dict(color=SEV_COLORS[sev], line=dict(color=INK, width=2)),
                name=f"{sev} · {pct:.1f}%",
                text=f"<b>{pct:.1f}%</b><br>{int(sev_counts[sev]):,}",
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(family="Fraunces, serif", size=15, color=INK),
                hovertemplate=f"<b>{sev}</b><br>{int(sev_counts[sev]):,} ({pct:.2f}%)<extra></extra>",
            ))
            cumul += sev_counts[sev]

        prop.update_layout(
            barmode="stack",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            showlegend=True,
            legend=dict(orientation="h", y=-0.4, x=0, font=dict(size=10)),
            margin=dict(l=0, r=0, t=80, b=50),
        )
        prop = editorial_layout(prop, 230, "The split", "PROPORTION · ALL INCIDENTS")
        st.plotly_chart(prop, use_container_width=True, config={"displayModeBar": False})

        # Big stats stack
        st.markdown(f"""
            <div style='display:flex;flex-direction:column;gap:10px;margin-top:10px'>
              <div style='background:{PAPER};border:1px solid {RULE};padding:14px;position:relative'>
                <div style='position:absolute;top:0;left:0;width:26px;height:2px;background:{RED}'></div>
                <div style='font-family:DM Mono,monospace;font-size:10px;color:{MUTED};letter-spacing:0.15em;text-transform:uppercase'>One in every</div>
                <div style='font-family:Fraunces,serif;font-size:2.4rem;font-weight:800;color:{CREAM};line-height:1'>{int(100/fatal_pct) if fatal_pct else 0}</div>
                <div style='font-family:Inter;font-size:12px;color:{CREAM_DIM}'>accidents ends in a fatality</div>
              </div>
              <div style='background:{PAPER};border:1px solid {RULE};padding:14px;position:relative'>
                <div style='position:absolute;top:0;left:0;width:26px;height:2px;background:{AMBER}'></div>
                <div style='font-family:DM Mono,monospace;font-size:10px;color:{MUTED};letter-spacing:0.15em;text-transform:uppercase'>Average casualties</div>
                <div style='font-family:Fraunces,serif;font-size:2.4rem;font-weight:800;color:{CREAM};line-height:1'>{home_df['Number_of_casualties'].mean():.2f}</div>
                <div style='font-family:Inter;font-size:12px;color:{CREAM_DIM}'>per recorded incident</div>
              </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown(
        f"<div class='pullquote'>Most accidents leave behind minor injuries. But one out of every "
        f"{int(100/fatal_pct) if fatal_pct else 0} crashes ends a life — and the patterns behind those cases "
        f"are anything but random.</div>",
        unsafe_allow_html=True,
    )

    # Dumbbell: cause volume vs fatal rate — replaces old donut
    st.markdown("### What puts people on the road to hospital — and worse")
    cause_counts = home_df["Cause_of_accident"].value_counts().head(10).reset_index()
    cause_counts.columns = ["cause", "count"]
    fr = fatal_rate_series(home_df, "Cause_of_accident").rename(columns={"Cause_of_accident": "cause"})
    merged = cause_counts.merge(fr, on="cause")
    merged["cause_t"] = merged["cause"].str.title().apply(lambda x: shorten(x, 28))
    merged = merged.sort_values("count")

    # Normalize for dual-scale
    max_cnt = merged["count"].max()
    merged["count_scaled"] = merged["count"] / max_cnt * 100

    fig_dumb = go.Figure()
    for _, r in merged.iterrows():
        fig_dumb.add_trace(go.Scatter(
            x=[r["count_scaled"], r["Fatal Rate (%)"]],
            y=[r["cause_t"], r["cause_t"]],
            mode="lines",
            line=dict(color=RULE, width=2),
            showlegend=False, hoverinfo="skip",
        ))
    fig_dumb.add_trace(go.Scatter(
        x=merged["count_scaled"], y=merged["cause_t"],
        mode="markers+text",
        marker=dict(size=15, color=CREAM, line=dict(color=INK, width=2)),
        text=[f"{int(c):,}" for c in merged["count"]],
        textposition="middle left",
        textfont=dict(family="DM Mono, monospace", size=10, color=CREAM_DIM),
        name="Volume (scaled)",
        hovertemplate="<b>%{y}</b><br>Accidents: %{text}<extra></extra>",
    ))
    fig_dumb.add_trace(go.Scatter(
        x=merged["Fatal Rate (%)"], y=merged["cause_t"],
        mode="markers+text",
        marker=dict(size=15, color=RED, line=dict(color=INK, width=2),
                    symbol="diamond"),
        text=[f"{v:.1f}%" for v in merged["Fatal Rate (%)"]],
        textposition="middle right",
        textfont=dict(family="DM Mono, monospace", size=10, color=RED),
        name="Fatal rate (%)",
        hovertemplate="<b>%{y}</b><br>Fatal rate: %{x:.2f}%<extra></extra>",
    ))
    fig_dumb.update_layout(
        xaxis=dict(title="← volume (scaled 0–100) · fatal rate % →", range=[-5, 105]),
        yaxis=dict(title=""),
        legend=dict(orientation="h", y=1.12, x=0.6),
    )
    st.plotly_chart(
        editorial_layout(fig_dumb, 500,
                         "Volume vs. lethality, by cause",
                         "DUMBBELL · WHITE = SHARE OF VOLUME · RED = FATAL RATE"),
        use_container_width=True, config={"displayModeBar": False},
    )
    st.caption("White dots are scaled relative to the most common cause. Red diamonds are the raw fatal rate within that cause — not all frequent causes are lethal, and vice versa.")

    st.markdown("<div class='endmark'><span>●</span>  <span>●</span>  <span>●</span></div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 2 — ANATOMY OF A CRASH (Trends & Causes)
# ════════════════════════════════════════════════════════════════════════════
elif page == "Anatomy of a Crash":
    st.markdown("<div class='kicker'>Chapter II · Causal Flow</div>", unsafe_allow_html=True)
    st.markdown("<h1>The anatomy<br/>of a crash.</h1>", unsafe_allow_html=True)
    st.markdown("<div class='deck'>Where a crash begins, and where it ends. A flow map from cause to consequence, "
                "followed by the edge cases — the causes that may be rare, yet routinely turn lethal.</div>",
                unsafe_allow_html=True)
    st.markdown(f"<div class='byline'>FILING: CAUSE → SEVERITY · 12,316 RECORDS</div>", unsafe_allow_html=True)

    sel_year = st.selectbox("Filter by Year", get_options("Year"), key="ac_year")
    filt = filter_df(df, year=sel_year)

    m1, m2, m3 = st.columns(3)
    m1.metric("Accidents in selection", f"{len(filt):,}")
    m2.metric("Leading cause", safe_mode(filt, "Cause_of_accident").title())
    m3.metric("Share of dataset", f"{round((len(filt)/len(df))*100,1)}%")

    # ── SANKEY: Cause (top 8) → Severity ─────────────────────────────────────
    top8 = filt["Cause_of_accident"].value_counts().head(8).index.tolist()
    snk = filt[filt["Cause_of_accident"].isin(top8)].copy()
    sankey_df = (
        snk.groupby(["Cause_of_accident", "severity_label"]).size().reset_index(name="count")
    )
    causes_list = list(dict.fromkeys(sankey_df["Cause_of_accident"].tolist()))
    sev_list = severity_order
    labels = [c.title() for c in causes_list] + sev_list
    label_colors = [CAUSE_PALETTE[i % len(CAUSE_PALETTE)] for i in range(len(causes_list))] + \
                   [SEV_COLORS[s] for s in sev_list]

    cause_idx = {c: i for i, c in enumerate(causes_list)}
    sev_idx = {s: len(causes_list) + i for i, s in enumerate(sev_list)}

    def hex_to_rgba(h, a=0.35):
        h = h.lstrip("#")
        return f"rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{a})"

    sources, targets, values, link_colors = [], [], [], []
    for _, r in sankey_df.iterrows():
        sources.append(cause_idx[r["Cause_of_accident"]])
        targets.append(sev_idx[r["severity_label"]])
        values.append(int(r["count"]))
        link_colors.append(hex_to_rgba(SEV_COLORS[r["severity_label"]], 0.35))

    fig_sankey = go.Figure(data=[go.Sankey(
        arrangement="snap",
        node=dict(
            pad=18, thickness=16,
            line=dict(color=INK, width=0.5),
            label=labels, color=label_colors,
        ),
        link=dict(source=sources, target=targets, value=values, color=link_colors,
                  hovertemplate="<b>%{source.label}</b> → <b>%{target.label}</b><br>%{value:,} cases<extra></extra>"),
    )])
    fig_sankey.update_layout(font=dict(family="Inter, sans-serif", size=11, color=CREAM_DIM))
    st.plotly_chart(
        editorial_layout(fig_sankey, 520,
                         "From cause to consequence — the crash flow",
                         "SANKEY · TOP 8 CAUSES → SEVERITY"),
        use_container_width=True, config={"displayModeBar": False},
    )

    st.markdown("<br/>", unsafe_allow_html=True)
    left, right = st.columns([1.05, 1])

    # ── LOLLIPOP: fatal rate by cause (>= 30 records) ────────────────────────
    with left:
        counts_all = filt["Cause_of_accident"].value_counts()
        fr_all = fatal_rate_series(filt, "Cause_of_accident")
        fr_all = fr_all[fr_all["Cause_of_accident"].isin(counts_all[counts_all >= 30].index)]
        fr_all = fr_all.sort_values("Fatal Rate (%)", ascending=False).head(10)
        fr_all["label"] = fr_all["Cause_of_accident"].str.title().apply(lambda x: shorten(x, 26))
        fr_all = fr_all.sort_values("Fatal Rate (%)")

        fig_lol = go.Figure()
        avg_rate = (filt["severity_label"] == "Fatal Injury").mean() * 100
        fig_lol.add_vline(x=avg_rate, line=dict(color=CREAM_DIM, width=1, dash="dot"),
                          annotation_text=f"avg {avg_rate:.2f}%",
                          annotation_position="top",
                          annotation_font=dict(family="DM Mono, monospace", size=9, color=CREAM_DIM))
        for _, r in fr_all.iterrows():
            fig_lol.add_trace(go.Scatter(
                x=[0, r["Fatal Rate (%)"]], y=[r["label"], r["label"]],
                mode="lines",
                line=dict(color=RULE, width=2),
                showlegend=False, hoverinfo="skip",
            ))
        fig_lol.add_trace(go.Scatter(
            x=fr_all["Fatal Rate (%)"], y=fr_all["label"],
            mode="markers+text",
            marker=dict(size=16, color=RED, line=dict(color=INK, width=2)),
            text=[f"{v:.1f}%" for v in fr_all["Fatal Rate (%)"]],
            textposition="middle right",
            textfont=dict(family="DM Mono, monospace", size=10.5, color=CREAM),
            showlegend=False,
            hovertemplate="<b>%{y}</b><br>Fatal rate: %{x:.2f}%<extra></extra>",
        ))
        fig_lol.update_layout(
            xaxis=dict(title="Fatal rate (%)", ticksuffix="%",
                       range=[0, fr_all["Fatal Rate (%)"].max() * 1.25]),
            yaxis=dict(title=""),
            margin=dict(r=60),
        )
        st.plotly_chart(
            editorial_layout(fig_lol, 500,
                             "The edge cases that kill",
                             "LOLLIPOP · CAUSES WITH ≥ 30 RECORDS · SORTED BY FATAL RATE"),
            use_container_width=True, config={"displayModeBar": False},
        )
        st.caption("Excludes rare causes with fewer than 30 records. Dotted line = dataset average fatal rate.")

    # ── Severity by road surface — diverging 100% stack ──────────────────────
    with right:
        road_col = "Road_surface_conditions"
        rd = filt.groupby([road_col, "severity_label"]).size().reset_index(name="count")
        totals = rd.groupby(road_col)["count"].transform("sum")
        rd["pct"] = rd["count"] / totals * 100
        rd_order = rd.groupby(road_col)["count"].sum().sort_values().index.tolist()
        rd[road_col] = rd[road_col].str.title()

        fig_rd = go.Figure()
        ordered_rows = [r.title() for r in rd_order]
        for sev in severity_order:
            sub = rd[rd["severity_label"] == sev][[road_col, "pct"]]
            sub = (
                sub.set_index(road_col)["pct"]
                .reindex(ordered_rows, fill_value=0)
                .reset_index()
            )
            fig_rd.add_trace(go.Bar(
                x=sub["pct"], y=sub[road_col],
                orientation="h",
                marker=dict(color=SEV_COLORS[sev], line=dict(color=INK, width=1)),
                name=sev,
                text=[f"{v:.0f}%" if v > 4 else "" for v in sub["pct"]],
                textposition="inside", insidetextanchor="middle",
                textfont=dict(family="DM Mono, monospace", size=10, color=INK),
                hovertemplate=f"<b>{sev}</b><br>%{{y}}<br>%{{x:.1f}}%<extra></extra>",
            ))
        fig_rd.update_layout(
            barmode="stack",
            xaxis=dict(title="Share of accidents (%)", ticksuffix="%", range=[0, 100]),
            yaxis=dict(title=""),
            legend=dict(orientation="h", y=1.08, x=0),
        )
        st.plotly_chart(
            editorial_layout(fig_rd, 500,
                             "Road surface × severity, normalised",
                             "100% STACKED · EACH ROW SUMS TO 100"),
            use_container_width=True, config={"displayModeBar": False},
        )

    st.info("The Sankey shows the flow of *volume*: which causes produce which outcomes. The lollipop shows *rate*: which causes, per incident, are most lethal. Together they reveal both the common and the catastrophic.")
    st.markdown("<div class='endmark'><span>●</span>  <span>●</span>  <span>●</span></div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 3 — THE CAUSE RACE (the one kept animation)
# ════════════════════════════════════════════════════════════════════════════
elif page == "The Cause Race":
    st.markdown("<div class='kicker'>Feature · Signature Animation</div>", unsafe_allow_html=True)
    st.markdown("<h1>The cause race —<br/>what drives the crashes.</h1>", unsafe_allow_html=True)
    st.markdown("<div class='deck'>Six years. Six leading causes. A single horizontal race that shows "
                "which hazards rose, which fell, and which quietly overtook the others.</div>",
                unsafe_allow_html=True)
    st.markdown("<div class='byline'>BAR-CHART RACE · PRESS ▶ TO PLAY · ONE SIGNATURE ANIMATION</div>",
                unsafe_allow_html=True)

    sel_sev = st.selectbox("Filter by Severity", severity_options(), key="race_sev")
    filt = filter_df(df, severity=sel_sev)

    all_years = sorted(filt["Year"].dropna().unique().tolist())
    race = (
        filt[filt["Cause_of_accident"].isin(TOP_CAUSES)]
        .groupby(["Year", "Cause_of_accident"]).size().reset_index(name="count")
    )
    idx = pd.MultiIndex.from_product([all_years, TOP_CAUSES], names=["Year", "Cause_of_accident"])
    race = race.set_index(["Year", "Cause_of_accident"]).reindex(idx, fill_value=0).reset_index()
    race["cause_t"] = race["Cause_of_accident"].str.title().apply(lambda x: shorten(x, 30))
    race = race.sort_values(["Year", "count"])

    # Build manually so bars sort by value each frame
    frames = []
    for yr in all_years:
        fr = race[race["Year"] == yr].sort_values("count")
        frames.append(go.Frame(
            name=str(int(yr)),
            data=[go.Bar(
                x=fr["count"], y=fr["cause_t"],
                orientation="h",
                marker=dict(
                    color=[CAUSE_COLOR_MAP[c.title()] for c in fr["Cause_of_accident"]],
                    line=dict(color=INK, width=1),
                ),
                text=[f"<b>{int(v):,}</b>" for v in fr["count"]],
                textposition="outside",
                textfont=dict(family="Fraunces, serif", size=14, color=CREAM),
                hovertemplate="<b>%{y}</b><br>%{x:,} accidents<extra></extra>",
            )],
            layout=go.Layout(
                annotations=[dict(
                    x=0.98, y=0.08, xref="paper", yref="paper",
                    text=f"<b style='font-size:60px'>{int(yr)}</b>",
                    showarrow=False, xanchor="right",
                    font=dict(family="Fraunces, serif", size=60, color=RULE),
                )],
            ),
        ))

    init = race[race["Year"] == all_years[0]].sort_values("count")
    max_x = race["count"].max() * 1.18

    fig_race = go.Figure(
        data=[go.Bar(
            x=init["count"], y=init["cause_t"],
            orientation="h",
            marker=dict(
                color=[CAUSE_COLOR_MAP[c.title()] for c in init["Cause_of_accident"]],
                line=dict(color=INK, width=1),
            ),
            text=[f"<b>{int(v):,}</b>" for v in init["count"]],
            textposition="outside",
            textfont=dict(family="Fraunces, serif", size=14, color=CREAM),
            hovertemplate="<b>%{y}</b><br>%{x:,} accidents<extra></extra>",
        )],
        frames=frames,
    )
    fig_race.update_layout(
        xaxis=dict(range=[0, max_x], title="Accidents per year",
                   gridcolor=RULE, zerolinecolor=RULE),
        yaxis=dict(title="", automargin=True),
        showlegend=False,
        annotations=[dict(
            x=0.98, y=0.08, xref="paper", yref="paper",
            text=f"<b>{int(all_years[0])}</b>",
            showarrow=False, xanchor="right",
            font=dict(family="Fraunces, serif", size=60, color=RULE),
        )],
        updatemenus=[dict(
            type="buttons", showactive=False,
            x=0.01, y=-0.18, xanchor="left", yanchor="top",
            bgcolor=PAPER, bordercolor=RULE,
            font=dict(family="DM Mono, monospace", size=11, color=CREAM),
            buttons=[
                dict(label="▶  Play", method="animate",
                     args=[None, dict(frame=dict(duration=1100, redraw=True),
                                      transition=dict(duration=500, easing="cubic-in-out"),
                                      fromcurrent=True, mode="immediate")]),
                dict(label="❚❚  Pause", method="animate",
                     args=[[None], dict(frame=dict(duration=0, redraw=False),
                                        mode="immediate", transition=dict(duration=0))]),
            ],
        )],
        sliders=[dict(
            active=0, x=0.15, y=-0.17, len=0.82,
            currentvalue=dict(prefix="Year · ", font=dict(
                family="DM Mono, monospace", size=12, color=CREAM)),
            bgcolor=PAPER2, bordercolor=RULE,
            font=dict(family="DM Mono, monospace", size=10, color=CREAM_DIM),
            steps=[dict(method="animate", label=str(int(y)),
                        args=[[str(int(y))], dict(mode="immediate",
                                                   frame=dict(duration=500, redraw=True),
                                                   transition=dict(duration=300))])
                   for y in all_years],
        )],
    )
    st.plotly_chart(
        editorial_layout(fig_race, 560,
                         "The top six causes, year by year",
                         "BAR-CHART RACE · SORTED ASCENDING EACH FRAME"),
        use_container_width=True, config={"displayModeBar": False},
    )

    # ── SLOPEGRAPH: rank change first year vs last year ──────────────────────
    st.markdown("### The rankings, then and now")
    st.caption(f"Each line traces how a cause moved in the rankings between "
               f"{int(all_years[0])} and {int(all_years[-1])}.")

    first_yr, last_yr = all_years[0], all_years[-1]
    left_counts = race[race["Year"] == first_yr].sort_values("count", ascending=False).reset_index(drop=True)
    right_counts = race[race["Year"] == last_yr].sort_values("count", ascending=False).reset_index(drop=True)
    left_counts["rank"] = left_counts.index + 1
    right_counts["rank"] = right_counts.index + 1

    fig_slope = go.Figure()
    for _, r in left_counts.iterrows():
        cause = r["Cause_of_accident"]
        r1 = r["rank"]
        r2 = right_counts.loc[right_counts["Cause_of_accident"] == cause, "rank"].iloc[0]
        v1 = r["count"]
        v2 = right_counts.loc[right_counts["Cause_of_accident"] == cause, "count"].iloc[0]
        color = CAUSE_COLOR_MAP[cause.title()]
        fig_slope.add_trace(go.Scatter(
            x=[first_yr, last_yr], y=[r1, r2],
            mode="lines+markers+text",
            line=dict(color=color, width=3),
            marker=dict(size=14, color=color, line=dict(color=INK, width=2)),
            text=[f"{shorten(cause.title(), 24)}  <b>{int(v1)}</b>",
                  f"<b>{int(v2)}</b>  {shorten(cause.title(), 24)}"],
            textposition=["middle left", "middle right"],
            textfont=dict(family="Inter", size=11, color=CREAM_DIM),
            showlegend=False,
            hovertemplate=f"<b>{cause.title()}</b><br>{first_yr}: #{r1} ({v1})<br>"
                          f"{last_yr}: #{r2} ({v2})<extra></extra>",
        ))
    fig_slope.update_layout(
        xaxis=dict(tickvals=[first_yr, last_yr],
                   ticktext=[f"<b>{first_yr}</b>", f"<b>{last_yr}</b>"],
                   tickfont=dict(family="Fraunces, serif", size=16, color=CREAM),
                   showgrid=False, range=[first_yr - 0.5, last_yr + 0.5]),
        yaxis=dict(autorange="reversed", showgrid=False, showticklabels=False,
                   title="rank (1 = most common)"),
        margin=dict(l=180, r=180),
    )
    st.plotly_chart(
        editorial_layout(fig_slope, 420, "Rank shift, first year vs. last year",
                         "SLOPEGRAPH · HIGHER = MORE COMMON"),
        use_container_width=True, config={"displayModeBar": False},
    )

    st.markdown("<div class='endmark'><span>●</span>  <span>●</span>  <span>●</span></div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 4 — WHO & WHEN (Severity Breakdown)
# ════════════════════════════════════════════════════════════════════════════
elif page == "Who & When":
    st.markdown("<div class='kicker'>Chapter III · Conditions</div>", unsafe_allow_html=True)
    st.markdown("<h1>Who, and when?</h1>", unsafe_allow_html=True)
    st.markdown("<div class='deck'>Severity doesn't distribute evenly. Some weekdays carry disproportionate risk, "
                "certain weather amplifies it, and particular ages recur in the fatality logs.</div>",
                unsafe_allow_html=True)
    st.markdown("<div class='byline'>WEATHER · LIGHT · DAY · AGE</div>", unsafe_allow_html=True)

    f1, f2 = st.columns(2)
    sel_gender = f1.selectbox("Driver Gender", get_options("Sex_of_driver"), key="ww_g")
    sel_sev    = f2.selectbox("Severity", severity_options(), key="ww_s")
    filt = filter_df(df, gender=sel_gender, severity=sel_sev)

    # ── SUNBURST: Weather → Light → Severity ─────────────────────────────────
    sb = (
        filt.groupby(["Weather_conditions", "Light_conditions", "severity_label"])
        .size().reset_index(name="count")
    )
    # Keep top weather categories only
    keep_w = filt["Weather_conditions"].value_counts().head(6).index.tolist()
    sb = sb[sb["Weather_conditions"].isin(keep_w)].copy()
    sb["Weather_conditions"] = sb["Weather_conditions"].str.title()
    sb["Light_conditions"]   = sb["Light_conditions"].str.title()

    left, right = st.columns([1.1, 1])

    with left:
        fig_sb = px.sunburst(
            sb, path=["Weather_conditions", "Light_conditions", "severity_label"],
            values="count", color="severity_label",
            color_discrete_map=SEV_COLORS,
        )
        fig_sb.update_traces(
            textinfo="label+percent parent",
            insidetextfont=dict(family="Inter", size=11, color=INK),
            marker=dict(line=dict(color=INK, width=2)),
            hovertemplate="<b>%{label}</b><br>%{value:,} cases<extra></extra>",
        )
        st.plotly_chart(
            editorial_layout(fig_sb, 500,
                             "Weather → light → severity",
                             "SUNBURST · HIERARCHY OF CONDITIONS"),
            use_container_width=True, config={"displayModeBar": False},
        )

    # ── HORIZON-style day-of-week × severity (100% normalised) ──────────────
    with right:
        dow_sev = filt.groupby(["Day_of_week", "severity_label"]).size().reset_index(name="count")
        dow_sev["Day_of_week"] = pd.Categorical(
            dow_sev["Day_of_week"].str.lower(), categories=dow_order, ordered=True
        )
        dow_sev = dow_sev.sort_values("Day_of_week").dropna(subset=["Day_of_week"])
        totals = dow_sev.groupby("Day_of_week", observed=True)["count"].transform("sum")
        dow_sev["pct"] = dow_sev["count"] / totals * 100
        dow_sev["day_t"] = dow_sev["Day_of_week"].astype(str).str.title()

        fig_dow = go.Figure()
        for sev in severity_order:
            sub = dow_sev[dow_sev["severity_label"] == sev]
            fig_dow.add_trace(go.Bar(
                x=sub["day_t"], y=sub["pct"],
                name=sev,
                marker=dict(color=SEV_COLORS[sev], line=dict(color=INK, width=1)),
                hovertemplate=f"<b>{sev}</b><br>%{{x}}<br>%{{y:.1f}}% of day's accidents<extra></extra>",
            ))
        fig_dow.update_layout(
            barmode="stack",
            xaxis=dict(title=""),
            yaxis=dict(title="Share (%)", ticksuffix="%", range=[0, 100]),
            legend=dict(orientation="h", y=1.08, x=0),
        )
        st.plotly_chart(
            editorial_layout(fig_dow, 500,
                             "Severity composition by weekday",
                             "100% STACKED · HOW DEADLY IS EACH DAY?"),
            use_container_width=True, config={"displayModeBar": False},
        )

    # ── RIDGELINE: casualties by severity (using violin traces offset) ──────
    st.markdown("### The spread of casualties per accident")
    vio_df = filt[["Number_of_casualties", "severity_label"]].dropna()
    if not vio_df.empty and vio_df["severity_label"].nunique() >= 2:
        fig_ridge = go.Figure()
        for i, sev in enumerate(severity_order):
            sub = vio_df[vio_df["severity_label"] == sev]
            if sub.empty: continue
            fig_ridge.add_trace(go.Violin(
                x=sub["Number_of_casualties"], y=[sev] * len(sub),
                name=sev, orientation="h",
                side="positive", width=1.8,
                line=dict(color=SEV_COLORS[sev], width=1.5),
                fillcolor=SEV_COLORS[sev], opacity=0.55,
                box=dict(visible=True, width=0.08, line=dict(color=CREAM, width=1.2)),
                meanline=dict(visible=True, color=CREAM, width=1.5),
                points=False,
                hovertemplate=f"<b>{sev}</b><br>Casualties: %{{x}}<extra></extra>",
            ))
        fig_ridge.update_layout(
            xaxis=dict(title="Casualties per accident", dtick=1),
            yaxis=dict(title="", categoryorder="array", categoryarray=severity_order[::-1]),
            showlegend=False, violingap=0.15,
        )
        st.plotly_chart(
            editorial_layout(fig_ridge, 380,
                             "Casualty distribution, per severity band",
                             "RIDGELINE · WIDTH = DENSITY · BOX = IQR"),
            use_container_width=True, config={"displayModeBar": False},
        )

    # ── ANNOTATED HEATMAP: weather × severity ───────────────────────────────
    weather_order_list = ["normal", "cloudy", "windy", "raining", "raining and windy",
                          "fog or mist", "snow", "other", "unknown"]
    h = filt.groupby(["Weather_conditions", "severity_label"]).size().reset_index(name="count")
    hp = h.pivot(index="Weather_conditions", columns="severity_label", values="count").fillna(0)
    rows = [w for w in weather_order_list if w in hp.index] + [r for r in hp.index if r not in weather_order_list]
    hp = hp.loc[rows]
    hp = hp[[c for c in severity_order if c in hp.columns]]

    left2, right2 = st.columns([1.3, 1])
    with left2:
        # Row-normalised heat
        hp_norm = hp.div(hp.sum(axis=1), axis=0) * 100
        z = hp_norm.values
        text = np.array([[f"<b>{int(hp.iat[i,j])}</b><br>{hp_norm.iat[i,j]:.0f}%" for j in range(hp.shape[1])] for i in range(hp.shape[0])])
        fig_h = go.Figure(go.Heatmap(
            z=z,
            x=[c.replace(" Injury", "") for c in hp.columns],
            y=[r.title() for r in hp.index],
            colorscale=[[0, PAPER2], [0.5, AMBER], [1, RED]],
            text=text, texttemplate="%{text}",
            textfont=dict(family="Inter", size=10.5, color=CREAM),
            hovertemplate="Weather: %{y}<br>Severity: %{x}<br>Share: %{z:.1f}%<extra></extra>",
            colorbar=dict(title=dict(text="Row %", font=dict(size=10, color=MUTED)),
                          tickfont=dict(size=9, color=MUTED), thickness=10, len=0.7),
        ))
        st.plotly_chart(
            editorial_layout(fig_h, 440,
                             "Weather × severity, row-normalised",
                             "HEATMAP · EACH ROW = 100% · SHADE = SEVERITY SHARE"),
            use_container_width=True, config={"displayModeBar": False},
        )

    # ── TREEMAP: age × severity ──────────────────────────────────────────────
    with right2:
        tm = filt.groupby(["severity_label", "age_band_clean"]).size().reset_index(name="count")
        tm = tm[tm["count"] > 0]
        fig_tm = px.treemap(
            tm, path=["severity_label", "age_band_clean"], values="count",
            color="severity_label", color_discrete_map=SEV_COLORS,
        )
        fig_tm.update_traces(
            textinfo="label+value+percent parent",
            textfont=dict(family="Inter", size=11, color=INK),
            marker=dict(line=dict(color=INK, width=2)),
        )
        st.plotly_chart(
            editorial_layout(fig_tm, 440,
                             "Age groups within each severity",
                             "TREEMAP · PROPORTIONAL BLOCKS"),
            use_container_width=True, config={"displayModeBar": False},
        )

    st.info("Normal weather dominates the accident count simply because most driving happens in it. The sunburst and 100%-stacked views correct for this by showing *shares*, not raw counts.")
    st.markdown("<div class='endmark'><span>●</span>  <span>●</span>  <span>●</span></div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 5 — ON THE ROAD (Vehicle & Driver)
# ════════════════════════════════════════════════════════════════════════════
elif page == "On the Road":
    st.markdown("<div class='kicker'>Chapter IV · The Vehicle</div>", unsafe_allow_html=True)
    st.markdown("<h1>On the road.</h1>", unsafe_allow_html=True)
    st.markdown("<div class='deck'>Not every vehicle is equally dangerous; not every pile-up kills. "
                "A profile of the metal and machinery behind the numbers.</div>",
                unsafe_allow_html=True)
    st.markdown("<div class='byline'>VEHICLE TYPE · PILE-UPS · SERVICE AGE</div>", unsafe_allow_html=True)

    sel_sev = st.selectbox("Filter by Severity", severity_options(), key="otr_sev")
    filt = filter_df(df, severity=sel_sev)

    m1, m2, m3 = st.columns(3)
    m1.metric("Accidents in selection", f"{len(filt):,}")
    m2.metric("Most common vehicle", safe_mode(filt, "Type_of_vehicle").title())
    m3.metric("Most common outcome", safe_mode(filt, "severity_label"))

    # ── DUMBBELL: vehicle count vs fatal rate ────────────────────────────────
    vc = filt["Type_of_vehicle"].value_counts().head(10).reset_index()
    vc.columns = ["veh", "count"]
    vf = fatal_rate_series(filt, "Type_of_vehicle").rename(columns={"Type_of_vehicle": "veh"})
    vc = vc.merge(vf, on="veh", how="left").fillna(0)
    vc["label"] = vc["veh"].str.title().apply(lambda x: shorten(x, 24))
    # Sort by count for display
    vc = vc.sort_values("count")
    max_c = vc["count"].max()
    vc["count_pct"] = vc["count"] / max_c * 100

    fig_db = go.Figure()
    for _, r in vc.iterrows():
        fig_db.add_trace(go.Scatter(
            x=[r["count_pct"], r["Fatal Rate (%)"]], y=[r["label"], r["label"]],
            mode="lines", line=dict(color=RULE, width=2),
            showlegend=False, hoverinfo="skip",
        ))
    fig_db.add_trace(go.Scatter(
        x=vc["count_pct"], y=vc["label"], mode="markers+text",
        marker=dict(size=15, color=CREAM, line=dict(color=INK, width=2)),
        text=[f"{int(c):,}" for c in vc["count"]],
        textposition="middle left",
        textfont=dict(family="DM Mono, monospace", size=10, color=CREAM_DIM),
        name="Accidents",
        hovertemplate="<b>%{y}</b><br>Count: %{text}<extra></extra>",
    ))
    fig_db.add_trace(go.Scatter(
        x=vc["Fatal Rate (%)"], y=vc["label"], mode="markers+text",
        marker=dict(size=15, color=RED, line=dict(color=INK, width=2), symbol="diamond"),
        text=[f"{v:.1f}%" for v in vc["Fatal Rate (%)"]],
        textposition="middle right",
        textfont=dict(family="DM Mono, monospace", size=10, color=RED),
        name="Fatal rate",
        hovertemplate="<b>%{y}</b><br>Fatal rate: %{x:.2f}%<extra></extra>",
    ))
    fig_db.update_layout(
        xaxis=dict(title="← count (scaled 0–100) · fatal rate % →", range=[-5, 105]),
        yaxis=dict(title=""),
        legend=dict(orientation="h", y=1.12, x=0.7),
    )
    st.plotly_chart(
        editorial_layout(fig_db, 520,
                         "Vehicle types — common vs. lethal",
                         "DUMBBELL · VOLUME (WHITE) vs FATAL RATE (RED)"),
        use_container_width=True, config={"displayModeBar": False},
    )

    st.markdown("<br/>", unsafe_allow_html=True)
    left, right = st.columns(2)

    # ── BUBBLE: vehicles involved × avg casualties ──────────────────────────
    with left:
        sc = (
            filt.groupby(["Number_of_vehicles_involved", "severity_label"])
            .agg(avg_cas=("Number_of_casualties", "mean"),
                 n=("Number_of_casualties", "count")).reset_index()
        )
        fig_bub = px.scatter(
            sc, x="Number_of_vehicles_involved", y="avg_cas",
            size="n", color="severity_label",
            color_discrete_map=SEV_COLORS,
            category_orders={"severity_label": severity_order},
            size_max=48, opacity=0.85,
            hover_data={"n": True, "avg_cas": ":.2f"},
            labels={"Number_of_vehicles_involved": "Vehicles involved",
                    "avg_cas": "Avg. casualties",
                    "severity_label": "Severity", "n": "Incidents"},
        )
        fig_bub.update_traces(marker=dict(line=dict(color=INK, width=1)))
        fig_bub.update_layout(
            xaxis=dict(range=[0.5, sc["Number_of_vehicles_involved"].max() + 0.5],
                       dtick=1),
            legend=dict(orientation="h", y=1.08, x=0),
        )
        st.plotly_chart(
            editorial_layout(fig_bub, 420,
                             "Pile-up size × human cost",
                             "BUBBLE · SIZE = INCIDENTS · MORE VEHICLES, MORE LIVES"),
            use_container_width=True, config={"displayModeBar": False},
        )

    # ── DUAL-AXIS: service age ──────────────────────────────────────────────
    with right:
        svc_order = ["below 1yr", "1-2yr", "2-5yrs", "5-10yrs", "above 10yr", "unknown"]
        s = filt.copy()
        s["Service_year_of_vehicle"] = s["Service_year_of_vehicle"].str.lower()
        sc2 = s["Service_year_of_vehicle"].value_counts().reindex(svc_order).fillna(0).reset_index()
        sc2.columns = ["Svc", "count"]
        sf = fatal_rate_series(s, "Service_year_of_vehicle").rename(columns={"Service_year_of_vehicle": "Svc"})
        sc2 = sc2.merge(sf, on="Svc", how="left").fillna(0)

        fig_sv = make_subplots(specs=[[{"secondary_y": True}]])
        fig_sv.add_trace(go.Bar(
            x=sc2["Svc"], y=sc2["count"],
            marker=dict(color=NAVY, line=dict(color=INK, width=1)),
            name="Accidents", opacity=0.85,
            hovertemplate="<b>%{x}</b><br>%{y:,} accidents<extra></extra>",
        ), secondary_y=False)
        fig_sv.add_trace(go.Scatter(
            x=sc2["Svc"], y=sc2["Fatal Rate (%)"],
            mode="lines+markers",
            line=dict(color=RED, width=2.5),
            marker=dict(size=10, color=RED, line=dict(color=INK, width=2)),
            name="Fatal rate (%)",
            hovertemplate="Fatal rate: %{y:.2f}%<extra></extra>",
        ), secondary_y=True)
        fig_sv.update_yaxes(title_text="Accidents", secondary_y=False,
                            gridcolor=RULE, zerolinecolor=RULE)
        fig_sv.update_yaxes(title_text="Fatal rate (%)", secondary_y=True,
                            ticksuffix="%", showgrid=False)
        fig_sv.update_layout(legend=dict(orientation="h", y=1.08, x=0))
        st.plotly_chart(
            editorial_layout(fig_sv, 420,
                             "Vehicle service age — volume & lethality",
                             "DUAL AXIS · BARS = COUNT · RED LINE = FATAL RATE"),
            use_container_width=True, config={"displayModeBar": False},
        )

    st.markdown(
        f"<div class='pullquote'>More vehicles in a crash means more casualties — almost linearly. "
        f"Older vehicles carry a notably higher fatal rate, even with fewer incidents logged.</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div class='endmark'><span>●</span>  <span>●</span>  <span>●</span></div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 6 — THE DRIVER
# ════════════════════════════════════════════════════════════════════════════
elif page == "The Driver":
    st.markdown("<div class='kicker'>Chapter V · Behind the Wheel</div>", unsafe_allow_html=True)
    st.markdown("<h1>The driver.</h1>", unsafe_allow_html=True)
    st.markdown("<div class='deck'>Age, experience and schooling trace an outline of the person at the wheel — "
                "and of the person most often mourned.</div>",
                unsafe_allow_html=True)
    st.markdown("<div class='byline'>DEMOGRAPHICS · EXPERIENCE · EDUCATION</div>", unsafe_allow_html=True)

    f1, f2 = st.columns(2)
    sel_sev    = f1.selectbox("Severity", severity_options(), key="dr_s")
    sel_gender = f2.selectbox("Gender", get_options("Sex_of_driver"), key="dr_g")
    filt = filter_df(df, severity=sel_sev, gender=sel_gender)

    # ── PARALLEL CATEGORIES: Age → Experience → Education → Severity ────────
    pc = filt[["age_band_clean", "Driving_experience", "Educational_level", "severity_label"]].copy()
    pc.columns = ["Age", "Experience", "Education", "Severity"]
    pc = pc.replace({"unknown": "Unknown", "nan": "Unknown", "": "Unknown"})
    pc["Age"] = pc["Age"].str.title()
    pc["Experience"] = pc["Experience"].str.title()
    pc["Education"] = pc["Education"].str.title()

    sev_color_idx = pc["Severity"].map({s: i for i, s in enumerate(severity_order)}).fillna(0)
    fig_pc = go.Figure(go.Parcats(
        dimensions=[
            dict(label="Age", values=pc["Age"]),
            dict(label="Experience", values=pc["Experience"]),
            dict(label="Education", values=pc["Education"]),
            dict(label="Severity", values=pc["Severity"],
                 categoryorder="array", categoryarray=severity_order),
        ],
        line=dict(
            color=sev_color_idx,
            colorscale=[[0, TEAL], [0.5, AMBER], [1, RED]],
            shape="hspline",
        ),
        counts=1,
        hoveron="color", hoverinfo="count+probability",
        labelfont=dict(family="DM Mono, monospace", size=11, color=CREAM),
        tickfont=dict(family="Inter", size=10, color=CREAM_DIM),
        arrangement="freeform",
    ))
    fig_pc.update_layout(margin=dict(l=60, r=40, t=78, b=20))
    st.plotly_chart(
        editorial_layout(fig_pc, 520,
                         "Age → Experience → Education → Severity",
                         "PARALLEL CATEGORIES · COLOUR = SEVERITY"),
        use_container_width=True, config={"displayModeBar": False},
    )

    st.markdown("<br/>", unsafe_allow_html=True)
    left, right = st.columns(2)

    # ── RADAR: severity profile by age band ─────────────────────────────────
    with left:
        ages = [a for a in age_order if a != "unknown"]
        radar_df = (
            filt[filt["age_band_clean"].isin(ages)]
            .groupby(["age_band_clean", "severity_label"]).size().reset_index(name="count")
        )
        piv = radar_df.pivot(index="age_band_clean", columns="severity_label", values="count").fillna(0)
        piv = piv.reindex(ages).fillna(0)
        # Row-normalise to % to compare shapes
        piv_pct = piv.div(piv.sum(axis=1).replace(0, 1), axis=0) * 100
        cats = [a.title() for a in piv_pct.index] + [piv_pct.index[0].title()]

        fig_rd = go.Figure()
        for sev in severity_order:
            if sev not in piv_pct.columns: continue
            vals = piv_pct[sev].tolist() + [piv_pct[sev].iloc[0]]
            fig_rd.add_trace(go.Scatterpolar(
                r=vals, theta=cats,
                fill="toself", name=sev,
                line=dict(color=SEV_COLORS[sev], width=2),
                fillcolor=f"rgba({int(SEV_COLORS[sev][1:3],16)},{int(SEV_COLORS[sev][3:5],16)},{int(SEV_COLORS[sev][5:7],16)},0.18)",
                hovertemplate=f"<b>{sev}</b><br>%{{theta}}: %{{r:.1f}}%<extra></extra>",
            ))
        fig_rd.update_layout(
            polar=dict(
                bgcolor=PAPER2,
                radialaxis=dict(visible=True, showticklabels=True,
                                gridcolor=RULE, tickfont=dict(size=9, color=MUTED),
                                ticksuffix="%"),
                angularaxis=dict(gridcolor=RULE, tickfont=dict(family="Inter", size=11, color=CREAM)),
            ),
            showlegend=True,
            legend=dict(orientation="h", y=-0.12, x=0.5, xanchor="center"),
        )
        st.plotly_chart(
            editorial_layout(fig_rd, 460,
                             "Severity shape, by age band",
                             "RADAR · EACH AGE NORMALISED TO 100%"),
            use_container_width=True, config={"displayModeBar": False},
        )

    # ── DUAL-AXIS: experience vs fatal rate ─────────────────────────────────
    with right:
        e = filt.copy()
        e["Driving_experience"] = e["Driving_experience"].str.lower()
        e = e[e["Driving_experience"] != "unknown"]
        ec = e["Driving_experience"].value_counts().reindex(exp_order).fillna(0).reset_index()
        ec.columns = ["exp", "count"]
        ef = fatal_rate_series(e, "Driving_experience").rename(columns={"Driving_experience": "exp"})
        ec = ec.merge(ef, on="exp", how="left").fillna(0)
        ec["exp_t"] = ec["exp"].str.title()

        fig_e = make_subplots(specs=[[{"secondary_y": True}]])
        fig_e.add_trace(go.Bar(
            x=ec["exp_t"], y=ec["count"],
            marker=dict(color=TEAL, line=dict(color=INK, width=1)),
            name="Accidents", opacity=0.85,
            hovertemplate="<b>%{x}</b><br>%{y:,} accidents<extra></extra>",
        ), secondary_y=False)
        fig_e.add_trace(go.Scatter(
            x=ec["exp_t"], y=ec["Fatal Rate (%)"],
            mode="lines+markers",
            line=dict(color=RED, width=2.5),
            marker=dict(size=10, color=RED, line=dict(color=INK, width=2)),
            name="Fatal rate",
            hovertemplate="Fatal rate: %{y:.2f}%<extra></extra>",
        ), secondary_y=True)
        fig_e.update_yaxes(title_text="Accidents", secondary_y=False,
                           gridcolor=RULE, zerolinecolor=RULE)
        fig_e.update_yaxes(title_text="Fatal rate (%)", secondary_y=True,
                           ticksuffix="%", showgrid=False)
        fig_e.update_layout(legend=dict(orientation="h", y=1.08, x=0))
        st.plotly_chart(
            editorial_layout(fig_e, 460,
                             "Experience — volume & lethality",
                             "DUAL AXIS · NEWCOMERS DRIVE MORE CRASHES, NOT NECESSARILY DEADLIER ONES"),
            use_container_width=True, config={"displayModeBar": False},
        )

    # ── Education lollipop (colored by fatal rate) ──────────────────────────
    ed = filt.copy()
    ed["Educational_level"] = ed["Educational_level"].str.lower()
    ec2 = ed["Educational_level"].value_counts().reindex(edu_order).fillna(0).reset_index()
    ec2.columns = ["ed", "count"]
    ef2 = fatal_rate_series(ed, "Educational_level").rename(columns={"Educational_level": "ed"})
    ec2 = ec2.merge(ef2, on="ed", how="left").fillna(0)
    ec2["label"] = ec2["ed"].str.title()
    ec2 = ec2[ec2["count"] > 0]

    fig_ed = go.Figure()
    for _, r in ec2.iterrows():
        fig_ed.add_trace(go.Scatter(
            x=[r["label"], r["label"]], y=[0, r["count"]],
            mode="lines", line=dict(color=RULE, width=2),
            showlegend=False, hoverinfo="skip",
        ))
    fig_ed.add_trace(go.Scatter(
        x=ec2["label"], y=ec2["count"], mode="markers+text",
        marker=dict(
            size=22, color=ec2["Fatal Rate (%)"],
            colorscale=[[0, TEAL], [0.5, AMBER], [1, RED]],
            cmin=0, cmax=max(ec2["Fatal Rate (%)"].max(), 5),
            line=dict(color=INK, width=2),
            colorbar=dict(title=dict(text="Fatal %", font=dict(size=10, color=MUTED)),
                          thickness=10, len=0.6, tickfont=dict(size=9, color=MUTED)),
        ),
        text=[f"{int(c):,}" for c in ec2["count"]],
        textposition="top center",
        textfont=dict(family="DM Mono, monospace", size=10, color=CREAM_DIM),
        showlegend=False,
        hovertemplate="<b>%{x}</b><br>Accidents: %{y:,}<br>Fatal rate: %{marker.color:.2f}%<extra></extra>",
    ))
    fig_ed.update_layout(
        xaxis=dict(title=""),
        yaxis=dict(title="Accidents", rangemode="tozero"),
    )
    st.plotly_chart(
        editorial_layout(fig_ed, 420,
                         "Driver education — accidents, shaded by fatal rate",
                         "LOLLIPOP · HEIGHT = VOLUME · COLOUR = LETHALITY"),
        use_container_width=True, config={"displayModeBar": False},
    )
    st.caption("Junior-high drivers appear most simply because they are the most common education level on the road.")

    st.markdown("<div class='endmark'><span>●</span>  <span>●</span>  <span>●</span></div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 7 — CLOCK & COMPASS (Time & Location)
# ════════════════════════════════════════════════════════════════════════════
elif page == "Clock & Compass":
    st.markdown("<div class='kicker'>Chapter VI · The Clock</div>", unsafe_allow_html=True)
    st.markdown("<h1>Clock &amp; compass.</h1>", unsafe_allow_html=True)
    st.markdown("<div class='deck'>When the roads fill, crashes follow. But the hours in which those crashes "
                "turn fatal are narrower, and darker, than most assume.</div>",
                unsafe_allow_html=True)
    st.markdown("<div class='byline'>HOUR · DAY · LOCATION</div>", unsafe_allow_html=True)

    sel_sev = st.selectbox("Filter by Severity", severity_options(), key="cc_sev")
    filt = filter_df(df, severity=sel_sev)

    m1, m2, m3 = st.columns(3)
    m1.metric("Accidents in selection", f"{len(filt):,}")
    peak_hour = int(filt["hour"].dropna().mode().iloc[0]) if not filt["hour"].dropna().empty else 17
    m2.metric("Peak hour", f"{peak_hour:02d}:00")
    top_area = safe_mode(filt, "Area_accident_occured").title()
    m3.metric("Top area", shorten(top_area, 16))

    # ── RADIAL 24-HOUR CLOCK ────────────────────────────────────────────────
    hr_df = filt.dropna(subset=["hour"]).copy()
    hr_counts = hr_df["hour"].value_counts().reindex(range(24), fill_value=0).sort_index()
    theta = [h * 15 for h in range(24)]   # 360/24 = 15 deg per hour
    labels = [f"{h:02d}:00" for h in range(24)]

    fig_clock = go.Figure(go.Barpolar(
        r=hr_counts.values,
        theta=theta,
        width=[14] * 24,
        marker=dict(
            color=hr_counts.values,
            colorscale=[[0, PAPER2], [0.4, AMBER], [1, RED]],
            line=dict(color=INK, width=1),
        ),
        hovertemplate="<b>%{text}</b><br>%{r:,} accidents<extra></extra>",
        text=labels,
    ))
    fig_clock.update_layout(
        polar=dict(
            bgcolor=PAPER2,
            radialaxis=dict(showticklabels=False, gridcolor=RULE, ticks=""),
            angularaxis=dict(
                direction="clockwise", rotation=90,
                tickmode="array",
                tickvals=theta,
                ticktext=labels,
                gridcolor=RULE,
                tickfont=dict(family="DM Mono, monospace", size=10, color=CREAM_DIM),
            ),
        ),
        showlegend=False,
    )
    left, right = st.columns([1, 1.15])
    with left:
        st.plotly_chart(
            editorial_layout(fig_clock, 520,
                             "A 24-hour clock of crashes",
                             "POLAR · HOUR AS ANGLE · LENGTH = FREQUENCY"),
            use_container_width=True, config={"displayModeBar": False},
        )

    # ── HOUR × DAY HEATMAP ──────────────────────────────────────────────────
    with right:
        hm = hr_df[hr_df["Day_of_week"].str.lower().isin(dow_order)].copy()
        hm["Day_of_week"] = hm["Day_of_week"].str.lower()
        piv = hm.groupby(["Day_of_week", "hour"]).size().unstack(fill_value=0)
        piv = piv.reindex([d for d in dow_order if d in piv.index])

        fig_hm = go.Figure(go.Heatmap(
            z=piv.values,
            x=[f"{h:02d}" for h in piv.columns],
            y=[d.title() for d in piv.index],
            colorscale=[[0, PAPER2], [0.4, AMBER], [1, RED]],
            hovertemplate="<b>%{y}</b><br>Hour %{x}:00<br>%{z:,} accidents<extra></extra>",
            colorbar=dict(thickness=10, len=0.7, tickfont=dict(size=9, color=MUTED)),
        ))
        fig_hm.update_layout(xaxis_title="Hour of day", yaxis_title="")
        st.plotly_chart(
            editorial_layout(fig_hm, 520,
                             "Hour × day density",
                             "HEATMAP · DARKEST ZONE = 16–19H, FRIDAYS"),
            use_container_width=True, config={"displayModeBar": False},
        )

    # ── TIME-OF-DAY DUAL AXIS ───────────────────────────────────────────────
    tp = filt[filt["time_period"] != "Unknown"]
    tpc = tp.groupby("time_period").size().reset_index(name="count")
    tpf = fatal_rate_series(tp, "time_period").rename(columns={"time_period": "time_period"})
    tpm = tpc.merge(tpf, on="time_period")
    tpm["time_period"] = pd.Categorical(tpm["time_period"], categories=time_period_order, ordered=True)
    tpm = tpm.sort_values("time_period")

    fig_tp = make_subplots(specs=[[{"secondary_y": True}]])
    fig_tp.add_trace(go.Bar(
        x=tpm["time_period"], y=tpm["count"],
        marker=dict(color=NAVY, line=dict(color=INK, width=1)), opacity=0.85,
        name="Accidents",
        hovertemplate="<b>%{x}</b><br>%{y:,}<extra></extra>",
    ), secondary_y=False)
    fig_tp.add_trace(go.Scatter(
        x=tpm["time_period"], y=tpm["Fatal Rate (%)"],
        mode="lines+markers",
        line=dict(color=RED, width=2.5),
        marker=dict(size=12, color=RED, line=dict(color=INK, width=2)),
        name="Fatal rate",
        hovertemplate="Fatal rate: %{y:.2f}%<extra></extra>",
    ), secondary_y=True)
    fig_tp.update_yaxes(title_text="Accidents", secondary_y=False,
                        gridcolor=RULE, zerolinecolor=RULE)
    fig_tp.update_yaxes(title_text="Fatal rate (%)", secondary_y=True,
                        ticksuffix="%", showgrid=False)
    fig_tp.update_layout(legend=dict(orientation="h", y=1.08, x=0))
    st.plotly_chart(
        editorial_layout(fig_tp, 400,
                         "When do crashes happen — and when do they kill?",
                         "DUAL AXIS · BARS = VOLUME · RED LINE = FATAL RATE"),
        use_container_width=True, config={"displayModeBar": False},
    )
    st.caption("Night hours hold a fraction of the accidents but a disproportionate share of deaths.")

    # ── AREA FATAL-RATE LOLLIPOP ────────────────────────────────────────────
    a = filt.copy()
    a["Area_accident_occured"] = a["Area_accident_occured"].str.lower()
    counts_a = a["Area_accident_occured"].value_counts()
    af = fatal_rate_series(a, "Area_accident_occured")
    af = af[af["Area_accident_occured"].isin(counts_a[counts_a >= 20].index)]
    af["label"] = af["Area_accident_occured"].str.title().apply(lambda x: shorten(x, 28))
    af = af.sort_values("Fatal Rate (%)")

    fig_al = go.Figure()
    for _, r in af.iterrows():
        fig_al.add_trace(go.Scatter(
            x=[0, r["Fatal Rate (%)"]], y=[r["label"], r["label"]],
            mode="lines", line=dict(color=RULE, width=2),
            showlegend=False, hoverinfo="skip",
        ))
    fig_al.add_trace(go.Scatter(
        x=af["Fatal Rate (%)"], y=af["label"], mode="markers+text",
        marker=dict(
            size=17,
            color=af["Fatal Rate (%)"],
            colorscale=[[0, TEAL], [0.5, AMBER], [1, RED]],
            line=dict(color=INK, width=2),
        ),
        text=[f"{v:.1f}%" for v in af["Fatal Rate (%)"]],
        textposition="middle right",
        textfont=dict(family="DM Mono, monospace", size=10.5, color=CREAM),
        showlegend=False,
        hovertemplate="<b>%{y}</b><br>Fatal rate: %{x:.2f}%<extra></extra>",
    ))
    fig_al.update_layout(
        xaxis=dict(title="Fatal rate (%)", ticksuffix="%"),
        yaxis=dict(title=""),
        margin=dict(r=80),
    )
    st.plotly_chart(
        editorial_layout(fig_al, 420,
                         "Where fatal crashes cluster",
                         "LOLLIPOP · ≥ 20 RECORDS · FATAL RATE BY AREA"),
        use_container_width=True, config={"displayModeBar": False},
    )
    st.info("Market and recreational areas — where pedestrians and vehicles mix at speed — carry disproportionate fatal share.")
    st.markdown("<div class='endmark'><span>●</span>  <span>●</span>  <span>●</span></div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 8 — COLLISION LEDGER
# ════════════════════════════════════════════════════════════════════════════
elif page == "Collision Ledger":
    st.markdown("<div class='kicker'>Chapter VII · Mechanics</div>", unsafe_allow_html=True)
    st.markdown("<h1>The collision ledger.</h1>", unsafe_allow_html=True)
    st.markdown("<div class='deck'>How the crash happens — the type of contact, the manoeuvre, the junction, "
                "the road under the tyres. A mechanical account of risk.</div>",
                unsafe_allow_html=True)
    st.markdown("<div class='byline'>COLLISION · MOVEMENT · JUNCTION · SURFACE</div>", unsafe_allow_html=True)

    sel_sev = st.selectbox("Filter by Severity", severity_options(), key="cl_sev")
    filt = filter_df(df, severity=sel_sev)

    m1, m2, m3 = st.columns(3)
    m1.metric("Accidents in selection", f"{len(filt):,}")
    m2.metric("Top collision", shorten(safe_mode(filt, "Type_of_collision").title(), 20))
    m3.metric("Top junction", shorten(safe_mode(filt, "Types_of_Junction").title(), 20))

    # ── COLLISION × MOVEMENT heatmap (matrix) ───────────────────────────────
    cm = filt.groupby(["Type_of_collision", "Vehicle_movement"]).size().reset_index(name="count")
    cm = cm[cm["Type_of_collision"].str.lower() != "unknown"]
    cm = cm[cm["Vehicle_movement"].str.lower() != "unknown"]
    # Keep top combos
    top_col = cm.groupby("Type_of_collision")["count"].sum().sort_values(ascending=False).head(8).index.tolist()
    top_mov = cm.groupby("Vehicle_movement")["count"].sum().sort_values(ascending=False).head(8).index.tolist()
    cm = cm[cm["Type_of_collision"].isin(top_col) & cm["Vehicle_movement"].isin(top_mov)]
    piv = cm.pivot(index="Type_of_collision", columns="Vehicle_movement", values="count").fillna(0)
    piv = piv.loc[top_col, [m for m in top_mov if m in piv.columns]]

    fig_mx = go.Figure(go.Heatmap(
        z=piv.values,
        x=[shorten(m.title(), 18) for m in piv.columns],
        y=[shorten(t.title(), 22) for t in piv.index],
        colorscale=[[0, PAPER2], [0.5, AMBER], [1, RED]],
        text=[[f"{int(v)}" if v > 0 else "" for v in row] for row in piv.values],
        texttemplate="%{text}",
        textfont=dict(family="DM Mono, monospace", size=10, color=CREAM),
        hovertemplate="Collision: %{y}<br>Movement: %{x}<br>%{z:,} cases<extra></extra>",
        colorbar=dict(thickness=10, len=0.7, tickfont=dict(size=9, color=MUTED)),
    ))
    fig_mx.update_layout(xaxis_title="Vehicle movement", yaxis_title="Type of collision",
                         xaxis=dict(tickangle=-25))
    st.plotly_chart(
        editorial_layout(fig_mx, 520,
                         "Collision × movement matrix",
                         "HEATMAP · WHICH MANOEUVRE LEADS TO WHICH COLLISION"),
        use_container_width=True, config={"displayModeBar": False},
    )

    st.markdown("<br/>", unsafe_allow_html=True)
    left, right = st.columns(2)

    # ── Movement fatal-rate lollipop ────────────────────────────────────────
    with left:
        m = filt.copy()
        m["Vehicle_movement"] = m["Vehicle_movement"].str.lower()
        mc = m["Vehicle_movement"].value_counts()
        mf = fatal_rate_series(m, "Vehicle_movement")
        mf = mf[mf["Vehicle_movement"].isin(mc[mc >= 30].index)]
        mf["label"] = mf["Vehicle_movement"].str.title().apply(lambda x: shorten(x, 24))
        mf = mf.sort_values("Fatal Rate (%)")

        fig_ml = go.Figure()
        for _, r in mf.iterrows():
            fig_ml.add_trace(go.Scatter(
                x=[0, r["Fatal Rate (%)"]], y=[r["label"], r["label"]],
                mode="lines", line=dict(color=RULE, width=2),
                showlegend=False, hoverinfo="skip",
            ))
        fig_ml.add_trace(go.Scatter(
            x=mf["Fatal Rate (%)"], y=mf["label"], mode="markers+text",
            marker=dict(
                size=16,
                color=mf["Fatal Rate (%)"],
                colorscale=[[0, TEAL], [0.5, AMBER], [1, RED]],
                line=dict(color=INK, width=2),
            ),
            text=[f"{v:.1f}%" for v in mf["Fatal Rate (%)"]],
            textposition="middle right",
            textfont=dict(family="DM Mono, monospace", size=10.5, color=CREAM),
            showlegend=False,
            hovertemplate="<b>%{y}</b><br>Fatal rate: %{x:.2f}%<extra></extra>",
        ))
        fig_ml.update_layout(
            xaxis=dict(title="Fatal rate (%)", ticksuffix="%"),
            yaxis=dict(title=""),
            margin=dict(r=70),
        )
        st.plotly_chart(
            editorial_layout(fig_ml, 460,
                             "Which manoeuvre kills?",
                             "LOLLIPOP · FATAL RATE BY VEHICLE MOVEMENT"),
            use_container_width=True, config={"displayModeBar": False},
        )
        st.caption("Overtaking is a small share of movements but carries the highest fatal rate.")

    # ── Surface treemap coloured by fatal rate ──────────────────────────────
    with right:
        rs = filt.copy()
        rsc = rs["Road_surface_type"].value_counts().reset_index()
        rsc.columns = ["surface", "count"]
        rsf = fatal_rate_series(rs, "Road_surface_type").rename(columns={"Road_surface_type": "surface"})
        rsc = rsc.merge(rsf, on="surface", how="left").fillna(0)
        rsc["surface_t"] = rsc["surface"].str.title()

        fig_tm = px.treemap(
            rsc, path=["surface_t"], values="count", color="Fatal Rate (%)",
            color_continuous_scale=[[0, TEAL], [0.5, AMBER], [1, RED]],
            range_color=[0, max(rsc["Fatal Rate (%)"].max(), 5)],
        )
        fig_tm.update_traces(
            textinfo="label+value",
            textfont=dict(family="Fraunces, serif", size=14, color=INK),
            marker=dict(line=dict(color=INK, width=2)),
            hovertemplate="<b>%{label}</b><br>Accidents: %{value:,}<br>Fatal rate: %{color:.2f}%<extra></extra>",
        )
        fig_tm.update_layout(coloraxis_colorbar=dict(
            title=dict(text="Fatal %", font=dict(size=10, color=MUTED)),
            thickness=10, len=0.6, tickfont=dict(size=9, color=MUTED),
        ))
        st.plotly_chart(
            editorial_layout(fig_tm, 460,
                             "Road surface — size = volume, shade = lethality",
                             "TREEMAP · SURFACE TYPE"),
            use_container_width=True, config={"displayModeBar": False},
        )

    # ── CASUALTY CLASS donut ────────────────────────────────────────────────
    cas = filt[filt["Casualty_class"].str.lower() != "na"].copy()
    if not cas.empty:
        cc = cas["Casualty_class"].value_counts().reset_index()
        cc.columns = ["Class", "Count"]
        fig_cd = go.Figure(go.Pie(
            labels=cc["Class"].str.title(), values=cc["Count"],
            hole=0.6,
            marker=dict(colors=[NAVY, AMBER, RED, OLIVE][:len(cc)], line=dict(color=INK, width=2)),
            textinfo="label+percent",
            textfont=dict(family="Inter", size=12, color=CREAM),
        ))
        fig_cd.update_layout(
            showlegend=False,
            annotations=[dict(
                text=f"<b style='font-family:Fraunces,serif;font-size:28px;color:{CREAM}'>"
                     f"{int(cc['Count'].sum()):,}</b><br>"
                     f"<span style='font-family:DM Mono,monospace;font-size:10px;color:{MUTED};letter-spacing:0.15em'>"
                     f"CASUALTIES</span>",
                x=0.5, y=0.5, showarrow=False,
            )],
        )
        st.plotly_chart(
            editorial_layout(fig_cd, 400,
                             "Who pays the price?",
                             "DONUT · CASUALTY CLASS"),
            use_container_width=True, config={"displayModeBar": False},
        )

    st.markdown(
        f"<div class='pullquote'>Overtaking. Night driving. Earth roads. Pedestrian collisions. "
        f"The shortest list of targets — and the heaviest lever on mortality.</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div class='endmark'><span>●</span>  <span>●</span>  <span>●</span></div>", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
# FOOTER
# ────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
    <div style='margin-top:40px;padding-top:18px;border-top:3px double {RULE};
                font-family:DM Mono,monospace;font-size:10px;color:{MUTED};
                text-align:center;letter-spacing:0.2em;text-transform:uppercase'>
      The Road Ledger · Ethiopia 2018–2023 · Data: Ethiopian Police ·
      Built with Streamlit &amp; Plotly
    </div>
""", unsafe_allow_html=True)
