"""Publication figures derived from the canonical rental sample and model."""
import json,csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def build(output=None):
    out=Path(output) if output else ROOT/'figures/rental';out.mkdir(parents=True,exist_ok=True)
    r=json.loads((ROOT/'results/rental-market-analysis.json').read_text(encoding='utf8'))
    from rental_market_analysis import read
    rows=read('primary-comparable-sample.csv');bench={x['benchmark_id']:float(x['value_eur_m2_month']) for x in read('market-benchmarks.csv') if x['value_eur_m2_month']}
    navy='#101C30';teal='#2F7776';gold='#C6A46C'
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':170})
    def save(name):plt.tight_layout();plt.savefig(out/name,bbox_inches='tight');plt.close()
    fig,ax=plt.subplots(figsize=(7,3));v=[float(x['base_monthly_eur']) for x in rows]
    ax.hist(v,bins=[600,700,800,900,1000,1100,1200,1300],color=navy,edgecolor='white');ax.axvline(r['primary']['mean'],color=gold,linewidth=2,label=f"Mean EUR{r['primary']['mean']:.2f}");ax.axvline(r['primary']['median'],color=teal,linestyle='--',label=f"Median EUR{r['primary']['median']:.0f}");ax.set_xlabel('Monthly base asking rent EUR');ax.set_ylabel('Selected comparable properties');ax.set_title(f"Primary rental sample distribution (n={len(rows)})");ax.set_xticks(range(600,1301,100));ax.legend(frameon=False,fontsize=9);save('rent-distribution.png')
    fig,ax=plt.subplots(figsize=(7,3));labels=['Sample mean','Sample median','Idealista Centro Citta','Immobiliare combined zone','Immobiliare city'];values=[r['primary_price_per_advertised_m2']['mean'],r['primary_price_per_advertised_m2']['median'],bench['B02'],bench['B04'],bench['B03']];ax.barh(labels,values,color=[navy,teal,'#657080','#657080','#657080']);ax.invert_yaxis();ax.set_xlabel('EUR per advertised/provider m² per month');ax.set_title('Unit-price context with different property mixes');
    for i,v in enumerate(values):ax.text(v+.12,i,f'{v:.2f}',va='center',fontsize=9)
    ax.set_xlim(0,max(values)+3);save('unit-price-context.png')
    c=r['counts'];fig,ax=plt.subplots(figsize=(7,3));labels=['Original rows','Preliminary leads','Additional candidates','Canonical groups*','Primary properties','Secondary properties'];values=[21,20,c['additional_candidates'],c['canonical_groups_including_unresolved'],len(rows),c['secondary_properties']];ax.barh(labels,values,color=[navy,navy,navy,'#657080',teal,gold]);ax.invert_yaxis();ax.set_xlabel('Count at each labelled stage (not additive)');ax.set_title('Candidate reconciliation and screening');
    for i,v in enumerate(values):ax.text(v+.7,i,str(v),va='center')
    ax.set_xlim(0,max(values)+10);save('candidate-screening.png')
    h=r['historical_900_scenario'];e=r['evidence_informed_scenario'];fig,ax=plt.subplots(figsize=(7,3));labels=['STR unchanged','LTR historical EUR 900','LTR sample-mean scenario'];values=[h['str_net'],h['ltr_net'],e['ltr_net']];ax.bar(labels,values,color=[navy,'#657080',teal]);ax.set_ylabel('Modelled annual net cash EUR');ax.set_ylim(0,8000);ax.set_title('Historical and evidence-informed scenarios');
    for i,v in enumerate(values):ax.text(i,v+120,f'{v:,.2f}',ha='center',fontsize=9)
    save('net-cash-comparison.png')
    fig,ax=plt.subplots(figsize=(7,3));g=r['rent_sensitivity'];ax.plot([x['monthly_rent'] for x in g],[x['ltr_net'] for x in g],marker='o',color=teal,label='LTR with 12 paid months');ax.axhline(h['str_net'],color=navy,linestyle='--',label='STR EUR 6,544.50');ax.scatter([e['monthly_base_rent']],[e['ltr_net']],color=gold,zorder=3,label=f"Sample mean EUR{e['monthly_base_rent']:.2f}");ax.set_xlabel('Monthly base rent EUR');ax.set_ylabel('Modelled annual net cash EUR');ax.set_title('Rental-alternative sensitivity');ax.legend(frameon=False,fontsize=8);save('rent-sensitivity.png')
    fig,ax=plt.subplots(figsize=(7,3));x=range(4);hv=[z['minimum_whole_nights'] for z in h['break_even']];ev=[z['minimum_whole_nights'] for z in e['break_even']];ax.bar([i-.18 for i in x],hv,width=.36,color='#657080',label='Historical EUR 900 rent');ax.bar([i+.18 for i in x],ev,width=.36,color=teal,label='Sample-mean rent');ax.set_xticks(list(x),['0','5,000','10,000','15,000']);ax.set_xlabel('Incremental preparation EUR recovered over 5 years');ax.set_ylabel('Minimum whole booked nights at EUR115');ax.set_ylim(0,280);ax.set_title('Booked-night thresholds by rental alternative');ax.legend(frameon=False,fontsize=8)
    for i in x:
        ax.text(i-.18,hv[i]+4,str(hv[i]),ha='center',fontsize=8);ax.text(i+.18,ev[i]+4,str(ev[i]),ha='center',fontsize=8)
    save('break-even-comparison.png')
    return out
if __name__=='__main__':print(build())
