import urllib.request
import json
import time

def test_stream(num_samples=15):
    url = "http://192.168.1.238/api/data"
    print(f"Connecting to ESP32-S3 at {url}...")
    for i in range(num_samples):
        try:
            t0 = time.time()
            with urllib.request.urlopen(url, timeout=2) as r:
                rtt_ms = (time.time() - t0) * 1000.0
                body = r.read().decode('utf-8')
                data = json.loads(body)
                print(f"[{i+1}/{num_samples}] Frame: {data.get('frame'):5} | Valid: {str(data.get('valid')):5} | Note: {data.get('note'):4} | Freq: {data.get('frequency', 0.0):7.2f} Hz | Target: {data.get('target', 0.0):7.2f} Hz | Cents: {data.get('cents', 0.0):+6.2f} | Conf: {data.get('confidence', 0.0):5.1f}% | Est: {data.get('estimator'):12} | DSP Latency: {data.get('latency_ms', 0.0):5.2f} ms | HTTP RTT: {rtt_ms:5.1f} ms")
        except Exception as e:
            print(f"[{i+1}/{num_samples}] Error: {e}")
        time.sleep(0.15)

if __name__ == "__main__":
    test_stream(15)
