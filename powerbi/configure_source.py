"""Configure this clone's sole Power Query path without regenerating visuals."""
from pathlib import Path
import argparse,re
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=root);a=p.parse_args()
target=root/'powerbi/Bergamo.SemanticModel/definition/expressions.tmdl'
value=str(a.root.resolve()).replace('"','""')
text=target.read_text(encoding='utf8');text,n=re.subn(r'(?m)^expression RepositoryRoot = "(?:[^"]|"")*"',lambda _:f'expression RepositoryRoot = "{value}"',text)
if n!=1:raise ValueError('Expected exactly one documented RepositoryRoot expression')
if not (a.root/'data/rental/canonical-properties.csv').exists():raise FileNotFoundError('Root must be the repository checkout containing data/rental')
target.write_text(text,encoding='utf8');print('Configured RepositoryRoot. Open Bergamo.pbip and Refresh in Power BI Desktop.')
