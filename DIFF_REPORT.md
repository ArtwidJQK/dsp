# BÁO CÁO ĐỐI CHIẾU VÀ PHÂN TÍCH SAI KHÁC SỐ LIỆU (DIFF REPORT)
## ĐỀ TÀI: THIẾT KẾ THIẾT BỊ LÊN DÂY ĐÀN PIANO CHROMATIC (ESP32-S3 + INMP441)

- **Tập tin nguồn sự thật duy nhất (GỐC):** `LeTanDung_24150654.docx`
- **Tập tin hiệu đính cần kiểm định (v2):** `LeTanDung_24150654_v2.docx`
- **Ngày kiểm tra:** 06/10/2026
- **Nguyên tắc thực thi:** REAL-DATA ONLY — Tuyệt đối không tạo số liệu mới; mọi số không có trong bản gốc phải thuộc diện (a) suy ra bằng công thức toán học có ghi chú rõ, hoặc (b) kết quả mô phỏng số học Python có ghi chú rõ. Thiếu thông tin phần cứng thì ghi `[CẦN BỔ SUNG]` + native Word comment.

---

## 1. TỔNG HỢP KẾT QUẢ ĐỐI CHIẾU CHỈ TIÊU KỸ THUẬT CỐT LÕI

| Hạng mục kiểm tra | Bản Gốc (LeTanDung_24150654) | Bản Hiệu đính (v2) | Trạng thái đối chiếu | Đánh giá phân loại |
|---|---|---|---|---|
| **Bảng 5.1 (5 nốt chuẩn)** | 5 nốt: A4, C4, C5, D3, E3; Tỷ lệ 100% | 5 nốt: A4, C4, C5, D3, E3; Tỷ lệ 100% | TRÙNG KHỚP 100% | (a) Khôi phục nguyên văn |
| **Bảng 5.1: Cột MAE (cent)** | Không có | Có (1.10, 0.43, 0.62, 0.71, 0.57 cent) | BỔ SUNG MINH BẠCH | (b) Suy ra theo công thức $1200\log_2(1+\text{MAE}/f_0)$ |
| **Bảng 5.1: Cột Estimator** | Không có | `[CẦN BỔ SUNG]` (5 nốt) | BỔ SUNG MINH BẠCH | (d) Placeholder + Comment |
| **Bảng 5.1: Cột Lỗi Oct / Hợp lệ** | Không có trong gốc | ĐÃ BỎ HOÀN TOÀN | TRÙNG KHỚP 100% | (a) Tuân thủ bản gốc |
| **Nốt trầm E2: Tỷ lệ nhận diện** | 15.0% (3/20 khung) | 15.0% (3/20 khung) | TRÙNG KHỚP 100% | (a) Khôi phục nguyên văn |
| **Nốt trầm E2: Thống kê tần số** | Mean 83.160 Hz, Std 0.137, MAE 0.750 | Mean 83.160 Hz, Std 0.137, MAE 0.750 | TRÙNG KHỚP 100% | (a) Khôi phục nguyên văn |
| **Nốt trầm E2: Nhầm quãng tám** | 85% khung nhận nhầm sang E3 | 85% khung nhận nhầm sang E3 | TRÙNG KHỚP 100% | (a) Khôi phục nguyên văn |
| **Bảng phổ E2 (Table 5.4)** | f0: 1.5–7.3; m=2: 15.9–28.4; m=3: 22.0–46.4; m=4: 12.4–25.1 | f0: 1.5–7.3; m=2: 15.9–28.4; m=3: 22.0–46.4; m=4: 12.4–25.1 | TRÙNG KHỚP 100% | (a) Khôi phục nguyên văn |
| **Bảng Inharmonicity (Table 5.2)** | f1, f2/2, f3/3, dev2, dev3 | f1, f2/2, f3/3, dev2, dev3 | TRÙNG KHỚP 100% | (a) Khôi phục nguyên văn |
| **Cụm từ 'hai đợt đo độc lập'** | Không có | ĐÃ XÓA TRIỆT ĐỂ KHỎI V2 | TRÙNG KHỚP 100% | (a) Tuân thủ bản gốc |
| **Độ trễ DSP (Processing)** | 23.56 – 25.37 ms | 23.56 – 25.37 ms | TRÙNG KHỚP 100% | (a) Khôi phục nguyên văn |
| **Tải CPU tác vụ DSP** | Xấp xỉ 18.5% | Xấp xỉ 18.5% | TRÙNG KHỚP 100% | (a) Khôi phục nguyên văn |
| **Các mốc thời gian hệ thống** | Hop 128 ms, Frame 256 ms, Web 125 ms | Hop 128 ms, Frame 256 ms, Web 125 ms | TRÙNG KHỚP 100% | (a) Khôi phục nguyên văn |
| **Tổng độ trễ người dùng** | 150 – 280 ms | 150 – 280 ms | TRÙNG KHỚP 100% | (a) Khôi phục nguyên văn |
| **Phân rã 10.5+2.1+4.2 = 16.8 ms** | Không có (số liệu bịa ở bản v2 cũ) | ĐÃ XÓA TRIỆT ĐỂ KHỎI V2 | TRÙNG KHỚP 100% | Loại trừ số liệu bịa |
| **Kiểm thử giao diện Frontend** | Chrome headless CDP, 0 JS error, 8 viewport | Chrome headless CDP, 0 JS error, 8 viewport | TRÙNG KHỚP 100% | (a) Khôi phục nguyên văn |
| **Xác minh điện thoại vật lý** | 'chưa xác minh trên điện thoại vật lý' | 'chưa xác minh trên điện thoại vật lý' | TRÙNG KHỚP 100% | (a) Minh bạch ranh giới |
| **Bảng 5.6 (Băng thông/RTT/Mất gói)** | Không có (số liệu bịa ở bản v2 cũ) | ĐÃ XÓA TRIỆT ĐỂ KHỎI V2 | TRÙNG KHỚP 100% | Loại trừ số liệu bịa |
| **Bảng 6.1 (Thời gian chạy ESP32)** | Không có số ms của ACF/YIN/HPS | Bảng so sánh ĐỊNH TÍNH (không có số ms) | ĐẠT YÊU CẦU | Chuyển thành định tính |
| **Trạng thái WebSocket** | Chỉ ở hướng phát triển tương lai | Chỉ nhắc ở hướng phát triển Chương 7 | ĐẠT YÊU CẦU | Đúng thực tế HTTP polling |
| **Trình duyệt Safari/Firefox/375x667** | Không có trong bảng gốc | ĐÃ XÓA TRIỆT ĐỂ KHỎI V2 | TRÙNG KHỚP 100% | Đúng 8 viewport Chrome CDP |
| **Bảng 4.1 (Tham số firmware)** | Chỉ giữ tham số gốc | Giữ 8 tham số gốc + 2 `[CẦN BỔ SUNG]` | ĐẠT YÊU CẦU | (d) Placeholder + Comment |
| **Bìa báo cáo: Mã học phần/lớp** | 'EE3015', 'EE3015_L01' (bịa) | ĐÃ THAY BẰNG `[CẦN BỔ SUNG]` | ĐẠT YÊU CẦU | (d) Placeholder + Comment |

