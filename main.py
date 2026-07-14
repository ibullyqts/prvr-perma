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
MESSAGE_LINE = "Yᴀsʜ - Hᴀʀɪsʜ - Mᴇᴍᴀx Ƭяу мσм кє ѕαтн вєᴅ ᴍᴀỉɴ  ᴍᴀsᴛỉ кᴀяυggᴀ 🌟"

# --- 🛡️ NAME GUARDIAN (Lightweight) ---
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
        await asyncio.sleep(120)

# --- 🔥 STRIKE ENGINE (Lean) ---
async def run_strike(cookie, target_id):
    async with async_playwright() as p:
        # Added --memory-pressure-off to prevent crashes in GitHub Actions
        context = await p.chromium.launch_persistent_context(
            user_data_dir="n_1", headless=True, channel="chrome",
            args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"]
        )
        await Stealth().apply_stealth_async(context)
        
        strike_script = """
            (config) => {
                const msg = config.line;
                const sig = config.sig;
                
                const send = (text) => {
                    const box = document.querySelector('div[role="textbox"]');
                    if (!box) return false;
                    box.innerText = text;
                    box.dispatchEvent(new Event('input', { bubbles: true }));
                    const btn = document.querySelector('div[role="button"][aria-label="Send"]');
                    if (btn) btn.click();
                    return true;
                };

                let count = 0;
                setInterval(() => {
                    if (count < 4) send(Array(4).fill(msg).join("\\n\\n"));
                    else send(sig);
                    count = (count + 1) % 5;
                }, 1500); // Stable 1.5s interval to save RAM
            }
        """
        
        page = await context.new_page()
        # Ensure cookies are added
        sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
        await context.add_cookies([{'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com', 'path': '/'}])
        
        await page.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="domcontentloaded")
        await page.evaluate(strike_script, {"line": MESSAGE_LINE, "sig": SIGNATURE})
        
        # Periodic reload to prevent memory leak
        while True:
            await asyncio.sleep(180) 
            await page.reload()
    
async def main():
    cookie = os.environ.get("INSTA_COOKIE")
    tid = os.environ.get("TARGET_THREAD_ID")
    if cookie and tid:
        await asyncio.gather(run_name_guardian(cookie, tid, SIGNATURE), run_strike(cookie, tid))

if __name__ == "__main__":
    asyncio.run(main())
