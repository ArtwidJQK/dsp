# -*- coding: utf-8 -*-
"""
Module: Chapter 3 (System Design) and Chapter 4 (Implementation)
Project: PIANO CHROMATIC TUNER USING ESP32-S3 AND INMP441
Student: Le Tan Dung - MSSV: 24150654
"""

from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import make_doc as md

def build_ch3_ch4(doc):
    # =========================================================================
    # CHƯƠNG 3 — THIẾT KẾ HỆ THỐNG
    # =========================================================================
    md.add_heading_1(doc, "CHƯƠNG 3 — THIẾT KẾ KIẾN TRÚC HỆ THỐNG")

    # 3.1 Kiến trúc tổng thể
    md.add_heading_2(doc, "3.1. Kiến trúc tổng thể hệ thống")
    md.add_p(doc, 
        "Hệ thống Piano Chromatic Tuner được thiết kế theo mô hình luồng dữ liệu thời gian thực khép kín (End-to-End Real-Time Pipeline), "
        "kết nối chặt chẽ giữa phần cứng thu nhận, tầng xử lý tín hiệu số nội tại trên chip và tầng hiển thị web không dây. "
        "Sơ đồ luồng xử lý tổng thể của hệ thống được mô tả chính xác như sau:", indent=0.4)

    # ASCII/Text architectural flow
    p_flow = doc.add_paragraph()
    p_flow.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_flow.paragraph_format.space_before = Pt(6)
    p_flow.paragraph_format.space_after = Pt(8)
    flow_text = (
        "Âm thanh Piano (Acoustic Pressure Wave)\n"
        "                     ↓\n"
        "Microphone MEMS I2S (INMP441) [ADC tích hợp]\n"
        "                     ↓  (Bus I2S 3-dây: BCLK, WS, SD)\n"
        "Bộ đệm DMA I2S (ESP32-S3 RX FIFO)\n"
        "                     ↓  (2048 mẫu mới = 128 ms)\n"
        "Bộ đệm trượt 50% Overlap (Rolling Buffer 4096 mẫu = 256 ms)\n"
        "                     ↓\n"
        "Khử mức một chiều (DC Removal: x[n] - mean)\n"
        "                     ↓\n"
        "Nhân cửa sổ Hann tiền tính toán (w[n] * x[n])\n"
        "                     ↓\n"
        "Biến đổi Fourier nhanh (FFT Radix-2 DIT 4096 điểm)\n"
        "                     ↓\n"
        "Tính phổ biên độ & Trích xuất đỉnh phổ cục bộ (Local Spectral Peaks)\n"
        "                     ↓\n"
        "Lọc sàn nhiễu trung vị 24-bin & Đánh giá tỷ số Prominence / SNR\n"
        "                     ↓\n"
        "Phân tích họa âm & Chấm điểm giả thuyết (Harmonic-Aware Hypothesis Scoring)\n"
        "                     ↓\n"
        "Nội suy parabol bậc hai (Quadratic Interpolation -> f0 liên tục)\n"
        "                     ↓\n"
        "Bộ lọc ổn định thời gian (Temporal Stability & Median Smoothing)\n"
        "                     ↓\n"
        "Ánh xạ nốt nhạc chuẩn MIDI (A4=440Hz) & Tính độ lệch Cents\n"
        "                     ↓  (Thread-Safe Critical Section Snapshot)\n"
        "Máy chủ HTTP nhúng (esp_http_server: GET /api/data)\n"
        "                     ↓  (Wi-Fi SoftAP / STA Transport)\n"
        "Giao diện Web Frontend người dùng (Celestial / Fantasy Piano Tuner)"
    )
    r_flow = p_flow.add_run(flow_text)
    r_flow.font.name = "Consolas"
    r_flow.font.size = Pt(9.5)
    r_flow.font.color.rgb = md.C_NAVY

    # 3.2 Thiết kế phần cứng
    md.add_heading_2(doc, "3.2. Thiết kế phần cứng vi điều khiển (ESP32-S3 N16R8)")
    md.add_p(doc, 
        "Khối xử lý trung tâm của hệ thống sử dụng module vi điều khiển thế hệ mới ESP32-S3 N16R8 của Espressif Systems. "
        "Đây là dòng vi điều khiển SoC chuyên dụng cho các ứng dụng xử lý tín hiệu âm thanh và AI/Edge Computing [3]. "
        "Các ưu điểm kỹ thuật then chốt khiến ESP32-S3 được lựa chọn thay vì các dòng vi điều khiển ESP32 đời cũ bao gồm:", indent=0.4)
    md.add_p(doc, 
        "• Lõi xử lý kép Xtensa 32-bit LX7 với xung nhịp tối đa lên tới 240 MHz, tích hợp tập lệnh mở rộng hỗ trợ tăng tốc phép tính số học véc-tơ (Vector Instructions / DSP SIMD), "
        "giúp thực thi thuật toán FFT Radix-2 và phép nhân dấu phẩy động 32-bit (single-precision float) cực nhanh [3].", indent=0.4)
    md.add_p(doc, 
        "• Dung lượng bộ nhớ dồi dào: 512 KB SRAM nội bộ kết hợp 8 MB Octal PSRAM tốc độ cao và 16 MB Quad SPI Flash (phiên bản N16R8). "
        "Dung lượng này cho phép cấp phát tĩnh toàn bộ các mảng đệm tín hiệu lớn (4096 điểm FFT thực, ảo, biên độ và cửa sổ Hann) hoàn toàn trong bộ nhớ nhanh SRAM (DRAM), "
        "tránh tối đa hiện tượng trễ truy xuất bus ngoài [3].", indent=0.4)
    md.add_p(doc, 
        "• Bộ điều khiển I2S thế hệ mới (I2S Standard Mode Driver) với công cụ DMA chuyên dụng, tự động chuyển tải dữ liệu từ bộ chuyển đổi ADC "
        "vào bộ đệm mà không làm tiêu tốn tài nguyên chu kỳ lệnh của CPU [3].", indent=0.4)

    table_esp_data = [
        ("Vi xử lý (CPU)", "Xtensa Dual-Core 32-bit LX7, xung nhịp cấu hình 240 MHz"),
        ("Tập lệnh DSP mở rộng", "Hỗ trợ SIMD Instructions, tăng tốc các phép toán bướm FFT"),
        ("Bộ nhớ SRAM nội bộ", "512 KB SRAM (Cấp phát toàn bộ mảng DSP trong DRAM nội tại)"),
        ("Bộ nhớ ngoài mở rộng", "8 MB Octal PSRAM + 16 MB Quad SPI Flash (N16R8)"),
        ("Khối ngoại vi I2S", "Bộ điều khiển I2S phần cứng hỗ trợ Master RX với 16 bộ mô tả DMA"),
        ("Khối kết nối mạng", "Wi-Fi 802.11 b/g/n (2.4 GHz) hỗ trợ đồng thời chế độ SoftAP và Station")
    ]
    md.add_custom_table(doc, ["Thông số phần cứng", "Đặc tính kỹ thuật chi tiết"], table_esp_data, [2.2, 4.1],
        title="Bảng 3.1. Thông số phần cứng chi tiết của khối xử lý ESP32-S3 N16R8")

    # 3.3 Kết nối INMP441
    md.add_heading_2(doc, "3.3. Thiết kế ghép nối cảm biến âm thanh I2S INMP441")
    md.add_p(doc, 
        "Cảm biến âm thanh đầu vào là module microphone MEMS INMP441 của TDK InvenSense. "
        "Đây là microphone đa hướng (omnidirectional), lỗ thu âm đáy (bottom-ported), tích hợp sẵn bộ lọc tiền khuếch đại và bộ biến đổi ADC 24-bit "
        "với tỷ số tín hiệu trên nhiễu cao (SNR = 61 dBA) và độ nhạy phẳng trên toàn dải tần âm thanh 60 Hz - 15 kHz [4].", indent=0.4)

    md.add_p(doc, 
        "Khác với các sơ đồ chân ngẫu nhiên hoặc thay đổi trong các hướng dẫn Arduino cũ, dự án đã khóa chặt sơ đồ chân kết nối phần cứng chuẩn "
        "trên bo mạch ESP32-S3 nhằm đảm bảo tính ổn định của bus I2S tần số cao:", indent=0.4)

    table_gpio_data = [
        ("SCK / BCLK", "GPIO 4", "I2S Bit Clock (Xung nhịp bit nối tiếp: 1.024 MHz)"),
        ("WS / LRCLK", "GPIO 5", "I2S Word Select (Xung chọn kênh / Khung mẫu: 16.000 Hz)"),
        ("SD / DOUT", "GPIO 6", "I2S Serial Data In (Dữ liệu âm thanh PCM 24-bit truyền vào vi điều khiển)"),
        ("VDD", "3.3V", "Nguồn điện áp cấp cho microphone (Cấp nguồn từ chân 3.3V ổn áp của ESP32-S3)"),
        ("GND", "GND", "Nối đất chung (Common Ground tín hiệu)"),
        ("L/R", "GND", "Cấu hình kênh âm thanh: Kéo xuống GND để microphone phát dữ liệu trên Kênh Trái (Left Channel)")
    ]
    md.add_custom_table(doc, ["Chân INMP441", "Chân ESP32-S3", "Chức năng và Vai trò tín hiệu kỹ thuật"], table_gpio_data, [1.5, 1.4, 3.4],
        title="Bảng 3.2. Sơ đồ kết nối dây phần cứng giữa ESP32-S3 và Microphone MEMS INMP441")

    md.add_p(doc, 
        "Giải thích chi tiết vai trò của cấu hình chân L/R: Chuẩn I2S Philips truyền thông theo khung stereo gồm hai khe thời gian (slot) liên tiếp: "
        "Khe Trái (Left Slot) khi WS = 0 và Khe Phải (Right Slot) khi WS = 1. Khi chân L/R của INMP441 được nối xuống GND, vi mạch sẽ kích hoạt bộ đệm đầu ra "
        "và truyền 24 bit âm thanh trong Khe Trái, đồng thời chuyển chân SD sang trạng thái trở kháng cao (High-Z) trong Khe Phải. "
        "Nhờ đó, vi điều khiển thu nhận dữ liệu sạch trên Kênh Trái mà không bị xung đột bus [4].", indent=0.4)

    # 3.4 Kiến trúc Firmware FreeRTOS
    md.add_heading_2(doc, "3.4. Kiến trúc Firmware đa nhiệm thời gian thực trên FreeRTOS")
    md.add_p(doc, 
        "Hệ thống firmware được xây dựng trên nền tảng FreeRTOS nguyên bản trong ESP-IDF, phân chia kiến trúc thành các tác vụ (tasks) độc lập "
        "hoạt động song song nhằm giải quyết triệt để vấn đề xung đột tài nguyên giữa tính toán DSP nặng và phục vụ Web Server [3]:", indent=0.4)
    md.add_p(doc, 
        "1. Tác vụ Xử lý DSP thời gian thực (Audio Processing Task): Được gán mức ưu tiên cao (Priority 5), chạy trên Core 1 của ESP32-S3. "
        "Tác vụ này thực hiện vòng lặp vô tận: đọc mẫu từ DMA I2S, nạp vào bộ đệm trượt, thực thi FFT, tìm đỉnh, tính f0 và nốt nhạc. "
        "Sau khi có kết quả mới, tác vụ cập nhật vào một biến cấu trúc dùng chung (s_latest_pitch) thông qua vùng bảo vệ FreeRTOS Critical Section (portENTER_CRITICAL).", indent=0.4)
    md.add_p(doc, 
        "2. Tác vụ Máy chủ Web (HTTP Server Task): Được quản lý tự động bởi thành phần `esp_http_server`, chạy trên Core 0 (cùng lõi với Wi-Fi stack). "
        "Khi trình duyệt của người dùng gửi yêu cầu HTTP GET /api/data, tác vụ web chỉ việc đọc nhanh bản sao snapshot mới nhất từ cấu trúc s_latest_pitch "
        "trong thời gian vài micro-giây rồi đóng gói JSON gửi đi. Cơ chế này đảm bảo tuyệt đối không có việc luồng Web Server làm gián đoạn hoặc gây trễ "
        "chu kỳ thu thập mẫu I2S của luồng DSP.", indent=0.4)

    # 3.5 Thiết kế DSP Pipeline (Overlapping Rolling Buffer)
    md.add_heading_2(doc, "3.5. Thiết kế Pipeline DSP với cơ chế đệm trượt 50% gối đầu")
    md.add_p(doc, 
        "Trong các phiên bản thử nghiệm ban đầu, hệ thống thu thập tuần tự từng khối tĩnh 4096 mẫu rồi mới bắt đầu tính toán, sau đó chèn hàm chờ trễ "
        "(vTaskDelay). Cách tiếp cận này dẫn đến hiện tượng trễ nghiêm trọng và bỏ lỡ hoàn toàn các nốt nhạc gõ ngắn (staccato) nếu phím đàn được gõ "
        "ở thời điểm vi điều khiển đang bận tính toán hoặc vừa kết thúc chu kỳ [2].", indent=0.4)

    md.add_p(doc, 
        "Để khắc phục hoàn toàn hiện tượng trên, hệ thống đã triển khai Kiến trúc Đệm trượt liên tục gối đầu 50% (Continuous Overlapping Rolling Buffer Pipeline):", indent=0.4)
    md.add_p(doc, 
        "• Kích thước khung phân tích FFT cố định: N = 4096 mẫu (tương ứng 256.0 ms tại Fs = 16 kHz).", indent=0.4)
    md.add_p(doc, 
        "• Độ dài bước nhảy (Hop Size): H = 2048 mẫu (tương ứng 128.0 ms, tỷ lệ chồng lấp Overlap = 50%).", indent=0.4)
    md.add_p(doc, 
        "• Nguyên lý dịch chuyển mẫu: Mỗi khi DMA thu nhận đủ 2048 mẫu âm thanh mới (Hop Buffer): "
        "(1) 2048 mẫu cũ ở nửa sau của Rolling Buffer được dịch chuyển lên nửa đầu: rolling[0..2047] = rolling[2048..4095]; "
        "(2) 2048 mẫu mới vừa thu được sao chép vào nửa sau: rolling[2048..4095] = hop[0..2047]; "
        "(3) Toàn bộ khung 4096 mẫu hoàn chỉnh ngay lập tức được chuyển sang khối xử lý DSP.", indent=0.4)

    table_dsp_baseline = [
        ("Tần số lấy mẫu (Fs)", "16.000 Hz", "Quyết định bởi xung nhịp I2S Master"),
        ("Độ dài khung phân tích (N)", "4.096 mẫu", "256.0 ms thời lượng quan sát trong miền thời gian"),
        ("Bước nhảy đệm trượt (Hop Size)", "2.048 mẫu", "128.0 ms chu kỳ thực thi thuật toán DSP (Overlap 50%)"),
        ("Độ phân giải bin phổ (df)", "3.90625 Hz/bin", "df = Fs / N = 16000 / 4096"),
        ("Tần số giới hạn Nyquist", "8.000 Hz", "Bao phủ hoàn toàn 88 phím piano (A0: 27.5Hz -> C8: 4186Hz)"),
        ("Hàm cửa sổ làm mịn", "Hann Window", "Búp phụ -31.5 dB, triệt tiêu rò rỉ phổ biên khung"),
        ("Ngưỡng năng lượng tối thiểu (RMS)", "0.0020 (chuẩn hóa)", "Loại bỏ tiếng ồn phòng tĩnh, bắt nhạy onset nốt")
    ]
    md.add_custom_table(doc, ["Tham số DSP Baseline", "Giá trị thiết kế", "Ý nghĩa và Cơ sở kỹ thuật"], table_dsp_baseline, [2.1, 1.5, 2.7],
        title="Bảng 3.3. Các tham số baseline của Pipeline Xử lý tín hiệu số (DSP Pipeline)")

    # 3.6 Harmonic-Aware Fundamental Detection
    md.add_heading_2(doc, "3.6. Thuật toán phân tích họa âm Harmonic-Aware Fundamental Detection")
    md.add_p(doc, 
        "Một sai lầm kinh điển trong các dự án tuner đơn giản là thuật toán 'chọn đỉnh FFT có biên độ lớn nhất toàn phổ'. "
        "Như đã phân tích tại mục 2.10, ở đàn piano cơ, nốt nhạc có chuỗi họa âm f0, 2f0, 3f0, 4f0,... Trong rất nhiều trường hợp (đặc biệt dải trầm), "
        "họa âm bậc 2 hoặc bậc 3 có biên độ lớn gấp 3-5 lần tần số cơ bản f0 [6]. Thuật toán chọn đỉnh lớn nhất sẽ ngay lập tức nhận diện sai nốt thành "
        "quãng tám trên. Để giải quyết triệt để vấn đề này, hệ thống triển khai Thuật toán phát hiện tần số cơ bản có nhận thức họa âm "
        "(Harmonic-Aware Fundamental Detection) với các bước logic chặt chẽ:", indent=0.4)

    md.add_p(doc, 
        "Bước 1: Trích xuất danh sách các đỉnh phổ cục bộ ứng viên (Candidate Peaks). "
        "Hệ thống quét dải tần số khả dĩ của đàn piano (từ Bin 7 ~ 27.34 Hz đến Bin 1072 ~ 4187.5 Hz), tìm tối đa 24 đỉnh cục bộ thỏa mãn "
        "điều kiện cực đại địa phương và có biên độ vượt ngưỡng sàn nhiễu.", indent=0.4)

    md.add_p(doc, 
        "Bước 2: Sinh các giả thuyết tần số cơ bản (Subharmonic Hypotheses Generation). "
        "Với mỗi đỉnh cục bộ f_peak mạnh tìm được, hệ thống không chỉ kiểm tra chính nó mà sinh ra một tập các giả thuyết tần số f_hyp "
        "bằng cách chia cho các ước số họa âm m in {1, 2, 3, 4, 5, 6}:", indent=0.4)
    md.add_equation(doc, "f_{\\text{hyp}} = \\frac{f_{\\text{peak}}}{m}, \\quad m = 1, 2, 3, 4, 5, 6", "3.1")

    md.add_p(doc, 
        "Bước 3: Khảo sát và tích lũy bằng chứng họa âm (Harmonic Evidence Collection). "
        "Với mỗi giả thuyết f_hyp, hệ thống dò tìm sự tồn tại của các đỉnh phổ thực tế tại các bội số lý thuyết k_m = round(m * f_hyp / df) "
        "trong cửa sổ hẹp +/- 2 bin. Một họa âm bậc m được công nhận hợp lệ (pass gate) nếu và chỉ nếu:", indent=0.4)
    md.add_equation(doc, "\\text{is\\_local\\_peak} == \\text{TRUE} \\quad \\text{và} \\quad \\text{Prominence}_m \\ge 2.2\\times \\quad \\text{và} \\quad \\text{mag}_m \\ge 1.0", "3.2")

    md.add_p(doc, 
        "Bước 4: Chấm điểm giả thuyết (Hypothesis Scoring Formula). "
        "Mỗi giả thuyết f_hyp được chấm điểm tổng hợp dựa trên năng lượng của các họa âm tìm thấy kết hợp hệ số thưởng cho số lượng họa âm h_count:", indent=0.4)
    md.add_equation(doc, "\\text{Score}_{\\text{raw}} = \\left( \\sum_{m \\in \\text{found}} \\frac{1}{\\sqrt{m}} \\ln(1 + \\text{Prominence}_m) \\sqrt{\\text{mag}_m} \\right) \\times \\left(1 + 0.40 \\times (h_{\\text{count}} - 1)\\right)", "3.3")

    md.add_p(doc, 
        "Bước 5: Áp dụng các luật trọng số âm học đặc thù (Acoustic Penalties & Bass-Gate Rules):", indent=0.4)
    md.add_p(doc, 
        "• Chống ảo ảnh quãng tám dưới (Subharmonic Phantom Check): Giả thuyết f_hyp bắt buộc phải có sự hiện diện của ít nhất một họa âm lẻ "
        "(m = 1, 3 hoặc 5). Nếu hoàn toàn không có họa âm lẻ nào xuất hiện (h_mask & 0x15 == 0), điểm số bị phạt nặng nhân với hệ số 0.05 "
        "(giảm 95% điểm) để triệt tiêu việc nhận nhầm một nốt thật thành một nốt trầm hơn một quãng tám.", indent=0.4)
    md.add_p(doc, 
        "• Cơ chế cứu nốt trầm khuyết fundamental (Missing m1 Rescue Policy): Ở nốt trầm piano, nếu fundamental (m=1) bị suy hao không đạt ngưỡng "
        "nhưng có mặt họa âm lẻ m=3 cùng với họa âm chẵn m=2 hoặc m=4, đây là bằng chứng âm học vững chắc cho thấy nốt trầm là có thật. "
        "Hệ thống chỉ áp dụng mức phạt nhẹ 0.85 (thay vì phạt 0.20), giúp bảo toàn điểm số cho các nốt trầm bị suy hao f0.", indent=0.4)
    md.add_p(doc, 
        "• Bộ bảo vệ dải hạ âm (Bass Guard Gate): "
        "(1) Với f_hyp < 55 Hz (k < 14): Yêu cầu bắt buộc phải có ít nhất 3 họa âm hợp lệ hoặc biên độ lớn nhất đạt tối thiểu 14.0 để ngăn chặn "
        "nhiễu điện lưới 50 Hz và tiếng búa gõ cơ học trầm 30-50 Hz; "
        "(2) Với 55 Hz <= f_hyp < 110 Hz (dải trầm C2 đến A2, bao gồm E2 ~ 82.4 Hz): Cho phép chấp nhận fundamental yếu khi có ít nhất 2 họa âm "
        "và có họa âm lẻ hỗ trợ (has_odd == TRUE).", indent=0.4)

    # 3.7 Note Detection & Temporal Stability
    md.add_heading_2(doc, "3.7. Bộ lọc ổn định thời gian và thuật toán nhận diện nốt nhạc")
    md.add_p(doc, 
        "Sau khi chọn được giả thuyết có điểm Score cao nhất, tần số f0 được tinh chỉnh bằng nội suy parabol bậc hai (QI). "
        "Để triệt tiêu các đột biến ngoại lai (outliers) do tiếng ồn ngẫu nhiên và đảm bảo kim đo hiển thị êm dịu, "
        "kết quả được đưa qua Bộ lọc ổn định thời gian (Temporal Stability Filter):", indent=0.4)
    md.add_p(doc, 
        "• Cấu trúc bộ nhớ: Lưu trữ lịch sử 5 ước lượng f0 gần nhất (PITCH_HISTORY_LEN = 5).", indent=0.4)
    md.add_p(doc, 
        "• Thuật toán khóa nốt nhanh (Fast Lock Mechanism): Khi phát hiện 2 khung liên tiếp có tần số lệch nhau dưới 3.5% (tương đương khoảng 50 cents), "
        "hệ thống xác nhận nốt đã đạt trạng thái ổn định (is_stable = TRUE) chỉ sau đúng 256 ms (2 khung gối đầu), "
        "và xuất ra giá trị Trung vị (Median) của các ước lượng lân cận. Cơ chế này giúp người chơi không cần phải giữ phím đàn 2-3 giây; "
        "ngay cả những nốt gõ ngắn staccato (300-400 ms) cũng được nhận diện chính xác và hiển thị tức thì.", indent=0.4)

    # 3.8 Embedded Web Server
    md.add_heading_2(doc, "3.8. Thiết kế máy chủ nhúng HTTP Server không khóa DSP")
    md.add_p(doc, 
        "Để loại bỏ hoàn toàn sự phụ thuộc vào màn hình OLED phần cứng và tạo ra trải nghiệm người dùng hiện đại, hệ thống triển khai máy chủ web nhúng "
        "sử dụng thành phần `esp_http_server` trên cổng mạng tiêu chuẩn 80 [3]. Máy chủ cung cấp 2 Endpoint duy nhất:", indent=0.4)
    md.add_p(doc, 
        "1. GET /: Phục vụ tệp giao diện người dùng `index.html`. Toàn bộ mã nguồn HTML, CSS và JavaScript được đóng gói trực tiếp vào phân vùng flash "
        "thông qua cơ chế EMBED_FILES của CMake. Khi người dùng truy cập, máy chủ truyền trực tiếp tệp từ bộ nhớ flash (zero-copy memory mapped) "
        "mà không tiêu tốn RAM động.", indent=0.4)
    md.add_p(doc, 
        "2. GET /api/data: Endpoint giao tiếp dữ liệu dạng JSON. Trình duyệt client gửi yêu cầu định kỳ để lấy thông tin trạng thái cao độ thời gian thực. "
        "Dữ liệu được trích xuất từ bản sao snapshot nội tại bảo vệ bởi Spinlock (s_pitch_mux), thời gian đáp ứng cực nhanh (< 2 ms).", indent=0.4)

    table_api_spec = [
        ("frequency", "float", "Tần số cơ bản ước lượng đo được thời gian thực (Hz, ví dụ: 440.237)"),
        ("note", "string", "Tên nốt nhạc danh định kèm chỉ số quãng tám (ví dụ: 'A4', 'C4', 'E2')"),
        ("target", "float", "Tần số mục tiêu chuẩn lý thuyết của nốt nhạc theo hệ âm bằng (Hz, ví dụ: 440.000)"),
        ("cents", "float", "Độ sai lệch cao độ đo được tính theo đơn vị cent (ví dụ: +0.93 cent)"),
        ("confidence", "float", "Mức độ tin cậy của thuật toán nhận diện tính theo phần trăm (0.0% đến 100.0%)"),
        ("estimator", "string", "Chế độ ước lượng được chọn ('F1_PRIMARY', 'F2_FALLBACK', 'F3_FALLBACK', 'NO_SIGNAL')"),
        ("valid", "boolean", "Cờ trạng thái nhị phân: true nếu có tín hiệu nốt nhạc hợp lệ, false nếu là nhiễu/im lặng"),
        ("frame", "unsigned long", "Chỉ số khung phân tích đếm tăng dần liên tục kể từ khi khởi động vi điều khiển"),
        ("latency_ms", "float", "Thời gian thực thi tính toán DSP thuần túy đo được trên phần cứng (mili-giây)")
    ]
    md.add_custom_table(doc, ["Tên trường JSON", "Kiểu dữ liệu", "Mô tả ý nghĩa và Giá trị thực nghiệm mẫu"], table_api_spec, [1.5, 1.2, 3.6],
        title="Bảng 3.4. Định nghĩa chi tiết các trường dữ liệu của JSON API Endpoint /api/data")

    # 3.9 Web Frontend (Celestial Tuner)
    md.add_heading_2(doc, "3.9. Thiết kế giao diện người dùng Web Frontend (Celestial Tuner)")
    md.add_p(doc, 
        "Giao diện người dùng Web Frontend được thiết kế theo phong cách Celestial / Fantasy Piano Tuner độc đáo và hiện đại, "
        "mang lại cảm giác trực quan, thẩm mỹ cao và sống động cho người chơi nhạc. Toàn bộ giao diện được xây dựng bằng công nghệ web tiêu chuẩn "
        "(HTML5, CSS3 hiện đại, Vanilla JavaScript) hoàn toàn độc lập, không sử dụng bất kỳ thư viện framework cồng kềnh nào (như React, Vue, Vite, GSAP) "
        "và tuyệt đối không liên kết đến các máy chủ CDN bên ngoài, cho phép thiết bị vận hành hoàn hảo ngay cả khi ngắt kết nối Internet toàn cầu.", indent=0.4)

    md.add_p(doc, 
        "Các đặc điểm thiết kế nổi bật của giao diện bao gồm:", indent=0.4)
    md.add_p(doc, 
        "• Hiệu ứng thị giác Celestial: Nền trời đêm huyền ảo (celestial dark theme) tích hợp các hạt sao lấp lánh (star particles) chuyển động ngẫu nhiên "
        "bằng CSS animations nhẹ, kết hợp các thẻ thông tin phong cách kính mờ (glassmorphism) và đường viền ánh kim vàng (gold borders).", indent=0.4)
    md.add_p(doc, 
        "• Đồng hồ đo sai lệch cao độ (Tuner Gauge): Kim chỉ thị (tuner needle) chuyển động mượt mà theo thang đo từ -50 cent đến +50 cent, "
        "kết hợp vòng hào quang tin cậy (confidence halo) và hiệu ứng phát nổ hạt ánh sáng (burst effect) khi nốt nhạc thay đổi.", indent=0.4)
    md.add_p(doc, 
        "• Hệ thống 4 trạng thái chỉ báo trực quan rõ ràng:", indent=0.4)
    md.add_p(doc, 
        "  - KHÔNG CÓ TÍN HIỆU (NO SIGNAL): Kim đo trở về vị trí trung hòa, thông số ẩn mờ, báo hiệu sẵn sàng nhận âm thanh.", indent=0.4)
    md.add_p(doc, 
        "  - ĐÚNG CAO ĐỘ (IN TUNE): Kích hoạt khi |cents| <= 3 đến 5 cent, viền kim đổi sang màu xanh lục ngọc rực rỡ, vòng hào quang sáng rõ.", indent=0.4)
    md.add_p(doc, 
        "  - QUÁ THẤP (TOO LOW / FLAT): Kích hoạt khi cents < -5 cent, hiển thị sắc thái lam tím lạnh, kim lệch về bên trái.", indent=0.4)
    md.add_p(doc, 
        "  - QUÁ CAO (TOO HIGH / SHARP): Kích hoạt khi cents > +5 cent, hiển thị sắc thái đỏ cam ấm, kim lệch về bên phải.", indent=0.4)
    md.add_p(doc, 
        "• Bàn phím piano ảo tương tác (Virtual Keyboard C2-C8): Mô phỏng đầy đủ các phím trắng và phím đen từ quãng 2 đến quãng 8. "
        "Khi hệ thống nhận diện được nốt nhạc đang chơi, phím piano tương ứng trên màn hình sẽ tự động phát sáng và nổi bật.", indent=0.4)
    md.add_p(doc, 
        "• Thiết kế co giãn đáp ứng hoàn hảo (Responsive Layout): Tự động tương thích và hiển thị tối ưu trên mọi kích thước màn hình "
        "từ máy tính để bàn (1920x1080), máy tính bảng đến điện thoại thông minh dạng đứng và nằm ngang.", indent=0.4)

    md.add_callout(doc, "NGUYÊN TẮC MINH BẠCH VỀ DỮ LIỆU ĐỒ THỊ TRÊN FRONTEND", 
        "Cần nhấn mạnh một nguyên tắc thiết kế quan trọng trong phiên bản này: Do API Endpoint /api/data của vi điều khiển chỉ truyền tải "
        "các thông số tóm tắt của nốt nhạc (frequency, note, target, cents, confidence, latency) để tối ưu băng thông mạng, "
        "giao diện Web Frontend TUYỆT ĐỐI KHÔNG TỰ Ý SINH RA DỮ LIỆU SÓNG ÂM (WAVEFORM) HOẶC PHỔ FFT GIẢ LẬP để trang trí. "
        "Mọi hiệu ứng hiển thị trên giao diện đều phản ánh chân thực dữ liệu đo đạc thực tế từ firmware.", alert_type="note")

    # =========================================================================
    # CHƯƠNG 4 — TRIỂN KHAI THỰC HIỆN
    # =========================================================================
    md.add_heading_1(doc, "CHƯƠNG 4 — TRIỂN KHAI THỰC HIỆN HỆ THỐNG")

    # 4.1 Môi trường ESP-IDF
    md.add_heading_2(doc, "4.1. Môi trường phát triển và cấu hình ESP-IDF")
    md.add_p(doc, 
        "Hệ thống được phát triển hoàn toàn trên bộ công cụ chính thức ESP-IDF v6.0.2 của Espressif. "
        "Dự án từ chối sử dụng môi trường Arduino IDE hoặc các thư viện ArduinoFFT do tính đóng kín và hiệu năng kém trong quản lý bộ đệm DMA. "
        "Hệ thống quản lý biên dịch thông qua CMake (`CMakeLists.txt`) với cấu hình tối ưu hóa trình biên dịch `-O2` và bật hỗ trợ dấu phẩy động phần cứng.", indent=0.4)

    # 4.2 Tầng I2S DMA
    md.add_heading_2(doc, "4.2. Triển khai tầng thu nhận dữ liệu âm thanh I2S và cấu hình DMA")
    md.add_p(doc, 
        "Tầng thu nhận I2S được khởi tạo thông qua thư viện chuẩn mới `driver/i2s_std.h`. "
        "Bộ điều khiển được cấu hình hoạt động ở chế độ Master RX với 16 bộ mô tả DMA (dma_desc_num = 16) và độ dài mỗi khung DMA là 256 mẫu (dma_frame_num = 256):", indent=0.4)

    # Code snippet in C
    p_c1 = doc.add_paragraph()
    p_c1.paragraph_format.space_before = Pt(4)
    p_c1.paragraph_format.space_after = Pt(6)
    code_i2s = (
        "// Cấu hình I2S Master RX 16 kHz, 32-bit slot stereo\n"
        "i2s_chan_config_t chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_AUTO, I2S_ROLE_MASTER);\n"
        "chan_cfg.dma_desc_num = 16;\n"
        "chan_cfg.dma_frame_num = 256;\n"
        "i2s_new_channel(&chan_cfg, NULL, &rx_handle);\n\n"
        "i2s_std_config_t std_cfg = {\n"
        "    .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(SAMPLE_RATE_HZ), // 16000 Hz\n"
        "    .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_STEREO),\n"
        "    .gpio_cfg = {\n"
        "        .bclk = GPIO_NUM_4, .ws = GPIO_NUM_5, .din = GPIO_NUM_6,\n"
        "        .dout = I2S_GPIO_UNUSED, .mclk = I2S_GPIO_UNUSED\n"
        "    },\n"
        "};\n"
        "i2s_channel_init_std_mode(rx_handle, &std_cfg);\n"
        "i2s_channel_enable(rx_handle);"
    )
    r_code = p_c1.add_run(code_i2s)
    r_code.font.name = "Consolas"
    r_code.font.size = Pt(9.5)
    r_code.font.color.rgb = md.C_BLUE

    md.add_p(doc, 
        "Hàm đọc mẫu `read_active_audio_samples()` thu nhận 2048 cặp mẫu 32-bit từ DMA. Do INMP441 truyền dữ liệu 24-bit căn lề trái trong khung 32-bit, "
        "dữ liệu được dịch phải 8 bit (`sample >> 8`) để đưa về giá trị số nguyên có dấu 24-bit chuẩn xác, đồng thời tự động kiểm tra kênh tích cực.", indent=0.4)

    # 4.3 Đệm Hop và Rolling
    md.add_heading_2(doc, "4.3. Quản lý bộ đệm Hop Buffer và Rolling Buffer")
    md.add_p(doc, 
        "Bộ đệm làm việc được cấp phát tĩnh hoàn toàn trong bộ nhớ nội tại DRAM của vi điều khiển:", indent=0.4)
    md.add_p(doc, 
        "• `s_hop_samples`: Chứa 2048 mẫu mono mới thu nhận (kích thước 8 KB).", indent=0.4)
    md.add_p(doc, 
        "• `s_rolling_samples`: Chứa 4096 mẫu mono cửa sổ phân tích trượt (kích thước 16 KB).", indent=0.4)
    md.add_p(doc, 
        "• `s_fft_real` và `s_fft_imag`: Chứa 4096 số thực dấu phẩy động phục vụ FFT (kích thước 16 KB x 2 = 32 KB).", indent=0.4)
    md.add_p(doc, 
        "Khi có dữ liệu mới, hàm `memmove` và `memcpy` thực hiện dịch chuyển và nạp mẫu với độ trễ dưới 5 micro-giây.", indent=0.4)

    # 4.4 Khử DC
    md.add_heading_2(doc, "4.4. Thuật toán khử thành phần một chiều (DC Removal)")
    md.add_p(doc, 
        "Tín hiệu thu từ microphone INMP441 luôn tồn tại một điện áp lệch một chiều nhỏ (DC offset) do dung sai chế tạo bộ ADC tích hợp. "
        "Nếu không khử mức DC này, thành phần tần số 0 Hz tại Bin 0 sẽ có biên độ khổng lồ và tràn sang làm ô nhiễm các bin dải siêu trầm (A0-C1). "
        "Thuật toán tính giá trị trung bình cộng của khung 4096 mẫu và trừ trực tiếp khỏi từng mẫu tín hiệu:", indent=0.4)
    md.add_equation(doc, "\\mu = \\frac{1}{N} \\sum_{n=0}^{N-1} x_{\\text{raw}}[n], \\quad x[n] = x_{\\text{raw}}[n] - \\mu", "4.1")

    # 4.5 Cửa sổ Hann và FFT Radix-2
    md.add_heading_2(doc, "4.5. Triển khai FFT Radix-2 và cửa sổ hóa Hann")
    md.add_p(doc, 
        "Mảng cửa sổ Hann 4096 phần tử được tính toán trước một lần duy nhất lúc khởi động hệ thống (`init_hann_window()`), lưu trong biến mảng tĩnh "
        "`s_hann_window[4096]`. Khi xử lý, từng mẫu x[n] sau khi khử DC được nhân với `s_hann_window[n]` và gán vào phần thực `s_fft_real[n]`, "
        "phần ảo `s_fft_imag[n]` được gán bằng 0.0f.", indent=0.4)

    md.add_p(doc, 
        "Hàm `fft_radix2()` thực thi đảo bit địa chỉ (bit-reversal permutation) và lặp qua log2(4096) = 12 tầng tính toán bướm. "
        "Phổ biên độ được tính toán cho 2048 bin dương đầu tiên (từ 0 Hz đến 8000 Hz) theo công thức căn bậc hai tổng bình phương.", indent=0.4)

    # 4.6 Sàn nhiễu trung vị
    md.add_heading_2(doc, "4.6. Trích xuất đỉnh phổ và tính sàn nhiễu trung vị")
    md.add_p(doc, 
        "Hàm `calculate_local_noise_floor()` thu thập 24 bin lân cận xung quanh bin k đang xét (12 bin bên trái và 12 bin bên phải, "
        "bỏ qua 4 bin thuộc búp sóng chính k-2 đến k+2). Dãy 24 giá trị được sắp xếp bằng thuật toán sắp xếp chèn (Insertion Sort) "
        "và trích xuất giá trị trung vị tại vị trí thứ 12 làm mức sàn nhiễu nền cục bộ. Cách tiếp cận này hoàn toàn miễn nhiễm với các đỉnh họa âm lân cận.", indent=0.4)

    # 4.7 Chấm điểm giả thuyết & Bass-Gate
    md.add_heading_2(doc, "4.7. Cài đặt thuật toán chấm điểm giả thuyết họa âm và Bass-Gate")
    md.add_p(doc, 
        "Hàm `evaluate_harmonic_hypothesis()` nhận vào một tần số giả thuyết hyp_f và quét tìm tối đa 6 họa âm. "
        "Cơ chế lọc được cài đặt chi tiết bằng ngôn ngữ C như sau:", indent=0.4)

    p_c2 = doc.add_paragraph()
    p_c2.paragraph_format.space_before = Pt(4)
    p_c2.paragraph_format.space_after = Pt(6)
    code_eval = (
        "// Chống ảo ảnh quãng tám dưới: Bắt buộc có họa âm lẻ\n"
        "bool has_odd = (h_mask & 0x15) != 0; // bit 0 (m=1), bit 2 (m=3), bit 4 (m=5)\n"
        "if (!has_odd) {\n"
        "    score *= 0.05f; // Phạt nặng nếu không có họa âm lẻ\n"
        "} else if ((h_mask & 0x01) == 0) {\n"
        "    // Nếu m=1 vắng mặt nhưng có m=3 và (m=2 hoặc m=4): Cứu nốt trầm piano\n"
        "    if ((h_mask & 0x04) != 0 && ((h_mask & 0x02) != 0 || (h_mask & 0x08) != 0)) {\n"
        "        score *= 0.85f; // Bằng chứng họa âm vững chắc cho nốt trầm\n"
        "    } else {\n"
        "        score *= 0.20f;\n"
        "    }\n"
        "}\n\n"
        "// Bộ lọc dải hạ âm (Bass Guard Gate)\n"
        "if (hyp_k < 14.0f) { // f < 55 Hz: Chặn nhiễu điện lưới 50Hz\n"
        "    if (h_count < 3 || max_found_mag < 14.0f) score *= 0.10f;\n"
        "} else if (hyp_k < 28.0f) { // 55 Hz <= f < 110 Hz (Dải trầm bao gồm E2 ~ 82.4 Hz)\n"
        "    bool has_bass_harmonics = (h_count >= 2 && has_odd && (max_found_mag >= 2.5f || total_energy >= 3.0f));\n"
        "    if (!has_bass_harmonics) score *= 0.10f;\n"
        "}"
    )
    r_code2 = p_c2.add_run(code_eval)
    r_code2.font.name = "Consolas"
    r_code2.font.size = Pt(9.5)
    r_code2.font.color.rgb = md.C_BLUE

    # 4.8 Cài đặt QI
    md.add_heading_2(doc, "4.8. Cài đặt nội suy parabol bậc hai (QI)")
    md.add_p(doc, 
        "Hàm nội suy bậc hai lấy 3 điểm biên độ `alpha = mag[k-1]`, `beta = mag[k]`, `gamma = mag[k+1]`. "
        "Mẫu số được bảo vệ chống chia cho 0 (`fabsf(denom) > 1e-6f`). Độ dịch p được giới hạn chặt chẽ trong khoảng [-0.5f, 0.5f] "
        "để loại trừ mọi trường hợp số học kỳ dị.", indent=0.4)

    # 4.9 Note Mapping & Cents
    md.add_heading_2(doc, "4.9. Triển khai ánh xạ nốt MIDI và độ lệch cents")
    md.add_p(doc, 
        "Ánh xạ nốt và tính độ lệch cent được thực thi theo các hàm toán học dấu phẩy động tối ưu của chuẩn C99 (`log2f`, `roundf`, `powf`):", indent=0.4)

    p_c3 = doc.add_paragraph()
    p_c3.paragraph_format.space_before = Pt(4)
    p_c3.paragraph_format.space_after = Pt(6)
    code_note = (
        "// 1. Tính số nốt MIDI gần nhất\n"
        "int midi = (int)roundf(69.0f + 12.0f * log2f(note_f0 / 440.0f));\n"
        "// 2. Tính tần số danh định mục tiêu\n"
        "float target_freq = 440.0f * powf(2.0f, (float)(midi - 69) / 12.0f);\n"
        "// 3. Tính độ sai lệch cents\n"
        "float cents = 1200.0f * log2f(note_f0 / target_freq);\n"
        "// 4. Xác định tên nốt và quãng tám\n"
        "static const char *k_note_names[12] = {\"C\", \"C#\", \"D\", \"D#\", \"E\", \"F\", \"F#\", \"G\", \"G#\", \"A\", \"A#\", \"B\"};\n"
        "int note_idx = (midi % 12 + 12) % 12;\n"
        "int octave = (midi / 12) - 1;\n"
        "snprintf(note_name_buf, sizeof(note_name_buf), \"%s%d\", k_note_names[note_idx], octave);"
    )
    r_code3 = p_c3.add_run(code_note)
    r_code3.font.name = "Consolas"
    r_code3.font.size = Pt(9.5)
    r_code3.font.color.rgb = md.C_BLUE

    # 4.10 Cài đặt API
    md.add_heading_2(doc, "4.10. Hiện thực hóa HTTP API Endpoint /api/data")
    md.add_p(doc, 
        "Hàm xử lý `api_data_get_handler()` sao chép dữ liệu từ biến toàn cục an toàn luồng và định dạng chuỗi JSON bằng `snprintf`: "
        "Đặt Header `Access-Control-Allow-Origin: *` để hỗ trợ cơ chế CORS và gửi phản hồi với kiểu nội dung `application/json`.", indent=0.4)

    # 4.11 Nhúng Frontend
    md.add_heading_2(doc, "4.11. Nhúng mã nguồn Web Frontend vào Firmware")
    md.add_p(doc, 
        "Tệp `main/index.html` chứa toàn bộ mã nguồn giao diện HTML, CSS và JavaScript được tích hợp vào binary thông qua lệnh CMake:", indent=0.4)
    md.add_p(doc, 
        "`target_add_binary_data(${COMPONENT_TARGET} \"index.html\" TEXT)`", indent=0.4)
    md.add_p(doc, 
        "Khi liên kết, trình biên dịch tự động tạo ra hai con trỏ biểu tượng nhị phân: `_binary_index_html_start` và `_binary_index_html_end`. "
        "Hàm xử lý `root_get_handler()` chỉ việc truyền con trỏ này qua hàm `httpd_resp_send()`, đạt hiệu suất phục vụ trang web tức thì.", indent=0.4)

    doc.add_page_break()

print("section_ch3_ch4 compiled successfully.")