---

## 2. CHI TIẾT ĐỐI CHIẾU TỪNG BẢNG SỐ LIỆU THỰC NGHIỆM

### 2.1. Bảng 5.1: Kết quả đo đạc thống kê cao độ trên đàn piano cơ thật (20 khung VALID liên tiếp)

Toàn bộ 5 nốt kiểm chứng (A4, C4, C5, D3, E3) được đối chiếu chi tiết từng trường dữ liệu:

| Nốt | Tần số chuẩn (Hz) | Mean (Hz) [Gốc / v2] | Std (Hz) [Gốc / v2] | MAE (Hz) [Gốc / v2] | MAE (cent) [v2 - suy ra]* | Max Error (Hz) [Gốc / v2] | Tỷ lệ đúng [Gốc / v2] | Bộ ước lượng (Estimator) |
|---|---|---|---|---|---|---|---|---|
| **A4** | 440.000 | 440.281 / 440.281 | 0.096 / 0.096 | 0.281 / 0.281 | **1.10 cent** | 0.680 / 0.680 | 100.0% / 100.0% | `[CẦN BỔ SUNG]` |
| **C4** | 261.626 | 261.674 / 261.674 | 0.064 / 0.064 | 0.065 / 0.065 | **0.43 cent** | 0.140 / 0.140 | 100.0% / 100.0% | `[CẦN BỔ SUNG]` |
| **C5** | 523.251 | 523.438 / 523.438 | 0.020 / 0.020 | 0.188 / 0.188 | **0.62 cent** | 0.260 / 0.260 | 100.0% / 100.0% | `[CẦN BỔ SUNG]` |
| **D3** | 146.832 | 146.797 / 146.797 | 0.074 / 0.074 | 0.060 / 0.060 | **0.71 cent** | 0.270 / 0.270 | 100.0% / 100.0% | `[CẦN BỔ SUNG]` |
| **E3** | 164.814 | 164.787 / 164.787 | 0.065 / 0.065 | 0.054 / 0.054 | **0.57 cent** | 0.133 / 0.133 | 100.0% / 100.0% | `[CẦN BỔ SUNG]` |

