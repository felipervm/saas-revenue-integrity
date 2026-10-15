-- Data contracts catch defects that an ARR bridge identity alone cannot detect.
SELECT 'active_with_zero_mrr' AS check_name,COUNT(*) AS failures FROM fact_subscription_month WHERE active=1 AND mrr_cad=0
UNION ALL SELECT 'unknown_account',COUNT(*) FROM fact_subscription_month s LEFT JOIN dim_account a ON a.account_id=s.account_id WHERE a.account_id IS NULL
UNION ALL SELECT 'invalid_cadence',COUNT(*) FROM fact_subscription_month WHERE billing_cadence NOT IN ('monthly','annual')
UNION ALL SELECT 'pre_cohort_recurring_value',COUNT(*) FROM fact_subscription_month s JOIN dim_account a ON a.account_id=s.account_id WHERE s.month<a.cohort_month AND s.mrr_cad<>0
UNION ALL SELECT 'incorrect_monthly_subscription_invoice',COUNT(*) FROM fact_invoice i JOIN fact_subscription_month s ON s.account_id=i.account_id AND s.month=i.month AND s.product_id=i.product_id WHERE s.billing_cadence='monthly' AND i.line_type='subscription' AND i.amount_cad<>s.mrr_cad
UNION ALL SELECT 'unexpected_invoice_type',COUNT(*) FROM fact_invoice WHERE line_type NOT IN ('subscription','one_time_credit');