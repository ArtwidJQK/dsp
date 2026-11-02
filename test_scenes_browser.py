import asyncio
import json
import subprocess
import time
import urllib.request
import tornado.websocket
from test_responsive_browser import start_http_server, send_cdp_cmd, evaluate_js, CHROME_PATH, HOST, HTTP_PORT, CDP_PORT

async def test_scenes():
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
        target_ws_url = [t['webSocketDebuggerUrl'] for t in tabs if t.get('type') == 'page' and '127.0.0.1' in t.get('url', '')][0]
        ws = await tornado.websocket.websocket_connect(target_ws_url)
        msg_id = [1]
        await send_cdp_cmd(ws, 'Page.enable', {}, msg_id)
        await asyncio.sleep(0.5)

        # 1. Start from cover
        s1 = await evaluate_js(ws, 'document.querySelector(".scene.active").id', msg_id)
        print('Initial Scene:', s1)

        # 2. Click start button
        await evaluate_js(ws, 'document.getElementById("btnStartTuner").click()', msg_id)
        await asyncio.sleep(1.0)
        s2 = await evaluate_js(ws, 'document.querySelector(".scene.active").id', msg_id)
        print('Scene after clicking btnStartTuner:', s2)

        # 3. Click navInfo
        await evaluate_js(ws, 'document.getElementById("navInfo").click()', msg_id)
        await asyncio.sleep(1.0)
        s3 = await evaluate_js(ws, 'document.querySelector(".scene.active").id', msg_id)
        print('Scene after clicking navInfo:', s3)

        # 4. Click btnBackToTuner
        await evaluate_js(ws, 'document.getElementById("btnBackToTuner").click()', msg_id)
        await asyncio.sleep(1.0)
        s4 = await evaluate_js(ws, 'document.querySelector(".scene.active").id', msg_id)
        print('Scene after clicking btnBackToTuner:', s4)

        # 5. Click navCover
        await evaluate_js(ws, 'document.getElementById("navCover").click()', msg_id)
        await asyncio.sleep(1.0)
        s5 = await evaluate_js(ws, 'document.querySelector(".scene.active").id', msg_id)
        print('Scene after clicking navCover:', s5)

        # Check console errors
        has_errors = await evaluate_js(ws, 'window.__hasErrors || false', msg_id)
        print('Console errors:', has_errors)

        all_ok = (s1 == 'scene-cover') and (s2 == 'scene-tuner') and (s3 == 'scene-info') and (s4 == 'scene-tuner') and (s5 == 'scene-cover')
        print(f"Scene Transition Verification: {'SUCCESS' if all_ok else 'FAILED'}")
        ws.close()
    finally:
        proc.kill()

if __name__ == '__main__':
    asyncio.run(test_scenes())