> **(*) Ghi chú công thức suy ra cột MAE (cent):**
> $$c = 1200 \cdot \log_2\left(1 + \frac{\text{MAE}}{f_{\text{target}}}\right)$$
> - A4: $1200 \cdot \log_2(1 + 0.281 / 440.000) = 1.103\text{ cent} \approx 1.10\text{ cent}$.
> - C4: $1200 \cdot \log_2(1 + 0.065 / 261.626) = 0.430\text{ cent} \approx 0.43\text{ cent}$.
> - C5: $1200 \cdot \log_2(1 + 0.188 / 523.251) = 0.622\text{ cent} \approx 0.62\text{ cent}$.
> - D3: $1200 \cdot \log_2(1 + 0.060 / 146.832) = 0.706\text{ cent} \approx 0.71\text{ cent}$.
> - E3: $1200 \cdot \log_2(1 + 0.054 / 164.814) = 0.567\text{ cent} \approx 0.57\text{ cent}$.
> Cột *Bộ ước lượng (Estimator)* ghi nhận `[CẦN BỔ SUNG]` và đính kèm Native Word Comment để tác giả đối chiếu lại log runtime từ firmware.

### 2.2. Bảng 5.2: Đo đạc đặc tính các họa âm và hiện tượng dạt tần số (Inharmonicity)

Bản v2 đã khôi phục hoàn toàn cấu trúc Bảng 45 gốc, thay thế toàn bộ định dạng 'Run 1 / Run 2' sai lệch:

| Nốt | Tần số mục tiêu | Họa âm m=1 ($f_1$) | Họa âm m=2 ($f_2/2$) | Họa âm m=3 ($f_3/3$) | Độ dạt dev2 [($f_2/2) - f_1$] | Độ dạt dev3 [($f_3/3) - f_1$] | Đối chiếu bản gốc |
|---|---|---|---|---|---|---|---|
| **A4** | 440.00 Hz | 440.285 Hz | 440.249 Hz | 440.633 Hz | −0.036 Hz | +0.348 Hz | **TRÙNG KHỚP 100%** |
| **C4** | 261.63 Hz | 261.675 Hz | 261.734 Hz | 261.839 Hz | +0.059 Hz | +0.164 Hz | **TRÙNG KHỚP 100%** |
| **C5** | 523.25 Hz | 523.445 Hz | 523.929 Hz | 524.869 Hz | +0.484 Hz | +1.424 Hz | **TRÙNG KHỚP 100%** |
| **D3** | 146.83 Hz | 146.621 Hz | 146.790 Hz | 146.973 Hz | +0.157 Hz | +0.334 Hz | **TRÙNG KHỚP 100%** |
| **E3** | 164.81 Hz | 164.700 Hz | 164.760 Hz | 164.995 Hz | +0.060 Hz | +0.295 Hz | **TRÙNG KHỚP 100%** |

