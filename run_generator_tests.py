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
HTTP_PORT = 8995
CDP_PORT = 9230

polling_request_count = 0
pending_responses = {}
captured_exceptions = []
captured_console_errors = []

class TestHTTPHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path == "/" or path == "/index.html":
            return os.path.abspath("d:/dsp/artwid/piano_tuner/main/index.html")
        return super().translate_path(path)

    def do_GET(self):
        global polling_request_count
        if self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
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
        pass

def start_http_server():
    server = HTTPServer((HOST, HTTP_PORT), TestHTTPHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server

async def cdp_dispatcher(ws):
    while True:
        try:
            msg_raw = await ws.read_message()
            if msg_raw is None:
                break
            msg = json.loads(msg_raw)
            if "id" in msg:
                pending_responses[msg["id"]] = msg
            else:
                method = msg.get("method")
                params = msg.get("params", {})
                if method == "Runtime.exceptionThrown":
                    details = params.get("exceptionDetails", {})
                    text = details.get("text", "")
                    exc_desc = details.get("exception", {}).get("description", "")
                    captured_exceptions.append(f"{text}: {exc_desc}")
                elif method == "Log.entryAdded":
                    entry = params.get("entry", {})
                    if entry.get("level") == "error":
                        captured_console_errors.append(f"[{entry.get('source')}] {entry.get('text')}")
                elif method == "Runtime.consoleAPICalled":
                    if params.get("type") == "error":
                        args_str = " ".join([str(a.get("value", a.get("description", ""))) for a in params.get("args", [])])
                        captured_console_errors.append(f"[Console.error] {args_str}")
        except Exception:
            break

async def send_cdp_cmd(ws, method, params=None, msg_id=[1]):
    mid = msg_id[0]
    msg_id[0] += 1
    req = {"id": mid, "method": method, "params": params or {}}
    await ws.write_message(json.dumps(req))
    while mid not in pending_responses:
        await asyncio.sleep(0.01)
    res = pending_responses.pop(mid)
    return res.get("result", {})

async def eval_js(ws, expr, msg_id=[1]):
    res = await send_cdp_cmd(ws, "Runtime.evaluate", {
        "expression": expr,
        "returnByValue": True,
        "awaitPromise": True
    }, msg_id)
    return res.get("result", {}).get("value")

async def run_full_verification_suite():
    global polling_request_count
    server = start_http_server()
    print(f"[TEST SETUP] HTTP Server listening on http://{HOST}:{HTTP_PORT}/")

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

    try:
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
        print("[TEST SETUP] Connected to Chrome DevTools Protocol (CDP)")

        # Start background event dispatcher for continuous exception & console error logging
        asyncio.create_task(cdp_dispatcher(ws))

        msg_id = [1]
        await send_cdp_cmd(ws, "Runtime.enable", msg_id=msg_id)
        await send_cdp_cmd(ws, "Page.enable", msg_id=msg_id)
        await send_cdp_cmd(ws, "Log.enable", msg_id=msg_id)

        await asyncio.sleep(0.6)

        # -------------------------------------------------------------
        # 1. FIX 1: Proper Browser Error Collection (Runtime.exceptionThrown & Log.entryAdded)
        # -------------------------------------------------------------
        print("\n--- FIX 1: Browser Error Collection via CDP Events ---")
        exc_count = len(captured_exceptions)
        console_err_count = len(captured_console_errors)
        print(f"Captured exceptions (Runtime.exceptionThrown): {exc_count}")
        print(f"Captured console errors (Log.entryAdded / Runtime.consoleAPICalled): {console_err_count}")
        fix1_pass = (exc_count == 0 and console_err_count == 0)
        results["fix1_real_error_collection"] = {
            "method": "CDP Runtime.exceptionThrown & Log.entryAdded",
            "exception_count": exc_count,
            "console_error_count": console_err_count,
            "exceptions": captured_exceptions,
            "console_errors": captured_console_errors,
            "pass": fix1_pass
        }
        print(f"PASS Fix 1: Error collection active (0 exceptions, 0 console errors): {fix1_pass}")

        # -------------------------------------------------------------
        # 2. FIX 3: Generator Animation Lifecycle (Demand-Driven Animation)
        # -------------------------------------------------------------
        print("\n--- FIX 3: Generator Animation Lifecycle (rAF on Generator Only) ---")
        init_scene = await eval_js(ws, "currentScene", msg_id)
        init_anim_id = await eval_js(ws, "waveAnimId", msg_id)
        print(f"Initial scene '{init_scene}': waveAnimId = {init_anim_id} (No perpetual loop on initial load)")

        # Enter generator
        await eval_js(ws, "switchSceneWithCurtain('generator')", msg_id)
        await asyncio.sleep(1.0)
        gen_scene = await eval_js(ws, "currentScene", msg_id)
        gen_anim_id = await eval_js(ws, "waveAnimId", msg_id)
        print(f"Entered '{gen_scene}': waveAnimId = {gen_anim_id} (Animation loop started)")

        # Leave to tuner
        await eval_js(ws, "switchSceneWithCurtain('tuner')", msg_id)
        await asyncio.sleep(1.0)
        tuner_scene = await eval_js(ws, "currentScene", msg_id)
        tuner_anim_id = await eval_js(ws, "waveAnimId", msg_id)
        print(f"Navigated to '{tuner_scene}': waveAnimId = {tuner_anim_id} (Animation cancelled, 0 FPS CPU waste)")

        # Return to generator
        await eval_js(ws, "switchSceneWithCurtain('generator')", msg_id)
        await asyncio.sleep(1.0)
        reentry_anim_id = await eval_js(ws, "waveAnimId", msg_id)
        print(f"Returned to generator: waveAnimId = {reentry_anim_id} (Animation loop resumed cleanly)")

        fix3_pass = (
            init_anim_id is None and
            gen_anim_id is not None and
            tuner_anim_id is None and
            reentry_anim_id is not None
        )
        results["fix3_animation_lifecycle"] = {
            "initial_waveAnimId": init_anim_id,
            "generator_waveAnimId": gen_anim_id,
            "tuner_waveAnimId": tuner_anim_id,
            "reentry_waveAnimId": reentry_anim_id,
            "pass": fix3_pass
        }
        print(f"PASS Fix 3: Animation lifecycle strictly demand-driven: {fix3_pass}")

        # -------------------------------------------------------------
        # 3. FIX 4: Audio Lifecycle Concurrency & Rapid Click Protection
        # -------------------------------------------------------------
        print("\n--- FIX 4: Audio Lifecycle Concurrency & Rapid Clicks ---")
        # Normal play / stop
        await eval_js(ws, "startGenerator()", msg_id)
        await asyncio.sleep(0.15)
        osc_active = await eval_js(ws, "activeOsc !== null", msg_id)
        gain_active = await eval_js(ws, "activeGain !== null", msg_id)
        ctx_state = await eval_js(ws, "audioCtx ? audioCtx.state : null", msg_id)

        await eval_js(ws, "stopGenerator()", msg_id)
        await asyncio.sleep(0.1)
        osc_cleared = await eval_js(ws, "activeOsc === null", msg_id)

        # Rapid Clicks Stress Test (10 toggles within 100ms)
        print("Simulating 10 rapid clicks on Play/Stop toggle within 100ms...")
        rapid_code = """
        (async () => {
            for (let i = 0; i < 10; i++) {
                toggleGenerator();
                await new Promise(r => setTimeout(r, 10));
            }
        })()
        """
        await eval_js(ws, rapid_code, msg_id)
        await asyncio.sleep(0.3)
        await eval_js(ws, "stopGenerator()", msg_id)
        await asyncio.sleep(0.15)

        rapid_playing = await eval_js(ws, "isGenPlaying", msg_id)
        rapid_osc = await eval_js(ws, "activeOsc === null", msg_id)
        rapid_gain = await eval_js(ws, "activeGain === null", msg_id)
        rapid_starting = await eval_js(ws, "isAudioStarting", msg_id)
        print(f"After rapid clicks: isGenPlaying={rapid_playing}, activeOsc==null={rapid_osc}, activeGain==null={rapid_gain}, isAudioStarting={rapid_starting}")

        fix4_pass = (osc_active and gain_active and osc_cleared and not rapid_playing and rapid_osc and rapid_gain and not rapid_starting)
        results["fix4_audio_concurrency"] = {
            "ctx_state": ctx_state,
            "no_orphaned_nodes": rapid_osc and rapid_gain,
            "pass": fix4_pass
        }
        print(f"PASS Fix 4: Audio concurrency protected against rapid toggles, 0 orphaned nodes: {fix4_pass}")

        # -------------------------------------------------------------
        # 4. FIX 2 & TESTS: AudioNode Structure Tests (Muted Headless Testing)
        # -------------------------------------------------------------
        print("\n--- FIX 2: AudioNode Graph & Controls (Muted Headless Structural Testing) ---")
        # 440 Hz
        await eval_js(ws, "setGeneratorFrequency(440.00, true)", msg_id)
        freq_sync = await eval_js(ws, "genFreq === 440.00 && parseFloat(document.getElementById('genFreqInput').value) === 440.00", msg_id)

        # Start tone
        await eval_js(ws, "startGenerator()", msg_id)
        await asyncio.sleep(0.15)
        # Dynamic frequency shift during playback to 523.25 Hz
        await eval_js(ws, "setGeneratorFrequency(523.25, true)", msg_id)
        await asyncio.sleep(0.15)
        shifted_freq = await eval_js(ws, "activeOsc ? activeOsc.frequency.value : null", msg_id)
        shift_ok = (abs(shifted_freq - 523.25) < 5.0)

        # Waveforms (sine, square, triangle)
        wave_results = {}
        for w in ["sine", "square", "triangle"]:
            await eval_js(ws, f"setGeneratorWaveform('{w}')", msg_id)
            actual_w = await eval_js(ws, "activeOsc ? activeOsc.type : null", msg_id)
            wave_results[w] = (actual_w == w)

        # Volume adjustment
        await eval_js(ws, "setGeneratorVolume(0.15)", msg_id)
        vol_readout = await eval_js(ws, "document.getElementById('genVolReadout').innerText", msg_id)
        vol_ok = (vol_readout == "15%")

        # Presets (A4, C4, C5, D3, E3, E2)
        presets_verified = {}
        for note, p_freq in [("A4", 440.0), ("C4", 261.626), ("C5", 523.251), ("D3", 146.832), ("E3", 164.814), ("E2", 82.407)]:
            await eval_js(ws, f"document.getElementById('preset{note}').click()", msg_id)
            cur_f = await eval_js(ws, "genFreq", msg_id)
            presets_verified[note] = (abs(cur_f - p_freq) < 0.05)

        await eval_js(ws, "stopGenerator()", msg_id)
        await asyncio.sleep(0.1)

        structural_pass = (
            freq_sync and
            shift_ok and
            all(wave_results.values()) and
            vol_ok and
            all(presets_verified.values())
        )
        results["structural_audio_tests"] = {
            "mode": "Muted Headless Structural Testing (AudioNode Graph)",
            "audible_output_physically_measured": "NOT VERIFIED (Automation runs muted; requires physical checklist)",
            "pass": structural_pass,
            "waveforms": wave_results,
            "presets": presets_verified
        }
        print(f"PASS AudioNode Structural Verification (Muted Automation): {structural_pass}")

        # -------------------------------------------------------------
        # 5. REGRESSION: Tuner Scene Navigation & Polling
        # -------------------------------------------------------------
        print("\n--- REGRESSION: Tuner Scene Navigation & Polling ---")
        await eval_js(ws, "switchSceneWithCurtain('tuner')", msg_id)
        await asyncio.sleep(1.0)
        tuner_note = await eval_js(ws, "document.getElementById('uiNote').innerText", msg_id)
        tuner_freq = await eval_js(ws, "document.getElementById('uiFrequency').innerText", msg_id)
        tuner_has_signal = await eval_js(ws, "document.getElementById('tunerCard').classList.contains('has-signal')", msg_id)
        tuner_ok = (tuner_note == "A4" and tuner_freq == "440.05 Hz" and tuner_has_signal)
        print(f"Tuner scene UI: Note='{tuner_note}', Freq='{tuner_freq}', has-signal={tuner_has_signal} -> PASS={tuner_ok}")

        p_before = polling_request_count
        await asyncio.sleep(0.5)
        p_delta = polling_request_count - p_before
        polling_ok = p_delta >= 2
        print(f"Polling requests in 500ms: {p_delta} -> PASS={polling_ok}")

        # -------------------------------------------------------------
        # 6. RESPONSIVE LAYOUT (6 resolutions)
        # -------------------------------------------------------------
        print("\n--- REGRESSION: Responsive Layout Across 6 Resolutions ---")
        resolutions = [
            (1920, 1080, "Desktop 1080p"),
            (1366, 768, "Laptop 768p"),
            (768, 1024, "Tablet Portrait"),
            (412, 915, "Mobile (Pixel 7)"),
            (390, 844, "Mobile (iPhone 14)"),
            (360, 800, "Mobile (Small Galaxy 360px)")
        ]
        resp_all_ok = True
        resp_details = {}
        for width, height, label in resolutions:
            await send_cdp_cmd(ws, "Emulation.setDeviceMetricsOverride", {
                "width": width,
                "height": height,
                "deviceScaleFactor": 1,
                "mobile": width <= 640
            }, msg_id)
            await asyncio.sleep(0.2)
            await eval_js(ws, "switchSceneWithCurtain('generator')", msg_id)
            await asyncio.sleep(0.9)

            no_overflow = await eval_js(ws, "document.documentElement.scrollWidth <= window.innerWidth + 2", msg_id)
            card_w = await eval_js(ws, "document.getElementById('generatorCard').getBoundingClientRect().width", msg_id)
            is_ok = no_overflow and (card_w <= width)
            if not is_ok:
                resp_all_ok = False
            resp_details[f"{width}x{height}"] = {"label": label, "card_width": round(card_w, 1), "no_overflow": no_overflow, "pass": is_ok}
            print(f"  {width}x{height} ({label}): card={round(card_w, 1)}px, no-overflow={no_overflow} -> {'PASS' if is_ok else 'FAIL'}")

        results["responsive_tests"] = {
            "all_passed": resp_all_ok,
            "details": resp_details
        }

        # -------------------------------------------------------------
        # 7. FINAL RUNTIME ERROR AUDIT
        # -------------------------------------------------------------
        print("\n--- FINAL RUNTIME ERROR AUDIT (WHOLE SESSION) ---")
        print(f"Total runtime JS exceptions: {len(captured_exceptions)}")
        print(f"Total runtime console errors: {len(captured_console_errors)}")
        final_errors_zero = (len(captured_exceptions) == 0 and len(captured_console_errors) == 0)

        all_passed = (
            fix1_pass and
            fix3_pass and
            fix4_pass and
            structural_pass and
            tuner_ok and
            polling_ok and
            resp_all_ok and
            final_errors_zero
        )
        results["ALL_VERIFICATION_TESTS_PASSED"] = all_passed
        print("\n=======================================================")
        print(f"OVERALL STATUS: {'ALL CHECKS PASSED (100%)' if all_passed else 'SOME CHECKS FAILED'}")
        print("=======================================================")

        with open("d:/dsp/artwid/piano_tuner/generator_test_report.json", "w", encoding="utf-8") as rf:
            json.dump(results, rf, indent=2)

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except:
            proc.kill()

if __name__ == "__main__":
    asyncio.run(run_full_verification_suite())
