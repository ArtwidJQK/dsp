# DANH MỤC CÁC MỤC MỞ VÀ CÔNG VIỆC CẦN TÁC GIẢ BỔ SUNG (OPEN ITEMS)
## BÁO CÁO TIỂU LUẬN KỸ THUẬT: PIANO CHROMATIC TUNER (ESP32-S3 + INMP441)
**Tác giả:** Lê Tấn Dũng (MSSV: 24150654)  
**Tập tin tài liệu hiệu đính:** `LeTanDung_24150654_v2.docx` & `LeTanDung_24150654_v2.pdf`  
**Tập tin nguồn sự thật (GỐC):** `LeTanDung_24150654.docx`  
**Ngày cập nhật:** 06/10/2026  

---

### HƯỚNG DẪN DÀNH CHO TÁC GIẢ
Bản hiệu đính `v2` đã khôi phục nguyên văn 100% số liệu thực nghiệm từ bản gốc `LeTanDung_24150654.docx` và loại bỏ toàn bộ các số liệu tự tạo theo nguyên tắc **REAL-DATA ONLY**. Để hoàn thiện bài nộp chính thức đạt điểm tối đa, tác giả cần xem xét và tự điền các mục mở (Open Items) được phân loại theo mức độ ưu tiên dưới đây. Toàn bộ các vị trí này đã được biên tập viên đánh dấu bằng ký hiệu `[CẦN BỔ SUNG]` và gắn sẵn **Native Word Comments** trực tiếp trong tập tin Word.

---

### NHÓM A: THÔNG TIN HÀNH CHÍNH & BÌA BÁO CÁO (BẮT BUỘC TRƯỚC KHI NỘP)

