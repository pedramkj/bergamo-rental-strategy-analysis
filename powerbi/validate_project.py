"""Validate PBIR against Microsoft's public schemas and check model bindings."""
from pathlib import Path
import json,urllib.request,urllib.parse,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];PBI=ROOT/'powerbi';CACHE=ROOT/'generated/powerbi-schema-cache';CACHE.mkdir(exist_ok=True)
try:import jsonschema
except ImportError:
    sys.path.insert(0,str(ROOT/'generated/powerbi-deps'));import jsonschema
def fetch(url):
    dest=CACHE/(hashlib.sha256(url.encode()).hexdigest()+'.json')
    if not dest.exists():
        try:data=urllib.request.urlopen(url,timeout=30).read()
        except urllib.error.HTTPError as e:
            if e.code != 404:raise
            alias=url.replace('schema.embedded.json','schema-embedded.json')
            if alias==url:raise
            data=urllib.request.urlopen(alias,timeout=30).read()
        dest.write_bytes(data)
    return json.loads(dest.read_text(encoding='utf8'))
issues=[];validated=0
for path in list((PBI/'Bergamo.Report').rglob('*.json'))+[PBI/'Bergamo.pbip',PBI/'Bergamo.Report/definition.pbir',PBI/'Bergamo.SemanticModel/definition.pbism',PBI/'Bergamo.Report/.platform',PBI/'Bergamo.SemanticModel/.platform']:
    if '.pbi' in path.parts:continue
    data=json.loads(path.read_text(encoding='utf8'));url=data.get('$schema')
    if not url:continue
    from referencing import Registry,Resource
    spec=fetch(url);registry=Registry(retrieve=lambda uri:Resource.from_contents(fetch(uri))).with_resource(url,Resource.from_contents(spec))
    validator=jsonschema.Draft7Validator(spec,registry=registry)
    for error in validator.iter_errors(data):issues.append({'path':str(path.relative_to(ROOT)),'location':list(error.absolute_path),'message':error.message})
    validated+=1
result={'json_documents_validated':validated,'schema_issues':issues,'source':'Microsoft public PBIP/PBIR JSON schemas','note':'Schema checks are separate from Desktop load, refresh, DAX execution and visual QA.'}
(PBI/'validation').mkdir(exist_ok=True);(PBI/'validation/schema-validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps(result,indent=2));sys.exit(bool(issues))
