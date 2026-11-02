#include <stdio.h>
#include <string.h>
#include <math.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_err.h"
#include "esp_timer.h"
#include "esp_idf_version.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// ==============================================================================
// 1. PIN & AUDIO DSP CONFIGURATION
// ==============================================================================
#define I2S_MIC_BCLK_PIN      GPIO_NUM_4
#define I2S_MIC_WS_PIN        GPIO_NUM_5
#define I2S_MIC_DATA_IN_PIN   GPIO_NUM_6

#define SAMPLE_RATE_HZ        16000
#define FFT_N                 4096   // N = 4096 points
#define BIN_RESOLUTION_HZ     ((float)SAMPLE_RATE_HZ / (float)FFT_N) // 16000 / 4096 = 3.90625 Hz

// Piano fundamental range: A0 (27.5 Hz) to C8 (4186.0 Hz)
#define PIANO_MIN_FREQ_HZ     27.5f
#define PIANO_MAX_FREQ_HZ     4186.0f
#define PIANO_MIN_BIN         7     // 7 * 3.90625 = 27.34 Hz
#define PIANO_MAX_BIN         1072  // 1072 * 3.90625 = 4187.5 Hz

// Noise threshold: maximum spectral peak must exceed this to qualify as a signal
#define NOISE_MAG_THRESHOLD   20.0f
#define MAX_CANDIDATE_PEAKS   16

static const char *TAG = "PIANO_TUNER";

// Precomputed Hann window
static float s_hann_window[FFT_N];

// FFT Working Buffers (allocated in DRAM)
static int32_t *s_raw_samples = NULL;
static float   *s_fft_real    = NULL;
static float   *s_fft_imag    = NULL;
static float   *s_magnitude   = NULL; // Length FFT_N / 2 (2048 bins)

// Peak Candidate Structure
typedef struct {
    int   bin;
    float raw_freq;
    float mag;
    float score;
    int   harmonics_found;
} peak_candidate_t;

// ==============================================================================
// 2. I2S DRIVER INITIALIZATION
// ==============================================================================
#if ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(5, 0, 0)
#include "driver/i2s_std.h"

static i2s_chan_handle_t rx_handle = NULL;

static esp_err_t init_i2s_microphone(void)
{
    ESP_LOGI(TAG, "Initializing I2S RX channel with ESP-IDF v5/v6 modern driver...");

    i2s_chan_config_t chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_AUTO, I2S_ROLE_MASTER);
    chan_cfg.dma_desc_num = 8;
    chan_cfg.dma_frame_num = 1024;

    esp_err_t ret = i2s_new_channel(&chan_cfg, NULL, &rx_handle);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to create I2S RX channel: %s", esp_err_to_name(ret));
        return ret;
    }

    i2s_std_config_t std_cfg = {
        .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(SAMPLE_RATE_HZ),
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_MONO),
        .gpio_cfg = {
            .mclk = I2S_GPIO_UNUSED,
            .bclk = I2S_MIC_BCLK_PIN,
            .ws   = I2S_MIC_WS_PIN,
            .dout = I2S_GPIO_UNUSED,
            .din  = I2S_MIC_DATA_IN_PIN,
            .invert_flags = {
                .mclk_inv = false,
                .bclk_inv = false,
                .ws_inv = false,
            },
        },
    };

    std_cfg.slot_cfg.slot_mask = I2S_STD_SLOT_LEFT;

    ret = i2s_channel_init_std_mode(rx_handle, &std_cfg);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to init I2S standard mode: %s", esp_err_to_name(ret));
        return ret;
    }

    ret = i2s_channel_enable(rx_handle);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to enable I2S channel: %s", esp_err_to_name(ret));
        return ret;
    }

    ESP_LOGI(TAG, "I2S initialized successfully (16 kHz, 32-bit, Mono Left).");
    return ESP_OK;
}

