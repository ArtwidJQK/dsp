# -*- coding: utf-8 -*-
"""
Module: Chapter 1 (Introduction) and Chapter 2 (Theoretical Foundations)
for LeTanDung_24150654_v2.docx
Strictly adheres to:
- A4, 13pt Times New Roman, Black, 1.3 line spacing, 6pt after, 1.0cm first line indent.
- Headings: Heading 1 (16pt bold uppercase), Heading 2 (14pt bold), Heading 3 (13pt bold italic).
- Real OMML equations (2.1 to 2.27) in 2-column borderless tables (7920 + 1152 dxa).
- Figures 2.1 to 2.5 inserted with captions below.
- Corrected formulas: strict Fs > 2 f_max (2.2), periodic Hann (2.12).
- Normalized symbols: Δf, π, α, β, γ, φ_m, ±, ×, →, ≤, ≥, f_Nyquist, N², log₂.
- In-text cent conversion table in 1.4, unified ±5 cent threshold.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn

import v2_helpers as vh

FIGURES_DIR = r"D:\dsp\LeTanDung_24150654\figures"

def build_ch1_ch2(doc):
    # =========================================================================
    # SECTION BREAK -> SECTION 3 (MAIN BODY)
    # =========================================================================
    doc.add_section(docx.enum.section.WD_SECTION.NEW_PAGE)
    sec3 = doc.sections[2]
    sec3.header.is_linked_to_previous = False
    sec3.footer.is_linked_to_previous = False

    # Header for Section 3: STYLEREF "Heading 1"
    hp3 = sec3.header.paragraphs[0]
    hp3.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    vh.add_toc_field(hp3, 'STYLEREF "Heading 1"')
    for r in hp3.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(9)
        r.font.italic = True
        r.font.color.rgb = RGBColor(80, 80, 80)

    # Footer for Section 3: Arabic numerals starting at 1
    fp3 = sec3.footer.paragraphs[0]
    fp3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    vh.add_toc_field(fp3, 'PAGE')
    sectPr3 = sec3._sectPr
    pgNumType3 = parse_xml(f'<w:pgNumType {nsdecls("w")} w:fmt="decimal" w:start="1"/>')
    sectPr3.append(pgNumType3)

    # =========================================================================
    # CHƯƠNG 1 — GIỚI THIỆU
    # =========================================================================
    vh.add_heading_1(doc, "CHƯƠNG 1 — GIỚI THIỆU", is_chapter=False)

    # 1.1 Đặt vấn đề
    vh.add_heading_2(doc, "1.1. Đặt vấn đề")
    vh.add_p(doc, 
        "Trong lĩnh vực âm nhạc và kỹ thuật âm thanh, việc căn chỉnh cao độ (tuning) cho các nhạc cụ có dây, "
        "đặc biệt là đàn piano cơ (acoustic piano), giữ vai trò quyết định đến chất lượng biểu diễn và cảm nhận âm học. "
        "Một cây đàn piano tiêu chuẩn sở hữu 88 phím tương ứng với dải tần số cơ bản trải dài từ A0 (27.50\u00A0Hz) đến C8 (4186.01\u00A0Hz). "
        "Khác với các nhạc cụ đơn giản như đàn guitar chỉ gồm 6 dây trong dải tần hẹp (khoảng 82\u00A0Hz đến 1\u00A0200\u00A0Hz), "
        "hệ thống dây đàn piano có sự biến thiên rất lớn về chiều dài, khối lượng riêng và lực căng tổng cộng (lên tới 15–20 tấn trên khung gang) [6].", indent=0.394)

    vh.add_p(doc, 
        "Hiện nay, mặc dù các ứng dụng lên dây trên điện thoại thông minh rất phổ biến, chúng thường gặp phải những giới hạn kỹ thuật "
        "đáng kể khi áp dụng cho piano: (1) Microphone tích hợp trên điện thoại thường tối ưu cho băng thông thoại truyền thống "
        "(khoảng 300\u00A0Hz đến 3.4\u00A0kHz), dẫn tới hiện tượng suy giảm rất mạnh ở dải hạ âm dưới 100\u00A0Hz; (2) Tầng thu âm chịu sự can thiệp của các thuật toán "
        "tự động như kiểm soát độ lợi (AGC) hay khử nhiễu tự động, làm méo mó cấu trúc đỉnh phổ âm học thực tế; (3) Độ trễ âm thanh của hệ điều hành "
        "di động dao động phức tạp, gây khó khăn cho việc phản hồi thời gian thực khi thao tác gõ phím liên tục [2]. "
        "Ngược lại, các máy lên dây thương mại chuyên dụng thường có giá thành cao và hoạt động như hệ thống đóng kín, "
        "không cung cấp khả năng quan sát chi tiết phổ họa âm hay tùy biến thuật toán xử lý tín hiệu.", indent=0.394)

    vh.add_p(doc, 
        "Xuất phát từ thực tiễn đó, việc nghiên cứu và hiện thực một thiết bị phần cứng nhúng độc lập, chi phí thấp, sử dụng vi điều khiển "
        "hiệu năng cao ESP32-S3 kết hợp microphone MEMS kỹ thuật số I2S INMP441 để xử lý tín hiệu âm thanh piano theo thời gian thực "
        "là một đề tài mang tính ứng dụng cao và phù hợp với mục tiêu đào tạo của môn học Xử lý tín hiệu số.", indent=0.394)

    # 1.2 Mục tiêu đề tài
    vh.add_heading_2(doc, "1.2. Mục tiêu đề tài")
    vh.add_p(doc, "Đề tài tập trung giải quyết 5 mục tiêu kỹ thuật cụ thể sau:", indent=0.394)

    goals = [
        "Thiết kế và triển khai chuỗi thu thập dữ liệu âm thanh số từ microphone MEMS INMP441 qua giao tiếp I2S DMA vào vi điều khiển ESP32-S3 ở tần số lấy mẫu 16\u00A0000\u00A0Hz, giảm thiểu nhiễu đường truyền tương tự nhờ ghép nối số I2S.",
        "Xây dựng chuỗi thuật toán xử lý tín hiệu số thời gian thực bao gồm: tiền xử lý khử offset DC, cửa sổ hóa Hann tuần hoàn, thuật toán biến đổi Fourier nhanh (FFT) radix-2 với độ dài khung 4\u00A0096 mẫu, phát hiện đỉnh phổ cục bộ, tinh chỉnh tần số bằng phương pháp nội suy parabol bậc hai và chấm điểm đa họa âm có điều kiện (bass-gate).",
        "Triển khai thuật toán ánh xạ tần số sang nốt nhạc chuẩn theo hệ âm đo bình quân 12 cung đều (12-TET), tính toán độ lệch cao độ theo đơn vị Cent và làm mịn dữ liệu qua các khung thời gian liên tiếp.",
        "Tích hợp giao diện người dùng hiển thị trực quan thông qua Web Server nhúng trên ESP32-S3, truyền thông dữ liệu kết quả đo đạc qua giao thức HTTP/CDP với tần suất cập nhật định kỳ 125\u00A0ms.",
        "Thực nghiệm và đánh giá định lượng độ chính xác của hệ thống trên tín hiệu đàn piano cơ thực tế, phân tích khách quan các sai số và giới hạn âm học đo đạc được."
    ]
    for g in goals:
        vh.add_p(doc, f"• {g}", indent=0.394, space_after=3)

    # 1.3 Phạm vi và giới hạn nghiên cứu
    vh.add_heading_2(doc, "1.3. Phạm vi và giới hạn nghiên cứu")
    vh.add_p(doc, 
        "Trong khuôn khổ đề tài này, các ranh giới kỹ thuật được xác định rõ ràng nhằm đảm bảo tính trung thực khoa học:", indent=0.394)

    vh.add_p(doc, 
        "1. Dữ liệu thực nghiệm được đo đạc trực tiếp trên đàn piano acoustic cơ thực tế cho 6 nốt đại diện: A4, C4, C5, D3, E3 và E2. "
        "Các dải tần số còn lại (bao gồm dải cực trầm A0–B1 và dải cao từ D5 đến C8) thuộc diện 'chưa kiểm chứng' bằng mẫu đàn cơ thực tế trong báo cáo này.", indent=0.394)

    vh.add_p(doc, 
        "2. Về giới hạn nhận diện dải âm cực trầm: thực nghiệm ghi nhận nốt E2 (82.41\u00A0Hz) xuất hiện lỗi nhận diện quãng tám do tần số cơ bản f₀ bị suy hao vật lý nghiêm trọng. "
        "Chi tiết nguyên nhân cơ học và phân tích cấu trúc phổ của hiện tượng này được trình bày cụ thể tại Mục 5.9 và Mục 6.2.", indent=0.394)

    vh.add_p(doc, 
        "3. Thiết bị được thiết kế cho mục đích hỗ trợ lên dây từng phím đơn âm (monophonic pitch tracking), không hỗ trợ nhận diện hợp âm đa âm (polyphonic transcription).", indent=0.394)

    # 1.4 Chỉ tiêu kỹ thuật đặt ra
    vh.add_heading_2(doc, "1.4. Chỉ tiêu kỹ thuật đặt ra")
    vh.add_p(doc, 
        "Dựa trên các yêu cầu âm học và khả năng của phần cứng nhúng, hệ thống hướng tới các chỉ tiêu kỹ thuật chính sau:", indent=0.394)

    # Bảng quy đổi sai số 0.5 Hz sang cent
    vh.add_caption(doc, "Bảng 1.1: Quy đổi chỉ tiêu sai số tần số 0.5 Hz sang độ lệch Cent theo từng nốt nhạc", is_table=True)
    tbl_cent = doc.add_table(rows=1, cols=4)
    tbl_cent.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_cent.autofit = False
    vh.set_table_borders(tbl_cent)

    cent_headers = ["Nốt nhạc", "Tần số danh định (Hz)", "Sai số tần số Δf (Hz)", "Độ lệch tương đương (Cent)"]
    hdr_c = tbl_cent.rows[0]
    for idx, text in enumerate(cent_headers):
        c = hdr_c.cells[idx]
        c.width = Inches(1.57)
        vh.set_cell_background(c, "EAECEF")
        vh.set_cell_margins(c, top=80, bottom=80, left=80, right=80)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.bold = True

    cent_data = [
        ("A4", "440.00", "±0.50", "±1.97 cent (≈ ±2.0 cent)"),
        ("C4", "261.63", "±0.50", "±3.30 cent (≈ ±3.3 cent)"),
        ("D3", "146.83", "±0.50", "±5.88 cent (≈ ±5.9 cent)"),
        ("E2", "82.41", "±0.50", "±10.46 cent (≈ ±10.5 cent)"),
    ]
    for row_data in cent_data:
        r = tbl_cent.add_row()
        for idx, text in enumerate(row_data):
            c = r.cells[idx]
            c.width = Inches(1.57)
            vh.set_cell_margins(c, top=60, bottom=60, left=80, right=80)
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx in [0, 2] else (WD_ALIGN_PARAGRAPH.RIGHT if idx == 1 else WD_ALIGN_PARAGRAPH.LEFT)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            run = p.add_run(text)
            run.font.name = "Times New Roman"
            run.font.size = Pt(11)
            if idx == 0:
                run.bold = True

    vh.make_table_responsive(tbl_cent)

    vh.add_p(doc, 
        "Nhận xét về tiêu chí sai số: Từ Bảng 1.1 có thể thấy, tiêu chí sai số cố định theo Hertz (Δf < 0.5\u00A0Hz) có đặc tính phi tuyến khi quy đổi sang cảm nhận cao độ (cent). "
        "Ở dải âm cao (A4), 0.5\u00A0Hz tương đương mức sai số rất khắt khe là ±2.0 cent; trong khi ở dải âm trầm (E2), 0.5\u00A0Hz lại tương đương ±10.5 cent. "
        "Do đó, để thống nhất quy chuẩn đánh giá âm nhạc, đề tài xác định tiêu chuẩn 'IN TUNE' (đạt chuẩn cân chỉnh) thống nhất là sai số nằm trong phạm vi ±5 cent. "
        "Trạng thái hiển thị bao gồm: THẤP (độ lệch < −5 cent), IN TUNE (độ lệch từ −5 đến +5 cent), và CAO (độ lệch > +5 cent).", indent=0.394)

    vh.add_p(doc, 
        "Về độ trễ và độ ổn định: Hệ thống đặt mục tiêu thời gian xử lý chu kỳ DSP không vượt quá 30\u00A0ms (chưa bao gồm thời gian thu thập khung âm thanh). "
        "Về độ ổn định vận hành dài hạn (không tràn bộ nhớ heap, không kích hoạt watchdog reset): [CẦN BỔ SUNG kết quả soak test thử nghiệm liên tục trong điều kiện đo dài hạn].", indent=0.394)

    # =========================================================================
    # CHƯƠNG 2 — CƠ SỞ LÝ THUYẾT
    # =========================================================================
    vh.add_heading_1(doc, "CHƯƠNG 2 — CƠ SỞ LÝ THUYẾT VỀ XỬ LÝ TÍN HIỆU ÂM THANH PIANO", is_chapter=True)

    # 2.1 Tín hiệu âm thanh piano và mô hình toán học
    vh.add_heading_2(doc, "2.1. Tín hiệu âm thanh piano và mô hình toán học")
    vh.add_p(doc, 
        "Âm thanh phát ra từ một phím đàn piano khi búa gõ vào dây là một tín hiệu âm học phức hợp gồm nhiều thành phần dao động điều hòa. "
        "Trong trường hợp lý thuyết dây đàn hoàn toàn mềm dẻo (không có độ cứng uốn), tín hiệu âm thanh liên tục x(t) có thể được biểu diễn "
        "bằng chuỗi Fourier điều hòa theo công thức sau:", indent=0.394)

    vh.add_equation_omml(doc, r"x(t) = \sum_{m=1}^{\infty} A_m \cos(2\pi m f_0 t + \phi_m)", "2.1")

    vh.add_p(doc, 
        "Trong đó, f₀ là tần số cơ bản của nốt nhạc, m là bậc họa âm (m = 1, 2, 3, ...), A_m và φ_m lần lượt là biên độ và pha ban đầu của họa âm bậc m. "
        "Đối với dây đàn thực tế, các thành phần tần số không hoàn toàn là bội số nguyên của f₀ do tính cứng của dây thép đàn piano, "
        "đây là đặc tính vật lý then chốt cần được xem xét kỹ lưỡng khi xây dựng thuật toán phân tích phổ [6].", indent=0.394)

    # 2.2 Rời rạc hóa tín hiệu và định lý lấy mẫu
    vh.add_heading_2(doc, "2.2. Rời rạc hóa tín hiệu và định lý lấy mẫu Nyquist-Shannon")
    vh.add_p(doc, 
        "Để xử lý tín hiệu âm thanh trên vi điều khiển số, tín hiệu tương tự liên tục x(t) phải được chuyển đổi thành dãy số rời rạc x[n] "
        "bằng cách lấy mẫu định kỳ tại các thời điểm t = n·T_s, trong đó T_s = 1/F_s là chu kỳ lấy mẫu. Theo định lý lấy mẫu Nyquist-Shannon, "
        "để có thể tái tạo hoàn toàn tín hiệu liên tục có băng thông giới hạn mà không bị hiện tượng chồng phổ (aliasing), "
        "tần số lấy mẫu F_s phải thỏa mãn điều kiện bất đẳng thức nghiêm ngặt [8]:", indent=0.394)

    vh.add_equation_omml(doc, r"F_s > 2 f_{\max}", "2.2")

    vh.add_p(doc, 
        "Trong hệ thống này, tần số lấy mẫu được cấu hình là F_s = 16\u00A0000\u00A0Hz. Do đó, tần số Nyquist giới hạn trên của dải tần có thể xử lý là:", indent=0.394)

    vh.add_equation_omml(doc, r"f_{\text{Nyquist}} = \frac{16000}{2} = 8000 \text{ Hz}", "2.3")

    vh.add_p(doc, 
        "Vì nốt cao nhất của đàn piano là C8 có tần số danh định khoảng 4\u00A0186.01\u00A0Hz, tần số Nyquist 8\u00A0000\u00A0Hz đảm bảo bao phủ "
        "toàn bộ tần số cơ bản của 88 phím đàn piano và các họa âm bậc 2 của các nốt trung âm dưới 4\u00A0000\u00A0Hz.", indent=0.394)

    vh.add_figure_image(doc, os.path.join(FIGURES_DIR, "fig_2_1_sampling.png"), 
                       "Hình 2.1: Quá trình lấy mẫu và phổ chu kỳ hóa tín hiệu tương tự sang số")

    # 2.3 Giao thức âm thanh kỹ thuật số I2S Philips
    vh.add_heading_2(doc, "2.3. Giao thức âm thanh kỹ thuật số I2S Philips")
    vh.add_p(doc, 
        "Giao thức I2S (Inter-IC Sound) là chuẩn truyền thông nối tiếp chuyên dụng cho âm thanh kỹ thuật số, được Philips Semiconductor phát triển. "
        "Khác với các microphone tương tự đòi hỏi mạch tiền khuếch đại và bộ biến đổi ADC bên ngoài, microphone MEMS INMP441 tích hợp sẵn "
        "tầng tiền khuếch đại, bộ chuyển đổi ADC delta-sigma và bộ tạo khung truyền thông I2S ngay trên chip silicon. Giao thức I2S sử dụng 3 đường tín hiệu chính:", indent=0.394)

    vh.add_p(doc, "• SCK / BCLK (Continuous Serial Clock): Xung đồng hồ đồng bộ hóa từng bit dữ liệu truyền tải.", indent=0.394, space_after=3)
    vh.add_p(doc, "• WS / LRCK (Word Select / Left-Right Clock): Xung chọn kênh, xác định dữ liệu thuộc kênh trái (WS = 0) hoặc kênh phải (WS = 1).", indent=0.394, space_after=3)
    vh.add_p(doc, "• SD / DOUT (Serial Data): Đường truyền dữ liệu âm thanh số nối tiếp theo thứ tự bit có trọng số cao nhất (MSB) trước.", indent=0.394, space_after=6)

    vh.add_figure_image(doc, os.path.join(FIGURES_DIR, "fig_2_2_i2s_timing.png"), 
                       "Hình 2.2: Giản đồ xung truyền thông giao thức I2S chuẩn Philips")

    # 2.4 Biến đổi Fourier rời rạc (DFT) và thuật toán FFT Cooley-Tukey
    vh.add_heading_2(doc, "2.4. Biến đổi Fourier rời rạc (DFT) và thuật toán FFT Cooley-Tukey")
    vh.add_p(doc, 
        "Để phân tích cấu trúc tần số của tín hiệu âm thanh rời rạc x[n] gồm N mẫu, Biến đổi Fourier rời rạc (DFT) được áp dụng [8]:", indent=0.394)

    vh.add_equation_omml(doc, r"X[k] = \sum_{n=0}^{N-1} x[n] e^{-j \frac{2\pi}{N} k n} = \sum_{n=0}^{N-1} x[n] W_N^{k n}, \quad k = 0, 1, \dots, N-1", "2.4")

    vh.add_p(doc, 
        "Trong đó, W_N = e^{−j 2π / N} là thừa số quay (twiddle factor). Phổ biên độ tại mỗi bin tần số k được tính bằng công thức:", indent=0.394)

    vh.add_equation_omml(doc, r"|X[k]| = \sqrt{\text{Re}\{X[k]\}^2 + \text{Im}\{X[k]\}^2}", "2.5")

    vh.add_p(doc, 
        "Nếu tính toán DFT trực tiếp theo công thức (2.4), độ phức tạp tính toán là O(N²), đòi hỏi 4\u00A0096² ≈ 16.7 triệu phép nhân phức cho mỗi khung xử lý, "
        "vượt quá khả năng tính toán thời gian thực của vi điều khiển. Do đó, thuật toán Fast Fourier Transform (FFT) phân chia theo thời gian "
        "(Decimation-in-Time Radix-2) của Cooley và Tukey [1] được triển khai, giảm độ phức tạp xuống O(N log₂ N):", indent=0.394)

    vh.add_equation_omml(doc, r"X[k] = X_{\text{even}}[k] + W_N^k X_{\text{odd}}[k]", "2.6")

    vh.add_p(doc, 
        "Nhờ thuật toán FFT radix-2, số phép nhân phức cho khung 4\u00A0096 điểm giảm xuống còn (N/2) log₂ N = 2\u00A0048 × 12 = 24\u00A0576 phép tính, "
        "giúp thời gian thực thi trên CPU ESP32-S3 đạt khoảng 10–12\u00A0ms [CẦN ĐO THỰC TẾ hoặc ghi rõ điều kiện tham chiếu].", indent=0.394)

    # 2.5 Độ phân giải tần số và đánh đổi thời gian - tần số
    vh.add_heading_2(doc, "2.5. Độ phân giải tần số và đánh đổi thời gian - tần số")
    vh.add_p(doc, 
        "Độ phân giải tần số của phép biến đổi FFT (khoảng cách tần số giữa hai bin phổ liên tiếp Δf) và thời lượng khung thời gian T_frame "
        "được xác định bởi các công thức cơ bản sau [8]:", indent=0.394)

    vh.add_equation_omml(doc, r"\Delta f = \frac{F_s}{N}", "2.7")
    vh.add_equation_omml(doc, r"T_{\text{frame}} = \frac{N}{F_s} = \frac{1}{\Delta f}", "2.8")

    vh.add_p(doc, 
        "Với cấu hình hệ thống F_s = 16\u00A0000\u00A0Hz và N = 4\u00A0096 mẫu, ta có các giá trị cụ thể:", indent=0.394)

    vh.add_equation_omml(doc, r"\Delta f = \frac{16000}{4096} = 3.90625 \text{ Hz/bin}", "2.9")
    vh.add_equation_omml(doc, r"T_{\text{frame}} = \frac{4096}{16000} = 0.256 \text{ s} = 256.0 \text{ ms}", "2.10")

    vh.add_callout(doc, "NGUYÊN LÝ ĐÁNH ĐỔI THỜI GIAN - TẦN SỐ",
        "Biểu thức (2.8) phản ánh nguyên lý bất định Heisenberg-Gabor trong xử lý tín hiệu: ta không thể đồng thời tối ưu hóa "
        "độ phân giải thời gian và độ phân giải tần số. Muốn thu hẹp khoảng cách bin phổ Δf để tăng độ chính xác nhận diện nốt trầm, "
        "bắt buộc phải tăng độ dài khung N, dẫn tới thời lượng khung T_frame kéo dài và làm tăng độ trễ đáp ứng của hệ thống. "
        "Lựa chọn N = 4 096 tại F_s = 16 000 Hz là điểm cân bằng kỹ thuật hợp lý giữa độ trễ (256 ms) và độ mịn phổ (3.90625 Hz/bin).")

    # 2.6 Rò rỉ phổ và kỹ thuật cửa sổ hóa
    vh.add_heading_2(doc, "2.6. Rò rỉ phổ và kỹ thuật cửa sổ hóa")
    vh.add_p(doc, 
        "Khi lấy một đoạn tín hiệu hữu hạn N mẫu, tương đương với việc nhân tín hiệu liên tục vô hạn với một cửa sổ chữ nhật trong miền thời gian. "
        "Trong miền tần số, phép nhân này chuyển thành phép tích chập của phổ tín hiệu với đáp ứng hàm sinc của cửa sổ chữ nhật. "
        "Vì búp sóng phụ (side lobe) của cửa sổ chữ nhật chỉ suy giảm ở mức −13\u00A0dB, năng lượng của đỉnh phổ sẽ bị tràn lan mạnh sang các bin lân cận, "
        "gây ra hiện tượng rò rỉ phổ (spectral leakage) và có thể che lấp các họa âm biên độ nhỏ lân cận. "
        "Để khắc phục, tín hiệu được nhân với một hàm cửa sổ mượt w[n] trước khi đưa vào thuật toán FFT [8]:", indent=0.394)

    vh.add_equation_omml(doc, r"x_w[n] = x[n] \cdot w[n], \quad n = 0, 1, \dots, N-1", "2.11")

    vh.add_p(doc, 
        "Hệ thống sử dụng cửa sổ Hann dạng tuần hoàn (periodic Hann window), được định nghĩa theo công thức:", indent=0.394)

    vh.add_equation_omml(doc, r"w[n] = 0.5 \left(1 - \cos\left(\frac{2\pi n}{N}\right)\right), \quad n = 0, 1, \dots, N-1", "2.12")

    vh.add_p(doc, 
        "Cửa sổ Hann có mức suy giảm búp phụ lên tới −31\u00A0dB và tốc độ suy giảm −18\u00A0dB/octave, giúp triệt tiêu hiện tượng rò rỉ phổ hiệu quả, "
        "bảo vệ các đỉnh họa âm yếu không bị nhiễu nền lấn át.", indent=0.394)

    vh.add_figure_image(doc, os.path.join(FIGURES_DIR, "fig_2_3_hann_leakage.png"), 
                       "Hình 2.3: Hiện tượng rò rỉ phổ và đáp ứng tần số của cửa sổ Hann")

    # 2.7 Phát hiện đỉnh phổ cục bộ và tỷ số tín hiệu trên nhiễu SNR
    vh.add_heading_2(doc, "2.7. Phát hiện đỉnh phổ cục bộ và tỷ số tín hiệu trên nhiễu SNR")
    vh.add_p(doc, 
        "Một bin tần số k được xác định là đỉnh phổ cục bộ nếu biên độ của nó lớn hơn hoặc bằng hai bin lân cận trực tiếp:", indent=0.394)

    vh.add_equation_omml(doc, r"\text{mag}[k] \ge \text{mag}[k-1] \quad \text{và} \quad \text{mag}[k] \ge \text{mag}[k+1]", "2.13")

    vh.add_p(doc, 
        "Để loại trừ các đỉnh nhiễu ngẫu nhiên, độ nổi bật của đỉnh (Prominence) so với nền nhiễu cục bộ LocalFloor_k được tính toán theo công thức:", indent=0.394)

    vh.add_equation_omml(doc, r"\text{Prominence}_k = \frac{\text{mag}[k]}{\max(\text{LocalFloor}_k, 0.05)}", "2.14")

    vh.add_p(doc, 
        "Tỷ số tín hiệu trên nhiễu theo thang Decibel tương ứng được biểu diễn bằng:", indent=0.394)

    vh.add_equation_omml(doc, r"\text{SNR}_{\text{dB}, k} = 20 \log_{10}(\text{Prominence}_k)", "2.15")

    # 2.8 Tinh chỉnh tần số bằng phương pháp nội suy parabol bậc hai
    vh.add_heading_2(doc, "2.8. Tinh chỉnh tần số bằng phương pháp nội suy parabol bậc hai")
    vh.add_p(doc, 
        "Vì độ phân giải bin phổ là Δf ≈ 3.90625\u00A0Hz, nếu chỉ lấy tần số tương ứng với chỉ số bin nguyên k, sai số lượng tử hóa tối đa có thể lên tới "
        "±Δf/2 ≈ ±1.953\u00A0Hz. Mức sai số này là quá lớn khi cân chỉnh piano (tương đương gần 8 cent ở nốt A4). "
        "Để đạt độ chính xác dưới 0.1\u00A0Hz, phương pháp nội suy parabol bậc hai (Quadratic Interpolation) trên 3 điểm phổ liên tiếp quanh đỉnh k được áp dụng [7]:", indent=0.394)

    vh.add_equation_omml(doc, r"\alpha = \text{mag}[k-1], \quad \beta = \text{mag}[k], \quad \gamma = \text{mag}[k+1]", "2.16")

    vh.add_p(doc, 
        "Độ lệch đỉnh thực tế p (tính theo đơn vị bin, −0.5 ≤ p ≤ +0.5) so với bin đỉnh nguyên k được xác định bởi điểm cực trị của đường parabol đi qua 3 điểm (k−1, α), (k, β), (k+1, γ):", indent=0.394)

    vh.add_equation_omml(doc, r"p = \frac{1}{2} \frac{\alpha - \gamma}{\alpha - 2\beta + \gamma} = 0.5 \frac{\text{mag}[k-1] - \text{mag}[k+1]}{\text{mag}[k-1] - 2\text{mag}[k] + \text{mag}[k+1]}", "2.17")

    vh.add_p(doc, 
        "Tần số tinh chỉnh sau nội suy f_interp được tính theo công thức:", indent=0.394)

    vh.add_equation_omml(doc, r"f_{\text{interp}} = (k + p) \frac{F_s}{N} = (k + p) \Delta f", "2.18")

    vh.add_figure_image(doc, os.path.join(FIGURES_DIR, "fig_2_4_quadratic_interp.png"), 
                       "Hình 2.4: Nguyên lý nội suy đỉnh parabol bậc hai trên 3 bin phổ lân cận")

    vh.add_callout(doc, "LƯU Ý VỀ ĐỘ CHÍNH XÁC VÀ BIAS CỦA NỘI SUY PARABOL",
        "Giải thuật nội suy parabol bậc hai (2.17) giả định đỉnh phổ có dạng đường cong parabol. Tuy nhiên, dạng búp sóng chính thực tế "
        "của cửa sổ Hann là hàm kết hợp của sinc. Do đó, việc nội suy trực tiếp trên biên độ tuyến tính sẽ tồn tại một độ lệch bias toán học "
        "cố hữu (được phân tích chi tiết tại Mục 5.2). Dù vậy, phương pháp này vẫn giúp giảm sai số lượng tử hóa từ ±1.95 Hz xuống dưới 0.25 Hz "
        "với chi phí tính toán cực kỳ thấp trên vi điều khiển.")

    # 2.9 Cấu trúc họa âm piano và hiện tượng mất tần số cơ bản
    vh.add_heading_2(doc, "2.9. Cấu trúc họa âm piano và hiện tượng mất tần số cơ bản")
    vh.add_p(doc, 
        "Trong chuỗi dao động âm thanh của nhạc cụ có dây, các tần số thành phần lý thuyết f_m xấp xỉ là bội số nguyên của tần số cơ bản f₀ [7]:", indent=0.394)

    vh.add_equation_omml(doc, r"f_1 \approx f_0, \quad f_2 \approx 2f_0, \quad f_3 \approx 3f_0, \quad f_4 \approx 4f_0, \dots", "2.19")

    vh.add_p(doc, 
        "Tuy nhiên, đối với đàn piano acoustic, đặc biệt ở các nốt thuộc quãng tám trầm (từ C1 đến E3), một đặc tính vật lý phức tạp xuất hiện: "
        "tần số cơ bản f₀ bị suy giảm biên độ rất mạnh do kích thước bảng cộng hưởng âm thanh (soundboard) không đủ lớn để bức xạ hiệu quả các bước sóng dài. "
        "Trong nhiều trường hợp, biên độ của họa âm bậc 2 (2f₀) hoặc bậc 3 (3f₀) lại lớn gấp hàng chục lần so với f₀. "
        "Nếu hệ thống chỉ tìm kiếm đỉnh phổ có biên độ lớn nhất một cách đơn giản, thiết bị sẽ nhận diện nhầm thành họa âm bậc cao và sinh ra lỗi quãng tám. "
        "Đây chính là lý do thuật toán cần cơ chế chấm điểm đa họa âm để tìm lại f₀ bị mất.", indent=0.394)

    # 2.10 Tính bất điều hòa của dây đàn piano (Inharmonicity)
    vh.add_heading_2(doc, "2.10. Tính bất điều hòa của dây đàn piano (Inharmonicity)")
    vh.add_p(doc, 
        "Dây đàn piano không phải là sợi dây lý thuyết hoàn toàn mềm dẻo, mà là dây thép có độ cứng uốn nhất định. "
        "Độ cứng này tạo thêm một lực hồi phục bổ sung, làm cho các họa âm bậc cao dao động nhanh hơn so với bội số nguyên lý thuyết. "
        "Hiện tượng này được gọi là tính bất điều hòa (Inharmonicity), được mô tả bởi phương trình Fletcher [6]:", indent=0.394)

    vh.add_equation_omml(doc, r"f_m = m f_0 \sqrt{1 + B m^2}", "2.20")

    vh.add_p(doc, 
        "Trong đó, m là bậc họa âm và B là hệ số bất điều hòa của dây đàn. Hệ số B phụ thuộc vào đường kính, chiều dài và lực căng dây:", indent=0.394)

    vh.add_p(doc, 
        "Ở các nốt trầm với dây đàn ngắn và dày, B có thể đạt từ 0.0001 đến 0.0005, khiến họa âm bậc 4 hoặc bậc 5 bị dịch lên cao đáng kể so với 4f₀ hoặc 5f₀. "
        "Do đó, thuật toán đối sánh họa âm phải có dải dung sai tìm kiếm linh hoạt (cho phép độ lệch tăng dần theo bậc m) thay vì dò tìm chính xác tại vị trí m·f₀.", indent=0.394)

    vh.add_figure_image(doc, os.path.join(FIGURES_DIR, "fig_2_5_inharmonicity.png"), 
                       "Hình 2.5: Quan hệ tần số họa âm piano và hệ số bất điều hòa B (Hình ảnh minh họa nguyên lý, không phải số đo thực tế)")

    # 2.11 Hệ âm đo bình quân 12 cung đều (12-TET)
    vh.add_heading_2(doc, "2.11. Hệ âm đo bình quân 12 cung đều (12-TET)")
    vh.add_p(doc, 
        "Hệ thống âm nhạc phương Tây hiện đại sử dụng Hệ âm đo bình quân 12 cung đều (12-Tone Equal Temperament — 12-TET), "
        "chia mỗi quãng tám (tỷ lệ tần số 2:1) thành 12 nửa cung với tỷ lệ tần số giữa hai nửa cung kế tiếp là một hằng số r:", indent=0.394)

    vh.add_equation_omml(doc, r"r = \sqrt[12]{2} = 2^{1/12} \approx 1.059463094", "2.21")

    vh.add_p(doc, 
        "Quy chuẩn quốc tế ISO 16 quy định nốt A4 có tần số chuẩn là 440.000\u00A0Hz, tương ứng với số thứ tự n_MIDI = 69 trong chuẩn MIDI. "
        "Từ một tần số cơ bản đo được f₀, chỉ số nốt MIDI liên tục n_cont và số thứ tự MIDI nguyên n_MIDI được tính theo công thức [5]:", indent=0.394)

    vh.add_equation_omml(doc, r"n_{\text{cont}} = 69 + 12 \log_2\left(\frac{f_0}{440.0}\right)", "2.22")
    vh.add_equation_omml(doc, r"n_{\text{MIDI}} = \text{round}\left(69 + 12 \log_2\left(\frac{f_0}{440.0}\right)\right)", "2.23")

    vh.add_p(doc, 
        "Tần số lý thuyết danh định của nốt nhạc f_target tương ứng với n_MIDI được xác định bởi:", indent=0.394)

    vh.add_equation_omml(doc, r"f_{\text{target}} = 440.0 \times 2^{\frac{n_{\text{MIDI}} - 69}{12}}", "2.24")

    vh.add_p(doc, 
        "Tên nốt nhạc và quãng tám tương ứng được trích xuất bằng các phép toán số học:", indent=0.394)

    vh.add_equation_omml(doc, r"\text{note\_idx} = n_{\text{MIDI}} \pmod{12}", "2.25")
    vh.add_equation_omml(doc, r"\text{octave} = \left\lfloor \frac{n_{\text{MIDI}}}{12} \right\rfloor - 1", "2.26")

    # 2.12 Khái niệm độ lệch Cent và phân loại trạng thái cân chỉnh
    vh.add_heading_2(doc, "2.12. Khái niệm độ lệch Cent và phân loại trạng thái cân chỉnh")
    vh.add_p(doc, 
        "Trong kỹ thuật âm thanh và chế tác nhạc cụ, một nửa cung được chia nhỏ thành 100 Cent theo thang đo logarit. "
        "Một quãng tám tương ứng với 1\u00A0200 Cent. Độ lệch cao độ Cent giữa tần số đo được f₀ và tần số mục tiêu f_target được tính theo công thức [5]:", indent=0.394)

    vh.add_equation_omml(doc, r"\text{cents} = 1200 \log_2\left(\frac{f_0}{f_{\text{target}}}\right)", "2.27")

    vh.add_p(doc, 
        "Hệ thống phân loại trạng thái lên dây thành 3 vùng rõ ràng dựa trên ngưỡng dung sai chuẩn ±5 cent:", indent=0.394)

    vh.add_p(doc, "• THẤP: cents < −5.0 cent (cao độ thấp hơn chuẩn, cần tăng lực căng dây).", indent=0.394, space_after=3)
    vh.add_p(doc, "• ĐẠT CHUẨN (IN TUNE): −5.0 cent ≤ cents ≤ +5.0 cent (cao độ đạt chuẩn, âm thanh chuẩn xác).", indent=0.394, space_after=3)
    vh.add_p(doc, "• CAO: cents > +5.0 cent (cao độ cao hơn chuẩn, cần giảm lực căng dây).", indent=0.394, space_after=6)

print("v2_ch1_ch2 module ready.")
