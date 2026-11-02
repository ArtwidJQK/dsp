# -*- coding: utf-8 -*-
"""
Helper module for building LeTanDung_24150654_v2.docx
Provides OMML equation rendering, standard typography styles,
section management, table formatting, callout formatting, and comment injection.
"""

import os
import sys
import zipfile
import shutil
import copy
import re
import lxml.etree as ET
from latex2mathml.converter import convert
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"

# Load XSLT stylesheet for LaTeX -> MathML -> OMML
XSLT_PATH = os.path.join(os.path.dirname(__file__), "MML2OMML.XSL")
xslt_tree = ET.parse(XSLT_PATH)
xslt_transform = ET.XSLT(xslt_tree)

def latex_to_omml(latex_code):
    """Converts a LaTeX equation string to an OMML element (<m:oMath>)."""
    try:
        mathml = convert(latex_code)
        dom = ET.fromstring(mathml.encode('utf-8'))
        omml = xslt_transform(dom)
        root = omml.getroot()
        # Post-process: ensure <m:nary> has expression body inside <m:e>
        for nary in root.findall(f'.//{{{M_NS}}}nary'):
            e = nary.find(f'{{{M_NS}}}e')
            if e is not None and len(e) == 0:
                parent = nary.getparent()
                if parent is not None:
                    idx = parent.index(nary)
                    siblings = list(parent)[idx+1:]
                    for sib in siblings:
                        parent.remove(sib)
                        e.append(sib)
        xml_str = ET.tostring(root, encoding='utf-8')
        return parse_xml(xml_str)
    except Exception as e:
        print(f"Error converting LaTeX: {latex_code} -> {e}")
        omath = parse_xml(f'<m:oMath {nsdecls("m")}><m:r><m:t>{latex_code}</m:t></m:r></m:oMath>')
        return omath

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_table_borders(table, color="D0D5DD", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'  <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def make_table_responsive(table):
    """Enables repeated header, prevents row split across pages, and clears cell indents."""
    for i, row in enumerate(table.rows):
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        if i == 0:
            trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.first_line_indent = Pt(0)
                p.paragraph_format.left_indent = Pt(0)


import re

def append_formatted_runs(p, text, base_font_size=13, default_color=RGBColor(0, 0, 0), bold=False, italic=False):
    """
    Appends text runs to a paragraph while automatically converting math subscripts
    (such as f_0, f_1, f_2, 2f_0, 3f_0, 4f_0, 5f_0, F_s, T_s, f_max, T_frame, dev2, dev3, LocalFloor_k, Score_raw, W_N, f_peak, f_hyp, etc.)
    into true Word subscript runs (<w:vertAlign w:val="subscript"/>).
    """
    if not text:
        return

    # Convert unicode subscripts to standard underscore notation first
    uni_map = {'₀': '_0', '₁': '_1', '₂': '_2', '₃': '_3', '₄': '_4', '₅': '_5', 'ₘ': '_m', 'ₛ': '_s'}
    for k, v in uni_map.items():
        text = text.replace(k, v)

    # Pattern for known variable subscripts with optional integer prefix (e.g. 2f_0, 3f_0)
    sub_pattern = re.compile(
        r'(\b[0-9]*)(f|F|T|A|φ|phi|n|dev|r|h|X|k|m|W|Score|LocalFloor|log)_(0|1|2|3|4|5|m|s|max|Nyquist|target|interp|hyp|test|log|frame|cont|MIDI|count|w|k|N|raw|peak)\b|\b(dev)([23])\b',
        re.IGNORECASE
    )

    pos = 0
    for m in sub_pattern.finditer(text):
        start, end = m.span()
        if start > pos:
            normal_part = text[pos:start]
            r = p.add_run(normal_part)
            r.font.name = "Times New Roman"
            r.font.size = Pt(base_font_size)
            r.font.color.rgb = default_color
            r.bold = bold
            r.italic = italic

        g = m.groups()
        if g[1] is not None:
            prefix = g[0]
            base_var = g[1]
            sub_val = g[2]
            if prefix:
                r_pre = p.add_run(prefix)
                r_pre.font.name = "Times New Roman"
                r_pre.font.size = Pt(base_font_size)
                r_pre.font.color.rgb = default_color
                r_pre.bold = bold
                r_pre.italic = italic
        else:
            base_var = g[3]
            sub_val = g[4]

        # Base variable run (italicized for standard single-letter math variables)
        r_base = p.add_run(base_var)
        r_base.font.name = "Times New Roman"
        r_base.font.size = Pt(base_font_size)
        r_base.font.color.rgb = default_color
        r_base.bold = bold
        r_base.italic = True if base_var.lower() in ['f', 't', 'a', 'm', 'k', 'n', 'p', 'x', 'w'] else (True if base_var.lower() == 'dev' else italic)

        # Subscript run
        r_sub = p.add_run(sub_val)
        r_sub.font.name = "Times New Roman"
        r_sub.font.size = Pt(base_font_size)
        r_sub.font.color.rgb = default_color
        r_sub.bold = bold
        r_sub.italic = False
        r_sub.font.subscript = True

        pos = end

    if pos < len(text):
        remaining = text[pos:]
        r = p.add_run(remaining)
        r.font.name = "Times New Roman"
        r.font.size = Pt(base_font_size)
        r.font.color.rgb = default_color
        r.bold = bold
        r.italic = italic


def add_p(doc, text="", style='Normal', align=WD_ALIGN_PARAGRAPH.JUSTIFY, 
          space_before=0, space_after=6, line_spacing=1.3, indent=0.394, bold=False, italic=False):
    """
    Standard body paragraph adhering strictly to:
    Times New Roman 13pt, Black, 1.0cm first-line indent, 1.3 line spacing, 6pt after.
    Automatically formats math variable subscripts.
    """
    p = doc.add_paragraph(style=style)
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    if indent > 0:
        p.paragraph_format.first_line_indent = Inches(indent)
    
    # Enable widow/orphan control
    pPr = p._p.get_or_add_pPr()
    pPr.append(parse_xml(f'<w:widowControl {nsdecls("w")} w:val="true"/>'))
    
    if text:
        append_formatted_runs(p, text, base_font_size=13, default_color=RGBColor(0, 0, 0), bold=bold, italic=italic)
    return p

def add_heading_1(doc, text, is_chapter=True):
    p = doc.add_heading(text, level=1)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    if is_chapter:
        p.paragraph_format.page_break_before = True
    for r in p.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(16)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0, 0, 0)
    return p

