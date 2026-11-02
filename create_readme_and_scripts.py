# -*- coding: utf-8 -*-
"""
Script to generate:
1. D:\dsp\LeTanDung_24150654\README.md
2. D:\dsp\LeTanDung_24150654\README.docx
3. D:\dsp\LeTanDung_24150654\sources\build_firmware.py
4. D:\dsp\LeTanDung_24150654\sources\flash_chip.py
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

BASE_DIR = r"D:\dsp\LeTanDung_24150654"
SOURCES_DIR = os.path.join(BASE_DIR, "sources")

README_MD_CONTENT = """# PIANO CHROMATIC TUNER USING ESP32-S3 AND INMP441
> **Đồ án môn học: Xử Lý Tín Hiệu Số (DSP)**  
> **Sinh viên thực hiện:** Lê Tấn Dũng  
> **Mã số sinh viên (MSSV):** 24150654  
> **Nền tảng:** ESP32-S3 N16R8 + INMP441 MEMS Microphone (ESP-IDF v6.0.2 / C/C++ / Web UI)

---

## 1. GIỚI THIỆU TỔNG QUAN DỰ ÁN

### 1.1. Project này là gì?
**Piano Chromatic Tuner** là thiết bị lên dây đàn piano chromatic đơn âm (Single-Note Tuner) hoạt động thời gian thực (real-time) độc lập trên nền tảng vi điều khiển SoC **ESP32-S3 N16R8** kết hợp microphone kỹ thuật số MEMS **INMP441** giao tiếp qua bus **I2S**.

Thiết bị thu nhận sóng âm thanh phát ra khi người chơi gõ từng phím đàn piano, áp dụng trực tiếp pipeline xử lý tín hiệu số (DSP) ngay trên chip để xác định tần số cơ bản ($f_0$), ánh xạ sang tên nốt nhạc danh định (chuẩn MIDI hệ âm bằng Equal Temperament 12-TET, $A_4 = 440\\text{ Hz}$) và tính toán độ sai lệch cao độ theo đơn vị cent (cents deviation).

Toàn bộ kết quả nhận diện được hiển thị trực tiếp và không dây qua giao diện web **Celestial / Fantasy Piano Tuner** do chính ESP32-S3 phát sóng Wi-Fi và đóng vai trò máy chủ HTTP nhúng. Người dùng có thể sử dụng bất kỳ thiết bị nào (điện thoại, máy tính bảng, laptop) kết nối vào Wi-Fi của tuner để quan sát mà không cần cài đặt phần mềm bên ngoài và không cần kết nối Internet.

---

### 1.2. Project này dùng để làm gì?
- **Mục đích chính:** Cung cấp giải pháp lên dây đàn piano cơ (acoustic piano) chính xác, phản hồi nhanh, trực quan và chi phí cực thấp (< 15 USD).
- **Giải quyết các hạn chế của ứng dụng trên smartphone:**
  - Microphone trên điện thoại thường bị suy hao rất mạnh ở dải hạ âm (< 100 Hz) do tối ưu cho giọng nói, đồng thời bị can thiệp bởi các mạch tự động điều chỉnh khuếch đại (AGC) và lọc khử ồn (Noise Suppression) làm méo mó các đỉnh phổ âm học thực tế của đàn piano.
  - Hệ điều hành di động (Android / iOS) có độ trễ âm thanh không cố định (audio buffer latency), dễ gây giật lag khi gõ phím liên tục.
- **Giải quyết các hạn chế của tuner phần cứng thương mại:** Các máy tuner chuyên dụng thường có giá thành rất cao, là hệ thống đóng kín, không hỗ trợ giao diện đồ họa trực quan đa thiết bị qua mạng không dây.

---

## 2. KIẾN TRÚC PHẦN CỨNG & SƠ ĐỒ NỐI DÂY (WIRING DIAGRAM)

### 2.1. Danh sách linh kiện phần cứng
1. **Vi điều khiển:** ESP32-S3 N16R8 (Xtensa 32-bit LX7 dual-core @ 240 MHz, 16 MB Quad SPI Flash, 8 MB Octal PSRAM).
2. **Microphone đầu vào:** Module Microphone MEMS I2S INMP441 (Tích hợp ADC 24-bit, SNR 61 dBA, đáp ứng phẳng 60 Hz – 15 kHz).
3. **Nguồn cấp:** Cáp USB Type-C (cấp nguồn 5V từ sạc điện thoại, cổng USB máy tính hoặc sạc dự phòng).
4. **Dây nối:** Dây cắm breadboard / jumper wires female-to-female.
*(Lưu ý: Phiên bản cuối không sử dụng màn hình OLED SSD1306 nhằm giải phóng tài nguyên chân GPIO và chuyển hoàn toàn sang giao diện Web đa nền tảng).*

---

### 2.2. Sơ đồ nối dây chi tiết (Hardware Pinout)

