-- Annual prepaid invoices and credits make cash-billing totals unsuitable as ARR.
WITH arr AS (SELECT month,SUM(mrr_cad)*12 AS contract_arr FROM fact_subscription_month GROUP BY month),
bill AS (SELECT month,SUM(amount_cad) AS invoiced_cad FROM fact_invoice GROUP BY month)
SELECT a.month,a.contract_arr,COALESCE(b.invoiced_cad,0) AS invoices_cad,
COALESCE(b.invoiced_cad,0)*12 AS naive_annualized_invoices,
COALESCE(b.invoiced_cad,0)*12-a.contract_arr AS invoice_vs_arr_delta
FROM arr a LEFT JOIN bill b USING(month) ORDER BY a.month;