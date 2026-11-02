# NHẬT KÝ THAY ĐỔI TOÀN DIỆN (CHANGELOG)
## BÁO CÁO TIỂU LUẬN KỸ THUẬT: PIANO CHROMATIC TUNER SỬ DỤNG ESP32-S3 VÀ INMP441
**Mã sinh viên / Tác giả:** Lê Tấn Dũng (MSSV: 24150654)  
**Tập tin nguồn sự thật duy nhất (GỐC):** `LeTanDung_24150654.docx`  
**Tập tin hiệu đính hoàn thiện:** `LeTanDung_24150654_v2.docx` & `LeTanDung_24150654_v2.pdf`  
**Báo cáo sai khác số liệu:** `DIFF_REPORT.md`  
**Danh mục mục mở:** `OPEN_ITEMS.md`  
**Ngày thực hiện:** 06/10/2026  
**Vai trò hiệu đính:** Biên tập viên kỹ thuật kiêm Chuyên gia định dạng Word & Kỹ sư DSP/Hệ thống nhúng  

---

### TỔNG QUAN HIỆU ĐÍNH THEO NGUYÊN TẮC REAL-DATA ONLY
Bản hiệu đính `v2` được rà soát và tái cấu trúc nghiêm ngặt dựa trên nguyên tắc **BẢN GỐC LÀ NGUỒN SỰ THẬT DUY NHẤT VỀ SỐ LIỆU (SINGLE SOURCE OF TRUTH)**:
1. **Tuyệt đối không bịa đặt số liệu:** Giữ nguyên vẹn cấu trúc, định dạng chuẩn mực, 31 công thức toán học OMML và 11 đồ họa kỹ thuật vector của bản v2; đồng thời loại bỏ toàn bộ các số liệu tự tạo xuất hiện trong các bản nháp trước.
2. **Khôi phục nguyên văn 100% số liệu thực nghiệm từ bản gốc:** Toàn bộ dữ liệu đo đạc trên đàn piano cơ thật tại Bảng 5.1, Bảng 5.2, Bảng 5.4, Bảng 5.5, Bảng 5.7 và kết quả kiểm thử Chrome CDP được đối chiếu chính xác từng con số với bản gốc `LeTanDung_24150654.docx`.
3. **Mọi số liệu không có trong bản gốc phải thuộc diện:**
   - (a) **Suy ra bằng công thức toán học từ dữ liệu gốc:** Ghi chú minh bạch nguồn gốc và công thức tính (ví dụ: cột MAE cent suy ra từ $1200\log_2(1 + \text{MAE}/f_{\text{target}})$, ngưỡng khóa nốt 3.5% quy đổi ~59.6 cent).
   - (b) **Kết quả mô phỏng số học bằng script Python:** Ghi chú rõ là mô phỏng toán học trên tín hiệu sin thuần túy để phân tích độ lệch bias của thuật toán nội suy parabol (Mục 5.2).
   - Nếu không thuộc hai diện trên thì bắt buộc xóa bỏ hoặc ghi nhận `[CẦN BỔ SUNG]` kèm Native Word Comment.

---

### MỤC 1: KHÔI PHỤC VÀ ĐỒNG BỘ HÓA SỐ LIỆU THỰC NGHIỆM CHƯƠNG 5

1. **Bảng 5.1 (Khôi phục nguyên văn 5 nốt kiểm chứng):**
   - Chỉ giữ đúng 5 nốt đại diện thuộc dải trung âm và cận trầm đã được xác thực thực tế trên đàn piano cơ thật: **A4, C4, C5, D3, E3**.
   - Khôi phục chính xác từng giá trị:
     - **A4:** Tần số chuẩn 440.000 Hz, Mean 440.281 Hz, Std 0.096 Hz, MAE 0.281 Hz, Max Error 0.680 Hz, Tỷ lệ đúng 100.0%.
     - **C4:** Tần số chuẩn 261.626 Hz, Mean 261.674 Hz, Std 0.064 Hz, MAE 0.065 Hz, Max Error 0.140 Hz, Tỷ lệ đúng 100.0%.
     - **C5:** Tần số chuẩn 523.251 Hz, Mean 523.438 Hz, Std 0.020 Hz, MAE 0.188 Hz, Max Error 0.260 Hz, Tỷ lệ đúng 100.0%.
     - **D3:** Tần số chuẩn 146.832 Hz, Mean 146.797 Hz, Std 0.074 Hz, MAE 0.060 Hz, Max Error 0.270 Hz, Tỷ lệ đúng 100.0%.
     - **E3:** Tần số chuẩn 164.814 Hz, Mean 164.787 Hz, Std 0.065 Hz, MAE 0.054 Hz, Max Error 0.133 Hz, Tỷ lệ đúng 100.0%.
   - **Bổ sung cột MAE (cent) có ghi chú suy ra minh bạch:**
     - A4: $1200 \cdot \log_2(1 + 0.281 / 440.000) = 1.10\text{ cent}$.
     - C4: $1200 \cdot \log_2(1 + 0.065 / 261.626) = 0.43\text{ cent}$.
     - C5: $1200 \cdot \log_2(1 + 0.188 / 523.251) = 0.62\text{ cent}$.
     - D3: $1200 \cdot \log_2(1 + 0.060 / 146.832) = 0.71\text{ cent}$.
     - E3: $1200 \cdot \log_2(1 + 0.054 / 164.814) = 0.57\text{ cent}$.
   - **Bổ sung cột Bộ ước lượng (Estimator):** Ghi rõ `[CẦN BỔ SUNG]` cho cả 5 nốt kèm Native Word Comment để tác giả đối chiếu lại log runtime từ firmware ESP32-S3.
   - **Xóa bỏ các cột không có trong bản gốc:** Bỏ hoàn toàn cột "Lỗi Oct" và cột "Hợp lệ" vốn không tồn tại trong Bảng 5.1 gốc.

