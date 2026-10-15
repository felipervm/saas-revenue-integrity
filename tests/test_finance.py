import sys,unittest,tempfile,json,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from build import generate,analyses,validate
class FinanceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory()
  cls.conn=generate(Path(cls.temp.name)/'test.sqlite')
  cls.out=analyses(cls.conn)
 @classmethod
 def tearDownClass(cls):
  cls.conn.close();cls.temp.cleanup()
 def test_reconciliation(self): validate(self.conn,self.out)
 def test_months(self): self.assertEqual(len(self.out['01_arr_bridge']),12)
 def test_annual_billing_is_not_arr(self): self.assertTrue(any(r['invoice_vs_arr_delta']!=0 for r in self.out['02_billing_distortion']))
 def test_annual_invoices_are_lumpy(self): self.assertTrue(self.conn.execute("SELECT COUNT(*) FROM fact_invoice WHERE amount_cad>=240").fetchone()[0]>0)
 def test_quality_checks(self): self.assertEqual(sum(r['failures'] for r in self.out['03_quality_checks']),0)
 def test_customer_product_expansion_not_new_logo(self):
  july=next(r for r in self.out['01_arr_bridge'] if r['month']=='2026-07')
  self.assertEqual(july['new_arr'],0);self.assertGreater(july['expansion_arr'],0)
 def test_cancellation_is_churn(self): self.assertGreater(sum(r['churn_arr'] for r in self.out['01_arr_bridge']),0)
 def test_monthly_nrr(self): self.assertTrue(any(r['monthly_net_revenue_retention_pct'] and r['monthly_net_revenue_retention_pct']>100 for r in self.out['04_retention']))
 def test_expansion_attribution(self):
  july=next(x for x in self.out['05_expansion_attribution'] if x['month']=='2026-07')
  aug=next(x for x in self.out['05_expansion_attribution'] if x['month']=='2026-08')
  self.assertGreater(july['cross_sell_arr'],0)
  self.assertEqual(july['existing_product_growth_arr'],0)
  self.assertGreater(aug['existing_product_growth_arr'],0)
  self.assertEqual(aug['cross_sell_arr'],0)
 def test_semantic_controls_all_pass(self):
  self.assertTrue(all(row['failures']==0 for row in self.out['06_semantic_controls']))
 def test_injected_invoice_error_is_detected(self):
  invoice=self.conn.execute("SELECT invoice_id FROM fact_invoice WHERE line_type='subscription' AND account_id=1 LIMIT 1").fetchone()[0]
  self.conn.execute('SAVEPOINT inject')
  try:
   self.conn.execute('UPDATE fact_invoice SET amount_cad=amount_cad+17 WHERE invoice_id=?',(invoice,))
   checks={r[0]:r[1] for r in self.conn.execute((Path(__file__).resolve().parents[1]/'sql'/'06_semantic_controls.sql').read_text())}
   self.assertEqual(checks['incorrect_monthly_subscription_invoice'],1)
  finally:
   self.conn.execute('ROLLBACK TO inject');self.conn.execute('RELEASE inject')
 def test_injected_subscription_error_is_detected(self):
  row=self.conn.execute("SELECT account_id,month,product_id FROM fact_subscription_month WHERE active=1 LIMIT 1").fetchone()
  self.conn.execute('SAVEPOINT inject')
  try:
   self.conn.execute('UPDATE fact_subscription_month SET mrr_cad=0 WHERE account_id=? AND month=? AND product_id=?',row)
   checks={r[0]:r[1] for r in self.conn.execute((Path(__file__).resolve().parents[1]/'sql'/'06_semantic_controls.sql').read_text())}
   self.assertEqual(checks['active_with_zero_mrr'],1)
  finally:
   self.conn.execute('ROLLBACK TO inject');self.conn.execute('RELEASE inject')
 def test_published_page_matches_sql_results(self):
  root=Path(__file__).resolve().parents[1]
  expected=json.loads((root/'data/analysis.json').read_text())
  for path in (root/'index.html',root/'site'/'index.html'):
   html=path.read_text()
   match=re.search(r'<script id="results" type="application/json">(.*?)</script>',html,re.S)
   self.assertIsNotNone(match,str(path))
   self.assertEqual(json.loads(match.group(1)),expected)
 def test_pages_are_identical(self):
  root=Path(__file__).resolve().parents[1]
  self.assertEqual((root/'index.html').read_bytes(),(root/'site'/'index.html').read_bytes())
 def test_cadences_and_month_end_are_valid(self):
  self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM fact_subscription_month WHERE billing_cadence NOT IN ('monthly','annual')").fetchone()[0],0)
  self.assertEqual(self.out['01_arr_bridge'][-1]['closing_arr'],52308)
 def test_determinism(self):
  other=generate(Path(self.temp.name)/'second.sqlite')
  try:self.assertEqual(analyses(other)['01_arr_bridge'],self.out['01_arr_bridge'])
  finally:other.close()
if __name__=='__main__':unittest.main()