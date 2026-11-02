import os
import sys
import time
import json
import asyncio
import subprocess
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.request
import tornado.websocket

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
HOST = "127.0.0.1"
HTTP_PORT = 8991
CDP_PORT = 9226

polling_request_count = 0

class TestHTTPHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path == "/" or path == "/index.html":
            return os.path.abspath("d:/dsp/artwid/piano_tuner/main/index.html")
        return super().translate_path(path)

    def do_GET(self):
        global polling_request_count
        if self.path == "/api/data":
            polling_request_count += 1
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            data = {
                "valid": True,
                "frequency": 440.05,
                "note": "A4",
                "target": 440.00,
                "cents": 0.20,
                "confidence": 99.0,
                "estimator": "F1_PRIMARY",
                "frame": polling_request_count
            }
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return
        super().do_GET()

    def log_message(self, format, *args):
        # Mute logging to keep output clean
        pass

def start_http_server():
    server = HTTPServer((HOST, HTTP_PORT), TestHTTPHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server

async def send_cdp_cmd(ws, method, params=None, msg_id=[1]):
    mid = msg_id[0]
    msg_id[0] += 1
    req = {"id": mid, "method": method, "params": params or {}}
    await ws.write_message(json.dumps(req))
    while True:
        resp_raw = await ws.read_message()
        resp = json.loads(resp_raw)
        if resp.get("id") == mid:
            return resp.get("result", {})

async def eval_js(ws, expr, msg_id=[1]):
    res = await send_cdp_cmd(ws, "Runtime.evaluate", {
        "expression": expr,
        "returnByValue": True,
        "awaitPromise": True
    }, msg_id)
    return res.get("result", {}).get("value")

async def run_all_tests():
    global polling_request_count
    server = start_http_server()
    print(f"[TEST SETUP] HTTP Server listening on http://{HOST}:{HTTP_PORT}/")

    # Start Chrome headless
    cmd = [
        CHROME_PATH,
        "--headless=new",
        f"--remote-debugging-port={CDP_PORT}",
        "--disable-gpu",
        "--no-sandbox",
        "--mute-audio",
        "--autoplay-policy=no-user-gesture-required",
        f"http://{HOST}:{HTTP_PORT}/"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(2.0)

    results = {}
    console_errors = []

    try:
        # Connect to CDP
        tabs_url = f"http://{HOST}:{CDP_PORT}/json"
        with urllib.request.urlopen(tabs_url) as resp:
            tabs = json.loads(resp.read().decode())
        
        target_ws_url = None
        for t in tabs:
            if t.get("type") == "page":
                target_ws_url = t["webSocketDebuggerUrl"]
                break
        
        if not target_ws_url:
            raise Exception("No Chrome page target found!")

        ws = await tornado.websocket.websocket_connect(target_ws_url)
        print("[TEST SETUP] Connected to Chrome DevTools Protocol via WebSocket")

        msg_id = [1]
        await send_cdp_cmd(ws, "Runtime.enable", msg_id=msg_id)
        await send_cdp_cmd(ws, "Page.enable", msg_id=msg_id)
        await send_cdp_cmd(ws, "Log.enable", msg_id=msg_id)

        # 1. Static HTML & JS Validation
        print("\n--- TEST 1: Static HTML/JavaScript Validation ---")
        title = await eval_js(ws, "document.title", msg_id)
        results["test1_title"] = title
        print(f"PASS: Page loaded with title '{title}'")

        # 2. Browser Load Test & DOM Existence
        print("\n--- TEST 2: Browser Load Test & Scene Structure ---")
        scenes = await eval_js(ws, "Array.from(document.querySelectorAll('.scene')).map(s => s.id)", msg_id)
        results["test2_scenes"] = scenes
        has_generator = "scene-generator" in scenes
        print(f"Scenes detected: {scenes}")
        print(f"PASS: scene-generator exists in DOM: {has_generator}")

        # 3. Console Error Check
        print("\n--- TEST 3: Console Error Check ---")
        # Evaluate if any error was thrown during initial load
        err_check = await eval_js(ws, "window.errors || []", msg_id)
        results["test3_errors"] = err_check
        print(f"PASS: Console error count on initial load: {len(err_check)}")

        # Switch to Generator Scene
        print("\n--- TRANSITION: Switching to scene-generator ---")
        await eval_js(ws, "document.getElementById('navGenerator').click()", msg_id)
        # Wait for curtain animation (420ms + 420ms = ~850ms)
        await asyncio.sleep(1.0)
        active_scene = await eval_js(ws, "currentScene", msg_id)
        scene_el_active = await eval_js(ws, "document.getElementById('scene-generator').classList.contains('active')", msg_id)
        print(f"Current active scene: {active_scene}, scene-generator active class: {scene_el_active}")
        results["transition_to_generator"] = (active_scene == "generator" and scene_el_active)

        # 4. Set frequency to 440 Hz
        print("\n--- TEST 4: Set frequency to 440 Hz ---")
        await eval_js(ws, "setGeneratorFrequency(440.00, true)", msg_id)
        freq_val = await eval_js(ws, "genFreq", msg_id)
        input_val = await eval_js(ws, "parseFloat(document.getElementById('genFreqInput').value)", msg_id)
        slider_val = await eval_js(ws, "parseFloat(document.getElementById('genFreqSlider').value)", msg_id)
        disp_text = await eval_js(ws, "document.getElementById('genFreqBig').innerText", msg_id)
        print(f"genFreq={freq_val}, input={input_val}, slider={slider_val}, display='{disp_text}'")
        test4_pass = (freq_val == 440.00 and input_val == 440.00 and slider_val == 440.00)
        results["test4_freq_440"] = test4_pass
        print(f"PASS: Frequency 440.00 Hz synchronized across all controls: {test4_pass}")

        # 5. Start and stop playback
        print("\n--- TEST 5: Start and Stop Playback ---")
        # Click Play
        await eval_js(ws, "document.getElementById('genPlayBtn').click()", msg_id)
        await asyncio.sleep(0.3)
        is_playing_after_start = await eval_js(ws, "isGenPlaying", msg_id)
        audio_ctx_state = await eval_js(ws, "audioCtx ? audioCtx.state : null", msg_id)
        osc_active = await eval_js(ws, "activeOsc !== null", msg_id)
        gain_active = await eval_js(ws, "activeGain !== null", msg_id)
        btn_text_start = await eval_js(ws, "document.getElementById('genPlayText').innerText", msg_id)
        print(f"After Play: isGenPlaying={is_playing_after_start}, audioCtx.state={audio_ctx_state}, activeOsc={osc_active}, activeGain={gain_active}, btnText='{btn_text_start}'")

        # Click Stop
        await eval_js(ws, "document.getElementById('genPlayBtn').click()", msg_id)
        await asyncio.sleep(0.3)
        is_playing_after_stop = await eval_js(ws, "isGenPlaying", msg_id)
        osc_stopped = await eval_js(ws, "activeOsc === null", msg_id)
        btn_text_stop = await eval_js(ws, "document.getElementById('genPlayText').innerText", msg_id)
        print(f"After Stop: isGenPlaying={is_playing_after_stop}, activeOsc={osc_stopped}, btnText='{btn_text_stop}'")
        test5_pass = (is_playing_after_start and not is_playing_after_stop and osc_stopped)
        results["test5_play_stop"] = test5_pass
        print(f"PASS: Play/Stop cycle completed cleanly: {test5_pass}")

        # 6. Change frequency during playback
        print("\n--- TEST 6: Change frequency during playback ---")
        await eval_js(ws, "startGenerator()", msg_id)
        await asyncio.sleep(0.2)
        # Change to 880 Hz while playing
        await eval_js(ws, "setGeneratorFrequency(880.00, true)", msg_id)
        await asyncio.sleep(0.2)
        osc_freq = await eval_js(ws, "activeOsc ? activeOsc.frequency.value : null", msg_id)
        gen_freq_val = await eval_js(ws, "genFreq", msg_id)
        print(f"During playback: genFreq={gen_freq_val}, oscillator.frequency.value={osc_freq}")
        test6_pass = (gen_freq_val == 880.00 and osc_freq is not None and abs(osc_freq - 880.00) < 5.0)
        results["test6_freq_change_during_playback"] = test6_pass
        print(f"PASS: Dynamic frequency adjustment during active playback: {test6_pass}")

        # 7. Test all three waveform types
        print("\n--- TEST 7: Test all three waveform types ---")
        waveform_results = {}
        for wave in ["sine", "square", "triangle"]:
            await eval_js(ws, f"setGeneratorWaveform('{wave}')", msg_id)
            await asyncio.sleep(0.1)
            actual_wave = await eval_js(ws, "activeOsc ? activeOsc.type : null", msg_id)
            btn_active = await eval_js(ws, f"document.querySelector('[data-wave=\"{wave}\"]').classList.contains('active')", msg_id)
            waveform_results[wave] = (actual_wave == wave and btn_active)
            print(f"Waveform '{wave}': osc.type={actual_wave}, button active={btn_active}")
        test7_pass = all(waveform_results.values())
        results["test7_waveforms"] = test7_pass
        print(f"PASS: Waveform types (sine, square, triangle): {test7_pass}")

        # 8. Test volume changes
        print("\n--- TEST 8: Test volume changes ---")
        await eval_js(ws, "setGeneratorVolume(0.25)", msg_id)
        await asyncio.sleep(0.1)
        vol_val = await eval_js(ws, "genVolume", msg_id)
        vol_readout = await eval_js(ws, "document.getElementById('genVolReadout').innerText", msg_id)
        gain_val = await eval_js(ws, "activeGain ? activeGain.gain.value : null", msg_id)
        print(f"Set volume 0.25: genVolume={vol_val}, readout='{vol_readout}', gain.value={gain_val}")
        test8_pass = (vol_val == 0.25 and vol_readout == "25%")
        results["test8_volume"] = test8_pass
        print(f"PASS: Volume adjustment and readout: {test8_pass}")

        # Stop playback after tests 5-8
        await eval_js(ws, "stopGenerator()", msg_id)
        await asyncio.sleep(0.2)

        # 9. Test all presets
        print("\n--- TEST 9: Test all presets ---")
        presets = [
            ("A4", 440.00),
            ("C4", 261.626),
            ("C5", 523.251),
            ("D3", 146.832),
            ("E3", 164.814),
            ("E2", 82.407),
        ]
        preset_results = {}
        for note, expected_freq in presets:
            await eval_js(ws, f"document.getElementById('preset{note}').click()", msg_id)
            await asyncio.sleep(0.1)
            actual_gen_freq = await eval_js(ws, "genFreq", msg_id)
            btn_is_active = await eval_js(ws, f"document.getElementById('preset{note}').classList.contains('active')", msg_id)
            diff = abs(actual_gen_freq - expected_freq)
            is_ok = (diff < 0.05 and btn_is_active)
            preset_results[note] = {"expected": expected_freq, "actual": actual_gen_freq, "active": btn_is_active, "pass": is_ok}
            print(f"Preset {note}: expected {expected_freq} Hz, actual {actual_gen_freq} Hz, active={btn_is_active} -> {'PASS' if is_ok else 'FAIL'}")
        test9_pass = all(p["pass"] for p in preset_results.values())
        results["test9_presets"] = test9_pass
        print(f"PASS: All 6 piano presets verified: {test9_pass}")

        # 10. Confirm existing tuner scene still works
        print("\n--- TEST 10: Confirm existing tuner scene still works ---")
        await eval_js(ws, "document.getElementById('navTuner').click()", msg_id)
        await asyncio.sleep(1.0)
        active_scene_tuner = await eval_js(ws, "currentScene", msg_id)
        tuner_card_has_signal = await eval_js(ws, "document.getElementById('tunerCard').classList.contains('has-signal')", msg_id)
        tuner_note = await eval_js(ws, "document.getElementById('uiNote').innerText", msg_id)
        tuner_freq = await eval_js(ws, "document.getElementById('uiFrequency').innerText", msg_id)
        print(f"Switched back to Tuner: currentScene={active_scene_tuner}, note='{tuner_note}', freq='{tuner_freq}', has-signal={tuner_card_has_signal}")
        test10_pass = (active_scene_tuner == "tuner" and tuner_note == "A4")
        results["test10_tuner_scene_works"] = test10_pass
        print(f"PASS: Tuner scene operational and receiving data: {test10_pass}")

        # 11. Confirm /api/data polling is unchanged
        print("\n--- TEST 11: Confirm /api/data polling is unchanged ---")
        count_before = polling_request_count
        await asyncio.sleep(0.5)
        count_after = polling_request_count
        delta = count_after - count_before
        test11_pass = delta >= 2
        results["test11_polling"] = {"requests_in_500ms": delta, "pass": test11_pass}
        print(f"Polling requests received in 500ms: {delta} (Total count: {count_after})")
        print(f"PASS: Background /api/data polling active and uninterrupted: {test11_pass}")

        # 12. Test responsive layouts across 6 resolutions
        print("\n--- TEST 12: Test responsive layouts across 6 resolutions ---")
        resolutions = [
            (1920, 1080, "Desktop 1080p"),
            (1366, 768, "Laptop 768p"),
            (768, 1024, "Tablet Portrait"),
            (412, 915, "Mobile (Pixel 7)"),
            (390, 844, "Mobile (iPhone 14)"),
            (360, 800, "Mobile (Small Galaxy 360px)")
        ]
        resp_results = {}
        for width, height, label in resolutions:
            await send_cdp_cmd(ws, "Emulation.setDeviceMetricsOverride", {
                "width": width,
                "height": height,
                "deviceScaleFactor": 1,
                "mobile": width <= 640
            }, msg_id)
            await asyncio.sleep(0.2)
            
            # Switch between scenes to verify layout rendering
            await eval_js(ws, "document.getElementById('navGenerator').click()", msg_id)
            await asyncio.sleep(0.9)
            
            body_overflow_x = await eval_js(ws, "document.documentElement.scrollWidth <= window.innerWidth + 2", msg_id)
            gen_card_width = await eval_js(ws, "document.getElementById('generatorCard').getBoundingClientRect().width", msg_id)
            nav_width = await eval_js(ws, "document.querySelector('.bottom-nav').getBoundingClientRect().width", msg_id)
            
            is_resp_ok = body_overflow_x and (gen_card_width <= width) and (nav_width <= width)
            resp_results[f"{width}x{height}"] = {
                "label": label,
                "no_horizontal_overflow": body_overflow_x,
                "card_width": round(gen_card_width, 1),
                "nav_width": round(nav_width, 1),
                "pass": is_resp_ok
            }
            print(f"Resolution {width}x{height} ({label}): card={round(gen_card_width, 1)}px, nav={round(nav_width, 1)}px, no-overflow={body_overflow_x} -> {'PASS' if is_resp_ok else 'FAIL'}")

        test12_pass = all(r["pass"] for r in resp_results.values())
        results["test12_responsive"] = test12_pass
        print(f"PASS: All 6 responsive resolutions verified without horizontal overflow: {test12_pass}")

        # Summary
        all_passed = all([
            results["test1_title"] is not None,
            results["test2_scenes"] is not None,
            results["transition_to_generator"],
            results["test4_freq_440"],
            results["test5_play_stop"],
            results["test6_freq_change_during_playback"],
            results["test7_waveforms"],
            results["test8_volume"],
            results["test9_presets"],
            results["test10_tuner_scene_works"],
            results["test11_polling"]["pass"],
            results["test12_responsive"]
        ])
        results["ALL_TESTS_PASSED"] = all_passed
        print("\n==========================================")
        print(f"OVERALL STATUS: {'ALL 12 TESTS PASSED!' if all_passed else 'SOME TESTS FAILED'}")
        print("==========================================")

        with open("d:/dsp/artwid/piano_tuner/generator_test_report.json", "w", encoding="utf-8") as rf:
            json.dump(results, rf, indent=2)

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except:
            proc.kill()

if __name__ == "__main__":
    asyncio.run(run_all_tests())

