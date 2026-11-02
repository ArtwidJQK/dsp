# -*- coding: utf-8 -*-
"""
Frontmatter module for LeTanDung_24150654_v2.docx
Generates:
1. Cover page (Bìa) - with '[CẦN BỔ SUNG: họ tên GVHD]' and clean academic layout.
2. Section Break to Frontmatter.
3. TÓM TẮT (200-250 words, concise, corrected harmonic 3).
4. ABSTRACT (200-250 words, matching English).
5. MỤC LỤC (Automatic TOC field).
6. DANH MỤC HÌNH VẼ (Automatic List of Figures field).
7. DANH MỤC BẢNG BIỂU (Automatic List of Tables field).
8. DANH MỤC TỪ VIẾT TẮT (Table of Abbreviations).
"""

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

import v2_helpers as vh

def build_frontmatter(doc):
    # =========================================================================
    # 1. TRANG BÌA (COVER PAGE)
    # =========================================================================
    p1 = doc.add_paragraph()
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p1.paragraph_format.space_before = Pt(0)
    p1.paragraph_format.space_after = Pt(2)
    r1 = p1.add_run("ĐẠI HỌC QUỐC GIA THÀNH PHỐ HỒ CHÍ MINH\nTRƯỜNG ĐẠI HỌC BÁCH KHOA\nKHOA ĐIỆN - ĐIỆN TỬ")
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(13)
    r1.bold = True
    r1.font.color.rgb = RGBColor(0, 0, 0)

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.paragraph_format.space_before = Pt(0)
    p2.paragraph_format.space_after = Pt(16)
    r2 = p2.add_run("BỘ MÔN VIỄN THÔNG - XỬ LÝ TÍN HIỆU")
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(12)
    r2.bold = True
    r2.font.color.rgb = RGBColor(0, 0, 0)

    # Decorative dividing line
    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_line.paragraph_format.space_before = Pt(0)
    p_line.paragraph_format.space_after = Pt(40)
    r_line = p_line.add_run("─────────── ★ ───────────")
    r_line.font.name = "Times New Roman"
    r_line.font.size = Pt(11)
    r_line.font.color.rgb = RGBColor(60, 60, 60)

    # Document Type & Title
    p_type = doc.add_paragraph()
    p_type.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_type.paragraph_format.space_before = Pt(0)
    p_type.paragraph_format.space_after = Pt(12)
    r_type = p_type.add_run("BÁO CÁO TIỂU LUẬN MÔN HỌC\nXỬ LÝ TÍN HIỆU SỐ\n[CẦN BỔ SUNG: Mã học phần]")
    r_type.font.name = "Times New Roman"
    r_type.font.size = Pt(14)
    r_type.bold = True
    r_type.font.color.rgb = RGBColor(0, 0, 0)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(16)
    p_title.paragraph_format.space_after = Pt(8)
    p_title.paragraph_format.line_spacing = 1.3
    r_title = p_title.add_run("THIẾT KẾ THIẾT BỊ LÊN DÂY ĐÀN PIANO CHROMATIC\nSỬ DỤNG VI ĐIỀU KHIỂN ESP32-S3\nVÀ MICROPHONE MEMS I2S INMP441")
    r_title.font.name = "Times New Roman"
    r_title.font.size = Pt(17)
    r_title.bold = True
    r_title.font.color.rgb = RGBColor(0, 0, 0)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(6)
    p_sub.paragraph_format.space_after = Pt(60)
    r_sub = p_sub.add_run("Đề tài: Nghiên cứu và hiện thực thuật toán ước lượng cao độ âm thanh piano thời gian thực")
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(12)
    r_sub.italic = True
    r_sub.font.color.rgb = RGBColor(40, 40, 40)

    # Student & Advisor Box
    tbl_meta = doc.add_table(rows=4, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_meta.autofit = False

    meta_w = [Inches(2.2), Inches(3.8)]
    meta_data = [
        ("Giảng viên hướng dẫn:", "[CẦN BỔ SUNG: họ tên GVHD]"),
        ("Sinh viên thực hiện:", "Lê Tấn Dũng"),
        ("Mã số sinh viên (MSSV):", "24150654"),
        ("Ngành / Lớp học phần:", "Kỹ thuật Điện tử - Viễn thông | [CẦN BỔ SUNG: Mã lớp học phần]"),
    ]

    for row_idx, (k, v) in enumerate(meta_data):
        row = tbl_meta.rows[row_idx]
        vh.set_cell_margins(row.cells[0], top=60, bottom=60, left=80, right=80)
        vh.set_cell_margins(row.cells[1], top=60, bottom=60, left=80, right=80)
        row.cells[0].width = meta_w[0]
        row.cells[1].width = meta_w[1]

        p_k = row.cells[0].paragraphs[0]
        p_k.paragraph_format.space_before = Pt(0)
        p_k.paragraph_format.space_after = Pt(0)
        r_k = p_k.add_run(k)
        r_k.font.name = "Times New Roman"
        r_k.font.size = Pt(12)
        r_k.bold = True
        r_k.font.color.rgb = RGBColor(0, 0, 0)

        p_v = row.cells[1].paragraphs[0]
        p_v.paragraph_format.space_before = Pt(0)
        p_v.paragraph_format.space_after = Pt(0)
        r_v = p_v.add_run(v)
        r_v.font.name = "Times New Roman"
        r_v.font.size = Pt(12)
        if "[CẦN BỔ SUNG" in v:
            r_v.bold = True
            r_v.font.color.rgb = RGBColor(180, 20, 20)
        else:
            r_v.font.color.rgb = RGBColor(0, 0, 0)

    # Remove borders
    for row in tbl_meta.rows:
        for cell in row.cells:
            tcPr = cell._tc.get_or_add_tcPr()
            borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="none"/><w:right w:val="none"/><w:top w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
            tcPr.append(borders)

    # Footer on Cover
    p_loc = doc.add_paragraph()
    p_loc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_loc.paragraph_format.space_before = Pt(80)
    p_loc.paragraph_format.space_after = Pt(0)
    r_loc = p_loc.add_run("THÀNH PHỐ HỒ CHÍ MINH — THÁNG 10 NĂM 2026")
    r_loc.font.name = "Times New Roman"
    r_loc.font.size = Pt(12)
    r_loc.bold = True
    r_loc.font.color.rgb = RGBColor(0, 0, 0)

    # =========================================================================
    # SECTION BREAK -> SECTION 2 (FRONTMATTER)
    # =========================================================================
    doc.add_section(docx.enum.section.WD_SECTION.NEW_PAGE)
    sec2 = doc.sections[1]
    sec2.header.is_linked_to_previous = False
    sec2.footer.is_linked_to_previous = False

    # Header for Section 2
    hp2 = sec2.header.paragraphs[0]
    hp2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hrun2 = hp2.add_run("TIỂU LUẬN KỸ THUẬT: THIẾT KẾ THIẾT BỊ LÊN DÂY ĐÀN PIANO CHROMATIC")
    hrun2.font.name = "Times New Roman"
    hrun2.font.size = Pt(9)
    hrun2.font.italic = True
    hrun2.font.color.rgb = RGBColor(80, 80, 80)

    # Footer for Section 2: Lowercase Roman numerals (i, ii, iii...)
    fp2 = sec2.footer.paragraphs[0]
    fp2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    vh.add_toc_field(fp2, 'PAGE \\* roman')
    # Set page number format
    sectPr2 = sec2._sectPr
    pgNumType2 = OxmlElement('w:pgNumType')
    pgNumType2.set(docx.oxml.ns.qn('w:fmt'), 'roman')
    pgNumType2.set(docx.oxml.ns.qn('w:start'), '1')
    sectPr2.append(pgNumType2)

    # =========================================================================
    # TÓM TẮT (VIETNAMESE ABSTRACT)
    # =========================================================================
    vh.add_heading_1(doc, "TÓM TẮT", is_chapter=False)

    vh.add_p(doc,
        "Tiểu luận kỹ thuật trình bày thiết kế và hiện thực thiết bị lên dây đàn piano chromatic đơn âm thời gian thực "
        "trên vi điều khiển ESP32-S3 kết hợp microphone MEMS kỹ thuật số I2S INMP441. Hệ thống giải quyết thách thức âm học phức tạp "
        "của đàn piano cơ gồm tính bất điều hòa (inharmonicity) của dây đàn và hiện tượng suy giảm năng lượng tần số cơ bản (f_0) ở dải trầm. "
        "Chuỗi xử lý tín hiệu DSP tối ưu bằng C/C++ thuần trong ESP-IDF gồm: thu nhận I2S DMA ở tần số lấy mẫu 16 000 Hz, phân tích khung 4 096 mẫu "
        "(hop size 2 048 mẫu, 128 ms), khử DC, cửa sổ Hann tuần hoàn, FFT Radix-2 4 096 điểm (độ phân giải bin 3.90625 Hz), lọc sàn nhiễu trung vị 24 bin, "
        "chấm điểm giả thuyết họa âm và nội suy đỉnh parabol bậc hai (QI). "
        "Thực nghiệm đo đạc trực tiếp trên đàn piano cơ thật đã ghi nhận độ chính xác cao trên 5 nốt kiểm chứng thuộc dải trung âm và cận trầm "
        "(tỷ lệ bắt đúng nốt đạt 100.0%): A4 (440.00 Hz) đạt mean 440.281 Hz, std 0.096 Hz, MAE 0.281 Hz (1.10 cent); "
        "C4 (261.63 Hz) đạt mean 261.674 Hz, std 0.064 Hz, MAE 0.065 Hz (0.43 cent); "
        "C5 (523.25 Hz) đạt mean 523.438 Hz, std 0.020 Hz, MAE 0.188 Hz (0.62 cent); "
        "D3 (146.83 Hz) đạt mean 146.797 Hz, std 0.074 Hz, MAE 0.060 Hz (0.71 cent); "
        "E3 (164.81 Hz) đạt mean 164.787 Hz, std 0.065 Hz, MAE 0.054 Hz (0.57 cent). "
        "Độ trễ tính toán DSP thuần túy đo được trên phần cứng là 23.56 đến 25.37 ms với mức chiếm dụng CPU xấp xỉ 18.5%. "
        "Kiểm thử tự động giao diện web qua Chrome DevTools Protocol (CDP) ghi nhận 0 lỗi JavaScript và giao diện co giãn đạt chuẩn trên 8 độ phân giải "
        "(chưa xác minh trên điện thoại vật lý). Theo nguyên tắc nghiên cứu thực chứng (REAL-DATA ONLY), báo cáo khẳng định rõ: "
        "hệ thống chưa đủ dữ liệu để tuyên bố độ chính xác < 0.5 Hz trên toàn bộ 88 phím piano. Tại nốt trầm E2 (82.41 Hz), năng lượng f_0 rất yếu "
        "(biên độ 1.5–7.3 so với 46.4 của họa âm bậc 3), dẫn đến tỷ lệ bắt đúng nốt chỉ đạt 15.0% (3/20 khung, mean 83.160 Hz, std 0.137 Hz, MAE 0.750 Hz) "
        "và 85% khung bị nhầm quãng tám sang E3. Các dải phím cực trầm (A0–C2), cực cao (C6–C8) và hợp âm polyphonic pedal được phân định minh bạch là CHƯA ĐƯỢC XÁC MINH.",
        indent=0.394)

    vh.add_p(doc,
        "Từ khóa: Xử lý tín hiệu số, ESP32-S3, INMP441, I2S, FFT, Cửa sổ Hann, Quadratic Interpolation, Harmonic-Aware Detection, Piano Chromatic Tuner, Cents Deviation, Real-Data Only.",
        indent=0.394, bold=False, italic=True)

    # =========================================================================
    # ABSTRACT (ENGLISH)
    # =========================================================================
    vh.add_heading_1(doc, "ABSTRACT", is_chapter=False)

    vh.add_p(doc,
        "This technical report presents the comprehensive design, digital signal processing (DSP) pipeline architecture, and empirical validation "
        "of an autonomous, embedded real-time Single-Note Piano Chromatic Tuner utilizing an ESP32-S3 microcontroller and an INMP441 digital I2S MEMS microphone. "
        "Acoustic piano pitch detection presents distinct challenges due to string inharmonicity and severe fundamental frequency (f_0) attenuation in bass registers, "
        "where higher harmonics dominate the energy spectrum. Implemented in native C/C++ within ESP-IDF, the pipeline features: 16 kHz I2S DMA acquisition, "
        "a 50% overlapping rolling buffer (N = 4096 samples, hop = 2048 samples, 128 ms), DC removal, periodic Hann windowing, Radix-2 DIT FFT (df = 3.90625 Hz), "
        "24-bin neighborhood median noise floor filtering, harmonic-aware hypothesis scoring, 3-point parabolic Quadratic Interpolation (QI), a 2-frame fast-lock temporal filter, "
        "and equal-temperament cents deviation mapping. Results are served asynchronously via an embedded HTTP server to a responsive HTML5/CSS3/Vanilla JS interface. "
        "Acoustic validation on a real acoustic piano confirmed 100.0% correct identification across 5 verified test notes: "
        "A4 (mean 440.281 Hz, std 0.096 Hz, MAE 0.281 Hz, 1.10 cents), C4 (mean 261.674 Hz, std 0.064 Hz, MAE 0.065 Hz, 0.43 cents), "
        "C5 (mean 523.438 Hz, std 0.020 Hz, MAE 0.188 Hz, 0.62 cents), D3 (mean 146.797 Hz, std 0.074 Hz, MAE 0.060 Hz, 0.71 cents), and "
        "E3 (mean 164.787 Hz, std 0.065 Hz, MAE 0.054 Hz, 0.57 cents). Dedicated DSP computation latency was benchmarked at 23.56 to 25.37 ms with ~18.5% CPU load. "
        "Headless Chrome CDP automation validated 0 JavaScript errors and seamless responsive fitting across 8 viewports (not yet verified on physical mobile hardware). "
        "Under strict real-data integrity guidelines, system-wide <0.5 Hz accuracy across the full 88-key compass cannot be claimed. At lower registers (specifically E2 ~ 82.41 Hz), "
        "weak fundamental excitation (magnitude 1.5–7.3 vs. 46.4 for the 3rd harmonic) yielded a 15.0% correct detection rate (3/20 frames, mean 83.160 Hz, std 0.137 Hz, MAE 0.750 Hz) "
        "with 85% octave-jumping errors to E3. Unmeasured compass limits (A0–C2, C6–C8) and polyphonic pedal resonances remain explicitly designated as NOT VERIFIED.",
        indent=0.394)

    vh.add_p(doc,
        "Keywords: Digital signal processing, ESP32-S3, INMP441, I2S, FFT, Hann window, Quadratic Interpolation, Harmonic-Aware Detection, Piano Chromatic Tuner, Cents Deviation, Real-Data Only.",
        indent=0.394, bold=False, italic=True)

    # =========================================================================
    # MỤC LỤC (AUTOMATIC TOC)
    # =========================================================================
    vh.add_heading_1(doc, "MỤC LỤC", is_chapter=False)
    p_toc = doc.add_paragraph()
    p_toc.paragraph_format.space_before = Pt(6)
    p_toc.paragraph_format.space_after = Pt(12)
    vh.add_toc_field(p_toc, 'TOC \\o "1-3" \\h \\z \\u')

    # =========================================================================
    # DANH MỤC HÌNH VẼ (AUTOMATIC LIST OF FIGURES)
    # =========================================================================
    vh.add_heading_1(doc, "DANH MỤC HÌNH VẼ", is_chapter=False)
    p_lof = doc.add_paragraph()
    p_lof.paragraph_format.space_before = Pt(6)
    p_lof.paragraph_format.space_after = Pt(12)
    vh.add_toc_field(p_lof, 'TOC \\t "FigureCaption,1" \\h \\z')

    # =========================================================================
    # DANH MỤC BẢNG BIỂU (AUTOMATIC LIST OF TABLES)
    # =========================================================================
    vh.add_heading_1(doc, "DANH MỤC BẢNG BIỂU", is_chapter=False)
    p_lot = doc.add_paragraph()
    p_lot.paragraph_format.space_before = Pt(6)
    p_lot.paragraph_format.space_after = Pt(12)
    vh.add_toc_field(p_lot, 'TOC \\t "TableCaption,1" \\h \\z')

    # =========================================================================
    # DANH MỤC TỪ VIẾT TẮT (ABBREVIATIONS)
    # =========================================================================
    vh.add_heading_1(doc, "DANH MỤC TỪ VIẾT TẮT", is_chapter=False)

    p_abbr_cap = doc.add_paragraph()
    p_abbr_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_abbr_cap.paragraph_format.space_before = Pt(8)
    p_abbr_cap.paragraph_format.space_after = Pt(4)
    r_ac = p_abbr_cap.add_run("Bảng 0.1: Danh mục các ký hiệu và thuật ngữ viết tắt trong báo cáo")
    r_ac.font.name = "Times New Roman"
    r_ac.font.size = Pt(11)
    r_ac.font.italic = True

    tbl_abbr = doc.add_table(rows=1, cols=3)
    tbl_abbr.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_abbr.autofit = False
    vh.set_table_borders(tbl_abbr)

    abbr_w = [Inches(1.0), Inches(2.0), Inches(3.3)]
    headers = ["Ký hiệu", "Thuật ngữ tiếng Anh", "Ý nghĩa / Định nghĩa tiếng Việt"]

    hdr_row = tbl_abbr.rows[0]
    for idx, h_text in enumerate(headers):
        cell = hdr_row.cells[idx]
        cell.width = abbr_w[idx]
        vh.set_cell_background(cell, "EAECEF")
        vh.set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h_text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.bold = True

    abbr_data = [
        ("ADC", "Analog-to-Digital Converter", "Bộ chuyển đổi tín hiệu tương tự sang số"),
        ("AGC", "Automatic Gain Control", "Tự động điều khiển độ lợi thu âm"),
        ("CDP", "Chrome DevTools Protocol", "Giao thức truyền thông điều khiển trình duyệt"),
        ("DFT", "Discrete Fourier Transform", "Biến đổi Fourier rời rạc"),
        ("DMA", "Direct Memory Access", "Truy cập bộ nhớ trực tiếp không qua CPU"),
        ("DSP", "Digital Signal Processing", "Xử lý tín hiệu số"),
        ("FFT", "Fast Fourier Transform", "Biến đổi Fourier nhanh"),
        ("FreeRTOS", "Real-Time Operating System", "Hệ điều hành thời gian thực mã nguồn mở"),
        ("GPIO", "General Purpose Input/Output", "Chân vào/ra đa dụng của vi điều khiển"),
        ("HPS", "Harmonic Product Spectrum", "Phổ tích họa âm"),
        ("I2S", "Inter-IC Sound", "Chuẩn giao tiếp nối tiếp cho âm thanh số"),
        ("ISR", "Interrupt Service Routine", "Chương trình phục vụ ngắt"),
        ("MAE", "Mean Absolute Error", "Sai số tuyệt đối trung bình"),
        ("MEMS", "Micro-Electro-Mechanical Systems", "Hệ thống vi cơ điện tử"),
        ("MIDI", "Musical Instrument Digital Interface", "Giao diện số kết nối nhạc cụ"),
        ("QI", "Quadratic Interpolation", "Nội suy parabol bậc hai"),
        ("RMS", "Root Mean Square", "Giá trị căn bậc hai trung bình bình phương (năng lượng)"),
        ("SIMD", "Single Instruction Multiple Data", "Đơn lệnh đa dữ liệu (xử lý vector)"),
        ("SNR", "Signal-to-Noise Ratio", "Tỷ số tín hiệu trên nhiễu"),
        ("12-TET", "12-Tone Equal Temperament", "Hệ âm đo bình quân 12 cung đều"),
        ("YIN", "YIN Pitch Estimation Algorithm", "Thuật toán ước lượng cao độ trong miền thời gian"),
    ]

    for item in abbr_data:
        row = tbl_abbr.add_row()
        for idx, text in enumerate(item):
            cell = row.cells[idx]
            cell.width = abbr_w[idx]
            vh.set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            if idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            elif idx == 1:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            r = p.add_run(text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(11)
            if idx == 0:
                r.bold = True

    vh.make_table_responsive(tbl_abbr)

print("v2_frontmatter module ready.")
