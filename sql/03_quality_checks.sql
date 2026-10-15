-- Automated guardrails: grain, sign, active state, month and orphan invoice checks.
SELECT 'duplicate_subscription_grain' AS check_name,COUNT(*) AS failures FROM (
 SELECT account_id,month,product_id FROM fact_subscription_month GROUP BY 1,2,3 HAVING COUNT(*)>1)
UNION ALL SELECT 'negative_or_inactive_mrr',COUNT(*) FROM fact_subscription_month WHERE mrr_cad<0 OR (active=0 AND mrr_cad<>0)
UNION ALL SELECT 'unknown_product',COUNT(*) FROM fact_subscription_month s LEFT JOIN dim_product p ON p.product_id=s.product_id WHERE p.product_id IS NULL
UNION ALL SELECT 'orphan_invoice',COUNT(*) FROM fact_invoice f LEFT JOIN fact_subscription_month s ON s.account_id=f.account_id AND s.month=f.month AND s.product_id=f.product_id WHERE s.account_id IS NULL
UNION ALL SELECT 'invalid_month',COUNT(*) FROM fact_subscription_month WHERE month NOT BETWEEN '2026-01' AND '2026-12';