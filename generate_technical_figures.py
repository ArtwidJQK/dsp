# -*- coding: utf-8 -*-
"""
Generate 11 technical figures for the technical report:
- 300 DPI, white background, Times New Roman font, clear Vietnamese labels.
- Saved in d:\dsp\LeTanDung_24150654\sources\figures (and local figures/)
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Setup fonts and style
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Liberation Serif']
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['figure.autolayout'] = True
plt.rcParams['mathtext.fontset'] = 'stix'

OUT_DIR = r"d:\dsp\LeTanDung_24150654\figures"
os.makedirs(OUT_DIR, exist_ok=True)
LOCAL_DIR = r"d:\Xử lý tín hiệu số\figures"
os.makedirs(LOCAL_DIR, exist_ok=True)

def save_fig(fig, name):
    for d in [OUT_DIR, LOCAL_DIR]:
        path = os.path.join(d, name)
        fig.savefig(path, dpi=300, facecolor='white', bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {name}")

# ==============================================================================
# HÌNH 2.1: LẤY MẪU VÀ PHỔ CHU KỲ HÓA (NYQUIST)
# ==============================================================================
def draw_fig_2_1():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.8))
    
    # Miền thời gian
    t = np.linspace(0, 1, 1000)
    sig = np.sin(2 * np.pi * 3 * t) + 0.5 * np.sin(2 * np.pi * 6 * t)
    ax1.plot(t, sig, 'b-', label='Tín hiệu liên tục $x(t)$', alpha=0.7)
    
    # Các mẫu rời rạc
    ts = np.linspace(0, 1, 17)
    sigs = np.sin(2 * np.pi * 3 * ts) + 0.5 * np.sin(2 * np.pi * 6 * ts)
    ax1.stem(ts, sigs, linefmt='r-', markerfmt='ro', basefmt='k-', label='Dãy mẫu $x[n] = x(n T_s)$')
    ax1.set_title('(a) Lấy mẫu trong miền thời gian ($T_s = 1/F_s$)')
    ax1.set_xlabel('Thời gian $t$ (giây)')
    ax1.set_ylabel('Biên độ')
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(loc='upper right', fontsize=9.5)
    
    # Miền tần số
    f = np.linspace(-25, 25, 1000)
    # Phổ tam giác chu kỳ
    def spectrum(freq, center):
        w = 4.0
        val = np.maximum(0, 1.0 - np.abs(freq - center) / w)
        return val
    
    spec = spectrum(f, -16) + spectrum(f, 0) + spectrum(f, 16)
    ax2.plot(f, spec, 'g-', lw=2)
    ax2.fill_between(f, 0, spec, color='green', alpha=0.15)
    ax2.axvline(-8, color='k', linestyle=':', label='$-F_s/2$ (Nyquist)')
    ax2.axvline(8, color='k', linestyle=':', label='$+F_s/2$ (Nyquist)')
    ax2.axvline(-16, color='r', linestyle='--', alpha=0.6, label='Bản sao phổ $-F_s$')
    ax2.axvline(16, color='r', linestyle='--', alpha=0.6, label='Bản sao phổ $+F_s$')
    ax2.set_title('(b) Chu kỳ hóa phổ theo định lý Nyquist ($F_s > 2f_{max}$)')
    ax2.set_xlabel('Tần số $f$ (kHz)')
    ax2.set_ylabel('Biên độ $|X(f)|$')
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(loc='upper right', fontsize=9)
    
    save_fig(fig, "fig_2_1_sampling.png")

# ==============================================================================
# HÌNH 2.2: GIẢN ĐỒ XUNG THỜI GIAN I2S PHILIPS
# ==============================================================================
def draw_fig_2_2():
    fig, ax = plt.subplots(figsize=(10, 3.8))
    
    # Trục thời gian
    t = np.arange(0, 20, 0.05)
    
    # BCLK (Square wave)
    bclk = np.where(np.sin(2 * np.pi * 0.5 * t) >= 0, 1, 0)
    
    # WS (Square wave with slower period, transition at t=2)
    # WS low for Left channel, high for Right
    ws = np.where(t < 10, 0, 1)
    
    # SD (Serial Data: 1 cycle delay after WS change)
    # MSB at t = 3, MSB-1 at t = 5, etc.
    sd = np.zeros_like(t)
    # simulate bits: bit0 (MSB) = 1, bit1 = 0, bit2 = 1, bit3 = 1
    sd[(t >= 3) & (t < 5)] = 1
    sd[(t >= 5) & (t < 7)] = 0
    sd[(t >= 7) & (t < 9)] = 1
    sd[(t >= 9) & (t < 11)] = 1
    sd[(t >= 13) & (t < 15)] = 1
    sd[(t >= 15) & (t < 17)] = 1
    
    # Plot traces
    offset = [4, 2, 0]
    ax.step(t, ws + offset[0], 'navy', lw=2, label='WS / LRCLK (0: Left, 1: Right)', where='post')
    ax.step(t, bclk + offset[1], 'darkgreen', lw=1.5, label='BCLK (Bit Clock: 1.024 MHz)', where='post')
    ax.step(t, sd + offset[2], 'darkred', lw=2, label='SD / DOUT (Dữ liệu âm thanh 24-bit)', where='post')
    
    # Annotations
    ax.axvline(2, color='gray', linestyle='--')
    ax.axvline(3, color='gray', linestyle='--')
    ax.annotate('Trễ 1 chu kỳ BCLK (Chuẩn Philips)', xy=(2.5, 0.5), xytext=(3.5, -0.8),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.2), fontsize=10)
    
    ax.text(4, 0.5, 'MSB', fontsize=10, fontweight='bold', color='darkred')
    ax.text(6, 0.5, 'MSB-1', fontsize=10, color='darkred')
    ax.text(8, 0.5, 'MSB-2', fontsize=10, color='darkred')
    
    ax.text(0.5, 4.5, 'Kênh Trái (Left Channel: L/R nối GND)', fontsize=10, color='navy', fontweight='bold')
    ax.text(11, 4.5, 'Kênh Phải (Right Channel)', fontsize=10, color='navy')
    
    ax.set_ylim(-1.5, 6)
    ax.set_yticks([])
    ax.set_xlabel('Chu kỳ thời gian đồng bộ')
    ax.set_title('Giản đồ thời gian chuẩn giao tiếp âm thanh I2S Philips (1-clock delay MSB)')
    ax.grid(True, linestyle=':', alpha=0.4)
    ax.legend(loc='upper right', fontsize=9.5)
    
    save_fig(fig, "fig_2_2_i2s_timing.png")

# ==============================================================================
# HÌNH 2.3: RÒ RỈ PHỔ VÀ ĐÁP ỨNG CỬA SỔ HANN
# ==============================================================================
def draw_fig_2_3():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.8))
    
    N = 256
    n = np.arange(N)
    # Tín hiệu sin không khớp chu kỳ (k = 16.35 bin)
    k_true = 16.35
    sig = np.sin(2 * np.pi * k_true * n / N)
    
    w_rect = np.ones(N)
    w_hann = 0.5 * (1.0 - np.cos(2 * np.pi * n / (N - 1)))
    
    X_rect = np.fft.rfft(sig * w_rect, n=N*4)
    X_hann = np.fft.rfft(sig * w_hann, n=N*4)
    
    f_bins = np.linspace(0, N/2, len(X_rect))
    mag_rect = 20 * np.log10(np.abs(X_rect) / np.max(np.abs(X_rect)) + 1e-12)
    mag_hann = 20 * np.log10(np.abs(X_hann) / np.max(np.abs(X_hann)) + 1e-12)
    
    # Plot dạng cửa sổ thời gian
    ax1.plot(n, w_rect, 'r--', label='Cửa sổ Chữ nhật (Rectangular)', lw=1.5)
    ax1.plot(n, w_hann, 'b-', label='Cửa sổ Hann (Hanning)', lw=2)
    ax1.set_title('(a) Hàm cửa sổ trong miền thời gian')
    ax1.set_xlabel('Mẫu $n$')
    ax1.set_ylabel('Trọng số $w[n]$')
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(loc='lower center', fontsize=9.5)
    
    # Plot phổ dB
    ax2.plot(f_bins, mag_rect, 'r--', label='Chữ nhật: Rò rỉ lớn (-13 dB búp phụ)', lw=1.2, alpha=0.8)
    ax2.plot(f_bins, mag_hann, 'b-', label='Hann: Búp phụ suy giảm nhanh (-31.5 dB)', lw=1.8)
    ax2.set_xlim(5, 30)
    ax2.set_ylim(-80, 5)
    ax2.set_title('(b) Phổ biên độ tương ứng (Hiện tượng rò rỉ phổ)')
    ax2.set_xlabel('Tần số chuẩn hóa (Bin phổ)')
    ax2.set_ylabel('Biên độ suy giảm (dB)')
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(loc='upper right', fontsize=9)
    
    save_fig(fig, "fig_2_3_hann_leakage.png")

# ==============================================================================
# HÌNH 2.4: NGUYÊN LÝ NỘI SUY PARABOL BẬC HAI (QI)
# ==============================================================================
def draw_fig_2_4():
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    
    k = 10
    p_true = -0.32
    # 3 điểm rời rạc
    # Parabola y(x) = a*(x - (k + p))^2 + y_max
    a = -8.0
    y_max = 25.0
    
    def quad(x):
        return a * (x - (k + p_true))**2 + y_max
    
    x_cont = np.linspace(k - 1.5, k + 1.5, 300)
    y_cont = quad(x_cont)
    
    x_bins = np.array([k - 1, k, k + 1])
    y_bins = quad(x_bins)
    
    ax.plot(x_cont, y_cont, 'b-', lw=2, label='Parabol nội suy liên tục $y(x)$')
    ax.stem(x_bins, y_bins, linefmt='k--', markerfmt='ko', basefmt=' ', label='3 bin rời rạc: $(k-1, \\alpha), (k, \\beta), (k+1, \\gamma)$')
    
    # Đỉnh thực tế
    x_peak = k + p_true
    y_peak = y_max
    ax.plot(x_peak, y_peak, 'r*', markersize=14, label='Đỉnh ước lượng $k + p$ ($p \\approx -0.32$)')
    ax.axvline(k, color='gray', linestyle=':', label='Bin cực đại rời rạc $k$')
    ax.axvline(x_peak, color='r', linestyle='--')
    
    # Labels for alpha, beta, gamma
    ax.text(k - 1 - 0.2, y_bins[0] - 1.5, '$\\alpha = \\mathrm{mag}[k-1]$', fontsize=10.5, color='black')
    ax.text(k - 0.1, y_bins[1] + 1.2, '$\\beta = \\mathrm{mag}[k]$', fontsize=10.5, color='black', fontweight='bold')
    ax.text(k + 1 - 0.1, y_bins[2] - 1.5, '$\\gamma = \\mathrm{mag}[k+1]$', fontsize=10.5, color='black')
    
    ax.annotate('Độ dịch phân số $p = 0.5\\frac{\\alpha - \\gamma}{\\alpha - 2\\beta + \\gamma}$',
                xy=(x_peak, y_peak), xytext=(k + 0.3, y_peak + 2.5),
                arrowprops=dict(arrowstyle='->', color='red', lw=1.5), fontsize=10.5, fontweight='bold', color='darkred')
    
    ax.set_xticks([k - 1, k, k + 1])
    ax.set_xticklabels(['Bin $k-1$', 'Bin $k$', 'Bin $k+1$'], fontsize=11)
    ax.set_ylabel('Biên độ phổ FFT')
    ax.set_title('Nguyên lý nội suy parabol bậc hai (Quadratic Interpolation) xác định đỉnh liên tục')
    ax.grid(True, linestyle='--', alpha=0.4)
    ax.legend(loc='lower left', fontsize=9.5)
    
    save_fig(fig, "fig_2_4_quadratic_interp.png")

# ==============================================================================
# HÌNH 2.5: ĐẶC TÍNH BẤT ĐIỀU HÒA (INHARMONICITY) CỦA ĐÀN PIANO
# ==============================================================================
def draw_fig_2_5():
    fig, ax = plt.subplots(figsize=(7.5, 4.0))
    
    m = np.arange(1, 9)
    f0 = 440.0 # A4
    B_demo = 0.0004 # Giá trị B điển hình cho dây trung âm piano (minh họa)
    
    f_harmonic = m * f0
    f_inharmonic = m * f0 * np.sqrt(1 + B_demo * (m**2))
    dev_hz = f_inharmonic - f_harmonic
    
    ax.plot(m, np.zeros_like(m), 'k--', label='Họa âm điều hòa lý thuyết ($m \\cdot f_0$)', lw=1.5)
    ax.plot(m, dev_hz, 'ro-', lw=2, label='Độ dạt tần số thực tế: $f_m - m f_0$ ($B = 0.0004$ minh họa)')
    
    for i, txt in enumerate(dev_hz):
        ax.annotate(f"+{txt:.2f} Hz", (m[i], dev_hz[i] + 0.3), fontsize=9, ha='center', color='darkred')
        
    ax.set_xlabel('Bậc họa âm $m$')
    ax.set_ylabel('Độ dạt tần số lên cao $\\Delta f_m$ (Hz)')
    ax.set_title('Sự sai lệch họa âm (Inharmonicity) theo phương trình Fletcher ($f_m = m f_0 \\sqrt{1 + B m^2}$)')
    ax.set_xticks(m)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='upper left', fontsize=10)
    
    # Ghi chú minh họa
    ax.text(4, -1.0, '* Lưu ý: Hệ số B = 0.0004 mang tính minh họa lý thuyết âm học, không phải số đo trực tiếp.',
            fontsize=9.5, style='italic', color='gray')
    ax.set_ylim(-1.5, max(dev_hz) + 1.5)
    
    save_fig(fig, "fig_2_5_inharmonicity.png")

# ==============================================================================
# HÌNH 3.1: SƠ ĐỒ KHỐI KIẾN TRÚC PHẦN CỨNG VÀ LUỒNG DỮ LIỆU
# ==============================================================================
def draw_fig_3_1():
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.axis('off')
    
    # Boxes
    boxes = [
        ("Sóng âm Piano\n(Acoustic Wave)", 0.05, 0.4, 0.14, 0.25, '#E8F0FE', '#1A73E8'),
        ("Microphone I2S\nINMP441 (MEMS)", 0.23, 0.4, 0.14, 0.25, '#CEEAD6', '#1E8E3E'),
        ("ESP32-S3 DMA RX\n(I2S Hardware)", 0.41, 0.4, 0.14, 0.25, '#FEF7E0', '#F9AB00'),
        ("Core DSP Pipeline\n(FFT Radix-2 + QI)", 0.59, 0.4, 0.15, 0.25, '#FCE8E6', '#D93025'),
        ("Embedded HTTP\n(esp_http_server)", 0.78, 0.4, 0.15, 0.25, '#F3E8FD', '#9334E6')
    ]
    
    for text, x, y, w, h, bg, border in boxes:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02", ec=border, fc=bg, lw=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=10.5, fontweight='bold', color='#202124')
        
    # Arrows
    for i in range(len(boxes) - 1):
        x1 = boxes[i][1] + boxes[i][3]
        y1 = boxes[i][2] + boxes[i][4]/2
        x2 = boxes[i+1][1]
        y2 = boxes[i+1][2] + boxes[i+1][4]/2
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", lw=2, color="#3C4043"))
        
    # User feedback loop
    rect_ui = patches.FancyBboxPatch((0.59, 0.05), 0.34, 0.22, boxstyle="round,pad=0.02", ec='#1B365D', fc='#E8EAED', lw=2)
    ax.add_patch(rect_ui)
    ax.text(0.76, 0.16, "Giao diện Web Celestial Tuner\n(HTML5/CSS3/JS qua Wi-Fi AP / STA)", ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Arrow down from HTTP to UI
    ax.annotate('', xy=(0.855, 0.27), xytext=(0.855, 0.4),
                arrowprops=dict(arrowstyle="->", lw=2, color="#3C4043"))
    ax.text(0.865, 0.33, "JSON /api/data", fontsize=9, color='purple')
    
    ax.set_title("Sơ đồ khối kiến trúc phần cứng và luồng xử lý tín hiệu thời gian thực", fontsize=12, fontweight='bold', pad=15)
    save_fig(fig, "fig_3_1_system_block.png")

# ==============================================================================
# HÌNH 3.2: SƠ ĐỒ KẾT NỐI CHÂN TÍN HIỆU PHẦN CỨNG
# ==============================================================================
def draw_fig_3_2():
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.axis('off')
    
    # Draw ESP32-S3 Box
    rect_esp = patches.FancyBboxPatch((0.55, 0.1), 0.38, 0.8, boxstyle="round,pad=0.03", ec='#1B365D', fc='#F4F6F9', lw=2.5)
    ax.add_patch(rect_esp)
    ax.text(0.74, 0.83, "ESP32-S3 N16R8\n(Microcontroller)", ha='center', va='center', fontsize=12, fontweight='bold', color='#1B365D')
    
    # Draw INMP441 Box
    rect_mic = patches.FancyBboxPatch((0.07, 0.1), 0.32, 0.8, boxstyle="round,pad=0.03", ec='#1E8E3E', fc='#E6F4EA', lw=2.5)
    ax.add_patch(rect_mic)
    ax.text(0.23, 0.83, "INMP441 MEMS MIC\n(I2S Digital Output)", ha='center', va='center', fontsize=12, fontweight='bold', color='#1E8E3E')
    
    # Pins
    connections = [
        ("SCK / BCLK", "GPIO 4 (Bit Clock)", 0.68, '#1A73E8'),
        ("WS / LRCLK", "GPIO 5 (Word Select)", 0.56, '#D93025'),
        ("SD / DOUT", "GPIO 6 (Data In)", 0.44, '#F9AB00'),
        ("L/R", "GND (Left Channel)", 0.32, '#5F6368'),
        ("VDD", "3.3V (Nguồn cấp)", 0.20, '#E37400'),
        ("GND", "GND (Đất chung)", 0.12, '#3C4043')
    ]
    
    for pin_m, pin_e, y_pos, color in connections:
        # Mic pin label
        ax.text(0.36, y_pos, pin_m, ha='right', va='center', fontsize=10, fontweight='bold', color='#202124')
        # ESP pin label
        ax.text(0.58, y_pos, pin_e, ha='left', va='center', fontsize=10, fontweight='bold', color='#202124')
        # Connecting line
        ax.plot([0.37, 0.57], [y_pos, y_pos], color=color, lw=2.2, solid_capstyle='round')
        ax.plot(0.37, y_pos, 'o', color=color, markersize=5)
        ax.plot(0.57, y_pos, '>', color=color, markersize=6)
        
    ax.set_title("Sơ đồ đấu nối chân phần cứng (Hardware Pinout) giữa INMP441 và ESP32-S3", fontsize=12, fontweight='bold', pad=10)
    save_fig(fig, "fig_3_2_wiring_pinout.png")

# ==============================================================================
# HÌNH 3.3: KIẾN TRÚC FIRMWARE FREERTOS
# ==============================================================================
def draw_fig_3_3():
    fig, ax = plt.subplots(figsize=(9.5, 4.4))
    ax.axis('off')
    
    # Core 1 (DSP)
    rect_c1 = patches.FancyBboxPatch((0.05, 0.1), 0.42, 0.8, boxstyle="round,pad=0.03", ec='#D93025', fc='#FCE8E6', lw=2)
    ax.add_patch(rect_c1)
    ax.text(0.26, 0.83, "CORE 1: XỬ LÝ DSP THỜI GIAN THỰC\n(Audio Processing Task, Priority 5)", ha='center', va='center', fontsize=11, fontweight='bold', color='#D93025')
    
    steps_c1 = [
        "1. Đọc DMA I2S (2048 mẫu hop)",
        "2. Đệm trượt 50% gối đầu (4096 mẫu)",
        "3. Khử DC & Nhân cửa sổ Hann",
        "4. Biến đổi FFT Radix-2 4096 điểm",
        "5. Chấm điểm giả thuyết & Quadratic Interp",
        "6. Bộ lọc ổn định 2-khung & Note mapping"
    ]
    for i, s in enumerate(steps_c1):
        ax.text(0.08, 0.70 - i*0.10, s, fontsize=9.5, color='#202124')
        
    # Core 0 (Network & Web Server)
    rect_c0 = patches.FancyBboxPatch((0.53, 0.1), 0.42, 0.8, boxstyle="round,pad=0.03", ec='#1A73E8', fc='#E8F0FE', lw=2)
    ax.add_patch(rect_c0)
    ax.text(0.74, 0.83, "CORE 0: MẠNG & WEB SERVER\n(HTTP Server Task + Wi-Fi Stack)", ha='center', va='center', fontsize=11, fontweight='bold', color='#1A73E8')
    
    steps_c0 = [
        "1. Wi-Fi SoftAP / Station Management",
        "2. GET / (Phục vụ file nhúng index.html)",
        "3. GET /api/data (Phục vụ JSON snapshot)",
        "4. Trả lời HTTP request cực nhanh (< 2 ms)",
        "5. Không làm gián đoạn chu kỳ lấy mẫu DSP"
    ]
    for i, s in enumerate(steps_c0):
        ax.text(0.56, 0.70 - i*0.11, s, fontsize=9.5, color='#202124')
        
    # Shared Data Structure (Spinlock)
    rect_sh = patches.FancyBboxPatch((0.35, 0.35), 0.30, 0.22, boxstyle="round,pad=0.02", ec='#E37400', fc='#FEF7E0', lw=2.5)
    ax.add_patch(rect_sh)
    ax.text(0.50, 0.48, "CẤU TRÚC DỮ LIỆU DÙNG CHUNG\ns_latest_pitch (Thread-Safe)", ha='center', va='center', fontsize=10, fontweight='bold', color='#E37400')
    ax.text(0.50, 0.40, "Bảo vệ bởi portENTER_CRITICAL\n(&s_pitch_mux)", ha='center', va='center', fontsize=8.5, color='#5F6368')
    
    # Bidirectional synchronization arrows
    ax.annotate('', xy=(0.35, 0.46), xytext=(0.28, 0.46), arrowprops=dict(arrowstyle="->", lw=2, color="#D93025"))
    ax.text(0.29, 0.49, "Ghi snapshot", fontsize=8.5, color="#D93025")
    
    ax.annotate('', xy=(0.65, 0.46), xytext=(0.72, 0.46), arrowprops=dict(arrowstyle="<-", lw=2, color="#1A73E8"))
    ax.text(0.66, 0.49, "Đọc snapshot", fontsize=8.5, color="#1A73E8")
    
    ax.set_title("Kiến trúc Firmware đa nhiệm thời gian thực trên FreeRTOS (ESP32-S3 Dual-Core)", fontsize=12, fontweight='bold', pad=10)
    save_fig(fig, "fig_3_3_freertos_tasks.png")

# ==============================================================================
# HÌNH 3.4: BỘ ĐỆM TRƯỢT 50% GỐI ĐẦU (ROLLING BUFFER)
# ==============================================================================
def draw_fig_3_4():
    fig, ax = plt.subplots(figsize=(9.5, 4.0))
    ax.axis('off')
    
    # Frame t
    ax.text(0.05, 0.82, "Khung $t$ (256 ms, 4096 mẫu):", fontsize=10.5, fontweight='bold')
    r1_old = patches.Rectangle((0.32, 0.75), 0.30, 0.15, ec='black', fc='#D0E2FF', lw=1.5)
    r1_new = patches.Rectangle((0.62, 0.75), 0.30, 0.15, ec='black', fc='#A7C7E7', lw=1.5)
    ax.add_patch(r1_old)
    ax.add_patch(r1_new)
    ax.text(0.47, 0.82, "2048 mẫu cũ", ha='center', va='center', fontsize=9.5)
    ax.text(0.77, 0.82, "2048 mẫu mới (Hop 1)", ha='center', va='center', fontsize=9.5, fontweight='bold')
    
    # Shift action
    ax.annotate('', xy=(0.47, 0.58), xytext=(0.77, 0.75),
                arrowprops=dict(arrowstyle="->", lw=2, color="#D93025", connectionstyle="arc3,rad=-0.2"))
    ax.text(0.65, 0.63, "Trượt 50% mẫu (Hop Shift = 128 ms)", fontsize=9.5, color='#D93025', fontweight='bold')
    
    # Frame t+1
    ax.text(0.05, 0.45, "Khung $t+1$ (256 ms, 4096 mẫu):", fontsize=10.5, fontweight='bold')
    r2_old = patches.Rectangle((0.32, 0.38), 0.30, 0.15, ec='black', fc='#A7C7E7', lw=1.5)
    r2_new = patches.Rectangle((0.62, 0.38), 0.30, 0.15, ec='black', fc='#85B1DE', lw=1.5)
    ax.add_patch(r2_old)
    ax.add_patch(r2_new)
    ax.text(0.47, 0.45, "2048 mẫu cũ (giữ lại)", ha='center', va='center', fontsize=9.5)
    ax.text(0.77, 0.45, "2048 mẫu mới (Hop 2)", ha='center', va='center', fontsize=9.5, fontweight='bold')
    
    # Timeline
    ax.annotate('', xy=(0.95, 0.15), xytext=(0.30, 0.15), arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    ax.text(0.95, 0.10, "Thời gian $t$", fontsize=10)
    
    ax.plot([0.32, 0.32], [0.12, 0.18], 'k-')
    ax.plot([0.62, 0.62], [0.12, 0.18], 'k-')
    ax.plot([0.92, 0.92], [0.12, 0.18], 'k-')
    ax.text(0.32, 0.08, "0 ms", ha='center', fontsize=9)
    ax.text(0.62, 0.08, "128 ms", ha='center', fontsize=9)
    ax.text(0.92, 0.08, "256 ms", ha='center', fontsize=9)
    
    ax.set_title("Cơ chế đệm trượt liên tục 50% gối đầu (Overlapping Rolling Buffer Pipeline)", fontsize=12, fontweight='bold', pad=10)
    save_fig(fig, "fig_3_4_rolling_buffer.png")

# ==============================================================================
# HÌNH 3.5: LƯU ĐỒ CHẤM ĐIỂM GIẢ THUYẾT HỌA ÂM
# ==============================================================================
def draw_fig_3_5():
    fig, ax = plt.subplots(figsize=(8.5, 6.0))
    ax.axis('off')
    
    # Flowchart blocks
    blocks = [
        ("Đỉnh phổ ứng viên $f_{\\mathrm{peak}}$\n(Local Peaks, Prominence $\\geq$ 2.2×)", 0.25, 0.86, 0.50, 0.10, '#E8F0FE'),
        ("Sinh giả thuyết: $f_{\\mathrm{hyp}} = f_{\\mathrm{peak}} / m$\n($m \\in \\{1, 2, 3, 4, 5, 6\\}$)", 0.25, 0.72, 0.50, 0.10, '#FEF7E0'),
        ("Dò tìm các đỉnh họa âm thực tế\n(Kiểm tra tại $1 f_{\\mathrm{hyp}}, 2 f_{\\mathrm{hyp}}, \\dots, 6 f_{\\mathrm{hyp}}$)", 0.25, 0.58, 0.50, 0.10, '#E6F4EA'),
        ("Kiểm tra có họa âm lẻ hay không?\n(m=1, 3 hoặc 5)", 0.25, 0.44, 0.50, 0.10, '#FCE8E6'),
        ("Quy tắc xử lý dải trầm (< 110 Hz):\nCứu $m=1$ bằng $m=3$ & Chặn nhiễu 50 Hz", 0.25, 0.30, 0.50, 0.10, '#F3E8FD'),
        ("Tính điểm $\\mathrm{Score}_{\\mathrm{final}}$ và chọn giả thuyết cao nhất\nTinh chỉnh tần số bằng Quadratic Interpolation (QI)", 0.15, 0.14, 0.70, 0.11, '#CEEAD6')
    ]
    
    for text, x, y, w, h, bg in blocks:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02", ec='#3C4043', fc=bg, lw=1.8)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=9.5, fontweight='bold', color='#202124')
        
    for i in range(len(blocks) - 1):
        ax.annotate('', xy=(0.50, blocks[i+1][2] + blocks[i+1][4]), xytext=(0.50, blocks[i][2]),
                    arrowprops=dict(arrowstyle="->", lw=2, color="#3C4043"))
        
    # Penalty branch from "Kiểm tra họa âm lẻ"
    ax.annotate('Không có họa âm lẻ:\nPhạt × 0.05 (Subharmonic rejection)', xy=(0.75, 0.49), xytext=(0.80, 0.49),
                fontsize=8.5, color='#D93025', fontweight='bold')
    
    ax.set_title("Lưu đồ thuật toán đánh giá giả thuyết họa âm (Harmonic-Aware Scoring Logic)", fontsize=12, fontweight='bold', pad=10)
    save_fig(fig, "fig_3_5_harmonic_flowchart.png")

# ==============================================================================
# HÌNH 3.6: LUỒNG POLLING DỮ LIỆU GIAO DIỆN WEB
# ==============================================================================
def draw_fig_3_6():
    fig, ax = plt.subplots(figsize=(9.5, 4.2))
    ax.axis('off')
    
    # Client & Server
    rect_client = patches.FancyBboxPatch((0.05, 0.1), 0.38, 0.8, boxstyle="round,pad=0.03", ec='#1A73E8', fc='#E8F0FE', lw=2)
    ax.add_patch(rect_client)
    ax.text(0.24, 0.83, "TRÌNH DUYỆT NGƯỜI DÙNG (CLIENT)\n(Smartphone / Tablet / Laptop)", ha='center', va='center', fontsize=11, fontweight='bold', color='#1A73E8')
    
    ui_elements = [
        "• Timer vòng lặp Polling: 125 ms",
        "• Hàm JavaScript: fetch('/api/data')",
        "• Cập nhật kim đo Tuner Needle (-50..+50 cent)",
        "• Đổi màu hào quang: Xanh / Đỏ / Tím / Xám",
        "• Sáng phím đàn tương ứng trên bàn phím C2-C8"
    ]
    for i, e in enumerate(ui_elements):
        ax.text(0.08, 0.68 - i*0.11, e, fontsize=9.5, color='#202124')
        
    rect_server = patches.FancyBboxPatch((0.57, 0.1), 0.38, 0.8, boxstyle="round,pad=0.03", ec='#1B365D', fc='#F4F6F9', lw=2)
    ax.add_patch(rect_server)
    ax.text(0.76, 0.83, "MÁY CHỦ NHÚNG ESP32-S3 (SERVER)\n(esp_http_server cổng 80)", ha='center', va='center', fontsize=11, fontweight='bold', color='#1B365D')
    
    srv_elements = [
        "• Nhận HTTP GET /api/data",
        "• Lấy snapshot s_latest_pitch an toàn luồng",
        "• Đóng gói JSON (freq, note, cents, valid...)",
        "• Gửi phản hồi HTTP 200 OK (< 2 ms)",
        "• Tiếp tục xử lý I2S DMA không bị ngắt quãng"
    ]
    for i, e in enumerate(srv_elements):
        ax.text(0.60, 0.68 - i*0.11, e, fontsize=9.5, color='#202124')
        
    # Arrows between Client & Server
    ax.annotate('', xy=(0.57, 0.55), xytext=(0.43, 0.55), arrowprops=dict(arrowstyle="->", lw=2, color="#1A73E8"))
    ax.text(0.50, 0.58, "HTTP GET /api/data", ha='center', fontsize=9.5, fontweight='bold', color='#1A73E8')
    
    ax.annotate('', xy=(0.43, 0.35), xytext=(0.57, 0.35), arrowprops=dict(arrowstyle="->", lw=2, color="#1E8E3E"))
    ax.text(0.50, 0.38, "JSON Response (200 OK)", ha='center', fontsize=9.5, fontweight='bold', color='#1E8E3E')
    
    ax.set_title("Kiến trúc truyền thông thời gian thực và luồng Polling dữ liệu giữa Web UI và ESP32-S3", fontsize=12, fontweight='bold', pad=10)
    save_fig(fig, "fig_3_6_ui_polling_flow.png")

def main():
    print("Generating 11 technical figures...")
    draw_fig_2_1()
    draw_fig_2_2()
    draw_fig_2_3()
    draw_fig_2_4()
    draw_fig_2_5()
    draw_fig_3_1()
    draw_fig_3_2()
    draw_fig_3_3()
    draw_fig_3_4()
    draw_fig_3_5()
    draw_fig_3_6()
    print("All 11 figures generated successfully!")

if __name__ == "__main__":
    main()
