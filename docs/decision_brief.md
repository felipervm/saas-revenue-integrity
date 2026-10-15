# The Revenue Truth — Finance decision brief

**Question:** When product packaging and billing cadence evolve, how do we keep recurring-revenue metrics interpretable and trusted?

**Design:** Deterministic, entirely synthetic 120-account / three-fictional-product subscription experiment. Snapshot grain is account × product × month, analyzed to an account-level ARR bridge. Annual invoices and nonrecurring credits are kept separate from recurring-contract value.

## Finding 01 — Annualized invoices are not ARR

In July 2026 (synthetic), **contractual ARR = CAD 56,832** but `12 × July invoices = CAD 46,188` (**CAD 10,644 lower**). In other months the naive metric can overstate ARR when a prepaid annual bill lands. Neither difference alone signals revenue loss or data errors. They reflect payment cadence and revenue metric definitions.

## Finding 02 — New product is not necessarily a new customer

July includes accounts adopting a third fictional product. At account grain, these are **existing-customer expansions**, even though the account-product combination is new. Classifying new product rows as new customers would distort acquisition and expansion narratives.

## Finding 03 — Definitions should be testable

A twelve-month bridge checks: **opening ARR + new + expansion − contraction − churn = closing ARR**. Five structural integrity checks return zero failures on the generated clean input. These are test results on synthetic data, not claims about a production data platform.

## Decision / recommended operating approach

1. Make account-level recurring contract snapshots the source of truth for ARR and retention.
2. Keep invoices as a separate lens for billing/cash process investigation rather than ARR computation.
3. Assign one owner to metric definitions and run reconciliation/integrity checks with every reporting refresh.
4. Route material unexplained differences to a human analyst; never let an AI-generated narrative invent a root cause.

## What this does *not* establish

No real 1Password data, no production financial accounting compliance analysis, no estimated revenue impact, and no observed reduction in manual effort or errors. Revenue recognition and contract modifications in real SaaS platforms require additional policies and controls.


## Second finding — explain expansion before recommending action

The SQL attribution exercise splits account-level expansion into **cross-sell** (first subscription to an additional product within a pre-existing account) and **existing-product growth** (increased MRR on a product already held). The synthetic July expansion is CAD 11,748 cross-sell; August expansion is CAD 2,376 existing-product growth. Both reconcile to the ARR bridge. This is a designed example, not evidence of 1Password's financial performance.

**Decision:** Finance should reconcile the movement first, then route it to the appropriate cross-functional question. Product adoption and seat/contract value expansion require different investigation and potentially different stakeholder involvement. Monthly invoices should never be a substitute for contract ARR, and dates/discounts must be read as contract terms rather than inferred from cash collected.

**Control testing:** added explicit semantic rules and fault-injection tests. The injected monthly invoice discrepancy and active-zero-MRR subscription are caught; other real-world inconsistencies remain outside this small illustrative test suite.