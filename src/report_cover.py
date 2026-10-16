"""Approved native Word cover, isolated from all analytical pipelines.

The one-page asset contains native locked page anchors, editable text boxes,
vector rules/icons and an unmodified user image behind an opaque curved mask.
Word-generated DrawingML and its VML fallbacks are preserved together.
"""
from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile
from lxml import etree
from docx.shared import Mm, Inches
from docx.enum.section import WD_SECTION_START
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
TITLE = 'More Tourists, Why Not More Profit?'
ASSETS = ROOT / 'assets/report-cover'
REFERENCE = ASSETS / 'approved-reference.png'
TEMPLATE = ASSETS / 'native-cover.docx'


def cover_paragraph(image_relationship):
    """Copy the reviewed one-page native cover without importing its styles.

    Direct cover typography does not change research-body styles. The single
    picture relation and drawing IDs are remapped for insertion in the report.
    This helper never invokes the report builder or writes analytical assets.
    """
    with ZipFile(TEMPLATE) as archive:
        root = etree.fromstring(archive.read('word/document.xml'))
    p = deepcopy(root.find(qn('w:body')).find(qn('w:p')))
    for element in p.iter():
        for attribute in [qn('r:embed'), qn('r:id')]:
            if attribute in element.attrib:
                assert element.get(attribute) == 'rId4', 'Unexpected cover relation'
                element.set(attribute, image_relationship)
    for index, properties in enumerate(p.iter(qn('wp:docPr')), start=10000):
        properties.set('id', str(index))
    return p


def add_cover(document):
    """Reproduce the reviewed cover on future builds, without running one."""
    cover = document.sections[0]
    header, footer = deepcopy(cover.header._element), deepcopy(cover.footer._element)
    cover.page_width = Mm(210); cover.page_height = Mm(297)
    cover.top_margin = cover.bottom_margin = Inches(.65)
    cover.left_margin = cover.right_margin = Inches(.75)
    # Keep a one-cell structural cover container (the historical report's
    # 23 tables include this cover container). Anchor artwork outside the cell.
    document.add_table(rows=1, cols=1)
    rid, _ = document.part.get_or_add_image(str(REFERENCE))
    document._body._body.insert(len(document._body._body)-1, cover_paragraph(rid))
    body = document.add_section(WD_SECTION_START.NEW_PAGE)
    body.header.is_linked_to_previous = False
    body.footer.is_linked_to_previous = False
    for target, original in [(body.header._element,header), (body.footer._element,footer)]:
        for element in list(target): target.remove(element)
        for element in original: target.append(deepcopy(element))
    from docx.opc.constants import RELATIONSHIP_TYPE as RT
    for link in body.header._element.iter(qn('w:hyperlink')):
        link.set(qn('r:id'), body.header.part.relate_to('https://www.linkedin.com/in/pedram-kojouri/',RT.HYPERLINK,is_external=True))
    for target in [document.sections[0].header._element,document.sections[0].footer._element]:
        for element in list(target): target.remove(element)
        target.append(OxmlElement('w:p'))
    body.page_width = Mm(210); body.page_height = Mm(297)
    body.top_margin = body.bottom_margin = Inches(.7)
    body.left_margin = body.right_margin = Inches(.8)
    page_number=OxmlElement('w:pgNumType');page_number.set(qn('w:start'),'1');body._sectPr.append(page_number)
    document.core_properties.title = TITLE
    return body