2. **Khôi phục thực nghiệm nốt trầm E2 (82.41 Hz):**
   - Đưa số liệu kiểm thử nốt trầm E2 về đúng mục riêng biệt (Mục 5.6):
     - Tỷ lệ nhận diện đúng trong bài Clean Regression Test: **15.0%** (3/20 khung).
     - Tần số trung bình khung nhận đúng: **83.160 Hz**, Std **0.137 Hz**, MAE **0.750 Hz**.
     - Tỷ lệ nhận nhầm quãng tám sang nốt E3 (~164.81 Hz): **85.0%** (17/20 khung).
   - **Bảng 5.4 (Đặc tính phổ E2):** Khôi phục nguyên văn Bảng 46 bản gốc:
     - Tần số cơ bản $f_0$ (Bin 21, 82.03 Hz): Biên độ **1.5 – 7.3** (Rất yếu do suy hao cơ học thùng đàn và mic).
     - Họa âm bậc 2 $m=2$ (Bin 42, 164.06 Hz): Biên độ **15.9 – 28.4** (Mạnh gấp 4–8 lần fundamental).
     - Họa âm bậc 3 $m=3$ (Bin 63, 246.09 Hz): Biên độ **22.0 – 46.4** (Đỉnh năng lượng mạnh nhất trên toàn phổ).
     - Họa âm bậc 4 $m=4$ (Bin 84, 328.12 Hz): Biên độ **12.4 – 25.1** (Mạnh gấp 3 lần fundamental).

3. **Bảng 5.2 (Khôi phục nguyên văn Bảng Inharmonicity gốc):**
   - Thay thế toàn bộ định dạng "Run 1 / Run 2" bằng bảng đo đạc đặc tính họa âm và hiện tượng dạt tần số (Inharmonicity) đúng như Bảng 45 gốc:
     - Các cột: Nốt | Mục tiêu | Họa âm m=1 ($f_1$) | Họa âm m=2 ($f_2/2$) | Họa âm m=3 ($f_3/3$) | Độ dạt dev2 [($f_2/2) - f_1$] | Độ dạt dev3 [($f_3/3) - f_1$].
     - A4: $f_1 = 440.285$, $f_2/2 = 440.249$, $f_3/3 = 440.633$, $\text{dev2} = -0.036\text{ Hz}$, $\text{dev3} = +0.348\text{ Hz}$.
     - C4: $f_1 = 261.675$, $f_2/2 = 261.734$, $f_3/3 = 261.839$, $\text{dev2} = +0.059\text{ Hz}$, $\text{dev3} = +0.164\text{ Hz}$.
     - C5: $f_1 = 523.445$, $f_2/2 = 523.929$, $f_3/3 = 524.869$, $\text{dev2} = +0.484\text{ Hz}$, $\text{dev3} = +1.424\text{ Hz}$.
     - D3: $f_1 = 146.621$, $f_2/2 = 146.790$, $f_3/3 = 146.973$, $\text{dev2} = +0.157\text{ Hz}$, $\text{dev3} = +0.334\text{ Hz}$.
     - E3: $f_1 = 164.700$, $f_2/2 = 164.760$, $f_3/3 = 164.995$, $\text{dev2} = +0.060\text{ Hz}$, $\text{dev3} = +0.295\text{ Hz}$.
   - **Xóa triệt để mọi câu văn về "hai đợt đo độc lập":** Loại bỏ các luận điểm tự tạo về việc đo hai lần độc lập để giải thích sai lệch tần số.

