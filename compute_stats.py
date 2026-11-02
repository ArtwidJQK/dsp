import re
import numpy as np

# Test 1 frames: 1146 to 1158 (13 frames)
t1_text = """
>>> [FRAME #1146 | VALID_PITCH] <<<
1. AC RMS                  :   161565.3 counts (norm: 0.019260)
2. Maximum FFT Magnitude   :       5.96 (Bin 113 = 441.41 Hz)
3. Candidate Frequency     :     441.41 Hz (Bin 113)
4. Candidate Magnitude     :       5.96
5. Local Noise Floor       :       0.10
6. Spectral Prominence/SNR :      58.12 x  (+35.3 dB)
7. Harmonic Score          :       5.96 (Harmonics verified: 1)
8. Final Confidence/State  : VALID_PITCH
9. Estimated Pitch (f0 QI) :     440.16 Hz (Interpolation p = -0.3197)
----------------------------------------------------------------------
>>> [FRAME #1147 | VALID_PITCH] <<<
1. AC RMS                  :   132934.9 counts (norm: 0.015847)
2. Maximum FFT Magnitude   :       6.08 (Bin 113 = 441.41 Hz)
3. Candidate Frequency     :     441.41 Hz (Bin 113)
4. Candidate Magnitude     :       6.08
5. Local Noise Floor       :       0.10
6. Spectral Prominence/SNR :      60.64 x  (+35.7 dB)
7. Harmonic Score          :       6.08 (Harmonics verified: 1)
8. Final Confidence/State  : VALID_PITCH
9. Estimated Pitch (f0 QI) :     440.21 Hz (Interpolation p = -0.3050)
----------------------------------------------------------------------
>>> [FRAME #1148 | VALID_PITCH] <<<
1. AC RMS                  :   121058.8 counts (norm: 0.014431)
2. Maximum FFT Magnitude   :       6.02 (Bin 113 = 441.41 Hz)
3. Candidate Frequency     :     441.41 Hz (Bin 113)
4. Candidate Magnitude     :       6.02
5. Local Noise Floor       :       0.09
6. Spectral Prominence/SNR :      63.71 x  (+36.1 dB)
7. Harmonic Score          :       6.02 (Harmonics verified: 1)
8. Final Confidence/State  : VALID_PITCH
9. Estimated Pitch (f0 QI) :     440.06 Hz (Interpolation p = -0.3441)
----------------------------------------------------------------------
>>> [FRAME #1149 | VALID_PITCH] <<<
1. AC RMS                  :   207746.6 counts (norm: 0.024765)
2. Maximum FFT Magnitude   :      10.56 (Bin 10 = 39.06 Hz)
3. Candidate Frequency     :     441.41 Hz (Bin 113)
4. Candidate Magnitude     :       6.14
5. Local Noise Floor       :       0.08
6. Spectral Prominence/SNR :      78.14 x  (+37.9 dB)
7. Harmonic Score          :       6.14 (Harmonics verified: 1)
8. Final Confidence/State  : VALID_PITCH
9. Estimated Pitch (f0 QI) :     440.19 Hz (Interpolation p = -0.3118)
----------------------------------------------------------------------
>>> [FRAME #1150 | VALID_PITCH] <<<
1. AC RMS                  :   228365.3 counts (norm: 0.027223)
2. Maximum FFT Magnitude   :       8.30 (Bin 9 = 35.16 Hz)
3. Candidate Frequency     :     441.41 Hz (Bin 113)
4. Candidate Magnitude     :       5.88
5. Local Noise Floor       :       0.09
6. Spectral Prominence/SNR :      68.58 x  (+36.7 dB)
7. Harmonic Score          :       5.88 (Harmonics verified: 1)
8. Final Confidence/State  : VALID_PITCH
9. Estimated Pitch (f0 QI) :     440.17 Hz (Interpolation p = -0.3162)
----------------------------------------------------------------------
>>> [FRAME #1151 | VALID_PITCH] <<<
1. AC RMS                  :   117244.3 counts (norm: 0.013977)
2. Maximum FFT Magnitude   :       7.47 (Bin 7 = 27.34 Hz)
3. Candidate Frequency     :     441.41 Hz (Bin 113)
4. Candidate Magnitude     :       6.11
5. Local Noise Floor       :       0.11
6. Spectral Prominence/SNR :      55.41 x  (+34.9 dB)
7. Harmonic Score          :       6.11 (Harmonics verified: 1)
8. Final Confidence/State  : VALID_PITCH
9. Estimated Pitch (f0 QI) :     440.27 Hz (Interpolation p = -0.2897)
----------------------------------------------------------------------
>>> [FRAME #1152 | VALID_PITCH] <<<
1. AC RMS                  :   166447.6 counts (norm: 0.019842)
2. Maximum FFT Magnitude   :       6.33 (Bin 113 = 441.41 Hz)
3. Candidate Frequency     :     441.41 Hz (Bin 113)
4. Candidate Magnitude     :       6.33
5. Local Noise Floor       :       0.08
6. Spectral Prominence/SNR :      75.95 x  (+37.6 dB)
7. Harmonic Score          :       6.33 (Harmonics verified: 1)
8. Final Confidence/State  : VALID_PITCH
9. Estimated Pitch (f0 QI) :     440.17 Hz (Interpolation p = -0.3174)
----------------------------------------------------------------------
>>> [FRAME #1153 | VALID_PITCH] <<<
1. AC RMS                  :   177294.0 counts (norm: 0.021135)
2. Maximum FFT Magnitude   :       9.20 (Bin 7 = 27.34 Hz)
3. Candidate Frequency     :     441.41 Hz (Bin 113)
4. Candidate Magnitude     :       5.95
5. Local Noise Floor       :       0.08
6. Spectral Prominence/SNR :      73.32 x  (+37.3 dB)
7. Harmonic Score          :       5.95 (Harmonics verified: 1)
8. Final Confidence/State  : VALID_PITCH
9. Estimated Pitch (f0 QI) :     440.08 Hz (Interpolation p = -0.3386)
----------------------------------------------------------------------
>>> [FRAME #1154 | VALID_PITCH] <<<
1. AC RMS                  :   130252.9 counts (norm: 0.015527)
2. Maximum FFT Magnitude   :       9.04 (Bin 11 = 42.97 Hz)
3. Candidate Frequency     :     441.41 Hz (Bin 113)
4. Candidate Magnitude     :       6.04
5. Local Noise Floor       :       0.10
6. Spectral Prominence/SNR :      61.03 x  (+35.7 dB)
7. Harmonic Score          :       6.04 (Harmonics verified: 1)
8. Final Confidence/State  : VALID_PITCH
9. Estimated Pitch (f0 QI) :     440.14 Hz (Interpolation p = -0.3234)
----------------------------------------------------------------------
>>> [FRAME #1155 | VALID_PITCH] <<<
1. AC RMS                  :   178032.3 counts (norm: 0.021223)
2. Maximum FFT Magnitude   :      12.09 (Bin 10 = 39.06 Hz)
3. Candidate Frequency     :     441.41 Hz (Bin 113)
4. Candidate Magnitude     :       6.01
5. Local Noise Floor       :       0.15
6. Spectral Prominence/SNR :      39.35 x  (+31.9 dB)
7. Harmonic Score          :       6.01 (Harmonics verified: 1)
8. Final Confidence/State  : VALID_PITCH
9. Estimated Pitch (f0 QI) :     440.24 Hz (Interpolation p = -0.2986)
----------------------------------------------------------------------
>>> [FRAME #1156 | VALID_PITCH] <<<
1. AC RMS                  :    89607.0 counts (norm: 0.010682)
2. Maximum FFT Magnitude   :       6.01 (Bin 113 = 441.41 Hz)
3. Candidate Frequency     :     441.41 Hz (Bin 113)
4. Candidate Magnitude     :       6.01
5. Local Noise Floor       :       0.10
6. Spectral Prominence/SNR :      57.78 x  (+35.2 dB)
7. Harmonic Score          :       6.01 (Harmonics verified: 1)
8. Final Confidence/State  : VALID_PITCH
9. Estimated Pitch (f0 QI) :     440.16 Hz (Interpolation p = -0.3198)
----------------------------------------------------------------------
>>> [FRAME #1157 | VALID_PITCH] <<<
1. AC RMS                  :    63237.9 counts (norm: 0.007539)
2. Maximum FFT Magnitude   :       6.07 (Bin 113 = 441.41 Hz)
3. Candidate Frequency     :     441.41 Hz (Bin 113)
4. Candidate Magnitude     :       6.07
5. Local Noise Floor       :       0.12
6. Spectral Prominence/SNR :      51.01 x  (+34.2 dB)
7. Harmonic Score          :       6.07 (Harmonics verified: 1)
8. Final Confidence/State  : VALID_PITCH
9. Estimated Pitch (f0 QI) :     440.13 Hz (Interpolation p = -0.3274)
----------------------------------------------------------------------
>>> [FRAME #1158 | VALID_PITCH] <<<
1. AC RMS                  :    91592.8 counts (norm: 0.010919)
2. Maximum FFT Magnitude   :       6.16 (Bin 113 = 441.41 Hz)
3. Candidate Frequency     :     441.41 Hz (Bin 113)
4. Candidate Magnitude     :       6.16
5. Local Noise Floor       :       0.10
6. Spectral Prominence/SNR :      58.77 x  (+35.4 dB)
7. Harmonic Score          :       6.16 (Harmonics verified: 1)
8. Final Confidence/State  : VALID_PITCH
9. Estimated Pitch (f0 QI) :     440.33 Hz (Interpolation p = -0.2748)
----------------------------------------------------------------------
"""