Bảng kết nối vật lý chuẩn giữa module INMP441 và bo mạch ESP32-S3 N16R8 (được khóa cố định trong firmware):

| Chân INMP441 (Mic) | Chân ESP32-S3 | Loại tín hiệu | Vai trò kỹ thuật chi tiết |
| :---: | :---: | :---: | :--- |
| **SCK / BCLK** | **GPIO 4** | Output từ ESP32 | Xung nhịp bit nối tiếp I2S Bit Clock (tần số 1.024 MHz) |
| **WS / LRCLK** | **GPIO 5** | Output từ ESP32 | Xung nhịp chọn kênh Word Select (tần số lấy mẫu 16.000 Hz) |
| **SD / DOUT** | **GPIO 6** | Input vào ESP32 | Dữ liệu âm thanh số PCM 24-bit truyền nối tiếp vào DMA |
| **L/R** | **GND** | Cấu hình kênh | Kéo xuống mức LOW để chọn Kênh Trái (Left Channel) |
| **VDD** | **3.3V** | Nguồn cấp | Điện áp nguồn 3.3V ổn định từ IC nguồn của ESP32-S3 |
| **GND** | **GND** | Nối đất | Đất chung hệ thống (Common Ground) |

#### Sơ đồ kết nối trực quan (ASCII Diagram):
```
    +-------------------------+             +-------------------------+
    |   INMP441 MEMS MIC      |             |   ESP32-S3 N16R8        |
    |                         |             |                         |
    |      [SCK / BCLK] ------+-------------> GPIO 4 (I2S BCLK)       |
    |      [WS / LRCLK] ------+-------------> GPIO 5 (I2S WS/LRCLK)   |
    |       [SD / DOUT] ------+-------------> GPIO 6 (I2S DATA IN)    |
    |             [L/R] ------+-------------> GND (Left Channel)      |
    |             [VDD] ------+-------------> 3.3V                    |
    |             [GND] ------+-------------> GND                     |
    +-------------------------+             +-------------------------+
                                                         | (USB Type-C)
                                                         v
                                                   Nguồn 5V / Debug PC
```

---

## 3. PIPELINE XỬ LÝ TÍN HIỆU SỐ (DSP PIPELINE)

Hệ thống triển khai pipeline xử lý tín hiệu số liên tục, tối ưu hóa toàn bộ bằng ngôn ngữ C thuần trên bộ khung ESP-IDF (không sử dụng ArduinoFFT):

```
Sóng âm Piano ──> INMP441 (ADC 24-bit) ──> I2S DMA (Core 1)
       │
       ▼
Hop Buffer (2048 mẫu mới = 128 ms) ──> Trượt 50% Overlap vào Rolling Buffer (4096 mẫu = 256 ms)
       │
       ▼
Khử thành phần một chiều (DC Removal: x[n] - mean)
       │
       ▼
Nhân cửa sổ Hann tiền tính toán (w[n] * x[n])
       │
       ▼
Biến đổi Fourier nhanh (FFT Radix-2 DIT 4096 điểm, độ phân giải df = 3.90625 Hz/bin)
       │
       ▼
Trích xuất đỉnh phổ cục bộ & Sàng lọc sàn nhiễu trung vị 24-bin (Prominence / SNR)
       │
       ▼
Phân tích họa âm Harmonic-Aware (Subharmonic hypotheses m=1..6, cứu missing m1, bass-guard)
       │
       ▼
Nội suy parabol bậc hai (Quadratic Interpolation -> ước lượng f0 mịn dưới bin)
       │
       ▼
Bộ lọc ổn định thời gian (Temporal Stability Filter: Fast Lock 2 khung = 256 ms, Median smoothing)
       │
       ▼
Ánh xạ nốt MIDI (A4 = 440 Hz) & Tính độ sai lệch cents
       │
       ▼
Cập nhật thread-safe qua FreeRTOS Critical Section (s_latest_pitch)
       │
       ▼
Máy chủ Web nhúng (esp_http_server cổng 80) phục vụ GET / và GET /api/data
       │
       ▼
Giao diện Web Frontend Celestial Tuner (HTML5/CSS3/JS Vanilla)
```

### Các thông số cốt lõi của DSP:
- **Tần số lấy mẫu ($F_s$):** $16.000\\text{ Hz}$
- **Độ dài khung phân tích ($N$):** $4096\\text{ mẫu}$ ($256.0\\text{ ms}$)
- **Bước nhảy đệm trượt (Hop size):** $2048\\text{ mẫu}$ ($128.0\\text{ ms}$, chồng lấp $50\\%$)
- **Độ phân giải bin phổ ($\\Delta f$):** $\\frac{16000}{4096} = 3.90625\\text{ Hz/bin}$
- **Tần số giới hạn Nyquist:** $8000\\text{ Hz}$ (Bao phủ hoàn toàn 88 phím piano từ $A_0: 27.5\\text{ Hz}$ đến $C_8: 4186\\text{ Hz}$)
- **Thời gian thực thi tính toán DSP:** $23.56 - 25.37\\text{ ms}$ (Tải CPU chỉ chiếm $\\approx 18.5\\%$)

