"""Cross-check shipped editable artifacts with the canonical rental result."""
import json,unittest,zipfile,xml.etree.ElementTree as E
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class PublicationConsistencyTests(unittest.TestCase):
    def test_word_contains_current_statistics_and_historical_case(self):
        with zipfile.ZipFile(ROOT/'reports/Bergamo_Rental_Strategies_Complete_EN_v03.docx') as z:
            xml=E.fromstring(z.read('word/document.xml'));text=' '.join(xml.itertext())
        for token in ['894.29','6,677.83','133.33','6,732','96 candidate','14 primary']:self.assertIn(token,text)
        self.assertIn('Complete rental candidate reconciliation',text)
    def test_carousel_text_matches_new_case(self):
        with zipfile.ZipFile(ROOT/'publication/Bergamo_LinkedIn_Carousel_EN_Final.pptx') as z:
            text=' '.join(' '.join(E.fromstring(z.read(n)).itertext()) for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml'))
        for token in ['894.29','6,678','96 candidates','14 comparable properties','133.33']:self.assertIn(token,text)
        self.assertNotIn('21 records, 4 missing prices',text)
    def test_native_break_even_chart_and_workbook_agree(self):
        ns={'c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
        with zipfile.ZipFile(ROOT/'publication/Bergamo_LinkedIn_Carousel_EN_Final.pptx') as z:
            charts=[n for n in z.namelist() if '/charts/' in n and n.endswith('.xml')]
            self.assertEqual(len(charts),4)
            vals=[[float(v.text) for v in E.fromstring(z.read(n)).findall('.//c:ser/c:val//c:v',ns)] for n in charts]
            self.assertIn([183,202,221,240],vals)
            workbooks=[n for n in z.namelist() if n.startswith('ppt/embeddings/') and n.endswith('.xlsx')];self.assertEqual(len(workbooks),4)
            from io import BytesIO
            with zipfile.ZipFile(BytesIO(z.read('ppt/embeddings/chart-data-snapshot-004.xlsx'))) as wb:
                ss={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                numbers=[float(c.find('s:v',ss).text) for c in E.fromstring(wb.read('xl/worksheets/sheet1.xml')).findall('.//s:c',ss) if c.get('t') not in ['s','inlineStr'] and c.find('s:v',ss) is not None]
            for v in [183,202,221,240]:self.assertIn(v,numbers)
    def test_readme_internal_targets_exist(self):
        import re
        readme=(ROOT/'README.md').read_text(encoding='utf8')
        targets=re.findall(r'\]\(([^)]+)\)',readme)+re.findall(r'(?:href|src)="([^"]+)"',readme)
        for target in targets:
            if not re.match(r'https?://|#',target):self.assertTrue((ROOT/target.split('#')[0]).exists(),target)
if __name__=='__main__':unittest.main()
