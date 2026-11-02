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

p_tof = doc.add_paragraph("DANH MUC HINH:")
p_tof_field = doc.add_paragraph()
add_fld(p_tof_field, 'TOC \\h \\z \\c "Hình"')

p_tot = doc.add_paragraph("DANH MUC BANG:")
p_tot_field = doc.add_paragraph()
add_fld(p_tot_field, 'TOC \\h \\z \\c "Bảng"')

# Add Figure Caption with SEQ
p_fig1 = doc.add_paragraph()
r = p_fig1.add_run("Hình ")
add_fld(p_fig1, 'SEQ Hình \\* ARABIC')
r2 = p_fig1.add_run(": Sơ đồ hệ thống")

# Add Table Caption with SEQ
p_tbl1 = doc.add_paragraph()
r = p_tbl1.add_run("Bảng ")
add_fld(p_tbl1, 'SEQ Bảng \\* ARABIC')
r2 = p_tbl1.add_run(": Thông số kỹ thuật")

doc.save("test_seq_caption.docx")
print("Saved test_seq_caption.docx")