---

## 4. CẤU TRÚC THƯ MỤC CỦA DỰ ÁN

Thư mục nộp bài chuẩn tại `D:\\dsp\\LeTanDung_24150654`:

```
LeTanDung_24150654/
│
├── LeTanDung_24150654.docx      # Báo cáo tiểu luận kỹ thuật cuối kỳ đầy đủ chuẩn học thuật (16.649 từ)
├── README.md                    # Tài liệu hướng dẫn A-Z chi tiết về dự án (bản Markdown)
├── README.docx                  # Tài liệu hướng dẫn A-Z chi tiết về dự án (bản Word định dạng đẹp)
│
└── sources/                     # Thư mục mã nguồn và các file cần thiết để chạy dự án
    ├── CMakeLists.txt           # File cấu hình build CMake gốc của ESP-IDF
    ├── sdkconfig                # File cấu hình phần cứng và phân vùng flash ESP32-S3
    │
    ├── main/
    │   ├── CMakeLists.txt       # Cấu hình component ESP-IDF (nhúng index.html)
    │   ├── main.c               # Toàn bộ mã nguồn firmware C/C++ (I2S, FFT, DSP, Web Server)
    │   └── index.html           # Toàn bộ giao diện Web Celestial Tuner (HTML5/CSS3/JS Vanilla)
    │
    ├── binaries/                # File nhị phân biên dịch sẵn (dùng để nạp nhanh)
    │   ├── piano_tuner.bin      # Firmware ứng dụng chính (911 KB)
    │   ├── bootloader.bin       # Bootloader ESP32-S3 (21 KB)
    │   └── partition-table.bin  # Bảng phân vùng bộ nhớ Flash (3 KB)
    │
    ├── build_firmware.py        # Script tự động hóa biên dịch firmware bằng ESP-IDF
    ├── flash_chip.py            # Script tự động hóa nạp firmware xuống ESP32-S3 qua cổng COM
    ├── read_serial.py           # Script đọc log chẩn đoán Serial UART (115200 bps)
    ├── check_com3.py            # Script kiểm tra kết nối cổng COM3
    └── test_live_esp32_web.py   # Script kiểm thử giao diện tự động qua Wi-Fi và Chrome CDP
```

---

## 5. HƯỚNG DẪN CÀI ĐẶT & NẠP FIRMWARE (BUILD & FLASH GUIDE)

### Cách 1: Nạp nhanh bằng file nhị phân biên dịch sẵn (Khuyên dùng - Không cần cài đặt ESP-IDF)
Trong thư mục `sources/binaries/` đã có sẵn các file firmware biên dịch chuẩn. Bạn chỉ cần Python và thư viện `esptool` và `pyserial`:

1. Cài đặt thư viện Python nếu chưa có:
   ```bash
   pip install esptool pyserial
   ```
2. Cắm bo mạch ESP32-S3 vào cổng USB của máy tính (xác định cổng COM, ví dụ `COM3`).
3. Chạy script nạp chip tự động:
   ```bash
   cd D:\dsp\LeTanDung_24150654\sources
   python flash_chip.py
   ```
   *Lưu ý: Nếu cần chỉ định cổng COM khác, bạn có thể truyền tham số hoặc chỉnh sửa biến `port` trong file `flash_chip.py`.*

---

### Cách 2: Biên dịch trực tiếp từ mã nguồn (Dành cho nhà phát triển)
1. Yêu cầu môi trường: Cài đặt **ESP-IDF v6.0.2** (hoặc v5.x) chính thức từ Espressif.
2. Mở cửa sổ dòng lệnh **ESP-IDF 6.0 PowerShell** hoặc terminal đã active môi trường IDF.
3. Di chuyển vào thư mục `sources`:
   ```bash
   cd D:\dsp\LeTanDung_24150654\sources
   ```
4. Thực hiện lệnh biên dịch:
   ```bash
   idf.py build
   ```
   *(Hoặc chạy script tự động: `python build_firmware.py`)*
5. Nạp chương trình xuống ESP32-S3:
   ```bash
   idf.py -p COM3 flash
   ```
6. Mở màn hình theo dõi log nối tiếp:
   ```bash
   idf.py -p COM3 monitor
   ```

---

## 6. HƯỚNG DẪN SỬ DỤNG TỪ A ĐẾN Z (USER MANUAL)

### Bước 1: Khởi động thiết bị
- Cắm cáp nguồn USB Type-C cho ESP32-S3.
- Sau khoảng 1.5 giây, đèn tín hiệu trên bo mạch sẽ sáng ổn định, hệ thống phát sóng Wi-Fi SoftAP và bắt đầu thu nhận âm thanh.

