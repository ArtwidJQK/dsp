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

current_mock_data = {
    "valid": True,
    "frequency": 440.15,
    "note": "A4",
    "target": 440.00,
    "cents": 0.59,
    "confidence": 98.5,
    "estimator": "F1_PRIMARY",
    "frame": 100,
    "latency_ms": 23.4
}

class CustomHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path == "/" or path == "/index.html":
            return os.path.abspath("main/index.html")
        return super().translate_path(path)

    def do_GET(self):
        if self.path == "/api/data":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(json.dumps(current_mock_data).encode("utf-8"))
            return
        super().do_GET()

    def log_message(self, format, *args):
        pass # suppress server logs

def start_http_server():
    server = HTTPServer((HOST, HTTP_PORT), CustomHandler)
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

async def evaluate_js(ws, expression, msg_id):
    res = await send_cdp_cmd(ws, "Runtime.evaluate", {
        "expression": expression,
        "returnByValue": True,
        "awaitPromise": True
    }, msg_id)
    return res.get("result", {}).get("value")

async def run_frontend_verification():
    print("="*75)
    print("STARTING BROWSER FRONTEND VERIFICATION VIA CHROME CDP")
    print("="*75)

    start_http_server()
    print(f"Local test HTTP Server running at http://{HOST}:{HTTP_PORT}/")

    cmd = [
        CHROME_PATH,
        "--headless=new",
        f"--remote-debugging-port={CDP_PORT}",
        "--user-data-dir=C:\\Users\\dxem1\\AppData\\Local\\Temp\\chrome_test_profile",
        "--disable-gpu",
        "--no-sandbox",
        "--mute-audio",
        f"http://{HOST}:{HTTP_PORT}/"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(2.5)

    global current_mock_data

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
            print("ERROR: No WebSocket debugger URL found from Chrome!")
            return False

        ws = await tornado.websocket.websocket_connect(target_ws_url)
        msg_id = [1]
        print("Connected to Chrome DevTools Protocol WebSocket!")

        await send_cdp_cmd(ws, "Page.enable", {}, msg_id)
        await send_cdp_cmd(ws, "DOM.enable", {}, msg_id)
        await send_cdp_cmd(ws, "Runtime.enable", {}, msg_id)
        await asyncio.sleep(0.8)

        # 1. Check Console Errors
        console_check = await evaluate_js(ws, "window.errors || []", msg_id)
        print("Initial Console Errors:", console_check)

        # 2. Test Scene Navigation & Curtain Transitions
        print("\n--- TEST SCENE TRANSITIONS ---")
        # Cover -> Tuner
        await evaluate_js(ws, "document.getElementById('btnStartTuner').click()", msg_id)
        await asyncio.sleep(1.0)
        active_scene = await evaluate_js(ws, "document.querySelector('.scene.active').id", msg_id)
        print(f"After 'NHẤN ĐỂ BẮT ĐẦU' -> Active Scene: {active_scene} (Expected: scene-tuner)")

        # Tuner -> Info
        await evaluate_js(ws, "document.getElementById('navInfo').click()", msg_id)
        await asyncio.sleep(1.0)
        active_scene = await evaluate_js(ws, "document.querySelector('.scene.active').id", msg_id)
        print(f"After 'navInfo' -> Active Scene: {active_scene} (Expected: scene-info)")

        # Info -> Back to Tuner
        await evaluate_js(ws, "document.getElementById('btnBackToTuner').click()", msg_id)
        await asyncio.sleep(1.0)
        active_scene = await evaluate_js(ws, "document.querySelector('.scene.active').id", msg_id)
        print(f"After 'btnBackToTuner' -> Active Scene: {active_scene} (Expected: scene-tuner)")

        # 3. Test Signal States & Virtual Keyboard
        print("\n--- TEST SIGNAL STATES & VIRTUAL KEYBOARD ---")
        
        # Test A4 (Valid In-Tune)
        current_mock_data = {
            "valid": True, "frequency": 440.10, "note": "A4", "target": 440.00,
            "cents": 0.39, "confidence": 98.0, "estimator": "F1_PRIMARY", "latency_ms": 23.4
        }
        await asyncio.sleep(0.4)
        tuner_state_script = """
        (() => {
            const note = document.getElementById('uiNote').textContent;
            const freq = document.getElementById('uiFrequency').textContent;
            const cents = document.getElementById('uiCentsText').textContent;
            const banner = document.getElementById('uiStateBanner').textContent;
            const bannerClass = document.getElementById('uiStateBanner').className;
            const needleLeft = parseFloat(document.getElementById('uiCentsNeedle').style.left || '50');
            const activeKey = document.querySelector('.active-key');
            const activeKeyNote = activeKey ? activeKey.dataset.note : 'none';
            const cardClasses = document.getElementById('tunerCard').className;
            return { note, freq, cents, banner, bannerClass, needleLeft, activeKeyNote, cardClasses };
        })()
        """
        st_a4 = await evaluate_js(ws, tuner_state_script, msg_id)
        print(f"[State A4 In-Tune]: Note={st_a4['note']}, Freq={st_a4['freq']}, Cents={st_a4['cents']}, Banner='{st_a4['banner']}' ({st_a4['bannerClass']}), KeyHighlighted='{st_a4['activeKeyNote']}', NeedleLeft={st_a4['needleLeft']:.1f}%")

        # Test C4 (Valid Too Low)
        current_mock_data = {
            "valid": True, "frequency": 259.50, "note": "C4", "target": 261.63,
            "cents": -14.15, "confidence": 88.0, "estimator": "F1_PRIMARY", "latency_ms": 24.1
        }
        await asyncio.sleep(0.5)
        st_c4 = await evaluate_js(ws, tuner_state_script, msg_id)
        print(f"[State C4 Too-Low]: Note={st_c4['note']}, Freq={st_c4['freq']}, Cents={st_c4['cents']}, Banner='{st_c4['banner']}' ({st_c4['bannerClass']}), KeyHighlighted='{st_c4['activeKeyNote']}', NeedleLeft={st_c4['needleLeft']:.1f}%")

        # Test E2 (Valid Too High)
        current_mock_data = {
            "valid": True, "frequency": 83.20, "note": "E2", "target": 82.41,
            "cents": 16.52, "confidence": 75.0, "estimator": "F3_FALLBACK", "latency_ms": 24.8
        }
        await asyncio.sleep(0.5)
        st_e2 = await evaluate_js(ws, tuner_state_script, msg_id)
        print(f"[State E2 Too-High]: Note={st_e2['note']}, Freq={st_e2['freq']}, Cents={st_e2['cents']}, Banner='{st_e2['banner']}' ({st_e2['bannerClass']}), KeyHighlighted='{st_e2['activeKeyNote']}', NeedleLeft={st_e2['needleLeft']:.1f}%")

        # Test NO SIGNAL
        current_mock_data = {
            "valid": False, "frequency": 0.0, "note": "N/A", "target": 0.0,
            "cents": 0.0, "confidence": 0.0, "estimator": "NO_SIGNAL", "latency_ms": 0.0
        }
        await asyncio.sleep(0.5)
        st_nosig = await evaluate_js(ws, tuner_state_script, msg_id)
        print(f"[State NO_SIGNAL]: Note={st_nosig['note']}, Freq={st_nosig['freq']}, Cents={st_nosig['cents']}, Banner='{st_nosig['banner']}', KeyHighlighted='{st_nosig['activeKeyNote']}', NeedleLeft={st_nosig['needleLeft']:.1f}%")

        # 4. Test Viewport Matrix (Mandatory Viewports)
        test_viewports = [
            ("Desktop 1920x1080", 1920, 1080, False),
            ("Desktop 1366x768",  1366, 768,  False),
            ("Tablet 1024x768",   1024, 768,  False),
            ("Tablet 768x1024",   768,  1024, False),
            ("Mobile 412x915",    412,  915,  True),
            ("Mobile 390x844",    390,  844,  True),
            ("Mobile 360x800",    360,  800,  True),
            ("Landscape 844x390", 844,  390,  True)
        ]

        print("\n--- TEST RESPONSIVE VIEWPORTS (ZERO HORIZONTAL OVERFLOW MANDATE) ---")
        current_mock_data = {
            "valid": True, "frequency": 440.00, "note": "A4", "target": 440.00,
            "cents": 0.00, "confidence": 99.0, "estimator": "F1_PRIMARY", "latency_ms": 23.4
        }
        
        viewport_results = []
        for name, w, h, is_mobile in test_viewports:
            await send_cdp_cmd(ws, "Emulation.setDeviceMetricsOverride", {
                "width": w,
                "height": h,
                "deviceScaleFactor": 2 if is_mobile else 1,
                "mobile": is_mobile
            }, msg_id)
            await asyncio.sleep(0.3)

            vp_check_script = """
            (() => {
                const docWidth = document.documentElement.scrollWidth;
                const winWidth = window.innerWidth;
                const hasOverflow = docWidth > winWidth;
                const card = document.getElementById('tunerCard');
                const cardRect = card ? card.getBoundingClientRect() : null;
                const cardFits = cardRect ? (cardRect.left >= 0 && cardRect.right <= winWidth + 1) : false;
                const nav = document.querySelector('.bottom-nav');
                const navRect = nav ? nav.getBoundingClientRect() : null;
                const navFits = navRect ? (navRect.left >= 0 && navRect.right <= winWidth + 1) : false;
                return { winWidth, docWidth, hasOverflow, cardFits, navFits };
            })()
            """
            vp_res = await evaluate_js(ws, vp_check_script, msg_id)
            status = "PASSED" if (not vp_res['hasOverflow'] and vp_res['cardFits'] and vp_res['navFits']) else "FAILED"
            viewport_results.append((name, w, h, vp_res, status))
            print(f"  {name:20} ({w:4}x{h:4}) -> DocWidth={vp_res['docWidth']:4}px | HasOverflow={vp_res['hasOverflow']} | CardFits={vp_res['cardFits']} | NavFits={vp_res['navFits']} | {status}")

        ws.close()
        
        all_passed = all(st == "PASSED" for _, _, _, _, st in viewport_results)
        print("\n" + "="*75)
        print(f"FRONTEND BROWSER AUTOMATION RESULT: {'ALL TESTS PASSED' if all_passed else 'TESTS FAILED'}")
        print("="*75)
        
        with open('browser_test_report.json', 'w', encoding='utf-8') as f:
            json.dump({
                'all_passed': all_passed,
                'viewports': viewport_results,
                'state_a4': st_a4,
                'state_c4': st_c4,
                'state_e2': st_e2,
                'state_nosig': st_nosig
            }, f, indent=2)
            
        return all_passed

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except:
            proc.kill()

if __name__ == '__main__':
    asyncio.run(run_frontend_verification())
