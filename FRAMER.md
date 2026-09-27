# Framer Portfolio — Final Copy

Paste-ready English copy for the portfolio landing page. Layout notes and publishing checklist at the bottom.

**Links to fill before publishing:**

| Link | Placeholder | Where |
|---|---|---|
| GitHub | `https://github.com/hazewazeraze/laundry-operations-analytics` | Hero button, Footer |
| Dashboard | `https://laundry-operations-analytics.streamlit.app` | Hero button, Dashboard section, Footer |
| Framer | `<FRAMER_URL>` | CV |

> Never publish `localhost:8501` — deploy the dashboard to Streamlit Cloud first.

---

## 1. Hero

**H1:** Laundry Operations Analytics

**Subtitle:** Analyzing customer value and operational reliability through transaction data.

**Body:** A data analytics project exploring customer behavior, revenue concentration, service reliability, and operational performance through transaction-level analysis — from raw export to statistically validated findings.

**Built with:** Python · Pandas · NumPy · Streamlit · Statistical Testing

**Buttons:** `View Dashboard` → `https://laundry-operations-analytics.streamlit.app` · `View GitHub` → `https://github.com/hazewazeraze/laundry-operations-analytics`

**Stat strip (big numbers, one row):**

| 467 | 155 | 66.2% | 38% | 8 |
|---|---|---|---|---|
| validated transactions | identified customers | revenue coverage | on-time delivery | hypothesis tests |

---

## 2. Project Overview

**H2:** From transaction records to business decisions

**Body:** This project looks at two months of laundry transaction data to understand customer value, revenue concentration, and how reliable the delivery promises are. It runs from data cleaning and exploratory analysis to segmentation and statistical testing, and it puts the data limitations on the table instead of hiding them.

---

## 3. Business Challenges (3 cards)

**H2:** Business challenges

**Card 1 — Customer understanding**
Which customer groups contribute the most observed revenue, and is their value measured by frequency or by spend per order?

**Card 2 — Operational reliability**
Do promised completion times match actual delivery — and where does the SLA break down?

**Card 3 — Data reliability**
How does incomplete revenue recording (66.2% coverage) change what the analysis can honestly claim?

---

## 4. Analytical Workflow (timeline)

**H2:** Analytical workflow

```
Data preparation
      ↓
Exploratory analysis
      ↓
Customer analysis
      ↓
Operational analysis
      ↓
Hypothesis testing
      ↓
Interactive dashboard
```

One-liners under each step (optional, small text):

1. **Data preparation** — cleaning, validation, feature engineering, quality flags
2. **Exploratory analysis** — revenue, demand patterns, data coverage
3. **Customer analysis** — segmentation, concentration, Pareto, robustness
4. **Operational analysis** — turnaround, SLA by promise, backlog
5. **Hypothesis testing** — 8 permutation/bootstrap tests: supported, rejected, inconclusive
6. **Interactive dashboard** — five views, same story as the documentation

---

## 5. Key Findings (4 blocks, big-number style)

**H2:** Key findings

### 01 — Revenue concentration

**Big number:** 57.7%

**Headline:** of observed revenue comes from the top 20% of customers.

**Sub:** Repeat customers account for 89.6% of observed revenue (bootstrap 95% CI 52.2–63.5%). Retention of high-value customers outranks acquisition.

---

### 02 — Customer value is not only frequency

**Big number:** 0.84 → 0.13
*(label: correlation of order frequency with total revenue → with average order value)*

**Headline:** Customers who order more spend more in total — not more per order.

**Sub:** Frequency correlates strongly with total revenue (ρ = 0.84), but not with average order value (ρ = 0.13, not significant). The 8 High-Value Occasional customers average 2.7× the revenue per order of Regular customers.

---

### 03 — Operational reliability opportunity

**Big number:** 38%

**Headline:** of orders completed on time.

**Sub:** The standard 3-day promise is the weak point — 26.6% on-time across 64% of measurable orders, while the 1-day promise holds at 79.5% among its measurable orders. Daily intake volume does not explain the lateness.

---

### 04 — Data quality matters

**Big number:** 66.2%

**Headline:** of transactions record revenue — and every conclusion says so.

**Sub:** Estimated unrecorded value is about Rp 3.1M (~30% of observed), modeled from observed patterns. All financial figures are labeled observed revenue; segment shares are re-checked on the high-coverage subset.

---

## 6. Dashboard Section

**H2:** Interactive dashboard

**Body:** Explore customer behavior, revenue patterns, operational performance, and analytical validation through five connected views — Overview, Revenue & services, Customers, Operations, and Data quality.

**Button:** `Open dashboard` → `https://laundry-operations-analytics.streamlit.app`

> Embed (Framer iframe) only after Streamlit Cloud deploy; if the iframe is blocked or slow, keep the button. Never embed localhost.

---

## 7. Tools & Methods (3 cards)

**H2:** Tools & methods

**Programming:** Python · Pandas · NumPy

**Analytics:** EDA · Customer profiling & segmentation · SLA analysis · Permutation & bootstrap testing

**Visualization:** Streamlit · Altair · Matplotlib

---

## 8. Analytical Limitations

**H2:** Analytical limitations

- Revenue insights cover only transactions where revenue was recorded (66.2% coverage; ~30% estimated unrecorded).
- Two-month window (April–May 2026) — no seasonality or lifetime-value conclusions.
- Date-level data only — SLA is measured in days, not hours.
- Segment shares are directional: Premium shifts from 55.9% to 39.6% on the ≥80%-coverage subset.

---

## 9. Footer

```
Built as a Data Analytics Portfolio Project
2026
```

Links: GitHub · Dashboard · README

---

## Visual Direction

- **Background:** off-white (`#FAFAF9`) / white; near-black text
- **Accent:** muted blue `#4C9BE8` (matches the dashboard charts) + soft red `#D95F4F` for contrast only
- **Type:** Inter or similar clean sans; big numbers 64–96px; body 16–18px
- **Layout:** generous whitespace, minimal cards with hairline borders, no heavy animation
- **Vibe:** Linear / Notion / Stripe docs — an analyst's page, not a SaaS launch page

## Layout Wireframe (top → bottom)

```
[ Hero: title · subtitle · body · tech line · View Dashboard / View GitHub ]
[ Stat strip: 467 · 155 · 66.2% · 38% · 8 ]
[ Overview: heading + paragraph, 2-column or centered ]
[ Business challenges: 3 cards ]
[ Analytical workflow: horizontal timeline, 6 steps ]
[ Key findings: 4 stacked blocks, big number + headline + sub, alternating alignment ]
[ Interactive dashboard: short text + Open dashboard button (or iframe) ]
[ Tools & methods: 3 cards ]
[ Analytical limitations: bullet list ]
[ Footer: Built as a Data Analytics Portfolio Project · 2026 · links ]
```

## Publishing Checklist

1. **GitHub repo** — push `README.md`, `requirements.txt`, `notebooks/`, `dashboard/`, `data/`, `outputs/` (add `.gitignore` for `__pycache__/`, `.streamlit/secrets.toml`)
2. **Streamlit Cloud** — new app from the repo, entry file `dashboard/streamlit_app.py` (runtime installs from `requirements.txt`)
3. **Smoke-test the live URL** — open all 5 pages, then use it for the Framer buttons and embed
4. **Framer** — build layout from the wireframe above, paste copy, set accent color
5. **Optional embed** — Framer iframe to the Streamlit URL; fallback is the button
6. **Final flow:** CV → Framer → GitHub + Dashboard → proof of skill
