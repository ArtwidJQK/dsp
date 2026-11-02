# -*- coding: utf-8 -*-
"""
Full Academic Report Generator for:
PIANO CHROMATIC TUNER USING ESP32-S3 AND INMP441
Student: Le Tan Dung - MSSV: 24150654
File: LeTanDung_24150654.docx
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def create_document():
    doc = docx.Document()
    
    # Page setup: A4, Margins: Top 2.0cm, Bottom 2.0cm, Left 3.0cm, Right 2.0cm
    section = doc.sections[0]
    section.page_width = Inches(8.27)   # A4 width
    section.page_height = Inches(11.69) # A4 height
    section.top_margin = Inches(0.79)     # 2.0 cm
    section.bottom_margin = Inches(0.79)  # 2.0 cm
    section.left_margin = Inches(1.18)    # 3.0 cm
    section.right_margin = Inches(0.79)   # 2.0 cm
    
    # Configure Header & Footer
    header = section.header
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hrun = hp.add_run("Báo cáo Tiểu luận DSP: Piano Chromatic Tuner | SV: Lê Tấn Dũng - MSSV: 24150654")
    hrun.font.name = "Times New Roman"
    hrun.font.size = Pt(8.5)
    hrun.font.italic = True
    hrun.font.color.rgb = RGBColor(120, 120, 120)
    
    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    frun = fp.add_run("Trang ")
    frun.font.name = "Times New Roman"
    frun.font.size = Pt(9)
    frun.font.color.rgb = RGBColor(100, 100, 100)
    
    # Add page number XML to footer
    f_p = fp._p
    fldSimple = OxmlElement('w:fldSimple')
    fldSimple.set(qn('w:instr'), 'PAGE')
    f_p.append(fldSimple)
    
    return doc

print("Document setup initialized.")
