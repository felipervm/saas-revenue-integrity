-- Account-level bridge; adding a product to an existing customer counts as expansion, not new-logo ARR.
-- No price changes from billing cadence: recurring contract value is the source of ARR.
WITH totals AS (
 SELECT account_id,month,SUM(mrr_cad) AS mrr_cad FROM fact_subscription_month GROUP BY account_id,month
), monthly AS (
 SELECT account_id,month,mrr_cad,
 COALESCE(LAG(mrr_cad) OVER(PARTITION BY account_id ORDER BY month),0) AS prior_mrr
 FROM totals
), movements AS (
 SELECT month,account_id,mrr_cad,prior_mrr,
 CASE WHEN prior_mrr=0 AND mrr_cad>0 THEN mrr_cad*12 ELSE 0 END AS new_arr,
 CASE WHEN prior_mrr>0 AND mrr_cad>prior_mrr THEN (mrr_cad-prior_mrr)*12 ELSE 0 END AS expansion_arr,
 CASE WHEN mrr_cad>0 AND prior_mrr>mrr_cad THEN (prior_mrr-mrr_cad)*12 ELSE 0 END AS contraction_arr,
 CASE WHEN prior_mrr>0 AND mrr_cad=0 THEN prior_mrr*12 ELSE 0 END AS churn_arr
 FROM monthly
)
SELECT month, SUM(prior_mrr)*12 AS opening_arr,SUM(new_arr) AS new_arr,
SUM(expansion_arr) AS expansion_arr,SUM(contraction_arr) AS contraction_arr,
SUM(churn_arr) AS churn_arr,SUM(mrr_cad)*12 AS closing_arr
FROM movements GROUP BY month ORDER BY month;