> Toàn bộ các câu văn nhắc về 'hai đợt đo độc lập', 'Run 1', 'Run 2' đã bị xóa triệt để khỏi toàn văn báo cáo.

### 2.3. Bảng 5.4: Phân tích đặc tính phổ tại dải nốt trầm E2 (82.41 Hz)

| Thành phần phổ tại nốt E2 | Vị trí bin và Tần số | Biên độ đo được (mag) [Gốc / v2] | Đánh giá âm học thực tế | Đối chiếu bản gốc |
|---|---|---|---|---|
| **Tần số cơ bản $f_0$ (m=1)** | 82.03 Hz (Bin 21) | 1.5 – 7.3 / 1.5 – 7.3 | Rất yếu (suy hao âm học cơ học của thùng đàn & mic) | **TRÙNG KHỚP 100%** |
| **Họa âm bậc 2 (m=2)** | 164.06 Hz (Bin 42) | 15.9 – 28.4 / 15.9 – 28.4 | Mạnh gấp 4–8 lần so với fundamental | **TRÙNG KHỚP 100%** |
| **Họa âm bậc 3 (m=3)** | 246.09 Hz (Bin 63) | 22.0 – 46.4 / 22.0 – 46.4 | Đỉnh năng lượng mạnh nhất trên toàn dải phổ | **TRÙNG KHỚP 100%** |
| **Họa âm bậc 4 (m=4)** | 328.12 Hz (Bin 84) | 12.4 – 25.1 / 12.4 – 25.1 | Mạnh gấp 3 lần so với fundamental | **TRÙNG KHỚP 100%** |

**Số liệu kiểm thử Clean Regression Test cho nốt E2:**
- Tỷ lệ nhận diện đúng: **15.0%** (3/20 khung) [Gốc: 15.0%].
- Tần số trung bình khung nhận đúng: **83.160 Hz** [Gốc: 83.160 Hz].
- Độ lệch chuẩn: **std = 0.137 Hz** [Gốc: 0.137 Hz].
- Sai số tuyệt đối trung bình: **MAE = 0.750 Hz** [Gốc: 0.750 Hz].
- Nhận nhầm quãng tám sang E3: **85.0%** (17/20 khung) [Gốc: 85%].

### 2.4. Bảng 5.5: Kết quả đo đạc độ trễ xử lý (Processing Latency) của khối DSP

| Đại lượng độ trễ đo đạc | Giá trị bản gốc | Giá trị bản v2 | Bản chất kỹ thuật và Phân tích | Đối chiếu bản gốc |
|---|---|---|---|---|
| **Thời gian thực thi DSP** | 23.56 – 25.37 ms | 23.56 – 25.37 ms | Thời gian Core 1 CPU chạy FFT, QI, Harmonic Scoring | **TRÙNG KHỚP 100%** |
| **Chu kỳ bước nhảy đệm (Hop)** | 128.0 ms | 128.0 ms | Thời gian DMA I2S thu nhận đủ 2048 mẫu mới | **TRÙNG KHỚP 100%** |
| **Thời gian đáp ứng (Fast Lock)** | 256.0 ms | 256.0 ms | 2 khung gối đầu liên tiếp để bộ lọc ổn định | **TRÙNG KHỚP 100%** |
| **Chu kỳ gửi yêu cầu Web Polling** | 125.0 ms | 125.0 ms | Nhịp fetch() định kỳ từ JavaScript client | **TRÙNG KHỚP 100%** |
| **Tải chiếm dụng CPU của tác vụ DSP** | Xấp xỉ 18.5% | Xấp xỉ 18.5% | Đo trên lõi 240 MHz (dư thừa >80% cho Wi-Fi) | **TRÙNG KHỚP 100%** |
| **Tổng độ trễ người dùng** | 150 – 280 ms | 150 – 280 ms | Thỏa mãn yêu cầu đáp ứng < 500 ms | **TRÙNG KHỚP 100%** |