# Test 2 frames: 1199 to 1211 (13 frames)
t2_text = """
>>> [FRAME #1199 | VALID_PITCH] <<<
1. AC RMS                  :   206896.4 counts (norm: 0.024664)
2. Maximum FFT Magnitude   :      12.10 (Bin 113 = 441.41 Hz)
3. Candidate Frequency     :     441.41 Hz (Bin 113)
4. Candidate Magnitude     :      12.10
5. Local Noise Floor       :       0.20
6. Spectral Prominence/SNR :      60.39 x  (+35.6 dB)
7. Harmonic Score          :      17.73 (Harmonics verified: 3)
8. Final Confidence/State  : VALID_PITCH
9. Estimated Pitch (f0 QI) :     440.29 Hz (Interpolation p = -0.2847)
----------------------------------------------------------------------
>>> [FRAME #1200 | VALID_PITCH] <<<
1. AC RMS                  :   224999.1 counts (norm: 0.026822)
2. Maximum FFT Magnitude   :      11.96 (Bin 113 = 441.41 Hz)
3. Candidate Frequency     :     441.41 Hz (Bin 113)
4. Candidate Magnitude     :      11.96
5. Local Noise Floor       :       0.22
6. Spectral Prominence/SNR :      53.44 x  (+34.6 dB)
7. Harmonic Score          :      17.43 (Harmonics verified: 3)
8. Final Confidence/State  : VALID_PITCH
9. Estimated Pitch (f0 QI) :     440.24 Hz (Interpolation p = -0.2988)
----------------------------------------------------------------------
>>> [FRAME #1201 | VALID_PITCH] <<<
1. AC RMS                  :   158168.1 counts (norm: 0.018855)
2. Maximum FFT Magnitude   :      12.27 (Bin 113 = 441.41 Hz)
3. Candidate Frequency     :     441.41 Hz (Bin 113)
4. Candidate Magnitude     :      12.27
5. Local Noise Floor       :       0.33
6. Spectral Prominence/SNR :      37.02 x  (+31.4 dB)
7. Harmonic Score          :      17.65 (Harmonics verified: 3)
8. Final Confidence/State  : VALID_PITCH
9. Estimated Pitch (f0 QI) :     440.25 Hz (Interpolation p = -0.2967)
----------------------------------------------------------------------
>>> [FRAME #1202 | VALID_PITCH] <<<
1. AC RMS                  :   149248.7 counts (norm: 0.017792)
2. Maximum FFT Magnitude   :      12.04 (Bin 113 = 441.41 Hz)
3. Candidate Frequency     :     441.41 Hz (Bin 113)
4. Candidate Magnitude     :      12.04
5. Local Noise Floor       :       0.21
6. Spectral Prominence/SNR :      56.02 x  (+35.0 dB)
7. Harmonic Score          :      17.43 (Harmonics verified: 3)
8. Final Confidence/State  : VALID_PITCH
9. Estimated Pitch (f0 QI) :     440.20 Hz (Interpolation p = -0.3093)
----------------------------------------------------------------------
>>> [FRAME #1203 | VALID_PITCH] <<<
1. AC RMS                  :   113077.4 counts (norm: 0.013480)
2. Maximum FFT Magnitude   :      11.66 (Bin 113 = 441.41 Hz)
3. Candidate Frequency     :     441.41 Hz (Bin 113)
4. Candidate Magnitude     :      11.66
5. Local Noise Floor       :       0.20
6. Spectral Prominence/SNR :      56.93 x  (+35.1 dB)
7. Harmonic Score          :      16.69 (Harmonics verified: 3)
8. Final Confidence/State  : VALID_PITCH
9. Estimated Pitch (f0 QI) :     440.23 Hz (Interpolation p = -0.3020)
----------------------------------------------------------------------
>>> [FRAME #1204 | VALID_PITCH] <<<
1. AC RMS                  :   119423.2 counts (norm: 0.014236)
2. Maximum FFT Magnitude   :      11.96 (Bin 113 = 441.41 Hz)
3. Candidate Frequency     :     441.41 Hz (Bin 113)
4. Candidate Magnitude     :      11.96
5. Local Noise Floor       :       0.19
6. Spectral Prominence/SNR :      63.83 x  (+36.1 dB)
7. Harmonic Score          :      15.91 (Harmonics verified: 2)
8. Final Confidence/State  : VALID_PITCH
9. Estimated Pitch (f0 QI) :     440.18 Hz (Interpolation p = -0.3132)
----------------------------------------------------------------------
>>> [FRAME #1205 | VALID_PITCH] <<<
1. AC RMS                  :   154734.8 counts (norm: 0.018446)
2. Maximum FFT Magnitude   :      12.41 (Bin 113 = 441.41 Hz)
3. Candidate Frequency     :     441.41 Hz (Bin 113)
4. Candidate Magnitude     :      12.41
5. Local Noise Floor       :       0.22
6. Spectral Prominence/SNR :      56.14 x  (+35.0 dB)
7. Harmonic Score          :      16.27 (Harmonics verified: 2)
8. Final Confidence/State  : VALID_PITCH
9. Estimated Pitch (f0 QI) :     440.22 Hz (Interpolation p = -0.3030)
----------------------------------------------------------------------
>>> [FRAME #1206 | VALID_PITCH] <<<
1. AC RMS                  :   156540.2 counts (norm: 0.018661)
2. Maximum FFT Magnitude   :      12.35 (Bin 113 = 441.41 Hz)
3. Candidate Frequency     :     441.41 Hz (Bin 113)
4. Candidate Magnitude     :      12.35
5. Local Noise Floor       :       0.22
6. Spectral Prominence/SNR :      56.27 x  (+35.0 dB)
7. Harmonic Score          :      17.13 (Harmonics verified: 3)
8. Final Confidence/State  : VALID_PITCH
9. Estimated Pitch (f0 QI) :     440.13 Hz (Interpolation p = -0.3256)
----------------------------------------------------------------------
>>> [FRAME #1207 | VALID_PITCH] <<<
1. AC RMS                  :   188044.2 counts (norm: 0.022417)
2. Maximum FFT Magnitude   :      12.39 (Bin 113 = 441.41 Hz)
3. Candidate Frequency     :     441.41 Hz (Bin 113)
4. Candidate Magnitude     :      12.39
5. Local Noise Floor       :       0.33
6. Spectral Prominence/SNR :      37.79 x  (+31.5 dB)
7. Harmonic Score          :      16.24 (Harmonics verified: 2)
8. Final Confidence/State  : VALID_PITCH
9. Estimated Pitch (f0 QI) :     440.15 Hz (Interpolation p = -0.3219)
----------------------------------------------------------------------
>>> [FRAME #1208 | VALID_PITCH] <<<
1. AC RMS                  :   111243.7 counts (norm: 0.013261)
2. Maximum FFT Magnitude   :      12.11 (Bin 113 = 441.41 Hz)
3. Candidate Frequency     :     441.41 Hz (Bin 113)
4. Candidate Magnitude     :      12.11
5. Local Noise Floor       :       0.14
6. Spectral Prominence/SNR :      85.14 x  (+38.6 dB)
7. Harmonic Score          :      16.05 (Harmonics verified: 2)
8. Final Confidence/State  : VALID_PITCH
9. Estimated Pitch (f0 QI) :     440.20 Hz (Interpolation p = -0.3075)
----------------------------------------------------------------------
>>> [FRAME #1209 | VALID_PITCH] <<<
1. AC RMS                  :   111302.8 counts (norm: 0.013268)
2. Maximum FFT Magnitude   :      12.36 (Bin 113 = 441.41 Hz)
3. Candidate Frequency     :     441.41 Hz (Bin 113)
4. Candidate Magnitude     :      12.36
5. Local Noise Floor       :       0.14
6. Spectral Prominence/SNR :      90.49 x  (+39.1 dB)
7. Harmonic Score          :      16.41 (Harmonics verified: 2)
8. Final Confidence/State  : VALID_PITCH
9. Estimated Pitch (f0 QI) :     440.14 Hz (Interpolation p = -0.3244)
----------------------------------------------------------------------
>>> [FRAME #1210 | VALID_PITCH] <<<
1. AC RMS                  :   102413.7 counts (norm: 0.012209)
2. Maximum FFT Magnitude   :      10.75 (Bin 113 = 441.41 Hz)
3. Candidate Frequency     :     441.41 Hz (Bin 113)
4. Candidate Magnitude     :      10.75
5. Local Noise Floor       :       0.14
6. Spectral Prominence/SNR :      76.53 x  (+37.7 dB)
7. Harmonic Score          :      14.22 (Harmonics verified: 2)
8. Final Confidence/State  : VALID_PITCH
9. Estimated Pitch (f0 QI) :     440.13 Hz (Interpolation p = -0.3279)
----------------------------------------------------------------------
>>> [FRAME #1211 | VALID_PITCH] <<<
1. AC RMS                  :    89392.4 counts (norm: 0.010656)
2. Maximum FFT Magnitude   :      10.17 (Bin 113 = 441.41 Hz)
3. Candidate Frequency     :     441.41 Hz (Bin 113)
4. Candidate Magnitude     :      10.17
5. Local Noise Floor       :       0.10
6. Spectral Prominence/SNR :      98.02 x  (+39.8 dB)
7. Harmonic Score          :      13.46 (Harmonics verified: 2)
8. Final Confidence/State  : VALID_PITCH
9. Estimated Pitch (f0 QI) :     440.17 Hz (Interpolation p = -0.3173)
----------------------------------------------------------------------
"""

