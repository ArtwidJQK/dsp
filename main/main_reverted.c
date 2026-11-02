#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <stdbool.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_err.h"
#include "esp_timer.h"
#include "driver/gpio.h"
#include "driver/i2s_std.h"
#include "nvs_flash.h"
#include "esp_netif.h"
#include "esp_event.h"
#include "esp_wifi.h"
#include "esp_mac.h"
#include "esp_http_server.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// ==============================================================================
// 1. CẤU HÌNH PHẦN CỨNG & DSP (BẢO TOÀN NGUYÊN BẢN)
// ==============================================================================
#define I2S_MIC_BCLK_PIN      GPIO_NUM_4
#define I2S_MIC_WS_PIN        GPIO_NUM_5
#define I2S_MIC_DATA_IN_PIN   GPIO_NUM_6

#define SAMPLE_RATE_HZ        16000
#define FFT_N                 4096   // Phân tích N = 4096 điểm (256 ms)
#define HOP_SIZE              2048   // Độ trượt 50% overlap = 2048 mẫu (128 ms)
#define BIN_RESOLUTION_HZ     ((float)SAMPLE_RATE_HZ / (float)FFT_N) // 3.90625 Hz/bin

// Dải tần số cơ bản của đàn Piano: A0 (27.5 Hz) đến C8 (4186.0 Hz)
#define PIANO_MIN_FREQ_HZ     27.5f
#define PIANO_MAX_FREQ_HZ     4186.0f
#define PIANO_MIN_BIN         7     // 7 * 3.90625 = 27.34 Hz
#define PIANO_MAX_BIN         1072  // 1072 * 3.90625 = 4187.5 Hz

#define MAX_CANDIDATE_PEAKS   24
#define PITCH_HISTORY_LEN     5

// Ngưỡng năng lượng AC tối thiểu (được tối ưu để bắt nhạy onset nốt)
#define MIN_AC_RMS_NORM       0.0020f

static const char *TAG = "REALTIME_TUNER";

// Bảng cửa sổ Hann tiền tính toán
static float s_hann_window[FFT_N];

// Bộ đệm làm việc cho DSP & Rolling Buffer (DRAM)
static uint32_t *s_stereo_buf      = NULL; // 2048 cặp stereo = 4096 từ 32-bit (16 KB)
static int32_t  *s_hop_samples     = NULL; // 2048 mẫu mono mới thu nhận (8 KB)
static int32_t  *s_rolling_samples = NULL; // 4096 mẫu mono cửa sổ trượt phân tích (16 KB)
static float    *s_fft_real        = NULL; // 4096 float (16 KB)
static float    *s_fft_imag        = NULL; // 4096 float (16 KB)
static float    *s_magnitude       = NULL; // 2048 float (8 KB)

static i2s_chan_handle_t rx_handle = NULL;

static int s_left_nonzeros = 0;
static int s_right_nonzeros = 0;

// Các trạng thái phân loại tín hiệu
typedef enum {
    PITCH_NO_SIGNAL = 0,
    PITCH_WEAK_SIGNAL = 1,
    PITCH_VALID_PITCH = 2
} pitch_state_t;

typedef struct {
    int   bin;
    float raw_freq;
    float mag;
    float local_floor;
    float prominence;
    float snr_db;
    float score;
    int   harmonics_found;
} peak_candidate_t;

// Cấu trúc lọc ổn định thời gian (Temporal Stability Filter)
typedef struct {
    float f0;
    float confidence;
    bool  is_valid;
    uint32_t frame;
} pitch_history_t;

static pitch_history_t s_history[PITCH_HISTORY_LEN];
static int s_hist_count = 0;
static int s_hist_idx = 0;
static int s_consecutive_valid = 0;

// ==============================================================================
// 2. TẦNG THU NHẬN I2S STEREO ĐÃ ĐƯỢC XÁC THỰC (GIỮ NGUYÊN)
// ==============================================================================
static esp_err_t init_i2s_microphone(void)
{
    gpio_set_pull_mode(I2S_MIC_DATA_IN_PIN, GPIO_PULLDOWN_ONLY);

    i2s_chan_config_t chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_AUTO, I2S_ROLE_MASTER);
    chan_cfg.dma_desc_num = 16;
    chan_cfg.dma_frame_num = 256;

    esp_err_t ret = i2s_new_channel(&chan_cfg, NULL, &rx_handle);
    if (ret != ESP_OK) return ret;

    i2s_std_config_t std_cfg = {
        .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(SAMPLE_RATE_HZ),
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_STEREO),
        .gpio_cfg = {
            .mclk = I2S_GPIO_UNUSED,
            .bclk = I2S_MIC_BCLK_PIN,
            .ws   = I2S_MIC_WS_PIN,
            .dout = I2S_GPIO_UNUSED,
            .din  = I2S_MIC_DATA_IN_PIN,
            .invert_flags = {
                .mclk_inv = false,
                .bclk_inv = false,
                .ws_inv   = false,
            },
        },
    };
    std_cfg.slot_cfg.slot_bit_width = I2S_SLOT_BIT_WIDTH_32BIT;

    ret = i2s_channel_init_std_mode(rx_handle, &std_cfg);
    if (ret != ESP_OK) return ret;

    return i2s_channel_enable(rx_handle);
}

static esp_err_t read_active_audio_samples(int32_t *out_samples, size_t samples_count, size_t *samples_read)
{
    size_t bytes_read = 0;
    esp_err_t ret = i2s_channel_read(rx_handle, s_stereo_buf, samples_count * 2 * sizeof(uint32_t), &bytes_read, portMAX_DELAY);
    if (ret != ESP_OK) {
        *samples_read = 0;
        return ret;
    }

    size_t stereo_pairs = bytes_read / (2 * sizeof(uint32_t));
    int l_nz = 0;
    int r_nz = 0;
    for (size_t i = 0; i < stereo_pairs; i++) {
        int32_t s_left  = (int32_t)s_stereo_buf[2 * i] >> 8;
        int32_t s_right = (int32_t)s_stereo_buf[2 * i + 1] >> 8;
        if (s_left != 0) l_nz++;
        if (s_right != 0) r_nz++;
        out_samples[i] = (s_left != 0) ? s_left : s_right;
    }
    s_left_nonzeros = l_nz;
    s_right_nonzeros = r_nz;
    *samples_read = stereo_pairs;
    return ESP_OK;
}

// ==============================================================================
// 3. THUẬT TOÁN DSP & FFT CỐT LÕI (GIỮ NGUYÊN)
// ==============================================================================
static void init_hann_window(void)
{
    for (int n = 0; n < FFT_N; n++) {
        s_hann_window[n] = 0.5f * (1.0f - cosf(2.0f * (float)M_PI * (float)n / (float)(FFT_N - 1)));
    }
}

static void fft_radix2(float *real, float *imag, int n)
{
    int j = 0;
    for (int i = 0; i < n - 1; i++) {
        if (i < j) {
            float tr = real[i];
            real[i] = real[j];
            real[j] = tr;

            float ti = imag[i];
            imag[i] = imag[j];
            imag[j] = ti;
        }
        int k = n >> 1;
        while (k <= j) {
            j -= k;
            k >>= 1;
        }
        j += k;
    }

    for (int len = 2; len <= n; len <<= 1) {
        float angle = -2.0f * (float)M_PI / (float)len;
        float wlen_r = cosf(angle);
        float wlen_i = sinf(angle);
        int half_len = len >> 1;

        for (int i = 0; i < n; i += len) {
            float w_r = 1.0f;
            float w_i = 0.0f;

            for (int k = 0; k < half_len; k++) {
                int u_idx = i + k;
                int v_idx = i + k + half_len;

                float u_r = real[u_idx];
                float u_i = imag[u_idx];

                float v_r = real[v_idx] * w_r - imag[v_idx] * w_i;
                float v_i = real[v_idx] * w_i + imag[v_idx] * w_r;

                real[u_idx] = u_r + v_r;
                imag[u_idx] = u_i + v_i;

                real[v_idx] = u_r - v_r;
                imag[v_idx] = u_i - v_i;

                float next_w_r = w_r * wlen_r - w_i * wlen_i;
                float next_w_i = w_r * wlen_i + w_i * wlen_r;
                w_r = next_w_r;
                w_i = next_w_i;
            }
        }
    }
}

// Đo sàn nhiễu cục bộ bằng trung vị 24 bin lân cận (loại trừ búp sóng chính +/- 2 bin)
static float calculate_local_noise_floor(const float *mag, int bin, int num_bins)
{
    float neighbors[24];
    int count = 0;

    int left_start = (bin - 12 < PIANO_MIN_BIN) ? PIANO_MIN_BIN : bin - 12;
    int left_end   = bin - 3;
    for (int k = left_start; k <= left_end && count < 24; k++) {
        neighbors[count++] = mag[k];
    }

    int right_start = bin + 3;
    int right_end   = (bin + 12 >= num_bins) ? num_bins - 1 : bin + 12;
    for (int k = right_start; k <= right_end && count < 24; k++) {
        neighbors[count++] = mag[k];
    }

    if (count == 0) return 0.2f;

    // Sắp xếp chèn tìm trung vị
    for (int i = 1; i < count; i++) {
        float val = neighbors[i];
        int j = i - 1;
        while (j >= 0 && neighbors[j] > val) {
            neighbors[j + 1] = neighbors[j];
            j--;
        }
        neighbors[j + 1] = val;
    }

    float median = neighbors[count / 2];
    if (median < 0.05f) median = 0.05f;
    return median;
}

// ==============================================================================
// 4. ĐÁNH GIÁ TÍNH NHẤT QUÁN HỌA ÂM (SUBHARMONIC HYPOTHESIS SCORING)
// ==============================================================================
typedef struct {
    int   target_k;
    int   peak_w;
    float peak_freq;
    float interp_f0;
    float mag;
    float local_floor;
    float prom;
    float snr_db;
    bool  is_local_peak;
    bool  pass_gate;
} diag_harm_info_t;