def add_heading_2(doc, text):
    p = doc.add_heading(text, level=2)
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    for r in p.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0, 0, 0)
    return p

def add_heading_3(doc, text):
    p = doc.add_heading(text, level=3)
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    for r in p.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.italic = True
        r.font.color.rgb = RGBColor(0, 0, 0)
    return p

def ensure_caption_styles(doc):
    """Ensures FigureCaption and TableCaption styles exist in document."""
    styles = doc.styles
    for s_name in ['FigureCaption', 'TableCaption']:
        try:
            s = styles[s_name]
        except KeyError:
            s = styles.add_style(s_name, WD_STYLE_TYPE.PARAGRAPH)
            s.font.name = "Times New Roman"
            s.font.size = Pt(11)
            s.font.italic = True
            s.font.color.rgb = RGBColor(0, 0, 0)

def add_caption(doc, text, is_table=False):
    """
    Standard caption for table (above) or figure (below).
    11pt, Italic, Centered, Black, keep_with_next.
    Uses TableCaption style for tables and FigureCaption style for figures.
    """
    ensure_caption_styles(doc)
    style_name = 'TableCaption' if is_table else 'FigureCaption'
    p = doc.add_paragraph(style=style_name)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8 if is_table else 4)
    p.paragraph_format.space_after = Pt(4 if is_table else 10)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.italic = True
    r.font.bold = False
    r.font.color.rgb = RGBColor(0, 0, 0)
    return p

