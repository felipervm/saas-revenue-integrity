# The Revenue Truth

**Beyond the ARR headline.** An independent Finance Analytics Proof of Work by Felipe Mattos, motivated by the reporting responsibilities of a Data Analyst at 1Password. Not affiliated with 1Password.

## The business decision

When a SaaS company introduces multiple products and annual billing, how should Finance distinguish **recurring economic growth** from cash invoice timing? What metric definitions and controls make an ARR bridge trustworthy?

The experiment uses **120 fictional accounts and three fictional products** over January–December 2026. All data and money amounts are **synthetic**; they are not 1Password results. The product names are invented and deliberately avoid 1Password's product naming.

## Reproduce

Requires Python 3.9+; no packages, API keys, or network access.

```bash
python src/build.py
python -m unittest discover -s tests -v
```

This creates `data/revenue_truth.sqlite` and `data/analysis.json` from seed `20261015`. The source of truth is account-month subscription MRR, not invoice amounts. Monthly recurring revenue (MRR) is annualized as `ARR = MRR × 12` for this illustrative constant-rate contract model.

## Model

- `dim_account` — account, segment, cohort.
- `dim_product` — fictional product catalog and illustrative list prices.
- `fact_subscription_month` — one row per account × product × month, active state, contractual recurring MRR, cadence.
- `fact_invoice` — invoice events including annual prepayments, monthly billing and nonrecurring credits.
- `experiment_labels` — scenario labels to inspect synthetic cases.

`sql/01_arr_bridge.sql`: **account-level** ARR bridge, classifying additional products sold to existing customers as expansion. `sql/02_billing_distortion.sql`: why `invoices × 12` is not ARR. `sql/03_quality_checks.sql`: structural integrity checks. `sql/06_semantic_controls.sql`: business-rule checks with deliberate mutation tests. `sql/04_retention.sql`: existing-customer revenue retention calculation. `sql/05_expansion_attribution.sql`: cross-sell vs existing-product growth, tied back to the account-level bridge.

## Observations on the synthetic dataset

The July 2026 bridge closes at **CAD 56,832 ARR**; annualizing invoices from July produces **CAD 46,188**, a **CAD −10,644** difference. This is a *constructed dataset*, not a measured finding about any company. The bridge equation is validated for each of 12 months: opening + new + expansion − contraction − churn = closing.

These observations support a workflow recommendation: build ARR on consistent account-level recurring-contract snapshots, preserve the invoice ledger for billing reconciliation, and flag unexplained deviations rather than treating the same metric names as interchangeable. All output values are reproducible in `data/analysis.json`.

## Limitations

- No access to real 1Password financial, customer, invoice or pricing systems.
- Amounts, dates and customer patterns are deliberately fabricated and are not a forecast.
- Simplified fixed-rate subscription contracts, no FX, refunds beyond simplified credits, tax, ASC 606/IFRS 15 revenue recognition, or true production data complexity.
- Monthly NRR is **not** trailing-12-month NRR.
- Some controls catch structural invalid data only; they cannot prove semantic correctness.
- No performance benchmark or claimed time savings.

## Files

- `src/build.py`: deterministic synthetic dataset generator and validation runner.
- `sql/`: reusable SQL with CTEs and window functions.
- `tests/test_finance.py`: deterministic and financial-invariant tests.
- `data/analysis.json`: published computed results.
- `data/revenue_truth.sqlite`: local analytical database.
- `docs/decision_brief.md`: executive interpretation.
- `site/index.html`: small visual report to accompany the reproducible analysis.

## Business interpretation

The project demonstrates advanced SQL, simple dimensional modeling, recurring-revenue definitions, reconciliations, data quality, and communication to Finance / RevOps. It proposes a way to reason about metrics; it does not claim the hiring company has a defect.

## Further analysis — v2

The July **CAD 11,748** expansion is entirely cross-sell to existing accounts. The August **CAD 2,376** expansion is entirely growth on existing product subscriptions. Both drivers reconcile exactly to the account-level ARR bridge; in this deliberately simple dataset they occur in separate months. This illustrates why an ARR headline alone is insufficient to prescribe a commercial response.

Six semantic control definitions additionally check active-but-zero recurring value, missing accounts, billing cadence, pre-cohort charges, invoice/contract mismatches on monthly subscription billing, and unexpected invoice types. The tests deliberately inject two errors and confirm the relevant controls flag them. Passing tests do not prove coverage of production data.

**Note on recognition:** this project analyzes *contract ARR*, not cash flow or GAAP/IFRS recognized revenue. Invoices are a separate ledger; annualization of one month's invoices is deliberately shown only as an invalid shortcut.

Website: [The Revenue Truth](https://felipervm.github.io/saas-revenue-integrity/). GitHub Pages should publish from `main` / repository root.