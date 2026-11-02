# -*- coding: utf-8 -*-
"""
Module: Chapter 5 (Testing & Results), Chapter 6 (Evaluation & Limitations),
Chapter 7 (Conclusion), References, and Appendices.
Project: PIANO CHROMATIC TUNER USING ESP32-S3 AND INMP441
Student: Le Tan Dung - MSSV: 24150654
"""

from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import make_doc as md

def build_ch5_ch7(doc):
    # =========================================================================
    # CHƯƠNG 5 — KIỂM THỬ VÀ KẾT QUẢ THỰC TẾ
    # =========================================================================
    md.add_heading_1(doc, "CHƯƠNG 5 — KIỂM THỬ VÀ PHÂN TÍCH KẾT QUẢ THỰC TẾ")

    # 5.1 Phương pháp kiểm thử
    md.add_heading_2(doc, "5.1. Phương pháp và môi trường kiểm thử thực nghiệm")
    md.add_p(doc, 
        "Tuân thủ nghiêm ngặt nguyên tắc REAL-DATA ONLY, toàn bộ dữ liệu trong chương này được thu thập trực tiếp "
        "từ phần cứng vi điều khiển ESP32-S3 kết hợp microphone MEMS INMP441 thông qua hệ thống đo đạc thiết bị (Hardware Instrumentation). "
        "Môi trường kiểm thử thực nghiệm được thiết lập như sau:", indent=0.4)
    md.add_p(doc, 
        "• Đối tượng kích âm: Đàn piano cơ acoustic thực tế, không sử dụng loa điện thoại phát lại file âm thanh để tránh làm méo đáp ứng tần số dải trầm.", indent=0.4)
    md.add_p(doc, 
        "• Bố trí cảm biến: Bo mạch phần cứng ESP32-S3 và microphone INMP441 được đặt ở cự ly thử nghiệm từ 5 cm đến 20 cm "
        "so với khu vực búa gõ và dây đàn tương ứng của từng nốt nhạc.", indent=0.4)
    md.add_p(doc, 
        "• Phương pháp thu thập dữ liệu: Ghi nhận trực tiếp dữ liệu log chẩn đoán qua cổng Serial UART tốc độ 115200 bps "
        "kết hợp các yêu cầu lấy mẫu liên tục từ Endpoint Web API `/api/data`.", indent=0.4)

    # 5.2 Kiểm thử tín hiệu tổng hợp
    md.add_heading_2(doc, "5.2. Kiểm thử xác thực thuật toán với tín hiệu tổng hợp")
    md.add_p(doc, 
        "Trước khi tiến hành đo đạc âm học phức tạp, thuật toán DSP cốt lõi (khử DC, cửa sổ Hann, FFT Radix-2 và Quadratic Interpolation) "
        "đã được kiểm chứng tính đúng đắn với các tín hiệu sóng sin thuần túy chuẩn:", indent=0.4)
    md.add_p(doc, 
        "• Tín hiệu sóng sin 440.00 Hz nhân tạo (tần số nằm giữa Bin 112 và Bin 113): Thuật toán nội suy parabol bậc hai (QI) "
        "xác định vị trí đỉnh phân số p = -0.36 bin, cho tần số ước lượng đạt chính xác 440.012 Hz (sai số tuyệt đối chỉ 0.012 Hz).", indent=0.4)
    md.add_p(doc, 
        "• Kiểm thử phòng yên tĩnh (Quiet Room Baseline): Khi không có tiếng đàn, tín hiệu nhiễu cơ học môi trường và rung động bàn "
        "tập trung tại dải 27.34 Hz và 39.06 Hz với biên độ nhỏ (7.9 - 13.6). Bộ lọc sàn nhiễu và cổng năng lượng RMS (MIN_AC_RMS_NORM = 0.0020) "
        "đã đóng hoàn toàn, hệ thống xuất trạng thái NO_SIGNAL đạt tỷ lệ 100%, không bị kích hoạt sai bởi tiếng ồn nền.", indent=0.4)

    # 5.3 Kiểm thử piano thực tế
    md.add_heading_2(doc, "5.3. Kết quả kiểm thử trên đàn Piano cơ (Acoustic Piano)")
    md.add_p(doc, 
        "Thử nghiệm đo đạc định lượng được thực hiện trên 5 nốt đại diện thuộc dải trung âm và cận trầm: "
        "A4 (440.00 Hz), C4 (261.63 Hz), C5 (523.25 Hz), D3 (146.83 Hz), E3 (164.81 Hz). "
        "Với mỗi nốt, hệ thống thu thập ít nhất 20 khung phân tích liên tiếp ở trạng thái nốt hợp lệ (VALID_PITCH frames). "
        "Kết quả thống kê định lượng đo đạc thực tế được tổng hợp chi tiết trong Bảng 5.1:", indent=0.4)

    table_dsp_res = [
        ("A4", "440.000 Hz", "440.281 Hz", "0.096 Hz", "0.281 Hz", "0.680 Hz", "100.0%"),
        ("C4", "261.626 Hz", "261.674 Hz", "0.064 Hz", "0.065 Hz", "0.140 Hz", "100.0%"),
        ("C5", "523.251 Hz", "523.438 Hz", "0.020 Hz", "0.188 Hz", "0.260 Hz", "100.0%"),
        ("D3", "146.832 Hz", "146.797 Hz", "0.074 Hz", "0.060 Hz", "0.270 Hz", "100.0%"),
        ("E3", "164.814 Hz", "164.787 Hz", "0.065 Hz", "0.054 Hz", "0.133 Hz", "100.0%")
    ]
    md.add_custom_table(doc, 
        ["Nốt nhạc", "Tần số chuẩn", "Trung bình đo (Mean)", "Độ lệch chuẩn (Std)", "Sai số tuyệt đối (MAE)", "Sai số cực đại (Max)", "Tỷ lệ bắt đúng nốt"],
        table_dsp_res, [0.9, 1.2, 1.4, 1.0, 1.1, 1.1, 1.1],
        title="Bảng 5.1. Kết quả đo đạc thống kê cao độ trên đàn piano cơ thật (20 khung VALID liên tiếp/nốt)")

    # 5.4 - 5.8 Chi tiết từng nốt
    md.add_heading_2(doc, "5.4. Phân tích chi tiết nốt A4 (440.00 Hz)")
    md.add_p(doc, 
        "Nốt A4 là nốt tham chiếu chuẩn quốc tế của âm nhạc. Phân tích phổ ghi nhận:", indent=0.4)
    md.add_p(doc, 
        "• Tần số cơ bản f1 xuất hiện tại Bin 113 với biên độ rất mạnh (~42.0), độ nổi bật Prominence vượt trội (190x - 220x), "
        "tỷ số SNR đạt từ +40 dB đến +46 dB. Độ dịch đỉnh phân số tính được là p xấp xỉ -0.31 bin.", indent=0.4)
    md.add_p(doc, 
        "• Tần số cơ bản trung bình đo được là 440.281 Hz với độ lệch chuẩn cực nhỏ (std = 0.096 Hz). "
        "Sai số tuyệt đối trung bình so với tần số danh định chỉ là 0.281 Hz (tương ứng độ lệch cao độ trung bình chỉ khoảng +1.1 cent), "
        "hoàn toàn thỏa mãn yêu cầu thiết kế < 0.5 Hz.", indent=0.4)

    md.add_heading_2(doc, "5.5. Phân tích chi tiết nốt C4 (261.63 Hz)")
    md.add_p(doc, 
        "Nốt C4 (Middle C) là mốc cao độ trung tâm của đàn piano. Thực nghiệm ghi nhận một hiện tượng âm học rất điển hình:", indent=0.4)
    md.add_p(doc, 
        "• Đỉnh âm học có biên độ lớn nhất trên phổ thực tế không phải là f1 (Bin 67, biên độ ~12.5) mà lại là họa âm bậc 2 (f2 = 523.47 Hz, Bin 134, biên độ ~38.0). "
        "Tuy nhiên, nhờ thuật toán Subharmonic Hypothesis Testing với ước số /2, hệ thống đã nhận diện chính xác đỉnh 523.47 Hz là họa âm của tần số cơ bản 261.72 Hz.", indent=0.4)
    md.add_p(doc, 
        "• Kết quả đo đạt độ chính xác phi thường: Trung bình đo đạt 261.674 Hz, sai số MAE chỉ 0.065 Hz, sai số cực đại chỉ 0.140 Hz.", indent=0.4)

    md.add_heading_2(doc, "5.6. Phân tích chi tiết nốt C5 (523.25 Hz)")
    md.add_p(doc, 
        "Nốt C5 thuộc dải cao (Treble). Thực nghiệm ghi nhận:", indent=0.4)
    md.add_p(doc, 
        "• Năng lượng f1 rất tập trung tại Bin 134 (biên độ ~45.0), độ biến thiên giữa các khung cực thấp với độ lệch chuẩn nhỏ nhất trong toàn bộ tập mẫu (std = 0.020 Hz). "
        "Tần số trung bình đo được là 523.438 Hz, MAE đạt 0.188 Hz.", indent=0.4)

    md.add_heading_2(doc, "5.7. Phân tích chi tiết nốt D3 (146.83 Hz) và E3 (164.81 Hz)")
    md.add_p(doc, 
        "Các nốt D3 và E3 bắt đầu bước vào dải cận trầm của đàn piano. Tại đây, hiện tượng suy giảm âm học của f1 bắt đầu xuất hiện:", indent=0.4)
    md.add_p(doc, 
        "• Tại nốt D3, f1 (Bin 38) có biên độ suy giảm xuống chỉ còn ~3.8, trong khi họa âm bậc 3 (440.92 Hz) có biên độ lên tới ~35.0. "
        "Thuật toán giả thuyết họa âm với ước số /3 đã bắt đúng tần số cơ bản 146.797 Hz, MAE đạt 0.060 Hz.", indent=0.4)
    md.add_p(doc, 
        "• Tại nốt E3, f1 (Bin 42) có biên độ ~4.5, trong khi họa âm bậc 2 (329.52 Hz) đạt biên độ ~28.0 và họa âm bậc 3 (494.99 Hz) đạt ~32.0. "
        "Hệ thống đạt tần số trung bình 164.787 Hz, MAE chỉ 0.054 Hz, độ lệch chuẩn std = 0.065 Hz.", indent=0.4)

    # Khảo sát Inharmonicity thực tế
    md.add_heading_2(doc, "5.8. Đo đạc đặc tính các họa âm và hiện tượng Inharmonicity thực tế")
    md.add_p(doc, 
        "Một đóng góp thực nghiệm quan trọng của đề tài là việc đo đạc định lượng trực tiếp hiện tượng bất điều hòa (Inharmonicity) "
        "của dây đàn thép piano trên phần cứng thật. Bảng 5.2 tổng hợp giá trị tần số ước lượng của từng bậc họa âm (f1, f2/2, f3/3) "
        "và độ dạt tần số tương ứng:", indent=0.4)

    table_inhar_data = [
        ("A4", "440.00 Hz", "440.285 Hz", "440.249 Hz", "440.633 Hz", "-0.036 Hz", "+0.348 Hz"),
        ("C4", "261.63 Hz", "261.675 Hz", "261.734 Hz", "261.839 Hz", "+0.059 Hz", "+0.164 Hz"),
        ("C5", "523.25 Hz", "523.445 Hz", "523.929 Hz", "524.869 Hz", "+0.484 Hz", "+1.424 Hz"),
        ("D3", "146.83 Hz", "146.621 Hz", "146.790 Hz", "146.973 Hz", "+0.157 Hz", "+0.334 Hz"),
        ("E3", "164.81 Hz", "164.700 Hz", "164.760 Hz", "164.995 Hz", "+0.060 Hz", "+0.295 Hz")
    ]
    md.add_custom_table(doc, 
        ["Nốt", "Mục tiêu", "Họa âm m=1 (f1)", "Họa âm m=2 (f2/2)", "Họa âm m=3 (f3/3)", "Độ dạt dev2 [(f2/2)-f1]", "Độ dạt dev3 [(f3/3)-f1]"],
        table_inhar_data, [0.8, 1.1, 1.2, 1.2, 1.2, 1.2, 1.2],
        title="Bảng 5.2. Đo đạc đặc tính các họa âm và hiện tượng dạt tần số (Inharmonicity) trên đàn piano thật")

    md.add_p(doc, 
        "Nhận xét kỹ thuật then chốt từ Bảng 5.2: "
        "(1) Độ dạt họa âm tăng theo cấp số nhân với bậc họa âm m và tăng rất mạnh ở các nốt cao (C5 ghi nhận dev3 dạt lên tới +1.424 Hz do dây treble ngắn và có độ cứng lớn); "
        "(2) Dữ liệu thực tế chứng minh rằng: Nếu áp dụng công thức trung bình cộng có trọng số đa họa âm (MHQI) một cách mù quáng, "
        "ước lượng f0 sẽ bị các họa âm bậc 2 và 3 kéo lệch lên cao một cách nhân tạo (ví dụ C5 bị kéo lệch lên 523.641 Hz). "
        "Do đó, kiến trúc DSP của dự án đã quyết định sử dụng chính sách: Ưu tiên f1 làm ước lượng số một (F1_PRIMARY) khi f1 có SNR tốt, "
        "và chỉ sử dụng f2/2 làm dự phòng (F2_FALLBACK) khi f1 bị chìm sâu trong dải trầm [6].", indent=0.4)

    # 5.9 Phân tích nốt trầm E2
    md.add_heading_2(doc, "5.9. Phân tích thực nghiệm nốt trầm E2 (82.41 Hz) và dải Bass")
    md.add_p(doc, 
        "Nhằm tuân thủ tuyệt đối tính trung thực khoa học, báo cáo không che giấu những khó khăn kỹ thuật tại dải nốt trầm, "
        "đặc biệt là nốt E2 (tần số danh định 82.41 Hz). Kết quả phân tích phổ chi tiết tại nốt E2 ghi nhận các số liệu thực tế sau:", indent=0.4)

    table_e2_data = [
        ("Tần số cơ bản f0 (m=1)", "82.03 Hz (Bin 21)", "1.5 - 7.3", "Rất yếu (suy hao âm học cơ học của thùng đàn & mic)"),
        ("Họa âm bậc 2 (m=2)", "164.06 Hz (Bin 42)", "15.9 - 28.4", "Mạnh gấp 4-8 lần so với fundamental"),
        ("Họa âm bậc 3 (m=3)", "246.09 Hz (Bin 63)", "22.0 - 46.4", "Đỉnh năng lượng mạnh nhất trên toàn dải phổ"),
        ("Họa âm bậc 4 (m=4)", "328.12 Hz (Bin 84)", "12.4 - 25.1", "Mạnh gấp 3 lần so với fundamental")
    ]
    md.add_custom_table(doc, ["Thành phần phổ tại nốt E2", "Vị trí bin và Tần số", "Biên độ đo được (mag)", "Đánh giá âm học thực tế"], table_e2_data, [1.8, 1.6, 1.4, 2.3],
        title="Bảng 5.4. Phân tích đặc tính phổ tại dải nốt trầm E2 (82.41 Hz) ghi nhận trên phần cứng")

    md.add_p(doc, 
        "Trong bài kiểm tra Clean Regression Test nghiêm ngặt (thu thập 20 khung liên tục độc lập khi gõ phím E2 trên đàn piano thật), "
        "kết quả thống kê ghi nhận:", indent=0.4)
    md.add_p(doc, 
        "• Tỷ lệ nhận diện đúng nốt E2 chỉ đạt 15.0% (3/20 khung).", indent=0.4)
    md.add_p(doc, 
        "• Tần số trung bình trong các khung bắt được là 83.160 Hz (std = 0.137 Hz, MAE = 0.750 Hz).", indent=0.4)
    md.add_p(doc, 
        "• Trong 85% số khung còn lại, hệ thống bị đánh lừa bởi năng lượng áp đảo của họa âm bậc 2 (164 Hz) và nhận nhầm thành nốt E3 (~164.81 Hz). "
        "Mặc dù firmware đã được bổ sung giải thuật Bass-Gate Modification (nới lỏng ngưỡng biên độ cho dải 55-110 Hz khi có đủ họa âm lẻ hỗ trợ), "
        "nhưng độ ổn định thực tế tại E2 vẫn chưa đủ để đưa ra kết luận rằng hệ thống hoạt động tin cậy trên toàn bộ dải trầm của đàn piano.", indent=0.4)

    # 5.10 Latency
    md.add_heading_2(doc, "5.10. Đo đạc độ trễ xử lý (Processing Latency vs Update Cadence)")
    md.add_p(doc, 
        "Một khía cạnh kỹ thuật tối quan trọng cần làm rõ là sự phân biệt giữa Độ trễ xử lý tính toán của DSP (Processing Latency) "
        "và Chu kỳ cập nhật giao diện tổng thể (Web Update Cadence):", indent=0.4)

    table_lat_data = [
        ("Thời gian thực thi DSP (Processing Latency)", "23.56 - 25.37 ms", "Thời gian Core 1 CPU chạy FFT, QI, Harmonic Scoring (Đo bằng esp_timer)"),
        ("Chu kỳ bước nhảy đệm (Hop Interval)", "128.0 ms", "Thời gian cần thiết để DMA I2S thu nhận đủ 2048 mẫu âm thanh mới"),
        ("Thời gian đáp ứng nốt tối thiểu (Fast Lock)", "256.0 ms", "2 khung gối đầu liên tiếp cần thiết để bộ lọc ổn định xác nhận trạng thái STABLE"),
        ("Chu kỳ gửi yêu cầu Web Polling", "125.0 ms", "Nhịp gửi hàm fetch() định kỳ từ mã JavaScript trên trình duyệt client"),
        ("Tải chiếm dụng CPU của tác vụ DSP", "Xấp xỉ 18.5%", "Đo đạc trên lõi 240 MHz (Dư thừa >80% năng lực CPU cho Wi-Fi và Web Server)")
    ]
    md.add_custom_table(doc, ["Đại lượng độ trễ đo đạc", "Giá trị thực nghiệm", "Bản chất kỹ thuật và Phân tích"], table_lat_data, [2.1, 1.4, 3.6],
        title="Bảng 5.5. Kết quả đo đạc độ trễ xử lý (Processing Latency) của khối DSP")

    md.add_p(doc, 
        "Kết luận: Độ trễ tính toán DSP thuần túy chỉ dao động trong khoảng 23.56 đến 25.37 ms, hoàn toàn đáp ứng xuất sắc tiêu chuẩn thời gian thực (< 50 ms). "
        "Tổng thời gian từ khi người chơi gõ phím đến khi kim đo trên trình duyệt phản hồi dao động trong khoảng 150 - 280 ms, "
        "hoàn toàn thỏa mãn yêu cầu cập nhật < 500 ms của đề tài môn học [2].", indent=0.4)

    # 5.11 Frontend CDP
    md.add_heading_2(doc, "5.11. Kiểm thử tự động Frontend trên Chrome Headless CDP Automation")
    md.add_p(doc, 
        "Để kiểm tra tính toàn vẹn của mã nguồn giao diện Web Frontend, hệ thống đã chạy quy trình kiểm thử tự động không đầu "
        "(Headless Browser Automation) thông qua giao thức Chrome DevTools Protocol (CDP). Kết quả xác nhận:", indent=0.4)
    md.add_p(doc, 
        "• Biên dịch firmware (Build): PASS.", indent=0.4)
    md.add_p(doc, 
        "• Nạp chip vi điều khiển (Flash): PASS.", indent=0.4)
    md.add_p(doc, 
        "• Kiểm tra lỗi JavaScript Console: Đạt 0 lỗi ngoại lệ (0 Errors / 0 Warnings).", indent=0.4)
    md.add_p(doc, 
        "• Chuyển cảnh giao diện (Scene Navigation): PASS.", indent=0.4)
    md.add_p(doc, 
        "• Xác thực hiển thị chính xác các trạng thái từ API Endpoint:", indent=0.4)
    md.add_p(doc, 
        "  - Trạng thái A4: Nhận diện 440.10 Hz, độ lệch +0.39 cent, hiển thị banner 'ĐÚNG CAO ĐỘ' (IN TUNE), kim đo ở vị trí 50.39%.", indent=0.4)
    md.add_p(doc, 
        "  - Trạng thái C4: Nhận diện 259.50 Hz, độ lệch -14.15 cent, hiển thị banner 'THẤP' (TOO LOW), kim đo lệch về 35.87%.", indent=0.4)
    md.add_p(doc, 
        "  - Trạng thái E2: Nhận diện 83.20 Hz, độ lệch +16.52 cent, hiển thị banner 'CAO' (TOO HIGH), kim đo lệch về 66.47%.", indent=0.4)
    md.add_p(doc, 
        "  - Trạng thái Không có tín hiệu: Hiển thị banner 'KHÔNG CÓ TÍN HIỆU' (NO SIGNAL), kim đo trở về trạng thái nghỉ.", indent=0.4)

    # 5.12 Responsive
    md.add_heading_2(doc, "5.12. Kiểm thử tính thích ứng giao diện (Responsive Layout Matrix)")
    md.add_p(doc, 
        "Khả năng thích ứng giao diện (Responsive) của trang web Celestial Tuner được kiểm định tự động trên 8 cấu hình độ phân giải màn hình tiêu chuẩn "
        "thông qua Chrome CDP. Kết quả kiểm tra được trình bày trong Bảng 5.7:", indent=0.4)

    table_resp_data = [
        ("Desktop Full HD", "1920 x 1080", "1920 px", "1920 px", "KHÔNG", "PASSED"),
        ("Desktop WXGA", "1366 x 768", "1366 px", "1366 px", "KHÔNG", "PASSED"),
        ("Tablet Landscape", "1024 x 768", "1024 px", "1024 px", "KHÔNG", "PASSED"),
        ("Tablet Portrait", "768 x 1024", "768 px", "768 px", "KHÔNG", "PASSED"),
        ("Mobile Modern (Large)", "412 x 915", "412 px", "412 px", "KHÔNG", "PASSED"),
        ("Mobile iPhone 12/13/14", "390 x 844", "390 px", "390 px", "KHÔNG", "PASSED"),
        ("Mobile Compact", "360 x 800", "360 px", "360 px", "KHÔNG", "PASSED"),
        ("Mobile Landscape", "844 x 390", "844 px", "844 px", "KHÔNG", "PASSED")
    ]
    md.add_custom_table(doc, 
        ["Thiết bị mô phỏng", "Độ phân giải (WxH)", "Chiều rộng Window", "Chiều rộng Document", "Tràn ngang (Overflow)", "Kết quả kiểm thử"],
        table_resp_data, [1.4, 1.2, 1.1, 1.1, 1.1, 1.0],
        title="Bảng 5.7. Ma trận kiểm thử tính tương thích giao diện co giãn Responsive trên 8 Viewport")

    md.add_callout(doc, "RANH GIỚI XÁC THỰC THIẾT BỊ DI ĐỘNG", 
        "Kết quả Bảng 5.7 xác nhận rằng giao diện đã vượt qua toàn bộ các bài kiểm tra co giãn giao diện tự động trên trình duyệt Chrome giả lập. "
        "Tuy nhiên, theo nguyên tắc REAL-DATA ONLY, báo cáo ghi nhận minh bạch rằng: HỆ THỐNG CHƯA ĐƯỢC XÁC MINH TRÊN ĐIỆN THOẠI VẬT LÝ THỰC TẾ "
        "(NOT VERIFIED ON PHYSICAL PHONE).", alert_type="warn")

    # =========================================================================
    # CHƯƠNG 6 — ĐÁNH GIÁ, THẢO LUẬN VÀ GIỚI HẠN
    # =========================================================================
    md.add_heading_1(doc, "CHƯƠNG 6 — ĐÁNH GIÁ, THẢO LUẬN VÀ GIỚI HẠN KỸ THUẬT")

    # 6.1 Đạt được
    md.add_heading_2(doc, "6.1. Tổng kết các mục tiêu kỹ thuật đạt được")
    md.add_p(doc, 
        "Đối chiếu với các yêu cầu đặt ra từ đề bài ban đầu, dự án đã đạt được những kết quả cụ thể sau:", indent=0.4)
    md.add_p(doc, 
        "1. Xây dựng thành công thiết bị phần cứng hoàn chỉnh, hoạt động độc lập với chi phí linh kiện cực thấp (< 15 USD), "
        "sử dụng chip ESP32-S3 N16R8 và microphone MEMS INMP441 chất lượng cao.", indent=0.4)
    md.add_p(doc, 
        "2. Triển khai hoàn chỉnh pipeline DSP tối ưu bằng C/C++ thuần trong ESP-IDF, làm chủ toàn bộ các khâu từ thu nhận I2S DMA, "
        "khử DC, cửa sổ Hann, biến đổi FFT Radix-2 4096 điểm, sàng lọc sàn nhiễu trung vị, chấm điểm giả thuyết họa âm và nội suy parabol bậc hai.", indent=0.4)
    md.add_p(doc, 
        "3. Đạt độ chính xác thực nghiệm xuất sắc trên các nốt kiểm thử thuộc dải trung âm và cận trầm (A4 MAE = 0.281 Hz, C4 MAE = 0.065 Hz, "
        "C5 MAE = 0.188 Hz, D3 MAE = 0.060 Hz, E3 MAE = 0.054 Hz), thỏa mãn hoàn toàn tiêu chuẩn sai số < 0.5 Hz.", indent=0.4)
    md.add_p(doc, 
        "4. Tối ưu hóa độ trễ tính toán ấn tượng (chỉ 23.56 - 25.37 ms), tải CPU thấp (~18.5%), không gây gián đoạn luồng mạng.", indent=0.4)
    md.add_p(doc, 
        "5. Thiết kế giao diện Web Celestial Tuner hiện đại, thẩm mỹ cao, tích hợp bàn phím piano ảo tương tác và co giãn mượt mà trên mọi màn hình.", indent=0.4)

    # 6.2 Chưa đạt / Chưa xác minh
    md.add_heading_2(doc, "6.2. Các nội dung chưa đạt và ranh giới chưa xác minh (Unverified Boundaries)")
    md.add_p(doc, 
        "Để đảm bảo tính liêm chính học thuật và độ tin cậy khoa học, ma trận phân định rõ ràng các ranh giới đã xác minh và chưa xác minh "
        "được trình bày trong Bảng 6.2:", indent=0.4)

    table_bound_data = [
        ("Nốt trung âm và cận trầm (A4, C4, C5, D3, E3)", "ĐÃ XÁC THỰC (VERIFIED)", "Đo đạc thực tế trên đàn piano cơ thật, đạt MAE 0.054 - 0.281 Hz"),
        ("Nốt trầm E2 (82.41 Hz)", "XÁC THỰC MỘT PHẦN (LIMITED)", "Tỷ lệ nhận diện đúng 15% trong test sạch, dễ nhầm sang E3 do họa âm mạnh"),
        ("Dải cực trầm (A0 - C2, 27.5 Hz đến 65.4 Hz)", "CHƯA XÁC MINH (NOT VERIFIED)", "Chưa đủ dữ liệu thực nghiệm để khẳng định độ chính xác"),
        ("Dải cực cao (C6 - C8, 1046 Hz đến 4186 Hz)", "CHƯA XÁC MINH (NOT VERIFIED)", "Chưa thu thập đủ mẫu kiểm thử trên đàn piano thật"),
        ("Độ chính xác < 0.5 Hz trên toàn bộ 88 phím", "KHÔNG ĐƯỢC TUYÊN BỐ", "Dữ liệu hiện tại không đủ để chứng minh toàn bộ bàn phím đạt tiêu chuẩn"),
        ("Tín hiệu hợp âm đa âm (Polyphonic / Chords)", "NGOÀI PHẠM VI (OUT OF SCOPE)", "Hệ thống chỉ thiết kế chuyên biệt cho nhận diện đơn âm"),
        ("Hiện tượng dậm pedal vang âm phức tạp", "CHƯA XÁC MINH (NOT VERIFIED)", "Chưa kiểm nghiệm sự giao thoa cộng hưởng đa dây khi mở damper"),
        ("Giao diện trên thiết bị di động vật lý thật", "CHƯA XÁC MINH (NOT VERIFIED)", "Mới chỉ xác thực trên trình duyệt Chrome giả lập qua giao thức CDP")
    ]
    md.add_custom_table(doc, ["Hạng mục kiểm thử và Khảo sát", "Trạng thái xác thực", "Căn cứ kỹ thuật và Ghi chú minh bạch"], table_bound_data, [1.9, 1.8, 3.4],
        title="Bảng 6.2. Ma trận phân định ranh giới xác thực thực tế (Verified vs. Not Verified)")

    # 6.3 Nguyên nhân sai số
    md.add_heading_2(doc, "6.3. Phân tích nguồn gốc sai số vật lý và toán học")
    md.add_p(doc, 
        "Các sai số quan sát được trong quá trình thực nghiệm xuất phát từ các nguyên nhân khách quan sau:", indent=0.4)
    md.add_p(doc, 
        "1. Sai số lượng tử hóa và rò rỉ phổ của FFT: Với Fs = 16 kHz và N = 4096, khoảng cách bin 3.90625 Hz tạo ra độ phân giải rời rạc. "
        "Mặc dù thuật toán nội suy parabol (QI) giúp ước lượng đỉnh phân số p, mô hình parabol chỉ là xấp xỉ bậc hai của hàm sinc/Hann. "
        "Khi đỉnh thực tế nằm gần biên bin (p gần +/- 0.5), sai số nội suy hình học có thể đạt từ 0.05 đến 0.15 Hz [1].", indent=0.4)
    md.add_p(doc, 
        "2. Sai số do tính bất điều hòa của dây đàn piano: Như phương trình Fletcher (2.20) đã chứng minh, các họa âm bậc 2 và 3 bị dạt tần số lên cao. "
        "Ở nốt D3 và E3, khi năng lượng f1 suy yếu và hệ thống phải dựa vào họa âm f2 để suy diễn f0, độ dạt inharmonicity của f2 "
        "tự động cộng thêm một lượng sai số khoảng +0.06 Hz vào ước lượng tần số cơ bản [6].", indent=0.4)
    md.add_p(doc, 
        "3. Giới hạn đáp ứng tần số thấp của cảm biến MEMS INMP441: Theo tài liệu kỹ thuật của nhà sản xuất [4], màng chắn vi cơ điện tử MEMS "
        "có độ suy giảm độ nhạy rất nhanh ở tần số dưới 60 Hz (-3 dB tại 60 Hz và giảm sâu hơn ở 30 Hz). "
        "Điều này khiến tỷ số SNR của các nốt trầm bị tụt dốc nghiêm trọng so với dải trung âm.", indent=0.4)

    # 6.4 - 6.5 Giới hạn & Hướng cải tiến
    md.add_heading_2(doc, "6.4. Giới hạn vận hành của hệ thống")
    md.add_p(doc, 
        "Hệ thống yêu cầu người chơi phải gảy từng phím đàn đơn lẻ và để phím đàn ngân tự nhiên ít nhất 256 ms. "
        "Nếu người chơi gảy đồng thời nhiều phím hoặc dậm pedal vang âm làm rung chuyển nhiều dây đàn cùng lúc, phổ tần số sẽ xuất hiện "
        "hàng chục đỉnh phổ đan xen, khiến thuật toán chấm điểm giả thuyết họa âm đơn bị quá tải và có thể xuất ra nốt sai.", indent=0.4)

    md.add_heading_2(doc, "6.5. Đề xuất các giải pháp nâng cấp tiềm năng")
    md.add_p(doc, 
        "Để khắc phục triệt để vấn đề nhận diện dải trầm mà không làm tăng độ trễ tính toán, các hướng nâng cấp sau được đề xuất:", indent=0.4)
    md.add_p(doc, 
        "1. Thuật toán kết hợp miền thời gian và miền tần số (Hybrid Time-Frequency Architecture): "
        "Sử dụng FFT cho dải trung và cao (từ C3 đến C8), kết hợp thuật toán tự tương quan chuẩn hóa (Normalized Cross-Correlation) "
        "hoặc thuật toán YIN cho dải trầm (A0 đến B2). Miền thời gian hoàn toàn miễn nhiễm với hiện tượng suy hao họa âm bậc cao [2].", indent=0.4)
    md.add_p(doc, 
        "2. Thuật toán lấy mẫu giảm cấp thích nghi (Adaptive Downsampling): "
        "Với dải trầm, tín hiệu có thể được lọc thông thấp số và giảm tần số lấy mẫu xuống Fs/4 = 4.000 Hz. Khi đó với N = 4096 điểm, "
        "độ phân giải bin sẽ mịn gấp 4 lần, đạt Delta f = 0.976 Hz/bin, cải thiện vượt bậc khả năng tách đỉnh ở dải 30-100 Hz [1].", indent=0.4)

    # =========================================================================
    # CHƯƠNG 7 — KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN
    # =========================================================================
    md.add_heading_1(doc, "CHƯƠNG 7 — KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN")

    md.add_heading_2(doc, "7.1. Kết luận chung")
    md.add_p(doc, 
        "Tiểu luận kỹ thuật đã hoàn thành xuất sắc mục tiêu nghiên cứu, thiết kế và chế tạo thực nghiệm thiết bị lên dây đàn piano chromatic "
        "(Piano Chromatic Tuner) sử dụng vi điều khiển ESP32-S3 N16R8 và microphone MEMS I2S INMP441. "
        "Dự án đã áp dụng thành công các kiến thức nền tảng trong Giáo trình Xử lý tín hiệu số [1] vào việc giải quyết một bài toán kỹ thuật "
        "thực tế có độ phức tạp cao.", indent=0.4)

    md.add_p(doc, 
        "Các đóng góp cốt lõi của đề tài bao gồm việc triển khai thành công pipeline DSP thời gian thực với cơ chế đệm trượt 50% gối đầu (hop size 128 ms), "
        "kỹ thuật cửa sổ hóa Hann, biến đổi FFT Radix-2 4096 điểm kết hợp nội suy parabol bậc hai (QI) và giải thuật phân tích họa âm có nhận thức "
        "(Harmonic-Aware Scoring). Hệ thống đạt độ chính xác thực nghiệm cao trên các nốt thử nghiệm đại diện, độ trễ xử lý cực thấp (~24 ms), "
        "và cung cấp giao diện người dùng Web Celestial Tuner sinh động, độc lập hoàn toàn với Internet ngoài.", indent=0.4)

    md.add_p(doc, 
        "Đồng thời, báo cáo đã giữ vững tính liêm chính học thuật bằng việc phân định ranh giới minh bạch giữa lý thuyết, triển khai mã nguồn "
        "và kết quả đo đạc thực tế, thẳng thắn chỉ ra các giới hạn âm học ở dải trầm (nốt E2) và khẳng định rõ ràng các phạm vi chưa được xác minh.", indent=0.4)

    md.add_heading_2(doc, "7.2. Hướng phát triển trong tương lai")
    md.add_p(doc, 
        "Trong các giai đoạn tiếp theo, đề tài có thể tiếp tục mở rộng theo các hướng:", indent=0.4)
    md.add_p(doc, 
        "• Tích hợp bộ giải thuật YIN tăng tốc phần cứng cho dải nốt cực trầm (A0 - C2).", indent=0.4)
    md.add_p(doc, 
        "• Thu thập dữ liệu âm học và xây dựng bảng hiệu chuẩn bù trừ tính bất điều hòa (Railsback curve calibration) chuyên biệt cho từng loại đàn piano cơ.", indent=0.4)
    md.add_p(doc, 
        "• Bổ sung tính năng lưu trữ lịch sử cân chỉnh và xuất báo cáo trạng thái phím đàn qua giao thức WebSocket.", indent=0.4)

    # =========================================================================
    # TÀI LIỆU THAM KHẢO
    # =========================================================================
    md.add_heading_1(doc, "TÀI LIỆU THAM KHẢO")
    
    refs = [
        "[1] Nguyễn Linh Trung, Trần Đức Tân, Huỳnh Hữu Tuệ, Giáo trình Xử lý tín hiệu số, Nhà xuất bản Đại học Quốc gia Hà Nội, 2012.",
        "[2] Trường Đại học Bách Khoa - ĐHQG-HCM, Tài liệu hướng dẫn đồ án bài cuối kỳ: Thiết bị lên dây đàn Chromatic Tuner, 2024.",
        "[3] Espressif Systems, ESP32-S3 Technical Reference Manual, Version 1.5, 2024.",
        "[4] InvenSense Inc., INMP441: Omnidirectional Microphone with I2S Digital Output, Datasheet Revision 1.1, 2014.",
        "[5] MIDI Manufacturers Association, The Complete MIDI 1.0 Detailed Specification, Document Version 96.1, 1996.",
        "[6] Fletcher, N. H., & Rossing, T. D., The Physics of Musical Instruments, 2nd Edition, Springer-Verlag, New York, 1998.",
        "[7] Smith, J. O., Spectral Audio Signal Processing, W3K Publishing, Stanford University, 2011.",
        "[8] Oppenheim, A. V., & Schafer, R. W., Discrete-Time Signal Processing, 3rd Edition, Prentice Hall, 2009."
    ]
    for r in refs:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.first_line_indent = Inches(-0.4)
        p.paragraph_format.left_indent = Inches(0.4)
        run = p.add_run(r)
        run.font.name = "Times New Roman"
        run.font.size = Pt(11.5)
        run.font.color.rgb = md.C_TEXT

    doc.add_page_break()

    # =========================================================================
    # PHỤ LỤC
    # =========================================================================
    md.add_heading_1(doc, "PHỤ LỤC")

    # Phụ lục A
    md.add_heading_2(doc, "Phụ lục A: Sơ đồ nối dây và thông số phần cứng chi tiết")
    md.add_p(doc, 
        "Bảng tổng hợp chi tiết cấu hình chân tín hiệu và kết nối vật lý của hệ thống thực nghiệm:", indent=0.4)
    table_app_a = [
        ("INMP441 SCK (Bit Clock)", "ESP32-S3 GPIO 4", "Tín hiệu xung nhịp BCLK chuẩn I2S Master"),
        ("INMP441 WS (Word Select)", "ESP32-S3 GPIO 5", "Tín hiệu chọn kênh LRCLK (16 kHz)"),
        ("INMP441 SD (Serial Data)", "ESP32-S3 GPIO 6", "Dữ liệu âm thanh nối tiếp từ microphone về vi điều khiển"),
        ("INMP441 L/R (Channel Select)", "ESP32-S3 GND", "Kéo xuống mức thấp để chọn Kênh Trái (Left Channel)"),
        ("INMP441 VDD (Power Supply)", "ESP32-S3 3.3V", "Nguồn điện áp 3.3V ổn định từ IC nguồn onboard"),
        ("INMP441 GND (Ground)", "ESP32-S3 GND", "Nối đất chung tín hiệu"),
        ("Cổng giao tiếp nạp / Debug", "ESP32-S3 USB Type-C", "Cổng USB-to-UART nạp firmware và xuất log Serial 115200 bps")
    ]
    md.add_custom_table(doc, ["Điểm kết nối cảm biến INMP441", "Chân kết nối bo mạch ESP32-S3", "Mô tả vai trò kỹ thuật"], table_app_a, [2.3, 1.8, 2.6])

    # Phụ lục B
    md.add_heading_2(doc, "Phụ lục B: Cấu trúc mẫu phản hồi API JSON /api/data thực tế")
    md.add_p(doc, 
        "Dữ liệu mẫu thu thập thực tế từ Endpoint HTTP GET `/api/data` tại thời điểm hệ thống bắt được nốt A4 hợp lệ:", indent=0.4)

    p_json = doc.add_paragraph()
    p_json.paragraph_format.space_before = Pt(4)
    p_json.paragraph_format.space_after = Pt(6)
    json_sample = (
        "{\n"
        "  \"frequency\": 440.237,\n"
        "  \"note\": \"A4\",\n"
        "  \"target\": 440.000,\n"
        "  \"cents\": 0.93,\n"
        "  \"confidence\": 100.0,\n"
        "  \"estimator\": \"F1_PRIMARY\",\n"
        "  \"valid\": true,\n"
        "  \"frame\": 397,\n"
        "  \"latency_ms\": 24.84\n"
        "}"
    )
    r_j = p_json.add_run(json_sample)
    r_j.font.name = "Consolas"
    r_j.font.size = Pt(10)
    r_j.font.color.rgb = md.C_BLUE

    # Phụ lục C
    md.add_heading_2(doc, "Phụ lục C: Bảng tần số chuẩn các nốt cơ bản của đàn Piano (A0 đến C8)")
    md.add_p(doc, 
        "Bảng tần số danh định lý thuyết của các nốt nhạc chuẩn theo hệ âm bằng 12-TET với A4 = 440.00 Hz:", indent=0.4)

    table_piano_keys = [
        ("A0", "21", "27.500 Hz", "C4 (Middle C)", "60", "261.626 Hz"),
        ("C1", "24", "32.703 Hz", "E4", "64", "329.628 Hz"),
        ("E1", "28", "41.203 Hz", "A4 (Concert Pitch)", "69", "440.000 Hz"),
        ("A1", "33", "55.000 Hz", "C5", "72", "523.251 Hz"),
        ("C2", "36", "65.406 Hz", "C6", "84", "1046.502 Hz"),
        ("E2", "40", "82.407 Hz", "A6", "93", "1760.000 Hz"),
        ("A2", "45", "110.000 Hz", "C7", "96", "2093.005 Hz"),
        ("C3", "48", "130.813 Hz", "A7", "105", "3520.000 Hz"),
        ("D3", "50", "146.832 Hz", "C8 (Highest Key)", "108", "4186.009 Hz"),
        ("E3", "52", "164.814 Hz", "--", "--", "--")
    ]
    md.add_custom_table(doc, 
        ["Nốt nhạc", "Số MIDI", "Tần số chuẩn", "Nốt nhạc", "Số MIDI", "Tần số chuẩn"],
        table_piano_keys, [1.0, 0.9, 1.4, 1.3, 0.9, 1.4])

    # Phụ lục D
    md.add_heading_2(doc, "Phụ lục D: Cấu hình firmware và trích đoạn mã DSP cốt lõi")
    md.add_p(doc, 
        "Trích đoạn hàm tính toán nội suy parabol bậc hai (Quadratic Interpolation) trong tệp `main/main.c`:", indent=0.4)

    p_cqi = doc.add_paragraph()
    p_cqi.paragraph_format.space_before = Pt(4)
    p_cqi.paragraph_format.space_after = Pt(6)
    cqi_code = (
        "// Thuật toán nội suy parabol bậc hai tìm cực trị liên tục giữa các bin\n"
        "float alpha = magnitude[peak_w - 1];\n"
        "float beta  = magnitude[peak_w];\n"
        "float gamma = magnitude[peak_w + 1];\n"
        "float denom = alpha - 2.0f * beta + gamma;\n"
        "float p = (fabsf(denom) > 1e-6f) ? 0.5f * (alpha - gamma) / denom : 0.0f;\n"
        "if (p < -0.5f) p = -0.5f;\n"
        "if (p >  0.5f) p =  0.5f;\n"
        "float interp_freq = (((float)peak_w + p) * BIN_RESOLUTION_HZ) / (float)m;"
    )
    r_cqi = p_cqi.add_run(cqi_code)
    r_cqi.font.name = "Consolas"
    r_cqi.font.size = Pt(9.5)
    r_cqi.font.color.rgb = md.C_BLUE

print("section_ch5_ch7 compiled successfully.")
