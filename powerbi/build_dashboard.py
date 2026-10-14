"""Build a native PBIP/PBIR/TMDL report from the reviewed project evidence.

Run with --configure-local to set the documented RepositoryRoot parameter for
this checkout. Without that flag the portable project uses the documented
C:\\BergamoRentalAnalysis location. No published research outputs are rewritten.
"""
from pathlib import Path
import argparse,collections,csv,json,hashlib,zipfile,shutil,sys,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];PBI=ROOT/'powerbi'
sys.path.insert(0,str(ROOT/'src'))
from financial_model import BOOKING_SCENARIOS,PRICE_SCENARIOS,RENT_SCENARIOS,INCREMENTAL_COST_SCENARIOS,PREPARATION_SCENARIOS
parser=argparse.ArgumentParser();parser.add_argument('--configure-local',action='store_true');args=parser.parse_args()
MODEL=PBI/'Bergamo.SemanticModel';REPORT=PBI/'Bergamo.Report';DEF=REPORT/'definition'
for generated in [DEF/'pages',MODEL/'definition/tables']:
    assert generated.resolve().is_relative_to(PBI.resolve())
    if generated.exists():shutil.rmtree(generated)
def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
def put(path,text):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text.rstrip()+'\n',encoding='utf8')
def schema(kind,version):return f'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/{kind}/{version}/schema.json'
def extract_design():
    source=ROOT/'publication/Bergamo_LinkedIn_Carousel_EN_Final.pptx';counts=collections.Counter();fonts=collections.Counter();sizes=collections.Counter();ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
    with zipfile.ZipFile(source) as z:
        for n in z.namelist():
            if n.startswith('ppt/slides/slide') and n.endswith('.xml'):
                x=ET.fromstring(z.read(n));sizes.update(int(e.get('sz'))/100 for e in x.findall('.//a:rPr',ns) if e.get('sz'));counts.update(e.get('val') for e in x.findall('.//a:srgbClr',ns));fonts.update(e.get('typeface') for e in x.findall('.//a:latin',ns))
    palette={'navy':'#0D233A','canvas':'#F6F8FA','surface':'#FFFFFF','blue':'#1C4C74','teal':'#32B8B2','muted':'#64798B','divider':'#DBE5EA','pale_teal':'#ADCDD2','soft_teal':'#9CCACD','gold':'#C6A46C','ivory':'#F7F5F0'}
    for color in list(palette.values())[:9]:assert color[1:] in counts,color
    # Gold and ivory are cover-specific colors, extracted from the approved cover source.
    cover=(ROOT/'src/report_cover.py').read_text(encoding='utf8');assert "GOLD='C6A46C'" in cover and "IVORY='F7F5F0'" in cover
    tokens={'source_priority':['publication/Bergamo_LinkedIn_Carousel_EN_Final.pptx','reports/Bergamo_Rental_Strategies_Complete_EN_v03.docx','src/report_cover.py'],'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'palette':palette,'typography':{'family':fonts.most_common(1)[0][0],'page_title_pt':27,'section_title_pt':15,'body_pt':11,'label_pt':10,'callout_pt':32},'grid':{'width':1280,'height':800,'outer_margin':48,'gutter':24,'base_unit':8,'header_height':128,'navigation_height':48},'source_color_occurrences':dict(counts),'source_font_occurrences':dict(fonts),'source_font_sizes_pt':dict(sizes),'formatting':{'currency':'€#,0.00;(€#,0.00);€0.00','count':'#,0','percent':'0.0%;(0.0%);0.0%'}}
    dump(PBI/'design/design-tokens.json',tokens);return tokens
TOKENS=extract_design();C=TOKENS['palette'];FONT=TOKENS['typography']['family']
theme={'name':'BergamoTheme.json','dataColors':[C['blue'],C['teal'],C['muted'],C['gold'],C['soft_teal']],'background':C['canvas'],'foreground':C['navy'],'tableAccent':C['teal'],'good':C['teal'],'neutral':C['gold'],'bad':C['blue'],'textClasses':{'title':{'fontFace':FONT,'fontSize':15,'color':C['navy']},'label':{'fontFace':FONT,'fontSize':10,'color':C['muted']},'callout':{'fontFace':FONT,'fontSize':32,'color':C['navy']},'header':{'fontFace':FONT,'fontSize':12,'color':C['navy']}},'visualStyles':{'*':{'*':{'background':[{'show':False}],'border':[{'show':False}],'dropShadow':[{'show':False}],'visualHeader':[{'show':False}],'title':[{'show':True,'fontFamily':FONT,'fontSize':14,'fontColor':C['navy']}],'padding':[{'top':8,'bottom':8,'left':8,'right':8}],'visualTooltip':[{'show':True}]}},'slicer':{'*':{'header':[{'fontFamily':FONT,'textSize':10,'fontColor':C['muted']}],'items':[{'fontFamily':FONT,'textSize':11,'fontColor':C['navy']}]}},'tableEx':{'*':{'columnHeaders':[{'fontFamily':FONT,'fontSize':10,'fontColor':C['navy'],'backColor':C['divider']}],'values':[{'fontFamily':FONT,'fontSize':10,'fontColor':C['navy']}]}}}}
dump(PBI/'design/powerbi-theme.json',theme);dump(REPORT/'StaticResources/RegisteredResources/BergamoTheme.json',theme)
dump(PBI/'Bergamo.pbip',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json','version':'1.0','artifacts':[{'report':{'path':'Bergamo.Report'}}],'settings':{'enableAutoRecovery':True}})
dump(REPORT/'definition.pbir',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json','version':'4.0','datasetReference':{'byPath':{'path':'../Bergamo.SemanticModel'}}})
for folder,kind,identity in [(REPORT,'Report','62075445-0f7b-48b4-9291-b43bf7c5e5c2'),(MODEL,'SemanticModel','757363be-1da0-45b6-9cd8-39ca7197d258')]:
    dump(folder/'.platform',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json','metadata':{'type':kind,'displayName':'Bergamo Rental Strategies','description':'Reviewed evidence and conditional STR/LTR cash comparison.'},'config':{'version':'2.0','logicalId':identity}})
dump(MODEL/'definition.pbism',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json','version':'4.2','settings':{'qnaEnabled':False}})
put(MODEL/'definition/database.tmdl','database\n\tcompatibilityLevel: 1606')
put(MODEL/'definition/model.tmdl','model Model\n\tculture: en-US\n\tdefaultPowerBIDataSourceVersion: powerBI_V3\n\tsourceQueryCulture: en-US\n\tdataAccessOptions\n\t\tlegacyRedirects\n\t\treturnErrorValuesAsNull\n\n\tannotation PBI_ProTooling = ["DevMode"]')
root_value=str(ROOT) if args.configure_local else r'C:\BergamoRentalAnalysis'
put(MODEL/'definition/expressions.tmdl',f'expression RepositoryRoot = "{root_value}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n\tlineageTag: 8447d76b-77cf-4b78-98e0-5d88bfe46719')
currency='€#,0.00;(€#,0.00);€0.00'
def table(name,columns,m=None,dax=None,measures=None,column_format=None):
    s=f'table {name}\n'
    for col,typ,source in columns:
        s+=f'\n\tcolumn {col}\n\t\tdataType: {typ}\n\t\tsummarizeBy: none\n\t\tsourceColumn: {source}\n'
        if col in ['URL','AirportSource']:s+='\t\tdataCategory: WebUrl\n'
        if name in ['RiskNights','RiskADR','RiskRent','RiskCost','Setup'] and col=='Value':s+='\t\tformatString: #,0\n'
        if col in ['Rent','RentPerM2']:s+='\t\tformatString: '+currency+'\n'
        if column_format:s+='\t\tformatString: '+column_format+'\n\n\t\textendedProperty ParameterMetadata = {"version":0}\n'
    for name2,formula,fmt in measures or []:
        s+=f'\n\tmeasure \'{name2}\' =\n'+''.join('\t\t\t'+line+'\n' for line in formula.splitlines())+f'\t\tformatString: {fmt}\n'
    if dax:
        s+=f'\n\tpartition {name} = calculated\n\t\tmode: import\n\t\tsource = {dax}\n'
    else:
        s+=f'\n\tpartition {name} = m\n\t\tmode: import\n\t\tsource =\n'+''.join('\t\t\t'+line+'\n' for line in m.splitlines())
    put(MODEL/f'definition/tables/{name}.tmdl',s)
def csv_m(path,columns):
    names=[x[2] for x in columns];types={'string':'type text','double':'type number','int64':'Int64.Type'}
    selected=', '.join('"'+n+'"' for n in names)
    specs=', '.join('{"'+src+'", '+types[typ]+'}' for _,typ,src in columns)
    return f'let\n Source = Csv.Document(File.Contents(RepositoryRoot & "\\{path.replace("/",chr(92))}"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n Selected = Table.SelectColumns(Headers, {{{selected}}}),\n Typed = Table.TransformColumnTypes(Selected, {{{specs}}}, "en-US")\nin Typed'
listingcols=[('PropertyID','string','property_id'),('Cohort','string','cohort'),('Neighborhood','string','neighborhood'),('Rent','double','base_monthly_eur'),('Area','double','advertised_m2'),('Contract','string','contract'),('URL','string','url'),('Platform','string','platform'),('Status','string','status'),('Location','string','location'),('VerificationNotes','string','verification_notes'),('RentPerM2','double','price_per_advertised_m2')]
table('Listings',listingcols,csv_m('data/rental/canonical-properties.csv',listingcols))
candidatecols=[('CandidateID','string','candidate_id'),('PropertyID','string','property_id'),('Origin','string','origin'),('Status','string','status')]
table('Candidates',candidatecols,csv_m('data/rental/master-listing-registry.csv',candidatecols))
auditcols=[(key,'int64',key) for key in ['total_candidates','canonical_groups_including_unresolved','confirmed_duplicate_clusters','probable_duplicate_review_pairs','primary_properties','secondary_properties','excluded_canonical_groups','unresolved_candidate_rows']]
table('Audit',auditcols,'let\n Source = Json.Document(File.Contents(RepositoryRoot & "\\results\\rental-market-analysis.json")),\n Rows = Table.FromRecords({Source[counts]})\nin Rows')
tourcols=[('Year','int64','year'),('Passengers','int64','airport_passengers'),('Arrivals','int64','city_arrivals'),('GuestNights','int64','city_guest_nights'),('AirportSource','string','airport_source'),('CitySource','string','city_source')]
tour_m='let\n Source = Json.Document(File.Contents(RepositoryRoot & "\\data\\airport-city-annual.json")),\n Rows = Table.FromRecords(Source),\n Typed = Table.TransformColumnTypes(Rows, {{"year", Int64.Type},{"airport_passengers", Int64.Type},{"city_arrivals", Int64.Type},{"city_guest_nights", Int64.Type}})\nin Typed'
table('Tourism',tourcols,tour_m)
a=json.loads((ROOT/'data/assumptions.json').read_text(encoding='utf8'));r=json.loads((ROOT/'results/rental-market-analysis.json').read_text(encoding='utf8'))
acols=[(k,'double',k) for k in a];am='let\n Source = Json.Document(File.Contents(RepositoryRoot & "\\data\\assumptions.json")),\n Rows = Table.FromRecords({Source})\nin Rows';table('Assumptions',acols,am)
table('Strategy',[('Name','string','Name')],'#table(type table [Name=text], {{"Short-term"}, {"Long-term"}})')
table('RentBands',[('Lower','int64','Lower'),('Band','string','Band')],'#table(type table [Lower=Int64.Type, Band=text], {'+','.join('{'+str(x)+',"€'+str(x)+'–'+str(x+99)+'"}' for x in range(600,1300,100))+'})')
for name,values in [('RiskNights',BOOKING_SCENARIOS),('RiskADR',PRICE_SCENARIOS),('RiskRent',RENT_SCENARIOS),('RiskCost',INCREMENTAL_COST_SCENARIOS),('Setup',PREPARATION_SCENARIOS)]:
    table(name,[('Value','double','Value')],'#table(type table [Value=number], {'+','.join('{'+str(x)+'}' for x in values)+'})')
parameters=[('BookedNights',0,330,1,'booked_nights','#,0'),('ADR',50,250,1,'gross_nightly_eur',currency),('LTRRent',500,1500,25,None,currency),('HostFee',0,.30,.005,'host_fee','0.0%'),('Tax',0,.40,.01,'tax','0.0%'),('Cleaning',0,100,1,'cleaning_per_turnover',currency),('Stay',1,14,.5,'stay_nights','0.0'),('VariableCost',0,40,1,'other_variable_per_night',currency),('STRFixed',0,8000,100,None,currency),('LTRFixed',0,4000,100,'common_fixed',currency),('PaidMonths',0,12,1,'paid_months','0'),('Preparation',0,30000,500,None,currency)]
measures=[]
for name,lo,hi,step,key,fmt in parameters:
    dax=f'GENERATESERIES({lo}, {hi}, {step})'
    if name in ['HostFee','Tax']:dax=f'SELECTCOLUMNS(GENERATESERIES({lo}, {hi}, {step}), "Value", ROUND([Value], 3))'
    if name=='LTRRent':dax=f'DISTINCT(UNION(GENERATESERIES({lo}, {hi}, {step}), ROW("Value", CALCULATE(AVERAGE(Listings[Rent]), Listings[Cohort] = "primary"))))'
    table('P'+name,[('Value','double','[Value]')],dax=dax,column_format=fmt)
    fallback=f'MAX(Assumptions[{key}])' if key else {'LTRRent':'[Primary Mean All]','STRFixed':'MAX(Assumptions[common_fixed]) + MAX(Assumptions[str_incremental_fixed])','Preparation':'0'}[name]
    measures.append((name,f'SELECTEDVALUE(P{name}[Value], {fallback})',fmt))
def add(name,formula,fmt=currency):measures.append((name,formula,fmt))
add('Primary Count','COALESCE(CALCULATE(COUNTROWS(Listings), KEEPFILTERS(Listings[Cohort] = "primary")), 0)','#,0')
add('Primary Mean','CALCULATE(AVERAGE(Listings[Rent]), KEEPFILTERS(Listings[Cohort] = "primary"))')
add('Primary Median','CALCULATE(MEDIAN(Listings[Rent]), KEEPFILTERS(Listings[Cohort] = "primary"))')
add('Primary Mean All','CALCULATE(AVERAGE(Listings[Rent]), REMOVEFILTERS(Listings), Listings[Cohort] = "primary")')
add('Mean EUR per m2','CALCULATE(AVERAGE(Listings[RentPerM2]), KEEPFILTERS(Listings[Cohort] = "primary"))')
add('Candidate Count','CALCULATE(COUNTROWS(Candidates), REMOVEFILTERS(Candidates), REMOVEFILTERS(Listings))','#,0')
add('Primary Count All','CALCULATE(COUNTROWS(Listings), REMOVEFILTERS(Listings), Listings[Cohort] = "primary")','#,0')
add('Secondary Count All','CALCULATE(COUNTROWS(Listings), REMOVEFILTERS(Listings), Listings[Cohort] = "secondary")','#,0')
add('Excluded Count All','CALCULATE(COUNTROWS(Listings), REMOVEFILTERS(Listings), Listings[Cohort] = "excluded")','#,0')
add('Rent Band Count','VAR LowerBound = SELECTEDVALUE(RentBands[Lower]) RETURN CALCULATE(COUNTROWS(Listings), KEEPFILTERS(Listings[Cohort] = "primary"), KEEPFILTERS(Listings[Rent] >= LowerBound), KEEPFILTERS(Listings[Rent] < LowerBound + 100))','#,0')
add('STR Net','[BookedNights] * [ADR] * (1 - [HostFee] - [Tax]) - DIVIDE([BookedNights] * [Cleaning], [Stay]) - [BookedNights] * [VariableCost] - [STRFixed]')
add('LTR Net','[PaidMonths] * [LTRRent] * (1 - [Tax]) - [LTRFixed]')
add('Annual Difference','[STR Net] - [LTR Net]')
add('Night Contribution','[ADR] * (1 - [HostFee] - [Tax]) - DIVIDE([Cleaning], [Stay]) - [VariableCost]')
add('Break-even Nights','VAR Target = [LTR Net] + [STRFixed] + DIVIDE([Preparation],MAX(Assumptions[recovery_years])) RETURN IF([Night Contribution] > 0, MAX(0,ROUNDUP(DIVIDE(Target,[Night Contribution]),0)), BLANK())','#,0')
add('Break-even ADR','VAR Margin = 1 - [HostFee] - [Tax] RETURN IF([BookedNights] > 0 && Margin > 0, DIVIDE(DIVIDE([LTR Net] + [STRFixed] + DIVIDE([Preparation],MAX(Assumptions[recovery_years])),[BookedNights]) + DIVIDE([Cleaning],[Stay]) + [VariableCost],Margin),BLANK())')
add('Break-even LTR Rent','IF([PaidMonths] > 0 && [Tax] < 1, DIVIDE([STR Net] + [LTRFixed], [PaidMonths] * (1 - [Tax])), BLANK())')
add('Strategy Net','SWITCH(SELECTEDVALUE(Strategy[Name]), "Short-term", [STR Net], "Long-term", [LTR Net])')
add('STR Comparison','IF(SELECTEDVALUE(Strategy[Name]) = "Short-term", [STR Net])')
add('LTR Comparison','IF(SELECTEDVALUE(Strategy[Name]) = "Long-term", [LTR Net])')
add('Historical LTR','MAX(Assumptions[paid_months])*MAX(Assumptions[long_monthly])*(1-MAX(Assumptions[tax]))-MAX(Assumptions[common_fixed])')
add('Historical STR','MAX(Assumptions[booked_nights])*MAX(Assumptions[gross_nightly_eur])*(1-MAX(Assumptions[host_fee])-MAX(Assumptions[tax]))-DIVIDE(MAX(Assumptions[booked_nights])*MAX(Assumptions[cleaning_per_turnover]),MAX(Assumptions[stay_nights]))-MAX(Assumptions[booked_nights])*MAX(Assumptions[other_variable_per_night])-MAX(Assumptions[common_fixed])-MAX(Assumptions[str_incremental_fixed])')
add('Decision','VAR Gap=[Annual Difference] RETURN IF(ABS(Gap)<500, "Narrow scenario gap", IF(Gap>0,"STR leads / scenario","LTR leads / scenario"))','General')
add('Empty Sample','IF(ISBLANK([Primary Mean]), "No primary comparables match these filters.", "Selected primary comparables; asking rents, not signed contracts.")','General')
add('Guest Nights','SUM(Tourism[GuestNights])','#,0')
add('Airport Passengers','SUM(Tourism[Passengers])','#,0')
add('Guest Nights Index','DIVIDE([Guest Nights],CALCULATE([Guest Nights],REMOVEFILTERS(Tourism),Tourism[Year]=2019))*100','0.0')
add('Airport Index','DIVIDE([Airport Passengers],CALCULATE([Airport Passengers],REMOVEFILTERS(Tourism),Tourism[Year]=2019))*100','0.0')
add('Guest Nights YoY','VAR Y=SELECTEDVALUE(Tourism[Year]) VAR Prev=CALCULATE([Guest Nights],REMOVEFILTERS(Tourism),Tourism[Year]=Y-1) RETURN IF(NOT ISBLANK(Prev),DIVIDE([Guest Nights]-Prev,Prev))','0.0%;(0.0%)')
add('Airport YoY','VAR Y=SELECTEDVALUE(Tourism[Year]) VAR Prev=CALCULATE([Airport Passengers],REMOVEFILTERS(Tourism),Tourism[Year]=Y-1) RETURN IF(NOT ISBLANK(Prev),DIVIDE([Airport Passengers]-Prev,Prev))','0.0%;(0.0%)')
add('Heatmap Gap','VAR N=SELECTEDVALUE(RiskNights[Value]) VAR Price=SELECTEDVALUE(RiskADR[Value]) RETURN N*Price*(1-[HostFee]-[Tax])-N*(DIVIDE([Cleaning],[Stay])+[VariableCost])-[STRFixed]-[LTR Net]')
add('Heatmap Color','IF(SELECTEDVALUE(RiskNights[Value])=MAX(Assumptions[booked_nights]) && SELECTEDVALUE(RiskADR[Value])=MAX(Assumptions[gross_nightly_eur]),"'+C['gold']+'",IF([Heatmap Gap]>0,"'+C['pale_teal']+'","'+C['divider']+'"))','General')
add('Rent Sensitivity','[STR Net] - (MAX(Assumptions[paid_months])*SELECTEDVALUE(RiskRent[Value])*(1-[Tax])-[LTRFixed])')
add('Cost Sensitivity','[STR Net] + MAX(Assumptions[str_incremental_fixed]) - SELECTEDVALUE(RiskCost[Value]) - [LTR Net]')
add('Frontier ADR','VAR N=SELECTEDVALUE(RiskNights[Value]) RETURN DIVIDE(DIVIDE([LTR Net]+[STRFixed],N)+DIVIDE([Cleaning],[Stay])+[VariableCost],1-[HostFee]-[Tax])')
add('Setup Nights','VAR Target=[LTR Net]+[STRFixed]+DIVIDE(SELECTEDVALUE(Setup[Value]),MAX(Assumptions[recovery_years])) RETURN IF([Night Contribution]>0,ROUNDUP(DIVIDE(Target,[Night Contribution]),0))','#,0')
add('Screening Summary','FORMAT(MAX(Audit[total_candidates]),"0") & " candidates · " & FORMAT(MAX(Audit[canonical_groups_including_unresolved]),"0") & " record groups · " & FORMAT(MAX(Audit[confirmed_duplicate_clusters]),"0") & " duplicate clusters · " & FORMAT(MAX(Audit[probable_duplicate_review_pairs]),"0") & " probable pairs · " & FORMAT(MAX(Audit[primary_properties]),"0") & " primary / " & FORMAT(MAX(Audit[secondary_properties]),"0") & " secondary / " & FORMAT(MAX(Audit[excluded_canonical_groups]),"0") & " excluded. Physical total unknown."','General')
add('Risk Case Labels','"Conservative " & FORMAT(MIN(RiskNights[Value]),"0") & " nights × " & FORMAT(MIN(RiskADR[Value]),"€0") & " | Baseline " & FORMAT(MAX(Assumptions[booked_nights]),"0") & " × " & FORMAT(MAX(Assumptions[gross_nightly_eur]),"€0") & " | Optimistic " & FORMAT(MAX(RiskNights[Value]),"0") & " × " & FORMAT(MAX(RiskADR[Value]),"€0") & ". Stress cases, not forecasts."','General')
display_currency=['STR Net','LTR Net','Annual Difference','Primary Mean','Primary Median','Mean EUR per m2','LTRRent','ADR','Break-even ADR','Break-even LTR Rent']
for numeric_measure in display_currency:
    empty='No matches' if numeric_measure in ['Primary Mean','Primary Median','Mean EUR per m2'] else 'Not defined'
    add(numeric_measure+' Display',f'IF(NOT ISBLANK([{numeric_measure}]), FORMAT([{numeric_measure}], "{currency}"), "{empty}")','General')
table('Metrics',[('_','int64','_')],'#table(type table [_=Int64.Type], {{0}})',measures=measures)
put(MODEL/'definition/relationships.tmdl','relationship 0ac4dc73-3552-46b8-8e73-9f30205cc3b1\n\tfromColumn: Candidates.PropertyID\n\ttoColumn: Listings.PropertyID')
dump(DEF/'version.json',{'$schema':schema('versionMetadata','1.0.0'),'version':'2.0.0'})
dump(DEF/'report.json',{'$schema':schema('report','3.1.0'),'themeCollection':{'customTheme':{'name':'BergamoTheme.json','reportVersionAtImport':{'visual':'2.9.0','report':'3.1.0','page':'2.0.0'},'type':'RegisteredResources'}},'resourcePackages':[{'name':'RegisteredResources','type':'RegisteredResources','items':[{'name':'BergamoTheme.json','path':'BergamoTheme.json','type':'CustomTheme'}]}],'settings':{'useStylableVisualContainerHeader':True,'exportDataMode':'AllowSummarized','defaultDrillFilterOtherVisuals':True}})

# PBIR visual primitives. Text headings are editorial; every numeric callout is a measure.
def lit(v):
    value=('true' if v else 'false') if isinstance(v,bool) else str(v)+'D' if isinstance(v,(int,float)) else "'"+v.replace("'","''")+"'"
    return {'expr':{'Literal':{'Value':value}}}
def color(v):return {'solid':{'color':lit(v)}}
def props(**kw):return [{'properties':kw}]
def field(table,col,measure=False,aggregation=False):
    x={('Measure' if measure else 'Column'):{'Expression':{'SourceRef':{'Entity':table}},'Property':col}}
    return {'Aggregation':{'Expression':x,'Function':0}} if aggregation else x
def projection(table,col,measure=False,aggregation=False):return {'field':field(table,col,measure,aggregation),'queryRef':table+'.'+col,'nativeQueryRef':({'RiskNights':'Booked nights','RiskADR':'Nightly ADR'}.get(table,table+' '+col) if col=='Value' else col)}
PAGE_NAMES=['Overview','Rental Market','Simulator','Tourism Context','Sensitivity']
PAGE_IDS=['Executive','RentalMarket','Simulator','Tourism','Risk']
dump(DEF/'pages/pages.json',{'$schema':schema('pagesMetadata','1.0.0'),'pageOrder':PAGE_IDS,'activePageName':PAGE_IDS[0]})
z=0;current=None
def visual(kind,x,y,w,h,objects=None,roles=None,title=None,vco=None,identity=None):
    global z
    z+=1;name=identity or f'{current}_{z:03d}'
    v={'visualType':kind,'objects':objects or {},'visualContainerObjects':{'background':props(show=lit(False)),'border':props(show=lit(False)),'visualHeader':props(show=lit(False)),'visualTooltip':props(show=lit(True)),'padding':props(top=lit(8),bottom=lit(8),left=lit(8),right=lit(8))}}
    if title:v['visualContainerObjects']['title']=props(show=lit(True),text=lit(title),fontSize=lit(14),fontFamily=lit(FONT),fontColor=color(C['navy']))
    else:v['visualContainerObjects']['title']=props(show=lit(False))
    if vco:v['visualContainerObjects'].update(vco)
    if roles:v['query']={'queryState':{role:{'projections':[projection(*a) for a in fields]} for role,fields in roles.items()}}
    result={'$schema':schema('visualContainer','2.9.0'),'name':name,'position':{'x':x,'y':y,'z':z,'width':w,'height':h,'tabOrder':z},'visual':v}
    dump(DEF/f'pages/{current}/visuals/{name}/visual.json',result);return result
def text(txt,x,y,w,h,size=12,ink=None,bold=False,background=None,align='left'):
    run={'value':txt,'textStyle':{'fontFamily':FONT,'fontSize':f'{size}pt','color':ink or C['navy'],'fontWeight':'bold' if bold else 'normal'}}
    vco={'background':props(show=lit(bool(background)),color=color(background or C['surface']),transparency=lit(0)),'padding':props(top=lit(0),bottom=lit(0),left=lit(0),right=lit(0))}
    return visual('textbox',x,y,w,h,objects={'general':props(paragraphs=[{'textRuns':[run],'horizontalTextAlignment':align}]),'text':props(fontFamily=lit(FONT),fontSize=lit(size),color=color(ink or C['navy']))},vco=vco)
def callout(label,measure,x,y,w=255,size=32):
    text(label.upper(),x,y,w,24,10,C['blue'],True,align='center')
    label_measure=measure+' Display' if measure in display_currency else measure
    visual('card',x,y+25,w,40 if size<=24 else 64,objects={'labels':props(fontSize=lit(size),color=color(C['navy']),fontFamily=lit(FONT),labelDisplayUnits=lit(0)),'categoryLabels':props(show=lit(False))},roles={'Values':[('Metrics',label_measure,True)]},vco={'padding':props(top=lit(0),bottom=lit(0),left=lit(0),right=lit(0))})
def chart(kind,x,y,w,h,title,roles,objects=None):
    defaults={'legend':props(show=lit(False)),'categoryAxis':props(fontSize=lit(10),fontFamily=lit(FONT),labelColor=color(C['muted'])),'valueAxis':props(fontSize=lit(10),fontFamily=lit(FONT),labelColor=color(C['muted']))}
    if objects:defaults.update(objects)
    return visual(kind,x,y,w,h,defaults,roles,title)
def slicer(table_,col,label,x,y,w=240,mode='Dropdown'):
    obj={'data':props(mode=lit(mode)),'header':props(show=lit(True),text=lit(label)),'selection':props(singleSelect=lit(table_.startswith('P')),selectAllCheckboxEnabled=lit(False))}
    if table_.startswith('P'):
        name=table_[1:];key=next(t[4] for t in parameters if t[0]==name)
        default=a[key] if key else {'LTRRent':r['primary']['mean'],'STRFixed':a['common_fixed']+a['str_incremental_fixed'],'Preparation':0}[name]
        condition={'In':{'Expressions':[{'Column':{'Expression':{'SourceRef':{'Source':'p'}},'Property':col}}],'Values':[[{'Literal':{'Value':str(default)+'D'}}]]}}
        obj['general']=props(filter={'filter':{'Version':2,'From':[{'Name':'p','Entity':table_,'Type':0}],'Where':[{'Condition':condition}]}})
    return visual('slicer',x,y,w,82,objects=obj,roles={'Values':[(table_,col)]},vco={'background':props(show=lit(True),color=color(C['surface']),transparency=lit(0))})
def button(label,x,y,w,dest=None,action=None,active=False):
    obj={'text':[{'properties':{'show':lit(True)}},{'selector':{'id':'default'},'properties':{'text':lit(label),'fontSize':lit(11),'fontFamily':lit(FONT),'fontColor':color(C['navy'] if active else C['muted']),'horizontalAlignment':lit('center')}}],'fill':props(show=lit(True),fillColor=color(C['surface'] if active else C['canvas'])),'outline':props(show=lit(False)),'icon':props(show=lit(False)),'shape':props(tileShape=lit('rectangle'))}
    link={'show':lit(True),'type':lit('PageNavigation' if dest else action)}
    if dest:link['navigationSection']=lit(dest)
    return visual('actionButton',x,y,w,42,obj,vco={'visualLink':props(**link)})
def page(i,title,kicker,note):
    global current;current=PAGE_IDS[i]
    dump(DEF/f'pages/{current}/page.json',{'$schema':schema('page','2.0.0'),'name':current,'displayName':PAGE_NAMES[i],'displayOption':'FitToPage','width':1280,'height':800,'objects':{'background':props(color=color(C['canvas']),transparency=lit(0)),'outspace':props(color=color(C['canvas']),transparency=lit(0))}})
    text('',0,0,1280,128,11,C['pale_teal'],background=C['navy'])
    text('BERGAMO / RENTAL STRATEGIES',48,16,690,24,10,C['pale_teal'],True)
    text(kicker.upper(),900,16,332,24,10,C['pale_teal'])
    text(title,48,49,1150,60,27,C['surface'],True)
    for j,name in enumerate(PAGE_NAMES):button(f'{j+1:02}  {name}',48+j*237,140,226,PAGE_IDS[j],active=j==i)
    text(note,48,190,1184,36,10,C['muted'])
    text('PEDRAM KOJOURI  /  INDEPENDENT DATA ANALYTICS',48,762,650,24,9,C['muted'])
    text(f'RESEARCH SNAPSHOT 14 OCT 2026  /  {i+1:02}',884,762,350,24,9,C['muted'])
page(0,'More tourists. More profit?','Decision research','EVIDENCE-INFORMED BASELINE  •  Asking rents and scenario cash flows are different evidence types.')
callout('Short-term / annual net','STR Net',48,240,270)
callout('Long-term / annual net','LTR Net',358,240,270)
callout('STR minus LTR / year','Annual Difference',668,240,270)
chart('barChart',48,356,786,300,'A narrow annual cash difference',{'Category':[('Strategy','Name')],'Y':[('Metrics','STR Comparison',True),('Metrics','LTR Comparison',True)],'Tooltips':[('Metrics','BookedNights',True),('Metrics','ADR',True)]},{'labels':props(show=lit(True),labelDisplayUnits=lit(0),labelPrecision=lit(2))})
text('DECISION / NOT A FORECAST',884,252,338,28,10,C['muted'],True)
visual('card',884,290,340,100,{'labels':props(fontSize=lit(18),color=color(C['navy'])),'categoryLabels':props(show=lit(False))},roles={'Values':[('Metrics','Decision',True)]})
text('Tourism growth creates an opportunity. It does not establish a city-wide profit advantage. Preparation, paid months and operating costs can change the result.',884,405,338,150,12,C['navy'])
callout('Monthly rent benchmark','LTRRent',48,658,270,23)
callout('Booked nights','BookedNights',358,658,160,23)
callout('Gross ADR','ADR',568,658,160,23)
callout('Parity / booked nights','Break-even Nights',778,658,240,23)
page(1,'Rental market intelligence','Evidence, screened','Primary statistics use strict comparable properties. Filter the evidence; source links remain inspectable.')
pagepath=DEF/f'pages/{current}/page.json';pagedata=json.loads(pagepath.read_text());pagedata['filterConfig']={'filters':[{'name':'PrimaryCohort','field':field('Listings','Cohort'),'type':'Categorical','filter':{'Version':2,'From':[{'Name':'l','Entity':'Listings','Type':0}],'Where':[{'Condition':{'In':{'Expressions':[{'Column':{'Expression':{'SourceRef':{'Source':'l'}},'Property':'Cohort'}}],'Values':[[{'Literal':{'Value':"'primary'"}}]]}}}]},'howCreated':'User','isLockedInViewMode':True}]};dump(pagepath,pagedata)
slicer('Listings','Neighborhood','Neighborhood',48,230,270);slicer('Listings','Platform','Source platform',342,230,270);slicer('Listings','Area','Advertised floor area / m²',636,230,270,mode='Between')
button('Clear filters',930,250,290,action='ClearAllSlicers')
callout('Selected primary properties','Primary Count',48,326,255,28);callout('Mean monthly base rent','Primary Mean',354,326,255,28);callout('Median monthly base rent','Primary Median',662,326,255,28);callout('Mean EUR / advertised m²','Mean EUR per m2',974,326,250,28)
chart('columnChart',48,428,366,184,'Rent distribution / €100 bands',{'Category':[('RentBands','Lower')],'Y':[('Metrics','Rent Band Count',True)]},{'categoryAxis':props(axisType=lit('Categorical'),fontSize=lit(10),labelDisplayUnits=lit(0))})
chart('scatterChart',434,428,390,184,'Area (m²) vs monthly rent (€)',{'Category':[('Listings','PropertyID')],'X':[('Listings','Area',False,True)],'Y':[('Listings','Rent',False,True)]},{'categoryAxis':props(showAxisTitle=lit(False),start=lit(38),end=lit(68),fontSize=lit(10)),'valueAxis':props(showAxisTitle=lit(False),start=lit(600),end=lit(1300),fontSize=lit(10))})
chart('barChart',848,428,376,184,'Neighborhood / selected mean',{'Category':[('Listings','Neighborhood')],'Y':[('Metrics','Primary Mean',True)],'Tooltips':[('Metrics','Primary Count',True)]},{'categoryAxis':props(maxMarginFactor=lit(.5),fontSize=lit(10))})
visual('tableEx',48,619,1184,112,roles={'Values':[('Listings','PropertyID'),('Listings','Location'),('Listings','Area'),('Listings','Rent'),('Listings','Contract'),('Listings','URL')]},title='Property evidence / scroll or open direct source',objects={'grid':props(rowPadding=lit(2)),'total':props(totals=lit(False))})
visual('card',48,730,1184,26,objects={'labels':props(fontSize=lit(9),color=color(C['blue'])),'categoryLabels':props(show=lit(False))},roles={'Values':[('Metrics','Screening Summary',True)]},vco={'padding':props(top=lit(0),bottom=lit(0),left=lit(0),right=lit(0))})
page(2,'Test the investment assumptions','Interactive simulator','Single-value parameters recalculate the model. Clear selections restores the documented baseline measures.')
for i,(name,_,_,_,_,_) in enumerate(parameters):
    labels={'BookedNights':'Annual booked nights','ADR':'Gross nightly ADR (€)','LTRRent':'Monthly LTR base rent (€)','HostFee':'Host platform fee','Tax':'Eligible income tax','Cleaning':'Cleaning / turnover (€)','Stay':'Average stay (nights)','VariableCost':'Other variable / night (€)','STRFixed':'STR annual fixed cost (€)','LTRFixed':'LTR owner costs / year (€)','PaidMonths':'LTR paid months','Preparation':'Additional preparation (€)'}
    slicer('P'+name,'Value',labels[name],48+(i%3)*260,234+(i//3)*108,236)
button('Reset assumptions',876,232,348,action='ClearAllSlicers')
for i,(label,m) in enumerate([('STR net / year','STR Net'),('LTR net / year','LTR Net'),('Difference / year','Annual Difference'),('Parity nights incl. preparation','Break-even Nights'),('Parity ADR incl. preparation','Break-even ADR'),('Parity monthly LTR rent','Break-even LTR Rent')]):callout(label,m,872,291+i*69,354,24)
text('No owner-time deduction. Preparation uses five-year simple recovery. Non-positive contribution or zero bookings produces a blank threshold, not an invented answer.',48,692,785,52,11,C['muted'])
page(3,'Demand context. No causal shortcut.','Bergamo / BGY','Passengers are movements, not guests staying in Bergamo. Airport traffic is never converted into apartment bookings.')
chart('lineChart',48,236,730,330,'Growth since 2019 / index = 100',{'Category':[('Tourism','Year')],'Y':[('Metrics','Guest Nights Index',True),('Metrics','Airport Index',True)]},{'legend':props(show=lit(True)),'dataPoint':[{'selector':{'metadata':'Metrics.Guest Nights Index'},'properties':{'fill':color(C['teal'])}},{'selector':{'metadata':'Metrics.Airport Index'},'properties':{'fill':color(C['muted'])}}]})
chart('columnChart',804,236,420,330,'City guest nights / annual',{'Category':[('Tourism','Year')],'Y':[('Metrics','Guest Nights',True)],'Tooltips':[('Metrics','Guest Nights YoY',True)]},{'categoryAxis':props(axisType=lit('Categorical'),fontSize=lit(10))})
visual('tableEx',48,582,730,166,roles={'Values':[('Tourism','Year'),('Metrics','Guest Nights YoY',True),('Metrics','Airport YoY',True),('Tourism','AirportSource')]},title='Annual change / source traceability',objects={'grid':props(rowPadding=lit(2)),'total':props(totals=lit(False))})
text('2025 diverges: BGY passenger movements declined while city guest nights increased.\n\n2019–2024 city data: reconciled regional series. 2025: separately identified provincial release.\n\nHistorical tourism seasonality is context, not observed apartment occupancy.',812,593,408,158,11,C['muted'])
page(4,'Small changes can reverse the ranking','Sensitivity / risk','Stress cases are scenarios, not forecasts or confidence intervals. The selected-sample LTR mean anchors the comparison.')
matrix_fill={'solid':{'color':{'expr':field('Metrics','Heatmap Color',True)}}}
matrix_values=[{'selector':{'data':[{'dataViewWildcard':{'matchingOption':1}}],'metadata':'Metrics.Heatmap Gap'},'properties':{'fontSize':lit(15),'backColor':matrix_fill}}]
visual('pivotTable',48,236,555,286,roles={'Rows':[('RiskNights','Value')],'Columns':[('RiskADR','Value')],'Values':[('Metrics','Heatmap Gap',True)]},title='STR minus LTR / booked nights × ADR',objects={'subTotals':props(rowSubtotals=lit(False),columnSubtotals=lit(False)),'values':matrix_values})
chart('lineChart',627,236,597,286,'Parity frontier / required nightly ADR',{'Category':[('RiskNights','Value')],'Y':[('Metrics','Frontier ADR',True)]})
chart('columnChart',48,548,370,170,'Monthly LTR rent / cash gap',{'Category':[('RiskRent','Value')],'Y':[('Metrics','Rent Sensitivity',True)]})
chart('columnChart',446,548,370,170,'STR incremental cost / cash gap',{'Category':[('RiskCost','Value')],'Y':[('Metrics','Cost Sensitivity',True)]},{'categoryAxis':props(axisType=lit('Categorical'),fontSize=lit(10),labelDisplayUnits=lit(0))})
chart('columnChart',842,548,382,170,'Preparation / parity booked nights',{'Category':[('Setup','Value')],'Y':[('Metrics','Setup Nights',True)]},{'categoryAxis':props(axisType=lit('Categorical'),fontSize=lit(10),labelDisplayUnits=lit(0))})
visual('card',48,724,1184,30,objects={'labels':props(fontSize=lit(10),color=color(C['blue'])),'categoryLabels':props(show=lit(False))},roles={'Values':[('Metrics','Risk Case Labels',True)]},vco={'padding':props(top=lit(0),bottom=lit(0),left=lit(0),right=lit(0))})
print(json.dumps({'project':str(PBI/'Bergamo.pbip'),'pages':5,'measures':len(measures),'parameters':len(parameters),'visuals':z,'configured_local':args.configure_local}))
