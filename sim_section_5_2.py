# -*- coding: utf-8 -*-
"""
Simulation script for Section 5.2:
Sine 440 Hz at Fs = 16000 Hz, N = 4096, Periodic Hann window.
Test quadratic interpolation on linear magnitude vs log magnitude.
Also sweep frequency offset to find worst-case bias.
"""

import numpy as np

def run_sim():
    Fs = 16000.0
    N = 4096
    df = Fs / N # 3.90625 Hz
    
    # Target frequency 440.0 Hz
    f_target = 440.0
    t = np.arange(N) / Fs
    
    # Periodic Hann window: w[n] = 0.5 * (1 - cos(2*pi*n / N))
    w_periodic = 0.5 * (1.0 - np.cos(2.0 * np.pi * np.arange(N) / N))
    # Symmetric Hann window: w[n] = 0.5 * (1 - cos(2*pi*n / (N-1)))
    w_symmetric = 0.5 * (1.0 - np.cos(2.0 * np.pi * np.arange(N) / (N - 1)))
    
    for win_name, w in [("Periodic Hann", w_periodic), ("Symmetric Hann", w_symmetric)]:
        x = np.sin(2.0 * np.pi * f_target * t)
        xw = x * w
        X = np.fft.rfft(xw)
        mag = np.abs(X)
        
        # Peak bin
        k = np.argmax(mag)
        alpha, beta, gamma = mag[k-1], mag[k], mag[k+1]
        
        # Linear QI
        denom_lin = alpha - 2.0 * beta + gamma
        p_lin = 0.5 * (alpha - gamma) / denom_lin
        f_lin = (k + p_lin) * df
        err_lin = f_lin - f_target
        
        # Log magnitude QI (Smith / Abe)
        la, lb, lg = np.log(alpha), np.log(beta), np.log(gamma)
        denom_log = la - 2.0 * lb + lg
        p_log = 0.5 * (la - lg) / denom_log
        f_log = (k + p_log) * df
        err_log = f_log - f_target
        
        print(f"=== {win_name} ===")
        print(f"Bin k = {k} ({k*df:.3f} Hz)")
        print(f"Linear: p = {p_lin:.4f}, f = {f_lin:.4f} Hz, Error = {err_lin:+.4f} Hz")
        print(f"Log-mag: p = {p_log:.4f}, f = {f_log:.4f} Hz, Error = {err_log:+.4f} Hz")
        
    # Sweep frequency across one bin [440 - df/2, 440 + df/2] with 200 points
    freqs = np.linspace(440.0 - df/2, 440.0 + df/2, 500)
    max_err_lin = 0.0
    max_err_log = 0.0
    
    for f_in in freqs:
        x = np.sin(2.0 * np.pi * f_in * t)
        xw = x * w_periodic
        X = np.fft.rfft(xw)
        mag = np.abs(X)
        k = np.argmax(mag)
        alpha, beta, gamma = mag[k-1], mag[k], mag[k+1]
        
        # Linear QI
        d_lin = alpha - 2.0 * beta + gamma
        p_l = 0.5 * (alpha - gamma) / d_lin if abs(d_lin) > 1e-12 else 0.0
        f_est_lin = (k + p_l) * df
        err_l = abs(f_est_lin - f_in)
        if err_l > max_err_lin:
            max_err_lin = err_l
            
        # Log QI
        la, lb, lg = np.log(alpha), np.log(beta), np.log(gamma)
        d_log = la - 2.0 * lb + lg
        p_lg = 0.5 * (la - lg) / d_log if abs(d_log) > 1e-12 else 0.0
        f_est_log = (k + p_lg) * df
        err_lg = abs(f_est_log - f_in)
        if err_lg > max_err_log:
            max_err_log = err_lg
            
    print(f"\nWorst-case sweep across bin [±df/2]:")
    print(f"Max absolute error (Linear QI): {max_err_lin:.4f} Hz")
    print(f"Max absolute error (Log-mag QI): {max_err_log:.4f} Hz")

if __name__ == "__main__":
    run_sim()