### Bước 2: Kết nối Wi-Fi vào Tuner
Bạn có 2 cách để truy cập vào giao diện Tuner:

- **Cách 1: Kết nối trực tiếp vào Wi-Fi do ESP32-S3 phát (Khuyên dùng - Tiện lợi nhất, không cần router):**
  1. Trên điện thoại hoặc laptop, mở cài đặt Wi-Fi và tìm mạng:
     - **Tên Wi-Fi (SSID):** `PianoTuner-ESP32`
     - **Mật khẩu (Password):** `12345678`
  2. Sau khi kết nối, mở trình duyệt web (Chrome, Safari, Edge, Cốc Cốc) và truy cập địa chỉ IP mặc định:
     ```
     http://192.168.4.1/
     ```

- **Cách 2: Truy cập qua mạng Wi-Fi gia đình (Station Mode):**
  - ESP32-S3 được cấu hình tự động kết nối vào Wi-Fi trạm (SSID `HongLinh_L3`).
  - Khi kết nối thành công, vi điều khiển nhận địa chỉ IP động từ router (ví dụ `http://192.168.1.238/`). Bạn có thể xem IP qua Serial Monitor hoặc kiểm tra router. Mọi thiết bị cùng mạng Wi-Fi này đều có thể truy cập qua địa chỉ đó.

---

### Bước 3: Đặt microphone và bắt đầu lên dây
- Đặt bo mạch có gắn microphone INMP441 cách khu vực búa gõ / dây đàn tương ứng từ **5 cm đến 20 cm**.
- Lỗ thu âm nhỏ ở mặt đáy của module INMP441 nên hướng về phía thùng đàn / dây đàn.
- **Cách chơi phím đàn:** Gảy dứt khoát từng phím đàn đơn lẻ và để phím đàn ngân tự nhiên ít nhất 300 ms (không gảy nhiều phím cùng lúc, không dậm pedal vang âm liên tục).

---

### Bước 4: Đọc kết quả trên giao diện Web Celestial Tuner

Giao diện web được thiết kế trực quan với các thành phần:

1. **Hiển thị Tên Nốt Nhạc (Note Name):**
   - Chữ nốt hiển thị to rõ ở chính giữa (ví dụ: `A4`, `C4`, `D3`, `E3`).
   - Tần số đo được thời gian thực (ví dụ: `440.24 Hz`) và tần số chuẩn tương ứng (`Target: 440.00 Hz`).
2. **Kim đo sai lệch Cents (Tuner Needle Gauge):**
   - Thang đo kéo dài từ **-50 cent** (quá thấp) đến **+50 cent** (quá cao), mốc 0 cent ở chính giữa.
   - Khi tần số đo được lệch chuẩn, kim đo sẽ xoay mượt mà chỉ rõ số cent sai lệch.
3. **Các trạng thái chỉ báo màu sắc:**
   - **`ĐÚNG CAO ĐỘ` (IN TUNE):** Khi sai lệch $|\\text{cents}| \\le 5\\text{ cent}$, viền kim và hào quang chuyển sang màu **xanh lục ngọc** sáng rực. Dây đàn đã chuẩn cao độ.
   - **`THẤP` (TOO LOW):** Khi $\\text{cents} < -5\\text{ cent}$, hiển thị màu **lam tím**, kim lệch trái. Cần vặn căng dây đàn lên.
   - **`CAO` (TOO HIGH):** Khi $\\text{cents} > +5\\text{ cent}$, hiển thị màu **đỏ cam**, kim lệch phải. Cần vặn chùng dây đàn xuống.
   - **`KHÔNG CÓ TÍN HIỆU` (NO SIGNAL):** Khi không có tiếng đàn hoặc phòng yên tĩnh, kim đo trở về trạng thái nghỉ.
4. **Bàn phím Piano ảo tương tác (Virtual Keyboard $C_2 – C_8$):**
   - Dải phím piano ảo bên dưới tự động làm nổi bật (highlight phát sáng) đúng vị trí phím đàn bạn vừa chơi.

---

### Bước 5: Truy vấn dữ liệu tự động qua REST API
Nếu bạn muốn tích hợp dữ liệu với phần mềm ngoài, gửi yêu cầu `GET` tới:
```http
GET http://192.168.4.1/api/data
```
Dữ liệu trả về định dạng JSON thời gian thực:
```json
{
  "frequency": 440.237,
  "note": "A4",
  "target": 440.000,
  "cents": 0.93,
  "confidence": 100.0,
  "estimator": "F1_PRIMARY",
  "valid": true,
  "frame": 397,
  "latency_ms": 24.84
}
```

---

## 7. KẾT QUẢ ĐO ĐẠC THỰC TẾ & GIỚI HẠN KỸ THUẬT (REAL-DATA ONLY)

