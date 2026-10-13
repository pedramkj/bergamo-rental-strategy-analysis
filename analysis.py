"""Offline reproduction of the report, using only Python's standard library."""
import calendar, csv, json, math, statistics
from pathlib import Path
ROOT = Path(__file__).resolve().parent
def read(name):
    return json.loads((ROOT/'data'/name).read_text(encoding='utf8'))
def str_cash(n, adr, a, incremental=None):
    return n*(adr*(1-a['tax']-a['host_fee'])-a['cleaning_per_turnover']/a['stay_nights']-a['other_variable_per_night'])-a['common_fixed']-(a['str_incremental_fixed'] if incremental is None else incremental)
def ltr_cash(rent, a, months=None):
    return rent*(a['paid_months'] if months is None else months)*(1-a['tax'])-a['common_fixed']
def allocate(total, shares):
    values=[total*s for s in shares];out=[math.floor(x) for x in values]
    order=sorted(range(12),key=lambda i: (-(values[i]-out[i]),i))
    for i in order[:total-sum(out)]:out[i]+=1
    return out
def run():
    a=read('assumptions.json');monthly=read('validated-monthly-analysis.json')
    assert len(monthly)==72
    annual={}
    for y in range(2019,2025):
        part=[x for x in monthly if x['year']==y]
        assert sorted(x['month'] for x in part)==list(range(1,13))
        annual[y]={k:sum(x[k] for x in part) for k in ['arrivals','guest_nights']}
    # Annual source contains overlapping totals; select the all-structure/all-nationality row.
    control=read('official-annual-raw.json')
    verified=[]
    for row in control:
        if row['tipo_struttura']=='Totale' and row['cittadinanza_turisti']=='Totale':
            y=int(row['anno'])
            if y in annual:
                assert annual[y]['arrivals']==int(row['arrivi'].replace(',',''))
                assert annual[y]['guest_nights']==int(row['presenze'].replace(',',''))
                verified.append(y)
    assert sorted(verified)==list(range(2019,2025)), 'Missing annual controls'
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
    allocated={str(n):allocate(n,shares) for n in [134,150,180,210]}
    stored=read('seasonal-booking-estimate.json')
    for n,values in allocated.items():
        assert values==[x['bookings'][n] for x in stored['months']], 'Seasonal snapshot differs'
    net=str_cash(a['booked_nights'],a['gross_nightly_eur'],a);long=ltr_cash(a['long_monthly'],a)
    contribution=a['gross_nightly_eur']*(1-a['tax']-a['host_fee'])-a['cleaning_per_turnover']/a['stay_nights']-a['other_variable_per_night']
    breaks=[]
    for setup in [0,5000,10000,15000]:
        exact=(long+a['common_fixed']+a['str_incremental_fixed']+setup/a['recovery_years'])/contribution
        breaks.append(dict(setup=setup,exact_nights=exact,minimum_whole_nights=math.ceil(exact)))
    listings=list(csv.DictReader((ROOT/'data/listings.csv').open(encoding='utf8')))
    prices=[float(x['monthly_eur']) for x in listings if x['group']=='primary']
    assert len({x['id'] for x in listings})==len(listings)
    result={'scope':'City of Bergamo; scenario incomes are not city averages','annual':annual,'annual_controls_verified':verified,'seasonal_allocations':allocated,'str_net':net,'ltr_net':long,'gap':net-long,'ltr_sensitivity':{r:ltr_cash(r,a) for r in [700,800,900,1000,1100]},'two_sided_gap':[{ 'str_incremental_fixed':c,'long_monthly':r,'gap':str_cash(180,115,a,c)-ltr_cash(r,a)} for c in [600,1200,1800] for r in [800,900,1000]],'break_even':breaks,'primary_listing_count':len(prices),'primary_asking_median':statistics.median(prices),'listing_screened_count':len(listings)}
    assert math.isclose(net,6544.5,abs_tol=1e-8)
    assert math.isclose(long,6732,abs_tol=1e-8)
    assert [x['minimum_whole_nights'] for x in breaks]==[184,203,222,241]
    for b in breaks:
        target=long+b['setup']/a['recovery_years']
        assert str_cash(b['minimum_whole_nights'],115,a)>=target
        assert str_cash(b['minimum_whole_nights']-1,115,a)<target
    out=ROOT/'results';out.mkdir(exist_ok=True)
    (out/'analysis.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps({k:result[k] for k in ['str_net','ltr_net','gap','primary_listing_count','primary_asking_median']},indent=2))
    return result
if __name__=='__main__':run()