typedef struct {
    float base_f;
    int   divisor;
    float test_f;
    float raw_score;
    float final_score;
    int   h_count;
    uint8_t h_mask;
    int   dominant_bin;
    bool  penalty_no_odd;
    bool  penalty_missing_m1;
    bool  penalty_missing_m1_rescued;
    bool  penalty_bass_guard;
    diag_harm_info_t harms[4];
} diag_hypothesis_t;

static float evaluate_harmonic_hypothesis(const float *magnitude, int num_bins, float hyp_f, 
                                          int *out_h_count, uint8_t *out_h_mask, int *out_dominant_bin,
                                          diag_hypothesis_t *diag_out)
{
    if (diag_out) {
        memset(diag_out, 0, sizeof(diag_hypothesis_t));
        diag_out->test_f = hyp_f;
    }

    if (hyp_f < PIANO_MIN_FREQ_HZ || hyp_f > PIANO_MAX_FREQ_HZ) {
        if (out_h_count) *out_h_count = 0;
        if (out_h_mask) *out_h_mask = 0;
        if (out_dominant_bin) *out_dominant_bin = 0;
        return 0.0f;
    }

    float hyp_k = hyp_f / BIN_RESOLUTION_HZ;
    int h_count = 0;
    uint8_t h_mask = 0;
    float total_energy = 0.0f;
    float max_found_mag = 0.0f;
    int dominant_bin = (int)roundf(hyp_k);

    for (int m = 1; m <= 6; m++) {
        int target_k = (int)roundf((float)m * hyp_k);
        if (target_k >= num_bins - 2) break;

        int w_start = (target_k - 2 < 1) ? 1 : target_k - 2;
        int w_end   = (target_k + 2 >= num_bins - 1) ? num_bins - 2 : target_k + 2;

        int peak_w = w_start;
        float max_v = magnitude[w_start];
        for (int w = w_start + 1; w <= w_end; w++) {
            if (magnitude[w] > max_v) {
                max_v = magnitude[w];
                peak_w = w;
            }
        }

        bool is_local_peak = (peak_w > 0 && peak_w < num_bins - 1 &&
                              magnitude[peak_w] >= magnitude[peak_w - 1] &&
                              magnitude[peak_w] >= magnitude[peak_w + 1]);

        float local_floor = calculate_local_noise_floor(magnitude, peak_w, num_bins);
        float prom = max_v / (local_floor > 0.05f ? local_floor : 0.05f);

        // Họa âm được công nhận nếu là đỉnh cục bộ có độ nhô >= 2.2x và biên độ >= 1.0
        bool pass_gate = (is_local_peak && prom >= 2.2f && max_v >= 1.0f);
        if (pass_gate) {
            h_count++;
            h_mask |= (1 << (m - 1));
            total_energy += (1.0f / sqrtf((float)m)) * log1pf(prom) * sqrtf(max_v);
            if (max_v > max_found_mag) {
                max_found_mag = max_v;
                dominant_bin = peak_w;
            }
        }

        if (diag_out && m <= 4) {
            int idx = m - 1;
            diag_out->harms[idx].target_k = target_k;
            diag_out->harms[idx].peak_w = peak_w;
            diag_out->harms[idx].peak_freq = (float)peak_w * BIN_RESOLUTION_HZ;
            diag_out->harms[idx].mag = max_v;
            diag_out->harms[idx].local_floor = local_floor;
            diag_out->harms[idx].prom = prom;
            diag_out->harms[idx].snr_db = 20.0f * log10f(prom > 0.1f ? prom : 0.1f);
            diag_out->harms[idx].is_local_peak = is_local_peak;
            diag_out->harms[idx].pass_gate = pass_gate;

            if (peak_w > 0 && peak_w < num_bins - 1) {
                float alpha = magnitude[peak_w - 1];
                float beta  = magnitude[peak_w];
                float gamma = magnitude[peak_w + 1];
                float denom = alpha - 2.0f * beta + gamma;
                float p = (fabsf(denom) > 1e-6f) ? 0.5f * (alpha - gamma) / denom : 0.0f;
                if (p < -0.5f) p = -0.5f;
                if (p >  0.5f) p =  0.5f;
                diag_out->harms[idx].interp_f0 = (((float)peak_w + p) * BIN_RESOLUTION_HZ) / (float)m;
            } else {
                diag_out->harms[idx].interp_f0 = ((float)peak_w * BIN_RESOLUTION_HZ) / (float)m;
            }
        }
    }

    if (h_count == 0) {
        if (out_h_count) *out_h_count = 0;
        if (out_h_mask) *out_h_mask = 0;
        if (out_dominant_bin) *out_dominant_bin = dominant_bin;
        if (diag_out) {
            diag_out->h_count = 0;
            diag_out->h_mask = 0;
            diag_out->raw_score = 0.0f;
            diag_out->final_score = 0.0f;
        }
        return 0.0f;
    }

    // 1. Điểm số cơ sở từ năng lượng họa âm và tính nhất quán
    float raw_score = total_energy * (1.0f + 0.40f * (float)(h_count - 1));
    float score = raw_score;

    bool pen_no_odd = false;
    bool pen_missing_m1 = false;
    bool pen_missing_m1_rescued = false;
    bool pen_bass_guard = false;

    // 2. Chống ảo ảnh Octave-down (Subharmonic phantom):
    bool has_odd = (h_mask & 0x15) != 0; // bit 0 (m=1), bit 2 (m=3), bit 4 (m=5) -> 0x01 | 0x04 | 0x10 = 0x15
    if (!has_odd) {
        score *= 0.05f; // Phạt nặng nếu hoàn toàn vắng bóng họa âm lẻ
        pen_no_odd = true;
    } else {
        // Nếu m=1 vắng mặt nhưng có cả m=2 và m=3: Nốt piano bị suy giảm tần số cơ bản do loa nhỏ
        if ((h_mask & 0x01) == 0) {
            if ((h_mask & 0x02) != 0 && (h_mask & 0x04) != 0) {
                score *= 0.85f; // Có m=2 và m=3: Bằng chứng rất mạnh cho nốt thật
                pen_missing_m1_rescued = true;
            } else {
                score *= 0.20f;
                pen_missing_m1 = true;
            }
        }
    }

    // 3. Xử lý dải hạ âm (< 110 Hz, k < 28) tránh nhiễu điện lưới 50Hz/100Hz:
    if (hyp_k < 28.0f) {
        if (h_count < 3 || max_found_mag < 14.0f) {
            score *= 0.10f;
            pen_bass_guard = true;
        }
    }

    if (diag_out) {
        diag_out->raw_score = raw_score;
        diag_out->final_score = score;
        diag_out->h_count = h_count;
        diag_out->h_mask = h_mask;
        diag_out->dominant_bin = dominant_bin;
        diag_out->penalty_no_odd = pen_no_odd;
        diag_out->penalty_missing_m1 = pen_missing_m1;
        diag_out->penalty_missing_m1_rescued = pen_missing_m1_rescued;
        diag_out->penalty_bass_guard = pen_bass_guard;
    }

    if (out_h_count) *out_h_count = h_count;
    if (out_h_mask)  *out_h_mask  = h_mask;
    if (out_dominant_bin) *out_dominant_bin = dominant_bin;
    return score;
}

// ==============================================================================
// 5. LỌC ỔN ĐỊNH THỜI GIAN (TEMPORAL STABILITY & OUTLIER REJECTION)
// ==============================================================================
static float update_temporal_stability(float raw_f0, float confidence, bool is_valid, bool *out_stable)
{
    s_history[s_hist_idx].f0 = raw_f0;
    s_history[s_hist_idx].confidence = confidence;
    s_history[s_hist_idx].is_valid = is_valid;
    s_hist_idx = (s_hist_idx + 1) % PITCH_HISTORY_LEN;
    if (s_hist_count < PITCH_HISTORY_LEN) s_hist_count++;

    if (!is_valid) {
        if (s_consecutive_valid > 0) s_consecutive_valid--;
        *out_stable = false;
        return 0.0f;
    }

    s_consecutive_valid++;

    // Thu thập các ước lượng gần đây khớp với raw_f0 trong khoảng +/- 3.5% (~50 cent)
    float close_f0[PITCH_HISTORY_LEN];
    int close_count = 0;
    for (int i = 0; i < s_hist_count; i++) {
        if (s_history[i].is_valid) {
            float diff = fabsf(s_history[i].f0 - raw_f0);
            if (diff / raw_f0 < 0.035f) {
                close_f0[close_count++] = s_history[i].f0;
            }
        }
    }

    // Nếu có ít nhất 2 ước lượng liên tiếp gần nhau: nốt ổn định!
    if (close_count >= 2 || s_consecutive_valid >= 2) {
        for (int i = 0; i < close_count - 1; i++) {
            for (int j = i + 1; j < close_count; j++) {
                if (close_f0[j] < close_f0[i]) {
                    float tmp = close_f0[i];
                    close_f0[i] = close_f0[j];
                    close_f0[j] = tmp;
                }
            }
        }
        *out_stable = true;
        return close_f0[close_count / 2]; // Trung vị (Median)
    }

    *out_stable = false;
    return raw_f0;
}

typedef enum {
    ESTIMATOR_F1_PRIMARY = 0,
    ESTIMATOR_F2_FALLBACK = 1,
    ESTIMATOR_F3_FALLBACK = 2,
    ESTIMATOR_INVALID = 3
} estimator_mode_t;

static const char *estimator_mode_to_str(estimator_mode_t mode)
{
    switch (mode) {
        case ESTIMATOR_F1_PRIMARY:  return "F1_PRIMARY";
        case ESTIMATOR_F2_FALLBACK: return "F2_FALLBACK";
        case ESTIMATOR_F3_FALLBACK: return "F3_FALLBACK";
        default:                    return "INVALID";
    }
}

#define REAL_PIANO_DIAG_FRAMES 20

