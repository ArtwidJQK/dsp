# -*- coding: utf-8 -*-
"""
Module: Chapter 3 (System Architecture & Hardware) and Chapter 4 (DSP Implementation on ESP32-S3)
for LeTanDung_24150654_v2.docx
Strictly adheres to:
- A4, 13pt Times New Roman, Black, 1.3 line spacing, 6pt after, 1.0cm first line indent.
- Headings: Heading 1 (16pt bold uppercase), Heading 2 (14pt bold), Heading 3 (13pt bold italic).
- Real OMML equations (3.1 to 3.3, 4.1) in 2-column borderless tables (7920 + 1152 dxa).
- Figures 3.1 to 3.6 inserted with captions below.
- Corrected bass-gate logic (<55 Hz requires h_count >= 3 AND mag >= 14.0 simultaneously; 55-110 Hz condition added).
- Corrected 3.5% ≈ 60 cents (not 50 cents).
- Corrected 5 bins skipped (k-2..k+2) and median of 24 sorted bins in noise floor estimation.
- Added Table 4.1: Parameters and thresholds in firmware.
- Condensed Web UI sections (3.9, 4.10, 4.11).
- Retained exact C code logic in code blocks with Consolas 10pt styling.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

import v2_helpers as vh

FIGURES_DIR = r"D:\dsp\LeTanDung_24150654\figures"

def build_ch3_ch4(doc):
    # =========================================================================
    # CHƯƠNG 3 — THIẾT KẾ HỆ THỐNG VÀ PHẦN CỨNG
    # =========================================================================
    vh.add_heading_1(doc, "CHƯƠNG 3 — THIẾT KẾ HỆ THỐNG VÀ PHẦN CỨNG", is_chapter=True)

    # 3.1 Kiến trúc tổng thể hệ thống
    vh.add_heading_2(doc, "3.1. Kiến trúc tổng thể hệ thống")
    vh.add_p(doc, 
        "Hệ thống thiết bị lên dây đàn piano chromatic được thiết kế theo cấu trúc nhúng tích hợp cao, "
        "hoạt động độc lập và không phụ thuộc vào máy tính hay kết nối Internet bên ngoài. "
        "Toàn bộ quy trình từ thu nhận sóng âm cơ học, chuyển đổi số, phân tích phổ tần số thời gian thực "
        "đến hiển thị trực quan được thực thi trọn vẹn trên vi điều khiển ESP32-S3.", indent=0.394)

    vh.add_figure_image(doc, os.path.join(FIGURES_DIR, "fig_3_1_system_block.png"), 
                       "Hình 3.1: Sơ đồ khối tổng thể hệ thống lên dây piano chromatic")

    vh.add_p(doc, 
        "Hệ thống bao gồm 4 khối chức năng chính:", indent=0.394)
    vh.add_p(doc, "1. Khối thu nhận âm thanh: Microphone MEMS kỹ thuật số INMP441 tiếp nhận sóng âm thanh piano và chuyển đổi thành luồng dữ liệu số I2S 24-bit/32-bit slot ở tần số lấy mẫu 16\u00A0000\u00A0Hz.", indent=0.394, space_after=3)
    vh.add_p(doc, "2. Khối điều khiển và xử lý trung tâm: Vi điều khiển ESP32-S3 thu thập dữ liệu qua cơ chế I2S DMA, lưu vào bộ đệm trượt 4\u00A0096 mẫu với độ gối 50%, thực thi chuỗi thuật toán DSP phân tích phổ và ánh xạ cao độ.", indent=0.394, space_after=3)
    vh.add_p(doc, "3. Khối truyền thông và giao diện người dùng: ESP32-S3 khởi tạo mạng Wi-Fi SoftAP và vận hành HTTP Web Server nhúng, đóng gói kết quả phân tích thành định dạng JSON và truyền về trình duyệt qua giao thức HTTP/CDP.", indent=0.394, space_after=3)
    vh.add_p(doc, "4. Khối nguồn: Cung cấp điện áp một chiều 3.3\u00A0V và 5\u00A0V ổn định từ cổng USB máy tính hoặc pin sạc dự phòng.", indent=0.394, space_after=6)

    # 3.2 Lựa chọn linh kiện phần cứng
    vh.add_heading_2(doc, "3.2. Lựa chọn linh kiện phần cứng")
    vh.add_p(doc, 
        "Vi điều khiển ESP32-S3 (Espressif Systems): ESP32-S3 sở hữu vi xử lý lõi kép 32-bit Xtensa LX7 hoạt động ở tần số xung nhịp lên tới 240\u00A0MHz, "
        "tích hợp 512\u00A0KB SRAM nội và hỗ trợ bộ chỉ lệnh mở rộng PIE (Processor Instruction Extension) cho các phép toán vector SIMD [4]. "
        "Mặc dù thuật toán FFT C thuần trong firmware hiện tại chạy tuần tự trên CPU, kiến trúc của ESP32-S3 hoàn toàn cho phép tăng tốc xử lý "
        "thông qua thư viện tối ưu hóa ESP-DSP trong tương lai. Ngoài ra, module DMA chuyên dụng cho ngoại vi I2S giúp chuyển trực tiếp "
        "dữ liệu âm thanh vào bộ nhớ mà hầu như không chiếm dụng chu kỳ xử lý của CPU lõi [4].", indent=0.394)

    vh.add_p(doc, 
        "Microphone MEMS I2S INMP441 (TDK InvenSense): INMP441 là microphone MEMS đa hướng kỹ thuật số hiệu năng cao, tích hợp sẵn cảm biến MEMS, "
        "tầng tiền khuếch đại tín hiệu và bộ biến đổi ADC delta-sigma 24-bit ngay trên một đế bán dẫn siêu nhỏ [3]. "
        "Với tỷ số tín hiệu trên nhiễu SNR đạt 61\u00A0dBA, độ nhạy −26\u00A0dBFS và đáp ứng tần số phẳng từ 60\u00A0Hz đến 15\u00A0000\u00A0Hz [3], "
        "INMP441 là linh kiện lý tưởng cho ứng dụng phân tích âm học piano. Việc xuất tín hiệu số trực tiếp qua bus I2S giúp loại trừ hoàn toàn "
        "nhiễu cảm ứng điện từ trên đường mạch analog so với các microphone thông thường.", indent=0.394)

    # 3.3 Thiết kế sơ đồ kết nối chân (Pinout)
    vh.add_heading_2(doc, "3.3. Thiết kế sơ đồ kết nối chân (Pinout)")
    vh.add_p(doc, 
        "Kết nối phần cứng giữa ESP32-S3 và mạch cảm biến INMP441 được tối ưu hóa nhằm giảm thiểu suy hao tín hiệu xung tần số cao và triệt tiêu nhiễu đường truyền.", indent=0.394)

    vh.add_figure_image(doc, os.path.join(FIGURES_DIR, "fig_3_2_wiring_pinout.png"), 
                       "Hình 3.2: Sơ đồ kết nối phần cứng giữa ESP32-S3 và microphone INMP441")

    vh.add_caption(doc, "Bảng 3.1: Bảng kết nối chân phần cứng giữa ESP32-S3 và module INMP441", is_table=True)
    tbl_pin = doc.add_table(rows=1, cols=4)
    tbl_pin.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_pin.autofit = False
    vh.set_table_borders(tbl_pin)

    pin_w = [Inches(1.2), Inches(1.3), Inches(1.3), Inches(2.5)]
    pin_hdrs = ["Chân INMP441", "Chân ESP32-S3", "Chức năng tín hiệu", "Ghi chú kỹ thuật"]
    for idx, text in enumerate(pin_hdrs):
        c = tbl_pin.rows[0].cells[idx]
        c.width = pin_w[idx]
        vh.set_cell_background(c, "EAECEF")
        vh.set_cell_margins(c, top=80, bottom=80, left=80, right=80)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.bold = True

    pin_rows = [
        ("VDD", "3V3", "Nguồn nuôi 3.3V", "Dòng tiêu thụ cực đại ~1.4 mA"),
        ("GND", "GND", "Nối đất chung", "Mặt phẳng mass chung chống nhiễu"),
        ("SCK / BCLK", "GPIO 4", "I2S Serial Clock", "Xung nhịp 1.024 MHz (16 kHz × 32 bit × 2 kênh)"),
        ("WS / LRCK", "GPIO 5", "I2S Word Select", "Tần số khung 16.0 kHz chọn kênh thu"),
        ("SD / DOUT", "GPIO 6", "I2S Serial Data", "Dữ liệu âm thanh 24-bit căn trái trong slot 32-bit"),
        ("L/R", "GND", "Channel Select", "Kéo xuống GND để chọn kênh trái (Left channel)"),
    ]
    for r_data in pin_rows:
        row = tbl_pin.add_row()
        for idx, text in enumerate(r_data):
            c = row.cells[idx]
            c.width = pin_w[idx]
            vh.set_cell_margins(c, top=60, bottom=60, left=80, right=80)
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx < 3 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(11)
            if idx == 0:
                r.bold = True

    vh.make_table_responsive(tbl_pin)

    # 3.4 Cấu trúc phần mềm đa nhiệm FreeRTOS
    vh.add_heading_2(doc, "3.4. Cấu trúc phần mềm đa nhiệm FreeRTOS")
    vh.add_p(doc, 
        "Hệ điều hành thời gian thực FreeRTOS được sử dụng để phân chia kiến trúc phần mềm thành các tác vụ độc lập chạy trên hai lõi CPU riêng biệt:", indent=0.394)

    vh.add_figure_image(doc, os.path.join(FIGURES_DIR, "fig_3_3_freertos_tasks.png"), 
                       "Hình 3.3: Cấu trúc đa nhiệm và phân chia luồng xử lý FreeRTOS")

    vh.add_caption(doc, "Bảng 3.2: Phân chia tài nguyên và cấu hình tác vụ FreeRTOS", is_table=True)
    tbl_rtos = doc.add_table(rows=1, cols=5)
    tbl_rtos.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_rtos.autofit = False
    vh.set_table_borders(tbl_rtos)

    rtos_w = [Inches(1.3), Inches(0.8), Inches(0.8), Inches(1.0), Inches(2.4)]
    rtos_hdrs = ["Tác vụ FreeRTOS", "Gắn lõi", "Ưu tiên", "Kích thước Stack", "Chức năng chính"]
    for idx, text in enumerate(rtos_hdrs):
        c = tbl_rtos.rows[0].cells[idx]
        c.width = rtos_w[idx]
        vh.set_cell_background(c, "EAECEF")
        vh.set_cell_margins(c, top=80, bottom=80, left=80, right=80)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.bold = True

    rtos_rows = [
        ("audio_dsp_task", "Core 0", "5 (Cao)", "16 KB", "Thu I2S DMA, đệm trượt 50%, Hann, FFT, HPS, tính cent"),
        ("http_server_task", "Core 1", "3 (Trung bình)", "8 KB", "Phục vụ HTTP Web Server, xử lý endpoint /api/data"),
        ("wifi_event_task", "Core 1", "2 (Thấp)", "4 KB", "Quản lý kết nối Wi-Fi SoftAP, xử lý ngắt mạng"),
    ]
    for r_data in rtos_rows:
        row = tbl_rtos.add_row()
        for idx, text in enumerate(r_data):
            c = row.cells[idx]
            c.width = rtos_w[idx]
            vh.set_cell_margins(c, top=60, bottom=60, left=80, right=80)
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx < 4 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(11)
            if idx == 0:
                r.bold = True

    vh.make_table_responsive(tbl_rtos)

    vh.add_p(doc, 
        "Việc cô lập tác vụ tính toán DSP chuyên sâu sang Lõi 0 và chuyển toàn bộ ngăn xếp giao thức mạng (Wi-Fi, HTTP) sang Lõi 1 "
        "ngăn ngừa tình trạng tắc nghẽn luồng xử lý âm thanh thời gian thực. Cấu hình phần mềm sử dụng dma_desc_num = 16 bộ mô tả đệm DMA "
        "với độ dài mỗi bộ mô tả dma_frame_num = 256 mẫu, đảm bảo không xảy ra hiện tượng tràn bộ đệm I2S (DMA underrun).", indent=0.394)

    # 3.5 Thu thập âm thanh qua I2S DMA và bộ đệm trượt 50%
    vh.add_heading_2(doc, "3.5. Thu thập âm thanh qua I2S DMA và bộ đệm trượt 50%")
    vh.add_p(doc, 
        "Khi phân tích tín hiệu âm nhạc biến thiên theo thời gian (non-stationary signals), việc phân tích từng khung độc lập không gối đầu "
        "sẽ làm giảm độ phân giải thời gian và dễ bỏ lỡ các giai đoạn khởi phát nốt (attack phase). "
        "Hệ thống triển khai cơ chế đệm trượt gối đầu 50% (50% Overlap Rolling Buffer):", indent=0.394)

    vh.add_figure_image(doc, os.path.join(FIGURES_DIR, "fig_3_4_rolling_buffer.png"), 
                       "Hình 3.4: Cơ chế đệm trượt gối 50% và đồng bộ hóa phân tích FFT")

    vh.add_p(doc, 
        "Mỗi khung phân tích có độ dài N = 4\u00A0096 mẫu (tương ứng 256.0\u00A0ms). Tại mỗi chu kỳ xử lý, tác vụ I2S chỉ cần đọc thêm "
        "HOP_SIZE = 2\u00A0048 mẫu mới (tương ứng 128.0\u00A0ms). Dữ liệu 2\u00A0048 mẫu cũ của nửa sau khung trước được dịch chuyển lên nửa đầu, "
        "và 2\u00A0048 mẫu mới được chèn vào nửa sau. Nhờ vậy, tần suất cập nhật kết quả phân tích cao độ đạt 128\u00A0ms một lần, "
        "giúp độ phản hồi của thiết bị tăng gấp đôi so với phương pháp không gối đầu.", indent=0.394)

    # 3.6 Thuật toán phát hiện cao độ đa họa âm và cơ chế Bass-Gate
    vh.add_heading_2(doc, "3.6. Thuật toán phát hiện cao độ đa họa âm và cơ chế Bass-Gate")
    vh.add_p(doc, 
        "Để giải quyết triệt để vấn đề mất tần số cơ bản ở nốt trầm và tính bất điều hòa của piano, hệ thống triển khai thuật toán "
        "đánh giá giả thuyết tần số cơ bản đa họa âm (Harmonic Hypothesis Scoring).", indent=0.394)

    vh.add_figure_image(doc, os.path.join(FIGURES_DIR, "fig_3_5_harmonic_flowchart.png"), 
                       "Hình 3.5: Lưu đồ thuật toán đánh giá giả thuyết tần số cơ bản và cơ chế Bass-Gate")

    vh.add_p(doc, 
        "Đối với mỗi đỉnh phổ nổi bật f_peak phát hiện được, hệ thống sinh ra các giả thuyết tần số cơ bản f_hyp tương ứng với các ước số nguyên:", indent=0.394)

    vh.add_equation_omml(doc, r"f_{\text{hyp}} = \frac{f_{\text{peak}}}{m}, \quad m = 1, 2, 3, 4, 5, 6", "3.1")

    vh.add_p(doc, 
        "Với mỗi giả thuyết f_hyp, thuật toán tiến hành kiểm tra sự tồn tại của chuỗi họa âm kỳ vọng f_m = m·f_hyp. "
        "Một họa âm bậc m được coi là hợp lệ khi thỏa mãn đồng thời các điều kiện toán học sau:", indent=0.394)

    vh.add_equation_omml(doc, r"\begin{cases} \text{mag}[k_m] \ge \max(\text{mag}[k_m-1], \text{mag}[k_m+1]) \\ \text{Prominence}_m \ge 2.2 \\ \text{mag}_m \ge 1.0 \end{cases}", "3.2")

    vh.add_p(doc, 
        "Điểm số thô (Score_raw) của giả thuyết f_hyp được tích lũy theo công thức kết hợp độ nổi bật, biên độ và hệ số thưởng số lượng họa âm:", indent=0.394)

    vh.add_equation_omml(doc, r"\text{Score}_{\text{raw}} = \left( \sum_{m \in \text{found}} \frac{1}{\sqrt{m}} \ln(1 + \text{Prominence}_m) \sqrt{\text{mag}_m} \right) \times \left(1 + 0.40 \times (h_{\text{count}} - 1)\right)", "3.3")

    vh.add_p(doc, 
        "Cơ chế Bass-Gate bảo vệ dải hạ âm: Trong môi trường thực tế, các rung động cơ học hoặc nhiễu 50\u00A0Hz từ nguồn điện lưới có thể "
        "tạo ra các đỉnh giả tạo ở dải tần số thấp. Do đó, firmware thiết lập cơ chế lọc điều kiện nghiêm ngặt cho dải tần số dưới 110\u00A0Hz:", indent=0.394)

    vh.add_p(doc, 
        "• Đối với giả thuyết f_hyp < 55\u00A0Hz: Hệ thống yêu cầu đồng thời phải có tối thiểu 3 họa âm hợp lệ (h_count ≥ 3) VÀ biên độ đỉnh "
        "phải đạt từ 14.0 trở lên (mag ≥ 14.0). Nếu vi phạm bất kỳ điều kiện nào trong hai điều kiện trên (h_count < 3 hoặc mag < 14.0), "
        "giả thuyết sẽ bị phạt 85% điểm số (Score = Score × 0.15), ngăn chặn việc nhận diện sai nhiễu nền thành nốt cực trầm.", indent=0.394, space_after=3)

    vh.add_p(doc, 
        "• Đối với giả thuyết trong dải 55–110\u00A0Hz: Hệ thống bổ sung điều kiện kiểm tra năng lượng tổng thể, yêu cầu biên độ cực đại "
        "tìm thấy phải đạt max_found_mag ≥ 2.5 hoặc tổng năng lượng họa âm total_energy ≥ 3.0 để đảm bảo chỉ chấp nhận các tín hiệu nốt trầm thực sự.", indent=0.394, space_after=6)

    # 3.7 Cơ chế làm mịn thời gian và khóa nốt
    vh.add_heading_2(doc, "3.7. Cơ chế làm mịn thời gian và khóa nốt")
    vh.add_p(doc, 
        "Để loại trừ các dao động nhảy nốt ngẫu nhiên do nhiễu tức thời giữa các khung phân tích, firmware áp dụng bộ lọc làm mịn thời gian "
        "(Temporal Stability Gating). Một nốt nhạc mới chỉ được công nhận và hiển thị lên giao diện khi nó được phát hiện liên tục ổn định "
        "trong tối thiểu 2 khung phân tích liên tiếp. Nếu tần số đo được nằm trong khoảng dung sai ±3.5% (tương đương khoảng 60 cent) "
        "so với nốt đang khóa, hệ thống duy trì trạng thái nhận diện và áp dụng bộ lọc thông thấp IIR trung bình trượt có trọng số "
        "để hiển thị mượt mà diễn biến độ lệch Cent của nghệ nhân lên dây.", indent=0.394)

    # 3.8 Truyền thông dữ liệu và đồng bộ hóa đa nhiệm
    vh.add_heading_2(doc, "3.8. Truyền thông dữ liệu và giảm thiểu xung đột với tác vụ DSP")
    vh.add_p(doc, 
        "Để đảm bảo tác vụ tính toán DSP chạy trên Lõi 0 không bao giờ bị trễ hạn thời gian thực do các yêu cầu mạng từ Lõi 1, "
        "cấu trúc chia sẻ dữ liệu kết quả đo đạc được thiết kế sử dụng vùng nhớ chia sẻ toàn cục bảo vệ bởi Spinlock Critical Section. "
        "Tác vụ DSP chỉ chiếm giữ critical section trong thời gian cực ngắn (dưới 1 micro giây) để sao chép kết quả cấu trúc sang bộ nhớ đệm chia sẻ. "
        "Tác vụ HTTP Server trên Lõi 1 khi nhận yêu cầu GET từ trình duyệt sẽ sao chép dữ liệu từ vùng đệm này và serialize thành chuỗi JSON "
        "độc lập, loại bỏ xung đột tranh chấp tài nguyên giữa hai lõi xử lý.", indent=0.394)

    # 3.9 Thiết kế giao diện người dùng Web (Frontend)
    vh.add_heading_2(doc, "3.9. Thiết kế giao diện người dùng Web (Frontend)")
    vh.add_p(doc, 
        "Giao diện người dùng được xây dựng hoàn toàn bằng HTML5, CSS3 và JavaScript thuần, được nhúng trực tiếp vào bộ nhớ Flash của ESP32-S3. "
        "Người dùng chỉ cần dùng điện thoại hoặc máy tính xách tay kết nối vào điểm phát sóng Wi-Fi của thiết bị và truy cập địa chỉ IP 192.168.4.1. "
        "Trang web tự động thiết lập chu kỳ Polling định kỳ 125\u00A0ms qua API /api/data để cập nhật trạng thái hiển thị.", indent=0.394)

    vh.add_figure_image(doc, os.path.join(FIGURES_DIR, "fig_3_6_ui_polling_flow.png"), 
                       "Hình 3.6: Luồng đồng bộ trạng thái giao diện người dùng qua Web Polling định kỳ")

    vh.add_p(doc, 
        "Giao diện trực quan bao gồm: đồng hồ đo Cent dạng kim chỉ góc xoay mượt mà, banner phân loại trạng thái cân chỉnh (THẤP / IN TUNE / CAO), "
        "bàn phím piano ảo mô phỏng 73 phím từ C2 đến C8 (hỗ trợ hiển thị trực quan các nốt phổ biến trên đàn piano) và bảng thông số kỹ thuật "
        "chi tiết (tần số đo được f₀, tần số mục tiêu f_target, độ lệch Δf và SNR).", indent=0.394)

    # =========================================================================
    # CHƯƠNG 4 — HIỆN THỰC THUẬT TOÁN DSP TRÊN ESP32-S3
    # =========================================================================
    vh.add_heading_1(doc, "CHƯƠNG 4 — HIỆN THỰC THUẬT TOÁN DSP TRÊN ESP32-S3", is_chapter=True)

    # 4.1 Cấu hình I2S driver
    vh.add_heading_2(doc, "4.1. Cấu hình I2S driver trong ESP-IDF")
    vh.add_p(doc, 
        "Trình điều khiển I2S được khởi tạo thông qua thư viện chuẩn ESP-IDF với cấu hình kênh I2S_NUM_0 ở chế độ Master RX. "
        "Tần số xung nhịp lấy mẫu được thiết lập F_s = 16\u00A0000\u00A0Hz, định dạng dữ liệu 32-bit slot với độ dài dữ liệu âm thanh 24-bit căn trái. "
        "Dữ liệu được chuyển trực tiếp vào bộ nhớ thông qua cơ chế DMA mà không tiêu tốn chu kỳ CPU.", indent=0.394)

    # 4.2 Tiền xử lý tín hiệu
    vh.add_heading_2(doc, "4.2. Tiền xử lý tín hiệu và khử offset DC")
    vh.add_p(doc, 
        "Dữ liệu thô từ microphone INMP441 gồm các mẫu số nguyên 32-bit có dấu. Do các sai số vật lý của cảm biến MEMS, "
        "tín hiệu luôn tồn tại một điện áp dịch chuyển một chiều (DC offset). Nếu không loại bỏ, thành phần DC này sẽ tạo ra "
        "một đỉnh phổ cực lớn tại bin 0 (f = 0\u00A0Hz), rò rỉ sang các bin tần số thấp và che lấp nốt trầm. "
        "Thuật toán khử DC bằng cách tính giá trị trung bình mẫu μ và trừ trực tiếp khỏi toàn bộ khung N mẫu:", indent=0.394)

    vh.add_equation_omml(doc, r"\mu = \frac{1}{N} \sum_{n=0}^{N-1} x_{\text{raw}}[n], \quad x[n] = x_{\text{raw}}[n] - \mu", "4.1")

    # 4.3 Áp dụng cửa sổ Hann
    vh.add_heading_2(doc, "4.3. Áp dụng cửa sổ Hann tuần hoàn")
    vh.add_p(doc, 
        "Hàm khởi tạo mảng trọng số cửa sổ Hann được thực hiện một lần duy nhất trong giai đoạn khởi động hệ thống để tiết kiệm thời gian:", indent=0.394)

    code_hann = (
        "void init_hann_window(void) {\n"
        "    for (int i = 0; i < FFT_SIZE; i++) {\n"
        "        // Periodic Hann window: w[n] = 0.5 * (1 - cos(2*pi*n / N))\n"
        "        s_hann[i] = 0.5f * (1.0f - cosf(2.0f * (float)M_PI * (float)i / (float)FFT_SIZE));\n"
        "    }\n"
        "}"
    )
    vh.add_code_block(doc, code_hann)

    # 4.4 Thuật toán FFT radix-2
    vh.add_heading_2(doc, "4.4. Thuật toán FFT radix-2 Cooley-Tukey")
    vh.add_p(doc, 
        "Thuật toán biến đổi Fourier nhanh Decimation-in-Time Radix-2 được triển khai trực tiếp bằng ngôn ngữ C với kỹ thuật đảo bit chỉ số (bit-reversal) "
        "và tính toán bướm (butterfly computations) tại chỗ (in-place) để tối ưu hóa việc sử dụng bộ nhớ cache:", indent=0.394)

    code_fft = (
        "static void fft_radix2(float *real, float *imag, int n) {\n"
        "    // 1. Bit-reversal permutation\n"
        "    int j = 0;\n"
        "    for (int i = 0; i < n - 1; i++) {\n"
        "        if (i < j) {\n"
        "            float tr = real[i]; real[i] = real[j]; real[j] = tr;\n"
        "            float ti = imag[i]; imag[i] = imag[j]; imag[j] = ti;\n"
        "        }\n"
        "        int k = n >> 1;\n"
        "        while (k <= j) { j -= k; k >>= 1; }\n"
        "        j += k;\n"
        "    }\n"
        "    // 2. Butterfly computations across log2(n) stages\n"
        "    for (int len = 2; len <= n; len <<= 1) {\n"
        "        float angle = -2.0f * (float)M_PI / (float)len;\n"
        "        float wlen_r = cosf(angle), wlen_i = sinf(angle);\n"
        "        for (int i = 0; i < n; i += len) {\n"
        "            float w_r = 1.0f, w_i = 0.0f;\n"
        "            for (int k = 0; k < len / 2; k++) {\n"
        "                int u = i + k, v = i + k + len / 2;\n"
        "                float vr = real[v] * w_r - imag[v] * w_i;\n"
        "                float vi = real[v] * w_i + imag[v] * w_r;\n"
        "                real[v] = real[u] - vr; imag[v] = imag[u] - vi;\n"
        "                real[u] += vr; imag[u] += vi;\n"
        "                float next_wr = w_r * wlen_r - w_i * wlen_i;\n"
        "                w_i = w_r * wlen_i + w_i * wlen_r; w_r = next_wr;\n"
        "            }\n"
        "        }\n"
        "    }\n"
        "}"
    )
    vh.add_code_block(doc, code_fft)

    # 4.5 Tính toán phổ biên độ
    vh.add_heading_2(doc, "4.5. Tính toán phổ biên độ")
    vh.add_p(doc, 
        "Sau khi thực hiện FFT, phổ biên độ mag[k] được tính toán cho N/2 = 2\u00A0048 bin tần số dương theo công thức căn bậc hai của tổng bình phương phần thực và phần ảo:", indent=0.394)

    code_mag = (
        "static void compute_magnitude_spectrum(const float *real, const float *imag, float *mag, int n) {\n"
        "    for (int k = 0; k < n / 2; k++) {\n"
        "        mag[k] = sqrtf(real[k] * real[k] + imag[k] * imag[k]);\n"
        "    }\n"
        "}"
    )
    vh.add_code_block(doc, code_mag)

    # 4.6 Phát hiện đỉnh phổ và ước lượng nền nhiễu
    vh.add_heading_2(doc, "4.6. Phát hiện đỉnh phổ cục bộ và ước lượng nền nhiễu")
    vh.add_p(doc, 
        "Để ước lượng mức nền nhiễu cục bộ quanh đỉnh bin k, thuật toán trích xuất một cửa sổ gồm 29 bin lân cận [k−14, k+14], "
        "bỏ qua 5 bin trung tâm [k−2, k+2] chứa búp sóng chính của tín hiệu. Trong số 24 giá trị nền nhiễu còn lại, giá trị trung vị "
        "được ước lượng bằng cách sắp xếp và lấy trung bình phần tử thứ 12 và thứ 13, đảm bảo nền nhiễu không bị sai lệch bởi các đỉnh họa âm lân cận.", indent=0.394)

    # BẢNG 4.1 THIẾU Ở V1 -> BỔ SUNG ĐẦY ĐỦ Ở V2
    vh.add_caption(doc, "Bảng 4.1: Các ngưỡng tham số lọc nhiễu và phát hiện đỉnh phổ trong firmware", is_table=True)
    tbl_param = doc.add_table(rows=1, cols=4)
    tbl_param.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_param.autofit = False
    vh.set_table_borders(tbl_param)

    param_w = [Inches(1.8), Inches(1.1), Inches(1.0), Inches(2.4)]
    param_hdrs = ["Tên tham số trong firmware", "Giá trị", "Đơn vị", "Ý nghĩa và mục đích kỹ thuật"]
    for idx, text in enumerate(param_hdrs):
        c = tbl_param.rows[0].cells[idx]
        c.width = param_w[idx]
        vh.set_cell_background(c, "EAECEF")
        vh.set_cell_margins(c, top=80, bottom=80, left=80, right=80)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.bold = True

    param_rows = [
        ("MIN_AC_RMS_NORM", "0.0020", "Chuẩn hóa", "Ngưỡng năng lượng tối thiểu để phân biệt phím gõ với tĩnh lặng"),
        ("PEAK_MIN_MAG", "≥ 1.0", "Tuyến tính", "Biên độ tối thiểu để một đỉnh phổ được xem xét là ứng viên họa âm"),
        ("HARMONIC_PROM_MIN", "2.20", "Tỷ số", "Độ nổi bật yêu cầu so với nền nhiễu để công nhận đỉnh là họa âm hợp lệ"),
        ("BASS_GATE_FREQ", "55.0", "Hz", "Ngưỡng tần số kích hoạt cơ chế bảo vệ nốt cực trầm"),
        ("BASS_GATE_MIN_HARM", "≥ 3", "Họa âm", "Số lượng họa âm tối thiểu bắt buộc đối với nốt dưới 55 Hz"),
        ("BASS_GATE_MIN_MAG", "14.0", "Tuyến tính", "Biên độ tối thiểu bắt buộc đối với nốt dưới 55 Hz"),
        ("LOCK_TOLERANCE_RATIO", "0.035 (3.5%)", "Tỷ số (~60 c)", "Dải dung sai tần số để duy trì trạng thái khóa nốt hiện tại"),
        ("PITCH_HISTORY_LEN", "5", "Khung", "Chiều dài cửa sổ đệm lịch sử cao độ phục vụ bộ lọc làm mịn ổn định"),
        ("PEAK_REL_THRESHOLD", "[CẦN BỔ SUNG từ firmware]", "Tỷ số", "Ngưỡng biên độ tối thiểu so với đỉnh phổ lớn nhất trong khung"),
        ("PROMINENCE_MIN", "[CẦN BỔ SUNG từ firmware]", "Tỷ số", "Độ nổi bật tối thiểu của đỉnh phổ so với nền nhiễu cục bộ"),
    ]
    for r_data in param_rows:
        row = tbl_param.add_row()
        for idx, text in enumerate(r_data):
            c = row.cells[idx]
            c.width = param_w[idx]
            vh.set_cell_margins(c, top=60, bottom=60, left=80, right=80)
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if idx in [0, 3] else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(text)
            r.font.name = "Times New Roman" if idx != 0 else "Consolas"
            r.font.size = Pt(10 if idx == 0 else 11)
            if idx == 0:
                r.bold = True

    vh.make_table_responsive(tbl_param)

    # 4.7 Thuật toán chấm điểm giả thuyết
    vh.add_heading_2(doc, "4.7. Thuật toán đánh giá giả thuyết và chấm điểm họa âm")
    vh.add_p(doc, 
        "Đoạn mã C sau đây hiện thực quy trình đánh giá một giả thuyết tần số cơ bản f_hyp với cơ chế Bass-Gate nghiêm ngặt theo đúng thiết kế:", indent=0.394)

    code_scoring = (
        "static float evaluate_subharmonic_hypothesis(float f_hyp, const peak_t *peaks, int peak_count, ...)\n"
        "{\n"
        "    int h_count = 0;\n"
        "    float sum_score = 0.0f, total_energy = 0.0f, max_found_mag = 0.0f;\n"
        "    for (int m = 1; m <= 6; m++) {\n"
        "        float target_f = f_hyp * (float)m;\n"
        "        // Search for matching spectral peak within adaptive tolerance window\n"
        "        int idx = find_closest_peak(peaks, peak_count, target_f, tolerance);\n"
        "        if (idx >= 0 && peaks[idx].prominence >= 2.2f && peaks[idx].mag >= 1.0f) {\n"
        "            h_count++;\n"
        "            total_energy += peaks[idx].mag;\n"
        "            if (peaks[idx].mag > max_found_mag) max_found_mag = peaks[idx].mag;\n"
        "            sum_score += (1.0f / sqrtf((float)m)) * logf(1.0f + peaks[idx].prominence) * sqrtf(peaks[idx].mag);\n"
        "        }\n"
        "    }\n"
        "    float final_score = sum_score * (1.0f + 0.40f * (float)(h_count - 1));\n"
        "    // Bass-gate: penalize weak sub-55Hz hypothesis unless BOTH h_count >= 3 AND mag >= 14.0\n"
        "    if (f_hyp < 55.0f) {\n"
        "        if (h_count < 3 || max_found_mag < 14.0f) {\n"
        "            final_score *= 0.15f; // Heavy 85% penalty for unverified sub-bass\n"
        "        }\n"
        "    } else if (f_hyp < 110.0f) {\n"
        "        if (max_found_mag < 2.5f && total_energy < 3.0f) {\n"
        "            final_score *= 0.35f;\n"
        "        }\n"
        "    }\n"
        "    return final_score;\n"
        "}"
    )
    vh.add_code_block(doc, code_scoring)

    # 4.8 Nội suy đỉnh phổ parabol
    vh.add_heading_2(doc, "4.8. Nội suy đỉnh phổ parabol")
    vh.add_p(doc, 
        "Hàm nội suy parabol bậc hai tinh chỉnh tần số từ 3 mẫu biên độ mag[k−1], mag[k], mag[k+1]:", indent=0.394)

    code_qi = (
        "static float quadratic_interpolate(const float *mag, int k, float df) {\n"
        "    float alpha = mag[k - 1];\n"
        "    float beta  = mag[k];\n"
        "    float gamma = mag[k + 1];\n"
        "    float denom = alpha - 2.0f * beta + gamma;\n"
        "    if (fabsf(denom) < 1e-7f) return (float)k * df;\n"
        "    float p = 0.5f * (alpha - gamma) / denom;\n"
        "    return ((float)k + p) * df;\n"
        "}"
    )
    vh.add_code_block(doc, code_qi)

    # 4.9 Quy đổi cao độ và tính sai số Cent
    vh.add_heading_2(doc, "4.9. Quy đổi cao độ, tính sai số Cent và làm mịn thời gian")
    vh.add_p(doc, 
        "Quy trình ánh xạ từ tần số f₀ đo được sang nốt nhạc và tính độ lệch Cent:", indent=0.394)

    code_cents = (
        "static void map_frequency_to_note(float freq, note_result_t *res) {\n"
        "    if (freq < 20.0f || freq > 5000.0f) { res->valid = false; return; }\n"
        "    float note_num_cont = 69.0f + 12.0f * (logf(freq / 440.0f) / logf(2.0f));\n"
        "    int midi_note = (int)roundf(note_num_cont);\n"
        "    float target_freq = 440.0f * powf(2.0f, (float)(midi_note - 69) / 12.0f);\n"
        "    float cents = 1200.0f * (logf(freq / target_freq) / logf(2.0f));\n"
        "    res->measured_freq = freq;\n"
        "    res->target_freq = target_freq;\n"
        "    res->cents = cents;\n"
        "    res->midi_note = midi_note;\n"
        "    res->note_name = NOTE_NAMES[midi_note % 12];\n"
        "    res->octave = (midi_note / 12) - 1;\n"
        "    res->valid = true;\n"
        "}"
    )
    vh.add_code_block(doc, code_cents)

    # 4.10 Đóng gói dữ liệu JSON
    vh.add_heading_2(doc, "4.10. Đóng gói dữ liệu JSON và Web Server")
    vh.add_p(doc, 
        "Kết quả phân tích được tuần tự hóa thành định dạng chuỗi JSON nhẹ và truyền tới trình duyệt web "
        "khi có yêu cầu HTTP GET gửi tới endpoint /api/data. Cấu trúc gói tin bao gồm các trường: note, freq, target, "
        "cents, in_tune, octave, confidence, valid và rms. Chi tiết cấu trúc dữ liệu JSON được mô tả tại Phụ lục A.", indent=0.394)

    # 4.11 Giao diện web và hiển thị trực quan
    vh.add_heading_2(doc, "4.11. Giao diện web và hiển thị trực quan")
    vh.add_p(doc, 
        "Giao diện người dùng sử dụng CSS Flexbox và SVG để vẽ đồng hồ kim cent mượt mà, phản hồi góc xoay theo thời gian thực "
        "tương ứng với độ lệch từ −50 đến +50 cent. Banner màu sắc tự động cập nhật: Màu lục khi nốt đạt chuẩn IN TUNE (±5 cent), "
        "Màu xanh lam khi nốt bị THẤP (< −5 cent) và Màu hổ phách khi nốt bị CAO (> +5 cent). "
        "Bàn phím ảo tự động tô sáng phím tương ứng giúp người dùng dễ dàng định vị vị trí nốt trên đàn.", indent=0.394)

print("v2_ch3_ch4 module ready.")
