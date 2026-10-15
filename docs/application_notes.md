# Using The Revenue Truth in a Finance Analytics application

This is an independent portfolio project for the Data Analyst, Finance Analytics role at 1Password. It uses 120 fictional accounts and three fictional products, not company data. The role mapping below follows the job description supplied for this application; it does not imply that every listed tool or production responsibility has been demonstrated.

## Evidence to lead with

| Role responsibility | Evidence in this repository | What to explain in conversation |
| --- | --- | --- |
| SQL, including joins, CTEs and window functions | [ARR bridge](../sql/01_arr_bridge.sql), [retention](../sql/04_retention.sql), [expansion attribution](../sql/05_expansion_attribution.sql) | Why product-month snapshots are aggregated to account-month before classifying new, expansion and churn movements. |
| Reliable fact and dimension models | [Schema and deterministic generator](../src/build.py): account/product dimensions, monthly subscription facts and invoice facts | State each table's grain; explain why joining invoice events directly to subscription snapshots can duplicate amounts. This is a small dimensional model, not a production warehouse. |
| Self-serve financial reporting | [Interactive case study](../site/index.html) with reporting-month exploration and linked evidence | Start with a stakeholder question, show how the view answers it, and describe what feedback would change the next iteration. The implementation is HTML/CSS/JavaScript, not Hex. |
| ARR, retention and subscription analysis | [ARR bridge](../sql/01_arr_bridge.sql), [billing comparison](../sql/02_billing_distortion.sql), [monthly retention](../sql/04_retention.sql) | Contract ARR differs from annualized invoices; monthly NRR is not trailing-12-month NRR. Account cohorts exist in the model, but a full cohort analysis is not included. |
| Month-close variance investigation | [Decision brief](decision_brief.md) and [published results](../data/analysis.json) | July's CAD 10,644 difference is a constructed metric-definition example, not lost revenue. July cross-sell and August existing-product growth suggest different follow-up questions. |
| Quality controls and metric definitions | [Structural checks](../sql/03_quality_checks.sql), [semantic controls](../sql/06_semantic_controls.sql), [tests](../tests/test_finance.py) | Explain what each control can detect. Two tests deliberately inject errors; passing the clean fixture does not prove coverage of real financial data. |
| AI-assisted reporting with accountability | Proposed workflow below | Distinguish a responsible design from a feature that has actually been implemented. No runtime AI service or automated narrative pipeline is connected. |

## Three-sentence application snippet

I created The Revenue Truth, an independent finance analytics case study using 120 fictional SaaS accounts to explore ARR, billing timing and expansion drivers. The repository includes a dimensional SQLite model, SQL with CTEs and window functions, a reconciled ARR bridge, and tests that deliberately inject invoice and subscription errors. I would welcome the opportunity to walk through the metric definitions, the business decisions they support, and how I would extend the work with Finance and Analytics Engineering at 1Password.

Use the case-study URL alongside the resume in the official application. The snippet describes this project; it does not replace accurate work history or establish eligibility for the role. No application or outreach has been sent as part of this work.

## Proposed AI workflow — design only

1. **Calculate before summarizing.** Run the deterministic SQL and reconciliation checks first. Keep metric definitions and the account-level bridge authoritative; an AI system does not calculate or overwrite the financial result.
2. **Use an approved input boundary.** In a future authorized environment, supply only approved aggregate fields, reporting periods, metric definitions and evidence references. Exclude raw customer identifiers, credentials and invoice details unless an approved policy explicitly permits their use. Confirm model/vendor retention and access policies before connecting real data.
3. **Constrain the draft.** Ask for an observation, supporting figures, open questions and proposed checks. Require a source reference for every factual claim and label explanations as hypotheses unless supported by evidence. Never infer a cause from a variance alone.
4. **Validate the output.** Check numeric claims against the input values and enforce required period/currency labels. If a claim lacks evidence or a check fails, withhold the draft and send it for analyst review; do not silently publish it.
5. **Keep a human accountable.** A Finance analyst reviews interpretation, signs off and records changes before any stakeholder distribution. Preserve input/version references and the reviewed output under approved access and retention controls.

Only the deterministic analysis, local tests and interactive presentation are implemented here. This proposed AI workflow has no measured productivity benefit, connected model, confidentiality certification or production deployment.

## Interview walkthrough

- **Business question:** How should Finance separate recurring economic growth from invoice timing when billing and product packaging evolve?
- **Definition:** Show the account-month grain and the bridge equation. Explain why an additional product for an existing customer counts as expansion.
- **Evidence:** Reproduce July, inspect the July/August expansion attribution, then demonstrate one injected-error test.
- **Decision:** Use recurring contract snapshots for ARR, reconcile the invoice ledger separately, and investigate the growth driver before recommending action.
- **Next questions:** Ask Finance about metric ownership, effective dates, contract amendments, FX, refunds and recognition policies. Ask Analytics Engineering about source freshness, lineage and deployment controls. Describe these as discovery questions rather than assumptions about 1Password's systems.
- **Collaboration:** Invite a stakeholder to challenge one definition and explain how the model, test and dashboard would be updated together. This project does not demonstrate an actual stakeholder engagement at the company.

## Tooling and scope limits

- SQLite and Python standard library are used; no live Salesforce, Stripe, NetSuite or other enterprise source is connected.
- There is no Hex workbook, dbt project, production scheduler, warehouse deployment or production-scale performance benchmark.
- The model analyzes simplified fixed-rate contract ARR, not recognized revenue under ASC 606 or IFRS 15. It does not cover real contract complexity, FX or comprehensive refunds.
- Dates, prices, customer patterns and amounts are synthetic. No conclusion describes 1Password's actual financial performance or systems.
- The project supports a conversation about analytical reasoning. It does not claim prior commercial impact, savings, hiring success or mastery of tools that are not present.
