# -*- coding: utf-8 -*-
"""
Frontmatter module: Cover page, Abstracts, Lists of tables/figures/abbreviations.
"""

from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

import make_doc as md

def build_frontmatter(doc):
    # =========================================================================
    # 1. TRANG BÌA (COVER PAGE)
    # =========================================================================
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(0)
    p_inst.paragraph_format.space_after = Pt(2)
    r = p_inst.add_run("ĐẠI HỌC QUỐC GIA THÀNH PHỐ HỒ CHÍ MINH\nTRƯỜNG ĐẠI HỌC BÁCH KHOA\nKHOA ĐIỆN - ĐIỆN TỬ")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.bold = True
    r.font.color.rgb = md.C_NAVY

    p_dep = doc.add_paragraph()
    p_dep.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dep.paragraph_format.space_before = Pt(0)
    p_dep.paragraph_format.space_after = Pt(24)
    r = p_dep.add_run("BỘ MÔN VIỄN THÔNG - XỬ LÝ TÍN HIỆU")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.bold = True
    r.font.color.rgb = md.C_NAVY

    # Decorative line
    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_line.paragraph_format.space_before = Pt(0)
    p_line.paragraph_format.space_after = Pt(36)
    r = p_line.add_run("-----------------------***-----------------------")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.color.rgb = md.C_MUTED

    p_type = doc.add_paragraph()
    p_type.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_type.paragraph_format.space_before = Pt(12)
    p_type.paragraph_format.space_after = Pt(12)
    r = p_type.add_run("BÁO CÁO TIỂU LUẬN KỸ THUẬT CUỐI KỲ\nMÔN HỌC: XỬ LÝ TÍN HIỆU SỐ (DSP)")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.bold = True
    r.font.color.rgb = md.C_BLUE

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(18)
    p_title.paragraph_format.space_after = Pt(18)
    r = p_title.add_run("ĐỀ TÀI:\nTHIẾT KẾ VÀ TRIỂN KHAI BỘ LÊN DÂY ĐÀN PIANO CHROMATIC THỜI GIAN THỰC SỬ DỤNG ESP32-S3 VÀ MICROPHONE MEMS I2S INMP441")
    r.font.name = "Times New Roman"
    r.font.size = Pt(17)
    r.bold = True
    r.font.color.rgb = md.C_NAVY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(48)
    r = p_sub.add_run("(PIANO CHROMATIC TUNER USING ESP32-S3 AND INMP441)")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.italic = True
    r.font.color.rgb = md.C_MUTED

    # Student info table
    tbl_info = doc.add_table(rows=4, cols=2)
    tbl_info.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_info.autofit = False
    col_w = [Inches(2.4), Inches(3.6)]
    info_data = [
        ("Sinh viên thực hiện:", "LÊ TẤN DŨNG"),
        ("Mã số sinh viên (MSSV):", "24150654"),
        ("Lớp / Chuyên ngành:", "Kỹ thuật Điện - Điện tử / Xử lý tín hiệu"),
        ("Giảng viên hướng dẫn:", "Bộ môn Viễn thông & Xử lý tín hiệu số")
    ]
    for r_idx, (k, v) in enumerate(info_data):
        c0 = tbl_info.rows[r_idx].cells[0]
        c1 = tbl_info.rows[r_idx].cells[1]
        c0.width, c1.width = col_w[0], col_w[1]
        md.set_cell_margins(c0, 60, 60, 80, 80)
        md.set_cell_margins(c1, 60, 60, 80, 80)
        
        # Borderless
        for cell in (c0, c1):
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="none"/><w:right w:val="none"/><w:top w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
            tcPr.append(tcBorders)
            
        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r0 = p0.add_run(k)
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(12.5)
        r0.bold = True
        r0.font.color.rgb = md.C_TEXT
        
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r1 = p1.add_run(v)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(12.5)
        r1.bold = (r_idx < 2)
        r1.font.color.rgb = md.C_NAVY if (r_idx < 2) else md.C_TEXT

    p_loc = doc.add_paragraph()
    p_loc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_loc.paragraph_format.space_before = Pt(64)
    p_loc.paragraph_format.space_after = Pt(0)
    r = p_loc.add_run("THÀNH PHỐ HỒ CHÍ MINH, THÁNG 10 NĂM 2026")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.bold = True
    r.font.color.rgb = md.C_NAVY

    doc.add_page_break()

    # =========================================================================
    # 2. TÓM TẮT & ABSTRACT
    # =========================================================================
    md.add_heading_1(doc, "TÓM TẮT ĐỀ TÀI")
    
    md.add_p(doc, 
        "Tiểu luận kỹ thuật này trình bày toàn diện quá trình nghiên cứu, thiết kế phần cứng, xây dựng "
        "pipeline xử lý tín hiệu số (DSP) và triển khai thực nghiệm thiết bị lên dây đàn piano chromatic đơn âm "
        "(Single-Note Piano Chromatic Tuner) hoạt động thời gian thực trên nền tảng vi điều khiển ESP32-S3 N16R8 "
        "kết hợp cảm biến microphone MEMS giao tiếp I2S INMP441.", indent=0.4)

    md.add_p(doc, 
        "Trong âm học đàn piano cơ, việc xác định chính xác cao độ của từng phím đàn là một bài toán phức tạp do "
        "tính chất bất điều hòa (inharmonicity) của dây đàn thép kéo căng và hiện tượng suy giảm năng lượng tần số cơ bản "
        "(fundamental frequency f0) ở dải trầm, nơi các họa âm bậc 2, 3, 4 có biên độ vượt trội so với f0. Để giải quyết "
        "vấn đề này mà không phụ thuộc vào các thư viện bên thứ ba của Arduino hay thư viện đồ họa cồng kềnh, hệ thống "
        "đã xây dựng một pipeline DSP tối ưu hoàn toàn trên nền tảng ESP-IDF và ngôn ngữ C/C++. Pipeline bao gồm: "
        "thu nhận dữ liệu âm thanh số qua DMA I2S (tần số lấy mẫu Fs = 16.000 Hz), bộ đệm trượt 50% gối đầu (hop size 2.048 mẫu, "
        "độ dài khung N = 4.096 mẫu tương ứng 256 ms), loại bỏ mức offset một chiều (DC removal), nhân cửa sổ Hann tiền tính toán, "
        "thực thi biến đổi FFT Radix-2 DIT 4.096 điểm (độ phân giải bin 3.90625 Hz), trích xuất các đỉnh phổ cục bộ kết hợp lọc sàn nhiễu "
        "trung vị (local noise floor median filtering), giải thuật chấm điểm giả thuyết họa âm (harmonic-aware hypothesis scoring), "
        "nội suy parabol bậc hai (Quadratic Interpolation - QI) để ước lượng đỉnh phổ liên tục dưới bin, bộ lọc ổn định thời gian "
        "(temporal stability filter) với cơ chế khóa nốt nhanh 2 khung (256 ms), ánh xạ nốt nhạc chuẩn MIDI hệ âm bằng (Equal Temperament, "
        "A4 = 440 Hz) và tính toán sai lệch cent. Kết quả nhận diện được đóng gói thành JSON snapshot thông qua FreeRTOS critical section, "
        "phục vụ người dùng qua Web Server nhúng (esp_http_server) với giao diện Celestial Tuner HTML5/CSS3/Vanilla JS mà không cần kết nối Internet ngoài.", indent=0.4)

    md.add_p(doc, 
        "Thực nghiệm đo đạc trực tiếp trên đàn piano cơ thật đã ghi nhận các kết quả xuất sắc trên các nốt kiểm thử: "
        "A4 (440.00 Hz) đạt mean 440.281 Hz, độ lệch chuẩn 0.096 Hz, MAE 0.281 Hz; C4 (261.63 Hz) đạt mean 261.674 Hz, std 0.064 Hz, MAE 0.065 Hz; "
        "C5 (523.25 Hz) đạt mean 523.438 Hz, std 0.020 Hz, MAE 0.188 Hz; D3 (146.83 Hz) đạt mean 146.797 Hz, std 0.074 Hz, MAE 0.060 Hz; "
        "E3 (164.81 Hz) đạt mean 164.787 Hz, std 0.065 Hz, MAE 0.054 Hz. Độ trễ tính toán DSP thuần đo được chỉ từ 23.56 đến 25.37 ms. "
        "Kiểm thử giao diện tự động bằng Chrome DevTools Protocol (CDP) ghi nhận 0 lỗi JavaScript và giao diện co giãn hoàn hảo trên 8 độ phân giải từ 360x800 đến 1920x1080.", indent=0.4)

    md.add_p(doc, 
        "Theo nguyên tắc nghiên cứu thực chứng nghiêm ngặt (REAL-DATA ONLY), báo cáo khẳng định rõ ràng rằng: Dù thuật toán "
        "nội suy bậc hai cải thiện đáng kể độ mịn tần số, hệ thống CHƯA ĐỦ DỮ LIỆU ĐỂ TUYÊN BỐ ĐẠT ĐỘ CHÍNH XÁC < 0.5 HZ TRÊN TOÀN BỘ 88 PHÍM PIANO. "
        "Ở dải trầm (đặc biệt nốt E2 ~ 82.41 Hz), năng lượng fundamental thực tế rất yếu (biên độ 1.5 - 7.3 so với 46.4 của họa âm bậc 3, 4), "
        "dẫn đến tỷ lệ bắt đúng nốt trong bài test nghiêm ngặt chỉ đạt 15% và dễ nhảy quãng tám sang E3. Các dải phím cực trầm (A0-C2), dải cực cao (C6-C8) "
        "và trường hợp đạp pedal vang âm phức tạp được phân loại rõ ràng là CHƯA ĐƯỢC XÁC MINH THỰC TẾ (NOT VERIFIED).", indent=0.4)

    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.space_before = Pt(6)
    p_kw.paragraph_format.space_after = Pt(14)
    r = p_kw.add_run("Từ khóa: ")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12.5)
    r = p_kw.add_run("Xử lý tín hiệu số, ESP32-S3, INMP441, I2S, FFT, Cửa sổ Hann, Quadratic Interpolation, Harmonic-Aware Detection, Piano Chromatic Tuner, Cents Deviation, Real-Data Only.")
    r.italic = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    # English Abstract
    md.add_heading_1(doc, "ABSTRACT")
    md.add_p(doc, 
        "This technical report presents the comprehensive design, digital signal processing (DSP) pipeline architecture, "
        "and empirical validation of an autonomous, embedded real-time Single-Note Piano Chromatic Tuner utilizing an "
        "ESP32-S3 N16R8 microcontroller and an INMP441 digital I2S MEMS microphone.", indent=0.4)

    md.add_p(doc, 
        "Acoustic piano pitch detection presents distinct challenges due to string inharmonicity and severe fundamental frequency (f0) "
        "attenuation in bass registers, where higher harmonics (2nd, 3rd, and 4th) dominate the energy spectrum. Implemented entirely "
        "within the native Espressif IoT Development Framework (ESP-IDF) and standard C/C++ without external Arduino or web frameworks, "
        "the architecture encompasses: continuous 16 kHz I2S DMA acquisition, a 50% overlapping rolling buffer (N = 4096 samples, hop = 2048 samples, "
        "frame duration = 256 ms), DC removal, precomputed Hann windowing, Radix-2 Decimation-In-Time FFT (bin resolution df = 3.90625 Hz), "
        "local peak prominence extraction with 24-bin neighborhood median noise floor filtering, harmonic-aware subharmonic candidate hypothesis "
        "scoring, 3-point parabolic Quadratic Interpolation (QI) for sub-bin peak localization, a 2-frame fast-lock temporal stability filter, "
        "equal-temperament MIDI note mapping (A4 = 440 Hz), and logarithmic cents deviation calculation. Results are served asynchronously via "
        "an embedded HTTP server to a lightweight, responsive HTML5/CSS3/Vanilla JS 'Celestial Tuner' interface.", indent=0.4)

    md.add_p(doc, 
        "Acoustic validation conducted on a real acoustic piano confirmed high accuracy across verified test notes: A4 (mean 440.281 Hz, std 0.096 Hz, MAE 0.281 Hz), "
        "C4 (mean 261.674 Hz, std 0.064 Hz, MAE 0.065 Hz), C5 (mean 523.438 Hz, std 0.020 Hz, MAE 0.188 Hz), D3 (mean 146.797 Hz, std 0.074 Hz, MAE 0.060 Hz), "
        "and E3 (mean 164.787 Hz, std 0.065 Hz, MAE 0.054 Hz). Dedicated DSP computation latency was benchmarked at 23.56 to 25.37 ms. "
        "Headless Chrome CDP automation validated 0 JavaScript errors and seamless responsive fitting across 8 distinct viewports.", indent=0.4)

    md.add_p(doc, 
        "Under strict real-data integrity guidelines, it is explicitly reported that system-wide <0.5 Hz accuracy across the full 88-key compass CANNOT "
        "be claimed. At lower registers (specifically E2 ~ 82.41 Hz), weak fundamental excitation causes susceptibility to octave-jumping errors, "
        "achieving a 15% correct detection rate in clean tests. Untested compass limits (A0-C2, C6-C8) and polyphonic acoustic conditions remain "
        "explicitly designated as NOT VERIFIED.", indent=0.4)

    p_kw_en = doc.add_paragraph()
    p_kw_en.paragraph_format.space_before = Pt(6)
    p_kw_en.paragraph_format.space_after = Pt(14)
    r = p_kw_en.add_run("Keywords: ")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12.5)
    r = p_kw_en.add_run("Digital Signal Processing (DSP), ESP32-S3, INMP441, I2S, FFT, Hann Window, Quadratic Interpolation, Harmonic Analysis, Piano Tuner, Pitch Detection, Empirical Validation.")
    r.italic = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    doc.add_page_break()

    # =========================================================================
    # 3. MỤC LỤC & DANH MỤC TỪ VIẾT TẮT
    # =========================================================================
    md.add_heading_1(doc, "MỤC LỤC TỔNG QUÁT")
    
    toc_items = [
        ("CHƯƠNG 1 — GIỚI THIỆU VÀ ĐẶT VẤN ĐỀ", "1"),
        ("  1.1. Đặt vấn đề và tính cấp thiết của đề tài", "1"),
        ("  1.2. Mục tiêu nghiên cứu và phát triển", "2"),
        ("  1.3. Phạm vi nghiên cứu và đối tượng áp dụng", "2"),
        ("  1.4. Yêu cầu kỹ thuật và tiêu chí đánh giá", "3"),
        ("  1.5. Phương pháp tiếp cận và quy trình thực hiện", "4"),
        ("CHƯƠNG 2 — CƠ SỞ LÝ THUYẾT XỬ LÝ TÍN HIỆU SỐ", "5"),
        ("  2.1. Bản chất tín hiệu âm thanh và sự hình thành cao độ", "5"),
        ("  2.2. Lấy mẫu tín hiệu và Định lý Nyquist - Shannon", "6"),
        ("  2.3. Giao thức truyền thông âm thanh số I2S (Inter-IC Sound)", "7"),
        ("  2.4. Biến đổi Fourier rời rạc (DFT) và Thuật toán FFT Radix-2", "8"),
        ("  2.5. Độ phân giải tần số và sự đánh đổi thời gian - tần số", "10"),
        ("  2.6. Hiện tượng rò rỉ phổ (Spectral Leakage) và Kỹ thuật cửa sổ hóa", "11"),
        ("  2.7. Đặc tính toán học của Cửa sổ Hann (Hann Window)", "12"),
        ("  2.8. Trích xuất đỉnh phổ cục bộ và đánh giá tỷ số SNR", "13"),
        ("  2.9. Thuật toán nội suy parabol bậc hai (Quadratic Interpolation)", "14"),
        ("  2.10. Tần số cơ bản, chuỗi họa âm và tính bất điều hòa của đàn Piano", "16"),
        ("  2.11. Hệ âm 12 nốt đồng đều (Equal Temperament)", "18"),
        ("  2.12. Ánh xạ tần số sang số nốt chuẩn MIDI", "19"),
        ("  2.13. Đơn vị đo sai lệch cao độ Cent (Cents Deviation)", "20"),
        ("CHƯƠNG 3 — THIẾT KẾ KIẾN TRÚC HỆ THỐNG", "21"),
        ("  3.1. Kiến trúc tổng thể hệ thống", "21"),
        ("  3.2. Lựa chọn và thiết kế phần cứng điều khiển (ESP32-S3 N16R8)", "22"),
        ("  3.3. Thiết kế ghép nối cảm biến âm thanh I2S INMP441", "23"),
        ("  3.4. Kiến trúc Firmware đa nhiệm thời gian thực trên FreeRTOS", "24"),
        ("  3.5. Thiết kế Pipeline DSP với cơ chế đệm trượt 50% gối đầu", "25"),
        ("  3.6. Thuật toán phân tích họa âm Harmonic-Aware Fundamental Detection", "27"),
        ("  3.7. Bộ lọc ổn định thời gian và thuật toán nhận diện nốt nhạc", "30"),
        ("  3.8. Thiết kế máy chủ nhúng HTTP Server không khóa DSP", "31"),
        ("  3.9. Thiết kế giao diện người dùng Web Frontend (Celestial Tuner)", "32"),
        ("CHƯƠNG 4 — TRIỂN KHAI THỰC HIỆN HỆ THỐNG", "34"),
        ("  4.1. Môi trường phát triển và cấu hình ESP-IDF", "34"),
        ("  4.2. Tầng thu nhận dữ liệu âm thanh I2S và cấu hình DMA", "35"),
        ("  4.3. Quản lý bộ đệm Hop Buffer và Rolling Buffer", "36"),
        ("  4.4. Thuật toán khử thành phần một chiều (DC Removal)", "37"),
        ("  4.5. Triển khai FFT Radix-2 và cửa sổ hóa Hann", "38"),
        ("  4.6. Trích xuất đỉnh phổ và tính sàn nhiễu trung vị", "39"),
        ("  4.7. Cài đặt thuật toán chấm điểm giả thuyết họa âm và Bass-Gate", "40"),
        ("  4.8. Cài đặt nội suy parabol bậc hai (QI)", "41"),
        ("  4.9. Triển khai ánh xạ nốt MIDI và độ lệch cents", "42"),
        ("  4.10. Hiện thực hóa HTTP API Endpoint /api/data", "43"),
        ("  4.11. Nhúng mã nguồn Web Frontend vào Firmware", "44"),
        ("CHƯƠNG 5 — KIỂM THỬ VÀ PHÂN TÍCH KẾT QUẢ THỰC TẾ", "46"),
        ("  5.1. Phương pháp và thiết lập môi trường kiểm thử thực nghiệm", "46"),
        ("  5.2. Kiểm thử xác thực thuật toán với tín hiệu tổng hợp", "47"),
        ("  5.3. Kết quả kiểm thử trên đàn Piano cơ (Acoustic Piano)", "48"),
        ("  5.4. Phân tích chi tiết nốt A4 (440.00 Hz)", "49"),
        ("  5.5. Phân tích chi tiết nốt C4 (261.63 Hz)", "50"),
        ("  5.6. Phân tích chi tiết nốt C5 (523.25 Hz)", "51"),
        ("  5.7. Phân tích chi tiết nốt D3 (146.83 Hz)", "52"),
        ("  5.8. Phân tích chi tiết nốt E3 (164.81 Hz)", "53"),
        ("  5.9. Phân tích thực nghiệm nốt trầm E2 (82.41 Hz) và dải Bass", "54"),
        ("  5.10. Đo đạc độ trễ xử lý (Processing Latency vs Update Cadence)", "56"),
        ("  5.11. Kiểm thử tự động Frontend trên Chrome Headless CDP", "57"),
        ("  5.12. Kiểm thử tính thích ứng giao diện (Responsive Layout Matrix)", "58"),
        ("  5.13. Tổng hợp và phân tích sai số toàn diện", "59"),
        ("CHƯƠNG 6 — ĐÁNH GIÁ, THẢO LUẬN VÀ GIỚI HẠN KỸ THUẬT", "61"),
        ("  6.1. Tổng kết các mục tiêu kỹ thuật đạt được", "61"),
        ("  6.2. Các nội dung chưa đạt và ranh giới chưa xác minh (Unverified)", "62"),
        ("  6.3. Phân tích nguồn gốc sai số vật lý và toán học", "63"),
        ("  6.4. Giới hạn vận hành của hệ thống", "65"),
        ("  6.5. Đề xuất các giải pháp nâng cấp tiềm năng", "66"),
        ("CHƯƠNG 7 — KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", "68"),
        ("  7.1. Kết luận chung", "68"),
        ("  7.2. Hướng phát triển trong tương lai", "69"),
        ("TÀI LIỆU THAM KHẢO", "70"),
        ("PHỤ LỤC", "71"),
        ("  Phụ lục A: Sơ đồ nối dây và thông số phần cứng chi tiết", "71"),
        ("  Phụ lục B: Cấu trúc JSON API /api/data thực tế", "72"),
        ("  Phụ lục C: Bảng tần số chuẩn 88 phím đàn Piano (A0 - C8)", "73"),
        ("  Phụ lục D: Cấu hình firmware và trích đoạn mã DSP quan trọng", "75")
    ]
    
    tbl_toc = doc.add_table(rows=len(toc_items), cols=2)
    tbl_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_toc.autofit = False
    for idx, (title, page) in enumerate(toc_items):
        r_c0 = tbl_toc.rows[idx].cells[0]
        r_c1 = tbl_toc.rows[idx].cells[1]
        r_c0.width = Inches(5.5)
        r_c1.width = Inches(0.8)
        md.set_cell_margins(r_c0, 20, 20, 40, 40)
        md.set_cell_margins(r_c1, 20, 20, 40, 40)
        
        tcPr0 = r_c0._tc.get_or_add_tcPr()
        tcPr1 = r_c1._tc.get_or_add_tcPr()
        b_none = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="none"/><w:right w:val="none"/><w:top w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
        tcPr0.append(b_none)
        tcPr1.append(parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="none"/><w:right w:val="none"/><w:top w:val="none"/><w:bottom w:val="none"/></w:tcBorders>'))
        
        p0 = r_c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r0 = p0.add_run(title)
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(11)
        if title.startswith("CHƯƠNG") or title.startswith("TÀI") or title.startswith("PHỤ"):
            r0.bold = True
            r0.font.color.rgb = md.C_NAVY
            
        p1 = r_c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r1 = p1.add_run(page)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(11)
        r1.font.color.rgb = md.C_MUTED

    doc.add_page_break()

    # =========================================================================
    # 4. DANH MỤC BẢNG BIỂU & TỪ VIẾT TẮT
    # =========================================================================
    md.add_heading_1(doc, "DANH MỤC BẢNG BIỂU")
    list_tables = [
        ("Bảng 2.1", "Tần số danh định lý thuyết của các nốt nhạc kiểm thử (Equal Temperament, A4 = 440 Hz)"),
        ("Bảng 3.1", "Thông số phần cứng chi tiết của khối xử lý ESP32-S3 N16R8"),
        ("Bảng 3.2", "Sơ đồ kết nối dây phần cứng giữa ESP32-S3 và Microphone MEMS INMP441"),
        ("Bảng 3.3", "Các tham số baseline của Pipeline Xử lý tín hiệu số (DSP Pipeline)"),
        ("Bảng 3.4", "Định nghĩa chi tiết các trường dữ liệu của JSON API Endpoint /api/data"),
        ("Bảng 4.1", "Các trạng thái tín hiệu phân loại trong Firmware và ngưỡng kích hoạt"),
        ("Bảng 5.1", "Kết quả đo đạc thống kê cao độ trên đàn piano cơ thật (20 khung VALID liên tiếp/nốt)"),
        ("Bảng 5.2", "Đo đạc đặc tính các họa âm và hiện tượng dạt tần số (Inharmonicity) trên đàn piano thật"),
        ("Bảng 5.3", "Kết quả kiểm thử Clean Regression trên đàn piano cơ thật (20 khung/nốt)"),
        ("Bảng 5.4", "Phân tích đặc tính phổ tại dải nốt trầm E2 (82.41 Hz) ghi nhận trên phần cứng"),
        ("Bảng 5.5", "Kết quả đo đạc độ trễ xử lý (Processing Latency) của khối DSP"),
        ("Bảng 5.6", "Kết quả kiểm thử tự động Frontend trên Chrome Headless CDP Automation"),
        ("Bảng 5.7", "Ma trận kiểm thử tính tương thích giao diện co giãn Responsive trên 8 Viewport"),
        ("Bảng 6.1", "Đối chiếu giữa yêu cầu kỹ thuật đồ án và kết quả thực nghiệm đạt được"),
        ("Bảng 6.2", "Ma trận phân định ranh giới xác thực thực tế (Verified vs. Not Verified)")
    ]
    md.add_custom_table(doc, ["Ký hiệu", "Tên bảng biểu chi tiết"], list_tables, [1.4, 4.9])

    md.add_heading_1(doc, "DANH MỤC HÌNH VẼ VÀ SƠ ĐỒ KỸ THUẬT")
    list_figs = [
        ("Hình 2.1", "Mô hình lấy mẫu tín hiệu liên tục và phổ chu kỳ hóa theo định lý Nyquist"),
        ("Hình 2.2", "Giản đồ xung thời gian của chuẩn giao tiếp âm thanh số I2S Philips"),
        ("Hình 2.3", "Hiện tượng rò rỉ phổ (Spectral Leakage) và đáp ứng tần số của Cửa sổ Hann"),
        ("Hình 2.4", "Nguyên lý ước lượng đỉnh phổ liên tục bằng phương pháp nội suy parabol bậc hai (QI)"),
        ("Hình 2.5", "Sự sai lệch họa âm (Inharmonicity) của dây đàn thép piano theo phương trình Fletcher"),
        ("Hình 3.1", "Sơ đồ khối kiến trúc phần cứng và luồng dữ liệu hệ thống Piano Chromatic Tuner"),
        ("Hình 3.2", "Sơ đồ kết nối chân tín hiệu I2S giữa INMP441 và ESP32-S3"),
        ("Hình 3.3", "Sơ đồ kiến trúc firmware đa nhiệm thời gian thực FreeRTOS"),
        ("Hình 3.4", "Pipeline xử lý tín hiệu số liên tục với cơ chế đệm trượt 50% gối đầu (Hop Overlap)"),
        ("Hình 3.5", "Lưu đồ thuật toán đánh giá giả thuyết họa âm (Harmonic-Aware Scoring Logic)"),
        ("Hình 3.6", "Kiến trúc giao diện người dùng Web Celestial Tuner và luồng polling dữ liệu API")
    ]
    md.add_custom_table(doc, ["Ký hiệu", "Tên hình vẽ và sơ đồ kỹ thuật"], list_figs, [1.4, 4.9])

    md.add_heading_1(doc, "DANH MỤC TỪ VIẾT TẮT")
    abbrs = [
        ("ADC", "Analog-to-Digital Converter", "Bộ biến đổi tương tự sang số"),
        ("AP", "Access Point", "Điểm truy cập mạng không dây"),
        ("CDP", "Chrome DevTools Protocol", "Giao thức điều khiển tự động hóa trình duyệt"),
        ("CISP / QI", "Quadratic Interpolation", "Nội suy parabol bậc hai"),
        ("DFT", "Discrete Fourier Transform", "Biến đổi Fourier rời rạc"),
        ("DMA", "Direct Memory Access", "Truy cập bộ nhớ trực tiếp"),
        ("DSP", "Digital Signal Processing", "Xử lý tín hiệu số"),
        ("ESP-IDF", "Espressif IoT Development Framework", "Bộ khung phát triển nhúng của Espressif"),
        ("FFT", "Fast Fourier Transform", "Biến đổi Fourier nhanh"),
        ("I2S", "Inter-IC Sound", "Chuẩn giao tiếp âm thanh số nối tiếp"),
        ("JSON", "JavaScript Object Notation", "Định dạng trao đổi dữ liệu dạng văn bản"),
        ("MAE", "Mean Absolute Error", "Sai số tuyệt đối trung bình"),
        ("MEMS", "Micro-Electro-Mechanical Systems", "Hệ thống vi cơ điện tử"),
        ("MIDI", "Musical Instrument Digital Interface", "Giao diện số cho nhạc cụ"),
        ("PCM", "Pulse-Code Modulation", "Điều chế mã xung"),
        ("RMS", "Root Mean Square", "Giá trị hiệu dụng"),
        ("RTOS", "Real-Time Operating System", "Hệ điều hành thời gian thực"),
        ("SNR", "Signal-to-Noise Ratio", "Tỷ số tín hiệu trên nhiễu"),
        ("STA", "Station Mode", "Chế độ máy trạm kết nối Wi-Fi"),
        ("UI", "User Interface", "Giao diện người dùng")
    ]
    md.add_custom_table(doc, ["Từ viết tắt", "Thuật ngữ tiếng Anh", "Ý nghĩa tiếng Việt"], abbrs, [1.1, 2.7, 2.5])

    doc.add_page_break()

print("section_frontmatter compiled successfully.")