static esp_err_t read_i2s_samples(int32_t *buffer, size_t samples_count, size_t *samples_read)
{
    size_t bytes_read = 0;
    esp_err_t ret = i2s_channel_read(rx_handle, buffer, samples_count * sizeof(int32_t), &bytes_read, pdMS_TO_TICKS(1500));
    if (ret == ESP_OK) {
        *samples_read = bytes_read / sizeof(int32_t);
    } else {
        *samples_read = 0;
    }
    return ret;
}

#else
#include "driver/i2s.h"
#define I2S_PORT_NUM I2S_NUM_0

static esp_err_t init_i2s_microphone(void)
{
    ESP_LOGI(TAG, "Initializing legacy I2S driver...");
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = SAMPLE_RATE_HZ,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 8,
        .dma_buf_len = 1024,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };
    i2s_pin_config_t pin_config = {
        .bck_io_num = I2S_MIC_BCLK_PIN,
        .ws_io_num = I2S_MIC_WS_PIN,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = I2S_MIC_DATA_IN_PIN
    };
    ESP_ERROR_CHECK(i2s_driver_install(I2S_PORT_NUM, &i2s_config, 0, NULL));
    ESP_ERROR_CHECK(i2s_set_pin(I2S_PORT_NUM, &pin_config));
    return ESP_OK;
}

static esp_err_t read_i2s_samples(int32_t *buffer, size_t samples_count, size_t *samples_read)
{
    size_t bytes_read = 0;
    esp_err_t ret = i2s_read(I2S_PORT_NUM, buffer, samples_count * sizeof(int32_t), &bytes_read, pdMS_TO_TICKS(1500));
    *samples_read = (ret == ESP_OK) ? (bytes_read / sizeof(int32_t)) : 0;
    return ret;
}
#endif

// ==============================================================================
// 3. DSP & FFT IMPLEMENTATION
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