Tuân thủ nghiêm ngặt tính liêm chính học thuật, toàn bộ số liệu dưới đây được đo trực tiếp trên đàn piano cơ thật:

| Nốt nhạc | Tần số chuẩn | Trung bình đo (Mean) | Độ lệch chuẩn (Std) | Sai số MAE | Sai số cực đại | Tỷ lệ nhận diện đúng |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **A4** | 440.000 Hz | **440.281 Hz** | 0.096 Hz | 0.281 Hz | 0.680 Hz | 100.0% |
| **C4** | 261.626 Hz | **261.674 Hz** | 0.064 Hz | 0.065 Hz | 0.140 Hz | 100.0% |
| **C5** | 523.251 Hz | **523.438 Hz** | 0.020 Hz | 0.188 Hz | 0.260 Hz | 100.0% |
| **D3** | 146.832 Hz | **146.797 Hz** | 0.074 Hz | 0.060 Hz | 0.270 Hz | 100.0% |
| **E3** | 164.814 Hz | **164.787 Hz** | 0.065 Hz | 0.054 Hz | 0.133 Hz | 100.0% |

- **Độ trễ tính toán DSP thuần đo được:** **23.56 – 25.37 ms** (thời gian tính FFT, QI và chấm điểm họa âm).
- **Kiểm thử tự động Web trên Chrome Headless CDP:** Đạt 0 lỗi JavaScript Console, vượt qua kiểm tra co giãn giao diện trên 8 kích thước màn hình từ 360x800 đến 1920x1080.

### Các giới hạn thực tế cần lưu ý (Transparent Limitations):
1. **Dải nốt trầm $E_2$ (82.41 Hz):** Ở các nốt trầm, năng lượng tần số cơ bản $f_0$ của đàn piano thực tế rất yếu (biên độ 1.5 – 7.3 so với 46.4 của họa âm bậc 3), dẫn đến tỷ lệ bắt đúng nốt $E_2$ trong bài test sạch chỉ đạt 15% và hay bị nhận nhầm thành $E_3$ (164.81 Hz).
2. **Không tuyên bố độ chính xác < 0.5 Hz trên toàn bộ 88 phím:** Do hạn chế mẫu thực nghiệm, các nốt cực trầm ($A_0 – C_2$) và cực cao ($C_6 – C_8$) được phân loại là **CHƯA ĐƯỢC XÁC MINH THỰC TẾ (NOT VERIFIED)**.
3. **Chỉ hỗ trợ đơn âm:** Hệ thống không hỗ trợ nhận diện hợp âm đa âm (Polyphonic).

---

## 8. XỬ LÝ SỰ CỐ THƯỜNG GẶP (TROUBLESHOOTING)

1. **Không mở được trang web 192.168.4.1:**
   - Kiểm tra xem thiết bị của bạn đã ngắt kết nối khỏi Wi-Fi nhà và kết nối đúng vào Wi-Fi `PianoTuner-ESP32` chưa.
   - Một số dòng smartphone tự động ngắt kết nối Wi-Fi không có Internet, hãy chọn *'Giữ kết nối mạng này' (Keep Wi-Fi connection)*.
2. **Giao diện luôn báo 'KHÔNG CÓ TÍN HIỆU' dù đã gõ đàn:**
   - Kiểm tra lại các dây nối phần cứng của INMP441, đặc biệt là chân **L/R bắt buộc phải nối chắc chắn vào chân GND**.
   - Đảm bảo micro được cấp nguồn 3.3V từ bo mạch ESP32.
   - Thử đưa micro lại gần dây đàn hơn (khoảng 5 – 10 cm).
3. **Báo lỗi khi nạp chip qua `flash_chip.py`:**
   - Đóng các phần mềm đang chiếm dụng cổng COM (như Arduino IDE Serial Monitor, PuTTY, idf.py monitor).
   - Đưa ESP32-S3 vào chế độ nạp thủ công: Nhấn giữ nút **BOOT**, nhấn nhả nút **RESET**, sau đó nhả nút **BOOT** rồi chạy lại script.

