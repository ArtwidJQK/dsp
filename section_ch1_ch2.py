# -*- coding: utf-8 -*-
"""
Module: Chapter 1 (Introduction) and Chapter 2 (Theoretical Foundations)
Project: PIANO CHROMATIC TUNER USING ESP32-S3 AND INMP441
Student: Le Tan Dung - MSSV: 24150654
"""

from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import make_doc as md

def build_ch1_ch2(doc):
    # =========================================================================
    # CHƯƠNG 1 — GIỚI THIỆU
    # =========================================================================
    md.add_heading_1(doc, "CHƯƠNG 1 — GIỚI THIỆU")

    # 1.1 Đặt vấn đề
    md.add_heading_2(doc, "1.1. Đặt vấn đề")
    md.add_p(doc, 
        "Trong lĩnh vực âm nhạc và kỹ thuật âm thanh, việc căn chỉnh cao độ (tuning) cho các nhạc cụ có dây, "
        "đặc biệt là đàn piano cơ (acoustic piano), giữ vai trò quyết định đến chất lượng biểu diễn và cảm nhận âm nhạc. "
        "Một cây đàn piano tiêu chuẩn có 88 phím tương ứng với dải tần số trải dài từ A0 (27.50 Hz) đến C8 (4186.01 Hz). "
        "Khác với các nhạc cụ đơn giản như guitar chỉ có 6 dây với dải tần tương đối hẹp (khoảng 82 Hz đến 1200 Hz), "
        "hệ thống dây đàn piano có sự biến thiên rất lớn về chiều dài, khối lượng riêng, lực căng (lên tới hơn 15-20 tấn trên toàn bộ khung gang) "
        "và đặc tính âm học của từng quãng tám [6].", indent=0.4)

    md.add_p(doc, 
        "Hiện nay, mặc dù các ứng dụng lên dây đàn trên điện thoại thông minh (smartphone) rất phổ biến, chúng thường gặp phải "
        "nhiều giới hạn khi áp dụng cho đàn piano: (1) Microphone tích hợp trên điện thoại thường được thiết kế ưu tiên thu âm giọng nói "
        "(300 Hz - 3.4 kHz) nên suy giảm rất mạnh ở dải hạ âm dưới 100 Hz; (2) Tầng thu âm chịu sự can thiệp của các thuật toán xử lý "
        "tự động (AGC - Automatic Gain Control, Noise Suppression) làm biến dạng đỉnh phổ thực tế; (3) Độ trễ âm thanh của hệ điều hành "
        "di động (Android/iOS audio latency) thường dao động khó lường, gây giật lag khi người dùng gõ phím liên tục [2]. "
        "Ngược lại, các thiết bị lên dây chuyên dụng thương mại (hardware tuners) có giá thành rất cao, thường là hệ thống đóng kín, "
        "không cho phép tùy biến sâu các thuật toán xử lý tín hiệu theo từng đặc tính âm học cụ thể.", indent=0.4)

    md.add_p(doc, 
        "Do đó, việc nghiên cứu và xây dựng một thiết bị phần cứng nhúng độc lập, chi phí thấp, sử dụng vi điều khiển hiệu năng cao "
        "ESP32-S3 kết hợp microphone MEMS kỹ thuật số I2S INMP441 để xử lý tín hiệu âm thanh piano theo thời gian thực là một đề tài mang "
        "tính thời sự và giá trị ứng dụng cao. Đây là cơ hội điển hình để áp dụng trực tiếp các kiến thức nền tảng trong môn học "
        "Xử lý tín hiệu số (DSP) vào một bài toán kỹ thuật thực tế đầy thách thức [1].", indent=0.4)

    # 1.2 Mục tiêu
    md.add_heading_2(doc, "1.2. Mục tiêu")
    md.add_p(doc, 
        "Mục tiêu cốt lõi của đề tài bao gồm:", indent=0.4)
    md.add_p(doc, 
        "1. Thiết kế và chế tạo hoàn chỉnh mô hình phần cứng thu nhận âm thanh số nhỏ gọn, sử dụng vi điều khiển ESP32-S3 N16R8 "
        "giao tiếp trực tiếp với microphone kỹ thuật số MEMS INMP441 qua bus I2S bằng chế độ DMA tốc độ cao, loại bỏ hoàn toàn nhiễu tương tự.", indent=0.4)
    md.add_p(doc, 
        "2. Nghiên cứu, xây dựng và tối ưu hóa một pipeline xử lý tín hiệu số (DSP Pipeline) hoàn chỉnh trên nền tảng ESP-IDF (C/C++), "
        "kết hợp các kỹ thuật lọc DC, cửa sổ hóa Hann, biến đổi Fourier nhanh (FFT), sàng lọc đỉnh phổ cục bộ, giải thuật phân tích họa âm "
        "(Harmonic-Aware Fundamental Detection) và nội suy parabol bậc hai (Quadratic Interpolation) để ước lượng chính xác tần số cơ bản f0.", indent=0.4)
    md.add_p(doc, 
        "3. Xây dựng thuật toán ánh xạ tự động tần số đo được sang nốt nhạc chuẩn theo hệ âm 12 nốt đồng đều (Equal Temperament, A4 = 440 Hz) "
        "và tính toán độ sai lệch cao độ theo đơn vị cent trong thời gian thực.", indent=0.4)
    md.add_p(doc, 
        "4. Tích hợp máy chủ web nhúng (Embedded HTTP Server) ngay trên ESP32-S3 và phát triển giao diện Web Frontend trực quan, sinh động "
        "(Celestial / Fantasy Piano Tuner) bằng HTML5/CSS3/JavaScript thuần, cho phép người dùng truy cập không dây qua Wi-Fi từ mọi trình duyệt "
        "mà không cần cài đặt ứng dụng hay phụ thuộc vào Internet bên ngoài.", indent=0.4)

    # 1.3 Phạm vi
    md.add_heading_2(doc, "1.3. Phạm vi nghiên cứu")
    md.add_p(doc, 
        "Phạm vi và giới hạn nghiên cứu của đề tài được xác định rõ ràng như sau:", indent=0.4)
    md.add_p(doc, 
        "• Đối tượng nhận diện: Thiết bị được thiết kế chuyên biệt cho bài toán nhận diện cao độ đơn âm (Single-Note Pitch Detection) "
        "của đàn piano cơ. Hệ thống KHÔNG hỗ trợ và nằm ngoài phạm vi xử lý tín hiệu hợp âm đa âm (Polyphonic Pitch Estimation / Chord Recognition). "
        "Người sử dụng được yêu cầu gảy hoặc nhấn từng phím đơn lẻ để thiết bị phân tích.", indent=0.4)
    md.add_p(doc, 
        "• Phạm vi kiểm thử thực tế: Do giới hạn điều kiện phòng thí nghiệm và thời gian thu thập mẫu âm học thực tế, các phép đo đạc định lượng "
        "đã được tập trung kiểm chứng trên 5 nốt đại diện thuộc dải trung âm và cận trầm: A4 (440.00 Hz), C4 (261.63 Hz), C5 (523.25 Hz), "
        "D3 (146.83 Hz), E3 (164.81 Hz), cùng các khảo sát chuyên sâu tại nốt trầm E2 (82.41 Hz). Các nốt thuộc quãng cực trầm (A0 - C2) "
        "và quãng cực cao (C6 - C8) được phân loại là chưa kiểm thử đầy đủ trên phần cứng thực tế.", indent=0.4)
    md.add_p(doc, 
        "• Kiến trúc hiển thị: Trong phiên bản cuối cùng của dự án, hệ thống chuyển đổi hoàn toàn sang hiển thị qua giao diện Web Server nhúng; "
        "màn hình phần cứng OLED/LCD không được sử dụng để tối ưu hóa tài nguyên chân GPIO và cung cấp không gian trực quan hóa phong phú hơn.", indent=0.4)

    # 1.4 Yêu cầu hệ thống
    md.add_heading_2(doc, "1.4. Yêu cầu hệ thống")
    md.add_p(doc, 
        "Dựa trên tài liệu hướng dẫn đồ án môn học Xử lý tín hiệu số [2], hệ thống phải thỏa mãn các tiêu chí kỹ thuật sau:", indent=0.4)
    md.add_p(doc, 
        "• Yêu cầu chức năng: Tự động phát hiện khi có tín hiệu âm thanh piano phát ra; xác định chính xác tên nốt nhạc danh định gần nhất "
        "(từ A0 đến C8); tính toán độ lệch tần số và hiển thị độ lệch cao độ (cents deviation) cùng thanh chỉ báo trạng thái trực quan: "
        "ĐÚNG CAO ĐỘ (IN TUNE), QUÁ THẤP (TOO LOW), hoặc QUÁ CAO (TOO HIGH).", indent=0.4)
    md.add_p(doc, 
        "• Yêu cầu độ chính xác lý thuyết và mục tiêu thiết kế: Độ chính xác tần số mục tiêu đặt ra cho bài toán lên dây đàn là sai số "
        "Delta f < 0.5 Hz (tương ứng với sai số cao độ trong phạm vi khoảng +/- 3 đến +/- 5 cents ở dải trung âm).", indent=0.4)
    md.add_p(doc, 
        "• Yêu cầu độ trễ thời gian thực (Real-time Latency): Thời gian xử lý từ lúc thu nhận âm thanh đến khi cập nhật kết quả đo phải "
        "đáp ứng chuẩn thời gian thực, với độ trễ xử lý tính toán của vi điều khiển nhỏ hơn 50 ms và tổng chu kỳ cập nhật giao diện nhỏ hơn 500 ms [2].", indent=0.4)
    md.add_p(doc, 
        "• Yêu cầu độ ổn định: Hệ thống phải hoạt động liên tục, không xảy ra hiện tượng tràn bộ nhớ (memory leak), tự khởi động lại (watchdog reset) "
        "hoặc khóa xung đột bộ nhớ giữa luồng tính toán DSP và luồng phục vụ mạng HTTP.", indent=0.4)

    # 1.5 Phương pháp thực hiện
    md.add_heading_2(doc, "1.5. Phương pháp thực hiện")
    md.add_p(doc, 
        "Đề tài áp dụng phương pháp nghiên cứu kết hợp giữa mô hình hóa lý thuyết và thực nghiệm kỹ thuật thực chứng (Empirical Engineering):", indent=0.4)
    md.add_p(doc, 
        "1. Phương pháp lý thuyết: Khảo sát mô hình toán học của tín hiệu rời rạc, biến đổi Fourier rời rạc (DFT), hiệu ứng rò rỉ phổ, hàm cửa sổ Hann, "
        "thuật toán nội suy parabol bậc hai (Quadratic Interpolation) theo giáo trình chuẩn của ĐHQG Hà Nội [1] và các nghiên cứu âm học nhạc cụ [6].", indent=0.4)
    md.add_p(doc, 
        "2. Phương pháp mô phỏng và kiểm chứng thuật toán: Xây dựng các kịch bản kiểm thử với sóng sin nhân tạo và tín hiệu piano mô phỏng "
        "để xác minh độ chính xác của thuật toán phân tích họa âm trước khi nạp xuống vi điều khiển.", indent=0.4)
    md.add_p(doc, 
        "3. Phương pháp triển khai nhúng: Viết mã nguồn C/C++ trực tiếp trên ESP-IDF v6.0.2 sử dụng FreeRTOS, cấu hình ngoại vi I2S ở chế độ DMA, "
        "tối ưu hóa bộ nhớ RAM bằng cách cấp phát tĩnh và tiền tính toán các bảng lượng giác.", indent=0.4)
    md.add_p(doc, 
        "4. Phương pháp đo đạc thực nghiệm trên phần cứng (Hardware Instrumentation): Kết nối phần cứng thật, gảy các phím piano cơ acoustic "
        "và ghi nhận trực tiếp các khung dữ liệu qua giao tiếp Serial và Web API. Toàn bộ các phân tích và kết luận trong báo cáo này đều tuân thủ "
        "nguyên tắc REAL-DATA ONLY, không sử dụng số liệu suy diễn hoặc giả lập chưa được kiểm chứng.", indent=0.4)

    # =========================================================================
    # CHƯƠNG 2 — CƠ SỞ LÝ THUYẾT
    # =========================================================================
    md.add_heading_1(doc, "CHƯƠNG 2 — CƠ SỞ LÝ THUYẾT")

    # 2.1 Tín hiệu âm thanh
    md.add_heading_2(doc, "2.1. Bản chất tín hiệu âm thanh đàn Piano")
    md.add_p(doc, 
        "Tín hiệu âm thanh là sự lan truyền của sóng áp suất cơ học trong môi trường đàn hồi (không khí). "
        "Khi một phím đàn piano được nhấn, búa đàn bọc nỉ (felt hammer) đập vào một hoặc cụm 2-3 sợi dây đàn thép được kéo căng. "
        "Dây đàn dao động tự do tạo ra sóng dừng với các nút và bụng sóng, truyền dao động qua ngựa đàn (bridge) vào bảng cộng hưởng (soundboard). "
        "Bảng cộng hưởng làm dao động khối không khí xung quanh, tạo ra sóng âm lan truyền đến tai người nghe và microphone [6].", indent=0.4)

    md.add_p(doc, 
        "Về mặt toán học, tín hiệu âm thanh của một nốt nhạc lý tưởng là tín hiệu tuần hoàn có thể biểu diễn dưới dạng chuỗi Fourier "
        "gồm tổng của các thành phần dao động điều hòa:", indent=0.4)
    md.add_equation(doc, "x(t) = \\sum_{m=1}^{\\infty} A_m \\cos(2\\pi m f_0 t + \\phi_m)", "2.1")
    md.add_p(doc, 
        "Trong đó: f0 là tần số cơ bản (fundamental frequency) quy định cao độ của nốt nhạc; m là bậc họa âm (harmonic number); "
        "Am và phi_m lần lượt là biên độ và pha ban đầu của họa âm bậc m.", indent=0.4)

    # 2.2 Lấy mẫu và Định lý Nyquist
    md.add_heading_2(doc, "2.2. Lấy mẫu tín hiệu và Định lý Nyquist - Shannon")
    md.add_p(doc, 
        "Để xử lý tín hiệu âm thanh liên tục x(t) bằng các hệ thống số, tín hiệu phải được rời rạc hóa theo thời gian thông qua quá trình lấy mẫu "
        "với chu kỳ lấy mẫu Ts = 1 / Fs, tạo thành dãy số rời rạc x[n] = x(n Ts) với n là chỉ số mẫu nguyên [1].", indent=0.4)

    md.add_p(doc, 
        "Theo Định lý lấy mẫu Nyquist - Shannon, để có thể khôi phục hoàn toàn và tránh hiện tượng chồng phổ (aliasing), tần số lấy mẫu Fs "
        "phải lớn hơn ít nhất hai lần tần số cực đại f_max có trong phổ của tín hiệu liên tục:", indent=0.4)
    md.add_equation(doc, "F_s \\ge 2 f_{\\max}", "2.2")
    md.add_p(doc, 
        "Tần số f_Nyquist = Fs / 2 được gọi là tần số Nyquist. Trong đề tài này, tần số lấy mẫu baseline được thiết lập là Fs = 16.000 Hz. "
        "Do đó, tần số Nyquist đạt được là:", indent=0.4)
    md.add_equation(doc, "f_{\\text{Nyquist}} = \\frac{16000}{2} = 8000 \\text{ Hz}", "2.3")
    md.add_p(doc, 
        "Vì nốt cao nhất của đàn piano là C8 có tần số danh định khoảng 4186.01 Hz, việc lựa chọn Fs = 16.000 Hz đảm bảo bao phủ hoàn toàn "
        "tất cả các tần số cơ bản của 88 phím piano, đồng thời cho phép phân tích các họa âm bậc 2 của các nốt lên đến 4.000 Hz mà không gặp "
        "hiện tượng méo do chồng phổ [1].", indent=0.4)

    # 2.3 Chuẩn I2S
    md.add_heading_2(doc, "2.3. Giao thức truyền thông âm thanh số I2S")
    md.add_p(doc, 
        "Chuẩn I2S (Inter-IC Sound) do hãng Philips Semiconductor định nghĩa là một giao thức truyền thông nối tiếp chuyên dụng đồng bộ 3 dây "
        "được thiết kế để truyền tải dữ liệu âm thanh số dạng PCM giữa các vi mạch tích hợp xử lý âm thanh [4]. Khác với các microphone tương tự (analog) "
        "dễ bị suy hao tín hiệu và nhiễu điện áp trên dây dẫn, microphone MEMS I2S tích hợp sẵn cảm biến áp suất âm vi cơ điện tử, mạch tiền khuếch đại "
        "và bộ biến đổi ADC độ phân giải cao ngay trên một vi mạch duy nhất.", indent=0.4)

    md.add_p(doc, 
        "Giao thức I2S sử dụng 3 đường tín hiệu chính:", indent=0.4)
    md.add_p(doc, 
        "• BCLK (Continuous Serial Clock / Bit Clock): Xung nhịp đồng bộ truyền từng bit dữ liệu. Tần số xung nhịp bit được xác định bởi công thức: "
        "f_BCLK = 2 x f_Fs x N_bits. Với Fs = 16 kHz và khung 32-bit mỗi kênh (stereo slot), f_BCLK = 2 x 16000 x 32 = 1.024.000 Hz (1.024 MHz).", indent=0.4)
    md.add_p(doc, 
        "• WS / LRCLK (Word Select / Left-Right Clock): Xung nhịp lựa chọn kênh âm thanh, có tần số đúng bằng tần số lấy mẫu Fs (16 kHz). "
        "Khi WS ở mức logic thấp (0), dữ liệu truyền thuộc Kênh Trái (Left Channel); khi WS ở mức logic cao (1), dữ liệu truyền thuộc Kênh Phải (Right Channel).", indent=0.4)
    md.add_p(doc, 
        "• SD / DIN (Serial Data): Đường truyền dữ liệu âm thanh nối tiếp dưới dạng bù 2 (two's complement), bắt đầu từ bit có trọng số lớn nhất (MSB). "
        "Dữ liệu được trễ 1 chu kỳ BCLK sau cạnh chuyển mức của tín hiệu WS theo đúng chuẩn Philips I2S tiêu chuẩn [4].", indent=0.4)

    # 2.4 FFT
    md.add_heading_2(doc, "2.4. Biến đổi Fourier rời rạc (DFT) và Thuật toán FFT")
    md.add_p(doc, 
        "Biến đổi Fourier rời rạc (Discrete Fourier Transform - DFT) là công cụ toán học nền tảng trong xử lý tín hiệu số dùng để chuyển đổi "
        "một chuỗi mẫu hữu hạn x[n] trong miền thời gian sang biểu diễn phổ tần số X[k] trong miền tần số rời rạc [1].", indent=0.4)

    md.add_p(doc, 
        "Biểu thức định nghĩa của biến đổi DFT N điểm được xác định theo Giáo trình Xử lý tín hiệu số [1]:", indent=0.4)
    md.add_equation(doc, "X[k] = \\sum_{n=0}^{N-1} x[n] e^{-j \\frac{2\\pi}{N} k n} = \\sum_{n=0}^{N-1} x[n] W_N^{k n}, \\quad k = 0, 1, \\dots, N-1", "2.4")
    md.add_p(doc, 
        "Trong đó: W_N = e^{-j 2pi / N} là hệ số quay (twiddle factor). Phổ biên độ (Magnitude Spectrum) được tính bằng:", indent=0.4)
    md.add_equation(doc, "|X[k]| = \\sqrt{\\text{Re}\\{X[k]\\}^2 + \\text{Im}\\{X[k]\\}^2}", "2.5")

    md.add_p(doc, 
        "Nếu tính toán trực tiếp theo công thức (2.4), độ phức tạp tính toán yêu cầu N^2 phép nhân và cộng phức. Để thực thi trong thời gian thực "
        "trên vi điều khiển nhúng, thuật toán Biến đổi Fourier nhanh (Fast Fourier Transform - FFT) cấu trúc Radix-2 Decimation-In-Time (DIT) theo giải thuật "
        "Cooley - Tukey được áp dụng [1]. Thuật toán phân chia dãy x[n] thành hai dãy con mẫu chẵn và mẫu lẻ:", indent=0.4)
    md.add_equation(doc, "X[k] = \\sum_{r=0}^{N/2-1} x[2r] W_{N/2}^{k r} + W_N^k \\sum_{r=0}^{N/2-1} x[2r+1] W_{N/2}^{k r} = X_{\\text{even}}[k] + W_N^k X_{\\text{odd}}[k]", "2.6")
    md.add_p(doc, 
        "Nhờ tính chất tuần hoàn và đối xứng của hệ số quay W_N^(k + N/2) = - W_N^k, độ phức tạp tính toán giảm xuống chỉ còn (N / 2) log2(N) phép nhân phức. "
        "Với N = 4096 điểm, FFT giúp giảm khối lượng tính toán từ khoảng 16.7 triệu phép tính xuống chỉ còn xấp xỉ 24.576 phép tính bướm (butterfly operations), "
        "cho phép vi điều khiển ESP32-S3 thực thi xong toàn bộ biến đổi trong thời gian chỉ khoảng 10-12 ms [1].", indent=0.4)

    # 2.5 Frequency Resolution
    md.add_heading_2(doc, "2.5. Độ phân giải tần số và sự đánh đổi thời gian - tần số")
    md.add_p(doc, 
        "Độ phân giải tần số (Frequency Bin Spacing - Delta f) của biến đổi DFT đại diện cho khoảng cách tần số giữa hai bin phổ liên tiếp k và k+1, "
        "được định nghĩa bởi công thức [1]:", indent=0.4)
    md.add_equation(doc, "\\Delta f = \\frac{F_s}{N}", "2.7")
    md.add_p(doc, 
        "Thời lượng của một khung tín hiệu phân tích trong miền thời gian (Frame Duration) là:", indent=0.4)
    md.add_equation(doc, "T_{\\text{frame}} = \\frac{N}{F_s} = \\frac{1}{\\Delta f}", "2.8")

    md.add_p(doc, 
        "Áp dụng các tham số baseline của hệ thống (Fs = 16.000 Hz, N = 4.096 điểm):", indent=0.4)
    md.add_equation(doc, "\\Delta f = \\frac{16000}{4096} = 3.90625 \\text{ Hz/bin}", "2.9")
    md.add_equation(doc, "T_{\\text{frame}} = \\frac{4096}{16000} = 0.256 \\text{ s} = 256.0 \\text{ ms}", "2.10")

    md.add_callout(doc, "NGUYÊN LÝ ĐÁNH ĐỔI THỜI GIAN - TẦN SỐ", 
        "Biểu thức (2.8) thể hiện nguyên lý bất định Heisenberg-Gabor trong xử lý tín hiệu: Muốn độ phân giải tần số càng mịn (Delta f nhỏ) "
        "thì độ dài khung phân tích thời gian bắt buộc phải càng lớn (T_frame lớn). Nếu chỉ tăng N thuần túy lên 8192 điểm để có Delta f = 1.95 Hz, "
        "thời gian tích lũy mẫu sẽ tăng lên tới 512 ms, gây ra độ trễ phản hồi quá lớn cho thiết bị lên dây đàn [2]. Ngược lại, nếu giảm N xuống 1024 điểm "
        "để cập nhật nhanh trong 64 ms, độ phân giải bin sẽ bị thoái hóa thành 15.625 Hz/bin, hoàn toàn không thể phân biệt được các nốt trầm liền kề "
        "(ví dụ E2 ~ 82.41 Hz và F2 ~ 87.31 Hz chỉ cách nhau 4.90 Hz). Do đó, N = 4096 là điểm cân bằng tối ưu giữa thời gian và tần số.", alert_type="note")

    # 2.6 Windowing
    md.add_heading_2(doc, "2.6. Hiện tượng rò rỉ phổ (Spectral Leakage) và Kỹ thuật cửa sổ hóa")
    md.add_p(doc, 
        "Biến đổi DFT ngầm định rằng chuỗi tín hiệu x[n] hữu hạn độ dài N được lặp lại vô hạn có chu kỳ. Khi tần số f của tín hiệu thực tế không phải "
        "là một bội số nguyên chính xác của độ phân giải bin Delta f (tức là f != k Delta f), số chu kỳ sóng nằm trong khung N điểm sẽ là một số lẻ phân số. "
        "Khi ghép nối các khung liên tiếp, tại biên n = 0 và n = N-1 sẽ xuất hiện bước nhảy gián đoạn (discontinuity) [1].", indent=0.4)

    md.add_p(doc, 
        "Bước nhảy gián đoạn nhân tạo này tạo ra các thành phần tần số cao không có trong tín hiệu gốc, dẫn đến hiện tượng năng lượng từ đỉnh phổ chính "
        "bị tràn sang tất cả các bin lân cận. Hiện tượng này được gọi là Hiện tượng rò rỉ phổ (Spectral Leakage) [1]. "
        "Để giảm thiểu rò rỉ phổ, tín hiệu trước khi đưa vào biến đổi FFT cần được nhân với một hàm cửa sổ trơn w[n]:", indent=0.4)
    md.add_equation(doc, "x_w[n] = x[n] \\cdot w[n], \\quad n = 0, 1, \\dots, N-1", "2.11")
    md.add_p(doc, 
        "Hàm cửa sổ có biên độ suy giảm dần về 0 một cách êm dịu ở hai đầu mút, giúp triệt tiêu bước nhảy gián đoạn khi tuần hoàn hóa tín hiệu [1].", indent=0.4)

    # 2.7 Hann Window
    md.add_heading_2(doc, "2.7. Đặc tính toán học của Cửa sổ Hann (Hann Window)")
    md.add_p(doc, 
        "Trong đề tài này, Cửa sổ Hann (Hanning Window) được lựa chọn làm hàm cửa sổ chuẩn nhờ sự cân bằng tuyệt vời giữa độ rộng búp sóng chính "
        "và khả năng triệt tiêu búp sóng phụ [1]. Biểu thức toán học của cửa sổ Hann N điểm được định nghĩa theo [1]:", indent=0.4)
    md.add_equation(doc, "w[n] = 0.5 \\left(1 - \\cos\\left(\\frac{2\\pi n}{N - 1}\\right)\\right) = \\sin^2\\left(\\frac{\\pi n}{N - 1}\\right), \\quad 0 \\le n \\le N - 1", "2.12")

    md.add_p(doc, 
        "Đặc tính phổ của cửa sổ Hann có các thông số kỹ thuật then chốt [1]:", indent=0.4)
    md.add_p(doc, 
        "• Bề rộng búp sóng chính (Mainlobe width): Bằng 4 bin phổ (4 Delta f = 15.625 Hz), rộng hơn cửa sổ chữ nhật (2 bin) nhưng búp sóng chính có dạng cong parabol rất mịn.", indent=0.4)
    md.add_p(doc, 
        "• Mức búp sóng phụ cao nhất (Peak sidelobe level): Đạt -31.5 dB so với đỉnh búp sóng chính (so với chỉ -13 dB của cửa sổ chữ nhật).", indent=0.4)
    md.add_p(doc, 
        "• Tốc độ suy giảm búp sóng phụ (Sidelobe roll-off rate): Suy giảm rất nhanh theo quy luật -18 dB/octave (-60 dB/decade), giúp ngăn chặn tuyệt đối "
        "năng lượng của các nốt nhạc mạnh ở dải trung tràn sang che lấp các nốt yếu ở dải trầm hoặc dải cao [1].", indent=0.4)

    # 2.8 Local Spectral Peak
    md.add_heading_2(doc, "2.8. Trích xuất đỉnh phổ cục bộ và đánh giá tỷ số SNR")
    md.add_p(doc, 
        "Sau khi thực hiện FFT và tính phổ biên độ mag[k], hệ thống không tìm kiếm mù quáng đỉnh lớn nhất toàn phổ mà quét tìm các Đỉnh phổ cục bộ "
        "(Local Spectral Peaks). Một bin k được xem là đỉnh phổ cục bộ nếu biên độ của nó lớn hơn hoặc bằng cả hai bin lân cận trực tiếp:", indent=0.4)
    md.add_equation(doc, "\\text{mag}[k] \\ge \\text{mag}[k-1] \\quad \\text{và} \\quad \\text{mag}[k] \\ge \\text{mag}[k+1]", "2.13")

    md.add_p(doc, 
        "Để loại trừ các dao động ngẫu nhiên của nhiễu nền môi trường, mỗi đỉnh cục bộ được đánh giá thông qua Sàn nhiễu cục bộ (Local Noise Floor) "
        "được tính bằng giá trị trung vị (median) của 24 bin lân cận (loại trừ +/- 2 bin thuộc búp sóng chính). Độ nổi bật (Prominence) và tỷ số SNR cục bộ được định nghĩa:", indent=0.4)
    md.add_equation(doc, "\\text{Prominence}_k = \\frac{\\text{mag}[k]}{\\max(\\text{LocalFloor}_k, 0.05)}", "2.14")
    md.add_equation(doc, "\\text{SNR}_{\\text{dB}, k} = 20 \\log_{10}(\\text{Prominence}_k)", "2.15")

    # 2.9 Quadratic Interpolation
    md.add_heading_2(doc, "2.9. Thuật toán nội suy parabol bậc hai (Quadratic Interpolation)")
    md.add_p(doc, 
        "Như đã phân tích ở mục 2.5, độ phân giải bin rời rạc của FFT là Delta f = 3.90625 Hz. Nếu chỉ lấy tần số tương ứng với chỉ số bin nguyên k "
        "(f_peak = k Delta f), sai số lượng tử hóa tối đa có thể lên tới +/- Delta f / 2 = +/- 1.953 Hz. Sai số này quá lớn, không thể đáp ứng tiêu chuẩn lên dây (< 0.5 Hz). "
        "Tuy nhiên, do búp sóng chính của cửa sổ Hann có dạng trơn liên tục, vị trí đỉnh thực sự của sóng sin nằm giữa các bin sẽ làm cho 3 giá trị biên độ tại "
        "k-1, k, k+1 có mối quan hệ hình học chặt chẽ [2].", indent=0.4)

    md.add_p(doc, 
        "Phương pháp Nội suy parabol bậc hai (Quadratic Interpolation / Parabolic Peak Interpolation) xấp xỉ hình dạng của đỉnh phổ liên tục trong lân cận "
        "bin k bằng một đường parabol bậc hai đi qua 3 điểm thực nghiệm: (k-1, alpha), (k, beta), (k+1, gamma), trong đó:", indent=0.4)
    md.add_equation(doc, "\\alpha = \\text{mag}[k-1], \\quad \\beta = \\text{mag}[k], \\quad \\gamma = \\text{mag}[k+1]", "2.16")

    md.add_p(doc, 
        "Giả sử hàm parabol có dạng y(x) = a (x - k)^2 + b (x - k) + c. Thay tọa độ 3 điểm vào và tìm điểm cực trị dy/dx = 0, ta thu được độ dịch đỉnh phân số p:", indent=0.4)
    md.add_equation(doc, "p = \\frac{1}{2} \\frac{\\alpha - \\gamma}{\\alpha - 2\\beta + \\gamma} = 0.5 \\frac{\\text{mag}[k-1] - \\text{mag}[k+1]}{\\text{mag}[k-1] - 2\\text{mag}[k] + \\text{mag}[k+1]}", "2.17")

    md.add_p(doc, 
        "Giá trị p luôn nằm trong khoảng [-0.5, +0.5] bin. Từ đó, tần số ước lượng chính xác liên tục của đỉnh phổ được xác định bởi:", indent=0.4)
    md.add_equation(doc, "f_{\\text{interp}} = (k + p) \\frac{F_s}{N} = (k + p) \\Delta f", "2.18")

    md.add_callout(doc, "LƯU Ý VỀ ĐỘ CHÍNH XÁC CỦA NỘI SUY (REAL-DATA PRINCIPLE)", 
        "Giải thuật nội suy parabol bậc hai (2.17) - (2.18) cho phép hệ thống ước lượng vị trí đỉnh phổ với độ mịn vượt qua giới hạn bin 3.90625 Hz. "
        "Tuy nhiên, về mặt toán học và vật lý thực tế, CẦN LƯU Ý RẰNG: NỘI SUY KHÔNG ĐỒNG NGHĨA VỚI VIỆC TỰ ĐỘNG ĐẢM BẢO ĐỘ CHÍNH XÁC < 0.5 HZ TRONG MỌI ĐIỀU KIỆN! "
        "Sai số của phương pháp nội suy phụ thuộc mật thiết vào tỷ số SNR, hiện tượng rò rỉ phổ từ các họa âm lân cận, và mức độ méo phổ do nhiễu môi trường. "
        "Do đó, bất kỳ kết luận nào về độ chính xác của hệ thống đều bắt buộc phải được chứng minh bằng số liệu đo đạc thực tế.", alert_type="warn")

    # 2.10 Fundamental & Harmonics
    md.add_heading_2(doc, "2.10. Tần số cơ bản, chuỗi họa âm và tính bất điều hòa của đàn Piano")
    md.add_p(doc, 
        "Một trong những khác biệt lớn nhất giữa tín hiệu âm thanh piano và tín hiệu sóng sin thuần túy là sự tồn tại của chuỗi họa âm phức tạp. "
        "Một nốt nhạc piano phát ra không chỉ có một tần số cơ bản f0 mà đi kèm một tập hợp các họa âm bậc cao:", indent=0.4)
    md.add_equation(doc, "f_1 \\approx f_0, \\quad f_2 \\approx 2f_0, \\quad f_3 \\approx 3f_0, \\quad f_4 \\approx 4f_0, \\dots", "2.19")

    md.add_p(doc, 
        "Trong thực tế đàn piano cơ, có hai hiện tượng âm học cực kỳ nghiêm trọng gây sai lệch thuật toán tìm tần số cơ bản:", indent=0.4)

    md.add_p(doc, 
        "1. Hiện tượng suy giảm năng lượng tần số cơ bản ở dải trầm (Weak Fundamental Phenomenon): "
        "Ở các nốt trầm (ví dụ A0 ~ 27.5 Hz đến E2 ~ 82.4 Hz), dây đàn piano rất dài và nặng nhưng bảng cộng hưởng (soundboard) và microphone MEMS "
        "bị suy hao cơ học rất mạnh tại tần số thấp. Kết quả thực nghiệm cho thấy năng lượng tại f0 cực kỳ yếu (thậm chí biên độ chỉ bằng 5-10% của họa âm), "
        "trong khi các họa âm bậc 2 (2f0), bậc 3 (3f0), bậc 4 (4f0) lại có biên độ lớn áp đảo. Nếu thuật toán chỉ tìm đỉnh FFT cực đại toàn cục (Global Peak), "
        "hệ thống chắc chắn sẽ bắt nhầm nốt thành quãng tám trên (Octave Jump) hoặc quãng năm đúng [6].", indent=0.4)

    md.add_p(doc, 
        "2. Hiện tượng bất điều hòa của dây đàn thép (String Inharmonicity): "
        "Dây đàn piano thực tế không phải là sợi dây mềm lý tưởng mà là các thanh thép có độ cứng uốn đàn hồi (bending stiffness). "
        "Độ cứng này tác dụng thêm một lực phục hồi phụ trợ khi dây dao động ở các bước sóng ngắn (họa âm bậc cao). "
        "Theo phương trình âm học Fletcher [6], tần số của họa âm bậc m bị dạt lên cao (stretch sharp) so với bội số nguyên lý thuyết theo công thức:", indent=0.4)
    md.add_equation(doc, "f_m = m f_0 \\sqrt{1 + B m^2}", "2.20")
    md.add_p(doc, 
        "Trong đó B là hệ số bất điều hòa (inharmonicity coefficient), phụ thuộc vào đường kính, lực căng và mô-đun đàn hồi Young của dây thép đàn. "
        "Do đó, họa âm bậc 2 sẽ có f2 > 2f0, họa âm bậc 3 có f3 > 3f0. Hiện tượng này đặc biệt rõ nét ở các nốt cao (dây ngắn và cứng) "
        "hoặc các nốt trầm có quấn dây đồng [6].", indent=0.4)

    # 2.11 Equal Temperament
    md.add_heading_2(doc, "2.11. Hệ âm 12 nốt đồng đều (Equal Temperament)")
    md.add_p(doc, 
        "Đàn piano hiện đại sử dụng hệ âm 12 nốt đồng đều (12-Tone Equal Temperament - 12-TET). "
        "Trong hệ thống này, một quãng tám (tỷ số tần số 2:1) được chia thành 12 nửa cung (semitones) có tỷ lệ tần số hoàn toàn bằng nhau [2]. "
        "Tỷ số tần số giữa hai nửa cung liền kề là hằng số:", indent=0.4)
    md.add_equation(doc, "r = \\sqrt[12]{2} = 2^{1/12} \\approx 1.059463094", "2.21")

    md.add_p(doc, 
        "Quy chuẩn quốc tế (ISO 16) lấy nốt La quãng tám 4 (A4) làm cao độ tham chiếu chuẩn với tần số chính xác là 440.00 Hz [2].", indent=0.4)

    # 2.12 Frequency-to-Note
    md.add_heading_2(doc, "2.12. Ánh xạ tần số sang số nốt chuẩn MIDI")
    md.add_p(doc, 
        "Chuẩn giao tiếp nhạc cụ số MIDI (Musical Instrument Digital Interface) quy ước nốt A4 tương ứng với số nốt MIDI n = 69. "
        "Từ một tần số cơ bản đo được f0, số nốt MIDI liên tục tương ứng được tính toán thông qua hàm logarit cơ số 2 [2]:", indent=0.4)
    md.add_equation(doc, "n_{\\text{cont}} = 69 + 12 \\log_2\\left(\\frac{f_0}{440.0}\\right)", "2.22")

    md.add_p(doc, 
        "Số nốt MIDI nguyên danh định gần nhất được xác định bằng phép làm tròn:", indent=0.4)
    md.add_equation(doc, "n_{\\text{MIDI}} = \\text{round}\\left(69 + 12 \\log_2\\left(\\frac{f_0}{440.0}\\right)\\right)", "2.23")

    md.add_p(doc, 
        "Tần số mục tiêu lý thuyết (Target Frequency) của nốt nhạc vừa tìm được là:", indent=0.4)
    md.add_equation(doc, "f_{\\text{target}} = 440.0 \\times 2^{\\frac{n_{\\text{MIDI}} - 69}{12}}", "2.24")

    md.add_p(doc, 
        "Tên nốt nhạc (Note Name) trong quãng tám và chỉ số quãng tám (Octave) được trích xuất trực tiếp từ n_MIDI:", indent=0.4)
    md.add_equation(doc, "\\text{note\\_idx} = n_{\\text{MIDI}} \\pmod{12}", "2.25")
    md.add_equation(doc, "\\text{octave} = \\left\\lfloor \\frac{n_{\\text{MIDI}}}{12} \\right\\rfloor - 1", "2.26")
    md.add_p(doc, 
        "Với mảng 12 tên nốt chuẩn: [C, C#, D, D#, E, F, F#, G, G#, A, A#, B]. Ví dụ: n = 60 cho note_idx = 0 (C), octave = 4 -> Nốt C4 (Middle C).", indent=0.4)

    # 2.13 Cents Deviation
    md.add_heading_2(doc, "2.13. Sai lệch Cent (Cents Deviation)")
    md.add_p(doc, 
        "Cent là đơn vị đo logarit phi tuyến được sử dụng trong âm nhạc để biểu thị tỷ lệ cao độ rất nhỏ giữa hai tần số âm thanh. "
        "Một nửa cung trong hệ âm 12-TET được định nghĩa chính xác bằng 100 cents, do đó một quãng tám (tỷ số 2:1) tương ứng với 1200 cents [2].", indent=0.4)

    md.add_p(doc, 
        "Độ sai lệch cent giữa tần số đo được f0 và tần số mục tiêu chuẩn f_target được tính bởi công thức:", indent=0.4)
    md.add_equation(doc, "\\text{cents} = 1200 \\log_2\\left(\\frac{f_0}{f_{\\text{target}}}\\right)", "2.27")

    md.add_p(doc, 
        "Ý nghĩa vật lý của giá trị cents:", indent=0.4)
    md.add_p(doc, 
        "• cents > 0: Tần số đo được cao hơn tần số chuẩn (dây đàn đang bị CĂNG / CAO - Sharp).", indent=0.4)
    md.add_p(doc, 
        "• cents < 0: Tần số đo được thấp hơn tần số chuẩn (dây đàn đang bị TRÙNG / THẤP - Flat).", indent=0.4)
    md.add_p(doc, 
        "• cents xấp xỉ 0 (thường quy ước trong phạm vi |cents| <= 3 đến 5 cents): Dây đàn đạt trạng thái CHUẨN CAO ĐỘ (IN TUNE) [2].", indent=0.4)

    # Bảng 2.1
    table_notes_data = [
        ("A4", "69", "440.000 Hz", "112.64", "Bin 113 (441.41 Hz)"),
        ("C4", "60", "261.626 Hz", "66.98", "Bin 67 (261.72 Hz)"),
        ("C5", "72", "523.251 Hz", "133.95", "Bin 134 (523.44 Hz)"),
        ("D3", "50", "146.832 Hz", "37.59", "Bin 38 (148.44 Hz)"),
        ("E3", "52", "164.814 Hz", "42.19", "Bin 42 (164.06 Hz)"),
        ("E2", "40", "82.407 Hz", "21.10", "Bin 21 (82.03 Hz)")
    ]
    md.add_custom_table(doc, 
        ["Nốt nhạc", "Số MIDI", "Tần số danh định f_target", "Chỉ số bin thực k", "Bin FFT nguyên gần nhất"],
        table_notes_data, [1.1, 1.0, 1.6, 1.2, 1.4],
        title="Bảng 2.1. Tần số danh định lý thuyết của các nốt nhạc kiểm thử (Equal Temperament, A4 = 440 Hz)")

    doc.add_page_break()

print("section_ch1_ch2 compiled successfully.")
