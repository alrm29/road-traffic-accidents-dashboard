# Road Traffic Accidents — Ethiopia 2018–2023 ("The Road Ledger")

## Latest update (v3 — student edition)
User requested:
1. Add ONE meaningful 3D animation
2. Add a data table related to the dataset
3. Make it university-student level (clearer explanations)
4. Limit each page to 3 charts

All four requests implemented.

## Architecture
- Single file: `/app/streamlit_app/app.py`
- Data: `/app/streamlit_app/RTA_Dataset_cleaned.csv`
- Stack: Streamlit 1.56 + Plotly 6.7 + pandas/numpy
- Run: `cd /app/streamlit_app && streamlit run app.py`

## 8 Pages — each has EXACTLY 3 charts
1. **Front Page** — (1) severity-stacked area over years · (2) dumbbell volume-vs-lethality · (3) **interactive data table** with filters + CSV download
2. **Anatomy of a Crash** — (1) Sankey cause→severity · (2) Lollipop fatal rate · (3) 100%-stacked road surface
3. **The Cause Race** — (1) Bar-chart race (2D signature animation) · (2) Slopegraph · (3) **3D risk-space scatter with orbital camera animation** (X=count, Y=avg casualties, Z=fatal rate, bubble=total casualties)
4. **Who & When** — (1) Sunburst weather→light→severity · (2) 100%-stacked weekday · (3) Ridgeline casualties distribution
5. **On the Road** — (1) Dumbbell vehicle types · (2) Pile-up bubble · (3) Service-age dual-axis
6. **The Driver** — (1) Parallel categories age→exp→edu→severity · (2) Radar severity shape by age · (3) Experience dual-axis
7. **Clock & Compass** — (1) Polar 24-hour clock · (2) Hour×day heatmap · (3) Area fatal-rate lollipop
8. **Collision Ledger** — (1) Collision×movement matrix · (2) Movement fatal lollipop · (3) Fatal-colored surface treemap

## Animation policy
- ONE 2D signature: horizontal bar-chart race on page 3 (sorted per frame)
- ONE 3D signature: orbiting 3D scatter on page 3 (36-frame camera animation around the risk cube)
- All repetitive animations from original removed

## Student-level features added
- Every chart now has a "HOW TO READ THIS" + "KEY TAKEAWAY" callout box below it, explaining axes in plain language
- Charts are numbered (CHART 1, CHART 2, CHART 3) so a reader can follow
- Glossary-style prose replaces jargon (e.g., "fatal rate = % of crashes that were fatal")
- Interactive data table on Front Page with three filters (Severity, Cause, Time window), sortable columns, and one-click CSV export for students running their own analysis

## Testing
- All 8 pages pass Streamlit `AppTest` — no exceptions
- Verified with narrow filter (Fatal Injury = 158 rows) — no empty-data crashes

## Next action items / backlog
- [P2] Printable single-page report
- [P2] Driver archetype clustering
- [P2] Choropleth map (needs geo columns)
- [P2] Narrative long-read mode
