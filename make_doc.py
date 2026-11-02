# -*- coding: utf-8 -*-
"""
Full Academic Report Generator: LeTanDung_24150654.docx
Project: PIANO CHROMATIC TUNER USING ESP32-S3 AND INMP441
Author: Le Tan Dung - MSSV: 24150654
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

# Colors
C_NAVY = RGBColor(27, 54, 93)      # #1B365D - Deep Navy for Headings
C_GOLD = RGBColor(197, 160, 89)    # #C5A059 - Muted Gold Accent
C_TEXT = RGBColor(30, 30, 30)      # #1E1E1E - Dark Charcoal Body Text
C_MUTED = RGBColor(100, 100, 100)  # #646464 - Muted Grey
C_BLUE = RGBColor(31, 78, 120)     # #1F4E78 - Medium Navy

HEX_HEADER_BG = "1B365D"
HEX_ZEBRA_BG = "F7F9FC"
HEX_CALLOUT_BG = "F4F6F9"
HEX_CALLOUT_BORDER = "1B365D"
HEX_WARN_BG = "FFFBEA"
HEX_WARN_BORDER = "D97706"

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

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

def add_p(doc, text="", style=None, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=4, line_spacing=1.25, indent=0.4):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    if indent and align == WD_ALIGN_PARAGRAPH.JUSTIFY:
        p.paragraph_format.first_line_indent = Inches(indent)
    if text:
        run = p.add_run(text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(13)
        run.font.color.rgb = C_TEXT
    return p

def add_run(p, text, bold=False, italic=False, color=C_TEXT, size=13):
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(size)
    r.bold = bold
    r.italic = italic
    r.font.color.rgb = color
    return r

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(15.5)
    r.bold = True
    r.font.color.rgb = C_NAVY
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.bold = True
    r.font.color.rgb = C_BLUE
    return p

def add_heading_3(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.bold = True
    r.italic = True
    r.font.color.rgb = C_TEXT
    return p

def add_callout(doc, title, text, alert_type="note"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    cell = tbl.rows[0].cells[0]
    cell.width = Inches(6.3)
    
    bg_color = HEX_WARN_BG if alert_type == "warn" else HEX_CALLOUT_BG
    border_color = HEX_WARN_BORDER if alert_type == "warn" else HEX_CALLOUT_BORDER
    
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>'
        f'  <w:top w:val="none"/>'
        f'  <w:bottom w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    cp = cell.paragraphs[0]
    cp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    cp.paragraph_format.space_before = Pt(2)
    cp.paragraph_format.space_after = Pt(2)
    cp.paragraph_format.line_spacing = 1.2
    
    if title:
        r_title = cp.add_run(f"[{title}] ")
        r_title.bold = True
        r_title.font.name = "Times New Roman"
        r_title.font.size = Pt(12)
        r_title.font.color.rgb = RGBColor(180, 83, 9) if alert_type == "warn" else C_NAVY
        
    r_body = cp.add_run(text)
    r_body.font.name = "Times New Roman"
    r_body.font.size = Pt(12)
    r_body.italic = True
    r_body.font.color.rgb = C_TEXT
    
    # spacing after table
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)

def add_equation(doc, eq_text, eq_num):
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    cell_eq = tbl.rows[0].cells[0]
    cell_num = tbl.rows[0].cells[1]
    
    cell_eq.width = Inches(5.5)
    cell_num.width = Inches(0.8)
    
    for c in [cell_eq, cell_num]:
        set_cell_margins(c, top=60, bottom=60, left=60, right=60)
        tcPr = c._tc.get_or_add_tcPr()
        borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="none"/><w:right w:val="none"/><w:top w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
        tcPr.append(borders)
        
    p1 = cell_eq.paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p1.paragraph_format.space_before = Pt(2)
    p1.paragraph_format.space_after = Pt(2)
    r1 = p1.add_run(eq_text)
    r1.font.name = "Cambria Math"
    r1.font.size = Pt(12.5)
    r1.bold = True
    r1.font.color.rgb = C_TEXT
    
    p2 = cell_num.paragraphs[0]
    p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p2.paragraph_format.space_before = Pt(2)
    p2.paragraph_format.space_after = Pt(2)
    r2 = p2.add_run(f"({eq_num})")
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(12)
    r2.font.italic = True
    r2.font.color.rgb = C_MUTED
    
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(2)

def add_custom_table(doc, headers, rows_data, col_widths, title=""):
    if title:
        tp = doc.add_paragraph()
        tp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        tp.paragraph_format.space_before = Pt(6)
        tp.paragraph_format.space_after = Pt(3)
        tp.paragraph_format.keep_with_next = True
        r = tp.add_run(title)
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.color.rgb = C_NAVY

    table = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table)

    # Header Row
    hdr_cells = table.rows[0].cells
    for i, header_text in enumerate(headers):
        hdr_cells[i].width = Inches(col_widths[i])
        set_cell_background(hdr_cells[i], HEX_HEADER_BG)
        set_cell_margins(hdr_cells[i], top=100, bottom=100, left=120, right=120)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(header_text)
        run.bold = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(255, 255, 255)

    # Data Rows
    for r_idx, row_values in enumerate(rows_data):
        row_cells = table.rows[r_idx + 1].cells
        bg_col = HEX_ZEBRA_BG if (r_idx % 2 == 1) else "FFFFFF"
        for c_idx, val in enumerate(row_values):
            row_cells[c_idx].width = Inches(col_widths[c_idx])
            set_cell_background(row_cells[c_idx], bg_col)
            set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=100, right=100)
            p = row_cells[c_idx].paragraphs[0]
            # If numeric or short, center; else left
            is_num = any(char.isdigit() for char in str(val)) and len(str(val)) < 25
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if is_num else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            run = p.add_run(str(val))
            run.font.name = "Times New Roman"
            run.font.size = Pt(11)
            run.font.color.rgb = C_TEXT

    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(6)

print("make_doc base infrastructure ready.")
