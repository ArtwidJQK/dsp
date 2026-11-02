# -*- coding: utf-8 -*-
"""
Master Builder Script:
Generates LeTanDung_24150654.docx
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

import make_doc as md
import section_frontmatter
import section_ch1_ch2
import section_ch3_ch4
import section_ch5_ch7

def main():
    print("Initializing document...")
    doc = docx.Document()

    # Set page size to A4 and margins to: Top 2.0cm, Bottom 2.0cm, Left 3.0cm, Right 2.0cm
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(0.79)     # ~2.0 cm
    section.bottom_margin = Inches(0.79)  # ~2.0 cm
    section.left_margin = Inches(1.18)    # ~3.0 cm
    section.right_margin = Inches(0.79)   # ~2.0 cm

    # Header
    header = section.header
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hrun = hp.add_run("Báo cáo Tiểu luận DSP: Piano Chromatic Tuner | SV: Lê Tấn Dũng - MSSV: 24150654")
    hrun.font.name = "Times New Roman"
    hrun.font.size = Pt(8.5)
    hrun.font.italic = True
    hrun.font.color.rgb = RGBColor(120, 120, 120)

    # Footer
    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    frun = fp.add_run("Trang ")
    frun.font.name = "Times New Roman"
    frun.font.size = Pt(9)
    frun.font.color.rgb = RGBColor(100, 100, 100)
    
    f_p = fp._p
    fldSimple = OxmlElement('w:fldSimple')
    fldSimple.set(qn('w:instr'), 'PAGE')
    f_p.append(fldSimple)

    print("Building Frontmatter (Cover, Abstracts, Lists, Abbreviations)...")
    section_frontmatter.build_frontmatter(doc)

    print("Building Chapter 1 (Introduction) and Chapter 2 (Theories)...")
    section_ch1_ch2.build_ch1_ch2(doc)

    print("Building Chapter 3 (System Design) and Chapter 4 (Implementation)...")
    section_ch3_ch4.build_ch3_ch4(doc)

    print("Building Chapter 5 (Results), Chapter 6 (Evaluation), Chapter 7 (Conclusion), References & Appendices...")
    section_ch5_ch7.build_ch5_ch7(doc)

    output_path = r"d:\Xử lý tín hiệu số\LeTanDung_24150654.docx"
    print(f"Saving final document to: {output_path}")
    doc.save(output_path)
    
    size_bytes = os.path.getsize(output_path)
    print(f"DONE! File created successfully. Size: {size_bytes} bytes ({size_bytes/1024:.2f} KB)")

if __name__ == "__main__":
    main()