def add_figure_image(doc, img_path, caption_text, width_inches=5.8):
    """Inserts a figure image and its caption below."""
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(8)
    p_img.paragraph_format.space_after = Pt(2)
    p_img.paragraph_format.keep_with_next = True
    
    if os.path.exists(img_path):
        p_img.add_run().add_picture(img_path, width=Inches(width_inches))
    else:
        r = p_img.add_run(f"[HÌNH ẢNH: {os.path.basename(img_path)}]")
        r.bold = True
        r.font.color.rgb = RGBColor(180, 0, 0)
        
    add_caption(doc, caption_text, is_table=False)

def add_placeholder_box(doc, placeholder_text, caption_text=""):
    """Inserts a formal placeholder frame for missing real photos/spectrograms."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = tbl.rows[0].cells[0]
    c.width = Inches(6.3)
    set_cell_background(c, "F8F9FA")
    set_cell_margins(c, top=200, bottom=200, left=200, right=200)
    
    tcPr = c._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:top w:val="dashed" w:sz="6" w:space="0" w:color="888888"/>'
        f'  <w:bottom w:val="dashed" w:sz="6" w:space="0" w:color="888888"/>'
        f'  <w:left w:val="dashed" w:sz="6" w:space="0" w:color="888888"/>'
        f'  <w:right w:val="dashed" w:sz="6" w:space="0" w:color="888888"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Pt(0)
    p.paragraph_format.left_indent = Pt(0)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(f"[CẦN BỔ SUNG: {placeholder_text}]")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.bold = True
    r.font.color.rgb = RGBColor(160, 40, 40)
    
    if caption_text:
        add_caption(doc, caption_text, is_table=False)

def add_callout(doc, title, text):
    """
    Formatted callout note:
    Left border 3pt dark grey, light grey background, bold title, italic text.
    Replaces old 1-cell tables with all-caps sentences.
    """
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = tbl.rows[0].cells[0]
    c.width = Inches(6.3)
    set_cell_background(c, "F8F9FA")
    set_cell_margins(c, top=120, bottom=120, left=180, right=180)
    
    tcPr = c._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:left w:val="single" w:sz="24" w:space="0" w:color="333333"/>'
        f'  <w:top w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'  <w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = c.paragraphs[0]
    p.paragraph_format.first_line_indent = Pt(0)
    p.paragraph_format.left_indent = Pt(0)
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.2
    
    r_t = p.add_run(f"{title}: ")
    r_t.font.name = "Times New Roman"
    r_t.font.size = Pt(11.5)
    r_t.bold = True
    r_t.font.color.rgb = RGBColor(0, 0, 0)
    
    r_b = p.add_run(text)
    r_b.font.name = "Times New Roman"
    r_b.font.size = Pt(11.5)
    r_b.italic = True
    r_b.font.color.rgb = RGBColor(20, 20, 20)
    
    # spacing after table
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)

def add_code_block(doc, code_text):
    """Formats code blocks: Consolas 10pt, grey background, boxed, no proofing."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = tbl.rows[0].cells[0]
    c.width = Inches(6.3)
    set_cell_background(c, "F4F6F9")
    set_cell_margins(c, top=100, bottom=100, left=150, right=150)
    
    tcPr = c._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:left w:val="single" w:sz="4" w:space="0" w:color="D0D5DD"/>'
        f'  <w:top w:val="single" w:sz="4" w:space="0" w:color="D0D5DD"/>'
        f'  <w:right w:val="single" w:sz="4" w:space="0" w:color="D0D5DD"/>'
        f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="D0D5DD"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.first_line_indent = Pt(0)
    p.paragraph_format.left_indent = Pt(0)
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.05
    
    r = p.add_run(code_text)
    r.font.name = "Consolas"
    r.font.size = Pt(9.5)
    r.font.color.rgb = RGBColor(20, 30, 45)
    # noProof
    rPr = r._r.get_or_add_rPr()
    rPr.append(parse_xml(f'<w:noProof {nsdecls("w")}/>'))
    
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)

