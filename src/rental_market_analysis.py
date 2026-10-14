"""Reconcile manually reviewed advertisements without inferring missing facts.

The source CSVs contain public listing facts, never private advertiser contacts.
Property identity decisions are explicit reviewed edges, not price-based merges.
"""
import csv,json,statistics,math
from collections import Counter,defaultdict
from pathlib import Path
from urllib.parse import urlparse
from listing_review import parse_monthly_eur
from financial_model import load_assumptions,ltr_cash,str_cash,booking_threshold,required_nightly_price,PREPARATION_SCENARIOS,RENT_SCENARIOS,INCREMENTAL_COST_SCENARIOS,BOOKING_SCENARIOS,PRICE_SCENARIOS
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data/rental'
CENTRAL_LABELS={'Centro',"Sant'Alessandro",'Piazzetta Santo Spirito'}
def read(name):
    with (DATA/name).open(encoding='utf8',newline='') as f:return list(csv.DictReader(f))
def write(name,rows,fields=None):
    fields=fields or list(dict.fromkeys(k for r in rows for k in r))
    with (DATA/name).open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def numeric(value):
    if value is None or str(value).strip()=='':return None
    return float(value)
def normalise_price(advertised,base=None,explicit_charges=None,bundled=False):
    """An explicit base takes priority; a bundle without a split stays unknown."""
    if base is not None:return base
    if bundled:return None if explicit_charges is None else advertised-explicit_charges
    return advertised
def contract_class(label):
    s=label.lower().replace(' ','')
    if 'mid' in s or 'temporary' in s or 'transitorio' in s:return 'temporary'
    return '4+4' if '4+4' in s else 'other_or_unspecified'
def geographic_eligible(r):
    return r.get('municipality')=='Bergamo' and r.get('neighborhood') in CENTRAL_LABELS and r.get('review_flag')!='conflicting_location'
def screen(r):
    reasons=[]
    if r.get('status')!='verified_advertisement':reasons.append('source_unresolved_or_historical')
    if r.get('review_flag'):reasons.append(r['review_flag'])
    if not geographic_eligible(r):reasons.append('outside_or_unresolved_selected_area')
    size=numeric(r.get('advertised_m2'));rent=numeric(r.get('base_monthly_eur'))
    if rent is None or rent<=0:reasons.append('base_rent_unresolved')
    if numeric(r.get('rooms'))!=2 or numeric(r.get('bedrooms'))!=1:reasons.append('not_verified_one_bedroom')
    if r.get('furnished')!='yes':reasons.append('not_verified_fully_furnished')
    if r.get('bundled_services')=='yes':reasons.append('serviced_or_bundled')
    if contract_class(r.get('contract',''))=='temporary':reasons.append('temporary_contract')
    if reasons:return 'excluded',sorted(set(reasons))
    if size is None or not 40<=size<=80:return 'excluded',['outside_secondary_size_range']
    if 40<=size<=65 and r['contract']=='4+4':return 'primary',[]
    return 'secondary',['larger_size_or_other_contract']
def describe(values):
    v=sorted(values);n=len(v)
    if not n:return {'n':0,'mean':None,'median':None,'sd':None,'min':None,'max':None,'q1':None,'q3':None,'iqr':None,'total':0}
    q=statistics.quantiles(v,n=4,method='inclusive') if n>1 else [v[0]]*3
    return dict(n=n,total=sum(v),mean=statistics.mean(v),median=statistics.median(v),sd=statistics.stdev(v) if n>1 else None,min=min(v),max=max(v),q1=q[0],q3=q[2],iqr=q[2]-q[0])
def property_groups(candidates,decisions):
    """Exact-URL repeats merge. Only reviewed confirmed edges merge properties."""
    parent={c['candidate_id']:c['candidate_id'] for c in candidates}
    def find(x):
        while parent[x]!=x:x=parent[x]
        return x
    def union(a,b):
        aa,bb=find(a),find(b)
        if aa!=bb:parent[max(aa,bb)]=min(aa,bb)
    seen={}
    for c in candidates:
        url=c['url']
        if url:
            if url in seen:union(c['candidate_id'],seen[url])
            else:seen[url]=c['candidate_id']
    for d in decisions:
        if d['decision']=='confirmed_duplicate':union(d['left_candidate'],d['right_candidate'])
    return {k:find(k) for k in parent}
