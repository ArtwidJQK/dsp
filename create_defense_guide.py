# -*- coding: utf-8 -*-
"""
Builder Script for: bao_ve_bai_lam.docx & bao_ve_bai_lam.pdf
Tài liệu hướng dẫn vấn đáp và bảo vệ tiểu luận môn học DSP:
"Piano Chromatic Tuner using ESP32-S3 and INMP441"
Sinh viên thực hiện: Lê Tấn Dũng (MSSV: 24150654)
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

import v2_helpers as vh

DOCX_OUT = r"D:\dsp\LeTanDung_24150654\bao_ve_bai_lam.docx"
DOCX_WORKSPACE = r"D:\Xử lý tín hiệu số\bao_ve_bai_lam.docx"
PDF_OUT  = r"D:\dsp\LeTanDung_24150654\bao_ve_bai_lam.pdf"

# Color Palette
CLR_PRIMARY = "1B365D"    # Deep Navy
CLR_SECONDARY = "2B6CB0"  # Steel Blue
CLR_GOAL_BG = "FFF5F5"    # Soft Red Tint for Teacher Traps
CLR_GOAL_BORDER = "E53E3E"
CLR_ANS_BG = "F0FFF4"     # Soft Green Tint for Perfect Answer
CLR_ANS_BORDER = "38A169"
CLR_TECH_BG = "F7FAFC"    # Soft Grey Tint for Technical Evidence
CLR_TECH_BORDER = "4A5568"
CLR_TIP_BG = "FEFCBF"     # Soft Yellow Tint for Defense Tips
CLR_TIP_BORDER = "D69E2E"

def add_callout_box(doc, title, content_paragraphs, border_color="1B365D", bg_color="F7FAFC", title_color="1B365D"):
    """Creates a beautifully styled callout box with a colored left accent border."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    vh.set_cell_margins(cell, top=100, bottom=100, left=160, right=140)
    vh.set_cell_background(cell, bg_color)
    
    # Left thick border, no other borders
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:left w:val="single" w:sz="36" w:space="0" w:color="{border_color}"/>'
        f'  <w:top w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'  <w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    # Title paragraph
    p0 = cell.paragraphs[0]
    p0.paragraph_format.space_before = Pt(0)
    p0.paragraph_format.space_after = Pt(4)
    p0.paragraph_format.line_spacing = 1.15
    p0.paragraph_format.first_line_indent = Pt(0)
    r_title = p0.add_run(title)
    r_title.font.name = "Times New Roman"
    r_title.font.size = Pt(11)
    r_title.bold = True
    r_title.font.color.rgb = RGBColor.from_string(title_color)
    
    # Content paragraphs
    for p_text in content_paragraphs:
        p = cell.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.2
        p.paragraph_format.first_line_indent = Pt(0)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        # Format runs
        vh.append_formatted_runs(p, p_text, base_font_size=11, default_color=RGBColor(40, 40, 40))
        
    # Spacer
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)

