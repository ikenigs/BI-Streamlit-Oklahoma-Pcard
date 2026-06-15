# Oklahoma State PCard Spending Analysis

**Course:** ALY 6110 – Data Management & Big Data | Northeastern University  
**Author:** Ivan Kenigsberg  
**Period covered:** July 2023 – June 2024

---

## Live Dashboard

> **[Launch Dashboard on Streamlit](_PLACEHOLDER_)**  
> *(link will be updated after deployment)*

---

## Business Overview

State purchasing cards (PCards) allow government employees to bypass the traditional purchase-order process for routine, low-value acquisitions. While this speeds up procurement, it also creates oversight challenges: without consistent monitoring, PCard programs can be vulnerable to policy violations, budget overruns, and misuse.

This project analyzes **420,243 PCard transactions** across **117 Oklahoma state agencies**, covering $184.6 million in purchases. The goal is to answer a single business question:

> **Which state agencies and merchant categories drive the highest PCard spending, and how does that spending vary month-over-month across the fiscal year?**

The findings are designed to support procurement managers and auditors in prioritizing oversight resources where they will have the greatest fiscal impact.

---

## Key Business Findings

### 1 — Spending is Highly Concentrated
A small number of agencies account for a disproportionate share of total expenditure. The **top 5 agencies represent over half of all PCard dollars**, making them the highest-priority targets for audit and budget review. This concentration means that a focused compliance effort covering fewer than 10 agencies would address the majority of financial risk across the entire state.

### 2 — Fiscal Year-End Surge
Monthly spend rises steadily through spring and **peaks in April–May**, immediately before Oklahoma's June 30 fiscal year-end. This pattern — commonly known as "use-it-or-lose-it" spending — is associated with lower purchasing efficiency and elevated procurement risk, as agencies rush to exhaust remaining budget authority rather than planning purchases in advance.

### 3 — IT and Industrial Categories Dominate
Industrial suppliers and IT/technology services absorb the largest share of PCard dollars by merchant category. The **top 5 merchant category codes account for over 35% of total spend**. Key vendors include Grainger ($6.3M), AT&T ($2.9M), and Dell Government ($1.1M). Understanding category concentration helps procurement teams negotiate volume contracts and set appropriate spending limits.

---

## Dataset

| Field | Detail |
|---|---|
| **Source** | Oklahoma Office of Management and Enterprise Services (OMES) — open government data |
| **Period** | July 2023 – June 2024 (12 monthly files) |
| **Rows** | 420,243 transactions |
| **Columns** | 13 |
| **Total spend analyzed** | $184,627,876 |
| **Agencies covered** | 117 |
| **Merchant categories (MCC)** | 420 |

---

## Dashboard Features

The interactive dashboard was built with **Streamlit** and **Plotly**. All visuals respond to sidebar filters (month and agency).

| Visual | Type | Business Purpose |
|---|---|---|
| Headline metrics | KPI cards | Instant summary of spend, transaction count, and average ticket size |
| Monthly Spend Trend | Line chart | Tracks the fiscal year-end acceleration pattern |
| Top N Agencies by Spend | Bar chart | Identifies which departments drive the budget |
| Spend by Merchant Category | Donut chart | Shows which purchasing categories dominate |
| Agency × Month Heatmap | Heatmap | Combines agency ranking and seasonality in one view |
| Transactions vs. Spend | Scatter plot | Flags agencies making few but very large purchases |

---

## Repository Structure

```
├── dashboard.py          # Streamlit application
├── EDA.ipynb             # Full exploratory data analysis notebook
├── pcard_clean.parquet   # Cleaned dataset (used by the dashboard)
├── requirements.txt      # Python dependencies for Streamlit Cloud
└── README.md
```

---

## Running Locally

```bash
pip install -r requirements.txt
python -m streamlit run dashboard.py
```

---

## References

- Oklahoma OMES PCard Public Data — [data.ok.gov](https://data.ok.gov)
- Streamlit Documentation — [docs.streamlit.io](https://docs.streamlit.io)
- Plotly Python Library — [plotly.com/python](https://plotly.com/python)