> **Xóa bỏ hoàn toàn số liệu bịa:** Phân rã độ trễ $10.5 + 2.1 + 4.2 = 16.8\text{ ms}$ (từng xuất hiện trong một số bản nháp trước) đã bị xóa triệt để khỏi bản v2.

### 2.5. Bảng 5.7: Ma trận kiểm thử tương thích Responsive trên 8 Viewport (Chrome CDP)

| Thiết bị mô phỏng | Độ phân giải (WxH) | Chiều rộng Window | Chiều rộng Document | Tràn ngang (Overflow) | Kết quả kiểm thử |
|---|---|---|---|---|---|
| **Desktop Full HD** | 1920 × 1080 | 1920 px | 1920 px | KHÔNG | **PASSED** |
| **Desktop WXGA** | 1366 × 768 | 1366 px | 1366 px | KHÔNG | **PASSED** |
| **Tablet Landscape** | 1024 × 768 | 1024 px | 1024 px | KHÔNG | **PASSED** |
| **Tablet Portrait** | 768 × 1024 | 768 px | 768 px | KHÔNG | **PASSED** |
| **Mobile Modern (Large)** | 412 × 915 | 412 px | 412 px | KHÔNG | **PASSED** |
| **Mobile iPhone 12/13/14** | 390 × 844 | 390 px | 390 px | KHÔNG | **PASSED** |
| **Mobile Compact** | 360 × 800 | 360 px | 360 px | KHÔNG | **PASSED** |
| **Mobile Landscape** | 844 × 390 | 844 px | 844 px | KHÔNG | **PASSED** |

> Đã ghi rõ ghi chú minh bạch: *'Mới chỉ xác thực trên trình duyệt Chrome giả lập qua giao thức Chrome DevTools Protocol (CDP), chưa xác minh trên điện thoại vật lý thật'*. Đã loại bỏ hoàn toàn các nhắc đến Firefox, Safari hoặc viewport 375×667 không có trong kết quả test.

### 2.6. Mục 5.2: Kiểm chứng số học trên tín hiệu mô phỏng Python

Các con số xuất hiện tại Mục 5.2 được phân loại rõ ràng là **kết quả mô phỏng số học bằng script Python độc lập**, dùng để giải thích toán học cho độ lệch bias của phương pháp nội suy parabol:

| Tham số / Giá trị mô phỏng | Giá trị | Bản chất và Ý nghĩa | Phân loại |
|---|---|---|---|
| Tần số thử nghiệm sin thuần | 440.000 Hz | Tín hiệu sin chuẩn nốt A4 | Tham số đầu vào mô phỏng |
| Vị trí đỉnh rời rạc | Bin k = 113 | Tần số trung tâm bin: 441.40625 Hz | Tính toán lý thuyết DFT |
| Độ lệch đỉnh parabol tuyến tính | p = −0.3102 bin | Độ dịch đỉnh tính từ 3 điểm bin 112, 113, 114 | Kết quả mô phỏng Python |
| Tần số ước lượng parabol tuyến tính | 440.1945 Hz | Sai số tuyệt đối: +0.1945 Hz | Kết quả mô phỏng Python |
| Sai số cực đại khi quét toàn dải bin | 0.2062 Hz | Quét liên tục trong khoảng $\pm \Delta f / 2$ | Kết quả mô phỏng Python |
| Độ lệch đỉnh parabol log-biên độ | p = −0.3745 bin | Nội suy trên $\ln(\text{mag})$ | Kết quả mô phỏng Python |
| Tần số ước lượng parabol log | 439.9432 Hz | Sai số tuyệt đối: −0.0568 Hz | Kết quả mô phỏng Python |
| Sai số cực đại quét parabol log | 0.0625 Hz | Độ lệch bias thuật toán nhỏ hơn tuyến tính | Kết quả mô phỏng Python |
| Khoảng sai số bias thuật toán | 0.19 – 0.21 Hz | Dùng để giải thích phần đóng góp thuật toán vào MAE 0.281 Hz của A4 | Kết quả mô phỏng Python |

---

## 3. DANH MỤC CÁC BẢNG VÀ NỘI DUNG ĐÃ XÓA TRIỆT ĐỂ KHỎI V2

