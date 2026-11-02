# -*- coding: utf-8 -*-
"""
Master Builder for LeTanDung_24150654_v2.docx
Implements all technical editing and formatting overhaul requirements (Sections A to H).
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
import lxml.etree as ET
from latex2mathml.converter import convert

# Load XSLT stylesheet for LaTeX -> MathML -> OMML
xslt_tree = ET.parse("MML2OMML.XSL")
xslt_transform = ET.XSLT(xslt_tree)

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"

def latex_to_omml(latex_code):
    """Converts a LaTeX equation string to an OMML element (<m:oMath>)."""
    try:
        mathml = convert(latex_code)
        dom = ET.fromstring(mathml.encode('utf-8'))
        omml = xslt_transform(dom)
        root = omml.getroot()
        # Ensure root is an oMath or wrapped
        return root
    except Exception as e:
        print(f"Error converting LaTeX: {latex_code} -> {e}")
        # fallback simple run
        omath = ET.Element(f"{{{M_NS}}}oMath")
        r = ET.SubElement(omath, f"{{{M_NS}}}r")
        t = ET.SubElement(r, f"{{{M_NS}}}t")
        t.text = latex_code
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

def add_equation_omml(doc, latex_str, eq_num_str):
    """
    Creates a 2-column borderless table for the equation.
    Col 1 (5.5 in = 7920 dxa): Centered OMML equation.
    Col 2 (0.8 in = 1152 dxa): Right-aligned equation number.
    Matching tblGrid and tcW.
    """
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    # Set tblGrid
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
    
    # Remove borders & set padding
    for c in [c1, c2]:
        set_cell_margins(c, top=40, bottom=40, left=40, right=40)
        tcPr = c._tc.get_or_add_tcPr()
        borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="none"/><w:right w:val="none"/><w:top w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
        tcPr.append(borders)
        
    p1 = c1.paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p1.paragraph_format.space_before = Pt(2)
    p1.paragraph_format.space_after = Pt(2)
    
    # Insert OMML element
    omml_elem = latex_to_omml(latex_str)
    p1._p.append(omml_elem)
    
    p2 = c2.paragraphs[0]
    p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p2.paragraph_format.space_before = Pt(2)
    p2.paragraph_format.space_after = Pt(2)
    r2 = p2.add_run(f"({eq_num_str})")
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(11.5)
    r2.font.italic = True
    
    # Spacing after table
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)

print("Base mathematical helpers defined.")