4. **Bảng 5.5 & Đo đạc độ trễ xử lý (Processing Latency):**
   - Khôi phục chính xác các mốc thời gian thực nghiệm:
     - Thời gian thực thi DSP: **23.56 – 25.37 ms** (đo bằng `esp_timer`).
     - Tải chiếm dụng CPU của tác vụ DSP: **Xấp xỉ 18.5%**.
     - Chu kỳ bước nhảy đệm (Hop Interval): **128.0 ms** (2048 mẫu I2S DMA mới).
     - Thời gian đáp ứng nốt tối thiểu (Fast Lock): **256.0 ms** (2 khung gối đầu liên tiếp).
     - Chu kỳ gửi yêu cầu Web Polling: **125.0 ms** (mã fetch JS định kỳ).
     - Tổng độ trễ phản hồi người dùng: **150 – 280 ms** (< 500 ms yêu cầu).
   - **Xóa bỏ hoàn toàn phân rã độ trễ bịa:** Loại bỏ công thức $10.5 + 2.1 + 4.2 = 16.8\text{ ms}$ không có trong dữ liệu phần cứng.

5. **Bảng 5.7 & Kiểm thử giao diện Frontend:**
   - Khôi phục nguyên văn kết quả kiểm thử tự động bằng Chrome DevTools Protocol (CDP) trên **8 Viewport tiêu chuẩn**:
     - Desktop Full HD (1920×1080), Desktop WXGA (1366×768), Tablet Landscape (1024×768), Tablet Portrait (768×1024), Mobile Modern (412×915), iPhone 12/13/14 (390×844), Mobile Compact (360×800), Mobile Landscape (844×390) — Tất cả đều **PASSED**, 0 lỗi JavaScript Console.
   - Ghi chú minh bạch: *"Mới chỉ xác thực trên trình duyệt Chrome giả lập qua giao thức CDP, chưa xác minh trên điện thoại vật lý thật"*.
   - **Xóa bỏ hoàn toàn:** Các trình duyệt Safari, Firefox và độ phân giải 375×667 không có trong kết quả đo đạc.

---

### MỤC 2: CÁC NỘI DUNG ĐÃ XÓA BỎ VÀ CHUYỂN ĐỔI THEO YÊU CẦU

1. **Xóa Bảng 5.6 cũ (Băng thông mạng, RTT, Tỷ lệ mất gói):** Đã xóa toàn bộ bảng và các đoạn văn mô tả số liệu ping RTT / packet loss tự tạo.
2. **Chuyển đổi Bảng 6.1 sang so sánh ĐỊNH TÍNH:** Bảng 6.1 so sánh phương pháp đề xuất với các giải thuật Autocorrelation, YIN, HPS được giữ lại dưới dạng phân tích định tính về độ phức tạp tính toán và miền xử lý, loại bỏ toàn bộ các con số mili-giây thời gian chạy ESP32 không có trong bản gốc.
3. **Chuẩn hóa trạng thái WebSocket:** Khẳng định giao thức đang hoạt động là HTTP Polling định kỳ 125 ms; chuyển toàn bộ nội dung về WebSocket sang mục Hướng phát triển trong tương lai ở Chương 7.
4. **Bảng 4.1 (Rà soát tham số firmware):** Chỉ giữ lại đúng các tham số có trong bản gốc (`MIN_AC_RMS_NORM = 0.0020`, `PEAK_MIN_MAG ≥ 1.0`, `HARMONIC_PROM_MIN = 2.20`, `BASS_GATE_FREQ = 55.0 Hz`, `BASS_GATE_MIN_HARM ≥ 3`, `BASS_GATE_MIN_MAG = 14.0`, `LOCK_TOLERANCE_RATIO = 0.035`, `PITCH_HISTORY_LEN = 5`). Các tham số chưa có số liệu gốc (`PEAK_REL_THRESHOLD`, `PROMINENCE_MIN`) chuyển thành `[CẦN BỔ SUNG từ firmware]`.
5. **Trang bìa:** Đã xóa bỏ các mã giả định "EE3015" và "EE3015_L01", thay thế bằng `[CẦN BỔ SUNG: Mã học phần]` và `[CẦN BỔ SUNG: Mã lớp học phần]`.

---

### MỤC 3: ĐỒNG BỘ HÓA TÓM TẮT (VI), ABSTRACT (EN) VÀ CÁC KẾT LUẬN

