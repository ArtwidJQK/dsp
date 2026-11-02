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
HTTP_PORT = 8990
CDP_PORT = 9225

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
            data = {
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
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return
        super().do_GET()

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

async def run_browser_tests():
    start_http_server()
    print(f"HTTP Server started at http://{HOST}:{HTTP_PORT}/")

    # Start Chrome headless
    cmd = [
        CHROME_PATH,
        "--headless=new",
        f"--remote-debugging-port={CDP_PORT}",
        "--disable-gpu",
        "--no-sandbox",
        "--mute-audio",
        f"http://{HOST}:{HTTP_PORT}/"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(1.5)

    try:
        # Get target websocket URL by finding the page tab
        tabs_url = f"http://{HOST}:{CDP_PORT}/json"
        with urllib.request.urlopen(tabs_url) as resp:
            tabs = json.loads(resp.read().decode())
        
        target_ws_url = None
        for t in tabs:
            if t.get("type") == "page" and "127.0.0.1" in t.get("url", ""):
                target_ws_url = t["webSocketDebuggerUrl"]
                break
        if not target_ws_url:
            for t in tabs:
                if t.get("type") == "page":
                    target_ws_url = t["webSocketDebuggerUrl"]
                    break
        
        if not target_ws_url:
            print("ERROR: No WebSocket debugger URL found from Chrome!")
            return None

        ws = await tornado.websocket.websocket_connect(target_ws_url)
        msg_id = [1]
        print("Connected to Chrome DevTools Protocol WebSocket (Target: Page)!")

        await send_cdp_cmd(ws, "Page.enable", {}, msg_id)
        await send_cdp_cmd(ws, "DOM.enable", {}, msg_id)
        await asyncio.sleep(1.0)

        # Viewport test matrix as required by the user prompt
        test_viewports = [
            ("Desktop 1920x1080", 1920, 1080, False),
            ("Desktop 1366x768", 1366, 768, False),
            ("Tablet 768x1024", 768, 1024, False),
            ("Mobile Portrait 360x800", 360, 800, True),
            ("Mobile Portrait 390x844", 390, 844, True),
            ("Mobile Portrait 412x915", 412, 915, True),
            ("Mobile Landscape 844x390", 844, 390, True)
        ]

        results = []
        for name, w, h, is_mobile in test_viewports:
            # Emulate device metrics
            await send_cdp_cmd(ws, "Emulation.setDeviceMetricsOverride", {
                "width": w,
                "height": h,
                "deviceScaleFactor": 2 if is_mobile else 1,
                "mobile": is_mobile
            }, msg_id)

            await asyncio.sleep(0.3)

            # Switch scene to Tuner
            await evaluate_js(ws, "document.getElementById('navTuner').click()", msg_id)
            await asyncio.sleep(1.0) # wait for curtain transition

            # Check dimensions, overflow, elements
            check_script = """
            (() => {
                const docWidth = document.documentElement.scrollWidth;
                const winWidth = window.innerWidth;
                const winHeight = window.innerHeight;
                const hasHorizOverflow = docWidth > winWidth;
                
                const card = document.getElementById('tunerCard');
                const cardRect = card ? card.getBoundingClientRect() : null;
                const cardFitsHoriz = cardRect ? (cardRect.left >= 0 && cardRect.right <= winWidth + 1) : false;
                
                const meterBox = document.querySelector('.meter-track-box');
                const meterRect = meterBox ? meterBox.getBoundingClientRect() : null;
                const meterFits = meterRect ? (meterRect.left >= 0 && meterRect.right <= winWidth + 1) : false;
                
                const nav = document.querySelector('.bottom-nav');
                const navRect = nav ? nav.getBoundingClientRect() : null;
                const navFits = navRect ? (navRect.left >= 0 && navRect.right <= winWidth + 1) : false;

                const noteEl = document.getElementById('uiNote');
                const noteText = noteEl ? noteEl.textContent : '';

                const freqEl = document.getElementById('uiFrequency');
                const freqText = freqEl ? freqEl.textContent : '';

                const centsText = document.getElementById('uiCentsText');
                const centsVal = centsText ? centsText.textContent : '';

                const centsMarker = document.getElementById('uiCentsMarker');
                const markerLeft = centsMarker ? centsMarker.style.left : '';

                const activeScene = document.querySelector('.scene.active');
                const activeSceneId = activeScene ? activeScene.id : '';

                return {
                    winWidth,
                    winHeight,
                    docWidth,
                    hasHorizOverflow,
                    cardFitsHoriz,
                    meterFits,
                    navFits,
                    activeSceneId,
                    noteText,
                    freqText,
                    centsVal,
                    markerLeft,
                    cardWidth: cardRect ? Math.round(cardRect.width) : 0,
                    cardHeight: cardRect ? Math.round(cardRect.height) : 0,
                    meterWidth: meterRect ? Math.round(meterRect.width) : 0,
                    navWidth: navRect ? Math.round(navRect.width) : 0
                };
            })()
            """
            data = await evaluate_js(ws, check_script, msg_id)
            results.append((name, w, h, data))
            print(f"[{name}] win={data['winWidth']}x{data['winHeight']}, docW={data['docWidth']}, horizOverflow={data['hasHorizOverflow']}, cardFits={data['cardFitsHoriz']} (w={data['cardWidth']}), meterFits={data['meterFits']} (w={data['meterWidth']}), navFits={data['navFits']} (w={data['navWidth']}), note={data['noteText']}, freq={data['freqText']}, cents={data['centsVal']}, marker={data['markerLeft']}")

        ws.close()
        return results

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except:
            proc.kill()

if __name__ == "__main__":
    res = asyncio.run(run_browser_tests())
    if res:
        print("\n=== SUMMARY OF VIEWPORT TESTS ===")
        all_passed = True
        for name, w, h, r in res:
            ok = (not r['hasHorizOverflow']) and r['cardFitsHoriz'] and r['meterFits'] and r['navFits'] and (r['noteText'] != '--')
            if not ok:
                all_passed = False
            status = "PASSED" if ok else "FAILED"
            print(f"{name:26} ({r['winWidth']:4}x{r['winHeight']:4}) -> Overflow={r['hasHorizOverflow']} | CardFits={r['cardFitsHoriz']} | MeterFits={r['meterFits']} | NavFits={r['navFits']} | Note='{r['noteText']}' | Result={status}")
        print(f"\nOverall Responsive Test Result: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