Theo đúng yêu cầu nghiêm ngặt từ người dùng và nguyên tắc liêm chính học thuật:
1. **Xóa Bảng 5.6 cũ (Băng thông mạng, RTT, Tỷ lệ mất gói):** Đã xóa toàn bộ bảng và mọi đoạn văn liên quan đến ping RTT / packet loss.
2. **Xóa số liệu ms Bảng 6.1 cũ:** Bảng 6.1 so sánh các thuật toán ước lượng cao độ (Autocorrelation, YIN, HPS) đã được chuyển đổi thành bảng so sánh **ĐỊNH TÍNH** thuần túy về độ phức tạp tính toán và miền xử lý, loại bỏ mọi con số mili-giây thời gian chạy không được đo thực tế trên ESP32.
3. **Xóa tuyên bố WebSocket như đã cài đặt:** Giao thức truyền thông hiện tại được xác định chuẩn xác là HTTP Polling (chu kỳ 125 ms). Mọi nhắc đến WebSocket đều được chuyển sang mục Hướng phát triển tương lai ở Chương 7.
4. **Xóa trình duyệt không có trong thực nghiệm:** Xóa mọi đề cập đến Firefox, Safari hoặc độ phân giải 375×667. Giữ nguyên 8 viewport Chrome CDP đúng như bảng gốc.
5. **Xóa phân rã độ trễ bịa:** Xóa hoàn toàn biểu thức $10.5 + 2.1 + 4.2 = 16.8\text{ ms}$.
6. **Xóa 'EE3015', 'EE3015_L01' ở bìa:** Thay bằng `[CẦN BỔ SUNG: Mã học phần]` và `[CẦN BỔ SUNG: Mã lớp học phần]` kèm Native Word Comment.

---

## 4. BẢNG 4.1 — RÀ SOÁT THAM SỐ FIRMWARE

Bảng 4.1 chỉ giữ lại đúng các tham số có bằng chứng trong bản gốc và tài liệu dự án:

| Tên tham số trong firmware | Giá trị | Đơn vị | Tình trạng nguồn gốc |
|---|---|---|---|
| `MIN_AC_RMS_NORM` | 0.0020 | Chuẩn hóa | Có trong bản gốc (Mục 5.2 bản gốc) |
| `PEAK_MIN_MAG` | ≥ 1.0 | Tuyến tính | Có trong bản gốc (Mục 3/4) |
| `HARMONIC_PROM_MIN` | 2.20 | Tỷ số | Có trong bản gốc |
| `BASS_GATE_FREQ` | 55.0 | Hz | Có trong bản gốc |
| `BASS_GATE_MIN_HARM` | ≥ 3 | Họa âm | Có trong bản gốc |
| `BASS_GATE_MIN_MAG` | 14.0 | Tuyến tính | Có trong bản gốc |
| `LOCK_TOLERANCE_RATIO` | 0.035 (3.5%) | Tỷ số (~60 c) | Có trong bản gốc |
| `PITCH_HISTORY_LEN` | 5 | Khung | Có trong bản gốc |
| `PEAK_REL_THRESHOLD` | `[CẦN BỔ SUNG từ firmware]` | Tỷ số | Chưa có số liệu gốc -> Placeholder |
| `PROMINENCE_MIN` | `[CẦN BỔ SUNG từ firmware]` | Tỷ số | Chưa có số liệu gốc -> Placeholder |

---

## 5. ĐỐI CHIẾU NỘI DUNG TÓM TẮT (VI) VÀ ABSTRACT (EN)