def add_equation_omml(doc, latex_str, eq_num_str):
    """
    2-column borderless table for equations:
    Col 1 (5.5 in = 7920 dxa): Centered OMML equation.
    Col 2 (0.8 in = 1152 dxa): Right-aligned equation number.
    Matching tblGrid and tcW = 9072 dxa total (6.3 inches).
    """
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    tblPr = tbl._tbl.tblPr
    tblGrid = OxmlElement('w:tblGrid')
    col1 = OxmlElement('w:gridCol')
    col1.set(qn('w:w'), '7920')
    col2 = OxmlElement('w:gridCol')
    col2.set(qn('w:w'), '1152')
    tblGrid.append(col1)
    tblGrid.append(col2)
    tbl._tbl.insert(tbl._tbl.index(tblPr) + 1, tblGrid)
    
    c1 = tbl.rows[0].cells[0]
    c2 = tbl.rows[0].cells[1]
    c1.width = Inches(5.5)
    c2.width = Inches(0.8)
    
    for c in [c1, c2]:
        set_cell_margins(c, top=40, bottom=40, left=40, right=40)
        tcPr = c._tc.get_or_add_tcPr()
        borders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'  <w:left w:val="none"/><w:right w:val="none"/><w:top w:val="none"/><w:bottom w:val="none"/>'
            f'</w:tcBorders>'
        )
        tcPr.append(borders)
        
    p1 = c1.paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p1.paragraph_format.first_line_indent = Pt(0)
    p1.paragraph_format.left_indent = Pt(0)
    p1.paragraph_format.space_before = Pt(2)
    p1.paragraph_format.space_after = Pt(2)
    
    omml_elem = latex_to_omml(latex_str)
    p1._p.append(omml_elem)
    
    p2 = c2.paragraphs[0]
    p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p2.paragraph_format.first_line_indent = Pt(0)
    p2.paragraph_format.left_indent = Pt(0)
    p2.paragraph_format.space_before = Pt(2)
    p2.paragraph_format.space_after = Pt(2)
    r2 = p2.add_run(f"({eq_num_str})")
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(11)
    r2.font.italic = True
    
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)

def add_toc_field(p, field_code):
    """Inserts a genuine Word field (e.g. TOC, SEQ, STYLEREF) into paragraph."""
    pPr = p._p.get_or_add_pPr()
    r1 = p.add_run()
    fld1 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
    r1._r.append(fld1)
    
    r2 = p.add_run()
    instr = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> {field_code} </w:instrText>')
    r2._r.append(instr)
    
    r3 = p.add_run()
    fld2 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="separate"/>')
    r3._r.append(fld2)
    
    r4 = p.add_run()
    fld3 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
    r4._r.append(fld3)