---
*Báo cáo tiểu luận chi tiết và toàn diện xem tại file: `LeTanDung_24150654.docx` nằm cùng thư mục.*
"""

def generate_files():
    # 1. Write README.md to D:\dsp\LeTanDung_24150654\README.md
    readme_md_path = os.path.join(BASE_DIR, "README.md")
    with open(readme_md_path, "w", encoding="utf-8") as f:
        f.write(README_MD_CONTENT)
    print(f"Generated README.md at: {readme_md_path} ({os.path.getsize(readme_md_path)} bytes)")

    # 2. Write dynamic build_firmware.py in sources
    build_script_path = os.path.join(SOURCES_DIR, "build_firmware.py")
    build_script_code = '''# -*- coding: utf-8 -*-
"""
Build script for ESP32-S3 Piano Chromatic Tuner.
Automatically detects ESP-IDF v6.0.2 environment and builds the current sources directory.
"""

import os
import subprocess
import sys

def main():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Building project at: {project_dir}")
    
    env = os.environ.copy()
    idf_path = env.get("IDF_PATH", r"C:\\ESP-IDF\\v6.0.2\\esp-idf")
    env["IDF_PATH"] = idf_path
    env["ESP_IDF_VERSION"] = "6.0.2"
    
    python_env_default = r"C:\\Users\\dxem1\\.espressif\\python_env\\idf6.0_py3.14_env"
    env["IDF_PYTHON_ENV_PATH"] = env.get("IDF_PYTHON_ENV_PATH", python_env_default)
    
    extra_paths = [
        r"C:\\Users\\dxem1\\.espressif\\tools\\xtensa-esp-elf\\esp-15.2.0_20251204\\xtensa-esp-elf\\bin",
        r"C:\\Users\\dxem1\\.espressif\\tools\\cmake\\4.0.3\\bin",
        r"C:\\Users\\dxem1\\.espressif\\tools\\ninja\\1.12.1",
        os.path.join(env["IDF_PYTHON_ENV_PATH"], "Scripts"),
        r"C:\\Users\\dxem1\\.espressif\\tools\\idf-exe\\1.0.3",
    ]
    env["PATH"] = os.pathsep.join([p for p in extra_paths if os.path.exists(p)]) + os.pathsep + env.get("PATH", "")
    
    python_exe = os.path.join(env["IDF_PYTHON_ENV_PATH"], "Scripts", "python.exe")
    if not os.path.exists(python_exe):
        python_exe = sys.executable
        
    idf_py = os.path.join(idf_path, "tools", "idf.py")
    
    cmd = [python_exe, idf_py, "-C", project_dir, "build"]
    print("Running command:", " ".join(cmd))
    res = subprocess.run(cmd, env=env)
    if res.returncode != 0:
        print(f"Build FAILED with return code: {res.returncode}")
        sys.exit(res.returncode)
        
    print("Build SUCCESSFUL! Binaries generated in build/ folder.")

if __name__ == "__main__":
    main()
'''
    with open(build_script_path, "w", encoding="utf-8") as f:
        f.write(build_script_code)
    print(f"Generated build_firmware.py at: {build_script_path}")

    # 3. Write dynamic flash_chip.py in sources
    flash_script_path = os.path.join(SOURCES_DIR, "flash_chip.py")
    flash_script_code = '''# -*- coding: utf-8 -*-
"""
Flash script for ESP32-S3 Piano Chromatic Tuner.
Flashes either local build binary or precompiled binaries/piano_tuner.bin.
"""

import os
import sys
import time
import subprocess

try:
    import serial
except ImportError:
    serial = None

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else 'COM3'
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check binary path
    bin_path = os.path.join(cur_dir, "build", "piano_tuner.bin")
    if not os.path.exists(bin_path):
        bin_path = os.path.join(cur_dir, "binaries", "piano_tuner.bin")
        
    if not os.path.exists(bin_path):
        print(f"Error: binary file not found! Checked build/ and binaries/")
        sys.exit(1)
        
    print(f"Selected binary for flashing: {bin_path} ({os.path.getsize(bin_path)} bytes)")
    print(f"Target port: {port}")
    
    # Trigger bootloader mode via DTR/RTS
    if serial:
        try:
            print(f"Triggering bootloader mode on {port}...")
            s = serial.Serial(port, 115200)
            s.dtr = False
            s.rts = True
            time.sleep(0.2)
            s.dtr = True
            time.sleep(0.1)
            s.rts = False
            time.sleep(0.5)
            s.dtr = False
            s.close()
            time.sleep(0.3)
        except Exception as e:
            print(f"Serial trigger note: {e}")

    python_idf = r"C:\\Users\\dxem1\\.espressif\\python_env\\idf6.0_py3.14_env\\Scripts\\python.exe"
    if not os.path.exists(python_idf):
        python_idf = sys.executable
        
    cmd = [
        python_idf, "-m", "esptool",
        "--chip", "esp32s3",
        "-p", port,
        "-b", "460800",
        "--before", "no-reset",
        "--after", "hard-reset",
        "write-flash", "0x10000", bin_path
    ]
    
    print("Running command:", " ".join(cmd))
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print("esptool flashing FAILED!")
        sys.exit(res.returncode)
        
    print("Flashing SUCCESSFUL! Application restarting...")

if __name__ == '__main__':
    main()
'''
    with open(flash_script_path, "w", encoding="utf-8") as f:
        f.write(flash_script_code)
    print(f"Generated flash_chip.py at: {flash_script_path}")

    # 4. Generate README.docx formatted beautifully
    print("Generating formatted README.docx...")
    doc = docx.Document()
    
    # Page setup
    section = doc.sections[0]
    section.top_margin = Inches(0.79)
    section.bottom_margin = Inches(0.79)
    section.left_margin = Inches(1.18)
    section.right_margin = Inches(0.79)
    
    # Header & Footer
    header = section.header
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hrun = hp.add_run("README - Hướng dẫn dự án Piano Chromatic Tuner | Lê Tấn Dũng - 24150654")
    hrun.font.name = "Times New Roman"
    hrun.font.size = Pt(8.5)
    hrun.font.italic = True
    hrun.font.color.rgb = RGBColor(120, 120, 120)

    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    frun = fp.add_run("Trang ")
    frun.font.name = "Times New Roman"
    frun.font.size = Pt(9)
    frun.font.color.rgb = RGBColor(100, 100, 100)
    f_p = fp._p
    fldSimple = OxmlElement('w:fldSimple')
    fldSimple.set(qn('w:instr'), 'PAGE')
    f_p.append(fldSimple)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(4)
    r = p_title.add_run("HƯỚNG DẪN DỰ ÁN TỪ A ĐẾN Z\nPIANO CHROMATIC TUNER USING ESP32-S3 AND INMP441")
    r.font.name = "Times New Roman"
    r.font.size = Pt(16)
    r.bold = True
    r.font.color.rgb = RGBColor(27, 54, 93)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(18)
    r = p_sub.add_run("Đồ án môn học: Xử Lý Tín Hiệu Số (DSP) | Sinh viên: Lê Tấn Dũng - MSSV: 24150654")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.italic = True
    r.font.color.rgb = RGBColor(100, 100, 100)

    # Add content sections
    sections_text = [
        ("1. GIỚI THIỆU TỔNG QUAN", [
            "Project này là gì?: Piano Chromatic Tuner là thiết bị lên dây đàn piano chromatic đơn âm thời gian thực độc lập trên vi điều khiển ESP32-S3 N16R8 kết hợp cảm biến microphone kỹ thuật số MEMS INMP441 qua bus I2S.",
            "Project dùng để làm gì?: Giải quyết bài toán cân chỉnh cao độ cho đàn piano cơ với độ chính xác cao. Loại bỏ hoàn toàn sự phụ thuộc vào microphone lọc thoại và mạch AGC méo mó của smartphone, cung cấp thiết bị phần cứng chi phí thấp (< 15 USD) với độ trễ xử lý cực nhỏ (~24 ms)."
        ]),
        ("2. LINH KIỆN & SƠ ĐỒ NỐI DÂY CHI TIẾT", [
            "Danh sách linh kiện: ESP32-S3 N16R8 (16MB Flash, 8MB PSRAM), Microphone MEMS I2S INMP441 (ADC 24-bit tích hợp), cáp nguồn USB-C, dây cắm jumper (không dùng OLED trong bản cuối).",
            "Sơ đồ chân khóa cố định:\n• INMP441 SCK (BCLK) -> ESP32-S3 GPIO 4 (Bit Clock)\n• INMP441 WS (LRCLK) -> ESP32-S3 GPIO 5 (Word Select)\n• INMP441 SD (DOUT) -> ESP32-S3 GPIO 6 (Serial Data In)\n• INMP441 L/R -> ESP32-S3 GND (Chọn Left Channel)\n• INMP441 VDD -> ESP32-S3 3.3V (Nguồn cấp)\n• INMP441 GND -> ESP32-S3 GND (Nối đất chung)"
        ]),
        ("3. PIPELINE XỬ LÝ TÍN HIỆU SỐ (DSP)", [
            "Quy trình xử lý âm thanh: Sóng âm piano -> INMP441 -> I2S DMA -> Rolling buffer 50% overlap (hop 2048 mẫu = 128 ms, khung 4096 mẫu = 256 ms tại Fs = 16 kHz) -> Khử DC -> Cửa sổ Hann -> FFT Radix-2 4096 điểm (df = 3.90625 Hz) -> Sàn nhiễu trung vị 24-bin & Prominence -> Chấm điểm giả thuyết họa âm (Harmonic scoring) -> Nội suy parabol bậc hai (Quadratic Interpolation) -> Bộ lọc ổn định thời gian (Fast lock 2 khung = 256 ms, Median filter) -> Ánh xạ nốt MIDI & Cents -> Web API /api/data -> Giao diện Web Celestial Tuner."
        ]),
        ("4. HƯỚNG DẪN BIÊN DỊCH VÀ NẠP FIRMWARE", [
            "Cách 1 (Nạp nhanh file có sẵn): Vào thư mục sources/ và chạy 'python flash_chip.py' để nạp ngay file binaries/piano_tuner.bin mà không cần cài đặt cả bộ ESP-IDF 5GB.",
            "Cách 2 (Biên dịch từ mã nguồn): Mở ESP-IDF PowerShell, di chuyển vào sources/ và chạy 'python build_firmware.py' (hoặc 'idf.py build'), sau đó nạp bằng 'idf.py -p COM3 flash'."
        ]),
        ("5. HƯỚNG DẪN SỬ DỤNG TỪ A ĐẾN Z", [
            "Bước 1: Cấp nguồn 5V cho ESP32-S3 qua cổng USB Type-C.",
            "Bước 2: Kết nối Wi-Fi: Dùng điện thoại hoặc laptop kết nối vào mạng Wi-Fi 'PianoTuner-ESP32' (mật khẩu: '12345678'). Mở trình duyệt web truy cập địa chỉ: http://192.168.4.1/",
            "Bước 3: Đặt microphone cách khu vực búa gõ/dây đàn piano từ 5 cm đến 20 cm.",
            "Bước 4: Gảy từng phím đơn lẻ và để nốt ngân tự nhiên ít nhất 300 ms.",
            "Bước 5: Quan sát giao diện Celestial Tuner:\n• Xem tên nốt to ở giữa (A4, C4, E3...).\n• Quan sát kim chỉ cents: Xanh lục ngọc = ĐÚNG CAO ĐỘ (IN TUNE); Lam tím = THẤP (TOO LOW, lệch trái); Đỏ cam = CAO (TOO HIGH, lệch phải); Xám mờ = KHÔNG CÓ TÍN HIỆU (NO SIGNAL).\n• Bàn phím piano ảo C2-C8 phía dưới tự động sáng phím đang chơi.",
            "Bước 6: Truy vấn dữ liệu tự động qua API JSON: GET http://192.168.4.1/api/data"
        ]),
        ("6. KẾT QUẢ ĐO ĐẠC THỰC TẾ & GIỚI HẠN (REAL-DATA ONLY)", [
            "Kết quả đo kiểm trên đàn piano cơ thật:\n• A4 (440.00 Hz): mean 440.281 Hz, std 0.096 Hz, MAE 0.281 Hz.\n• C4 (261.63 Hz): mean 261.674 Hz, std 0.064 Hz, MAE 0.065 Hz.\n• C5 (523.25 Hz): mean 523.438 Hz, std 0.020 Hz, MAE 0.188 Hz.\n• D3 (146.83 Hz): mean 146.797 Hz, std 0.074 Hz, MAE 0.060 Hz.\n• E3 (164.81 Hz): mean 164.787 Hz, std 0.065 Hz, MAE 0.054 Hz.\n• Độ trễ tính toán DSP: 23.56 - 25.37 ms (tải CPU ~18.5%).",
            "Giới hạn kỹ thuật minh bạch:\n• Nốt trầm E2 (82.41 Hz): Fundamental yếu (mag 1.5 - 7.3) trong khi họa âm rất mạnh (mag lên tới 46.4), tỷ lệ bắt đúng nốt trong test sạch là 15%, dễ nhảy quãng tám sang E3.\n• Dải cực trầm (A0-C2) và cực cao (C6-C8) chưa được xác minh đầy đủ (NOT VERIFIED).\n• Không tự động tuyên bố toàn bộ 88 phím đạt <0.5 Hz khi chưa đủ dữ liệu đo đạc."
        ]),
        ("7. XỬ LÝ SỰ CỐ THƯỜNG GẶP (TROUBLESHOOTING)", [
            "Không vào được web: Đảm bảo đã kết nối đúng Wi-Fi 'PianoTuner-ESP32' và mở trình duyệt gõ đúng http://192.168.4.1/.",
            "Không nhận tiếng: Kiểm tra chân nối INMP441, đặc biệt chân L/R phải nối chặt vào chân GND.",
            "Lỗi cổng COM: Đóng các phần mềm đang mở cổng COM3, đưa chip vào bootloader (giữ BOOT, bấm RESET, nhả BOOT) rồi flash lại."
        ])
    ]

    for sec_title, sec_paragraphs in sections_text:
        hp = doc.add_paragraph()
        hp.paragraph_format.space_before = Pt(12)
        hp.paragraph_format.space_after = Pt(4)
        hp.paragraph_format.keep_with_next = True
        hrun = hp.add_run(sec_title)
        hrun.font.name = "Times New Roman"
        hrun.font.size = Pt(13)
        hrun.bold = True
        hrun.font.color.rgb = RGBColor(27, 54, 93)

        for p_content in sec_paragraphs:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.25
            prun = p.add_run(p_content)
            prun.font.name = "Times New Roman"
            prun.font.size = Pt(11.5)
            prun.font.color.rgb = RGBColor(30, 30, 30)

    readme_docx_path = os.path.join(BASE_DIR, "README.docx")
    doc.save(readme_docx_path)
    print(f"Generated README.docx at: {readme_docx_path} ({os.path.getsize(readme_docx_path)} bytes)")

if __name__ == "__main__":
    generate_files()