def add_q_header(doc, q_num, q_title, category="", priority=""):
    """Question Header with badge and optional priority."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.first_line_indent = Pt(0)
    
    r_num = p.add_run(f"CÂU HỎI {q_num}: ")
    r_num.font.name = "Times New Roman"
    r_num.font.size = Pt(13)
    r_num.bold = True
    r_num.font.color.rgb = RGBColor.from_string(CLR_PRIMARY)
    
    r_txt = p.add_run(q_title)
    r_txt.font.name = "Times New Roman"
    r_txt.font.size = Pt(13)
    r_txt.bold = True
    r_txt.font.color.rgb = RGBColor(0, 0, 0)
    
    if category:
        r_cat = p.add_run(f"  [{category}]")
        r_cat.font.name = "Times New Roman"
        r_cat.font.size = Pt(10)
        r_cat.bold = True
        r_cat.italic = True
        r_cat.font.color.rgb = RGBColor.from_string(CLR_SECONDARY)

    if priority:
        r_prio = p.add_run(f"  ({priority})")
        r_prio.font.name = "Times New Roman"
        r_prio.font.size = Pt(10)
        r_prio.bold = True
        r_prio.font.color.rgb = RGBColor(200, 30, 30)

def build_document():
    doc = docx.Document()
    
    # Page setup: A4
    sec = doc.sections[0]
    sec.page_width = Inches(8.27)
    sec.page_height = Inches(11.69)
    sec.top_margin = Inches(0.79)     # 2.0 cm
    sec.bottom_margin = Inches(0.79)  # 2.0 cm
    sec.left_margin = Inches(0.98)    # 2.5 cm
    sec.right_margin = Inches(0.79)   # 2.0 cm
    
    # Header & Footer
    hdr = sec.header.paragraphs[0]
    hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_hdr = hdr.add_run("BÍ KÍP VẤN ĐÁP BẢO VỆ TIỂU LUẬN DSP — PIANO CHROMATIC TUNER (ESP32-S3 + INMP441)")
    r_hdr.font.name = "Times New Roman"
    r_hdr.font.size = Pt(8.5)
    r_hdr.italic = True
    r_hdr.font.color.rgb = RGBColor(100, 100, 100)
    
    ftr = sec.footer.paragraphs[0]
    ftr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    vh.add_toc_field(ftr, 'PAGE')
    
    # Document Title Block
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(0)
    p_inst.paragraph_format.space_after = Pt(2)
    r_inst = p_inst.add_run("TRƯỜNG ĐẠI HỌC BÁCH KHOA - ĐHQG-HCM | KHOA ĐIỆN - ĐIỆN TỬ")
    r_inst.font.name = "Times New Roman"
    r_inst.font.size = Pt(11)
    r_inst.bold = True
    r_inst.font.color.rgb = RGBColor.from_string(CLR_SECONDARY)
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(4)
    p_title.paragraph_format.space_after = Pt(4)
    r_t = p_title.add_run("TÀI LIỆU ÔN TẬP VÀ BÍ KÍP VẤN ĐÁP BẢO VỆ TIỂU LUẬN DSP\nBỘ 15 CÂU HỎI TRỌNG TÂM & CHIẾN LƯỢC ĐẠT ĐIỂM TỐI ĐA")
    r_t.font.name = "Times New Roman"
    r_t.font.size = Pt(16)
    r_t.bold = True
    r_t.font.color.rgb = RGBColor.from_string(CLR_PRIMARY)
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(2)
    p_sub.paragraph_format.space_after = Pt(14)
    r_s = p_sub.add_run("Đề tài: Thiết kế thiết bị lên dây đàn Piano Chromatic sử dụng ESP32-S3 và INMP441\nSinh viên thực hiện: Lê Tấn Dũng — MSSV: 24150654 — Học kỳ 1, Năm học 2026–2027")
    r_s.font.name = "Times New Roman"
    r_s.font.size = Pt(11)
    r_s.italic = True
    r_s.font.color.rgb = RGBColor(60, 60, 60)
    
    # =========================================================================
    # PHẦN I: MA TRẬN PHÂN TÍCH VÀ NGUYÊN TẮC BẢO VỆ
    # =========================================================================
    vh.add_heading_1(doc, "PHẦN I — MA TRẬN PHÂN TÍCH VÀ NGUYÊN TẮC VÀNG KHI BẢO VỆ", is_chapter=False)
    
    vh.add_p(doc, 
        "Khi bảo vệ đồ án / tiểu luận môn học Xử lý tín hiệu số (DSP) trước Hội đồng hoặc Giảng viên hướng dẫn, "
        "mục tiêu cốt lõi của giảng viên không phải là 'đánh đố' mà là kiểm tra 3 năng lực nền tảng: "
        "(1) Sinh viên có thực sự tự làm và hiểu thấu suốt chuỗi xử lý tín hiệu hay không? "
        "(2) Sinh viên có nắm vững các nguyên lý toán học nền tảng (Lấy mẫu, Nyquist, FFT, nội suy đỉnh) hay chỉ gọi thư viện đen? "
        "(3) Sinh viên có thái độ trung thực khoa học, dám thừa nhận các giới hạn vật lý thực tế của đề tài hay ngụy tạo số liệu?", indent=0.3)
    
    add_callout_box(doc, "★ 3 NGUYÊN TẮC VÀNG BẢO VỆ ĐỒ ÁN ĐẠT ĐIỂM TỐI ĐA", [
        "1. NGUYÊN TẮC DÒNG CHẢY PIPELINE (NÓI CÓ HỆ THỐNG): Bất kỳ câu hỏi nào về thuật toán, luôn dẫn dắt giảng viên theo đúng luồng xử lý: "
        "Microphone I2S DMA → Đệm trượt 50% → Khử DC → Cửa sổ Hann → FFT Radix-2 → Lọc sàn nhiễu trung vị → Chấm điểm đa họa âm (Harmonic Scoring) → "
        "Cơ chế Bass-Gate → Nội suy Parabol bậc hai (QI) → Ánh xạ nốt 12-TET → Lọc làm mịn thời gian → JSON API → Giao diện Web.",
        
        "2. NGUYÊN TẮC REAL-DATA ONLY (LIÊM CHÍNH KHOA HỌC TUYỆT ĐỐI): Tuyệt đối không bao giờ trả lời 'hệ thống hoàn hảo 100% trên 88 phím'. "
        "Hãy tự tin khẳng định: 'Hệ thống đã kiểm chứng thực tế và đạt độ chính xác xuất sắc trên 5 nốt đại diện dải trung và cận trầm (A4, C4, C5, D3, E3) với MAE < 0.29 Hz (dưới 1.1 cent); "
        "riêng nốt trầm E2 độ chính xác đạt 15% do giới hạn âm học; các dải cực trầm A0–C2 và cực cao C6–C8 nhóm chưa đủ dữ liệu nên không dám khẳng định'. "
        "Giảng viên cực kỳ tôn trọng sinh viên hiểu rõ giới hạn của hệ thống.",
        
        "3. NGUYÊN TẮC TRADE-OFF (HIỂU BẢN CHẤT ĐÁNH ĐỔI): Mọi quyết định thiết kế phần cứng và thuật toán (Fs = 16 kHz, N = 4096, Hop = 128 ms, cửa sổ Hann, dung sai 3.5%) "
        "đều là kết quả của sự cân bằng toán học giữa độ phân giải tần số, độ trễ thời gian thực và tài nguyên vi điều khiển ESP32-S3."
    ], border_color=CLR_PRIMARY, bg_color="EDF2F7", title_color=CLR_PRIMARY)

    # Top 5 Priority Table
    vh.add_heading_2(doc, "🎯 TOP 5 CÂU HỎI 'TỬ HUYỆT' GIẢNG VIÊN DÙNG ĐỂ BẮT BẺ & CÁCH HÓA GIẢI")
    vh.add_p(doc, 
        "Nếu thời gian vấn đáp bị rút ngắn hoặc giảng viên muốn kiểm tra trực diện năng lực thật của nhóm trong 3–5 phút, "
        "5 câu hỏi sau đây là những câu hỏi có xác suất xuất hiện cao nhất và mang tính quyết định điểm số:", indent=0.3)

    tbl_top5 = doc.add_table(rows=1, cols=4)
    tbl_top5.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_top5.autofit = False
    vh.set_table_borders(tbl_top5)
    
    w_top5 = [Inches(1.0), Inches(1.8), Inches(1.8), Inches(1.9)]
    h_top5 = ["Ưu tiên", "Câu hỏi then chốt", "Mục tiêu khảo sát của Giảng viên", "Chiến thuật trả lời ăn điểm"]
    for idx, text in enumerate(h_top5):
        c = tbl_top5.rows[0].cells[idx]
        c.width = w_top5[idx]
        vh.set_cell_background(c, "EAECEF")
        vh.set_cell_margins(c, top=60, bottom=60, left=40, right=40)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(9.5)
        r.bold = True
        
    top5_data = [
        ("🔥 Ưu tiên 1", "Câu 7: Vì sao không chọn peak lớn nhất?", "Kiểm tra hiểu bản chất pitch detection và hiện tượng Missing Fundamental ở piano.", "Dẫn chứng D3 (họa âm 3 mạnh gấp 9 lần f0) và E2 (họa âm 3 mạnh gấp 10 lần f0). Nhấn mạnh giải thuật Harmonic Scoring."),
        ("🔥 Ưu tiên 2", "Câu 8: Quadratic Interpolation làm gì?", "Kiểm tra hiểu bản chất toán học DSP hay chỉ gọi thư viện đen.", "Viết công thức tính độ lệch đỉnh p từ 3 bin liền kề; giải thích cách vượt qua giới hạn độ rộng bin rời rạc 3.906 Hz."),
        ("🔥 Ưu tiên 3", "Câu 12: E2 đã được xử lý thế nào?", "Kiểm tra hiểu phần nhóm tự debug và giải quyết vấn đề kỹ thuật.", "Trình bày trung thực E2 chỉ đạt 15% trong test sạch; phân tích cơ chế Bass-Gate (55–110 Hz) cứu f0 yếu khi có năng lượng họa âm."),
        ("🔥 Ưu tiên 4", "Câu 14: Có đạt < 0.5 Hz toàn keyboard?", "Kiểm tra đạo đức khoa học và tính liêm chính thực nghiệm.", "Thẳng thắn trả lời 'Chưa thể khẳng định'; chứng minh đạt xuất sắc trên 5 nốt trung/cận trầm; thừa nhận giới hạn ở dải cực trầm/cao."),
        ("🔥 Ưu tiên 5", "Câu 15: Nếu octave error thì debug ở đâu?", "Kiểm tra khả năng chẩn đoán toàn hệ thống từ phần cứng đến Web.", "Trình bày dứt khoát Quy trình chẩn đoán 10 tầng tín hiệu từ I2S raw, RMS, DC, FFT, Peak, Harmonic, QI đến Smoothing."),
    ]
    for r_data in top5_data:
        row = tbl_top5.add_row()
        for idx, text in enumerate(r_data):
            c = row.cells[idx]
            c.width = w_top5[idx]
            vh.set_cell_margins(c, top=50, bottom=50, left=40, right=40)
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx == 0 else WD_ALIGN_PARAGRAPH.JUSTIFY
            r = p.add_run(text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.0)
            if idx == 0:
                r.bold = True
                r.font.color.rgb = RGBColor(200, 30, 30)
            elif idx == 1:
                r.bold = True
                
    vh.make_table_responsive(tbl_top5)
    
    # Master Checklist Table
    vh.add_heading_2(doc, "📋 BẢNG TRA CỨU NHANH 15 CÂU HỎI VẤN ĐÁP THEO 5 NHÓM CHỦ ĐỀ")
    vh.add_p(doc, "Dưới đây là sơ đồ tóm tắt 15 câu hỏi được phân loại theo 5 năng lực chuyên môn DSP:", indent=0.3)
    
    tbl_all = doc.add_table(rows=1, cols=4)
    tbl_all.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_all.autofit = False
    vh.set_table_borders(tbl_all)
    
    w_all = [Inches(1.5), Inches(0.8), Inches(2.2), Inches(2.0)]
    h_all = ["Nhóm chủ đề", "Mã câu", "Nội dung câu hỏi cốt lõi", "Từ khóa giải pháp then chốt"]
    for idx, text in enumerate(h_all):
        c = tbl_all.rows[0].cells[idx]
        c.width = w_all[idx]
        vh.set_cell_background(c, "EAECEF")
        vh.set_cell_margins(c, top=60, bottom=60, left=40, right=40)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(9.5)
        r.bold = True
        
    all_data = [
        ("🟢 Nhóm 1:\nHiểu tổng thể project", "Câu 1", "Mô tả toàn bộ luồng xử lý từ búa gõ đến Web", "10 mắt xích: I2S → DC → Hann → FFT → Peak → QI → Web"),
        ("🟢 Nhóm 1:\nHiểu tổng thể project", "Câu 2", "Tại sao DSP trên ESP32 mà không gửi raw lên Web?", "Tiết kiệm 98% băng thông (512 kbps vs <1 KB/s), Realtime"),
        ("🟢 Nhóm 1:\nHiểu tổng thể project", "Câu 3", "Tại sao dùng mic I2S mà không dùng mic analog?", "ADC 24-bit MEMS, chống nhiễu EMI Wi-Fi/nguồn, DMA"),
        ("🟡 Nhóm 2:\nFFT & Sampling", "Câu 4", "Fs = 16 kHz nghĩa là gì? Nếu giảm xuống 8 kHz?", "Nyquist 8 kHz; giảm 8 kHz gây Aliasing C8 và họa âm"),
        ("🟡 Nhóm 2:\nFFT & Sampling", "Câu 5", "Tại sao chọn N = 4096? Tăng lên 8192 có tốt hơn?", "Đánh đổi Δf = 3.9 Hz và trễ 256 ms; 8192 trễ 512 ms"),
        ("🟡 Nhóm 2:\nFFT & Sampling", "Câu 6", "Bin 3.906 Hz có giới hạn độ chính xác ở 437.5/441.4 Hz?", "Không, Quadratic Interpolation xấp xỉ liên tục giữa 2 bin"),
        ("🟠 Nhóm 3:\nPitch Detection", "Câu 7 🔥", "Tại sao không chọn FFT peak lớn nhất?", "Missing Fundamental: D3 họa âm gấp 9, E2 họa âm gấp 10"),
        ("🟠 Nhóm 3:\nPitch Detection", "Câu 8 🔥", "Quadratic Interpolation thực sự làm gì?", "Xấp xỉ đỉnh parabol: p = (α - γ)/(2(α - 2β + γ))"),
        ("🟠 Nhóm 3:\nPitch Detection", "Câu 9", "A4 có họa âm 880 Hz mạnh hơn 440 Hz thì xử lý sao?", "Harmonic Scoring: thưởng hệ số [1 + 0.4(h_count - 1)]"),
        ("🟠 Nhóm 3:\nPitch Detection", "Câu 10", "Vì sao phải khử DC offset trước FFT?", "Khử xung Dirac tại 0 Hz; tránh rò rỉ phổ che lấp dải trầm"),
        ("🔴 Nhóm 4:\nThực tế Piano", "Câu 11", "Tại sao nốt bass E2 khó nhận diện hơn A4?", "Soundboard yếu ở 82 Hz, họa âm áp đảo, gần nhiễu 50 Hz"),
        ("🔴 Nhóm 4:\nThực tế Piano", "Câu 12 🔥", "Lỗi E2 sửa thế nào? Tại sao sửa hợp lý?", "E2 đúng 15%; Bass-Gate (55–110 Hz) nới biên độ khi có họa âm"),
        ("🔴 Nhóm 4:\nThực tế Piano", "Câu 13", "Tại sao không hạ threshold toàn bộ cho E2?", "Gây False Positives: nhiễu bàn 7.9–13.6 nhảy nốt lung tung"),
        ("🔴 Nhóm 5:\nĐánh giá & Debug", "Câu 14 🔥", "Project có đạt < 0.5 Hz trên toàn bộ keyboard?", "Chưa khẳng định; đạt xuất sắc 5 nốt trung; E2 còn hạn chế"),
        ("🔴 Nhóm 5:\nĐánh giá & Debug", "Câu 15 🔥", "Nếu nhận sai 1 octave, kiểm tra những phần nào?", "Quy trình chẩn đoán 10 tầng: I2S → RMS → DC → FFT → QI..."),
    ]
    for r_data in all_data:
        row = tbl_all.add_row()
        for idx, text in enumerate(r_data):
            c = row.cells[idx]
            c.width = w_all[idx]
            vh.set_cell_margins(c, top=40, bottom=40, left=40, right=40)
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx in [0, 1] else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.0)
            if idx == 1 and "🔥" in text:
                r.bold = True
                r.font.color.rgb = RGBColor(200, 30, 30)
            elif idx == 0:
                r.bold = True
                
    vh.make_table_responsive(tbl_all)

    # =========================================================================
    # PHẦN II: CHI TIẾT 15 CÂU HỎI VẤN ĐÁP THEO 5 NHÓM CHỦ ĐỀ
    # =========================================================================
    vh.add_heading_1(doc, "PHẦN II — CHI TIẾT 15 CÂU HỎI VẤN ĐÁP KÈM LỜI GIẢI MẪU VÀ MẸO ĐỐI ĐÁP", is_chapter=False)

    # -------------------------------------------------------------------------
    # NHÓM 1: TỔNG THỂ KIẾN TRÚC
    # -------------------------------------------------------------------------
    vh.add_heading_2(doc, "🟢 NHÓM 1 — HIỂU TỔNG THỂ KIẾN TRÚC PROJECT VÀ SIGNAL CHAIN")

    # Q1
    add_q_header(doc, "1", "Em hãy mô tả toàn bộ luồng xử lý của hệ thống từ lúc nhấn một phím piano đến khi Web hiển thị A4 – 440 Hz?", "Tổng thể kiến trúc")
    add_callout_box(doc, "🎯 MỤC TIÊU CỦA GIẢNG VIÊN & ĐIỂM CHẾT CẦN TRÁNH", [
        "• Giảng viên muốn kiểm tra: Sinh viên có nắm được toàn bộ dòng chảy dữ liệu (signal chain) từ phần cứng đến phần mềm hay chỉ biết code chắp vá.",
        "• Điểm chết: Kể thiếu các khâu cốt lõi như Khử DC, Cửa sổ Hann, đệm trượt 50% hoặc không phân biệt được vai trò của FFT và Quadratic Interpolation."
    ], border_color=CLR_GOAL_BORDER, bg_color=CLR_GOAL_BG, title_color=CLR_GOAL_BORDER)

    add_callout_box(doc, "💬 CÂU TRẢ LỜI MẪU CHUẨN ĐIỂM 10 (TRẢ LỜI TỰ TIN, MẠCH LẠC)", [
        "\"Thưa thầy, toàn bộ chuỗi xử lý của hệ thống trải qua 10 mắt xích liên hoàn theo thời gian thực:",
        "1. Thu nhận âm thanh: Khi búa gõ vào dây đàn A4, microphone MEMS kỹ thuật số INMP441 thu sóng âm, chuyển đổi ADC 24-bit ở tần số lấy mẫu Fs = 16 kHz và truyền qua bus I2S.",
        "2. Đệm trượt DMA 50%: Bộ điều khiển I2S DMA trên ESP32-S3 nạp các mẫu âm thanh vào bộ đệm trượt N = 4 096 mẫu (256 ms), với chu kỳ bước nhảy hop size = 2 048 mẫu (128 ms).",
        "3. Tiền xử lý & Khử DC: Thuật toán tính giá trị trung bình mẫu μ và trừ trực tiếp khỏi 4 096 mẫu để loại bỏ triệt để điện áp lệch DC offset của microphone.",
        "4. Cửa sổ Hann tuần hoàn: Nhân mảng tín hiệu với cửa sổ Hann w[n] = 0.5*(1 - cos(2*pi*n/N)) để triệt tiêu hiện tượng rò rỉ phổ (spectral leakage).",
        "5. Biến đổi FFT Radix-2: Thuật toán FFT 4 096 điểm chạy trên Lõi 0 của ESP32-S3, tính phổ biên độ mag[k] cho 2 048 bin dương với độ rộng mỗi bin Δf = 3.90625 Hz.",
        "6. Ước lượng sàn nhiễu trung vị & Dò đỉnh phổ: Trích xuất cửa sổ 29 bin quanh mỗi bin, loại 5 bin giữa, sắp xếp 24 bin còn lại để lấy trung vị làm sàn nhiễu LocalFloor. Lọc các đỉnh có biên độ mag ≥ 1.0 và độ nổi bật Prominence ≥ 2.2.",
        "7. Chấm điểm giả thuyết đa họa âm (Harmonic Scoring): Với các đỉnh tìm được, thuật toán sinh các giả thuyết tần số cơ bản f_hyp = f_peak / m (m = 1..6) và tính điểm số tích lũy dựa trên số lượng họa âm tìm thấy kèm cơ chế Bass-Gate.",
        "8. Nội suy đỉnh Parabol bậc hai (Quadratic Interpolation): Lấy 3 bin lân cận quanh đỉnh được chọn để tính độ lệch phân số p, từ đó ước lượng chính xác tần số cơ bản liên tục f0 = (k + p)*Δf = 440.281 Hz.",
        "9. Ánh xạ nốt, tính Cent & Lọc làm mịn: Tần số f0 được đổi sang số MIDI n = 69 + 12*log2(f0/440) ra nốt A4 (MIDI 69), tính độ lệch cent = 1200*log2(f0/440.0) ≈ +1.1 cent. Bộ lọc ổn định 2 khung liên tiếp xác nhận trạng thái STABLE.",
        "10. Xuất giao diện Web: Kết quả được serialize thành chuỗi JSON, máy chủ HTTP nhúng trên Lõi 1 phản hồi request GET từ trình duyệt client (chu kỳ 125 ms), giao diện Celestial Tuner xoay kim đo về vị trí 50.39% và bật banner xanh IN TUNE.\""
    ], border_color=CLR_ANS_BORDER, bg_color=CLR_ANS_BG, title_color=CLR_ANS_BORDER)

    add_callout_box(doc, "🔬 DẪN CHỨNG SỐ LIỆU THỰC TẾ & MẸO ĐỐI ĐÁP", [
        "• Số liệu thực tế trong báo cáo: Thời gian chạy DSP thuần (bước 3 đến bước 9) chỉ mất 23.56 – 25.37 ms trên Lõi 240 MHz (CPU load ~18.5%). Tổng độ trễ từ gõ búa đến Web là 150 – 280 ms.",
        "• Mẹo: Nói dứt khoát 10 bước theo thứ tự số, giảng viên sẽ thấy bạn nắm hệ thống như lòng bàn tay và không cần hỏi thêm câu kiến trúc."
    ], border_color=CLR_TECH_BORDER, bg_color=CLR_TECH_BG, title_color=CLR_TECH_BORDER)

    # Q2
    add_q_header(doc, "2", "Tại sao không gửi tín hiệu microphone trực tiếp lên Web rồi xử lý bằng JavaScript, mà lại chạy DSP trên ESP32-S3?", "Kiến trúc hệ thống")
    add_callout_box(doc, "🎯 MỤC TIÊU CỦA GIẢNG VIÊN & ĐIỂM CHẾT", [
        "• Mục tiêu: Kiểm tra xem sinh viên có hiểu kiến trúc hệ thống nhúng (Embedded IoT) và bài toán băng thông mạng không.",
        "• Điểm chết: Trả lời 'vì đề tài bắt làm trên ESP32' hoặc 'vì em thích code C hơn JS'."
    ], border_color=CLR_GOAL_BORDER, bg_color=CLR_GOAL_BG, title_color=CLR_GOAL_BORDER)

    add_callout_box(doc, "💬 CÂU TRẢ LỜI MẪU CHUẨN ĐIỂM 10", [
        "\"Thưa thầy, nhóm thiết kế DSP chạy hoàn toàn trên vi điều khiển ESP32-S3 vì 4 lý do kỹ thuật sống còn:",
        "1. Tiết kiệm băng thông mạng Wi-Fi (>98%): Âm thanh thô 16 kHz / 24-bit đòi hỏi băng thông stream liên tục 512 kbps (~64 KB/s). Truyền liên tục qua Wi-Fi SoftAP của vi điều khiển sẽ gây nghẽn băng thông và rớt gói. Trong khi đó, gói tin JSON sau khi DSP xử lý chỉ nặng ~120 byte, gửi ở nhịp 125 ms chỉ tốn < 1 KB/s.",
        "2. Tính tất định về thời gian thực (Real-time Determinism): Mạng không dây luôn có độ trễ biến thiên và rung pha (jitter). Xử lý DSP tại biên (Edge DSP) trên ESP32 đảm bảo chu trình tính toán cố định 24 ms, không bị phụ thuộc vào chất lượng sóng Wi-Fi.",
        "3. Tính độc lập của thiết bị nhúng: Tuner là một sản phẩm phần cứng độc lập. Thiết bị phải tự hoàn thành chức năng đo đạc và có thể tích hợp màn hình OLED hoặc còi báo mà không bắt buộc phải có máy tính hay điện thoại mở trình duyệt.",
        "4. Không phụ thuộc cấu hình client: Không phải điện thoại nào cũng chạy FFT JS mượt mà; xử lý tại vi điều khiển đảm bảo mọi thiết bị (từ máy tính bảng cũ đến điện thoại rẻ tiền) mở web đều hiển thị mượt mà như nhau.\""
    ], border_color=CLR_ANS_BORDER, bg_color=CLR_ANS_BG, title_color=CLR_ANS_BORDER)

    add_callout_box(doc, "🔬 DẪN CHỨNG SỐ LIỆU THỰC TẾ & MẸO ĐỐI ĐÁP", [
        "• Số liệu thực tế: Băng thông stream âm thanh thô = 16 000 samples/s * 32-bit (I2S DMA word) = 512 kbps. Băng thông gói tin JSON = 120 bytes / 0.125s = 960 bytes/s (~7.68 kbps) -> Giảm tải băng thông tới 98.5%!",
        "• Mẹo: Nhấn mạnh khái niệm 'Edge Computing / Edge DSP' (Tính toán tại biên), giảng viên đánh giá rất cao tư duy kiến trúc hiện đại."
    ], border_color=CLR_TECH_BORDER, bg_color=CLR_TECH_BG, title_color=CLR_TECH_BORDER)

    # Q3
    add_q_header(doc, "3", "Tại sao project này cần microphone I2S thay vì một microphone analog thông thường?", "Phần cứng & ADC")
    add_callout_box(doc, "🎯 MỤC TIÊU CỦA GIẢNG VIÊN & ĐIỂM CHẾT", [
        "• Mục tiêu: Kiểm tra kiến thức phần cứng âm thanh số, cấu trúc MEMS và giao thức I2S.",
        "• Điểm chết: Nhầm lẫn rằng microphone analog cho âm thanh 'ấm hơn' hoặc không giải thích được vấn đề nhiễu EMI."
    ], border_color=CLR_GOAL_BORDER, bg_color=CLR_GOAL_BG, title_color=CLR_GOAL_BORDER)

    add_callout_box(doc, "💬 CÂU TRẢ LỜI MẪU CHUẨN ĐIỂM 10", [
        "\"Thưa thầy, nhóm chọn microphone kỹ thuật số I2S INMP441 vì 4 ưu điểm vượt trội so với micro analog:",
        "1. Tích hợp sẵn bộ tiền khuếch đại và ADC 24-bit chất lượng cao: Tín hiệu âm học được chuyển đổi sang số nhị phân ngay trên chip cảm biến MEMS, đạt tỷ số tín hiệu trên nhiễu SNR = 61 dBA và độ nhạy cao -26 dBFS.",
        "2. Miễn nhiễm tuyệt đối với nhiễu điện từ (EMI): Tín hiệu analog từ micro truyền thống có biên độ rất nhỏ (vài mV), khi đi trên dây cắm breadboard rất dễ bị cảm ứng nhiễu sóng Wi-Fi của ESP32 và nhiễu nguồn xung 5V. Luồng số I2S truyền dữ liệu nhị phân nên không bị suy hao hay biến dạng biên độ.",
        "3. Giao tiếp DMA trực tiếp vào RAM: Bộ điều khiển I2S trên ESP32-S3 tự động chuyển dữ liệu vào bộ nhớ qua kênh DMA mà không tiêu tốn một chu kỳ lệnh nào của CPU.",
        "4. Tránh hạn chế của bộ ADC tích hợp sẵn trên ESP32: ADC analog nội của ESP32 có đặc tính phi tuyến lớn ở hai đầu dải đo và mức nhiễu nền cao, không phù hợp cho việc phân tích âm thanh nhạc cụ chính xác.\""
    ], border_color=CLR_ANS_BORDER, bg_color=CLR_ANS_BG, title_color=CLR_ANS_BORDER)

    add_callout_box(doc, "🔬 DẪN CHỨNG SỐ LIỆU THỰC TẾ & MẸO ĐỐI ĐÁP", [
        "• Thông số kỹ thuật INMP441: Tần số đáp ứng phẳng 60 Hz – 15 kHz, SNR 61 dBA, mức áp suất âm tối đa AOP = 120 dB SPL. Không cần thêm op-amp tiền khuếch đại bên ngoài.",
        "• Mẹo: Nếu giảng viên hỏi 'Tại sao chân L/R nối GND?', trả lời ngay: 'Để cấu hình INMP441 phát dữ liệu trên kênh trái (Left channel) của khung truyền I2S'."
    ], border_color=CLR_TECH_BORDER, bg_color=CLR_TECH_BG, title_color=CLR_TECH_BORDER)

    # -------------------------------------------------------------------------
    # NHÓM 2: FFT VÀ SAMPLING
    # -------------------------------------------------------------------------
    vh.add_heading_2(doc, "🟡 NHÓM 2 — BẢN CHẤT XỬ LÝ TÍN HIỆU SỐ: SAMPLING, CỬA SỔ VÀ BIẾN ĐỔI FFT")

    # Q4
    add_q_header(doc, "4", "Fs = 16 kHz có ý nghĩa gì trong project? Nếu giảm Fs xuống 8 kHz thì chuyện gì xảy ra?", "Sampling & Nyquist")
    add_callout_box(doc, "🎯 MỤC TIÊU CỦA GIẢNG VIÊN & ĐIỂM CHẾT", [
        "• Mục tiêu: Kiểm tra định lý lấy mẫu Nyquist-Shannon và sự hiểu biết về dải tần âm học của đàn piano.",
        "• Điểm chết: Quên rằng nốt cao nhất của piano là C8 (4186 Hz) và các họa âm bậc cao nằm trên 4 kHz."
    ], border_color=CLR_GOAL_BORDER, bg_color=CLR_GOAL_BG, title_color=CLR_GOAL_BORDER)

    add_callout_box(doc, "💬 CÂU TRẢ LỜI MẪU CHUẨN ĐIỂM 10", [
        "\"Thưa thầy, theo định lý lấy mẫu Nyquist-Shannon, tần số lấy mẫu Fs = 16 kHz cho phép hệ thống phân tích dải tần số âm thanh tối đa lên tới f_Nyquist = Fs / 2 = 8 000 Hz.",
        "• Ý nghĩa trong project: Đàn piano 88 phím có nốt cao nhất là C8 với tần số 4 186.01 Hz. Dải Nyquist 8 kHz không những bao trọn toàn bộ tần số cơ bản của 88 phím mà còn thu nhận được các họa âm bậc 2, bậc 3 của các nốt trung và cao (ví dụ nốt C5: 523 Hz có họa âm bậc 3 tại 1570 Hz; nốt C6: 1046 Hz có họa âm bậc 4 tại 4186 Hz).",
        "• Nếu giảm Fs xuống 8 kHz:",
        "1. Tần số Nyquist giảm xuống chỉ còn 4 000 Hz.",
        "2. Nốt C8 (4 186 Hz) sẽ bị hiện tượng chồng phổ (Aliasing) ngay tại tần số cơ bản, bị gập gương thành 8000 - 4186 = 3814 Hz!",
        "3. Họa âm bậc 2 của các nốt từ C5 trở lên sẽ bị phản xạ gập ngược vào dải tần thấp, tạo ra các đỉnh phổ ảo giả mạo làm phá vỡ hoàn toàn thuật toán nhận diện đa họa âm.\""
    ], border_color=CLR_ANS_BORDER, bg_color=CLR_ANS_BG, title_color=CLR_ANS_BORDER)

    add_callout_box(doc, "🔬 DẪN CHỨNG SỐ LIỆU THỰC TẾ & MẸO ĐỐI ĐÁP", [
        "• Công thức toán học: f_Nyquist = Fs / 2. Nếu f > f_Nyquist, tần số quan sát được f_alias = |Fs - f|.",
        "• Mẹo: Nhấn mạnh rằng 16 kHz là tiêu chuẩn vàng của xử lý tiếng nói và nhạc cụ cơ bản vì nó vừa đủ bao quát dải âm nghe rõ của tai người mà không gây quá tải bộ đệm DMA như 44.1 kHz hay 48 kHz."
    ], border_color=CLR_TECH_BORDER, bg_color=CLR_TECH_BG, title_color=CLR_TECH_BORDER)

    # Q5
    add_q_header(doc, "5", "Tại sao nhóm chọn N = 4096? Nếu tăng N lên 8192 thì hệ thống tốt hơn hay xấu hơn?", "Độ phân giải vs Độ trễ")
    add_callout_box(doc, "🎯 MỤC TIÊU CỦA GIẢNG VIÊN & ĐIỂM CHẾT", [
        "• Mục tiêu: Kiểm tra nguyên lý đánh đổi giữa miền thời gian và miền tần số (Time-Frequency Uncertainty Principle).",
        "• Điểm chết: Trả lời phiến diện '8192 tốt hơn vì độ phân giải cao hơn'."
    ], border_color=CLR_GOAL_BORDER, bg_color=CLR_GOAL_BG, title_color=CLR_GOAL_BORDER)

    add_callout_box(doc, "💬 CÂU TRẢ LỜI MẪU CHUẨN ĐIỂM 10", [
        "\"Thưa thầy, việc chọn N = 4 096 là kết quả của sự cân bằng tối ưu giữa độ phân giải tần số và độ trễ thời gian thực:",
        "• Với Fs = 16 kHz và N = 4 096:",
        "  - Độ phân giải tần số: Δf = Fs / N = 16 000 / 4 096 = 3.90625 Hz/bin.",
        "  - Chiều dài cửa sổ thời gian: T_frame = N / Fs = 4 096 / 16 000 = 0.256 s = 256 ms.",
        "• Nếu tăng N lên 8 192, hệ thống KHÔNG HẲN TỐT HƠN mà phải chịu sự đánh đổi tiêu cực nghiêm trọng:",
        "1. Độ trễ thời gian tăng gấp đôi: T_frame tăng lên 512 ms. Người chơi gõ phím phải chờ hơn nửa giây mới cập nhật kết quả, làm mất tính phản hồi thời gian thực.",
        "2. Bộ nhớ RAM tăng gấp đôi: Mảng số phức FFT 8 192 điểm chiếm 64 KB RAM cho mỗi buffer.",
        "3. Thời gian tính toán FFT tăng hơn gấp đôi: Theo O(N log2 N), số phép tính tăng từ 49 152 lên 106 496 phép tính bướm, đẩy tải CPU lên cao cạnh tranh với tác vụ Wi-Fi.",
        "4. Tín hiệu piano là không dừng (Non-stationary): Cửa sổ 512 ms quá dài sẽ làm nhòe pha khởi phát (attack) và làm giảm biên độ do dao động tắt dần (decay).",
        "• Do đó, kết hợp N = 4 096 với thuật toán nội suy Parabol (QI) là giải pháp tối ưu nhất.\""
    ], border_color=CLR_ANS_BORDER, bg_color=CLR_ANS_BG, title_color=CLR_ANS_BORDER)

    add_callout_box(doc, "🔬 DẪN CHỨNG SỐ LIỆU THỰC TẾ & MẸO ĐỐI ĐÁP", [
        "• Đo lường thực tế: Tại N = 4096, thời gian chạy DSP là 23.56 – 25.37 ms. Nếu N = 8192, thời gian tính toán sẽ vọt lên > 55 ms, cộng với thời gian thu mẫu 256 ms (hop 50%) sẽ khiến tổng độ trễ vượt ngưỡng 350 ms.",
        "• Mẹo: Khẳng định 'Trong kỹ thuật nhúng, giải pháp tốt nhất không phải là giải pháp cực đại hóa một thông số mà là điểm cân bằng tối ưu các ràng buộc'."
    ], border_color=CLR_TECH_BORDER, bg_color=CLR_TECH_BG, title_color=CLR_TECH_BORDER)

    # Q6
    add_q_header(doc, "6", "Với Fs = 16 kHz, N = 4096, bin spacing là bao nhiêu? Có phải hệ thống chỉ nhận được 437.5 Hz hoặc 441.4 Hz không?", "FFT Bin Resolution")
    add_callout_box(doc, "🎯 MỤC TIÊU CỦA GIẢNG VIÊN & ĐIỂM CHẾT", [
        "• Mục tiêu: Kiểm tra xem sinh viên có phân biệt được giữa 'Độ rộng bin FFT rời rạc' và 'Độ chính xác ước lượng tần số thực tế' không.",
        "• Điểm chết: Thừa nhận rằng hệ thống bị giới hạn ở 437.5 Hz hoặc 441.4 Hz."
    ], border_color=CLR_GOAL_BORDER, bg_color=CLR_GOAL_BG, title_color=CLR_GOAL_BORDER)

    add_callout_box(doc, "💬 CÂU TRẢ LỜI MẪU CHUẨN ĐIỂM 10", [
        "\"Thưa thầy, khoảng cách giữa 2 bin FFT rời rạc là Δf = Fs / N = 16 000 / 4 096 = 3.90625 Hz/bin.",
        "• Bin 112 tương ứng 112 * 3.90625 = 437.50 Hz.",
        "• Bin 113 tương ứng 113 * 3.90625 = 441.40625 Hz.",
        "NHƯNG HỆ THỐNG HOÀN TOÀN KHÔNG BỊ GIỚI HẠN ở 2 giá trị này! Hệ thống đo được chính xác 440.281 Hz là nhờ thuật toán NỘI SUY PARABOL BẬC HAI (Quadratic Interpolation):",
        "- Sóng âm piano khi nhân cửa sổ Hann sẽ rò rỉ năng lượng sang các bin lân cận, tạo thành búp sóng liên tục.",
        "- Thuật toán lấy 3 điểm biên độ quanh đỉnh k = 113: alpha = mag[112], beta = mag[113], gamma = mag[114].",
        "- Bằng cách giải cực trị parabol, ta tính được độ lệch đỉnh phân số p = (alpha - gamma) / (2*(alpha - 2*beta + gamma)).",
        "- Tần số ước lượng thực tế là f = (k + p) * Δf. Nhờ giá trị thực p, hệ thống đạt độ mịn tần số liên tục, sai số thực tế nốt A4 chỉ là 0.281 Hz (1.10 cent), nhỏ hơn độ rộng bin tới 14 lần!\""
    ], border_color=CLR_ANS_BORDER, bg_color=CLR_ANS_BG, title_color=CLR_ANS_BORDER)

    add_callout_box(doc, "🔬 DẪN CHỨNG SỐ LIỆU THỰC TẾ & MẸO ĐỐI ĐÁP", [
        "• Số liệu thực tế Bảng 5.1: A4 đạt 440.281 Hz (p ≈ -0.288 bin), C4 đạt 261.674 Hz (p ≈ +0.019 bin), C5 đạt 523.438 Hz (p ≈ -0.0001 bin).",
        "• Mẹo: Vẽ nhanh hình parabol đi qua 3 điểm trên giấy nháp nếu được yêu cầu giải thích, giảng viên sẽ hoàn toàn bị thuyết phục."
    ], border_color=CLR_TECH_BORDER, bg_color=CLR_TECH_BG, title_color=CLR_TECH_BORDER)

    # -------------------------------------------------------------------------
    # NHÓM 3: THUẬT TOÁN PITCH DETECTION
    # -------------------------------------------------------------------------
    vh.add_heading_2(doc, "🟠 NHÓM 3 — THUẬT TOÁN ƯỚC LƯỢNG CAO ĐỘ (PITCH DETECTION ALGORITHM)")

    # Q7
    add_q_header(doc, "7", "Tại sao không chọn FFT peak lớn nhất làm tần số của nốt piano?", "Harmonic Pitch Detection", "🔥 CÂU HỎI TRỌNG TÂM SỐ 1")
    add_callout_box(doc, "🎯 MỤC TIÊU CỦA GIẢNG VIÊN & ĐIỂM CHẾT", [
        "• Mục tiêu: Đây là câu hỏi kinh điển nhất trong thi DSP âm thanh. Giảng viên muốn biết bạn có hiểu hiện tượng 'mất tần số cơ bản' (Missing Fundamental) của nhạc cụ không.",
        "• Điểm chết: Nói rằng 'đỉnh lớn nhất luôn là tần số cơ bản'."
    ], border_color=CLR_GOAL_BORDER, bg_color=CLR_GOAL_BG, title_color=CLR_GOAL_BORDER)

    add_callout_box(doc, "💬 CÂU TRẢ LỜI MẪU CHUẨN ĐIỂM 10", [
        "\"Thưa thầy, tuyệt đối không thể chọn đỉnh lớn nhất vì trong đàn piano cơ, HỌA ÂM BẬC CAO THƯỜNG XUYÊN MẠNH HƠN TẦN SỐ CƠ BẢN:",
        "1. Dẫn chứng thực tế nốt D3 (146.8 Hz): Đỉnh cơ bản f1 tại Bin 38 chỉ đạt biên độ 3.8, trong khi họa âm bậc 3 tại 440.9 Hz đạt biên độ lên tới 35.0 (mạnh gấp 9 lần f1!). Nếu chọn đỉnh lớn nhất, hệ thống sẽ nhận nhầm D3 thành A4!",
        "2. Dẫn chứng thực tế nốt E2 (82.4 Hz): Đỉnh cơ bản f0 tại Bin 21 chỉ đạt biên độ 1.5–7.3, trong khi họa âm bậc 3 (246 Hz) vọt lên 46.4 (mạnh gấp 6–10 lần!). Nếu chọn đỉnh lớn nhất, hệ thống sẽ nhận nhầm thành nốt B3!",
        "3. Do đặc tính cơ học của thùng đàn và dây thép, năng lượng bức xạ ở dải trầm bị suy hao mạnh, năng lượng dồn hết vào các họa âm bậc 2, 3, 4.",
        "• Do đó, project bắt buộc phải sử dụng giải thuật Harmonic-Aware Scoring: xem xét tập hợp nhiều đỉnh phổ, sinh các giả thuyết ước số f_hyp = f_peak / m và chọn tần số có chuỗi họa âm nhất quán nhất.\""
    ], border_color=CLR_ANS_BORDER, bg_color=CLR_ANS_BG, title_color=CLR_ANS_BORDER)

    add_callout_box(doc, "🔬 DẪN CHỨNG SỐ LIỆU THỰC TẾ & MẸO ĐỐI ĐÁP", [
        "• Số liệu thực tế Bảng 5.3 & 5.4: D3 (f0=146.8 Hz, mag=3.8; 2f0=293.7 Hz, mag=16.3; 3f0=440.9 Hz, mag=35.0). E2 (f0=82.4 Hz, mag=1.5-7.3; 2f0=164 Hz, mag=28.4; 3f0=246 Hz, mag=46.4).",
        "• Mẹo: Sử dụng cụm từ 'Hiện tượng thiếu hụt tần số cơ bản (Missing Fundamental Effect)', đây là thuật ngữ chuyên sâu về âm nhạc học tính toán."
    ], border_color=CLR_TECH_BORDER, bg_color=CLR_TECH_BG, title_color=CLR_TECH_BORDER)

    # Q8
    add_q_header(doc, "8", "Quadratic Interpolation (QI) thực sự làm gì trong project?", "Nội suy đỉnh Parabol", "🔥 CÂU HỎI TRỌNG TÂM SỐ 2")
    add_callout_box(doc, "🎯 MỤC TIÊU CỦA GIẢNG VIÊN & ĐIỂM CHẾT", [
        "• Mục tiêu: Kiểm tra xem sinh viên có nhớ công thức và hiểu nguyên lý toán học của QI hay chỉ trả lời chung chung 'để tăng độ chính xác'.",
        "• Điểm chết: Không viết được công thức tính p hoặc không giải thích được vai trò của 3 bin lân cận."
    ], border_color=CLR_GOAL_BORDER, bg_color=CLR_GOAL_BG, title_color=CLR_GOAL_BORDER)

    add_callout_box(doc, "💬 CÂU TRẢ LỜI MẪU CHUẨN ĐIỂM 10", [
        "\"Thưa thầy, Quadratic Interpolation (Nội suy Parabol bậc hai) thực hiện việc xấp xỉ đỉnh phổ thực liên tục từ 3 điểm mẫu rời rạc:",
        "1. Thuật toán xác định đỉnh rời rạc k, lấy 3 giá trị biên độ: alpha = mag[k-1], beta = mag[k], gamma = mag[k+1].",
        "2. Đặt đường cong parabol đi qua 3 điểm: y(x) = a*(x-k)^2 + b*(x-k) + c.",
        "3. Giải hệ phương trình và tìm tọa độ điểm cực đại y'(x) = 0, ta được độ lệch đỉnh phân số p:",
        "   $$p = \\frac{\\alpha - \\gamma}{2(\\alpha - 2\\beta + \\gamma)}$$  với p thuộc [-0.5, +0.5].",
        "4. Tần số ước lượng chính xác là: f_est = (k + p) * (Fs / N).",
        "• Trong firmware project: Hàm quadratic_interpolate() được áp dụng trực tiếp cho các đỉnh ứng viên, giúp đưa sai số đo đạc của nốt C4 xuống chỉ còn 0.065 Hz (0.43 cent) và A4 xuống 0.281 Hz (1.10 cent).\""
    ], border_color=CLR_ANS_BORDER, bg_color=CLR_ANS_BG, title_color=CLR_ANS_BORDER)

    add_callout_box(doc, "🔬 DẪN CHỨNG SỐ LIỆU THỰC TẾ & MẸO ĐỐI ĐÁP", [
        "• Dẫn chứng mã nguồn C: Hàm `quadratic_interpolate(const float *mag, int k, float *delta, float *val)` trong `main/main.c`. Mẫu số `denom = 2 * (alpha - 2*beta + gamma)`, nếu `fabs(denom) < 1e-6` thì gán `p = 0` để tránh chia cho 0.",
        "• Mẹo: Nhấn mạnh rằng QI dựa trên giả định búp sóng chính của cửa sổ Hann ở thang decibel hoặc tuyến tính có thể xấp xỉ bậc 2 gần đỉnh."
    ], border_color=CLR_TECH_BORDER, bg_color=CLR_TECH_BG, title_color=CLR_TECH_BORDER)

    # Q9
    add_q_header(doc, "9", "Nếu thu âm A4 nhưng họa âm 880 Hz mạnh hơn 440 Hz, thuật toán làm thế nào để vẫn chọn đúng 440 Hz?", "Harmonic Scoring Logic")
    add_callout_box(doc, "🎯 MỤC TIÊU CỦA GIẢNG VIÊN & ĐIỂM CHẾT", [
        "• Mục tiêu: Kiểm tra sâu mã nguồn C trong hàm evaluate_subharmonic_hypothesis() xem sinh viên có tự tay hiện thực thuật toán chấm điểm hay không.",
        "• Điểm chết: Ứng khẩu lúng túng, không nêu được công thức chấm điểm đa họa âm."
    ], border_color=CLR_GOAL_BORDER, bg_color=CLR_GOAL_BG, title_color=CLR_GOAL_BORDER)

    add_callout_box(doc, "💬 CÂU TRẢ LỜI MẪU CHUẨN ĐIỂM 10", [
        "\"Thưa thầy, thuật toán giải quyết bằng cơ chế Sinh giả thuyết và Chấm điểm tích lũy có thưởng:",
        "1. Sinh giả thuyết: Khi gặp đỉnh mạnh tại 880 Hz, thuật toán sinh ra các giả thuyết f_hyp = 880/1 = 880 Hz và f_hyp = 880/2 = 440 Hz. Đỉnh tại 440 Hz cũng sinh ra giả thuyết 440 Hz.",
        "2. Chấm điểm từng giả thuyết theo công thức firmware:",
        "   Score = [ sum_{m in found} (1 / sqrt(m)) * ln(1 + Prom_m) * sqrt(mag_m) ] * [ 1 + 0.40 * (h_count - 1) ]",
        "3. So sánh:",
        "   - Với giả thuyết 880 Hz: Hệ thống chỉ tìm thấy các họa âm là bội của 880 Hz (880, 1760 Hz...). Các đỉnh tại 440 Hz, 1320 Hz không thuộc chuỗi họa âm này -> h_count chỉ bằng 1 hoặc 2.",
        "   - Với giả thuyết 440 Hz: Hệ thống tìm thấy đỉnh 440 Hz (m=1), đỉnh 880 Hz (m=2), đỉnh 1320 Hz (m=3) -> h_count = 3.",
        "   - Hệ số thưởng số lượng họa âm [1 + 0.40 * (3 - 1)] = 1.8 lần! Điểm số của giả thuyết 440 Hz vượt trội hoàn toàn so với giả thuyết 880 Hz.",
        "Do đó, thuật toán chọn chính xác 440 Hz làm tần số thắng cuộc.\""
    ], border_color=CLR_ANS_BORDER, bg_color=CLR_ANS_BG, title_color=CLR_ANS_BORDER)

    add_callout_box(doc, "🔬 DẪN CHỨNG SỐ LIỆU THỰC TẾ & MẸO ĐỐI ĐÁP", [
        "• Trọng số họa âm trong mã nguồn: `weight = 1.0f / sqrtf(m)`. Họa âm bậc thấp được ưu tiên hơn họa âm bậc cao. Dung sai tìm kiếm họa âm `HARMONIC_TOLERANCE = 0.035` (3.5%).",
        "• Mẹo: Nhấn mạnh chữ 'Harmonic Consistency' (Sự nhất quán họa âm) — nốt nhạc thật có chuỗi họa âm dày đặc chứ không đứng cô lập một mình như một vạch phổ nhiễu."
    ], border_color=CLR_TECH_BORDER, bg_color=CLR_TECH_BG, title_color=CLR_TECH_BORDER)

    # Q10
    add_q_header(doc, "10", "Vì sao phải xử lý DC offset trước FFT? Nếu không xử lý thì chuyện gì xảy ra?", "DC Removal")
    add_callout_box(doc, "🎯 MỤC TIÊU CỦA GIẢNG VIÊN & ĐIỂM CHẾT", [
        "• Mục tiêu: Kiểm tra xem sinh viên có hiểu về tính chất của thành phần 0 Hz trong miền biến đổi Fourier hay không.",
        "• Điểm chết: Nói rằng 'để âm thanh nghe to hơn'."
    ], border_color=CLR_GOAL_BORDER, bg_color=CLR_GOAL_BG, title_color=CLR_GOAL_BORDER)

    add_callout_box(doc, "💬 CÂU TRẢ LỜI MẪU CHUẨN ĐIỂM 10", [
        "\"Thưa thầy, cảm biến microphone MEMS I2S luôn tồn tại một điện áp dịch chuyển một chiều (DC bias). Nếu không loại bỏ:",
        "1. Thành phần DC tương ứng với một xung Dirac tại f = 0 Hz (Bin 0) có biên độ cực lớn.",
        "2. Do hiện tượng rò rỉ phổ của cửa sổ Hann, năng lượng khổng lồ tại Bin 0 sẽ tràn sang các bin lân cận (Bin 1: 3.9 Hz, Bin 2: 7.8 Hz, kéo dài tới tận 50–80 Hz).",
        "3. Sàn nhiễu tại dải tần số thấp bị đội lên rất cao, che lấp hoàn toàn các nốt trầm như E2 (82.4 Hz), D3 (146.8 Hz).",
        "• Do đó, trong Mục 4.2 của báo cáo, firmware thực hiện tính trung bình mẫu μ = (1/N) * sum(x_raw[n]) và trừ trực tiếp x[n] = x_raw[n] - μ trước khi nhân cửa sổ Hann và chạy FFT.\""
    ], border_color=CLR_ANS_BORDER, bg_color=CLR_ANS_BG, title_color=CLR_ANS_BORDER)

    add_callout_box(doc, "🔬 DẪN CHỨNG SỐ LIỆU THỰC TẾ & MẸO ĐỐI ĐÁP", [
        "• Dẫn chứng mã nguồn C: `float mean = 0.0f; for(int i=0; i<N; i++) mean += buf[i]; mean /= N; for(int i=0; i<N; i++) buf[i] -= mean;`. Thực hiện mất < 0.1 ms nhưng cứu toàn bộ phổ dải trầm.",
        "• Mẹo: Nếu giảng viên hỏi 'Tại sao không dùng bộ lọc thông cao IIR khử DC?', trả lời: 'Trừ trung bình mẫu trong khung tĩnh N=4096 không gây méo pha và không làm mất tính ổn định như bộ lọc đệ quy IIR'."
    ], border_color=CLR_TECH_BORDER, bg_color=CLR_TECH_BG, title_color=CLR_TECH_BORDER)

    # -------------------------------------------------------------------------
    # NHÓM 4: THỰC TẾ PIANO VÀ BASS-GATE
    # -------------------------------------------------------------------------
    vh.add_heading_2(doc, "🔴 NHÓM 4 — THÁCH THỨC ÂM HỌC PIANO VÀ CƠ CHẾ BASS-GATE")

    # Q11
    add_q_header(doc, "11", "Tại sao các nốt bass như E2 khó nhận diện hơn A4 trong project của nhóm?", "Thách thức âm học Piano")
    add_callout_box(doc, "🎯 MỤC TIÊU CỦA GIẢNG VIÊN & ĐIỂM CHẾT", [
        "• Mục tiêu: Kiểm tra xem sinh viên có trải nghiệm đo đạc thực tế trên đàn piano thật hay chỉ nạp tín hiệu sin lý thuyết.",
        "• Điểm chết: Trả lời chung chung 'do loa dở' hoặc 'do mic dở'."
    ], border_color=CLR_GOAL_BORDER, bg_color=CLR_GOAL_BG, title_color=CLR_GOAL_BORDER)

    add_callout_box(doc, "💬 CÂU TRẢ LỜI MẪU CHUẨN ĐIỂM 10", [
        "\"Thưa thầy, nốt bass E2 (82.41 Hz) khó nhận diện hơn nốt A4 (440 Hz) do 5 nguyên nhân âm học và cơ học thực tế:",
        "1. Năng lượng tần số cơ bản cực kỳ yếu: Dây bass dài và nặng, nhưng thùng đàn upright không đủ diện tích soundboard để bức xạ hiệu quả bước sóng dài 4.1 m của 82 Hz. Thực tế Bảng 5.4 cho thấy biên độ f0 chỉ đạt 1.5 – 7.3.",
        "2. Họa âm bậc cao áp đảo: Họa âm bậc 2 (164 Hz) đạt mag 28.4 (mạnh gấp 4-8 lần f0) và bậc 3 (246 Hz) đạt mag 46.4 (mạnh gấp 10 lần f0!).",
        "3. Hiện tượng bất điều hòa (Inharmonicity) lớn: Dây bass có độ cứng uốn cao, làm các họa âm dạt lên cao hơn bội số nguyên lý thuyết.",
        "4. Gần nguồn nhiễu môi trường: 82 Hz nằm rất sát tần số nhiễu rung cơ học sàn nhà và nhiễu điện lưới 50 Hz.",
        "5. Độ phân giải bin tương đối kém: Với Δf = 3.906 Hz, tại 440 Hz độ rộng bin chỉ chiếm 0.88%, nhưng tại 82 Hz độ rộng bin chiếm tới 4.76% tần số nốt, làm độ bất định cao hơn rất nhiều.\""
    ], border_color=CLR_ANS_BORDER, bg_color=CLR_ANS_BG, title_color=CLR_ANS_BORDER)

    add_callout_box(doc, "🔬 DẪN CHỨNG SỐ LIỆU THỰC TẾ & MẸO ĐỐI ĐÁP", [
        "• Số liệu thực tế Bảng 5.4: Trong 20 khung của E2, có tới 17 khung hệ thống bị năng lượng khổng lồ của họa âm bậc 2 (164 Hz) thu hút, dẫn tới nhảy sang nốt E3 (164.8 Hz).",
        "• Mẹo: Nhấn mạnh công thức bước sóng λ = c / f = 343 / 82.4 ≈ 4.16 m. Một thùng đàn nhỏ không thể cộng hưởng tốt bước sóng 4 mét, giải thích rất thuyết phục theo vật lý âm học."
    ], border_color=CLR_TECH_BORDER, bg_color=CLR_TECH_BG, title_color=CLR_TECH_BORDER)

    # Q12
    add_q_header(doc, "12", "Nhóm đã gặp lỗi E2 thế nào? Đã sửa bằng cách nào và tại sao cách sửa đó hợp lý?", "Bass-Gate Fix", "🔥 CÂU HỎI TRỌNG TÂM SỐ 3")
    add_callout_box(doc, "🎯 MỤC TIÊU CỦA GIẢNG VIÊN & ĐIỂM CHẾT", [
        "• Mục tiêu: Đây là câu hỏi thể hiện rõ nhất năng lực DEBUG và giải quyết vấn đề kỹ thuật của sinh viên.",
        "• Điểm chết: Khẳng định E2 đã bắt đúng 100% (bản gốc ghi nhận đúng 15%!)."
    ], border_color=CLR_GOAL_BORDER, bg_color=CLR_GOAL_BG, title_color=CLR_GOAL_BORDER)

    add_callout_box(doc, "💬 CÂU TRẢ LỜI MẪU CHUẨN ĐIỂM 10", [
        "\"Thưa thầy, trong thử nghiệm Clean Regression Test, nhóm ghi nhận tỷ lệ nhận diện đúng của E2 chỉ đạt 15.0% (3/20 khung), trong 85% khung còn lại hệ thống bị năng lượng cực mạnh của họa âm bậc 2 (164 Hz) kéo lệch thành nốt E3.",
        "• Cách nhóm đã sửa (Cơ chế Bass-Gate Modification):",
        "1. Ban đầu thuật toán áp dụng ngưỡng biên độ cao mag >= 14.0 cho toàn bộ dải trầm, khiến đỉnh f0 yếu của E2 (chỉ đạt 1.5-7.3) bị loại bỏ ngay lập tức.",
        "2. Nhóm đã sửa: Trong vùng 55 – 110 Hz, thuật toán cho phép ứng viên có biên độ nhỏ hơn (chỉ cần max_mag >= 2.5) được xem xét NẾU tổng năng lượng các họa âm hỗ trợ phía sau total_energy >= 3.0.",
        "3. Đồng thời, đối với dải cực trầm < 55 Hz, nhóm vẫn giữ chốt chặn nghiêm ngặt: Bắt buộc phải có tối thiểu 3 họa âm và biên độ >= 14.0, nếu không sẽ bị phạt 85% điểm số.",
        "• Tính hợp lý: Cách sửa này cho phép cứu được tần số cơ bản yếu của E2 khi có bằng chứng họa âm, mà không làm tăng nguy cơ nhận diện sai nhiễu điện lưới 50 Hz thành nốt cực trầm.\""
    ], border_color=CLR_ANS_BORDER, bg_color=CLR_ANS_BG, title_color=CLR_ANS_BORDER)

    add_callout_box(doc, "🔬 DẪN CHỨNG SỐ LIỆU THỰC TẾ & MẸO ĐỐI ĐÁP", [
        "• Số liệu thực tế trong báo cáo: 3 khung bắt đúng E2 cho tần số trung bình 83.160 Hz, std = 0.137 Hz, MAE = 0.750 Hz (15.6 cent).",
        "• Mẹo: Thừa nhận thẳng thắn: 'Cơ chế Bass-Gate giúp thuật toán xem xét được E2, nhưng do họa âm 164 Hz quá mạnh nên hệ thống vẫn bị nhầm 85%. Đây là giới hạn vật lý của FFT 4096 điểm và là hướng phát triển tương lai của nhóm'."
    ], border_color=CLR_TECH_BORDER, bg_color=CLR_TECH_BG, title_color=CLR_TECH_BORDER)

    # Q13
    add_q_header(doc, "13", "Tại sao không đơn giản giảm threshold toàn bộ để E2 dễ nhận diện hơn?", "Adaptive Thresholding")
    add_callout_box(doc, "🎯 MỤC TIÊU CỦA GIẢNG VIÊN & ĐIỂM CHẾT", [
        "• Mục tiêu: Đây là câu hỏi bẫy cực hay. Giảng viên muốn xem bạn có hiểu hậu quả của việc 'hạ ngưỡng toàn cục' không.",
        "• Điểm chết: Đồng ý rằng hạ ngưỡng toàn bộ là giải pháp tốt."
    ], border_color=CLR_GOAL_BORDER, bg_color=CLR_GOAL_BG, title_color=CLR_GOAL_BORDER)

    add_callout_box(doc, "💬 CÂU TRẢ LỜI MẪU CHUẨN ĐIỂM 10", [
        "\"Thưa thầy, hạ threshold toàn bộ là một SAI LẦM KỸ THUẬT NGHIÊM TRỌNG vì sẽ gây ra bùng nổ BÁO ĐỘNG GIẢ (False Positives):",
        "1. Khi ở trạng thái phòng yên tĩnh (không gõ đàn), nhiễu cơ học môi trường và rung chấn bàn đo đạc được ở mức biên độ 7.9 – 13.6 tại các tần số 27 Hz và 39 Hz.",
        "2. Nếu hạ ngưỡng biên độ toàn cục xuống thấp (ví dụ < 4.0), các đỉnh nhiễu này sẽ ngay lập tức bị nhận diện sai thành các nốt cực trầm A0, C1 hoặc E2!",
        "3. Thiết bị sẽ liên tục hiển thị nốt nhảy loạn xạ ngay cả khi phòng hoàn toàn im lặng.",
        "• Do đó, giải pháp khoa học duy nhất là: Giữ nguyên ngưỡng bảo vệ nghiêm ngặt ở vùng nhiễu (< 55 Hz) và chỉ nới lỏng có điều kiện kèm bằng chứng đa họa âm ở dải 55–110 Hz.\""
    ], border_color=CLR_ANS_BORDER, bg_color=CLR_ANS_BG, title_color=CLR_ANS_BORDER)

    add_callout_box(doc, "🔬 DẪN CHỨNG SỐ LIỆU THỰC TẾ & MẸO ĐỐI ĐÁP", [
        "• Số liệu thực nghiệm nhiễu phòng trong Báo cáo Mục 5.3: Nhiễu bàn đạt đỉnh tại 27.3 Hz (mag = 13.6) và 39.1 Hz (mag = 7.9). Ngưỡng bảo vệ < 55 Hz chặn hoàn toàn các đỉnh này.",
        "• Mẹo: Dùng cụm từ 'Cân bằng giữa tỷ lệ bỏ sót (False Negatives) và tỷ lệ báo động giả (False Positives)', thể hiện sự am hiểu sâu sắc về lý thuyết phát hiện tín hiệu."
    ], border_color=CLR_TECH_BORDER, bg_color=CLR_TECH_BG, title_color=CLR_TECH_BORDER)

    # -------------------------------------------------------------------------
    # NHÓM 5: LIÊM CHÍNH HỌC THUẬT VÀ DEBUG
    # -------------------------------------------------------------------------
    vh.add_heading_2(doc, "🔴 NHÓM 5 — ĐÁNH GIÁ LIÊM CHÍNH HỌC THUẬT VÀ KỸ NĂNG DEBUG")

    # Q14
    add_q_header(doc, "14", "Project hiện tại có thực sự đạt yêu cầu độ chính xác < 0.5 Hz trên toàn bộ bàn phím piano không?", "Liêm chính học thuật", "🔥 CÂU HỎI TRỌNG TÂM SỐ 4")
    add_callout_box(doc, "🎯 MỤC TIÊU CỦA GIẢNG VIÊN & ĐIỂM CHẾT", [
        "• Mục tiêu: Giảng viên muốn kiểm tra đạo đức nghiên cứu khoa học. Rất nhiều sinh viên cố trả lời 'Đạt ạ' để rồi bị trừ điểm nặng khi bị hỏi số liệu chứng minh.",
        "• Điểm chết: Tuyên bố bừa bãi rằng đạt < 0.5 Hz trên toàn bộ 88 phím."
    ], border_color=CLR_GOAL_BORDER, bg_color=CLR_GOAL_BG, title_color=CLR_GOAL_BORDER)

    add_callout_box(doc, "💬 CÂU TRẢ LỜI MẪU CHUẨN ĐIỂM 10 (TRẢ LỜI THẲNG THẮN, KHOA HỌC)", [
        "\"Thưa thầy, câu trả lời trung thực nhất là: NHÓM CHƯA THỂ KHẲNG ĐỊNH HỆ THỐNG ĐẠT < 0.5 HZ TRÊN TOÀN BỘ 88 PHÍM PIANO:",
        "1. Những gì đã xác thực thành công (VERIFIED): Nhóm đã đo đạc thực tế trên đàn piano cơ thật và chứng minh hệ thống đạt độ chính xác xuất sắc trên 5 nốt đại diện dải trung âm và cận trầm: A4 (MAE 0.281 Hz), C4 (MAE 0.065 Hz), C5 (MAE 0.188 Hz), D3 (MAE 0.060 Hz) và E3 (MAE 0.054 Hz) — toàn bộ đều có sai số < 0.29 Hz (dưới 1.1 cent) với tỷ lệ nhận diện đúng 100.0%.",
        "2. Những hạn chế thực tế (LIMITED & UNVERIFIED):",
        "   - Tại nốt trầm E2 (82.41 Hz), hệ thống chỉ đạt tỷ lệ nhận diện đúng 15% trong test sạch, 85% khung bị nhầm sang E3.",
        "   - Các dải cực trầm (A0–C2), cực cao (C6–C8) và các hiện tượng cộng hưởng pedal đa âm chưa thu thập đủ mẫu thực nghiệm trên đàn cơ.",
        "• Vì tuân thủ nghiêm ngặt nguyên tắc nghiên cứu thực chứng REAL-DATA ONLY, nhóm đã ghi rõ trong Bảng 6.2 của báo cáo: 'Không tuyên bố hệ thống đạt độ chính xác < 0.5 Hz trên toàn bộ 88 phím khi chưa có đủ dữ liệu kiểm chứng'.\""
    ], border_color=CLR_ANS_BORDER, bg_color=CLR_ANS_BG, title_color=CLR_ANS_BORDER)

    add_callout_box(doc, "🔬 DẪN CHỨNG SỐ LIỆU THỰC TẾ & MẸO ĐỐI ĐÁP", [
        "• Điểm cộng tuyệt đối: Giảng viên đại học đánh giá cao nhất tính trung thực học thuật. Thừa nhận đúng thực tế số liệu đo trong Bảng 5.1 và Bảng 6.2 sẽ giúp bạn ghi điểm trọn vẹn ở phần thái độ nghiên cứu khoa học.",
        "• Mẹo: Nói thêm: 'Nhóm đề xuất giải pháp đa độ phân giải Multi-rate / Downsampling cho dải trầm để giải quyết triệt để vấn đề này trong tương lai'."
    ], border_color=CLR_TECH_BORDER, bg_color=CLR_TECH_BG, title_color=CLR_TECH_BORDER)

    # Q15
    add_q_header(doc, "15", "Nếu thầy đưa một nốt piano mà hệ thống nhận sai một octave, em sẽ kiểm tra những phần nào để tìm nguyên nhân?", "Quy trình Debug chuyên nghiệp", "🔥 CÂU HỎI TRỌNG TÂM SỐ 5")
    add_callout_box(doc, "🎯 MỤC TIÊU CỦA GIẢNG VIÊN & ĐIỂM CHẾT", [
        "• Mục tiêu: Đây là câu hỏi tổng hợp xuất sắc nhất để kết thúc buổi vấn đáp. Giảng viên muốn thấy tư duy của một kỹ sư DSP chuyên nghiệp.",
        "• Điểm chết: Trả lời nhảy cóc 'em vào code sửa lại ngưỡng' mà không biết lỗi nằm ở tầng nào."
    ], border_color=CLR_GOAL_BORDER, bg_color=CLR_GOAL_BG, title_color=CLR_GOAL_BORDER)

    add_callout_box(doc, "💬 CÂU TRẢ LỜI MẪU CHUẨN ĐIỂM 10 (QUY TRÌNH 10 TẦNG CHUẨN DSP)", [
        "\"Thưa thầy, đối với lỗi nhảy quãng tám (Octave Error), em sẽ tuyệt đối không vội vàng sửa code mà tiến hành cô lập lỗi theo quy trình chẩn đoán 10 tầng tín hiệu:",
        "1. Tầng 1 - Kiểm tra I2S thô: Đọc log mẫu số thô, xem tín hiệu có bị bão hòa (clipping) làm méo sóng hay không.",
        "2. Tầng 2 - Mức năng lượng RMS: Kiểm tra ac_rms_norm xem biên độ tín hiệu có vượt ngưỡng phát hiện 0.0020 không.",
        "3. Tầng 3 - Khử DC Offset: Kiểm tra giá trị trung bình μ xem mức DC có bị rò rỉ vào các bin tần số thấp không.",
        "4. Tầng 4 - Phổ biên độ FFT: In mảng mag[k] để xem năng lượng đang tập trung ở bin nào (ví dụ bin của f0 hay bin của 2f0).",
        "5. Tầng 5 - Dò đỉnh phổ (Peak Detection): Kiểm tra xem đỉnh cơ bản f0 có được nhận diện là peak không, hay bị loại bởi ngưỡng mag >= 1.0 hoặc Prominence >= 2.2.",
        "6. Tầng 6 - Tương quan họa âm: So sánh biên độ f1 so với f2/2, f3/3 để xác định đây là lỗi 'nhảy lên quãng tám trên' (2f0 quá mạnh) hay 'nhảy xuống quãng tám dưới' (nhiễu subharmonic).",
        "7. Tầng 7 - Chấm điểm giả thuyết (Hypothesis Scoring): Kiểm tra log điểm số của hàm evaluate_subharmonic_hypothesis() xem giả thuyết f0 đúng bị mất điểm ở tiêu chí nào (thiếu họa âm hay bị phạt bởi Bass-Gate).",
        "8. Tầng 8 - Nội suy Parabol (QI): Kiểm tra giá trị độ lệch p xem đỉnh parabol có bị tính toán sai lệch hay không.",
        "9. Tầng 9 - Ánh xạ nốt (Note Mapping): Kiểm tra công thức n = 69 + 12*log2(f/440) xem tần số ước lượng rơi vào nửa cung nào.",
        "10. Tầng 10 - Bộ lọc làm mịn thời gian (Temporal Smoothing): Kiểm tra bộ đệm 5 khung xem hệ thống có bị kẹt trạng thái khóa nốt cũ (Lock Tolerance 3.5%) của phím vừa bấm trước đó không.\""
    ], border_color=CLR_ANS_BORDER, bg_color=CLR_ANS_BG, title_color=CLR_ANS_BORDER)

    add_callout_box(doc, "🔬 DẪN CHỨNG SỐ LIỆU THỰC TẾ & MẸO ĐỐI ĐÁP", [
        "• Dẫn chứng công cụ debug: Firmware đã tích hợp sẵn log UART định kỳ in chi tiết các giá trị `rms`, `k_peak`, `mag_peak`, `f_est`, `note`, `cents`, `confidence`. Bật log cấp độ DEBUG là có thể định vị chính xác lỗi trong 30 giây.",
        "• Mẹo: Câu trả lời này thể hiện phương pháp luận kỹ thuật bài bản của một kỹ sư thực thụ, chắc chắn sẽ kết thúc buổi bảo vệ với điểm số xuất sắc."
    ], border_color=CLR_TECH_BORDER, bg_color=CLR_TECH_BG, title_color=CLR_TECH_BORDER)

    # =========================================================================
    # PHẦN III: BẢNG SỐ LIỆU NẰM LÒNG KHI VÀO PHÒNG BẢO VỆ
    # =========================================================================
    vh.add_heading_1(doc, "PHẦN III — BẢNG SỐ LIỆU THỰC NGHIỆM CỐT LÕI CẦN HỌC THUỘC LÒNG", is_chapter=False)
    
    vh.add_p(doc, 
        "Khi trả lời vấn đáp, việc nhớ chính xác các con số thực nghiệm trong bài báo cáo sẽ tạo ấn tượng cực kỳ mạnh mẽ "
        "với giảng viên rằng bạn chính là tác giả trực tiếp thực hiện thí nghiệm:", indent=0.3)
    
    vh.add_heading_2(doc, "BẢNG III.1 — KẾT QUẢ ĐO ĐẠC THỰC NGHIỆM TRÊN ĐÀN PIANO THẬT (CLEAN REGRESSION)")
    tbl_num = doc.add_table(rows=1, cols=6)
    tbl_num.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_num.autofit = False
    vh.set_table_borders(tbl_num)
    
    t_w = [Inches(0.9), Inches(1.1), Inches(1.1), Inches(1.1), Inches(1.1), Inches(1.2)]
    t_hdrs = ["Nốt nhạc", "Tần số chuẩn", "Trung bình đo", "Sai số MAE", "MAE (cent)", "Tỷ lệ đúng"]
    for idx, text in enumerate(t_hdrs):
        c = tbl_num.rows[0].cells[idx]
        c.width = t_w[idx]
        vh.set_cell_background(c, "EAECEF")
        vh.set_cell_margins(c, top=60, bottom=60, left=40, right=40)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(9.5)
        r.bold = True
        
    num_data = [
        ("A4", "440.000 Hz", "440.281 Hz", "0.281 Hz", "1.10 cent", "100.0%"),
        ("C4", "261.626 Hz", "261.674 Hz", "0.065 Hz", "0.43 cent", "100.0%"),
        ("C5", "523.251 Hz", "523.438 Hz", "0.188 Hz", "0.62 cent", "100.0%"),
        ("D3", "146.832 Hz", "146.797 Hz", "0.060 Hz", "0.71 cent", "100.0%"),
        ("E3", "164.814 Hz", "164.787 Hz", "0.054 Hz", "0.57 cent", "100.0%"),
        ("E2", "82.407 Hz", "83.160 Hz", "0.750 Hz", "15.6 cent", "15.0% (3/20)*"),
    ]
    for r_data in num_data:
        row = tbl_num.add_row()
        for idx, text in enumerate(r_data):
            c = row.cells[idx]
            c.width = t_w[idx]
            vh.set_cell_margins(c, top=40, bottom=40, left=40, right=40)
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx in [0, 5] else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            if idx == 0:
                r.bold = True
            if "15.0%" in text:
                r.font.color.rgb = RGBColor(180, 20, 20)
                r.bold = True
                
    vh.make_table_responsive(tbl_num)
    
    p_n = doc.add_paragraph()
    p_n.paragraph_format.space_before = Pt(3)
    p_n.paragraph_format.space_after = Pt(8)
    r_nt = p_n.add_run("(* Ghi chú: Nốt E2 có 85% số khung bị nhận nhầm sang E3 do họa âm bậc 2 164 Hz quá mạnh).")
    r_nt.font.name = "Times New Roman"
    r_nt.font.size = Pt(9)
    r_nt.italic = True
    r_nt.font.color.rgb = RGBColor(100, 100, 100)

    # Timing metrics summary
    vh.add_heading_2(doc, "BẢNG III.2 — CÁC MỐC THỜI GIAN, ĐỘ TRỄ VÀ TÀI NGUYÊN HỆ THỐNG")
    add_callout_box(doc, "⏱️ CÁC THÔNG SỐ ĐỘ TRỄ THỜI GIAN THỰC CẦN NHỚ", [
        "• Thời gian tính toán DSP thuần túy (Core 0): 23.56 – 25.37 ms (Đo bằng esp_timer_get_time).",
        "• Tải chiếm dụng CPU của tác vụ DSP: Xấp xỉ 18.5% (Dư thừa > 80% cho Wi-Fi & Web).",
        "• Chu kỳ bước nhảy đệm DMA (Hop interval): 128.0 ms (Thu nhận 2 048 mẫu I2S mới).",
        "• Chiều dài khung phân tích thời gian (Frame length): 256.0 ms (N = 4 096 mẫu tại Fs = 16 kHz).",
        "• Thời gian đáp ứng nốt tối thiểu (Fast Lock): 256.0 ms (2 khung liên tiếp để bộ lọc ổn định).",
        "• Chu kỳ gửi request Web Polling: 125.0 ms (JavaScript client gửi fetch định kỳ).",
        "• Tổng độ trễ phản hồi thị giác: 150 – 280 ms (Hoàn toàn thỏa mãn yêu cầu phản hồi < 500 ms)."
    ], border_color=CLR_SECONDARY, bg_color="EBF8FF", title_color=CLR_SECONDARY)

    # DSP Glossary
    vh.add_heading_2(doc, "BẢNG III.3 — TỪ ĐIỂN THUẬT NGỮ DSP CHUYÊN NGÀNH SONG NGỮ (GLOSSARY)")
    vh.add_p(doc, "Sử dụng chính xác các thuật ngữ dưới đây sẽ giúp câu trả lời mang đậm phong cách chuyên gia:", indent=0.3)
    
    tbl_lex = doc.add_table(rows=1, cols=3)
    tbl_lex.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_lex.autofit = False
    vh.set_table_borders(tbl_lex)
    
    w_lex = [Inches(1.8), Inches(1.8), Inches(2.9)]
    h_lex = ["Thuật ngữ tiếng Anh", "Thuật ngữ tiếng Việt", "Ý nghĩa trong đồ án"]
    for idx, text in enumerate(h_lex):
        c = tbl_lex.rows[0].cells[idx]
        c.width = w_lex[idx]
        vh.set_cell_background(c, "EAECEF")
        vh.set_cell_margins(c, top=60, bottom=60, left=40, right=40)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(9.5)
        r.bold = True
        
    lex_data = [
        ("Signal Chain", "Chuỗi xử lý tín hiệu", "Toàn bộ chuỗi 10 mắt xích từ mic I2S đến giao diện Web"),
        ("Spectral Leakage", "Rò rỉ phổ", "Năng lượng tràn sang các bin lân cận, được giảm nhờ cửa sổ Hann"),
        ("Missing Fundamental", "Thiếu tần số cơ bản", "Đặc tính nốt trầm piano: năng lượng f0 yếu, họa âm áp đảo"),
        ("Quadratic Interpolation (QI)", "Nội suy Parabol bậc hai", "Xấp xỉ đỉnh liên tục từ 3 bin rời rạc để đạt độ mịn tần số"),
        ("Subharmonic Hypothesis", "Giả thuyết tần số ước số", "Sinh các giả thuyết f_hyp = f_peak / m để tìm tần số gốc"),
        ("Harmonic Consistency", "Sự nhất quán họa âm", "Tiêu chí chấm điểm thưởng dựa trên số lượng họa âm tìm thấy"),
        ("Inharmonicity", "Hiện tượng bất điều hòa", "Độ cứng dây đàn làm họa âm dạt cao hơn bội số nguyên"),
        ("Bass-Gate Mechanism", "Cơ chế cổng bảo vệ nốt trầm", "Chốt chặn chống nhiễu 50Hz nhưng cứu nốt trầm khi có họa âm"),
        ("Octave Error", "Lỗi nhảy quãng tám", "Nhận nhầm f0 thành 2f0 (nhảy lên) hoặc f0/2 (nhảy xuống)"),
        ("Cents Deviation", "Độ lệch Cent", "Đơn vị logarit chia nửa cung thành 100 phần: 1200*log2(f/f0)"),
    ]
    for r_data in lex_data:
        row = tbl_lex.add_row()
        for idx, text in enumerate(r_data):
            c = row.cells[idx]
            c.width = w_lex[idx]
            vh.set_cell_margins(c, top=40, bottom=40, left=40, right=40)
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.0)
            if idx == 0:
                r.bold = True
                
    vh.make_table_responsive(tbl_lex)

    # Final Defense Mindset Callout
    add_callout_box(doc, "★ LỜI KHUYÊN CUỐI CÙNG VỀ TÂM LÝ & PHONG THÁI BẢO VỆ", [
        "1. Luôn bình tĩnh, lắng nghe trọn vẹn câu hỏi của thầy cô trước khi trả lời. Nếu câu hỏi dài, hãy tóm tắt lại ý chính: 'Dạ thưa thầy, thầy đang hỏi về lý do tại sao...' để có 3 giây định hình cấu trúc câu trả lời.",
        "2. Không nói vòng vo: Hãy đưa ra kết luận cốt lõi ngay trong câu đầu tiên, sau đó mới giải thích các luận điểm 1, 2, 3 bằng dẫn chứng số liệu thực tế.",
        "3. Tôn trọng sự thật khoa học: Khi gặp câu hỏi về hạn chế của đề tài (như E2 hay dải cực trầm), đừng tìm cách ngụy biện hay né tránh. Thừa nhận thẳng thắn và trình bày nguyên nhân âm học cùng hướng cải tiến sẽ biến một điểm yếu thành cơ hội ghi điểm xuất sắc về tư duy nghiên cứu!",
        "4. Chúc bạn có một buổi bảo vệ tiểu luận thành công rực rỡ và đạt điểm số tối đa!"
    ], border_color="D69E2E", bg_color="FEFCBF", title_color="975A16")

    # Save initial docx
    print(f"Saving compiled docx to {DOCX_OUT}...")
    doc.save(DOCX_OUT)
    print("Docx saved successfully.")
    
    # Also save to workspace
    doc.save(DOCX_WORKSPACE)
    print(f"Copied backup docx to {DOCX_WORKSPACE}.")

if __name__ == "__main__":
    build_document()
