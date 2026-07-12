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
MESSAGE_TEXT = "AARAV Ƭяу мσм кє ѕαтн вєᴅ ᴍᴀỉɴ  ᴍᴀsᴛỉ кᴀяυggα"

async def run_guardian(cookie, target_id):
    """Monitors and secures the thread name."""
    sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0", "X-IG-App-ID": "936619743392459"})
    session.cookies.set("sessionid", sid, domain=".instagram.com")
    while True:
        try:
            resp = session.get(f"https://www.instagram.com/api/v1/direct_v2/threads/{target_id}/")
            if resp.status_code == 200:
                current_name = resp.json().get("thread", {}).get("thread_title", "")
                if current_name != SIGNATURE:
                    csrf = session.cookies.get("csrftoken", "")
                    session.post(f"https://www.instagram.com/api/v1/direct_v2/threads/{target_id}/update_title/",
                                 data={"title": SIGNATURE, "_csrftoken": csrf, "_uuid": str(uuid.uuid4())},
                                 headers={"X-CSRFToken": csrf})
        except: pass
        await asyncio.sleep(300) # Guardian check every 5 mins

async def run_strike(cookie, target_id):
    """Striker using your preferred high-performance paste logic."""
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir="n_1", headless=True,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15",
            viewport={'width': 375, 'height': 667},
            args=["--no-sandbox", "--disable-gpu"]
        )
        await Stealth().apply_stealth_async(context)
        sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
        await context.add_cookies([{'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com', 'path': '/', 'secure': True}])

        strike_script = """
            (msg) => {
                const sleepEmojis = ["🛌", "💤", "🥱", "🛌"];
                let count = 0;
                
                const pulse = () => {
                    const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                    if (box) {
                        const emoji = sleepEmojis[count % sleepEmojis.length];
                        const line = msg + "  " + emoji;
                        const finalBlock = line + "\\n".repeat(2) + line + "\\n".repeat(4) + line + "\\n".repeat(2) + line;
                        
                        const dt = new DataTransfer();
                        dt.setData('text/plain', finalBlock);
                        const paste = new ClipboardEvent('paste', {clipboardData: dt, bubbles: true});
                        box.focus(); box.dispatchEvent(paste); box.dispatchEvent(new Event('input', {bubbles: true}));
                        
                        setTimeout(() => {
                            const btn = Array.from(document.querySelectorAll('div[role="button"], button')).find(el => 
                                el.innerText === 'Send' || el.getAttribute('aria-label') === 'Send');
                            if (btn) btn.click();
                        }, 500);
                        count++;
                    }
                    setTimeout(pulse, 5000 + Math.random() * 2000);
                }
                pulse();
            }
        """
        page = await context.new_page()
        await page.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="networkidle")
        await page.evaluate(strike_script, MESSAGE_TEXT)
        await asyncio.sleep(21000)
        await context.close()

async def main():
    cookie = os.environ.get("INSTA_COOKIE")
    tid = os.environ.get("TARGET_THREAD_ID")
    await asyncio.gather(run_guardian(cookie, tid), run_strike(cookie, tid))

if __name__ == "__main__":
    asyncio.run(main())