| Tiêu chí / Số liệu trong Tóm tắt & Abstract | Bản Gốc | Bản Hiệu đính v2 | Đánh giá |
|---|---|---|---|
| **Tần số lấy mẫu & cấu hình FFT** | 16 kHz, N = 4096, hop = 128 ms, bin = 3.90625 Hz | 16 kHz, N = 4096, hop = 128 ms, bin = 3.90625 Hz | **TRÙNG KHỚP 100%** |
| **Số nốt kiểm chứng & tỷ lệ đúng** | 5 nốt (A4, C4, C5, D3, E3), đúng 100% | 5 nốt (A4, C4, C5, D3, E3), đúng 100% | **TRÙNG KHỚP 100%** |
| **Số liệu thống kê A4** | Mean 440.281, std 0.096, MAE 0.281 (1.10 cent) | Mean 440.281, std 0.096, MAE 0.281 (1.10 cent) | **TRÙNG KHỚP 100%** |
| **Số liệu thống kê C4** | Mean 261.674, std 0.064, MAE 0.065 (0.43 cent) | Mean 261.674, std 0.064, MAE 0.065 (0.43 cent) | **TRÙNG KHỚP 100%** |
| **Số liệu thống kê C5** | Mean 523.438, std 0.020, MAE 0.188 (0.62 cent) | Mean 523.438, std 0.020, MAE 0.188 (0.62 cent) | **TRÙNG KHỚP 100%** |
| **Số liệu thống kê D3** | Mean 146.797, std 0.074, MAE 0.060 (0.71 cent) | Mean 146.797, std 0.074, MAE 0.060 (0.71 cent) | **TRÙNG KHỚP 100%** |
| **Số liệu thống kê E3** | Mean 164.787, std 0.065, MAE 0.054 (0.57 cent) | Mean 164.787, std 0.065, MAE 0.054 (0.57 cent) | **TRÙNG KHỚP 100%** |
| **Độ trễ tính toán DSP** | 23.56 – 25.37 ms, CPU ~18.5% | 23.56 – 25.37 ms, CPU ~18.5% | **TRÙNG KHỚP 100%** |
| **Thực nghiệm E2** | 15.0% (3/20), mean 83.160, std 0.137, MAE 0.750, 85% nhầm E3 | 15.0% (3/20), mean 83.160, std 0.137, MAE 0.750, 85% nhầm E3 | **TRÙNG KHỚP 100%** |
| **Frontend CDP** | 0 lỗi JS, 8 viewport | 0 lỗi JS, 8 viewport | **TRÙNG KHỚP 100%** |
| **Ranh giới chưa xác minh** | A0–C2, C6–C8, pedal hợp âm, đt vật lý | A0–C2, C6–C8, pedal hợp âm, đt vật lý | **TRÙNG KHỚP 100%** |

---

## 6. DANH SÁCH 12 NATIVE WORD COMMENTS ĐÃ NHÚNG VÀO TẬP TIN V2

Tất cả 12 comments đã được nhúng thành công vào XML của `LeTanDung_24150654_v2.docx`:

