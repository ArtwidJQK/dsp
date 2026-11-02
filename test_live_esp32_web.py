import os
import sys
import time
import json
import asyncio
import subprocess
import urllib.request
import tornado.websocket

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ESP32_HOST = "192.168.1.238"
CDP_PORT = 9226

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

async def test_live_esp32_responsive():
    esp32_url = f"http://{ESP32_HOST}/"
    print(f"Connecting headless Chrome to real ESP32-S3 at {esp32_url}...")
    
    cmd = [
        CHROME_PATH,
        "--headless=new",
        f"--remote-debugging-port={CDP_PORT}",
        "--disable-gpu",
        "--no-sandbox",
        "--mute-audio",
        esp32_url
    ]
    proc = subprocess.Popen(cmd)
    time.sleep(2.0)
    
    try:
        tabs_url = f"http://127.0.0.1:{CDP_PORT}/json"
        with urllib.request.urlopen(tabs_url) as resp:
            tabs = json.loads(resp.read().decode())
            
        target_ws_url = None
        for t in tabs:
            if t.get("type") == "page" and ESP32_HOST in t.get("url", ""):
                target_ws_url = t["webSocketDebuggerUrl"]
                break
        if not target_ws_url:
            for t in tabs:
                if t.get("type") == "page":
                    target_ws_url = t["webSocketDebuggerUrl"]
                    break
                    
        ws = await tornado.websocket.websocket_connect(target_ws_url)
        msg_id = [1]
        await send_cdp_cmd(ws, "Page.enable", {}, msg_id)
        await asyncio.sleep(1.0)
        
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
            await send_cdp_cmd(ws, "Emulation.setDeviceMetricsOverride", {
                "width": w,
                "height": h,
                "deviceScaleFactor": 2 if is_mobile else 1,
                "mobile": is_mobile
            }, msg_id)
            await asyncio.sleep(0.3)
            
            await evaluate_js(ws, "document.getElementById('navTuner').click()", msg_id)
            await asyncio.sleep(1.0)
            
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

                const statusText = document.getElementById('uiStatusText');
                const statusStr = statusText ? statusText.textContent : '';

                return {
                    winWidth,
                    winHeight,
                    docWidth,
                    hasHorizOverflow,
                    cardFitsHoriz,
                    meterFits,
                    navFits,
                    statusStr,
                    cardWidth: cardRect ? Math.round(cardRect.width) : 0,
                    meterWidth: meterRect ? Math.round(meterRect.width) : 0,
                    navWidth: navRect ? Math.round(navRect.width) : 0
                };
            })()
            """
            d = await evaluate_js(ws, check_script, msg_id)
            results.append((name, w, h, d))
            print(f"[{name}] win={d['winWidth']}x{d['winHeight']} | docW={d['docWidth']} | Overflow={d['hasHorizOverflow']} | CardFits={d['cardFitsHoriz']} (w={d['cardWidth']}) | MeterFits={d['meterFits']} | NavFits={d['navFits']} | Status='{d['statusStr']}'")
            
        ws.close()
        return results
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    res = asyncio.run(test_live_esp32_responsive())
    print("\n=== SUMMARY OF LIVE ESP32 WEB TESTING ===")
    all_ok = True
    for name, w, h, r in res:
        ok = (not r['hasHorizOverflow']) and r['cardFitsHoriz'] and r['meterFits'] and r['navFits']
        if not ok: all_ok = False
        print(f"{name:26} ({r['winWidth']:4}x{r['winHeight']:4}) -> Overflow={r['hasHorizOverflow']} | CardFits={r['cardFitsHoriz']} | Result={'PASSED' if ok else 'FAILED'}")
    print(f"Overall Result: {'ALL PASSED' if all_ok else 'SOME FAILED'}")