typedef struct {
    int   midi;
    char  note_name[16];
    float target_freq;
    int   count;
    float final_f0[REAL_PIANO_DIAG_FRAMES];
    float cents[REAL_PIANO_DIAG_FRAMES];
    float confidence[REAL_PIANO_DIAG_FRAMES];
    float latency_ms[REAL_PIANO_DIAG_FRAMES];
    int   estimator_mode[REAL_PIANO_DIAG_FRAMES];
    float f1[REAL_PIANO_DIAG_FRAMES];
    float f2[REAL_PIANO_DIAG_FRAMES];
    float f3[REAL_PIANO_DIAG_FRAMES];
    bool  ok1[REAL_PIANO_DIAG_FRAMES];
    bool  ok2[REAL_PIANO_DIAG_FRAMES];
    bool  ok3[REAL_PIANO_DIAG_FRAMES];
    float dev2[REAL_PIANO_DIAG_FRAMES];
    float dev3[REAL_PIANO_DIAG_FRAMES];
    float mhqi[REAL_PIANO_DIAG_FRAMES];
} real_piano_stat_tracker_t;

static real_piano_stat_tracker_t s_diag_tracker = {0};

// ==============================================================================
// 5. CẤU TRÚC KẾT QUẢ PITCH & WEB API (THREAD-SAFE SNAPSHOT)
// ==============================================================================
typedef struct {
    float frequency;
    char  note[16];
    float target;
    float cents;
    float confidence;
    char  estimator[32];
    bool  valid;
    uint32_t frame;
    float latency_ms;
} pitch_api_data_t;

static pitch_api_data_t s_latest_pitch = {
    .frequency   = 0.0f,
    .note        = "N/A",
    .target      = 0.0f,
    .cents       = 0.0f,
    .confidence  = 0.0f,
    .estimator   = "NO_SIGNAL",
    .valid       = false,
    .frame       = 0,
    .latency_ms  = 0.0f
};

static portMUX_TYPE s_pitch_mux = portMUX_INITIALIZER_UNLOCKED;

#define WIFI_SSID           "HongLinh_L3"
#define WIFI_PASS           "Hl139nvl@@"
#define WIFI_AP_SSID        "PianoTuner-ESP32"
#define WIFI_AP_PASS        "12345678"

static esp_netif_t *s_netif_sta = NULL;
static esp_netif_t *s_netif_ap  = NULL;
static httpd_handle_t s_http_server = NULL;
static char s_sta_ip_str[32] = "0.0.0.0";
static bool s_sta_connected = false;

static void wifi_event_handler(void* arg, esp_event_base_t event_base,
                               int32_t event_id, void* event_data)
{
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();
        ESP_LOGI(TAG, "Wi-Fi STA khởi động, đang kết nối tới %s...", WIFI_SSID);
    } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
        s_sta_connected = false;
        ESP_LOGW(TAG, "Wi-Fi STA bị ngắt kết nối, thử kết nối lại...");
        esp_wifi_connect();
    } else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t* event = (ip_event_got_ip_t*) event_data;
        esp_ip4addr_ntoa(&event->ip_info.ip, s_sta_ip_str, sizeof(s_sta_ip_str));
        s_sta_connected = true;
        ESP_LOGI(TAG, "==================================================");
        ESP_LOGI(TAG, ">>> WI-FI ĐÃ KẾT NỐI! STA IP: http://%s/ <<<", s_sta_ip_str);
        ESP_LOGI(TAG, ">>> ENDPOINT DỮ LIỆU: http://%s/api/data <<<", s_sta_ip_str);
        ESP_LOGI(TAG, "==================================================");
    } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_AP_STACONNECTED) {
        wifi_event_ap_staconnected_t* event = (wifi_event_ap_staconnected_t*) event_data;
        ESP_LOGI(TAG, "Thiết bị kết nối vào SoftAP: MAC " MACSTR, MAC2STR(event->mac));
    }
}

static void init_wifi_network(void)
{
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        nvs_flash_erase();
        nvs_flash_init();
    }

    esp_netif_init();
    esp_event_loop_create_default();

    s_netif_sta = esp_netif_create_default_wifi_sta();
    s_netif_ap  = esp_netif_create_default_wifi_ap();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    esp_wifi_init(&cfg);

    esp_event_handler_instance_t instance_any_id;
    esp_event_handler_instance_t instance_got_ip;
    esp_event_handler_instance_register(WIFI_EVENT, ESP_EVENT_ANY_ID, &wifi_event_handler, NULL, &instance_any_id);
    esp_event_handler_instance_register(IP_EVENT, IP_EVENT_STA_GOT_IP, &wifi_event_handler, NULL, &instance_got_ip);

    wifi_config_t sta_config = {
        .sta = {
            .ssid = WIFI_SSID,
            .password = WIFI_PASS,
            .threshold.authmode = WIFI_AUTH_WPA2_PSK,
        },
    };

    wifi_config_t ap_config = {
        .ap = {
            .ssid = WIFI_AP_SSID,
            .ssid_len = strlen(WIFI_AP_SSID),
            .password = WIFI_AP_PASS,
            .max_connection = 4,
            .authmode = WIFI_AUTH_WPA2_PSK,
            .channel = 1
        },
    };

    esp_wifi_set_mode(WIFI_MODE_APSTA);
    esp_wifi_set_config(WIFI_IF_STA, &sta_config);
    esp_wifi_set_config(WIFI_IF_AP, &ap_config);
    esp_wifi_start();

    ESP_LOGI(TAG, "Khởi tạo Wi-Fi APSTA thành công.");
    ESP_LOGI(TAG, "SoftAP SSID: %s (IP mặc định: http://192.168.4.1/)", WIFI_AP_SSID);
}

extern const uint8_t index_html_start[] asm("_binary_index_html_start");
extern const uint8_t index_html_end[]   asm("_binary_index_html_end");

static esp_err_t root_get_handler(httpd_req_t *req)
{
    httpd_resp_set_type(req, "text/html; charset=utf-8");
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    const size_t index_len = index_html_end - index_html_start;
    return httpd_resp_send(req, (const char *)index_html_start, index_len);
}

static esp_err_t api_data_get_handler(httpd_req_t *req)
{
    pitch_api_data_t snapshot;
    portENTER_CRITICAL(&s_pitch_mux);
    snapshot = s_latest_pitch;
    portEXIT_CRITICAL(&s_pitch_mux);

    char json_buf[256];
    int len = snprintf(json_buf, sizeof(json_buf),
        "{\n"
        "  \"frequency\": %.3f,\n"
        "  \"note\": \"%s\",\n"
        "  \"target\": %.3f,\n"
        "  \"cents\": %.2f,\n"
        "  \"confidence\": %.1f,\n"
        "  \"estimator\": \"%s\",\n"
        "  \"valid\": %s,\n"
        "  \"frame\": %lu,\n"
        "  \"latency_ms\": %.2f\n"
        "}\n",
        snapshot.frequency,
        snapshot.note,
        snapshot.target,
        snapshot.cents,
        snapshot.confidence,
        snapshot.estimator,
        snapshot.valid ? "true" : "false",
        (unsigned long)snapshot.frame,
        snapshot.latency_ms
    );

    httpd_resp_set_type(req, "application/json");
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    return httpd_resp_send(req, json_buf, len);
}

static httpd_handle_t start_webserver(void)
{
    httpd_handle_t server = NULL;
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = 80;
    config.lru_purge_enable = true;

    httpd_uri_t root_uri = {
        .uri       = "/",
        .method    = HTTP_GET,
        .handler   = root_get_handler,
        .user_ctx  = NULL
    };

    httpd_uri_t api_data_uri = {
        .uri       = "/api/data",
        .method    = HTTP_GET,
        .handler   = api_data_get_handler,
        .user_ctx  = NULL
    };

    if (httpd_start(&server, &config) == ESP_OK) {
        httpd_register_uri_handler(server, &root_uri);
        httpd_register_uri_handler(server, &api_data_uri);
        ESP_LOGI(TAG, "May chu HTTP da khoi dong thanh cong tren cong 80.");
        return server;
    }

    ESP_LOGE(TAG, "Khoi dong may chu HTTP that bai!");
    return NULL;
}