def inject_comments_to_docx(docx_path, comments_list):
    """
    Injects native Word comments into docx via XML manipulation.
    comments_list: list of dict(
        id=int, 
        author="Biên tập viên", 
        date="2026-10-06T12:00:00Z", 
        text="...", 
        search_target="..."
    )
    """
    tmp_path = docx_path + ".tmp.zip"
    shutil.copy2(docx_path, tmp_path)
    
    with zipfile.ZipFile(tmp_path, 'r') as zin, zipfile.ZipFile(docx_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
        # 1. Build comments.xml
        root_c = ET.Element(f'{{{W_NS}}}comments', nsmap={'w': W_NS})
        for c in comments_list:
            cid = str(c['id'])
            c_elem = ET.SubElement(root_c, f'{{{W_NS}}}comment', {
                f'{{{W_NS}}}id': cid,
                f'{{{W_NS}}}author': c.get('author', 'Biên tập viên'),
                f'{{{W_NS}}}date': c.get('date', '2026-10-06T12:00:00Z'),
                f'{{{W_NS}}}initials': 'BTV'
            })
            p = ET.SubElement(c_elem, f'{{{W_NS}}}p')
            r = ET.SubElement(p, f'{{{W_NS}}}r')
            t = ET.SubElement(r, f'{{{W_NS}}}t')
            t.text = c['text']
        comments_xml_bytes = ET.tostring(root_c, encoding='utf-8', xml_declaration=True)
        zout.writestr('word/comments.xml', comments_xml_bytes)
        
        # 2. Modify other files
        for item in zin.infolist():
            if item.filename == 'word/comments.xml':
                continue
            data = zin.read(item.filename)
            
            if item.filename == '[Content_Types].xml':
                root = ET.fromstring(data)
                has_override = False
                for child in root:
                    if child.get('PartName') == '/word/comments.xml':
                        has_override = True
                if not has_override:
                    new_ov = ET.SubElement(root, f'{{{CT_NS}}}Override', {
                        'PartName': '/word/comments.xml',
                        'ContentType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml'
                    })
                data = ET.tostring(root, encoding='utf-8', xml_declaration=True)
                
            elif item.filename == 'word/_rels/document.xml.rels':
                root = ET.fromstring(data)
                has_rel = False
                for child in root:
                    if child.get('Type') == 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments':
                        has_rel = True
                if not has_rel:
                    ET.SubElement(root, f'{{{REL_NS}}}Relationship', {
                        'Id': 'rIdComments',
                        'Type': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments',
                        'Target': 'comments.xml'
                    })
                data = ET.tostring(root, encoding='utf-8', xml_declaration=True)
                
            elif item.filename == 'word/document.xml':
                root = ET.fromstring(data)
                # Search and wrap targets
                for c in comments_list:
                    cid = str(c['id'])
                    target = c['search_target']
                    # Look through runs with matching text
                    found = False
                    for r in root.iter(f'{{{W_NS}}}r'):
                        for t in r.iter(f'{{{W_NS}}}t'):
                            if t.text and target in t.text:
                                p = r.getparent()
                                idx = p.index(r)
                                # Insert commentRangeStart before r
                                c_start = ET.Element(f'{{{W_NS}}}commentRangeStart', {f'{{{W_NS}}}id': cid})
                                c_end = ET.Element(f'{{{W_NS}}}commentRangeEnd', {f'{{{W_NS}}}id': cid})
                                c_ref_r = ET.Element(f'{{{W_NS}}}r')
                                c_ref = ET.SubElement(c_ref_r, f'{{{W_NS}}}commentReference', {f'{{{W_NS}}}id': cid})
                                
                                p.insert(idx, c_start)
                                p.insert(idx + 2, c_end)
                                p.insert(idx + 3, c_ref_r)
                                found = True
                                break
                        if found:
                            break
                data = ET.tostring(root, encoding='utf-8', xml_declaration=True)
                
            zout.writestr(item.filename, data)
            
    os.remove(tmp_path)
    print(f"Injected {len(comments_list)} native Word comments into {docx_path}")

def clean_all_subscripts_in_docx(docx_path):
    """
    Scans word/document.xml in docx and converts any remaining raw subscripts
    (such as f_0, 2f_0, 3f_0, 4f_0, 5f_0, F_s, T_frame, dev2, dev3, LocalFloor_k, Score_raw, W_N, f_peak, f_target, f₀, f₁, f₂, f₃)
    outside code blocks into native Word subscript runs (<w:vertAlign w:val="subscript"/>).
    """
    tmp_path = docx_path + ".sub_tmp.zip"
    shutil.copy2(docx_path, tmp_path)
    
    sub_pattern = re.compile(
        r'(\b[0-9]*)(f|F|T|A|φ|phi|n|dev|r|h|X|k|m|W|Score|LocalFloor|log)_(0|1|2|3|4|5|m|s|max|Nyquist|target|interp|hyp|test|log|frame|cont|MIDI|count|w|k|N|raw|peak)\b|\b(dev)([23])\b|([fFTkmn])([₀₁₂₃₄₅])',
        re.IGNORECASE
    )
    uni_map = {'₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4', '₅': '5'}
    
    with zipfile.ZipFile(tmp_path, 'r') as zin, zipfile.ZipFile(docx_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == 'word/document.xml':
                root = ET.fromstring(data)
                converted_count = 0
                for p in root.iter(f'{{{W_NS}}}p'):
                    pPr = p.find(f'{{{W_NS}}}pPr')
                    if pPr is not None:
                        pStyle = pPr.find(f'{{{W_NS}}}pStyle')
                        if pStyle is not None and 'Code' in pStyle.get(f'{{{W_NS}}}val', ''):
                            continue
                    
                    runs_to_replace = []
                    for r in list(p.iter(f'{{{W_NS}}}r')):
                        rPr = r.find(f'{{{W_NS}}}rPr')
                        if rPr is not None:
                            rFonts = rPr.find(f'{{{W_NS}}}rFonts')
                            if rFonts is not None:
                                ascii_f = rFonts.get(f'{{{W_NS}}}ascii', '')
                                if 'Consolas' in ascii_f or 'Courier' in ascii_f:
                                    continue
                            va = rPr.find(f'{{{W_NS}}}vertAlign')
                            if va is not None and va.get(f'{{{W_NS}}}val') == 'subscript':
                                continue
                        
                        t = r.find(f'{{{W_NS}}}t')
                        if t is None or not t.text:
                            continue
                        
                        if sub_pattern.search(t.text):
                            runs_to_replace.append((r, rPr, t.text))
                    
                    for r, rPr, text in runs_to_replace:
                        matches = list(sub_pattern.finditer(text))
                        if not matches:
                            continue
                        
                        new_runs = []
                        pos = 0
                        
                        def make_r(txt, is_sub=False, is_i=None):
                            nr = ET.Element(f'{{{W_NS}}}r')
                            if rPr is not None:
                                nr_pr = copy.deepcopy(rPr)
                            else:
                                nr_pr = ET.Element(f'{{{W_NS}}}rPr')
                            
                            if is_i is True:
                                if nr_pr.find(f'{{{W_NS}}}i') is None:
                                    nr_pr.append(ET.Element(f'{{{W_NS}}}i'))
                            elif is_i is False:
                                i_elem = nr_pr.find(f'{{{W_NS}}}i')
                                if i_elem is not None:
                                    nr_pr.remove(i_elem)
                            
                            if is_sub:
                                va = nr_pr.find(f'{{{W_NS}}}vertAlign')
                                if va is None:
                                    va = ET.Element(f'{{{W_NS}}}vertAlign')
                                    nr_pr.append(va)
                                va.set(f'{{{W_NS}}}val', 'subscript')
                                i_sub = nr_pr.find(f'{{{W_NS}}}i')
                                if i_sub is not None:
                                    nr_pr.remove(i_sub)
                            
                            nr.append(nr_pr)
                            nt = ET.SubElement(nr, f'{{{W_NS}}}t')
                            nt.text = txt
                            if txt.startswith(' ') or txt.endswith(' '):
                                nt.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
                            return nr
                        
                        for m in matches:
                            start, end = m.span()
                            if start > pos:
                                new_runs.append(make_r(text[pos:start]))
                            
                            g = m.groups()
                            if g[1] is not None:
                                prefix, var, sub = g[0], g[1], g[2]
                                if prefix:
                                    new_runs.append(make_r(prefix))
                                new_runs.append(make_r(var, is_i=True if len(var) == 1 else None))
                                new_runs.append(make_r(sub, is_sub=True))
                            elif g[3] is not None:
                                var, sub = g[3], g[4]
                                new_runs.append(make_r(var, is_i=True))
                                new_runs.append(make_r(sub, is_sub=True))
                            else:
                                var, sub = g[5], uni_map.get(g[6], g[6])
                                new_runs.append(make_r(var, is_i=True))
                                new_runs.append(make_r(sub, is_sub=True))
                            pos = end
                            converted_count += 1
                        
                        if pos < len(text):
                            new_runs.append(make_r(text[pos:]))
                        
                        if r in list(p):
                            idx = list(p).index(r)
                            p.remove(r)
                            for offset, nr in enumerate(new_runs):
                                p.insert(idx + offset, nr)
                
                data = ET.tostring(root, encoding='utf-8', xml_declaration=True)
                print(f"Cleaned and converted {converted_count} math subscripts in document XML.")
            zout.writestr(item.filename, data)
    
    os.remove(tmp_path)

print("v2_helpers module ready.")