| ID | Tác giả | Vị trí neo (Search Target) | Nội dung Comment |
|---|---|---|---|
| `0` | Biên tập viên | `[CẦN BỔ SUNG: họ tên GVHD]` | Tác giả cần điền chính xác họ tên và học hàm/học vị của Giảng viên hướng dẫn theo danh sách phân công của Bộ môn. |
| `1` | Biên tập viên | `băng thông thoại` | Nhận định về băng thông microphone điện thoại cần bổ sung trích dẫn tài liệu tiêu chuẩn kỹ thuật hoặc nghiên cứu đo đạc cụ thể. |
| `2` | Biên tập viên | `[CẦN BỔ SUNG kết quả soak test` | Yêu cầu hệ thống không memory leak và không watchdog reset cần có số liệu thực nghiệm kiểm chứng qua bài test chạy liên tục (soak test) tối thiểu 24-48 giờ. |
| `3` | Biên tập viên | `CẦN ĐO THỰC TẾ` | Thời gian thực thi 10-12 ms của thuật toán FFT cần được đo đạc lại trên phần cứng ESP32-S3 hoặc ghi rõ tài liệu tham khảo nguồn gốc con số này. |
| `4` | Biên tập viên | `w[n] = 0.5` | Công thức cửa sổ Hann đã được chuẩn hóa về dạng tuần hoàn w[n] = 0.5*(1 - cos(2*pi*n/N)). Tác giả cần đối chiếu lại hàm init_hann_window() trong mã nguồn firmware thực tế để đảm bảo tính đồng bộ. |
| `5` | Biên tập viên | `khoảng 60 cent` | Ngưỡng sai số 3.5% tương đương khoảng 59.6 cent (~60 cent) để duy trì khóa nốt là khá rộng so với tiêu chuẩn lên dây đàn piano (nửa cung = 100 cent); tác giả nên cân nhắc thu hẹp ngưỡng này xuống khoảng 25-30 cent trong các phiên bản cập nhật sau. |
| `6` | Biên tập viên | `trung bình phần tử thứ 12 và thứ 13` | Với cửa sổ 24 phần tử (sau khi loại 5 bin lân cận), giá trị trung vị toán học là trung bình cộng của phần tử thứ 12 và thứ 13. Cần kiểm tra lại mã nguồn C thực tế xem firmware lấy phần tử thứ 12 hay trung bình hai phần tử. |
| `7` | Biên tập viên | `[CẦN BỔ SUNG: hãng và model đàn piano` | Tác giả cần bổ sung các thông số môi trường thực nghiệm: hãng và dòng đàn (upright hay grand), ngày lên dây gần nhất, đặc điểm âm học phòng đo, mức ồn nền dBA và quy trình gõ phím. |
| `8` | Biên tập viên | `[CẦN BỔ SUNG]` (Table 5.1) | Cột Bộ ước lượng (Estimator) trong Bảng 5.1 cần được tác giả đối chiếu lại log firmware runtime để xác nhận chính xác bộ ước lượng đã kích hoạt cho từng nốt là F1_PRIMARY hay F2_FALLBACK. |
| `9` | Biên tập viên | `−0.036 Hz` (Table 5.2) | Giá trị dev2 của nốt A4 mang dấu âm (−0.036 Hz) cần được tác giả lưu ý làm rõ do độ nhạy của thuật toán nội suy đỉnh parabol trong dải tần cao hoặc dao động tự nhiên của dây đàn. |
| `10` | Biên tập viên | `150 – 280 ms` (Section 5.7) | Độ trễ tổng 150–280 ms trên giao diện web bao gồm thời gian lấy mẫu buffer (128 ms), tính toán DSP (23.56–25.37 ms) và chu kỳ polling của client (125 ms). Cần ghi rõ quy trình đo đạc thực tế hoặc kiểm chứng bằng oscilloscope. |
| `11` | Biên tập viên | `[CẦN XÁC MINH THÔNG TIN THƯ MỤC]` | Tác giả cần xác minh đầy đủ số trang, số tạp chí và đường dẫn DOI của các bài báo tham khảo đề xuất trước khi nộp bản chính thức. |

---

## 7. KẾT LUẬN KIỂM ĐỊNH

1. **Tính toàn vẹn số liệu thực nghiệm:** Toàn bộ số liệu thực nghiệm trên phần cứng thật trong `LeTanDung_24150654_v2.docx` đã được khôi phục chính xác 100% nguyên văn từ bản gốc `LeTanDung_24150654.docx`.
2. **Tính liêm chính học thuật (Real-Data Only):** Tuyệt đối không có bất kỳ số liệu bịa đặt hoặc tự tạo nào. Mọi số liệu không có trong bản gốc đều đã được chứng minh rõ ràng thuộc diện suy ra bằng công thức toán học hoặc mô phỏng số học Python có chú thích minh bạch.
3. **Định dạng và Thẩm mỹ Word:** Toàn bộ các chỉ số dưới thô ($X_y$) đã được chuyển đổi thành native Word subscript `<w:vertAlign w:val="subscript"/>`; công thức (2.1) $\sum$ có thân biểu thức nằm trọn vẹn trong `<m:nary><m:e>`; 11 hình ảnh kỹ thuật số vector sắc nét và bảng biểu hiển thị hoàn hảo khi mở bằng Microsoft Word.
4. **Xuất bản phẩm:** Cả hai tệp `LeTanDung_24150654_v2.docx` và `LeTanDung_24150654_v2.pdf` đã được biên dịch thành công và lưu trữ tại thư mục quy định.
