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

p_title = doc.add_paragraph("DANH MUC HINH (by Caption style):")
p_fld = doc.add_paragraph()
add_fld(p_fld, 'TOC \\t "Caption,1" \\h \\z')

# Add caption with style 'Caption'
p1 = doc.add_paragraph(style='Caption')
r1 = p1.add_run("Hình 2.1: Quá trình lấy mẫu tín hiệu")

p2 = doc.add_paragraph(style='Caption')
r2 = p2.add_run("Hình 2.2: Giản đồ xung I2S")

doc.save("test_caption_style.docx")
print("Saved test_caption_style.docx")
