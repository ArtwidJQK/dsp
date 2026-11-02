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

p_f_hdr = doc.add_paragraph("DANH MUC HINH:")
p_f_tof = doc.add_paragraph()
add_fld(p_f_tof, 'TOC \\t "FigureCaption,1" \\h \\z')

p_t_hdr = doc.add_paragraph("DANH MUC BANG:")
p_t_tof = doc.add_paragraph()
add_fld(p_t_tof, 'TOC \\t "TableCaption,1" \\h \\z')

# Add figure
pf1 = doc.add_paragraph(style='FigureCaption')
pf1.add_run("Hình 2.1: Quá trình lấy mẫu tín hiệu")

pf2 = doc.add_paragraph(style='FigureCaption')
pf2.add_run("Hình 2.2: Giản đồ xung I2S")

# Add table
pt1 = doc.add_paragraph(style='TableCaption')
pt1.add_run("Bảng 1.1: Bảng quy đổi sai số cent")

pt2 = doc.add_paragraph(style='TableCaption')
pt2.add_run("Bảng 3.1: Bảng kết nối chân phần cứng")

doc.save("test_fig_tbl_styles.docx")
print("Saved test_fig_tbl_styles.docx")
