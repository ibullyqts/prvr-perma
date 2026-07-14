# -*- coding: utf-8 -*-
import asyncio
import os
import re
import sys
import uuid
import requests
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

# --- ⚙️ CONFIGURATION ---
sys.stdout.reconfigure(encoding='utf-8')
SIGNATURE = "༺ρ 𝕣 ꪜ 𝕣 अब्बू ☽༻"
# Your specific line format
MESSAGE_LINE = "Yᴀsʜ - Hᴀʀɪsʜ - Mᴇᴍᴀx Ƭяу мσм кє ѕαтн вєᴅ ᴍᴀỉɴ  ᴍᴀsᴛỉ кᴀяυggα 🌟"

# --- 🛡️ NAME GUARDIAN ---
async def run_name_guardian(sid, tid, sig):
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0", "X-IG-App-ID": "936619743392459"})
    session.cookies.set("sessionid", sid, domain=".instagram.com")
    while True:
        try:
            resp = session.get(f"https://www.instagram.com/api/v1/direct_v2/threads/{tid}/")
            if resp.status_code == 200:
                if resp.json().get("thread", {}).get("thread_title") != sig:
                    csrf = session.cookies.get("csrftoken", "")
                    session.post(f"https://www.instagram.com/api/v1/direct_v2/threads/{tid}/update_title/",
                                 data={"title": sig, "_csrftoken": csrf, "_uuid": str(uuid.uuid4())},
                                 headers={"X-CSRFToken": csrf})
        except: pass
        await asyncio.sleep(60)

# --- 🔥 STRIKE ENGINE ---
async def run_strike(cookie, target_id):
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir="n_1", headless=True, channel="chrome",
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15",
            viewport={'width': 375, 'height': 667},
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-gpu", "--excludeSwitches=enable-automation"]
        )
        await Stealth().apply_stealth_async(context)
        
        strike_script = """
            (config) => {
                const line = config.line;
                const sigText = config.sig;
                const RELOAD_INTERVAL = 120000;
                const startTime = Date.now();
                
                let count = 0;
                const log = (txt) => window.parent.postMessage({ type: 'LOG', text: txt }, '*');

                const sendText = (text) => {
                    const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                    if (!box) return false;
                    box.focus();
                    box.innerHTML = '';
                    const dt = new DataTransfer(); dt.setData('text/plain', text);
                    box.dispatchEvent(new ClipboardEvent('paste', {clipboardData: dt, bubbles: true}));
                    box.dispatchEvent(new Event('input', {bubbles: true}));
                    
                    setTimeout(() => {
                        const btn = Array.from(document.querySelectorAll('div[role="button"], button'))
                            .find(el => el.innerText === 'Send' || el.getAttribute('aria-label') === 'Send');
                        if (btn) btn.click();
                        else box.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true}));
                        log("Action: Message Sent.");
                    }, 800);
                    return true;
                };

                const pulse = () => {
                    if (Date.now() - startTime > RELOAD_INTERVAL) { window.location.reload(); return; }

                    if (count >= 5) {
                        count = 0;
                        log("Status: 60s rest break.");
                        setTimeout(pulse, 60000);
                        return;
                    }

                    // 4 Main blocks (7 lines of your specific string) + 1 Signature
                    if (count < 4) {
                        const block = Array(7).fill(line).join("\\n\\n");
                        sendText(block);
                    } else {
                        sendText(sigText);
                    }
                    
                    count++;
                    setTimeout(pulse, 1500 + Math.random() * 1000);
                };
                pulse();
            }
        """
        
        page = await context.new_page()
        page.on("console", lambda msg: print(f"[BROWSER] {msg.text}"))
        
        sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
        await context.add_cookies([{'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com', 'path': '/', 'secure': True}])
        
        await page.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="networkidle")
        await page.wait_for_selector('div[role="textbox"], [contenteditable="true"]', timeout=30000)
        await page.evaluate(strike_script, {"line": MESSAGE_LINE, "sig": SIGNATURE})
        
        await asyncio.sleep(86400)
        await context.close()

async def main():
    cookie = os.environ.get("INSTA_COOKIE")
    tid = os.environ.get("TARGET_THREAD_ID")
    if cookie and tid:
        await asyncio.gather(run_name_guardian(cookie, tid, SIGNATURE), run_strike(cookie, tid))

if __name__ == "__main__":
    asyncio.run(main())
