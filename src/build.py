"""Deterministic, entirely synthetic SaaS finance analytics experiment (stdlib only)."""
from __future__ import annotations
import json, random, sqlite3, re
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'data' / 'revenue_truth.sqlite'
SEED = 20261015
MONTHS = [f'2026-{m:02d}' for m in range(1, 13)]
PRODUCTS = [('Vault', 20), ('Access', 35), ('SecureOps', 55)]  # deliberately fictional offerings

def generate(path=DB):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists(): path.unlink()
    rng = random.Random(SEED)
    conn = sqlite3.connect(str(path))
    conn.executescript('''
    CREATE TABLE dim_account(account_id INTEGER PRIMARY KEY, segment TEXT NOT NULL, cohort_month TEXT NOT NULL);
    CREATE TABLE dim_product(product_id INTEGER PRIMARY KEY, product_name TEXT NOT NULL, monthly_list_price_cad INTEGER NOT NULL);
    CREATE TABLE fact_subscription_month(account_id INTEGER NOT NULL, month TEXT NOT NULL, product_id INTEGER NOT NULL,
        active INTEGER NOT NULL CHECK(active IN (0,1)), mrr_cad INTEGER NOT NULL CHECK(mrr_cad>=0),
        billing_cadence TEXT NOT NULL, PRIMARY KEY(account_id, month, product_id));
    CREATE TABLE fact_invoice(invoice_id TEXT PRIMARY KEY, account_id INTEGER NOT NULL, month TEXT NOT NULL,
        product_id INTEGER NOT NULL, line_type TEXT NOT NULL, amount_cad INTEGER NOT NULL);
    CREATE TABLE experiment_labels(account_id INTEGER NOT NULL, month TEXT NOT NULL, product_id INTEGER NOT NULL,
        scenario TEXT NOT NULL, PRIMARY KEY(account_id,month,product_id));
    ''')
    conn.executemany('INSERT INTO dim_product VALUES (?,?,?)',[(i+1,name,price) for i,(name,price) in enumerate(PRODUCTS)])
    accounts = [(i,'SMB' if i%3 else 'Mid-market', MONTHS[(i*7)%5]) for i in range(1,121)]
    conn.executemany('INSERT INTO dim_account VALUES (?,?,?)', accounts)
    snapshots=[]; invoices=[]; labels=[]; invoice_ix=0
    for account_id, segment, cohort in accounts:
        cohort_idx=MONTHS.index(cohort)
        cadence='annual' if account_id%5==0 else 'monthly'
        products=[1]
        if account_id%4==0: products.append(2)
        cancellation=(9 if account_id%13==0 else 11 if account_id%17==0 else None)
        for mi,month in enumerate(MONTHS):
            if mi==6 and account_id%7==0: products.append(3)
            for product_id in sorted(set(products)):
                active=int(mi>=cohort_idx and (cancellation is None or mi<cancellation))
                base=PRODUCTS[product_id-1][1]
                seat_mult=2 if account_id%9==0 else 1
                # Price changes are economic expansion; billing-frequency changes are not.
                upgrade=(mi>=7 and product_id==1 and account_id%6==0)
                mrr=(base*seat_mult + (10 if upgrade else 0))*active
                if account_id%11==0 and active: mrr=int(mrr*0.8) # contracted commercial discount
                snapshots.append((account_id,month,product_id,active,mrr,cadence))
                if not active: continue
                scenario='new' if mi==cohort_idx else 'expansion' if upgrade and mi==7 else 'product_addition' if product_id==3 and mi==6 else 'ordinary'
                labels.append((account_id,month,product_id,scenario))
                # Invoice ledger intentionally differs from recognized recurring economics.
                if cadence=='monthly':
                    invoice_ix+=1; invoices.append((f'INV-{invoice_ix:06}',account_id,month,product_id,'subscription',mrr))
                elif (mi-cohort_idx)%12==0:
                    invoice_ix+=1; invoices.append((f'INV-{invoice_ix:06}',account_id,month,product_id,'subscription',mrr*12))
                if mi==8 and account_id%10==0 and product_id==1:
                    invoice_ix+=1; invoices.append((f'INV-{invoice_ix:06}',account_id,month,product_id,'one_time_credit',-15))
    conn.executemany('INSERT INTO fact_subscription_month VALUES (?,?,?,?,?,?)',snapshots)
    conn.executemany('INSERT INTO fact_invoice VALUES (?,?,?,?,?,?)',invoices)
    conn.executemany('INSERT INTO experiment_labels VALUES (?,?,?,?)',labels)
    conn.commit()
    return conn

def analyses(conn):
    sql_root=ROOT/'sql'
    outputs={}
    for filename in ['01_arr_bridge.sql','02_billing_distortion.sql','03_quality_checks.sql','04_retention.sql','05_expansion_attribution.sql','06_semantic_controls.sql']:
        rows=conn.execute((sql_root/filename).read_text()).fetchall()
        fields=[d[0] for d in conn.execute((sql_root/filename).read_text()).description]
        outputs[filename.replace('.sql','')]=[dict(zip(fields,row)) for row in rows]
    return outputs

def validate(conn,results):
    assert conn.execute('SELECT COUNT(*) FROM dim_account').fetchone()[0]==120
    bridge=results['01_arr_bridge']
    assert len(bridge)==12
    for row in bridge:
        assert row['opening_arr']+row['new_arr']+row['expansion_arr']-row['contraction_arr']-row['churn_arr']==row['closing_arr'],row
    assert all(r['failures']==0 for r in results['03_quality_checks'])
    assert all(r['failures']==0 for r in results['06_semantic_controls'])
    assert all(r['identified_expansion_arr']==b['expansion_arr'] for r,b in zip(results['05_expansion_attribution'], bridge))
    assert any(r['invoice_vs_arr_delta']!=0 for r in results['02_billing_distortion'])

def main():
    conn=generate()
    results=analyses(conn)
    validate(conn,results)
    payload={'metadata':{'dataset':'Synthetic fictional SaaS accounts and products — NOT 1Password internal data', 'seed':SEED,'accounts':120,'period':'Jan–Dec 2026','currency':'CAD','pricing':'illustrative only'},'results':results}
    (ROOT/'data'/'analysis.json').write_text(json.dumps(payload,indent=2)+'\n')
    # Keep both static pages in lockstep with the SQL results on every rebuild.
    inline_json = json.dumps(payload, ensure_ascii=True, separators=(',', ':')).replace('<', '\u003c')
    pattern = r'(<script id="results" type="application/json">).*?(</script>)'
    for page in (ROOT / 'index.html', ROOT / 'site' / 'index.html'):
        html = page.read_text(encoding='utf-8')
        updated, count = re.subn(pattern, lambda match: match.group(1) + inline_json + match.group(2), html, count=1, flags=re.S)
        if count != 1:
            raise RuntimeError(f'Missing unique results script in {page}')
        page.write_text(updated, encoding='utf-8')
    conn.close()
    print('Wrote',DB,'and data/analysis.json; all reconciliation checks passed')
    print('December',results['01_arr_bridge'][-1])
if __name__=='__main__': main()