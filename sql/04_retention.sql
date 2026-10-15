-- NRR on existing account cohorts, excluding new accounts' initial MRR.
WITH account_month AS (
 SELECT account_id,month,SUM(mrr_cad) AS mrr FROM fact_subscription_month GROUP BY account_id,month
), prior AS (
 SELECT account_id,month,mrr,LAG(mrr) OVER(PARTITION BY account_id ORDER BY month) AS prior_mrr FROM account_month
)
SELECT month, SUM(CASE WHEN prior_mrr>0 THEN prior_mrr ELSE 0 END)*12 AS retained_cohort_opening_arr,
SUM(CASE WHEN prior_mrr>0 THEN mrr ELSE 0 END)*12 AS retained_cohort_closing_arr,
ROUND(100.0*SUM(CASE WHEN prior_mrr>0 THEN mrr ELSE 0 END)/NULLIF(SUM(CASE WHEN prior_mrr>0 THEN prior_mrr ELSE 0 END),0),2) AS monthly_net_revenue_retention_pct
FROM prior GROUP BY month ORDER BY month;