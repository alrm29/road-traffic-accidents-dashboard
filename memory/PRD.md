# Road Traffic Accidents — Ethiopia 2018–2023 ("The Road Ledger")

## Original problem statement
User shared a working Streamlit dashboard analyzing Ethiopian road traffic accidents (2018–2023, ~12,316 records across 33 variables). They asked to "make this better visualizations and animation", with follow-up choices:
1. Both better animations AND richer visualizations
2. Keep pure Streamlit (no React/FastAPI)
3. News / editorial style aesthetic
4. Remove repetitive animations — keep only meaningful ones

## Architecture
- **Single file**: `/app/streamlit_app/app.py` (~1050 lines)
- **Data**: `/app/streamlit_app/RTA_Dataset_cleaned.csv`
- **Stack**: Streamlit 1.56 + Plotly 6.7 + pandas/numpy
- **Run**: `streamlit run app.py` (port 8601 used for testing)

## Design system
- **Aesthetic**: Editorial / newsroom dark (warm near-black ink, cream text, editorial red accent)
- **Typography**: Fraunces serif (display), DM Mono (datalines/kickers), Inter (body)
- **Palette**: ink #0D0E10, cream #EDE6D3, red #D94141, amber #E8A33D, teal #4FA3A8, navy #3A5C82
- **News elements**: Masthead sidebar, kicker labels, byline rules, deck/dek intro paragraphs, pull quotes with red ruling, ticker strips, end-marks, double-rule footer

## 8 Pages
1. **Front Page** — Area chart (severity-stacked, peak annotation), proportion bar, big stats, dumbbell volume-vs-lethality
2. **Anatomy of a Crash** — **NEW: Sankey** (cause → severity), **NEW: Lollipop** (fatal rate by cause), 100%-stacked road surface
3. **The Cause Race** — **🎬 Signature animation**: manual bar-chart race (auto-sorted per frame) + **NEW: Slopegraph** of rank change
4. **Who & When** — **NEW: Sunburst** (weather → light → severity), 100%-stacked weekday, **NEW: Ridgeline plot** (violin horizontal), annotated row-% heatmap, age treemap
5. **On the Road** — **NEW: Dumbbell** (vehicle count vs fatal rate), pile-up bubble, dual-axis service age
6. **The Driver** — **NEW: Parallel Categories** (Age→Exp→Edu→Severity), **NEW: Radar** (severity shape by age, normalised), dual-axis experience, education lollipop
7. **Clock & Compass** — **NEW: Polar 24-hour clock**, hour×day heatmap, dual-axis time-period, area fatal-rate lollipop
8. **Collision Ledger** — **NEW: Collision×movement matrix** heatmap, movement fatal lollipop, surface treemap (fatal-colored), casualty donut

## Animation policy
- Old app had 4 animations (repetitive). All removed except **one signature animation**: horizontal bar-chart race on "The Cause Race" page with play/pause controls and year slider.

## What was changed vs the original
- Complete visual rewrite: editorial newsroom style replaces generic dark theme
- ~15 new chart types introduced: Sankey, sunburst, polar clock, parallel categories, radar, dumbbell, slopegraph, ridgeline, lollipop, matrix heatmap, proportion bar
- Removed 3 of 4 animations; kept only the race
- Editorial copy (kickers, decks, pull quotes, bylines) throughout

## Testing
- All 8 pages pass Streamlit AppTest with no exceptions
- Tested with "Fatal Injury" filter (only 158 records) — all pages still render without empty-data errors

## Running
```bash
cd /app/streamlit_app
streamlit run app.py
```

## Next action items / backlog
- [P2] Add CSV export button per page
- [P2] Add a printable report view (single scrolling PDF-like layout)
- [P2] Choropleth map if geographic columns are available in extended dataset
- [P2] Narrative long-read mode (linear scroll through all pages)
- [P2] Driver archetype clustering (k-means on age/exp/edu/gender)
