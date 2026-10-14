"""Guard the native report's binding, cohort and financial invariants."""
import json
import re
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PBI = ROOT / 'powerbi'

class PowerBITests(unittest.TestCase):
    def test_visual_native_reference_names_are_unique(self):
        # Duplicate Value references in a matrix pass schema checks but fail in Desktop.
        for path in (PBI / 'Bergamo.Report/definition/pages').rglob('visual.json'):
            visual = json.loads(path.read_text(encoding='utf8'))['visual']
            refs = [p['nativeQueryRef'] for role in visual.get('query', {}).get('queryState', {}).values() for p in role['projections']]
            self.assertEqual(len(refs), len(set(refs)), str(path.relative_to(ROOT)))

    def test_navigation_targets_and_primary_scope(self):
        pages_dir = PBI / 'Bergamo.Report/definition/pages'
        pages = json.loads((pages_dir / 'pages.json').read_text())['pageOrder']
        self.assertEqual(len(pages), 5)
        for page in pages:
            targets = []
            for path in (pages_dir / page).rglob('visual.json'):
                visual = json.loads(path.read_text(encoding='utf8'))['visual']
                for obj in visual.get('visualContainerObjects', {}).get('visualLink', []):
                    props = obj['properties']
                    if props.get('type', {}).get('expr', {}).get('Literal', {}).get('Value') == "'PageNavigation'":
                        targets.append(props['navigationSection']['expr']['Literal']['Value'].strip("'"))
            self.assertEqual(set(targets), set(pages))
        scope = json.loads((pages_dir / 'RentalMarket/page.json').read_text())['filterConfig']['filters'][0]
        self.assertTrue(scope['isLockedInViewMode'])
        self.assertIn("'primary'", json.dumps(scope))

    def test_actual_dax_results_match_all_python_cases(self):
        reference = json.loads((PBI / 'validation/python-reference.json').read_text())
        actual = json.loads((PBI / 'validation/desktop-dax-validation.json').read_text(encoding='utf-8-sig'))
        results = {case['case']: case['actual'] for case in actual['cases']}
        changed = {key for case in reference['cases'] for key in case['selections']}
        self.assertTrue(set(reference['defaults']) <= changed)
        self.assertEqual(actual['numerical_checks'], len(reference['cases']) * 6)
        for case in reference['cases']:
            for key, expected in case['expected'].items():
                observed = results[case['name']][key]
                if expected is None: self.assertIsNone(observed)
                else: self.assertAlmostEqual(observed, expected, places=6)
        self.assertAlmostEqual(results['baseline']['STR'], 6544.50, places=6)
        self.assertAlmostEqual(results['baseline']['LTR'], 6677.828571428572, places=6)
        self.assertAlmostEqual(results['historical900']['LTR'], 6732, places=6)
        self.assertEqual(results['zero_paid_months']['LTRRent'], None)

    def test_model_bindings_exist_and_measure_count(self):
        models = {}
        for path in (PBI / 'Bergamo.SemanticModel/definition/tables').glob('*.tmdl'):
            text = path.read_text(encoding='utf8')
            models[path.stem] = set(re.findall(r'^\tcolumn (.+)$', text, re.M)) | set(re.findall(r"^\tmeasure '(.+)' =", text, re.M))
        for path in (PBI / 'Bergamo.Report/definition/pages').rglob('visual.json'):
            visual = json.loads(path.read_text(encoding='utf8'))['visual']
            for role in visual.get('query', {}).get('queryState', {}).values():
                for projection in role['projections']:
                    table, column = projection['queryRef'].split('.', 1)
                    self.assertIn(column, models[table], str(path.relative_to(ROOT)))
        self.assertEqual(len(models), 25)
        self.assertEqual(len(models['Metrics']) - 1, 60)

    def test_saved_pbix_has_native_model_and_five_pages(self):
        with zipfile.ZipFile(PBI / 'Bergamo.pbix') as archive:
            self.assertIsNone(archive.testzip())
            self.assertIn('DataModel', archive.namelist())
            pages = json.loads(archive.read('Report/definition/pages/pages.json'))['pageOrder']
            self.assertEqual(pages, ['Executive','RentalMarket','Simulator','Tourism','Risk'])
            self.assertEqual(len([n for n in archive.namelist() if n.endswith('/visual.json')]),131)

if __name__ == '__main__': unittest.main()
