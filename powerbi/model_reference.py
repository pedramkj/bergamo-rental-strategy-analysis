"""Python-model reference cases for execution against actual Desktop DAX."""
from pathlib import Path
import json,sys,math
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from financial_model import load_assumptions,str_cash,ltr_cash
a=load_assumptions();r=json.loads((ROOT/'results/rental-market-analysis.json').read_text(encoding='utf8'))
defaults={'BookedNights':a['booked_nights'],'ADR':a['gross_nightly_eur'],'LTRRent':r['primary']['mean'],'HostFee':a['host_fee'],'Tax':a['tax'],'Cleaning':a['cleaning_per_turnover'],'Stay':a['stay_nights'],'VariableCost':a['other_variable_per_night'],'STRFixed':a['common_fixed']+a['str_incremental_fixed'],'LTRFixed':a['common_fixed'],'PaidMonths':a['paid_months'],'Preparation':0}
def reference(changes):
    p={**defaults,**changes};shared={**a,'host_fee':p['HostFee'],'tax':p['Tax'],'cleaning_per_turnover':p['Cleaning'],'stay_nights':p['Stay'],'other_variable_per_night':p['VariableCost']}
    sn=str_cash(p['BookedNights'],p['ADR'],{**shared,'common_fixed':0,'str_incremental_fixed':p['STRFixed']})
    ln=ltr_cash(p['LTRRent'],{**shared,'common_fixed':p['LTRFixed']},p['PaidMonths'])
    contribution=p['ADR']*(1-p['HostFee']-p['Tax'])-p['Cleaning']/p['Stay']-p['VariableCost'];target=ln+p['STRFixed']+p['Preparation']/a['recovery_years']
    return {'STR':sn,'LTR':ln,'Gap':sn-ln,'Nights':max(0,math.ceil(target/contribution)) if contribution>0 else None,'ADR':((target/p['BookedNights'])+p['Cleaning']/p['Stay']+p['VariableCost'])/(1-p['HostFee']-p['Tax']) if p['BookedNights']>0 else None,'LTRRent':(sn+p['LTRFixed'])/(p['PaidMonths']*(1-p['Tax'])) if p['PaidMonths']>0 else None}
cases=[('baseline',{}),('historical900',{'LTRRent':a['long_monthly']})]
for name,value in [('BookedNights',210),('ADR',130),('LTRRent',1000),('HostFee',.20),('Tax',.25),('Cleaning',45),('Stay',2),('VariableCost',15),('STRFixed',4000),('LTRFixed',2500),('PaidMonths',11),('Preparation',15000)]:cases.append(('change_'+name,{name:value}))
cases += [('native_ADR50',{'ADR':50}),('zero_paid_months',{'PaidMonths':0}),('zero_bookings',{'BookedNights':0}),('negative_night_contribution',{'ADR':50,'Cleaning':100,'Stay':1,'VariableCost':40}),('combined',{'BookedNights':210,'ADR':130,'Cleaning':45,'Stay':4,'HostFee':.20,'Tax':.25,'LTRRent':1000,'STRFixed':4000,'LTRFixed':2000,'PaidMonths':11,'Preparation':15000})]
result={'source_commit':'f53e659a98b110904498613ff4b5e8beabfa212d','defaults':defaults,'cases':[{'name':name,'selections':changes,'expected':reference(changes)} for name,changes in cases]}
dest=ROOT/'powerbi/validation/python-reference.json';dest.parent.mkdir(exist_ok=True);dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(f'Wrote {len(cases)} Python reference cases.')
