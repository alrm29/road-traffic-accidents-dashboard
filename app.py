import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Road Traffic Accidents",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Color system ──────────────────────────────────────────────────────────────
C_SLIGHT  = "#4477bb"
C_SERIOUS = "#cc8833"
C_FATAL   = "#aa3333"
C_NEUTRAL = "#556677"

SEV_COLORS = {"Slight Injury": C_SLIGHT, "Serious Injury": C_SERIOUS, "Fatal Injury": C_FATAL}
SEV_ORDER  = ["Slight Injury", "Serious Injury", "Fatal Injury"]
DAY_ORDER  = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
EXP_ORDER  = ["below 1yr","1-2yr","2-5yr","5-10yr","above 10yr","no licence"]
TIME_ORDER = ["Night (0-6)","Morning (6-12)","Afternoon (12-17)","Evening (17-21)","Late Night (21-24)"]
QUAL       = ["#4477bb","#cc8833","#aa3333","#448866","#7755aa","#bb6644","#448899","#996633"]

st.markdown("""
<style>
.stApp { background-color: #f5f4e8; }
.block-container { padding-top: .8rem; max-width: 1420px; }
section[data-testid="stSidebar"] { background-color: #ecebd8; }
[data-testid="stMetricValue"] { color: #1a1a2e !important; font-size: 1.05rem !important; font-weight: 700 !important; white-space: normal !important; word-break: break-word !important; line-height: 1.35 !important; overflow-wrap: anywhere !important; }
[data-testid="stMetricLabel"] { color: #666 !important; font-size: .72rem !important; font-weight: 600; text-transform: uppercase; letter-spacing: .05em; }
[data-testid="stMetric"] { background: #e6e5d0; border-radius: 8px; padding: 12px 14px; min-height: 80px; }
h1 { color: #1a1a2e !important; font-size: 2.2rem !important; font-weight: 800 !important; letter-spacing: -.02em; margin-bottom: .1rem !important; }
h2 { color: #2a2a44 !important; font-size: 1.1rem !important; font-weight: 700 !important; margin: 1rem 0 .25rem !important; }
p, label { color: #444; }
.stCaption p { color: #777 !important; font-style: italic; font-size: .82rem !important; margin-top: 2px; }
hr { border-color: #d5d4c0; }
.stAlert { background-color: #e4e3cf !important; border-color: #c5c4b0 !important; }
div[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load():
    df = pd.read_csv("RTA_Dataset_cleaned.csv")
    for c in df.columns:
        if df[c].dtype == "object":
            df[c] = df[c].astype(str).str.strip().str.lower()
    df["Type_of_vehicle"] = df["Type_of_vehicle"].str.replace(r"\?", "-", regex=True)
    sm = {"slight injury":"Slight Injury","serious injury":"Serious Injury","fatal injury":"Fatal Injury"}
    df["severity"] = df["Accident_severity"].map(sm)
    df["hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S", errors="coerce").dt.hour
    def tb(h):
        if pd.isna(h): return "Unknown"
        if h<6:  return "Night (0-6)"
        if h<12: return "Morning (6-12)"
        if h<17: return "Afternoon (12-17)"
        if h<21: return "Evening (17-21)"
        return "Late Night (21-24)"
    df["time_period"] = df["hour"].apply(tb)
    df["Area_accident_occured"] = df["Area_accident_occured"].replace(
        "rural village areasoffice areas","rural village areas")
    df["Defect_of_vehicle"] = df["Defect_of_vehicle"].replace({"7":"unknown","5":"unknown"})
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
    df["Number_of_casualties"]        = pd.to_numeric(df["Number_of_casualties"], errors="coerce")
    df["Number_of_vehicles_involved"] = pd.to_numeric(df["Number_of_vehicles_involved"], errors="coerce")
    df["is_fatal"] = df["severity"] == "Fatal Injury"
    return df

df = load()

AREA_GEO = {
    "office areas":        {"city":"Addis Ababa (Bole)",  "lat":9.0121, "lon":38.7636},
    "residential areas":   {"city":"Addis Ababa (Yeka)",  "lat":9.0250, "lon":38.8100},
    "church areas":        {"city":"Bahir Dar",            "lat":11.5742,"lon":37.3614},
    "industrial areas":    {"city":"Adama",                "lat":8.5400, "lon":39.2690},
    "school areas":        {"city":"Hawassa",              "lat":7.0621, "lon":38.4764},
    "market areas":        {"city":"Dire Dawa",            "lat":9.6009, "lon":41.8501},
    "hospital areas":      {"city":"Mekelle",              "lat":13.4967,"lon":39.4753},
    "recreational areas":  {"city":"Bishoftu",             "lat":8.7523, "lon":38.9785},
    "rural village areas": {"city":"Jimma",                "lat":7.6667, "lon":36.8333},
    "outside rural areas": {"city":"Gondar",               "lat":12.6030,"lon":37.4521},
    "other":               {"city":"Addis Ababa (Centre)", "lat":9.0250, "lon":38.7469},
}


# ── Helpers ───────────────────────────────────────────────────────────────────
def sh(t, n=28):
    t = str(t).replace("_"," ").title()
    return t if len(t)<=n else t[:n-3]+"..."

def fr(d): return round(d["is_fatal"].mean()*100,1) if len(d) else 0.0

def sm(d,c):
    s = d[c].dropna().astype(str)
    s = s[~s.str.lower().isin(["nan","na","unknown","other",""])]
    return sh(s.mode().iloc[0],36) if not s.empty else "N/A"

def fl(fig, h=460, t=38, b=55, l=20, r=20):
    fig.update_layout(
        height=h, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#333",size=12),
        margin=dict(l=l,r=r,t=t,b=b),
        legend=dict(
            bgcolor="rgba(236,235,216,0.9)", bordercolor="#c8c7b0", borderwidth=1,
            font=dict(color="#333",size=12), orientation="h",
            yanchor="top", y=-0.13, xanchor="center", x=0.5,
        ),
        xaxis=dict(gridcolor="#dddcc8",linecolor="#c8c7b0",
                   tickfont=dict(color="#555",size=11),title_font=dict(color="#555",size=12)),
        yaxis=dict(gridcolor="#dddcc8",linecolor="#c8c7b0",
                   tickfont=dict(color="#555",size=11),title_font=dict(color="#555",size=12)),
        hoverlabel=dict(bgcolor="white",font=dict(color="#333",size=12)),
    )
    if fig.layout.updatemenus:
        fig.layout.updatemenus[0].bgcolor="#ecebd8"
        fig.layout.updatemenus[0].bordercolor="#aaa"
        fig.layout.updatemenus[0].font=dict(color="#333")
    if fig.layout.sliders:
        fig.layout.sliders[0].bgcolor="#ddd"
        fig.layout.sliders[0].font=dict(color="#333")
        fig.layout.sliders[0].currentvalue.font=dict(color="#333")
    return fig

def spd(fig, fm=900, tm=480):
    try:
        fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"]=fm
        fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"]=tm
    except: pass
    return fig

def h2(t): st.markdown(f"## {t}")
def cap(t): st.caption(t)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Road Traffic Accidents")
    st.caption("Ethiopia  ·  2018–2023")
    st.markdown("---")
    page = st.radio("", ["Overview","Causes & Risk","Driver & Vehicle",
                         "Time & Place","Collision & Road"],
                    label_visibility="collapsed")
    st.markdown("---")
    st.markdown('<p style="font-size:.7rem;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:.07em;margin:0">Filters</p>',
                unsafe_allow_html=True)
    yr_vals = sorted(df["Year"].dropna().unique().astype(int).tolist())
    sel_yr  = st.multiselect("Year", yr_vals, default=yr_vals)
    sel_sev = st.selectbox("Severity", ["All"]+SEV_ORDER)
    st.markdown("---")
    fdf = df[df["Year"].astype(int).isin(sel_yr)] if sel_yr else df.copy()
    if sel_sev!="All": fdf = fdf[fdf["severity"]==sel_sev]
    st.metric("Records", f"{len(fdf):,}")
    st.metric("Fatal rate", f"{fr(fdf)}%")
    st.markdown(
        f'<div style="margin-top:10px;font-size:.8rem;line-height:2.2">'
        f'<span style="color:{C_SLIGHT}">&#11044;</span> Slight&nbsp;&nbsp;'
        f'<span style="color:{C_SERIOUS}">&#11044;</span> Serious&nbsp;&nbsp;'
        f'<span style="color:{C_FATAL}">&#11044;</span> Fatal</div>',
        unsafe_allow_html=True)
    st.caption(f"{len(df):,} total incidents · 5 pages")

if fdf.empty:
    st.warning("No records match the filters."); st.stop()


# =============================================================================
# OVERVIEW — 4 chart types: bar | line | funnel | donut
# =============================================================================
if page=="Overview":
    st.title("Overview")
    st.caption("Scale, severity distribution, yearly trend, and escalation funnel — Ethiopia 2018–2023.")
    st.markdown("---")

    tot = len(fdf); fat = int(fdf["is_fatal"].sum())
    ser = int((fdf["severity"]=="Serious Injury").sum())
    sli = int((fdf["severity"]=="Slight Injury").sum())

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Accidents",  f"{tot:,}")
    c2.metric("Slight Injuries",  f"{sli:,}")
    c3.metric("Serious Injuries", f"{ser:,}")
    c4.metric("Fatal Cases",      f"{fat:,}  ({fr(fdf)}%)")

    st.markdown("---")
    L,R = st.columns(2)

    # Chart 1 — Severity bar
    with L:
        h2("Accidents by severity level")
        sc = fdf["severity"].value_counts().reindex(SEV_ORDER).fillna(0).reset_index()
        sc.columns = ["Severity","Count"]
        sc["Pct"] = (sc["Count"]/sc["Count"].sum()*100).round(1)
        mc = sc["Count"].max()
        sc["Disp"] = sc["Count"].apply(lambda v: max(v, mc*0.03) if v>0 else 0)
        b = px.bar(sc, x="Severity", y="Disp", color="Severity",
                   color_discrete_map=SEV_COLORS, text="Pct",
                   custom_data=["Count"], labels={"Disp":"Accidents","Severity":""})
        b.update_traces(texttemplate="%{text}%", textposition="outside", textfont_size=14,
                        hovertemplate="<b>%{x}</b><br>%{customdata[0]:,} accidents (%{text}%)<extra></extra>")
        b.update_layout(showlegend=False,
                        yaxis=dict(range=[0,mc*1.3],showticklabels=False,title=""),
                        xaxis=dict(tickangle=0,tickfont=dict(size=13)))
        st.plotly_chart(fl(b,460,t=20,b=25), use_container_width=True)
        cap("Slight injuries make up 84.6% of all accidents. Fatal cases are 1.3% — small in count, highest in consequence.")

    # Chart 2 — Yearly trend line
    with R:
        h2("Accidents recorded per year")
        by = fdf.groupby("Year").size().reset_index(name="Count")
        by["Year"] = by["Year"].astype(int)
        if not by.empty:
            pk = by.loc[by["Count"].idxmax()]
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=by["Year"], y=by["Count"],
                mode="lines+markers+text",
                text=by["Count"], textposition="top center", textfont=dict(size=13),
                line=dict(color=C_SLIGHT,width=2.5), marker=dict(size=9,color=C_SLIGHT),
                name="Accidents",
            ))
            fig.update_layout(showlegend=False,
                xaxis=dict(tickmode="array",tickvals=by["Year"].tolist(),title="Year"),
                yaxis=dict(rangemode="tozero",title="Number of accidents"),
                annotations=[dict(x=pk["Year"],y=pk["Count"],text="Peak year",
                    showarrow=True,arrowhead=2,ax=45,ay=-35,
                    font=dict(size=12,color=C_FATAL),arrowcolor=C_FATAL)])
            st.plotly_chart(fl(fig,460,t=20,b=50), use_container_width=True)
            cap("Annual totals hold steady near 2,000. Serious injuries show a gradual rise post-2020.")

    st.markdown("---")
    L2,R2 = st.columns(2)

    # Chart 3 — Severity funnel (NEW — distinct type)
    with L2:
        h2("Accident severity escalation funnel")
        inj = int(fdf["severity"].isin(["Slight Injury","Serious Injury"]).sum())
        funnel = go.Figure(go.Funnel(
            y=["All Accidents","Any Injury","Serious Injury","Fatal"],
            x=[tot, inj, ser, fat],
            marker=dict(color=["#667788",C_SLIGHT,C_SERIOUS,C_FATAL]),
            textinfo="value+percent initial",
            textfont=dict(size=13),
            hovertemplate="<b>%{y}</b><br>%{x:,} cases (%{percentInitial})<extra></extra>",
        ))
        funnel.update_layout(showlegend=False,
                             paper_bgcolor="rgba(0,0,0,0)",
                             font=dict(color="#333",size=12),
                             margin=dict(l=20,r=20,t=20,b=20),
                             height=460,
                             hoverlabel=dict(bgcolor="white",font=dict(color="#333")))
        st.plotly_chart(funnel, use_container_width=True)
        cap("Each stage filters down to the next severity level. Fatal cases represent 1.3% of all accidents — the critical intervention target.")

    # Chart 4 — Severity donut
    with R2:
        h2("Severity breakdown")
        sd = fdf["severity"].value_counts().reindex(SEV_ORDER).fillna(0).reset_index()
        sd.columns = ["Severity","Count"]
        donut = go.Figure(go.Pie(
            labels=sd["Severity"], values=sd["Count"], hole=0.58,
            marker=dict(colors=[SEV_COLORS[s] for s in sd["Severity"]],
                        line=dict(color="white",width=3)),
            textinfo="label+percent", textfont=dict(color="#333",size=13),
            hovertemplate="<b>%{label}</b><br>%{value:,} (%{percent})<extra></extra>",
        ))
        donut.add_annotation(text=f"<b>{tot:,}</b><br><span style='font-size:11px'>accidents</span>",
                             x=0.5,y=0.5,showarrow=False,font=dict(color="#222",size=19))
        donut.update_layout(showlegend=False,
                            paper_bgcolor="rgba(0,0,0,0)",
                            font=dict(color="#333"),
                            margin=dict(l=20,r=20,t=20,b=20),
                            height=460,
                            hoverlabel=dict(bgcolor="white",font=dict(color="#333")))
        st.plotly_chart(donut, use_container_width=True)
        cap("The donut confirms the scale: with 12,316 accidents, 84.6% are slight — but the 1.3% fatal share is where policy must focus.")


# =============================================================================
# CAUSES & RISK — 4 chart types: horiz bar | horiz bar (color) | bubble scatter | animated bar
# =============================================================================
elif page=="Causes & Risk":
    st.title("Causes & Risk")
    st.caption("Which causes are most frequent, which are most deadly, and how cause volumes shift year by year.")

    m1,m2,m3 = st.columns(3)
    m1.metric("Accidents", f"{len(fdf):,}")
    m2.metric("Most common cause", sm(fdf,"Cause_of_accident").title())
    m3.metric("Fatal rate", f"{fr(fdf)}%")
    st.markdown("---")

    cs = (fdf.groupby("Cause_of_accident")
          .agg(Accidents=("severity","count"),Fatals=("is_fatal","sum"),
               Avg_Cas=("Number_of_casualties","mean"))
          .reset_index())
    cs = cs[cs["Accidents"]>=30].copy()
    cs["Fatal Rate (%)"] = (cs["Fatals"]/cs["Accidents"]*100).round(1)
    cs["Avg Casualties"]  = cs["Avg_Cas"].round(2)
    cs["Cause"] = cs["Cause_of_accident"].apply(lambda x: sh(x,32))

    L,R = st.columns(2)

    with L:
        h2("Top 10 most frequent causes")
        freq = fdf["Cause_of_accident"].value_counts().head(10).reset_index()
        freq.columns=["Cause","Accidents"]
        freq["Cause"]=freq["Cause"].apply(lambda x:sh(x,32))
        freq=freq.sort_values("Accidents")
        b=px.bar(freq,x="Accidents",y="Cause",orientation="h",
                 color_discrete_sequence=[C_SLIGHT],
                 labels={"Cause":""},text="Accidents")
        b.update_traces(textposition="outside",textfont_size=12)
        b.update_layout(showlegend=False,xaxis=dict(range=[0,freq["Accidents"].max()*1.22]))
        st.plotly_chart(fl(b,520,t=18,b=25), use_container_width=True)
        cap("No distancing leads by a wide margin — a behavioural cause directly addressable through enforcement.")

    with R:
        h2("Deadliest causes by fatal rate")
        st.caption("Causes with fewer than 30 records excluded")
        risk=cs.sort_values("Fatal Rate (%)").tail(10)
        b=px.bar(risk,x="Fatal Rate (%)",y="Cause",orientation="h",
                 color="Fatal Rate (%)",
                 color_continuous_scale=[[0,"#f5d0d0"],[1,C_FATAL]],
                 text="Fatal Rate (%)",labels={"Cause":""})
        b.update_traces(texttemplate="%{text}%",textposition="outside",textfont_size=12)
        b.update_layout(showlegend=False,coloraxis_showscale=False,
                        xaxis=dict(range=[0,risk["Fatal Rate (%)"].max()*1.28]))
        st.plotly_chart(fl(b,520,t=18,b=25,r=55), use_container_width=True)
        cap("Overloading and turnover carry fatal rates above 2.5% — nearly double the overall 1.3% average.")

    st.markdown("---")
    L2,R2 = st.columns(2)

    with L2:
        h2("Frequency vs fatal risk")
        st.caption("Bubble size = avg casualties per accident — a 3-variable view of cause danger")
        bub=px.scatter(cs,x="Accidents",y="Fatal Rate (%)",
                       size="Avg Casualties",color="Fatal Rate (%)",
                       hover_name="Cause",
                       hover_data={"Accidents":True,"Fatal Rate (%)":True,"Avg Casualties":True,"Cause":False},
                       color_continuous_scale=[[0,"#fce8e8"],[0.5,"#dd8855"],[1,C_FATAL]],
                       size_max=52,labels={"Accidents":"Number of Accidents"})
        bub.update_layout(coloraxis_showscale=False,showlegend=False,
                        yaxis=dict(range=[0, cs["Fatal Rate (%)"].max()*1.2]))
        st.plotly_chart(fl(bub,520,t=18,b=25), use_container_width=True)
        cap("Top-right quadrant = frequent AND deadly. Moving backward and driving carelessly sit dangerously high on both axes.")

    with R2:
        h2("Top causes by year")
        st.caption("Animation · press ▶ · Fixed axis and colors — bar length changes are real year-to-year shifts.")
        yrs=sorted(df["Year"].dropna().astype(int).unique())
        ab=df.copy()
        if sel_sev!="All": ab=ab[ab["severity"]==sel_sev]
        T8=ab["Cause_of_accident"].value_counts().head(8).index.tolist()
        D8={c:sh(c,28) for c in T8}
        C8={D8[c]:QUAL[i%len(QUAL)] for i,c in enumerate(T8)}
        ad=(ab[ab["Cause_of_accident"].isin(T8)]
            .groupby(["Year","Cause_of_accident"]).size().reset_index(name="Accidents"))
        fi=pd.MultiIndex.from_product([yrs,T8],names=["Year","Cause_of_accident"])
        ad=(ad.set_index(["Year","Cause_of_accident"]).reindex(fi,fill_value=0).reset_index())
        ad["Cause"]=ad["Cause_of_accident"].map(D8)
        ad["Year"]=ad["Year"].astype(str)
        ym=int(ad["Accidents"].max()*1.3)
        f1=px.bar(ad,x="Accidents",y="Cause",color="Cause",orientation="h",
                  animation_frame="Year",animation_group="Cause",
                  color_discrete_map=C8,range_x=[0,ym],
                  labels={"Accidents":"Number of Accidents","Cause":""})
        f1.update_layout(showlegend=False,yaxis=dict(categoryorder="total ascending"))
        # Fix bar order to overall total — bars stay in place, only lengths change
        fixed_order = (ad.groupby("Cause")["Accidents"].sum()
                       .sort_values(ascending=True).index.tolist())
        f1.update_layout(yaxis=dict(categoryorder="array", categoryarray=fixed_order))
        f1=spd(f1,900,450)
        st.plotly_chart(fl(f1,520,t=18,b=50), use_container_width=True)


# =============================================================================
# DRIVER & VEHICLE — 4 types: stacked bar | scatter bubble | horiz bar | animated stacked bar
# =============================================================================
elif page=="Driver & Vehicle":
    st.title("Driver & Vehicle")
    st.caption("Who is involved in accidents — age, experience, and vehicle type — and how risk changes over time.")

    gcol="Sex_of_driver"
    gopts=["All"]+[v.title() for v in sorted(df[gcol].dropna().unique()) if v!="unknown"]
    sg=st.selectbox("Filter by gender",gopts)
    if sg!="All": fdf=fdf[fdf[gcol]==sg.lower()]

    m1,m2,m3=st.columns(3)
    m1.metric("Accidents",f"{len(fdf):,}")
    m2.metric("Most common outcome",sm(fdf,"severity"))
    m3.metric("Fatal rate",f"{fr(fdf)}%")
    st.markdown("---")
    L,R=st.columns(2)

    # Chart 1 — Age × severity stacked bar
    with L:
        h2("Driver age group by severity")
        as_=fdf.groupby(["Age_band_of_driver","severity"]).size().reset_index(name="Count")
        ao=["under 18","18-30","31-50","over 51","unknown"]
        as_["Age_band_of_driver"]=pd.Categorical(as_["Age_band_of_driver"],categories=ao,ordered=True)
        as_=as_.sort_values("Age_band_of_driver")
        b=px.bar(as_,x="Age_band_of_driver",y="Count",color="severity",
                 color_discrete_map=SEV_COLORS,category_orders={"severity":SEV_ORDER},
                 barmode="stack",
                 labels={"Age_band_of_driver":"Age group","Count":"Accidents","severity":"Severity"})
        st.plotly_chart(fl(b,500,t=18,b=80), use_container_width=True)
        cap("18–30 and 31–50 dominate by volume. Over-51 drivers show a proportionally higher serious and fatal share.")

    # Chart 2 — Experience vs accidents bubble scatter (NEW distinct type)
    with R:
        h2("Driving experience — accidents vs fatal risk")
        st.caption("Bubble size = number of accidents · color = fatal rate — one bubble per experience tier")
        ed=(fdf[fdf["Driving_experience"].isin(EXP_ORDER)]
            .groupby("Driving_experience")
            .agg(Accidents=("severity","count"),Fatals=("is_fatal","sum"))
            .reset_index())
        ed=ed[ed["Accidents"]>=10].copy()
        ed["Fatal Rate (%)"]=( ed["Fatals"]/ed["Accidents"]*100).round(1)
        ed["Driving_experience"]=pd.Categorical(ed["Driving_experience"],categories=EXP_ORDER,ordered=True)
        ed=ed.sort_values("Driving_experience")
        ed["exp_rank"]=range(1,len(ed)+1)
        bub2=px.scatter(ed,x="exp_rank",y="Fatal Rate (%)",
                        size="Accidents",color="Fatal Rate (%)",
                        hover_name="Driving_experience",
                        hover_data={"Accidents":True,"Fatal Rate (%)":True,"exp_rank":False},
                        color_continuous_scale=[[0,"#d0e8f5"],[0.5,C_SERIOUS],[1,C_FATAL]],
                        size_max=60,labels={"exp_rank":"Driving experience","Fatal Rate (%)":"Fatal Rate (%)"})
        bub2.update_layout(
            coloraxis_showscale=False,showlegend=False,
            xaxis=dict(tickmode="array",tickvals=list(range(1,len(ed)+1)),
                       ticktext=[sh(e,12) for e in ed["Driving_experience"]],tickangle=-20),
        )
        st.plotly_chart(fl(bub2,500,t=18,b=70), use_container_width=True)
        cap("Bubble size = accident frequency. Height = fatal risk. 2-5yr drivers have the most accidents; above-10yr retains surprisingly high fatal rate.")

    st.markdown("---")
    L2,R2=st.columns(2)

    # Chart 3 — Vehicle type bar
    with L2:
        h2("Vehicle types involved in accidents")
        veh=(fdf[~fdf["Type_of_vehicle"].isin(["unknown","other"])]
             ["Type_of_vehicle"].value_counts().head(8).reset_index())
        veh.columns=["Vehicle","Count"]
        veh["Vehicle"]=veh["Vehicle"].apply(lambda x:sh(x,28))
        veh=veh.sort_values("Count")
        b=px.bar(veh,x="Count",y="Vehicle",orientation="h",
                 color_discrete_sequence=["#448866"],
                 labels={"Count":"Accidents","Vehicle":""},text="Count")
        b.update_traces(textposition="outside",textfont_size=12)
        b.update_layout(showlegend=False,xaxis=dict(range=[0,veh["Count"].max()*1.22]))
        st.plotly_chart(fl(b,500,t=18,b=25), use_container_width=True)
        cap("Automobiles and lorries account for the majority — consistent with the Ethiopian road fleet composition.")

    # Chart 4 — Animation: experience × severity stacked bar
    with R2:
        h2("Driving experience by severity over time")
        st.caption("Animation · press ▶ · Fixed Y-axis ensures height changes are real shifts, not rescaling.")
        ab3=df.copy()
        if sel_sev!="All": ab3=ab3[ab3["severity"]==sel_sev]
        if sg!="All": ab3=ab3[ab3[gcol]==sg.lower()]
        yrs3=sorted(ab3["Year"].dropna().astype(int).unique())
        ae=(ab3[ab3["Driving_experience"].isin(EXP_ORDER)]
            .groupby(["Year","Driving_experience","severity"]).size().reset_index(name="Count"))
        ix3=pd.MultiIndex.from_product([yrs3,EXP_ORDER,SEV_ORDER],
                                        names=["Year","Driving_experience","severity"])
        ae=(ae.set_index(["Year","Driving_experience","severity"]).reindex(ix3,fill_value=0).reset_index())
        ae["Year"]=ae["Year"].astype(str)
        ym3=int(ae.groupby(["Year","Driving_experience"])["Count"].sum().max()*1.25)
        f3=px.bar(ae,x="Driving_experience",y="Count",color="severity",
                  animation_frame="Year",animation_group="Driving_experience",
                  color_discrete_map=SEV_COLORS,
                  category_orders={"severity":SEV_ORDER,"Driving_experience":EXP_ORDER},
                  barmode="stack",range_y=[0,ym3],
                  labels={"Driving_experience":"Experience","Count":"Accidents","severity":"Severity"})
        f3.update_layout(xaxis=dict(tickangle=-15))
        f3=spd(f3,900,480)
        st.plotly_chart(fl(f3,500,t=18,b=90), use_container_width=True)
        cap("2-5yr and 5-10yr groups dominate across all years. The severity split reveals fatal risk persists even with experience.")

    # Chart 5 — 3D scatter: cause × accident count × fatal rate × avg casualties
    st.markdown("---")
    h2("Cause risk in 3D — frequency, fatality, and casualty depth")
    st.caption(
        "Each point = one accident cause  ·  X = accident count  ·  "
        "Y = fatal rate (%)  ·  Z = avg casualties per accident  ·  "
        "Bubble size = total casualties  ·  Colour = fatal rate  ·  "
        "Causes with fewer than 30 records excluded  ·  Drag to rotate"
    )
    risk3d = (
        fdf.groupby("Cause_of_accident")
        .agg(
            accidents=("severity","count"),
            fatal_cases=("is_fatal","sum"),
            avg_casualties=("Number_of_casualties","mean"),
            total_casualties=("Number_of_casualties","sum"),
        )
        .reset_index()
    )
    risk3d = risk3d[risk3d["accidents"] >= 30].copy()
    risk3d["fatal_rate"]       = (risk3d["fatal_cases"] / risk3d["accidents"] * 100).round(2)
    risk3d["avg_casualties"]   = risk3d["avg_casualties"].round(2)
    risk3d["total_casualties"] = risk3d["total_casualties"].clip(lower=1)
    risk3d["Cause"]            = risk3d["Cause_of_accident"].apply(lambda x: sh(x, 32))
    risk3d = risk3d.sort_values("accidents", ascending=False).head(15)

    fig3d = px.scatter_3d(
        risk3d,
        x="accidents",
        y="fatal_rate",
        z="avg_casualties",
        size="total_casualties",
        color="fatal_rate",
        color_continuous_scale=[[0,"#d0e8f5"],[0.4,C_SERIOUS],[1,C_FATAL]],
        hover_name="Cause",
        hover_data={
            "accidents":True,
            "fatal_rate":True,
            "avg_casualties":True,
            "total_casualties":True,
            "Cause":False,
        },
        size_max=28,
        opacity=0.88,
        labels={
            "accidents":       "Accident Count",
            "fatal_rate":      "Fatal Rate (%)",
            "avg_casualties":  "Avg Casualties",
            "total_casualties":"Total Casualties",
        },
    )
    fig3d.update_layout(
        height=580,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#333", size=12),
        margin=dict(l=0, r=0, t=20, b=0),
        coloraxis_colorbar=dict(
            title=dict(text="Fatal %", font=dict(color="#555", size=12)),
            tickfont=dict(color="#555", size=11),
            thickness=14,
        ),
        scene=dict(
            bgcolor="#eeede0",
            xaxis=dict(
                title="Accident Count",
                backgroundcolor="#e8e7d8",
                gridcolor="#cccbb8",
                linecolor="#bbbaa8",
                tickfont=dict(color="#555", size=10),
                title_font=dict(color="#555", size=12),
            ),
            yaxis=dict(
                title="Fatal Rate (%)",
                backgroundcolor="#e8e7d8",
                gridcolor="#cccbb8",
                linecolor="#bbbaa8",
                tickfont=dict(color="#555", size=10),
                title_font=dict(color="#555", size=12),
            ),
            zaxis=dict(
                title="Avg Casualties",
                backgroundcolor="#e8e7d8",
                gridcolor="#cccbb8",
                linecolor="#bbbaa8",
                tickfont=dict(color="#555", size=10),
                title_font=dict(color="#555", size=12),
            ),
        ),
        hoverlabel=dict(bgcolor="white", font=dict(color="#333", size=12)),
    )
    st.plotly_chart(fig3d, use_container_width=True)
    cap(
        "The 3D view reveals cause clusters invisible in 2D: causes high on all three axes "
        "(top-right, elevated Z) are the most complex risk profiles — frequent, deadly, and injurious. "
        "Drag to rotate and hover for exact values."
    )

    # Summary table
    st.markdown("---")
    h2("Driver risk summary table")
    tbl=(fdf[fdf["Driving_experience"].isin(EXP_ORDER)]
         .groupby("Driving_experience")
         .agg(Accidents=("severity","count"),
              Fatal_Cases=("is_fatal","sum"),
              Serious_Cases=("severity",lambda x:(x=="Serious Injury").sum()),
              Avg_Casualties=("Number_of_casualties","mean"))
         .reset_index())
    tbl["Fatal Rate (%)"]=(tbl["Fatal_Cases"]/tbl["Accidents"]*100).round(1)
    tbl["Avg Casualties"]=tbl["Avg_Casualties"].round(2)
    tbl["Driving_experience"]=pd.Categorical(tbl["Driving_experience"],categories=EXP_ORDER,ordered=True)
    tbl=tbl.sort_values("Driving_experience").reset_index(drop=True)
    tbl=tbl.rename(columns={"Driving_experience":"Experience",
                             "Fatal_Cases":"Fatal Cases","Serious_Cases":"Serious Cases"})
    st.dataframe(
        tbl[["Experience","Accidents","Fatal Cases","Serious Cases","Fatal Rate (%)","Avg Casualties"]],
        use_container_width=True, hide_index=True,
    )
    cap("Table confirms that 2-5yr drivers have the highest absolute accident count, while above-10yr drivers retain a disproportionate fatal rate.")


# =============================================================================
# TIME & PLACE — 4 chart types: heatmap | bar+color | horiz bar | map
# =============================================================================
elif page=="Time & Place":
    st.title("Time & Place")
    st.caption("When accidents cluster through the day and which area types carry the highest fatal risk.")

    m1,m2,m3=st.columns(3)
    m1.metric("Accidents",f"{len(fdf):,}")
    ph=int(fdf["hour"].dropna().mode().iloc[0]) if not fdf["hour"].dropna().empty else 17
    m2.metric("Peak accident hour",f"{ph:02d}:00")
    m3.metric("Fatal rate",f"{fr(fdf)}%")
    st.markdown("---")

    # Chart 1 — Hour × day heatmap (full width)
    h2("Accident heatmap — hour of day vs day of week")
    cap("Darker cells = more accidents. The evening rush (16–19h) stands out across all weekdays.")
    hm=fdf.dropna(subset=["hour"]).copy()
    hm["Day_of_week"]=hm["Day_of_week"].str.strip()
    hm=hm[hm["Day_of_week"].isin(DAY_ORDER)]
    hp=(hm.groupby(["Day_of_week","hour"]).size()
        .unstack(fill_value=0).reindex(DAY_ORDER).fillna(0))
    hfig=go.Figure(go.Heatmap(
        z=hp.values,
        x=[f"{h:02d}:00" for h in hp.columns],
        y=[d.title() for d in hp.index],
        colorscale="YlOrRd",
        hovertemplate="<b>%{y}</b> at %{x}<br>%{z:,} accidents<extra></extra>",
        colorbar=dict(title=dict(text="Count",font=dict(color="#555",size=12)),
                      tickfont=dict(color="#555",size=11),thickness=14),
    ))
    hfig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#333"), height=320,
        margin=dict(l=90,r=50,t=10,b=65),
        xaxis=dict(tickangle=-45,tickfont=dict(color="#555",size=10),
                   title="Hour of day",title_font=dict(color="#555",size=12)),
        yaxis=dict(tickfont=dict(color="#555",size=12)),
        hoverlabel=dict(bgcolor="white",font=dict(color="#333")),
    )
    st.plotly_chart(hfig, use_container_width=True)
    st.markdown("---")

    L,R=st.columns(2)

    # Chart 2 — Time period bar (count + fatal rate color)
    with L:
        h2("Accidents by time of day")
        st.caption("Bar height = accident count  ·  bar color = fatal rate — two variables, one chart")
        tp=fdf[fdf["time_period"]!="Unknown"].copy()
        ts=(tp.groupby("time_period")
            .agg(Accidents=("severity","count"),Fatals=("is_fatal","sum")).reset_index())
        ts["Fatal Rate (%)"]=( ts["Fatals"]/ts["Accidents"]*100).round(1)
        ts["time_period"]=pd.Categorical(ts["time_period"],categories=TIME_ORDER,ordered=True)
        ts=ts.sort_values("time_period")
        bt=px.bar(ts,x="time_period",y="Accidents",
                  color="Fatal Rate (%)",
                  color_continuous_scale=[[0,"#d0e8d0"],[0.5,C_SERIOUS],[1,C_FATAL]],
                  text="Fatal Rate (%)",labels={"time_period":"","Fatal Rate (%)":"Fatal Rate (%)"})
        bt.update_traces(texttemplate="%{text}%",textposition="outside",textfont_size=13)
        bt.update_layout(xaxis=dict(tickangle=-15),
                         coloraxis_colorbar=dict(
                             title=dict(text="Fatal %",font=dict(color="#555",size=11)),
                             tickfont=dict(color="#555",size=10),thickness=12))
        st.plotly_chart(fl(bt,480,t=18,b=80), use_container_width=True)
        cap("Afternoon has the most accidents. Night and late night have 2-3x higher fatal rates despite far fewer incidents.")

    # Chart 3 — Area fatal rate bar
    with R:
        h2("Fatal rate by area type")
        as2=(fdf.groupby("Area_accident_occured")
             .agg(Accidents=("severity","count"),Fatals=("is_fatal","sum")).reset_index())
        as2=as2[~as2["Area_accident_occured"].isin(["unknown","other"])&(as2["Accidents"]>=20)].copy()
        as2["Fatal Rate (%)"]=( as2["Fatals"]/as2["Accidents"]*100).round(1)
        as2["Area"]=as2["Area_accident_occured"].apply(lambda x:sh(x,26))
        as2=as2.sort_values("Fatal Rate (%)")
        ba=px.bar(as2,x="Fatal Rate (%)",y="Area",orientation="h",
                  color="Fatal Rate (%)",
                  color_continuous_scale=[[0,"#f5d0d0"],[1,C_FATAL]],
                  text="Fatal Rate (%)",labels={"Area":""})
        ba.update_traces(texttemplate="%{text}%",textposition="outside",textfont_size=12)
        ba.update_layout(showlegend=False,coloraxis_showscale=False,
                         xaxis=dict(range=[0,as2["Fatal Rate (%)"].max()*1.3]))
        st.plotly_chart(fl(ba,480,t=18,b=30,r=60), use_container_width=True)
        cap("Market and recreational areas carry the highest fatal rates — pedestrian exposure and mixed traffic conditions.")

    st.markdown("---")

    # Chart 4 — Geographic map with verified non-overlapping coordinates
    # Each area category mapped to a real Ethiopian city >= 76km from all others
    AREA_MAP = {
        "office areas":        {"city":"Addis Ababa",    "note":"Capital CBD — offices & government", "lat":9.0121,  "lon":38.7636},
        "residential areas":   {"city":"Haramaya",       "note":"University residential town",         "lat":9.5450,  "lon":39.9820},
        "church areas":        {"city":"Bahir Dar",      "note":"Lake Tana — major church sites",      "lat":11.5742, "lon":37.3614},
        "industrial areas":    {"city":"Adama",          "note":"Eastern industrial corridor",         "lat":8.5400,  "lon":39.2690},
        "school areas":        {"city":"Debre Berhan",   "note":"Known educational hub",               "lat":11.1400, "lon":38.6200},
        "recreational areas":  {"city":"Ziway",          "note":"Lake resort & recreation town",       "lat":7.9370,  "lon":38.7030},
        "hospital areas":      {"city":"Mekelle",        "note":"Major hospital & health centre",      "lat":13.4967, "lon":39.4753},
        "market areas":        {"city":"Dire Dawa",      "note":"Largest market & trade hub",          "lat":9.6009,  "lon":41.8501},
        "outside rural areas": {"city":"Gondar",         "note":"Northern rural gateway",              "lat":12.6030, "lon":37.4521},
        "rural village areas": {"city":"Jimma",          "note":"Southwest rural farming region",      "lat":7.6667,  "lon":36.8333},
        "other":               {"city":"Wolaita Sodo",   "note":"Southern mixed-use town",             "lat":6.8500,  "lon":37.9000},
    }

    h2("Accident area types — mapped across Ethiopia")
    st.info(
        "The dataset records area category, not GPS coordinates. "
        "Each bubble is placed at a real Ethiopian city chosen to represent that area type "
        "(e.g. market areas → Dire Dawa · hospital areas → Mekelle · church areas → Bahir Dar). "
        "All cities are at least 76 km apart — no overlap.  "
        "Bubble size = accident count  ·  Colour = fatal rate."
    )

    ar=(fdf.groupby("Area_accident_occured")
        .agg(Accidents=("severity","count"),Fatals=("is_fatal","sum"),
             Avg_Casualties=("Number_of_casualties","mean"))
        .reset_index())
    ar=ar[~ar["Area_accident_occured"].isin(["unknown"])].copy()
    ar["Fatal Rate (%)"]=( ar["Fatals"]/ar["Accidents"]*100).round(1)
    ar["Avg Casualties"]=ar["Avg_Casualties"].round(2)

    geo_rows=[]
    for _,row in ar.iterrows():
        info=AREA_MAP.get(row["Area_accident_occured"],{"city":"Ethiopia","note":"","lat":9.0,"lon":38.7})
        geo_rows.append({
            "Area":sh(row["Area_accident_occured"],28),
            "City":info["city"],
            "Note":info["note"],
            "lat":info["lat"],"lon":info["lon"],
            "Accidents":int(row["Accidents"]),
            "Fatal Rate (%)":row["Fatal Rate (%)"],
            "Avg Casualties":row["Avg Casualties"],
        })
    gdf=pd.DataFrame(geo_rows)

    # Apply a minimum visible size so small but high-risk areas (e.g. market areas,
    # 63 accidents but 4.8% fatal rate — highest of all) are not invisible on the map.
    # Raw accidents are used in hover; the display size uses a floored scale.
    max_acc = gdf["Accidents"].max()
    min_display_pct = 0.12          # smallest bubble = 12% of largest diameter
    gdf["Size_display"] = gdf["Accidents"].apply(
        lambda v: max(v, max_acc * min_display_pct)
    )

    fig_map=px.scatter_mapbox(
        gdf, lat="lat", lon="lon",
        size="Size_display", color="Fatal Rate (%)",
        hover_name="City",
        hover_data={"Area":True,"Note":True,"Accidents":True,
                    "Fatal Rate (%)":True,"Avg Casualties":True,
                    "lat":False,"lon":False,"Size_display":False},
        color_continuous_scale=[[0,"#aaccee"],[0.4,C_SERIOUS],[1,C_FATAL]],
        size_max=55, zoom=4.8,
        center={"lat":9.8,"lon":39.0},
        mapbox_style="carto-positron",
        labels={"Fatal Rate (%)":"Fatal Rate (%)"},
    )
    fig_map.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", font_color="#333",
        height=520, margin=dict(l=0,r=0,t=10,b=0),
        coloraxis_colorbar=dict(
            title=dict(text="Fatal %",font=dict(color="#555",size=12)),
            tickfont=dict(color="#555",size=11), thickness=14,
        ),
    )
    st.plotly_chart(fig_map, use_container_width=True)
    cap("Large bubbles = high accident volume. Red colour = high fatal rate. Market areas (Dire Dawa) are small in count but the most dangerous — 4.8% fatal rate, the highest of any area type.")

    # Area summary table below the map
    area_tbl = gdf.sort_values("Fatal Rate (%)", ascending=False)[
        ["Area","City","Accidents","Fatal Rate (%)","Avg Casualties"]
    ].reset_index(drop=True)
    st.dataframe(area_tbl, use_container_width=True, hide_index=True)


# =============================================================================
# COLLISION & ROAD — 4 chart types: stacked bar | grouped bar | donut | animated bubble
# =============================================================================
elif page=="Collision & Road":
    st.title("Collision & Road")
    st.caption("How accidents happen — collision type, road surface, who gets hurt, and cause risk evolution over time.")

    m1,m2,m3=st.columns(3)
    m1.metric("Accidents",f"{len(fdf):,}")
    m2.metric("Most common collision",sm(fdf,"Type_of_collision").title())
    m3.metric("Fatal rate",f"{fr(fdf)}%")
    st.markdown("---")
    L,R=st.columns(2)

    # Chart 1 — Collision type × severity stacked bar
    with L:
        h2("Accidents by collision type and severity")
        cs2=(fdf.groupby(["Type_of_collision","severity"]).size().reset_index(name="Count"))
        cs2["Collision"]=cs2["Type_of_collision"].apply(lambda x:sh(x,32))
        co=(cs2.groupby("Collision")["Count"].sum().sort_values().index.tolist())
        bc=px.bar(cs2,x="Count",y="Collision",color="severity",orientation="h",
                  category_orders={"severity":SEV_ORDER,"Collision":co},
                  color_discrete_map=SEV_COLORS,
                  labels={"Count":"Accidents","severity":"Severity","Collision":""})
        st.plotly_chart(fl(bc,520,t=18,b=80), use_container_width=True)
        cap("Vehicle-to-vehicle collisions dominate. Pedestrian collisions are rarer but carry a disproportionately high fatal share.")

    # Chart 2 — Road surface × severity GROUPED bar (clear comparison)
    with R:
        h2("Accidents by road surface and severity")
        rs=(fdf.groupby(["Road_surface_type","severity"]).size().reset_index(name="Count"))
        rs=rs[~rs["Road_surface_type"].isin(["unknown","other"])].copy()
        rs["Road Surface"]=rs["Road_surface_type"].apply(lambda x:sh(x,22))
        ro=(rs.groupby("Road Surface")["Count"].sum().sort_values(ascending=False).index.tolist())
        bg=px.bar(rs,x="Road Surface",y="Count",color="severity",
                  category_orders={"severity":SEV_ORDER,"Road Surface":ro},
                  color_discrete_map=SEV_COLORS,barmode="group",
                  labels={"Count":"Accidents","severity":"Severity","Road Surface":""},
                  text="Count")
        bg.update_traces(textposition="outside",textfont_size=10,
                         texttemplate="%{text:,}")
        bg.update_layout(xaxis=dict(tickangle=-20))
        st.plotly_chart(fl(bg,520,t=18,b=90), use_container_width=True)
        cap("Grouped bars make it easy to compare severity within each road type. Earth roads have a much higher fatal proportion relative to their count.")

    st.markdown("---")
    L2,R2=st.columns(2)

    # Chart 3 — Casualty class donut (NEW distinct type for this page)
    with L2:
        h2("Who is being hurt — casualty class")
        cc=(fdf[~fdf["Casualty_class"].isin(["na","unknown"])]
            ["Casualty_class"].value_counts().reset_index())
        cc.columns=["Type","Count"]
        cc["Type"]=cc["Type"].str.title()
        cd=go.Figure(go.Pie(
            labels=cc["Type"],values=cc["Count"],hole=0.50,
            marker=dict(colors=[C_SLIGHT,C_FATAL,C_SERIOUS,"#888899"],
                        line=dict(color="white",width=3)),
            textinfo="label+percent",textfont=dict(color="#333",size=13),
            hovertemplate="<b>%{label}</b><br>%{value:,} (%{percent})<extra></extra>",
            sort=False,
        ))
        cd.update_layout(showlegend=False,
                         paper_bgcolor="rgba(0,0,0,0)",
                         font=dict(color="#333"),
                         margin=dict(l=20,r=20,t=20,b=20),
                         height=480,
                         hoverlabel=dict(bgcolor="white",font=dict(color="#333")))
        st.plotly_chart(cd, use_container_width=True)
        cap("Drivers and riders make up 62% of casualties. Pedestrians at 21% are a significant and particularly vulnerable group.")

    # Chart 4 — Animation: bubble (cause risk by year) — 3 distinct variables
    with R2:
        h2("Cause risk evolution by year")
        st.caption("Animation · press ▶ · X = frequency  ·  Y = fatal rate  ·  size = total casualties  ·  Fixed axes & colors.")
        ab5=df.copy()
        if sel_sev!="All": ab5=ab5[ab5["severity"]==sel_sev]
        yrs5=sorted(ab5["Year"].dropna().astype(int).unique())
        T6=ab5["Cause_of_accident"].value_counts().head(6).index.tolist()
        D6={c:sh(c,28) for c in T6}
        C6={D6[c]:QUAL[i%len(QUAL)] for i,c in enumerate(T6)}
        bd=(ab5[ab5["Cause_of_accident"].isin(T6)]
            .groupby(["Year","Cause_of_accident"])
            .agg(Accidents=("severity","count"),
                 Total_Cas=("Number_of_casualties","sum"),
                 Fatals=("is_fatal","sum"))
            .reset_index())
        i5=pd.MultiIndex.from_product([yrs5,T6],names=["Year","Cause_of_accident"])
        bd=(bd.set_index(["Year","Cause_of_accident"]).reindex(i5,fill_value=0).reset_index())
        bd["Fatal Rate (%)"]=( bd["Fatals"]/bd["Accidents"].replace(0,1)*100).round(1)
        bd["Total Casualties"]=bd["Total_Cas"].clip(lower=1)
        bd["Cause"]=bd["Cause_of_accident"].map(D6)
        bd["Year"]=bd["Year"].astype(str)
        x5=bd["Accidents"].max()*1.15
        y5=bd["Fatal Rate (%)"].max()*1.2+0.3
        f5=px.scatter(bd,x="Accidents",y="Fatal Rate (%)",
                      size="Total Casualties",color="Cause",
                      animation_frame="Year",animation_group="Cause",
                      hover_name="Cause",
                      hover_data={"Accidents":True,"Fatal Rate (%)":True,
                                  "Total Casualties":True,"Cause":False},
                      color_discrete_map=C6,size_max=55,opacity=0.85,
                      range_x=[0,x5],range_y=[0,y5],
                      labels={"Accidents":"Accidents","Fatal Rate (%)":"Fatal Rate (%)"})
        f5.update_layout(
            legend=dict(orientation="h",y=-0.18,x=0.5,xanchor="center",
                        font=dict(size=11),
                        bgcolor="rgba(236,235,216,0.9)",
                        bordercolor="#c8c7b0",borderwidth=1))
        f5=spd(f5,900,500)
        st.plotly_chart(fl(f5,480,t=18,b=90), use_container_width=True)
        cap("Moving right = more accidents. Moving up = higher fatal rate. Growing bubble = more total casualties. Same color per cause across all years.")

    # Summary table
    st.markdown("---")
    h2("Road & collision risk summary")
    rtbl=(fdf.groupby("Road_surface_type")
          .agg(Accidents=("severity","count"),
               Fatal_Cases=("is_fatal","sum"),
               Avg_Casualties=("Number_of_casualties","mean"))
          .reset_index())
    rtbl=rtbl[~rtbl["Road_surface_type"].isin(["unknown","other"])].copy()
    rtbl["Fatal Rate (%)"]=( rtbl["Fatal_Cases"]/rtbl["Accidents"]*100).round(1)
    rtbl["Avg Casualties"]=rtbl["Avg_Casualties"].round(2)
    rtbl=rtbl.sort_values("Fatal Rate (%)",ascending=False).reset_index(drop=True)
    rtbl=rtbl.rename(columns={"Road_surface_type":"Road Surface","Fatal_Cases":"Fatal Cases"})
    st.dataframe(
        rtbl[["Road Surface","Accidents","Fatal Cases","Fatal Rate (%)","Avg Casualties"]],
        use_container_width=True, hide_index=True,
        column_config={
            "Road Surface":    st.column_config.TextColumn("Road Surface", width="medium"),
            "Accidents":       st.column_config.NumberColumn("Accidents", format="%d"),
            "Fatal Cases":     st.column_config.NumberColumn("Fatal Cases", format="%d"),
            "Fatal Rate (%)":  st.column_config.NumberColumn("Fatal Rate (%)", format="%.1f%%"),
            "Avg Casualties":  st.column_config.NumberColumn("Avg Casualties", format="%.2f"),
        },
    )
    cap("Earth roads have the highest fatal rate despite lower accident count — high-risk surfaces require targeted intervention.")


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Ethiopia Road Traffic Accidents  ·  2018–2023  ·  12,316 records  ·  Streamlit & Plotly")
