"""Editable A4 editorial cover with original schematic architectural artwork."""
from copy import deepcopy
from pathlib import Path
from PIL import Image, ImageDraw
from docx.shared import Inches, Mm, Pt, RGBColor
from docx.enum.section import WD_SECTION_START
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parents[1]
NAVY='101C30';IVORY='F7F5F0';TEAL='2F7776';GOLD='C6A46C'

def artwork():
    # Conceptual architecture, deliberately not a surveyed or photographic skyline.
    paths=[[(0,206),(1100,206)],[(10,185),(80,167),(180,175),(240,154),(365,165),(420,140),(555,150),(625,128),(700,150),(780,127),(875,147),(980,164),(1090,176)],
        [(75,180),(75,107),(135,107),(135,180)],[(135,180),(135,129),(213,129),(213,180)],[(247,169),(247,83),(286,83),(286,59),(312,59),(312,83),(350,83),(350,169)],
        [(392,153),(392,102),(425,77),(458,102),(458,153)],[(469,151),(469,115),(552,115),(552,151)],
        [(580,141),(580,67),(600,67),(600,36),(615,21),(630,36),(630,67),(650,67),(650,141)],
        [(682,151),(682,100),(736,75),(790,100),(790,151)],[(809,147),(809,104),(867,104),(867,147)],[(903,159),(903,124),(963,124),(963,159)]]
    for x,y in [(94,128),(270,110),(309,110),(593,92),(619,92),(707,111),(748,111),(826,121),(916,138)]:
        paths.append([(x,y+14),(x,y),(x+10,y),(x+10,y+14)])
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="2200" height="440" viewBox="0 0 1100 220">',f'<rect width="1100" height="220" fill="#{NAVY}"/>',f'<g fill="none" stroke="#{GOLD}" stroke-width="1.35" stroke-linejoin="miter">']
    image=Image.new('RGB',(2200,440),'#'+NAVY);draw=ImageDraw.Draw(image)
    for line in paths:
        svg.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in line)+'"/>')
        draw.line([(x*2,y*2) for x,y in line],fill='#'+GOLD,width=3)
    svg.extend(['</g>','</svg>'])
    folder=ROOT/'figures';folder.mkdir(exist_ok=True)
    (folder/'bergamo-cover-art.svg').write_text('\n'.join(svg),encoding='utf8')
    image.save(folder/'bergamo-cover-art.png')
    return folder/'bergamo-cover-art.png'

def add_cover(document):
    cover=document.sections[0]
    cover.page_width=Mm(210);cover.page_height=Mm(297)
    cover.top_margin=cover.bottom_margin=Inches(.65)
    cover.left_margin=cover.right_margin=Inches(.75)
    header=deepcopy(cover.header._element);footer=deepcopy(cover.footer._element)
    table=document.add_table(rows=1,cols=1);table.autofit=False;table.columns[0].width=Inches(6.75)
    cell=table.cell(0,0);pr=cell._tc.get_or_add_tcPr()
    sh=OxmlElement('w:shd');sh.set(qn('w:fill'),NAVY);pr.append(sh)
    margins=OxmlElement('w:tcMar')
    for edge,value in [('top','400'),('bottom','400'),('left','380'),('right','380')]:
        el=OxmlElement('w:'+edge);el.set(qn('w:w'),value);el.set(qn('w:type'),'dxa');margins.append(el)
    pr.append(margins)
    def paragraph(text,size=12,color=IVORY,bold=False,before=0,after=12):
        p=cell.add_paragraph() if cell.paragraphs[0].text else cell.paragraphs[0]
        p.paragraph_format.space_before=Pt(before);p.paragraph_format.space_after=Pt(after)
        p.paragraph_format.line_spacing=1.05
        r=p.add_run(text);r.font.name='Calibri';r.font.size=Pt(size);r.font.bold=bold;r.font.color.rgb=RGBColor.from_string(color)
        return p
    paragraph('INDEPENDENT RESEARCH\nBERGAMO, ITALY',9,GOLD,True,after=42)
    paragraph('MORE TOURISTS,\nMORE PROFIT?',36,IVORY,True,after=22)
    paragraph('A Data-Driven Business Case Study on\nRental Profitability in Bergamo',16,IVORY,False,after=20)
    paragraph('Short-Term Rentals vs\nLong-Term Residential Leasing',12,'B3C7C7',False,after=48)
    p=cell.add_paragraph();p.paragraph_format.space_after=Pt(8);p.add_run().add_picture(str(artwork()),width=Inches(6.0))
    paragraph('Original schematic architecture inspired by Bergamo',8,'B3C7C7',after=45)
    paragraph('Pedram Kojouri',22,IVORY,True,after=9)
    paragraph('Independent Data Analytics Portfolio Project',11,GOLD,after=8)
    paragraph('October 2026',11,IVORY,after=32)
    paragraph('Tourism Demand | Rental Economics\nFinancial Modelling | Business Decision-Making',9,'B3C7C7',after=0)
    body=document.add_section(WD_SECTION_START.NEW_PAGE)
    cover=document.sections[0]
    body.header.is_linked_to_previous=False;body.footer.is_linked_to_previous=False
    for target,original in [(body.header._element,header),(body.footer._element,footer)]:
        for element in list(target):target.remove(element)
        for element in original:target.append(deepcopy(element))
    from docx.opc.constants import RELATIONSHIP_TYPE as RT
    for link in body.header._element.iter(qn('w:hyperlink')):
        link.set(qn('r:id'),body.header.part.relate_to('https://www.linkedin.com/in/pedram-kojouri/',RT.HYPERLINK,is_external=True))
    for target in [cover.header._element,cover.footer._element]:
        for element in list(target):target.remove(element)
        target.append(OxmlElement('w:p'))
    body.page_width=Mm(210);body.page_height=Mm(297)
    body.top_margin=body.bottom_margin=Inches(.7);body.left_margin=body.right_margin=Inches(.8)
    page_number=OxmlElement('w:pgNumType');page_number.set(qn('w:start'),'1');body._sectPr.append(page_number)
    return body