1. **Viết lại Tóm tắt tiếng Việt:**
   - Cập nhật chính xác 100% các số liệu: 5 nốt kiểm chứng đạt 100.0%, nốt A4 (mean 440.281 Hz, std 0.096 Hz, MAE 0.281 Hz, 1.10 cent), C4 (261.674 Hz, 0.43 cent), C5 (523.438 Hz, 0.62 cent), D3 (146.797 Hz, 0.71 cent), E3 (164.787 Hz, 0.57 cent).
   - Nốt trầm E2: Tỷ lệ đúng 15.0% (3/20 khung), mean 83.160 Hz, std 0.137 Hz, MAE 0.750 Hz; 85% nhầm sang E3; năng lượng $f_0$ yếu (1.5–7.3 so với 46.4 của họa âm bậc 3).
   - Độ trễ DSP 23.56–25.37 ms, CPU ~18.5%, Chrome CDP 8 viewport 0 lỗi JS (chưa xác minh trên điện thoại vật lý).
   - Minh định ranh giới: Dải cực trầm (A0–C2), dải cực cao (C6–C8) và hợp âm pedal là CHƯA ĐƯỢC XÁC MINH.
2. **Viết lại Abstract tiếng Anh:** Đồng bộ song ngữ chuẩn xác toàn bộ các số liệu và thuật ngữ kỹ thuật tương ứng.
3. **Cập nhật Bảng 6.2 (Ranh giới xác thực thực tế):** Khôi phục nguyên văn Bảng 50 bản gốc (Verified vs. Not Verified).
4. **Cập nhật Chương 7 (Kết luận và Hướng phát triển):** Các kết luận định lượng bám sát đúng số liệu đã khôi phục.

---

### MỤC 4: CHUẨN HÓA ĐỊNH DẠNG VÀ CÔNG THỨC TOÁN HỌC

1. **Chuẩn hóa toàn bộ chỉ số dưới thô ($X_y$) thành Native Word Subscript:**
   - Triển khai thuật toán xử lý XML tự động quét toàn bộ văn bản `word/document.xml`.
   - Chuyển đổi toàn bộ các biến toán học ($f_0, f_1, f_2, 2f_0, 3f_0, 4f_0, 5f_0, F_s, T_{\text{frame}}, \text{dev2}, \text{dev3}, \text{LocalFloor}_k, \text{Score}_{\text{raw}}, W_N, f_{\text{peak}}, f_{\text{target}}$) sang định dạng Word Subscript chuẩn `<w:vertAlign w:val="subscript"/>` kết hợp in nghiêng tên biến.
   - Tuyệt đối không để sót bất kỳ dấu gạch dưới thô nào ngoài các định danh code khối lập trình.
2. **Sửa lỗi công thức tổng $\sum$ tại Phương trình (2.1):**
   - Đảm bảo toàn bộ thân biểu thức $A_m \cos(2\pi m f_0 t + \phi_m)$ nằm trọn vẹn bên trong thẻ `<m:nary><m:e>`, hiển thị chuẩn mực và đầy đủ khi mở bằng Microsoft Word.
3. **Nhúng 12 Native Word Comments:**
   - Đã nhúng đầy đủ 12 comment học thuật chính thức vào cây XML `word/comments.xml` và `word/document.xml` với các ID từ 0 đến 11, xác định rõ các vị trí cần tác giả bổ sung thông tin thực tế.

---

### MỤC 5: TỔNG KẾT TẬP TIN XUẤT BẢN

| Tên tập tin | Định dạng | Trạng thái | Đường dẫn lưu trữ |
|---|---|---|---|
| `LeTanDung_24150654.docx` | DOCX | Bản gốc (giữ nguyên vẹn, không ghi đè) | `D:\dsp\LeTanDung_24150654\LeTanDung_24150654.docx` |
| `LeTanDung_24150654_v2.docx` | DOCX | Bản hiệu đính hoàn thiện, khớp 100% số liệu gốc | `D:\dsp\LeTanDung_24150654\LeTanDung_24150654_v2.docx` |
| `LeTanDung_24150654_v2.pdf` | PDF | Bản PDF xuất trực tiếp từ Microsoft Word COM | `D:\dsp\LeTanDung_24150654\LeTanDung_24150654_v2.pdf` |
| `DIFF_REPORT.md` | Markdown | Báo cáo đối chiếu sai khác số liệu tự động | `D:\dsp\LeTanDung_24150654\DIFF_REPORT.md` |
| `CHANGELOG.md` | Markdown | Nhật ký thay đổi toàn diện (tập tin này) | `D:\dsp\LeTanDung_24150654\CHANGELOG.md` |
| `OPEN_ITEMS.md` | Markdown | Danh mục các mục mở cần tác giả tự bổ sung | `D:\dsp\LeTanDung_24150654\OPEN_ITEMS.md` |
