"""Reproduce the descriptive BGY/city comparison from attributed numeric snapshots."""
import json,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run():
    rows=json.loads((ROOT/'data/airport-city-annual.json').read_text(encoding='utf8'))
    source=json.loads((ROOT/'data/airport-bgy-source-rows.json').read_text(encoding='utf8'))
    monthly=json.loads((ROOT/'data/validated-monthly-analysis.json').read_text(encoding='utf8'))
    if not ([r['year'] for r in rows] == list(range(2019, 2026))):
        raise ValueError("Validation failed: [r['year'] for r in rows] == list(range(2019, 2026))")
    result=[]
    for i,r in enumerate(rows):
        src=source[i]['rows'];assert len(src)==8
        # Row 4 is cumulative all-traffic summary; row 6 is cumulative passenger detail.
        if not (r['airport_passengers'] == int(src[6][-2].replace('.', ''))):
            raise ValueError("Validation failed: r['airport_passengers'] == int(src[6][-2].replace('.', ''))")
        if not (r['airport_passengers'] == int(src[4][5 if r['year'] in [2021, 2022, 2023] else 4].replace('.', ''))):
            raise ValueError("Validation failed: r['airport_passengers'] == int(src[4][5 if r['year'] in [2021, 2022, 2023] else 4].replace('.', ''))")
        if r['year']<2025:
            for k in ['arrivals','guest_nights']:
                if not (r['city_' + k] == sum((x[k] for x in monthly if x['year'] == r['year']))):
                    raise ValueError("Validation failed: r['city_' + k] == sum((x[k] for x in monthly if x['year'] == r['year']))")
        calc={'year':r['year']}
        for key in ['airport_passengers','city_arrivals','city_guest_nights']:
            calc[key]=r[key]
            calc[key+'_index_2019']=100*r[key]/rows[0][key]
            calc[key+'_yoy_pct']=None if i==0 else 100*(r[key]/rows[i-1][key]-1)
        result.append(calc)
    if not (result[-1]['airport_passengers_yoy_pct'] < 0):
        raise ValueError("Validation failed: result[-1]['airport_passengers_yoy_pct'] < 0")
    if not (result[-1]['city_arrivals_yoy_pct'] > 0):
        raise ValueError("Validation failed: result[-1]['city_arrivals_yoy_pct'] > 0")
    if not (result[-1]['city_guest_nights_yoy_pct'] > 0):
        raise ValueError("Validation failed: result[-1]['city_guest_nights_yoy_pct'] > 0")
    out=ROOT/'results';out.mkdir(exist_ok=True)
    (out/'airport-comparison.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    with (out/'airport-comparison.csv').open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(result[0]));w.writeheader();w.writerows(result)
    print('Validated seven annual airport totals and city join; 2025 trends diverge.')
    return result
if __name__=='__main__':run()
