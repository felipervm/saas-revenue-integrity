-- Explain positive MRR changes at account-product grain, while treating a new logo separately.
-- Each amount is annualized CAD. A new product on an existing account is expansion.
WITH line_month AS (
 SELECT s.account_id,s.product_id,s.month,s.mrr_cad,
 COALESCE(LAG(s.mrr_cad) OVER(PARTITION BY s.account_id,s.product_id ORDER BY s.month),0) AS prior_line_mrr
 FROM fact_subscription_month s
), account_month AS (
 SELECT account_id,month,SUM(mrr_cad) AS total_mrr,
 COALESCE(LAG(SUM(mrr_cad)) OVER(PARTITION BY account_id ORDER BY month),0) AS prior_total_mrr
 FROM fact_subscription_month GROUP BY account_id,month
), detail AS (
 SELECT l.month,l.account_id,l.product_id,l.prior_line_mrr,l.mrr_cad,a.prior_total_mrr,
 CASE WHEN a.prior_total_mrr>0 AND l.prior_line_mrr=0 AND l.mrr_cad>0 THEN l.mrr_cad*12 ELSE 0 END AS cross_sell_arr,
 CASE WHEN a.prior_total_mrr>0 AND l.prior_line_mrr>0 AND l.mrr_cad>l.prior_line_mrr THEN (l.mrr_cad-l.prior_line_mrr)*12 ELSE 0 END AS existing_product_growth_arr
 FROM line_month l JOIN account_month a ON a.account_id=l.account_id AND a.month=l.month
)
SELECT month,SUM(cross_sell_arr) AS cross_sell_arr,SUM(existing_product_growth_arr) AS existing_product_growth_arr,
 SUM(cross_sell_arr+existing_product_growth_arr) AS identified_expansion_arr
FROM detail GROUP BY month ORDER BY month;