// ==============================================================================
// 4. MAIN TUNER TASK: FFT + HARMONIC FUNDAMENTAL DETECTION + QUADRATIC INTERP
// ==============================================================================
void app_main(void)
{
    ESP_LOGI(TAG, "=== PIANO TUNER: STAGE 3 - FUNDAMENTAL DETECTION & INTERPOLATION ===");
    ESP_LOGI(TAG, "Fs = %d Hz, N = %d, Resolution = %.4f Hz/bin", 
             SAMPLE_RATE_HZ, FFT_N, BIN_RESOLUTION_HZ);

    init_hann_window();

    // Allocate buffers
    s_raw_samples = (int32_t *)malloc(FFT_N * sizeof(int32_t));
    s_fft_real    = (float *)malloc(FFT_N * sizeof(float));
    s_fft_imag    = (float *)malloc(FFT_N * sizeof(float));
    s_magnitude   = (float *)malloc((FFT_N / 2) * sizeof(float));

    if (!s_raw_samples || !s_fft_real || !s_fft_imag || !s_magnitude) {
        ESP_LOGE(TAG, "Failed to allocate memory for FFT buffers!");
        return;
    }

    esp_err_t err = init_i2s_microphone();
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "I2S Init Failed! Aborting.");
        return;
    }

    ESP_LOGI(TAG, "System ready. Listening for piano notes...");

    int64_t last_print_time_us = 0;

    while (1) {
        // Step 1: Collect exactly N = 4096 samples at Fs = 16000 Hz
        size_t samples_read = 0;
        esp_err_t ret = read_i2s_samples(s_raw_samples, FFT_N, &samples_read);

        if (ret != ESP_OK || samples_read < FFT_N) {
            ESP_LOGW(TAG, "I2S read incomplete (%d/%d samples)", samples_read, FFT_N);
            vTaskDelay(pdMS_TO_TICKS(10));
            continue;
        }

        // Step 2 & 3: Convert INMP441 raw samples and remove DC offset
        double sum = 0.0;
        for (int n = 0; n < FFT_N; n++) {
            int32_t s24 = s_raw_samples[n] >> 8;
            float x_norm = (float)s24 / 8388608.0f;
            s_fft_real[n] = x_norm;
            sum += x_norm;
        }
        float mean = (float)(sum / (double)FFT_N);

        // Step 4 & 5: Apply Hann window
        for (int n = 0; n < FFT_N; n++) {
            float x_dc = s_fft_real[n] - mean;
            s_fft_real[n] = x_dc * s_hann_window[n];
            s_fft_imag[n] = 0.0f;
        }

        // Step 6: 4096-point FFT
        fft_radix2(s_fft_real, s_fft_imag, FFT_N);

        // Step 7: Magnitude spectrum
        int num_bins = FFT_N / 2;
        for (int k = 0; k < num_bins; k++) {
            s_magnitude[k] = sqrtf(s_fft_real[k] * s_fft_real[k] + s_fft_imag[k] * s_fft_imag[k]);
        }

        // Step 8: Search for peak candidates within piano fundamental range (27.5 Hz - 4186 Hz)
        float max_mag_in_range = 0.0f;
        int max_mag_bin = 0;
        for (int k = PIANO_MIN_BIN; k <= PIANO_MAX_BIN; k++) {
            if (s_magnitude[k] > max_mag_in_range) {
                max_mag_in_range = s_magnitude[k];
                max_mag_bin = k;
            }
        }

        int64_t now_us = esp_timer_get_time();

        // 8.1 Check Noise Threshold (NO SIGNAL)
        if (max_mag_in_range < NOISE_MAG_THRESHOLD) {
            // Print NO SIGNAL every 3 seconds to avoid flooding console
            if (now_us - last_print_time_us >= 6000000LL) {
                last_print_time_us = now_us;
                printf("\n==================== [MÁY ĐO CAO ĐỘ PIANO: KHÔNG CÓ TÍN HIỆU] ====================\n");
                printf("Trạng thái                 : CHƯA PHÁT HIỆN ÂM THANH (NO SIGNAL)\n");
                printf("Biên độ cực đại đo được    : %8.2f  (Ngưỡng kích hoạt tối thiểu: %.1f)\n", max_mag_in_range, NOISE_MAG_THRESHOLD);
                printf("Chu kỳ cập nhật            : 6.0 giây / lần\n");
                printf("Ghi chú                    : Phòng yên tĩnh hoặc chưa gõ phím đàn\n");
                printf("==================================================================================\n");
            }
            continue;
        }

        // 8.2 Detect local peaks within piano range
        peak_candidate_t candidates[MAX_CANDIDATE_PEAKS];
        int candidate_count = 0;

        for (int k = PIANO_MIN_BIN; k <= PIANO_MAX_BIN && candidate_count < MAX_CANDIDATE_PEAKS; k++) {
            if (s_magnitude[k] > s_magnitude[k - 1] && s_magnitude[k] > s_magnitude[k + 1]) {
                // Must be at least 12% of the strongest peak in range
                if (s_magnitude[k] >= 0.12f * max_mag_in_range && s_magnitude[k] >= 8.0f) {
                    candidates[candidate_count].bin = k;
                    candidates[candidate_count].raw_freq = (float)k * BIN_RESOLUTION_HZ;
                    candidates[candidate_count].mag = s_magnitude[k];
                    candidates[candidate_count].score = 0.0f;
                    candidates[candidate_count].harmonics_found = 0;
                    candidate_count++;
                }
            }
        }

        // Fallback: if no local peak passed thresholds, add the maximum peak
        if (candidate_count == 0) {
            candidates[0].bin = max_mag_bin;
            candidates[0].raw_freq = (float)max_mag_bin * BIN_RESOLUTION_HZ;
            candidates[0].mag = max_mag_in_range;
            candidates[0].score = max_mag_in_range;
            candidates[0].harmonics_found = 1;
            candidate_count = 1;
        }

        // 8.3 Harmonic-based candidate scoring
        int best_cand_idx = 0;
        float best_score = -1.0f;

        for (int c = 0; c < candidate_count; c++) {
            int k_cand = candidates[c].bin;
            float cand_mag = candidates[c].mag;
            float total_score = 0.0f;
            int h_count = 0;

            int max_harmonic = 8;
            if (k_cand * max_harmonic >= num_bins) {
                max_harmonic = (num_bins - 1) / k_cand;
            }

            for (int h = 1; h <= max_harmonic; h++) {
                int target_k = h * k_cand;
                int start_w = (target_k - 2 < 0) ? 0 : target_k - 2;
                int end_w   = (target_k + 2 >= num_bins) ? num_bins - 1 : target_k + 2;

                float max_h_mag = 0.0f;
                for (int w = start_w; w <= end_w; w++) {
                    if (s_magnitude[w] > max_h_mag) {
                        max_h_mag = s_magnitude[w];
                    }
                }

                // If a noticeable harmonic peak is present
                if (max_h_mag >= 0.10f * cand_mag || h == 1) {
                    h_count++;
                    float weight = 1.0f / sqrtf((float)h);
                    total_score += weight * max_h_mag;
                }
            }

            candidates[c].score = total_score;
            candidates[c].harmonics_found = h_count;

            if (total_score > best_score) {
                best_score = total_score;
                best_cand_idx = c;
            }
        }

        // Step 9: Quadratic Interpolation around selected fundamental bin k
        int sel_bin = candidates[best_cand_idx].bin;
        float alpha = s_magnitude[sel_bin - 1];
        float beta  = s_magnitude[sel_bin];
        float gamma = s_magnitude[sel_bin + 1];

        float denom = alpha - 2.0f * beta + gamma;
        float p = 0.0f;
        if (fabsf(denom) > 1e-6f) {
            p = 0.5f * (alpha - gamma) / denom;
        }
        if (p < -0.5f) p = -0.5f;
        if (p > 0.5f)  p = 0.5f;

        float f0 = ((float)sel_bin + p) * BIN_RESOLUTION_HZ;

        // Print results (rate limited to at most once every 1.5 seconds)
        if (now_us - last_print_time_us >= 6000000LL) {
            last_print_time_us = now_us;

            printf("\n==================== [MÁY ĐO CAO ĐỘ PIANO: ĐÃ PHÁT HIỆN CAO ĐỘ] ====================\n");
            printf("Tần số cơ bản nội suy (f0) : %8.2f Hz  (Tần số thực tế của nốt đàn)\n", f0);
            printf("Bin FFT tương ứng          : %4d       (Tần số thô của bin: %.2f Hz)\n", sel_bin, (float)sel_bin * BIN_RESOLUTION_HZ);
            printf("Độ lệch nội suy bậc hai (p): %+7.4f     (Khoảng lệch [-0.5, +0.5] bin)\n", p);
            printf("Điểm số chuỗi họa âm       : %8.2f     (Khớp %d họa âm: 1f, 2f, 3f...)\n", candidates[best_cand_idx].score, candidates[best_cand_idx].harmonics_found);
            printf("Chu kỳ báo cáo             : 6.0 giây / lần\n");
            printf("-----------------------------------------------------------------------------------\n");
            printf("Bảng phân tích các đỉnh phổ ứng viên (Top %d đỉnh trong dải 27.5 - 4186 Hz):\n", candidate_count);
            printf("  [STT] |  Bin  | Tần số thô |  Biên độ  | Số họa âm |  Điểm số   | Đánh giá\n");

            for (int c = 0; c < candidate_count; c++) {
                const char *sel_mark = (c == best_cand_idx) ? "<=== TẦN SỐ CƠ BẢN (f0)" : "";
                printf("  [%2d]  | %5d | %8.2f Hz | %9.2f |    %2d     | %10.2f | %s\n", 
                       c + 1, 
                       candidates[c].bin, 
                       candidates[c].raw_freq, 
                       candidates[c].mag, 
                       candidates[c].harmonics_found, 
                       candidates[c].score, 
                       sel_mark);
            }
            printf("===================================================================================\n");
        }
    }
}