// ==============================================================================
// 6. CHƯƠNG TRÌNH CHÍNH & VÒNG LẶP THỜI GIAN THỰC (HOP = 128 MS, OVERLAP = 50%)
// ==============================================================================
void app_main(void)
{
    ESP_LOGI(TAG, "=== HỆ THỐNG ĐO CAO ĐỘ REAL-TIME: 50%% OVERLAP (HOP = 128 MS) ===");
    ESP_LOGI(TAG, "Fs = %d Hz, FFT_N = %d (256ms), HOP_SIZE = %d (128ms)", 
             SAMPLE_RATE_HZ, FFT_N, HOP_SIZE);

    init_hann_window();

    // Khởi tạo Wi-Fi và Web API Server (hoạt động độc lập, không block DSP)
    init_wifi_network();
    s_http_server = start_webserver();

    // Cấp phát bộ đệm DRAM
    s_stereo_buf      = (uint32_t *)malloc(HOP_SIZE * 2 * sizeof(uint32_t)); // 2048 stereo pairs
    s_hop_samples     = (int32_t  *)malloc(HOP_SIZE * sizeof(int32_t));       // 2048 samples
    s_rolling_samples = (int32_t  *)malloc(FFT_N * sizeof(int32_t));           // 4096 samples
    s_fft_real        = (float    *)malloc(FFT_N * sizeof(float));
    s_fft_imag        = (float    *)malloc(FFT_N * sizeof(float));
    s_magnitude       = (float    *)malloc((FFT_N / 2) * sizeof(float));

    if (!s_stereo_buf || !s_hop_samples || !s_rolling_samples || !s_fft_real || !s_fft_imag || !s_magnitude) {
        ESP_LOGE(TAG, "Lỗi cấp phát bộ đệm!");
        return;
    }

    memset(s_rolling_samples, 0, FFT_N * sizeof(int32_t));

    esp_err_t err = init_i2s_microphone();
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Khởi tạo I2S thất bại!");
        return;
    }
    ESP_LOGI(TAG, "Khởi tạo I2S hoàn tất. Bắt đầu thu nhận liên tục và chạy DSP mỗi 128 ms...");

    uint32_t frame_counter = 0;
    int num_bins = FFT_N / 2;

    int64_t t_last_hop_end_us = esp_timer_get_time();
    int64_t last_print_time_us = 0;

    while (1) {
        // 1. Thu thập liên tục HOP_SIZE = 2048 mẫu từ microphone thật INMP441 (mất đúng 128 ms)
        size_t samples_read = 0;
        esp_err_t ret = read_active_audio_samples(s_hop_samples, HOP_SIZE, &samples_read);
        if (ret != ESP_OK || samples_read < HOP_SIZE) {
            vTaskDelay(pdMS_TO_TICKS(5));
            continue;
        }

        int64_t t_dsp_start_us = esp_timer_get_time();
        frame_counter++;

        // 2. Cập nhật cửa sổ trượt (Rolling Buffer 50% Overlap)
        memmove(&s_rolling_samples[0], &s_rolling_samples[HOP_SIZE], (FFT_N - HOP_SIZE) * sizeof(int32_t));
        memcpy(&s_rolling_samples[FFT_N - HOP_SIZE], s_hop_samples, HOP_SIZE * sizeof(int32_t));

        // 3. Khử DC và nhân cửa sổ Hann trên 4096 mẫu phân tích
        double sum = 0.0;
        double sum_sq = 0.0;
        for (int n = 0; n < FFT_N; n++) {
            float x_norm = (float)s_rolling_samples[n] / 8388608.0f;
            s_fft_real[n] = x_norm;
            sum += x_norm;
        }
        float mean = (float)(sum / (double)FFT_N);

        float ac_peak_norm = 0.0f;
        for (int n = 0; n < FFT_N; n++) {
            float x_dc = s_fft_real[n] - mean;
            float abs_x = fabsf(x_dc);
            if (abs_x > ac_peak_norm) ac_peak_norm = abs_x;
            sum_sq += (double)(x_dc * x_dc);
            s_fft_real[n] = x_dc * s_hann_window[n];
            s_fft_imag[n] = 0.0f;
        }

        float raw_ac_rms_norm = sqrtf((float)(sum_sq / (double)FFT_N));

        // 4. Biến đổi FFT Radix-2 4096 điểm
        fft_radix2(s_fft_real, s_fft_imag, FFT_N);

        for (int k = 0; k < num_bins; k++) {
            s_magnitude[k] = sqrtf(s_fft_real[k] * s_fft_real[k] + s_fft_imag[k] * s_fft_imag[k]);
        }

        // 5. Xác định đỉnh lớn nhất toàn cục trong dải Piano [PIANO_MIN_BIN .. PIANO_MAX_BIN]
        float max_mag_in_range = 0.0f;
        int max_mag_bin = 0;
        for (int k = PIANO_MIN_BIN; k <= PIANO_MAX_BIN; k++) {
            if (s_magnitude[k] > max_mag_in_range) {
                max_mag_in_range = s_magnitude[k];
                max_mag_bin = k;
            }
        }

        // 6. Trích xuất danh sách tất cả các đỉnh phổ cục bộ và tính độ nổi bật (Prominence)
        static peak_candidate_t candidates[MAX_CANDIDATE_PEAKS];
        int candidate_count = 0;

        for (int k = PIANO_MIN_BIN; k <= PIANO_MAX_BIN && candidate_count < MAX_CANDIDATE_PEAKS; k++) {
            if (s_magnitude[k] > s_magnitude[k - 1] && s_magnitude[k] > s_magnitude[k + 1]) {
                float local_floor = calculate_local_noise_floor(s_magnitude, k, num_bins);
                float prominence = s_magnitude[k] / (local_floor > 0.05f ? local_floor : 0.05f);
                float snr_db = 20.0f * log10f(prominence > 0.1f ? prominence : 0.1f);

                // Lưu lại ứng viên nếu có biên độ đáng kể hoặc nhô rõ so với sàn nhiễu
                if (s_magnitude[k] >= 1.5f && prominence >= 2.0f) {
                    candidates[candidate_count].bin = k;
                    candidates[candidate_count].raw_freq = (float)k * BIN_RESOLUTION_HZ;
                    candidates[candidate_count].mag = s_magnitude[k];
                    candidates[candidate_count].local_floor = local_floor;
                    candidates[candidate_count].prominence = prominence;
                    candidates[candidate_count].snr_db = snr_db;
                    candidates[candidate_count].score = 0.0f;
                    candidates[candidate_count].harmonics_found = 0;
                    candidate_count++;
                }
            }
        }

        // Nếu không có đỉnh nào thỏa mãn, đưa đỉnh lớn nhất vào danh sách xét
        if (candidate_count == 0) {
            float local_floor = calculate_local_noise_floor(s_magnitude, max_mag_bin, num_bins);
            candidates[0].bin = max_mag_bin;
            candidates[0].raw_freq = (float)max_mag_bin * BIN_RESOLUTION_HZ;
            candidates[0].mag = max_mag_in_range;
            candidates[0].local_floor = local_floor;
            candidates[0].prominence = max_mag_in_range / (local_floor > 0.05f ? local_floor : 0.05f);
            candidates[0].snr_db = 20.0f * log10f(candidates[0].prominence > 0.1f ? candidates[0].prominence : 0.1f);
            candidates[0].score = 0.0f;
            candidates[0].harmonics_found = 0;
            candidate_count = 1;
        }

        // 7. Thuật toán kiểm định giả thuyết họa âm (Subharmonic Hypothesis Testing)
        // Tìm ứng viên đỉnh mạnh nhất để thử nghiệm các giả thuyết f, f/2, f/3, f/4
        int top_cand_idx = 0;
        float top_cand_mag = candidates[0].mag;
        for (int c = 1; c < candidate_count; c++) {
            if (candidates[c].mag > top_cand_mag) {
                top_cand_mag = candidates[c].mag;
                top_cand_idx = c;
            }
        }

        peak_candidate_t *primary_cand = &candidates[top_cand_idx];
        float cand_peak_freq = primary_cand->raw_freq;
        int cand_peak_bin = primary_cand->bin;
        float cand_peak_mag = primary_cand->mag;

        float best_hyp_freq = cand_peak_freq;
        float best_hyp_score = -1.0f;
        int best_divisor = 1;
        int best_h_count = 0;
        uint8_t best_h_mask = 0;
        int best_dom_bin = cand_peak_bin;

        // Lưu điểm số các giả thuyết f, f/2, f/3 cho dòng chẩn đoán
        float diag_f_score = 0.0f;
        float diag_f2_score = 0.0f;
        float diag_f3_score = 0.0f;

        // Cấu trúc lưu vết các giả thuyết đã đánh giá để phục vụ [E2-DIAG]
        #define MAX_DIAG_HYPS 24
        static diag_hypothesis_t s_diag_hyps[MAX_DIAG_HYPS];
        int diag_hyp_count = 0;

        // Thử nghiệm các giả thuyết subharmonic: f, f/2, f/3, f/4 từ đỉnh mạnh nhất
        for (int d = 1; d <= 4; d++) {
            float test_f = cand_peak_freq / (float)d;
            if (test_f < PIANO_MIN_FREQ_HZ) break;

            int h_cnt = 0;
            uint8_t h_msk = 0;
            int dom_b = 0;
            diag_hypothesis_t *d_ptr = (diag_hyp_count < MAX_DIAG_HYPS) ? &s_diag_hyps[diag_hyp_count] : NULL;
            float sc = evaluate_harmonic_hypothesis(s_magnitude, num_bins, test_f, &h_cnt, &h_msk, &dom_b, d_ptr);
            if (d_ptr) {
                d_ptr->base_f = cand_peak_freq;
                d_ptr->divisor = d;
                diag_hyp_count++;
            }

            if (d == 1) diag_f_score = sc;
            if (d == 2) diag_f2_score = sc;
            if (d == 3) diag_f3_score = sc;

            if (sc > best_hyp_score) {
                best_hyp_score = sc;
                best_hyp_freq = test_f;
                best_divisor = d;
                best_h_count = h_cnt;
                best_h_mask = h_msk;
                best_dom_bin = dom_b;
            }
        }

        // Kiểm tra thêm các đỉnh ứng viên tiềm năng khác (tối đa 4 đỉnh tiếp theo)
        for (int c = 0; c < candidate_count && c < 5; c++) {
            if (c == top_cand_idx) continue;
            float other_f = candidates[c].raw_freq;
            for (int d = 1; d <= 3; d++) {
                float test_f = other_f / (float)d;
                if (test_f < PIANO_MIN_FREQ_HZ) break;

                int h_cnt = 0;
                uint8_t h_msk = 0;
                int dom_b = 0;
                diag_hypothesis_t *d_ptr = (diag_hyp_count < MAX_DIAG_HYPS) ? &s_diag_hyps[diag_hyp_count] : NULL;
                float sc = evaluate_harmonic_hypothesis(s_magnitude, num_bins, test_f, &h_cnt, &h_msk, &dom_b, d_ptr);
                if (d_ptr) {
                    d_ptr->base_f = other_f;
                    d_ptr->divisor = d;
                    diag_hyp_count++;
                }

                if (sc > best_hyp_score) {
                    best_hyp_score = sc;
                    best_hyp_freq = test_f;
                    best_divisor = d;
                    best_h_count = h_cnt;
                    best_h_mask = h_msk;
                    best_dom_bin = dom_b;
                    cand_peak_freq = candidates[c].raw_freq;
                    cand_peak_bin = candidates[c].bin;
                    cand_peak_mag = candidates[c].mag;
                }
            }
        }

        // 8. Cổng phân loại trạng thái (Signal Gate & Confidence)
        int hyp_target_bin = (int)roundf(best_hyp_freq / BIN_RESOLUTION_HZ);
        if (hyp_target_bin < 1) hyp_target_bin = 1;
        if (hyp_target_bin >= num_bins - 1) hyp_target_bin = num_bins - 2;

        float sel_local_floor = calculate_local_noise_floor(s_magnitude, hyp_target_bin, num_bins);
        float sel_mag = s_magnitude[hyp_target_bin];
        float sel_prominence = sel_mag / (sel_local_floor > 0.05f ? sel_local_floor : 0.05f);
        float sel_snr_db = 20.0f * log10f(sel_prominence > 0.1f ? sel_prominence : 0.1f);

        pitch_state_t state = PITCH_NO_SIGNAL;
        bool pass_energy_gate = (raw_ac_rms_norm >= MIN_AC_RMS_NORM);

        if (pass_energy_gate && best_hyp_score >= 20.0f) {
            if (best_hyp_freq < 110.0f) {
                // Tần số thấp (< 110 Hz): Phải có ít nhất 3 họa âm liên kết
                if (best_h_count >= 3 && cand_peak_mag >= 14.0f) {
                    state = PITCH_VALID_PITCH;
                } else if (best_h_count >= 2 && cand_peak_mag >= 9.0f) {
                    state = PITCH_WEAK_SIGNAL;
                } else {
                    state = PITCH_NO_SIGNAL;
                }
            } else {
                // Tần số >= 110 Hz (bao gồm C4, A4, C5):
                // Được xác thực VALID_PITCH khi điểm nhất quán họa âm cao hoặc độ nổi bật phổ tốt
                if ((best_hyp_score >= 120.0f) ||
                    (sel_prominence >= 4.0f && sel_mag >= 1.5f) ||
                    (primary_cand->prominence >= 6.0f && primary_cand->mag >= 2.0f && best_h_count >= 2)) {
                    state = PITCH_VALID_PITCH;
                } else if (best_hyp_score >= 40.0f || sel_prominence >= 2.5f) {
                    state = PITCH_WEAK_SIGNAL;
                } else {
                    state = PITCH_NO_SIGNAL;
                }
            }
        } else {
            state = PITCH_NO_SIGNAL;
        }

        // Tính độ tin cậy [0 .. 100%]
        float confidence = 0.0f;
        if (state == PITCH_VALID_PITCH) {
            confidence = 50.0f + (sel_snr_db - 10.0f) * 1.5f + (best_hyp_score / 20.0f) + (float)(best_h_count - 1) * 8.0f;
            if (confidence > 100.0f) confidence = 100.0f;
            if (confidence < 60.0f)  confidence = 60.0f;
        } else if (state == PITCH_WEAK_SIGNAL) {
            confidence = 30.0f + (sel_snr_db - 6.0f) * 2.0f;
            if (confidence > 59.0f) confidence = 59.0f;
            if (confidence < 25.0f) confidence = 25.0f;
        } else {
            confidence = 0.0f;
        }

        // 9. Multi-Harmonic Weighted Quadratic Interpolation (MHQI)
        // Với mỗi họa âm m = 1, 2, 3 của giả thuyết cơ bản best_hyp_freq:
        //   (a) Tìm local peak thực tế trong khoảng ±1 bin quanh target bin.
        //   (b) Xác nhận đỉnh cục bộ hợp lệ: mag[k] >= mag[k-1] && mag[k] >= mag[k+1].
        //   (c) Chạy QI tại đỉnh đó.
        //   (d) Quy về tần số cơ bản: f0_m = interp_freq / m.
        //   (e) Trọng số: weight_m = m * mag_peak_m.
        // Final f0 = Σ(weight_m * f0_m) / Σ(weight_m).

        float p = 0.0f; // offset QI của m=1 (cho diagnostic)

        // Mảng chẩn đoán multi-harmonic (đo lường m=1..4 cho diagnostic)
        float mhqi_f0[4]       = {0.0f, 0.0f, 0.0f, 0.0f};
        float mhqi_mag[4]      = {0.0f, 0.0f, 0.0f, 0.0f};
        int   mhqi_bin[4]      = {0, 0, 0, 0};
        float mhqi_p[4]        = {0.0f, 0.0f, 0.0f, 0.0f};
        float mhqi_w[4]        = {0.0f, 0.0f, 0.0f, 0.0f};
        float mhqi_floor[4]    = {0.0f, 0.0f, 0.0f, 0.0f};
        float mhqi_prom[4]     = {0.0f, 0.0f, 0.0f, 0.0f};
        float mhqi_snr[4]      = {0.0f, 0.0f, 0.0f, 0.0f};
        bool  mhqi_ok[4]       = {false, false, false, false};
        float mhqi_target_f[4] = {0.0f, 0.0f, 0.0f, 0.0f};

        float hyp_k_float = best_hyp_freq / BIN_RESOLUTION_HZ;

        for (int m = 1; m <= 4; m++) {
            mhqi_target_f[m - 1] = best_hyp_freq * (float)m;
            int target_k = (int)roundf((float)m * hyp_k_float);
            if (target_k < 1 || target_k >= num_bins - 1) continue;

            // Tìm local peak trong ±1 bin
            int search_lo = (target_k - 1 < 1)             ? 1             : target_k - 1;
            int search_hi = (target_k + 1 >= num_bins - 1) ? num_bins - 2  : target_k + 1;

            int   best_k_m   = target_k;
            float best_mag_m = s_magnitude[target_k];
            for (int kk = search_lo; kk <= search_hi; kk++) {
                if (s_magnitude[kk] > best_mag_m) {
                    best_mag_m = s_magnitude[kk];
                    best_k_m   = kk;
                }
            }

            // Xác nhận đỉnh cục bộ
            if (best_k_m < 1 || best_k_m >= num_bins - 1) continue;
            bool is_lp = (s_magnitude[best_k_m] >= s_magnitude[best_k_m - 1] &&
                          s_magnitude[best_k_m] >= s_magnitude[best_k_m + 1] &&
                          s_magnitude[best_k_m] >= 0.5f);
            if (!is_lp) continue;

            // Quadratic Interpolation
            float alpha_m = s_magnitude[best_k_m - 1];
            float beta_m  = s_magnitude[best_k_m];
            float gamma_m = s_magnitude[best_k_m + 1];
            float denom_m = alpha_m - 2.0f * beta_m + gamma_m;
            float p_m = 0.0f;
            if (fabsf(denom_m) > 1e-6f) {
                p_m = 0.5f * (alpha_m - gamma_m) / denom_m;
            }
            if (p_m < -0.5f) p_m = -0.5f;
            if (p_m >  0.5f) p_m =  0.5f;

            float interp_freq_m = ((float)best_k_m + p_m) * BIN_RESOLUTION_HZ;
            float f0_m          = interp_freq_m / (float)m;

            float floor_m = calculate_local_noise_floor(s_magnitude, best_k_m, num_bins);
            float prom_m  = best_mag_m / (floor_m > 0.05f ? floor_m : 0.05f);
            float snr_m   = 20.0f * log10f(prom_m > 0.1f ? prom_m : 0.1f);

            int idx = m - 1;
            mhqi_ok[idx]    = true;
            mhqi_bin[idx]   = best_k_m;
            mhqi_mag[idx]   = best_mag_m;
            mhqi_p[idx]     = p_m;
            mhqi_f0[idx]    = f0_m;
            mhqi_w[idx]     = (float)m * best_mag_m;
            mhqi_floor[idx] = floor_m;
            mhqi_prom[idx]  = prom_m;
            mhqi_snr[idx]   = snr_m;

            if (m == 1) p = p_m;
        }

        // ==============================================================================
        // ESTIMATOR POLICY (PRIMARY: f1, FALLBACK: f2/2, f3/3)
        // Standard Quality Gate: mag >= 1.5f && prominence >= 4.0f (SNR >= 12.0 dB)
        // ==============================================================================
        #define PEAK_PASS_GATE(idx) (mhqi_ok[idx] && mhqi_mag[idx] >= 1.5f && mhqi_prom[idx] >= 4.0f)

        estimator_mode_t est_mode = ESTIMATOR_INVALID;
        float final_f0 = 0.0f;

        // Kiểm tra xem f1 có bị lấn át bởi họa âm bậc 2 ở dải trầm (f0 < 200 Hz) không
        bool f1_submerged_in_bass = false;
        if (best_hyp_freq < 200.0f && PEAK_PASS_GATE(1)) {
            // Ở nốt trầm piano, nếu m=2 mạnh vượt trội so với m=1 (m2 >= 2.0*m1 hoặc SNR m1 < 14dB),
            // m=1 thường bị suy hao âm học và nhiễu phòng làm méo đỉnh QI.
            // Khi đó m=2/2 là ước lượng ổn định và chính xác hơn nhiều.
            if (!PEAK_PASS_GATE(0) || (mhqi_mag[1] >= 2.0f * mhqi_mag[0]) || (mhqi_snr[0] < 14.0f)) {
                f1_submerged_in_bass = true;
            }
        }

        if (!f1_submerged_in_bass && PEAK_PASS_GATE(0)) {
            // 1. PRIMARY ESTIMATOR: f1
            est_mode = ESTIMATOR_F1_PRIMARY;
            final_f0 = mhqi_f0[0];
        } else if (PEAK_PASS_GATE(1)) {
            // 2. FALLBACK 1: f2 / 2 (Ưu tiên cho nốt trầm khi fundamental bị yếu/lấn át)
            est_mode = ESTIMATOR_F2_FALLBACK;
            final_f0 = mhqi_f0[1];
        } else if (PEAK_PASS_GATE(0)) {
            // 3. Fallback về f1 nếu m=1 hợp lệ nhưng m=2 không qua cổng chất lượng
            est_mode = ESTIMATOR_F1_PRIMARY;
            final_f0 = mhqi_f0[0];
        } else if (PEAK_PASS_GATE(2)) {
            // 4. FALLBACK 2: f3 / 3
            est_mode = ESTIMATOR_F3_FALLBACK;
            final_f0 = mhqi_f0[2];
        } else {
            // 5. INVALID
            est_mode = ESTIMATOR_INVALID;
            final_f0 = 0.0f;
            state = PITCH_NO_SIGNAL;
        }

        #undef PEAK_PASS_GATE

        // Tính MHQI cũ strictly for diagnostic comparison
        float mhqi_comp_f0 = 0.0f;
        float wsum_f0  = 0.0f;
        float wsum_tot = 0.0f;
        for (int m = 1; m <= 3; m++) {
            int idx = m - 1;
            if (mhqi_ok[idx]) {
                wsum_f0  += mhqi_w[idx] * mhqi_f0[idx];
                wsum_tot += mhqi_w[idx];
            }
        }
        if (wsum_tot > 0.0f) {
            mhqi_comp_f0 = wsum_f0 / wsum_tot;
        } else {
            mhqi_comp_f0 = best_hyp_freq;
        }

        float raw_f0 = final_f0;

        // 10. Lọc ổn định thời gian (Temporal Stability & Median Smoothing)
        bool is_stable = false;
        bool is_valid_pitch = (state == PITCH_VALID_PITCH);
        float smooth_f0 = update_temporal_stability(raw_f0, confidence, is_valid_pitch, &is_stable);

        // 11. Nhận diện nốt nhạc (Musical Note Identification: Equal Temperament, A4 = 440 Hz)
        int midi = 0;
        float target_freq = 0.0f;
        float cents = 0.0f;
        float note_f0 = 0.0f;
        char note_name_buf[16] = "N/A";

        if (state == PITCH_VALID_PITCH) {
            note_f0 = is_stable ? smooth_f0 : raw_f0;
            if (note_f0 > 10.0f) {
                // 1. Tính số nốt MIDI gần nhất: midi = round(69 + 12 * log2(f0 / 440.0))
                midi = (int)roundf(69.0f + 12.0f * log2f(note_f0 / 440.0f));

                // 2. Tính tần số chuẩn của nốt MIDI: target = 440.0 * pow(2.0, (midi - 69) / 12.0)
                target_freq = 440.0f * powf(2.0f, (float)(midi - 69) / 12.0f);

                // 3. Tính độ lệch cents: cents = 1200 * log2(f0 / target)
                cents = 1200.0f * log2f(note_f0 / target_freq);

                // 4. Chuyển đổi sang tên nốt nhạc (C, C#, D, D#, E, F, F#, G, G#, A, A#, B)
                static const char *k_note_names[12] = {"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"};
                int note_idx = midi % 12;
                if (note_idx < 0) note_idx += 12;

                // 5. Tính quãng tám (Octave) theo chuẩn MIDI: octave = midi / 12 - 1
                int octave = (midi / 12) - 1;
                snprintf(note_name_buf, sizeof(note_name_buf), "%s%d", k_note_names[note_idx], octave);
            }
        }

        int64_t t_dsp_end_us = esp_timer_get_time();
        float dsp_latency_ms = (float)(t_dsp_end_us - t_dsp_start_us) / 1000.0f;
        float dsp_interval_ms = (float)(t_dsp_end_us - t_last_hop_end_us) / 1000.0f;
        t_last_hop_end_us = t_dsp_end_us;

        // 12. Cập nhật snapshot kết quả Web API một cách thread-safe (không block DSP)
        portENTER_CRITICAL(&s_pitch_mux);
        if (state == PITCH_VALID_PITCH) {
            s_latest_pitch.frequency  = note_f0;
            s_latest_pitch.target     = target_freq;
            s_latest_pitch.cents      = cents;
            s_latest_pitch.confidence = confidence;
            s_latest_pitch.valid      = true;
            strncpy(s_latest_pitch.note, note_name_buf, sizeof(s_latest_pitch.note) - 1);
            s_latest_pitch.note[sizeof(s_latest_pitch.note) - 1] = '\0';
            strncpy(s_latest_pitch.estimator, estimator_mode_to_str(est_mode), sizeof(s_latest_pitch.estimator) - 1);
            s_latest_pitch.estimator[sizeof(s_latest_pitch.estimator) - 1] = '\0';
        } else {
            s_latest_pitch.frequency  = 0.0f;
            s_latest_pitch.target     = 0.0f;
            s_latest_pitch.cents      = 0.0f;
            s_latest_pitch.confidence = confidence;
            s_latest_pitch.valid      = false;
            strncpy(s_latest_pitch.note, "N/A", sizeof(s_latest_pitch.note));
            strncpy(s_latest_pitch.estimator, (state == PITCH_WEAK_SIGNAL) ? "WEAK_SIGNAL" : "NO_SIGNAL", sizeof(s_latest_pitch.estimator));
        }
        s_latest_pitch.frame      = frame_counter;
        s_latest_pitch.latency_ms = dsp_latency_ms;
        portEXIT_CRITICAL(&s_pitch_mux);

        // Định dạng chuỗi chất lượng đỉnh của f1, f2, f3
        char f1_q_str[64], f2_q_str[64], f3_q_str[64];
        if (mhqi_ok[0]) {
            snprintf(f1_q_str, sizeof(f1_q_str), "SNR %+5.1f dB (Prom %4.1fx, Mag %4.1f)",
                     mhqi_snr[0], mhqi_prom[0], mhqi_mag[0]);
        } else {
            snprintf(f1_q_str, sizeof(f1_q_str), "N/A");
        }
        if (mhqi_ok[1]) {
            snprintf(f2_q_str, sizeof(f2_q_str), "SNR %+5.1f dB (Prom %4.1fx, Mag %4.1f)",
                     mhqi_snr[1], mhqi_prom[1], mhqi_mag[1]);
        } else {
            snprintf(f2_q_str, sizeof(f2_q_str), "N/A");
        }
        if (mhqi_ok[2]) {
            snprintf(f3_q_str, sizeof(f3_q_str), "SNR %+5.1f dB (Prom %4.1fx, Mag %4.1f)",
                     mhqi_snr[2], mhqi_prom[2], mhqi_mag[2]);
        } else {
            snprintf(f3_q_str, sizeof(f3_q_str), "N/A");
        }

        // ==============================================================================
        // DIAGNOSTIC INSTRUMENTATION: [E2-DIAG] (SECTIONS A, B, C, D)
        // Activated on real musical events: valid pitch, weak signal, or significant harmonic score
        // ==============================================================================
        bool do_diag_print = (state == PITCH_VALID_PITCH || state == PITCH_WEAK_SIGNAL || 
                              (pass_energy_gate && (best_hyp_score >= 10.0f || cand_peak_mag >= 6.0f)));
        if (do_diag_print) {
            printf("\n==================== [E2-DIAG FRAME #%lu] ====================\n", (unsigned long)frame_counter);
            printf("RMS Energy Norm : %.6f (Gate >= %.4f) | State: %s\n",
                   raw_ac_rms_norm, (float)MIN_AC_RMS_NORM,
                   (state == PITCH_VALID_PITCH) ? "VALID_PITCH" : (state == PITCH_WEAK_SIGNAL ? "WEAK_SIGNAL" : "NO_SIGNAL"));

            // A. Top 5 Spectral Peaks
            static peak_candidate_t sorted_cands[MAX_CANDIDATE_PEAKS];
            int s_count = candidate_count < MAX_CANDIDATE_PEAKS ? candidate_count : MAX_CANDIDATE_PEAKS;
            for (int i = 0; i < s_count; i++) sorted_cands[i] = candidates[i];
            for (int i = 0; i < s_count - 1; i++) {
                for (int j = i + 1; j < s_count; j++) {
                    if (sorted_cands[j].mag > sorted_cands[i].mag) {
                        peak_candidate_t tmp = sorted_cands[i];
                        sorted_cands[i] = sorted_cands[j];
                        sorted_cands[j] = tmp;
                    }
                }
            }
            printf("A. Top 5 Spectral Peaks:\n");
            for (int i = 0; i < s_count && i < 5; i++) {
                int kb = sorted_cands[i].bin;
                float interp_freq = sorted_cands[i].raw_freq;
                if (kb > 0 && kb < num_bins - 1) {
                    float a = s_magnitude[kb - 1];
                    float b = s_magnitude[kb];
                    float g = s_magnitude[kb + 1];
                    float d = a - 2.0f * b + g;
                    float p_val = (fabsf(d) > 1e-6f) ? 0.5f * (a - g) / d : 0.0f;
                    if (p_val < -0.5f) p_val = -0.5f;
                    if (p_val >  0.5f) p_val =  0.5f;
                    interp_freq = ((float)kb + p_val) * BIN_RESOLUTION_HZ;
                }
                printf("   #%d: Bin %4d | Raw: %7.2f Hz | Interp: %7.2f Hz | Mag: %6.2f | Floor: %5.2f | Prom: %5.1fx | SNR: %+5.1f dB\n",
                       i + 1, sorted_cands[i].bin, sorted_cands[i].raw_freq, interp_freq,
                       sorted_cands[i].mag, sorted_cands[i].local_floor,
                       sorted_cands[i].prominence, sorted_cands[i].snr_db);
            }

            // B. Selected Hypothesis Harmonics (m=1,2,3,4)
            printf("B. Selected Hypothesis Harmonics (best_hyp = %6.2f Hz):\n", best_hyp_freq);
            for (int m = 1; m <= 4; m++) {
                int idx = m - 1;
                int tgt_k = (int)roundf(mhqi_target_f[idx] / BIN_RESOLUTION_HZ);
                bool pass = (mhqi_ok[idx] && mhqi_mag[idx] >= 1.5f && mhqi_prom[idx] >= 4.0f);
                printf("   m=%d: Target: %7.2f Hz (Bin %4d) | Peak: %7.2f Hz (Bin %4d) | f0/%d: %7.2f Hz | Mag: %5.2f | Prom: %4.1fx (SNR %+5.1f dB) | Gate: %s\n",
                       m, mhqi_target_f[idx], tgt_k,
                       (float)mhqi_bin[idx] * BIN_RESOLUTION_HZ, mhqi_bin[idx],
                       m, mhqi_ok[idx] ? mhqi_f0[idx] : 0.0f,
                       mhqi_mag[idx], mhqi_prom[idx], mhqi_snr[idx],
                       pass ? "PASS" : "FAIL");
            }

            // C. Candidate Scoring & Ranking
            static diag_hypothesis_t sorted_hyps[MAX_DIAG_HYPS];
            int h_cnt_sort = diag_hyp_count < MAX_DIAG_HYPS ? diag_hyp_count : MAX_DIAG_HYPS;
            for (int i = 0; i < h_cnt_sort; i++) sorted_hyps[i] = s_diag_hyps[i];
            for (int i = 0; i < h_cnt_sort - 1; i++) {
                for (int j = i + 1; j < h_cnt_sort; j++) {
                    if (sorted_hyps[j].final_score > sorted_hyps[i].final_score) {
                        diag_hypothesis_t tmp = sorted_hyps[i];
                        sorted_hyps[i] = sorted_hyps[j];
                        sorted_hyps[j] = tmp;
                    }
                }
            }
            printf("C. Candidate Scoring Ranking (Total Tested: %d):\n", diag_hyp_count);
            for (int i = 0; i < h_cnt_sort && i < 10; i++) {
                printf("   Rank #%2d: Cand %6.2f Hz (Base %6.2f /%d) | Final: %6.2f (Raw: %6.2f) | H_Count: %d (Mask 0x%02X) | DomBin %4d | Pen: %s%s%s%s\n",
                       i + 1, sorted_hyps[i].test_f, sorted_hyps[i].base_f, sorted_hyps[i].divisor,
                       sorted_hyps[i].final_score, sorted_hyps[i].raw_score,
                       sorted_hyps[i].h_count, sorted_hyps[i].h_mask, sorted_hyps[i].dominant_bin,
                       sorted_hyps[i].penalty_no_odd ? "[NO_ODD:x0.05] " : "",
                       sorted_hyps[i].penalty_missing_m1 ? "[NO_M1:x0.20] " : "",
                       sorted_hyps[i].penalty_missing_m1_rescued ? "[M1_RESCUED:x0.85] " : "",
                       sorted_hyps[i].penalty_bass_guard ? "[BASS_GUARD_k<28:x0.10] " : "");
            }

            // Head-to-Head: E2 (~82.4 Hz) vs E3 (~164.8 Hz)
            int e2_idx = -1, e3_idx = -1;
            float min_d2 = 999.0f, min_d3 = 999.0f;
            for (int i = 0; i < diag_hyp_count; i++) {
                float d2 = fabsf(s_diag_hyps[i].test_f - 82.407f);
                if (d2 < min_d2 && d2 < 12.0f) { min_d2 = d2; e2_idx = i; }
                float d3 = fabsf(s_diag_hyps[i].test_f - 164.814f);
                if (d3 < min_d3 && d3 < 15.0f) { min_d3 = d3; e3_idx = i; }
            }
            printf("--- [E2 (82.4 Hz) vs E3 (164.8 Hz) COMPARISON] ---\n");
            if (e2_idx >= 0) {
                printf("   [E2 CANDIDATE]: Freq: %6.2f Hz (from %6.2f/%d) | Raw: %6.2f | Final: %6.2f | H_Count: %d | Mask: 0x%02X | Penalties: %s%s%s%s\n",
                       s_diag_hyps[e2_idx].test_f, s_diag_hyps[e2_idx].base_f, s_diag_hyps[e2_idx].divisor,
                       s_diag_hyps[e2_idx].raw_score, s_diag_hyps[e2_idx].final_score,
                       s_diag_hyps[e2_idx].h_count, s_diag_hyps[e2_idx].h_mask,
                       s_diag_hyps[e2_idx].penalty_no_odd ? "[NO_ODD:x0.05] " : "",
                       s_diag_hyps[e2_idx].penalty_missing_m1 ? "[NO_M1:x0.20] " : "",
                       s_diag_hyps[e2_idx].penalty_missing_m1_rescued ? "[M1_RESCUED:x0.85] " : "",
                       s_diag_hyps[e2_idx].penalty_bass_guard ? "[BASS_GUARD:x0.10] " : "");
                for (int m = 1; m <= 4; m++) {
                    int mi = m - 1;
                    printf("      m=%d: Target k=%2d | Peak bin=%2d (%6.2f Hz) | f0/%d=%6.2f Hz | Mag=%5.2f | Floor=%5.2f | Prom=%4.1fx (SNR %+5.1fdB) | LP:%s | PassGate:%s\n",
                           m, s_diag_hyps[e2_idx].harms[mi].target_k,
                           s_diag_hyps[e2_idx].harms[mi].peak_w, s_diag_hyps[e2_idx].harms[mi].peak_freq,
                           m, s_diag_hyps[e2_idx].harms[mi].interp_f0,
                           s_diag_hyps[e2_idx].harms[mi].mag, s_diag_hyps[e2_idx].harms[mi].local_floor,
                           s_diag_hyps[e2_idx].harms[mi].prom, s_diag_hyps[e2_idx].harms[mi].snr_db,
                           s_diag_hyps[e2_idx].harms[mi].is_local_peak ? "YES" : "NO",
                           s_diag_hyps[e2_idx].harms[mi].pass_gate ? "PASS" : "FAIL");
                }
            } else {
                printf("   [E2 CANDIDATE]: NOT EVALUATED (no candidate near 82.4 Hz)\n");
            }
            if (e3_idx >= 0) {
                printf("   [E3 CANDIDATE]: Freq: %6.2f Hz (from %6.2f/%d) | Raw: %6.2f | Final: %6.2f | H_Count: %d | Mask: 0x%02X | Penalties: %s%s%s%s\n",
                       s_diag_hyps[e3_idx].test_f, s_diag_hyps[e3_idx].base_f, s_diag_hyps[e3_idx].divisor,
                       s_diag_hyps[e3_idx].raw_score, s_diag_hyps[e3_idx].final_score,
                       s_diag_hyps[e3_idx].h_count, s_diag_hyps[e3_idx].h_mask,
                       s_diag_hyps[e3_idx].penalty_no_odd ? "[NO_ODD:x0.05] " : "",
                       s_diag_hyps[e3_idx].penalty_missing_m1 ? "[NO_M1:x0.20] " : "",
                       s_diag_hyps[e3_idx].penalty_missing_m1_rescued ? "[M1_RESCUED:x0.85] " : "",
                       s_diag_hyps[e3_idx].penalty_bass_guard ? "[BASS_GUARD:x0.10] " : "");
                for (int m = 1; m <= 4; m++) {
                    int mi = m - 1;
                    printf("      m=%d: Target k=%2d | Peak bin=%2d (%6.2f Hz) | f0/%d=%6.2f Hz | Mag=%5.2f | Floor=%5.2f | Prom=%4.1fx (SNR %+5.1fdB) | LP:%s | PassGate:%s\n",
                           m, s_diag_hyps[e3_idx].harms[mi].target_k,
                           s_diag_hyps[e3_idx].harms[mi].peak_w, s_diag_hyps[e3_idx].harms[mi].peak_freq,
                           m, s_diag_hyps[e3_idx].harms[mi].interp_f0,
                           s_diag_hyps[e3_idx].harms[mi].mag, s_diag_hyps[e3_idx].harms[mi].local_floor,
                           s_diag_hyps[e3_idx].harms[mi].prom, s_diag_hyps[e3_idx].harms[mi].snr_db,
                           s_diag_hyps[e3_idx].harms[mi].is_local_peak ? "YES" : "NO",
                           s_diag_hyps[e3_idx].harms[mi].pass_gate ? "PASS" : "FAIL");
                }
            } else {
                printf("   [E3 CANDIDATE]: NOT EVALUATED (no candidate near 164.8 Hz)\n");
            }
            if (e2_idx >= 0 && e3_idx >= 0) {
                if (s_diag_hyps[e2_idx].final_score < s_diag_hyps[e3_idx].final_score) {
                    printf("   >>> VERDICT: E3 BEAT E2 by score (E3: %.2f vs E2: %.2f). Diff = %.2f\n",
                           s_diag_hyps[e3_idx].final_score, s_diag_hyps[e2_idx].final_score,
                           s_diag_hyps[e3_idx].final_score - s_diag_hyps[e2_idx].final_score);
                } else {
                    printf("   >>> VERDICT: E2 WON over E3 (E2: %.2f vs E3: %.2f)\n",
                           s_diag_hyps[e2_idx].final_score, s_diag_hyps[e3_idx].final_score);
                }
            }

            // D. Final Decision
            printf("D. Final Decision:\n");
            printf("   Best Hyp Freq   : %7.3f Hz\n", best_hyp_freq);
            printf("   Estimator Mode  : %s\n", estimator_mode_to_str(est_mode));
            printf("   Raw f0          : %7.3f Hz\n", raw_f0);
            printf("   Smooth f0       : %7.3f Hz (is_stable: %s)\n", smooth_f0, is_stable ? "YES" : "NO");
            printf("   Final Frequency : %7.3f Hz\n", note_f0);
            printf("   Final Note      : %s (MIDI %d, Target %.2f Hz)\n", note_name_buf, midi, target_freq);
            printf("   Cents Error     : %+.2f cents\n", cents);
            printf("   Confidence      : %5.1f%%\n", confidence);
            printf("   DSP Latency     : %5.2f ms\n", dsp_latency_ms);
            printf("================================================================\n\n");
            fflush(stdout);
        }

        if (state == PITCH_VALID_PITCH) {
            // Kiểm tra xem nốt có bị đổi không
            if (midi != s_diag_tracker.midi) {
                s_diag_tracker.midi = midi;
                s_diag_tracker.target_freq = target_freq;
                snprintf(s_diag_tracker.note_name, sizeof(s_diag_tracker.note_name), "%s", note_name_buf);
                s_diag_tracker.count = 0;
            }

            int cur_idx = s_diag_tracker.count;
            s_diag_tracker.final_f0[cur_idx] = final_f0;
            s_diag_tracker.cents[cur_idx] = cents;
            s_diag_tracker.confidence[cur_idx] = confidence;
            s_diag_tracker.latency_ms[cur_idx] = dsp_latency_ms;
            s_diag_tracker.estimator_mode[cur_idx] = (int)est_mode;
            s_diag_tracker.f1[cur_idx] = mhqi_ok[0] ? mhqi_f0[0] : 0.0f;
            s_diag_tracker.f2[cur_idx] = mhqi_ok[1] ? mhqi_f0[1] : 0.0f;
            s_diag_tracker.f3[cur_idx] = mhqi_ok[2] ? mhqi_f0[2] : 0.0f;
            s_diag_tracker.ok1[cur_idx] = mhqi_ok[0];
            s_diag_tracker.ok2[cur_idx] = mhqi_ok[1];
            s_diag_tracker.ok3[cur_idx] = mhqi_ok[2];
            s_diag_tracker.dev2[cur_idx] = (mhqi_ok[0] && mhqi_ok[1]) ? (mhqi_f0[1] - mhqi_f0[0]) : 0.0f;
            s_diag_tracker.dev3[cur_idx] = (mhqi_ok[0] && mhqi_ok[2]) ? (mhqi_f0[2] - mhqi_f0[0]) : 0.0f;
            s_diag_tracker.mhqi[cur_idx] = mhqi_comp_f0;
            s_diag_tracker.count++;

            fflush(stdout);

            // 2. Khi đủ 20 frame liên tiếp: tính và in bảng thống kê
            if (s_diag_tracker.count >= REAL_PIANO_DIAG_FRAMES) {
                float sum_f0 = 0.0f, sum_sq_f0 = 0.0f;
                float sum_abs_err = 0.0f, max_abs_err = 0.0f;
                float sum_cents = 0.0f, sum_conf = 0.0f, sum_lat = 0.0f;
                int mode_counts[4] = {0};

                for (int i = 0; i < REAL_PIANO_DIAG_FRAMES; i++) {
                    float f = s_diag_tracker.final_f0[i];
                    sum_f0 += f;
                    float err = fabsf(f - s_diag_tracker.target_freq);
                    sum_abs_err += err;
                    if (err > max_abs_err) max_abs_err = err;
                    sum_cents += s_diag_tracker.cents[i];
                    sum_conf  += s_diag_tracker.confidence[i];
                    sum_lat   += s_diag_tracker.latency_ms[i];
                    int m = s_diag_tracker.estimator_mode[i];
                    if (m >= 0 && m < 4) mode_counts[m]++;
                }
                float mean_f0 = sum_f0 / (float)REAL_PIANO_DIAG_FRAMES;
                for (int i = 0; i < REAL_PIANO_DIAG_FRAMES; i++) {
                    float d = s_diag_tracker.final_f0[i] - mean_f0;
                    sum_sq_f0 += d * d;
                }
                float std_f0 = sqrtf(sum_sq_f0 / (float)(REAL_PIANO_DIAG_FRAMES - 1));
                float mean_abs_err = sum_abs_err / (float)REAL_PIANO_DIAG_FRAMES;
                float mean_cents = sum_cents / (float)REAL_PIANO_DIAG_FRAMES;
                float mean_conf = sum_conf / (float)REAL_PIANO_DIAG_FRAMES;
                float mean_lat = sum_lat / (float)REAL_PIANO_DIAG_FRAMES;

                // Harmonic m=1
                float sum_f1 = 0.0f, sum_sq_f1 = 0.0f;
                int n_f1 = 0;
                for (int i = 0; i < REAL_PIANO_DIAG_FRAMES; i++) {
                    if (s_diag_tracker.ok1[i]) {
                        sum_f1 += s_diag_tracker.f1[i];
                        n_f1++;
                    }
                }
                float mean_f1 = (n_f1 > 0) ? (sum_f1 / (float)n_f1) : 0.0f;
                for (int i = 0; i < REAL_PIANO_DIAG_FRAMES; i++) {
                    if (s_diag_tracker.ok1[i]) {
                        float d = s_diag_tracker.f1[i] - mean_f1;
                        sum_sq_f1 += d * d;
                    }
                }
                float std_f1 = (n_f1 > 1) ? sqrtf(sum_sq_f1 / (float)(n_f1 - 1)) : 0.0f;

                // Harmonic m=2
                float sum_f2 = 0.0f, sum_sq_f2 = 0.0f;
                float sum_dev2 = 0.0f, sum_sq_dev2 = 0.0f;
                int n_f2 = 0;
                for (int i = 0; i < REAL_PIANO_DIAG_FRAMES; i++) {
                    if (s_diag_tracker.ok2[i]) {
                        sum_f2 += s_diag_tracker.f2[i];
                        sum_dev2 += s_diag_tracker.dev2[i];
                        n_f2++;
                    }
                }
                float mean_f2 = (n_f2 > 0) ? (sum_f2 / (float)n_f2) : 0.0f;
                float mean_dev2 = (n_f2 > 0) ? (sum_dev2 / (float)n_f2) : 0.0f;
                for (int i = 0; i < REAL_PIANO_DIAG_FRAMES; i++) {
                    if (s_diag_tracker.ok2[i]) {
                        float d = s_diag_tracker.f2[i] - mean_f2;
                        sum_sq_f2 += d * d;
                        float dd = s_diag_tracker.dev2[i] - mean_dev2;
                        sum_sq_dev2 += dd * dd;
                    }
                }
                float std_f2 = (n_f2 > 1) ? sqrtf(sum_sq_f2 / (float)(n_f2 - 1)) : 0.0f;
                float std_dev2 = (n_f2 > 1) ? sqrtf(sum_sq_dev2 / (float)(n_f2 - 1)) : 0.0f;

                // Harmonic m=3
                float sum_f3 = 0.0f, sum_sq_f3 = 0.0f;
                float sum_dev3 = 0.0f, sum_sq_dev3 = 0.0f;
                int n_f3 = 0;
                for (int i = 0; i < REAL_PIANO_DIAG_FRAMES; i++) {
                    if (s_diag_tracker.ok3[i]) {
                        sum_f3 += s_diag_tracker.f3[i];
                        sum_dev3 += s_diag_tracker.dev3[i];
                        n_f3++;
                    }
                }
                float mean_f3 = (n_f3 > 0) ? (sum_f3 / (float)n_f3) : 0.0f;
                float mean_dev3 = (n_f3 > 0) ? (sum_dev3 / (float)n_f3) : 0.0f;
                for (int i = 0; i < REAL_PIANO_DIAG_FRAMES; i++) {
                    if (s_diag_tracker.ok3[i]) {
                        float d = s_diag_tracker.f3[i] - mean_f3;
                        sum_sq_f3 += d * d;
                        float dd = s_diag_tracker.dev3[i] - mean_dev3;
                        sum_sq_dev3 += dd * dd;
                    }
                }
                float std_f3 = (n_f3 > 1) ? sqrtf(sum_sq_f3 / (float)(n_f3 - 1)) : 0.0f;
                float std_dev3 = (n_f3 > 1) ? sqrtf(sum_sq_dev3 / (float)(n_f3 - 1)) : 0.0f;

                // MHQI
                float sum_mhqi = 0.0f, sum_sq_mhqi = 0.0f;
                for (int i = 0; i < REAL_PIANO_DIAG_FRAMES; i++) {
                    sum_mhqi += s_diag_tracker.mhqi[i];
                }
                float mean_mhqi = sum_mhqi / (float)REAL_PIANO_DIAG_FRAMES;
                for (int i = 0; i < REAL_PIANO_DIAG_FRAMES; i++) {
                    float d = s_diag_tracker.mhqi[i] - mean_mhqi;
                    sum_sq_mhqi += d * d;
                }
                float std_mhqi = sqrtf(sum_sq_mhqi / (float)(REAL_PIANO_DIAG_FRAMES - 1));

                printf("\n================================================================================\n");
                printf("=== 20-FRAME HARDWARE VALIDATION SUMMARY FOR NOTE %s ===\n", s_diag_tracker.note_name);
                printf("================================================================================\n");
                printf("Target Note              : %s (MIDI %d)\n", s_diag_tracker.note_name, s_diag_tracker.midi);
                printf("Target Frequency         : %6.2f Hz\n", s_diag_tracker.target_freq);
                printf("Mean Final f0            : %7.3f Hz\n", mean_f0);
                printf("StdDev                   : %6.3f Hz\n", std_f0);
                printf("Mean Absolute Error      : %6.3f Hz\n", mean_abs_err);
                printf("Maximum Absolute Error   : %6.3f Hz\n", max_abs_err);
                printf("Mean Cents               : %+6.2f cents\n", mean_cents);
                printf("Estimator Mode Used      : F1: %d/20 | F2: %d/20 | F3: %d/20 | INVALID: %d/20\n",
                       mode_counts[0], mode_counts[1], mode_counts[2], mode_counts[3]);
                printf("Mean Confidence          : %5.1f%%\n", mean_conf);
                printf("Mean DSP Latency         : %5.2f ms\n", mean_lat);
                printf("Harmonic m=1 (f1)        : Mean = %7.3f Hz | StdDev = %6.3f Hz (valid: %d/20)\n",
                       mean_f1, std_f1, n_f1);
                if (n_f2 > 0) {
                    printf("Harmonic m=2 (f2/2)      : Mean = %7.3f Hz | StdDev = %6.3f Hz (Dev vs m=1: %+6.3f Hz)\n",
                           mean_f2, std_f2, mean_dev2);
                }
                if (n_f3 > 0) {
                    printf("Harmonic m=3 (f3/3)      : Mean = %7.3f Hz | StdDev = %6.3f Hz (Dev vs m=1: %+6.3f Hz)\n",
                           mean_f3, std_f3, mean_dev3);
                }
                printf("Comparison - Legacy MHQI : Mean = %7.3f Hz | StdDev = %6.3f Hz\n",
                       mean_mhqi, std_mhqi);
                printf("================================================================================\n\n");
                fflush(stdout);

                s_diag_tracker.count = 0; // reset streak để sẵn sàng cho lần tiếp theo
            }
        } else {
            // Signal gate đóng: reset chuỗi liên tục
            s_diag_tracker.count = 0;

            int64_t now_us = esp_timer_get_time();
            if (now_us - last_print_time_us >= 400000LL) {
                last_print_time_us = now_us;
                const char *state_str = (state == PITCH_WEAK_SIGNAL) ? "WEAK_SIGNAL" : "NO_SIGNAL";
                printf("[FRAME #%lu | %s] Listening... Max Peak: %6.2f Hz (Bin %4d, Mag: %5.2f)\n",
                       (unsigned long)frame_counter, state_str,
                       (float)max_mag_bin * BIN_RESOLUTION_HZ, max_mag_bin, max_mag_in_range);
                fflush(stdout);
            }
        }
        vTaskDelay(pdMS_TO_TICKS(1));
    }
}
