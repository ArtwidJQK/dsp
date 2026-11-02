import docx
from docx.shared import Pt, Inches
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

doc = docx.Document()

def add_fld(p, code):
    r1 = p.add_run()
    r1._r.append(parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>'))
    r2 = p.add_run()
    r2._r.append(parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> {code} </w:instrText>'))
    r3 = p.add_run()
    r3._r.append(parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="separate"/>'))
    r4 = p.add_run()
    r4._r.append(parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>'))

# Test 1: By SEQ with Chapter
p1 = doc.add_paragraph("DANH MUC HINH (by SEQ):")
p1_fld = doc.add_paragraph()
add_fld(p1_fld, 'TOC \\h \\z \\c "Hình"')

# Test 2: By Style TableCaption and FigureCaption
p2 = doc.add_paragraph("DANH MUC HINH (by Style):")
p2_fld = doc.add_paragraph()
add_fld(p2_fld, 'TOC \\t "FigureCaption,1" \\h \\z')

p3 = doc.add_paragraph("DANH MUC BANG (by Style):")
p3_fld = doc.add_paragraph()
add_fld(p3_fld, 'TOC \\t "TableCaption,1" \\h \\z')

# Add custom styles if needed or paragraphs
styles = doc.styles
try:
    s_fig = styles.add_style('FigureCaption', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
    s_fig.font.name = 'Times New Roman'
    s_fig.font.size = Pt(11)
    s_fig.font.italic = True
except:
    pass

try:
    s_tbl = styles.add_style('TableCaption', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
    s_tbl.font.name = 'Times New Roman'
    s_tbl.font.size = Pt(11)
    s_tbl.font.italic = True
except:
    pass

# Add a figure caption
pf = doc.add_paragraph(style='FigureCaption')
rf = pf.add_run("Hình ")
add_fld(pf, 'SEQ Hình \\* ARABIC')
rf2 = pf.add_run(": Sơ đồ khối hệ thống")

# Add a table caption
pt = doc.add_paragraph(style='TableCaption')
rt = pt.add_run("Bảng ")
add_fld(pt, 'SEQ Bảng \\* ARABIC')
rt2 = pt.add_run(": Thông số kỹ thuật")

doc.save("test_tof_styles.docx")
print("Saved test_tof_styles.docx")
