"""Offline reproduction of the report, using only Python's standard library."""
import calendar, csv, json, math, statistics
from pathlib import Path
from financial_model import str_cash, ltr_cash, booking_threshold, validate_assumptions, BOOKING_SCENARIOS, RENT_SCENARIOS, COMPARISON_RENTS, INCREMENTAL_COST_SCENARIOS, PREPARATION_SCENARIOS
ROOT = Path(__file__).resolve().parents[1]
def read(name):
    return json.loads((ROOT/'data'/name).read_text(encoding='utf8'))
def allocate(total, shares):
    values=[total*s for s in shares];out=[math.floor(x) for x in values]
    order=sorted(range(12),key=lambda i: (-(values[i]-out[i]),i))
    for i in order[:total-sum(out)]:out[i]+=1
    return out
def run():
    a=read('assumptions.json');validate_assumptions(a);monthly=read('validated-monthly-analysis.json')
    if not (len(monthly) == 72):
        raise ValueError('Validation failed: len(monthly) == 72')
    annual={}
    for y in range(2019,2025):
        part=[x for x in monthly if x['year']==y]
        if not (sorted((x['month'] for x in part)) == list(range(1, 13))):
            raise ValueError("Validation failed: sorted((x['month'] for x in part)) == list(range(1, 13))")
        annual[y]={k:sum(x[k] for x in part) for k in ['arrivals','guest_nights']}
    # Annual source contains overlapping totals; select the all-structure/all-nationality row.
    control=read('official-annual-raw.json')
    verified=[]
    for row in control:
        if row['tipo_struttura']=='Totale' and row['cittadinanza_turisti']=='Totale':
            y=int(row['anno'])
            if y in annual:
                if not (annual[y]['arrivals'] == int(row['arrivi'].replace(',', ''))):
                    raise ValueError("Validation failed: annual[y]['arrivals'] == int(row['arrivi'].replace(',', ''))")
                if not (annual[y]['guest_nights'] == int(row['presenze'].replace(',', ''))):
                    raise ValueError("Validation failed: annual[y]['guest_nights'] == int(row['presenze'].replace(',', ''))")
                verified.append(y)
    if not (sorted(verified) == list(range(2019, 2025))):
        raise ValueError('Missing annual controls')
    years=[2019,2022,2023,2024]
    daily_index=[]
    for m in range(1,13):
        ratios=[]
        for y in years:
            row=next(x for x in monthly if x['year']==y and x['month']==m)
            ratios.append((row['guest_nights']/calendar.monthrange(y,m)[1])/(annual[y]['guest_nights']/(366 if calendar.isleap(y) else 365)))
        daily_index.append(statistics.mean(ratios))
    weights=[v*calendar.monthrange(2025,i+1)[1] for i,v in enumerate(daily_index)]
    shares=[v/sum(weights) for v in weights]
    allocated={str(n):allocate(n,shares) for n in (134,*BOOKING_SCENARIOS)}
    stored=read('seasonal-booking-estimate.json')
    for n,values in allocated.items():
        if not (values == [x['bookings'][n] for x in stored['months']]):
            raise ValueError('Seasonal snapshot differs')
    net=str_cash(a['booked_nights'],a['gross_nightly_eur'],a);long=ltr_cash(a['long_monthly'],a)
    breaks=[]
    for setup in PREPARATION_SCENARIOS:
        breaks.append(booking_threshold(setup,a))
    listings=list(csv.DictReader((ROOT/'data/listings.csv').open(encoding='utf8')))
    prices=[float(x['monthly_eur']) for x in listings if x['group']=='primary']
    if not (len({x['id'] for x in listings}) == len(listings)):
        raise ValueError("Validation failed: len({x['id'] for x in listings}) == len(listings)")
    result={'scope':'City of Bergamo; scenario incomes are not city averages','annual':annual,'annual_controls_verified':verified,'seasonal_allocations':allocated,'str_net':net,'ltr_net':long,'gap':net-long,'ltr_sensitivity':{r:ltr_cash(r,a) for r in RENT_SCENARIOS},'two_sided_gap':[{ 'str_incremental_fixed':c,'long_monthly':r,'gap':str_cash(a['booked_nights'],a['gross_nightly_eur'],a,c)-ltr_cash(r,a)} for c in INCREMENTAL_COST_SCENARIOS for r in COMPARISON_RENTS],'break_even':breaks,'primary_listing_count':len(prices),'primary_asking_median':statistics.median(prices),'listing_screened_count':len(listings)}
    for b in breaks:
        target=long+b['setup']/a['recovery_years']
        if not (str_cash(b['minimum_whole_nights'], a['gross_nightly_eur'], a) >= target):
            raise ValueError('Whole-night threshold fails to meet target')
        if not (str_cash(b['minimum_whole_nights'] - 1, a['gross_nightly_eur'], a) < target):
            raise ValueError('Break-even threshold is not minimal')
    out=ROOT/'results';out.mkdir(exist_ok=True)
    (out/'analysis.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps({k:result[k] for k in ['str_net','ltr_net','gap','primary_listing_count','primary_asking_median']},indent=2))
    return result
if __name__=='__main__':run()
