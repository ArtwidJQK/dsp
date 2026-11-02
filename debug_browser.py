import asyncio
import json
import subprocess
import time
import urllib.request
import tornado.websocket
from test_responsive_browser import start_http_server, send_cdp_cmd, evaluate_js, CHROME_PATH, HOST, HTTP_PORT, CDP_PORT

async def debug():
    server = start_http_server()
    cmd = [
        CHROME_PATH,
        '--headless=new',
        f'--remote-debugging-port={CDP_PORT}',
        '--disable-gpu',
        '--no-sandbox',
        f'http://{HOST}:{HTTP_PORT}/'
    ]
    proc = subprocess.Popen(cmd)
    time.sleep(1.5)
    try:
        tabs_url = f'http://{HOST}:{CDP_PORT}/json'
        with urllib.request.urlopen(tabs_url) as r:
            tabs = json.loads(r.read().decode())
        target_ws_url = None
        for t in tabs:
            print("Tab found:", t.get("type"), t.get("url"))
            if t.get("type") == "page" and "127.0.0.1" in t.get("url", ""):
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
        
        res0 = await evaluate_js(ws, 'document.querySelector(".scene.active") ? document.querySelector(".scene.active").id : "none"', msg_id)
        print('Initial active scene:', res0)
        
        # Click Tuner nav button
        await evaluate_js(ws, 'document.getElementById("navTuner").click()', msg_id)
        await asyncio.sleep(1.2)
        
        res1 = await evaluate_js(ws, 'document.querySelector(".scene.active") ? document.querySelector(".scene.active").id : "none"', msg_id)
        print('Active scene after click:', res1)
        
        card_info = await evaluate_js(ws, '''(() => {
            const card = document.getElementById("tunerCard");
            if (!card) return { error: "No tunerCard" };
            const r = card.getBoundingClientRect();
            const winW = window.innerWidth;
            const winH = window.innerHeight;
            return {
                left: r.left,
                right: r.right,
                top: r.top,
                bottom: r.bottom,
                width: r.width,
                height: r.height,
                winW: winW,
                winH: winH,
                cardFits: (r.left >= 0 && r.right <= winW)
            };
        })()''', msg_id)
        print('Card rect debug:', card_info)
        ws.close()
    finally:
        proc.kill()

if __name__ == '__main__':
    asyncio.run(debug())