def scenario(rent,a):
    b=dict(a,long_monthly=rent);sn=str_cash(a['booked_nights'],a['gross_nightly_eur'],a);ln=ltr_cash(rent,a)
    return {'monthly_base_rent':rent,'annual_gross':12*rent,'str_net':sn,'ltr_net':ln,'gap':sn-ln,'break_even':[{**booking_threshold(s,b),'required_nightly_price':required_nightly_price(s,b)} for s in PREPARATION_SCENARIOS], 'ltr_vacancy':[{'paid_months':m,'ltr_net':ltr_cash(rent,a,m)} for m in [10,11,12]],'differential_cost_sensitivity':[{'str_additional_fixed':c,'gap':str_cash(a['booked_nights'],a['gross_nightly_eur'],a,c)-ln} for c in INCREMENTAL_COST_SCENARIOS]}
def run():
    candidates=read('candidate-register.csv');observations=read('source-observations.csv');decisions=read('deduplication-decisions.csv')
    ids=[r['candidate_id'] for r in candidates]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate candidate identifier')
    if set(ids)&{f'C{i:02}' for i in range(1,22)}!={f'C{i:02}' for i in range(1,22)}:raise ValueError('Original candidate missing')
    if set(ids)&{f'A{i:02}' for i in range(1,21)}!={f'A{i:02}' for i in range(1,21)}:raise ValueError('Assistant lead missing')
    byurl={r['url']:r for r in observations}
    if len(byurl)!=len(observations):raise ValueError('Source URL repeated')
    groups=property_groups(candidates,decisions);master=[]
    for c in candidates:
        o=byurl.get(c['url'],{})
        r={**c,**o,'candidate_id':c['candidate_id'],'property_id':'P-'+groups[c['candidate_id']] if o.get('status')=='verified_advertisement' else 'U-'+groups[c['candidate_id']]}
        if not o:r.update(status='unresolved',verification_notes='Exact listing URL not recovered. Possible matches do not establish property identity.')
        cohort,reasons=screen(r);r['cohort']=cohort;r['exclusion_reason']=';'.join(reasons)
        r['duplicate_status']='unresolved_identity' if r['property_id'].startswith('U-') else 'distinct_within_reviewed_set'
        for d in decisions:
            if r['candidate_id'] in [d['left_candidate'],d['right_candidate']]:
                if d['decision'] in ['confirmed_duplicate','probable_duplicate']:r['duplicate_status']=d['decision']
        r['price_per_advertised_m2']=numeric(r.get('base_monthly_eur'))/numeric(r.get('advertised_m2')) if numeric(r.get('base_monthly_eur')) and numeric(r.get('advertised_m2')) else ''
        master.append(r)
    grouped=defaultdict(list)
    for r in master:grouped[r['property_id']].append(r)
    primary=[];secondary=[];properties=[]
    for pid,rs in sorted(grouped.items()):
        # A duplicate's other ad can expose a price conflict. Never average two offers.
        prices={numeric(r.get('base_monthly_eur')) for r in rs if r.get('status')=='verified_advertisement'}-{None}
        if len(prices)>1:
            for r in rs:r.update(cohort='excluded',exclusion_reason='conflicting_cluster_price')
        first=rs[0];rr=dict(first,candidate_ids=';'.join(r['candidate_id'] for r in rs),source_urls=';'.join(dict.fromkeys(r['url'] for r in rs if r['url'])))
        properties.append(rr)
        if rr['cohort']=='primary':primary.append(rr)
        if rr['cohort']=='secondary':secondary.append(rr)
    fields=list(dict.fromkeys(k for r in master for k in r))
    write('master-listing-registry.csv',master,fields)
    write('canonical-properties.csv',properties)
    write('original-21-audit.csv',[r for r in master if r['origin']=='original_21'],fields)
    write('assistant-20-audit.csv',[r for r in master if r['origin']=='assistant_20'],fields)
    write('primary-comparable-sample.csv',primary,list(properties[0]))
    write('secondary-sample.csv',secondary,list(properties[0]))
    write('duplicate-clusters.csv',[{'property_id':pid,'candidate_ids':';'.join(r['candidate_id'] for r in rs),'source_urls':';'.join(dict.fromkeys(r['url'] for r in rs if r['url'])),'decision':'confirmed_duplicate','price_status':'conflict' if len({r.get('base_monthly_eur') for r in rs})>1 else 'consistent'} for pid,rs in grouped.items() if len(rs)>1])
    raw_original=[parse_monthly_eur(r['recorded_price']) for r in candidates if r['origin']=='original_21'];raw_original=[v for v in raw_original if v is not None]
    raw_assistant=[parse_monthly_eur(r['recorded_price']) for r in candidates if r['origin']=='assistant_20']
    if len(raw_original)!=17 or sum(raw_original)!=17240 or sum(raw_assistant)!=17185:raise ValueError('Historical arithmetic control failed')
    a=load_assumptions();hist=scenario(900,a)
    if not math.isclose(hist['str_net'],6544.5,abs_tol=1e-8) or hist['ltr_net']!=6732:raise ValueError('Historical financial baseline changed')
    pstats=describe([numeric(r['base_monthly_eur']) for r in primary]);sstats=describe([numeric(r['base_monthly_eur']) for r in secondary]);ppsqm=describe([numeric(r['price_per_advertised_m2']) for r in primary])
    eligible_roots={groups[r['candidate_id']] for r in master if r['cohort']=='primary'}
    result={'observation_date':'2026-10-14','method':'Manual online rental listing review','geography_rule':'Comune di Bergamo; source label Centro or Sant\u0027Alessandro or explicitly named Piazzetta Santo Spirito. Portal-label study selection, not an official cadastral boundary. Conflicting location excluded.','counts':{'original_candidates':21,'assistant_leads':20,'additional_candidates':len(candidates)-41,'total_candidates':len(candidates),'distinct_source_urls':len({r['url'] for r in candidates if r['url']}),'canonical_groups_including_unresolved':len(grouped),'unique_physical_properties_total':None,'verified_distinct_properties':sum(r.get('status')=='verified_advertisement' and r['duplicate_status'] not in ['probable_duplicate','unresolved_identity'] for r in properties),'confirmed_duplicate_clusters':sum(len(rs)>1 for rs in grouped.values()),'confirmed_duplicate_rows_removed':len(candidates)-len(grouped),'probable_duplicate_review_pairs':sum(d['decision']=='probable_duplicate' for d in decisions),'primary_properties':len(primary),'secondary_properties':len(secondary),'excluded_canonical_groups':len(grouped)-len(primary)-len(secondary),'unresolved_candidate_rows':sum(r.get('status') not in ['verified_advertisement','verified_wrong_property'] or not r.get('url') for r in master),'primary_origins':dict(Counter(r['origin'] for r in primary))},'raw_original_numeric':describe(raw_original),'raw_assistant_leads':describe(raw_assistant),'primary':pstats,'secondary':sstats,'primary_price_per_advertised_m2':ppsqm,'exclusion_reason_counts':dict(Counter(reason for r in properties if r['cohort']=='excluded' for reason in r['exclusion_reason'].split(';'))),'primary_neighborhood_breakdown':{k:describe([numeric(r['base_monthly_eur']) for r in primary if r['neighborhood']==k]) for k in sorted({r['neighborhood'] for r in primary})},'primary_contract_breakdown':dict(Counter(r['contract'] for r in primary)),'primary_source_breakdown':dict(Counter(r['platform'] for r in primary)),'historical_900_scenario':hist,'evidence_informed_scenario':scenario(pstats['mean'],a) if pstats['n'] else None,'rent_sensitivity':[{'monthly_rent':r,'ltr_net':ltr_cash(r,a),'gap':hist['str_net']-ltr_cash(r,a)} for r in sorted(set(RENT_SCENARIOS+(pstats['mean'],)))] if pstats['n'] else [],'str_price_booking_sensitivity':[{'booked_nights':n,'gross_nightly_eur':p,'str_net':str_cash(n,p,a)} for n in BOOKING_SCENARIOS for p in PRICE_SCENARIOS],'limitations':['Convenience sample, not a representative city market average.','Source content may be indexed or cached. Apartment availability and signed contract rents are not verified.','Complete physical-property count remains unknown for unresolved leads and probable duplicates.','Advertised surface measures differ from net OMI surfaces and may include weighted outdoor/accessory areas.','Amenity and parking differences remain; no causal adjustment estimated.','Fewer than20 strict comparables is reported without weakening criteria.']}
    result['counts']['verified_advertisement_groups_no_probable_match']=result['counts'].pop('verified_distinct_properties')
    result['counts']['primary_candidate_rows']=sum(r['cohort']=='primary' for r in master)
    result['counts']['secondary_candidate_rows']=sum(r['cohort']=='secondary' for r in master)
    result['counts']['excluded_candidate_rows']=sum(r['cohort']=='excluded' for r in master)
    result['secondary_contract_breakdown']=dict(Counter(r['contract'] for r in secondary))
    result['secondary_source_breakdown']=dict(Counter(r['platform'] for r in secondary))
    result['candidate_contract_breakdown']=dict(Counter(r.get('contract','unresolved') for r in master))
    result['candidate_source_breakdown']=dict(Counter(r.get('platform','unresolved') for r in master))
    (ROOT/'results/rental-market-analysis.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    write('source-register.csv',[{k:r.get(k,'') for k in ['url','platform','listing_id','verification_date','access_mode','status','listing_updated','verification_notes']} for r in observations])
    def fmt(x):return 'Missing' if x in ['',None] else str(x)
    report=['# Rental listing investigation','',f"Manual online rental listing review on14October2026. {len(candidates)} candidate rows, {len(grouped)} canonical groups including unresolved identities, {len(primary)} primary and {len(secondary)} secondary comparable properties. The total physical-property count is unknown. The target of20 primary properties was not reached.",'',f"Primary mean EUR{pstats['mean']:.2f}, median EUR{pstats['median']:.2f}; total EUR{pstats['total']:,.0f} / {pstats['n']}. Raw controls remain17240/17=1014.12 and17185/20=859.25. These describe different evidence sets.",'','Historical STR/LTR: EUR6544.50 / EUR6732.00, gap minus187.50. Evidence-informed LTR: EUR'+f"{result['evidence_informed_scenario']['ltr_net']:.2f}"+', gap minus'+f"{abs(result['evidence_informed_scenario']['gap']):.2f}"+'. Conditional model outputs, not observed profits.','', '## Complete candidate audit','', 'Recorded prices are preserved in the source register. The table shows separately verified base rent when available; inclusive advertised packages and historical-only values remain labelled. Candidate identifiers are public research IDs, not cadastral IDs.','', '| Candidate | Property group | Platform | Source base EUR/month | Advertised m² | Location | Contract | Source | Verification | Identity | Cohort and reason |','|---|---|---|---:|---:|---|---|---|---|---|---|']
    for r in master:
        vals=[r['candidate_id'],r['property_id'],r.get('platform','unresolved'),fmt(r.get('base_monthly_eur')),fmt(r.get('advertised_m2')),r.get('location') or r.get('recorded_location'),r.get('contract','unresolved'),f"[Listing]({r['url']})" if r['url'] else 'URL unresolved',r.get('status','unresolved'),r['duplicate_status'],r['cohort']+' '+r['exclusion_reason']]
        report.append('| '+' | '.join(str(x).replace('|','/') for x in vals)+' |')
    report+=['','## Reviewed identity decisions','','| Left | Right | Decision | Evidence |','|---|---|---|---|']
    report.extend('| '+' | '.join(d[k] for k in ['left_candidate','right_candidate','decision','evidence'])+' |' for d in decisions)
    report+=['','Full source facts, historical prices, fees and original links remain in [master registry](../data/rental/master-listing-registry.csv) and [source observations](../data/rental/source-observations.csv). [Criteria and conventions](../data/rental/data-dictionary.md) document the geographic proxy, retrieval limits, missing values and statistical choices.','']
    (ROOT/'reports/Rental_Listing_Investigation.md').write_text('\n'.join(report),encoding='utf8')
    return result
if __name__=='__main__':
    result=run();print(json.dumps({'counts':result['counts'],'primary':result['primary'],'new_scenario':result['evidence_informed_scenario']},indent=2))