| STT | Vị trí trong báo cáo | Mục cần điền | Hướng dẫn chi tiết | Trạng thái hiện tại |
| :---: | :--- | :--- | :--- | :--- |
| **A.1** | **Trang bìa** | **Họ tên Giảng viên hướng dẫn** | Điền chính xác họ tên, học hàm, học vị của GVHD (ví dụ: *TS. Nguyễn Văn A* hoặc *PGS.TS. Trần Thị B*) theo phân công của Bộ môn Viễn thông - Xử lý tín hiệu. *(Word Comment #0).* | Đã đặt `[CẦN BỔ SUNG: họ tên GVHD]` |
| **A.2** | **Trang bìa** | **Mã học phần** | Điền mã học phần chính thức của môn Xử lý tín hiệu số tại trường (thay thế mã tạm thời đã xóa). | Đã đặt `[CẦN BỔ SUNG: Mã học phần]` |
| **A.3** | **Trang bìa** | **Mã lớp học phần** | Điền mã lớp học phần cụ thể của học kỳ (thay thế mã tạm thời đã xóa). | Đã đặt `[CẦN BỔ SUNG: Mã lớp học phần]` |

---

### NHÓM B: SỐ LIỆU ĐỐI CHIẾU FIRMWARE VÀ THỰC NGHIỆM PHẦN CỨNG

| STT | Vị trí trong báo cáo | Mục cần điền | Hướng dẫn chi tiết | Mức độ ưu tiên |
| :---: | :--- | :--- | :--- | :--- |
| **B.1** | **Bảng 4.1** (Trang 17) | **Tham số `PEAK_REL_THRESHOLD` và `PROMINENCE_MIN`** | Mở mã nguồn firmware C (`main.c` / `pitch_detector.c`), tra cứu giá trị macro định nghĩa ngưỡng biên độ tương đối của đỉnh so với đỉnh lớn nhất trong khung và độ nổi bật tối thiểu. Điền giá trị thực tế thay cho placeholder. | **Cao** |
| **B.2** | **Bảng 5.1** (Trang 21) | **Bộ ước lượng (Estimator) cho từng nốt** | Kiểm tra lại log runtime từ cổng Serial ESP32-S3 khi gõ từng nốt (A4, C4, C5, D3, E3) để xác nhận thuật toán đã kích hoạt ước lượng qua đỉnh tần số cơ bản trực tiếp (`F1_PRIMARY`) hay qua họa âm dự phòng (`F2_FALLBACK`). *(Word Comment #8).* | **Cao** |
| **B.3** | **Mục 5.1 & Phụ lục B** (Trang 20, 31) | **Đặc tả đàn piano và môi trường âm học phòng đo** | Bổ sung các thông số môi trường thực nghiệm: Hãng sản xuất và model đàn piano (Upright hay Grand), ngày lên dây gần nhất, đặc điểm âm học phòng đo, nhiệt độ môi trường (°C), mức ồn nền phòng đo (dBA) và quy trình gõ phím. *(Word Comment #7).* | **Trung bình** |
| **B.4** | **Mục 3.2 & Bảng 6.2** (Trang 15, 27) | **Kiểm thử chạy liên tục dài hạn (Soak test)** | Cho hệ thống chạy thu âm và phục vụ web liên tục tối thiểu 24–48 giờ trong phòng lab. Ghi nhận dung lượng free heap ban đầu và sau test để khẳng định không bị rò rỉ bộ nhớ (memory leak), số lần watchdog reset = 0. *(Word Comment #2).* | **Trung bình** |
| **B.5** | **Mục 5.7 & Bảng 5.5** (Trang 24) | **Quy trình đo đạc độ trễ phản hồi tổng 150–280 ms** | Ghi rõ phương pháp đo đạc độ trễ từ lúc búa gõ phím đến khi giao diện web cập nhật (ví dụ: dùng camera quay tốc độ cao hoặc ghi nhận timestamp mạng). *(Word Comment #10).* | **Trung bình** |

---

### NHÓM C: CÁC QUYẾT ĐỊNH KỸ THUẬT VÀ GIẢI TRÌNH HỌC THUẬT

| STT | Vị trí trong báo cáo | Vấn đề kỹ thuật | Phân tích và Phương án tác giả |
| :---: | :--- | :--- | :--- |
| **C.1** | **Bảng 5.2** (Trang 22) | **Độ dạt họa âm dev2 của A4 mang dấu âm (−0.036 Hz)** | **Hiện trạng:** Tại nốt A4, $f_1 = 440.285\text{ Hz}$, $f_2/2 = 440.249\text{ Hz}$, dẫn đến $\text{dev2} = (f_2/2) - f_1 = -0.036\text{ Hz}$.<br>**Giải trình:** Tác giả giữ nguyên số liệu thật và lưu ý giải thích: Giá trị âm này nằm trong phạm vi sai số ước lượng đỉnh của thuật toán nội suy parabol (độ phân giải bin thô 3.906 Hz) hoặc do dao động vi mô cơ học của dây đàn khi rung tự do. *(Word Comment #9).* |
| **C.2** | **Mục 4.3 & Hàm `init_hann_window()`** (Trang 16) | **Chuẩn hóa công thức cửa sổ Hann tuần hoàn** | **Hiện trạng:** Công thức đã được chuẩn hóa về dạng tuần hoàn $w[n] = 0.5(1 - \cos(2\pi n / N))$ (chia cho $N$).<br>**Quyết định:** Tác giả đối chiếu với mã nguồn C xem firmware chia cho `FFT_SIZE` hay `(FFT_SIZE - 1)` để đảm bảo tính đồng bộ hoàn toàn giữa báo cáo lý thuyết và code thực thi. *(Word Comment #4).* |
| **C.3** | **Mục 4.6 & Thuật toán sàn nhiễu trung vị** (Trang 17) | **Xử lý trung vị trên 24 phần tử nền nhiễu** | **Hiện trạng:** Cửa sổ 29 bin loại 5 bin trung tâm còn lại 24 phần tử. Trung vị lý thuyết của mảng 24 phần tử chẵn là trung bình của phần tử thứ 12 và 13.<br>**Quyết định:** Kiểm tra xem firmware C lấy trực tiếp phần tử thứ 12 hay trung bình hai phần tử để ghi chú thống nhất. *(Word Comment #6).* |
| **C.4** | **Mục 3.7 & Dung sai khóa nốt** (Trang 15) | **Dung sai 3.5% (~60 cent)** | **Hiện trạng:** Ngưỡng 3.5% tần số tương đương ~59.6 cent là khá rộng so với tiêu chuẩn lên dây chuyên nghiệp ($\pm 5\text{ cent}$).<br>**Quyết định:** Tác giả giải thích lý do giữ 3.5% trong giai đoạn ổn định nốt khi năng lượng tắt dần (decay phase) và đề xuất thu hẹp xuống 25–30 cent trong phần Hướng phát triển ở Chương 7. *(Word Comment #5).* |
| **C.5** | **Tài liệu tham khảo [9], [10]** (Trang 29) | **Xác minh số trang và DOI thư mục** | Tác giả kiểm tra lại chính xác số tập, số trang và DOI của hai bài báo tham khảo của tác giả Jacobsen & Kootsookos (2007) và Abe & Smith (2004) trước khi in nộp bản bìa cứng. *(Word Comment #11).* |

---

### HÌNH ẢNH MINH HỌA THỰC TẾ CẦN CHỤP CHÈN VÀO KHUNG PLACEHOLDER
Trong bản v2, hai khung Placeholder đồ họa thực tế đã được bố trí sẵn khung viền nét đứt trang nhã kèm caption chuẩn. Trước khi nộp bản in cuối cùng, tác giả chỉ cần chèn ảnh thật vào:
1. **Hình 5.1 (Trang 20):** *Ảnh chụp bố trí thực nghiệm đo đạc âm thanh thực tế trên đàn piano acoustic* (Cây đàn piano, cự ly đặt bo ESP32-S3 và mic INMP441).
2. **Hình 5.2 (Trang 20):** *Ảnh chụp màn hình giao diện web Celestial Tuner thực tế khi thiết bị đang nhận diện phím đàn piano*.
