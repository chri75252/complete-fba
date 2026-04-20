import csv
path = r'OUTPUTS\PRODUCTS_LISTS\efghousewares-co-uk_validation_20260419_102255\csvs\verified_profitable_efghousewares-co-uk_20260419.csv'
with open(path,'r',encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

a_disc = [r for r in rows if r['Bucket']=='A' and r.get('Profit_Discrepancy')=='YES']
print(f'Bucket A with profit discrepancy: {len(a_disc)}')
for r in a_disc:
    st = r['SupplierTitle'][:45]
    ap = r['NetProfit']
    fp = r['FinReport_NetProfit']
    print(f'  {st} | Analysis={ap} | Fin={fp}')

t3b = [r for r in rows if r['Bucket']=='B' and r['tier']=='TIER_3_NEEDS_REVIEW']
print(f'\nT3 in Bucket B: {len(t3b)}')
for r in t3b[:5]:
    st = r['SupplierTitle'][:40]
    at = r['AmazonTitle'][:40]
    print(f'  S: {st} <-> A: {at}')

ba = sum(1 for r in rows if r['Bucket']=='A')
bb = sum(1 for r in rows if r['Bucket']=='B')
bc = sum(1 for r in rows if r['Bucket']=='C')
print(f'\nBucket dist: A={ba}, B={bb}, C={bc}')
uqm = sum(1 for r in rows if r['Unit_Qty_Flag']=='MATCH')
uqa = sum(1 for r in rows if r['Unit_Qty_Flag']=='MISMATCH_ADJUST')
uqu = sum(1 for r in rows if r['Unit_Qty_Flag']=='UNCLEAR')
print(f'UQF: MATCH={uqm}, MISMATCH_ADJUST={uqa}, UNCLEAR={uqu}')
