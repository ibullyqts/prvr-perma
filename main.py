# -*- coding: utf-8 -*-
import asyncio
import os
import re
import sys
import uuid
import random
import time
import requests
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

# --- ⚙️ CONFIGURATION ---
sys.stdout.reconfigure(encoding='utf-8')
SIGNATURE = "༺ρ 𝕣 ꪜ 𝕣 अब्बू ☽༻"

async def run_guardian(cookie, target_id):
    """Monitors the group chat name and keeps it locked to the signature."""
    sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0", "X-IG-App-ID": "936619743392459"})
    session.cookies.set("sessionid", sid, domain=".instagram.com")
    
    last_update_time = 0
    print("[GUARD] Guardian service started.")
    
    while True:
        try:
            resp = session.get(f"https://www.instagram.com/api/v1/direct_v2/threads/{target_id}/")
            if resp.status_code == 200:
                data = resp.json().get("thread", {})
                current_name = data.get("thread_title", "")
                
                # Check and update title randomly between 30 to 60 minutes if changed
                if current_name != SIGNATURE and (time.time() - last_update_time) > random.randint(1800, 3600):
                    csrf = session.cookies.get("csrftoken", "")
                    session.post(
                        f"https://www.instagram.com/api/v1/direct_v2/threads/{target_id}/update_title/",
                        data={"title": SIGNATURE, "_csrftoken": csrf, "_uuid": str(uuid.uuid4())},
                        headers={"X-CSRFToken": csrf}
                    )
                    last_update_time = time.time()
                    print(f"[GUARD] 🚨 Name breach detected! Reverted to: {SIGNATURE}")
        except Exception as e:
            print(f"[GUARD] Error: {e}")
        await asyncio.sleep(60)

async def run_strike(cookie, target_id):
    """Runs the single-tab messaging pulse with human-like active resting loops."""
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir="n_1", headless=True,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15",
            viewport={'width': 375, 'height': 667}
        )
        await Stealth().apply_stealth_async(context)
        sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
        await context.add_cookies([{'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com', 'path': '/', 'secure': True}])

        strike_script = """
            (signature) => {
                let messageCount = 0;
                const sleepEmojis = ["🛌", "💤", "🥱", "🛌"];

                const log = (msg) => window.parent.postMessage({ type: 'LOG', text: msg }, '*');

                const sendText = (text) => {
                    const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                    if (box) {
                        const dataTransfer = new DataTransfer();
                        dataTransfer.setData('text/plain', text);
                        const pasteEvent = new ClipboardEvent('paste', { clipboardData: dataTransfer, bubbles: true, cancelable: true });
                        box.focus(); box.dispatchEvent(pasteEvent); box.dispatchEvent(new Event('input', { bubbles: true }));
                        setTimeout(() => {
                            const btn = Array.from(document.querySelectorAll('div[role="button"], button')).find(el => el.innerText === 'Send');
                            if (btn) btn.click();
                        }, 500);
                    }
                };

                const pulse = () => {
                    // REST SESSION: After 5 messages, send signature then browse naturally
                    if (messageCount > 0 && messageCount % 5 === 0) {
                        log("Action: Sending Signature...");
                        sendText(signature);
                        log("Status: Resting and Browsing...");
                        const end = Date.now() + 8000;
                        const rest = () => {
                            if (Date.now() < end) { window.scrollBy(0, 200); setTimeout(rest, 1000); }
                            else { messageCount = 0; pulse(); }
                        };
                        rest(); return;
                    }

                    const emoji = sleepEmojis[messageCount % sleepEmojis.length];
                    const line = "AARAV Ƭяу мσм кє ѕαтн вєᴅ ᴍᴀỉɴ  ᴍᴀsᴛỉ кᴀяυggα  " + emoji;
                    
                    // Layout: Line 1 -> [2 lines gap] -> Line 2 -> [4 lines gap] -> Line 3 -> [2 lines gap] -> Line 4
                    const finalBlock = line + "\\n".repeat(2) + line + "\\n".repeat(4) + line + "\\n".repeat(2) + line;
                    
                    log("Action: Sending Message " + (messageCount + 1) + "/5...");
                    sendText(finalBlock);
                    
                    messageCount++;
                    setTimeout(pulse, Math.floor(Math.random() * 4000) + 1000);
                }
                pulse();
            }
        """

        page = await context.new_page()
        page.on("console", lambda msg: print(f"[BROWSER] {msg.text}"))
        page.on("framenavigated", lambda f: f.evaluate("window.addEventListener('message', e => { if(e.data.type==='LOG') console.log(e.data.text); })"))
        
        await page.goto(f"https://www.instagram.com/direct/t/{target_id}/")
        await page.evaluate(strike_script, SIGNATURE)
        
        await asyncio.sleep(21000) # Keep session execution path active
        await context.close()

async def main():
    cookie = os.environ.get("INSTA_COOKIE")
    tid = os.environ.get("TARGET_THREAD_ID")
    if cookie and tid:
        await asyncio.gather(run_guardian(cookie, tid), run_strike(cookie, tid))

if __name__ == "__main__":
    asyncio.run(main())