def analyze(text, name):
    from run_validation_test import parse_stream
    frames = parse_stream(text)
    total = len(frames)
    valid_count = sum(1 for f in frames if f['state'] == 'VALID_PITCH')
    f0s = [f['f0'] for f in frames if f['f0'] is not None]
    mags = [f['cand_mag'] for f in frames if 'cand_mag' in f]
    proms = [f['prominence'] for f in frames if 'prominence' in f]
    
    print(f"=== {name} ===")
    print(f"Total frames: {total}")
    print(f"VALID_PITCH frames: {valid_count} / {total} ({valid_count/total*100:.1f}%)")
    print(f"f0 Median: {np.median(f0s):.2f} Hz")
    print(f"f0 Min: {np.min(f0s):.2f} Hz | Max: {np.max(f0s):.2f} Hz | Std: {np.std(f0s):.3f} Hz")
    print(f"Magnitude Median: {np.median(mags):.2f} | Min: {np.min(mags):.2f} | Max: {np.max(mags):.2f}")
    print(f"Prominence Median: {np.median(proms):.2f} x | Min: {np.min(proms):.2f} x | Max: {np.max(proms):.2f} x")
    print()

if __name__ == '__main__':
    analyze(t1_text, "TEST 1: SINE 440 HZ AT 10 CM")
    analyze(t2_text, "TEST 2: ONLINEPIANIST PIANO A4 AT 10-20 CM")
