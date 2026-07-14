# -*- coding: utf-8 -*-
import asyncio
import os
import re
import sys
import uuid
import time
import random
import requests
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from pyvirtualdisplay import Display

# --- ⚙️ CONFIGURATION ---
sys.stdout.reconfigure(encoding='utf-8')
SIGNATURE = "༺ρ 𝕣 ꪜ 𝕣 अब्बू ☽༻"
# Base message text
BASE_TEXT = "Yᴀsʜ - Hᴀʀɪsʜ - Mᴇᴍᴀx Ƭяу мσм кє ѕαтн вєᴅ ᴍᴀỉɴ  ᴍᴀsᴛỉ кᴀяυggᴀ"
EMOJIS = ["🔥", "🌟", "✨", "💫", "🚀", "💎", "🌙", "🧿", "🍃", "🦋"]

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
            user_data_dir="n_1", 
            headless=False, 
            channel="chrome",
            args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage", "--mute-audio"]
        )
        await Stealth().apply_stealth_async(context)
        page = await context.new_page()
        
        sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
        await context.add_cookies([{'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com', 'path': '/'}])
        
        print("[BOT] Navigating to Instagram...")
        await page.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="networkidle")
        
        textbox_selector = 'div[role="textbox"][contenteditable="true"]'
        await page.wait_for_selector(textbox_selector, timeout=30000)

        while True:
            try:
                print("[BOT] 10s cycle reached. Reloading for WebSocket health...")
                await page.reload(wait_until="networkidle")
                await page.wait_for_selector(textbox_selector, timeout=30000)
                
                # Send 10 blocks + 1 signature
                for i in range(11):
                    if i < 10:
                        # Select a random emoji for this specific block
                        current_emoji = random.choice(EMOJIS)
                        # Build a line containing the text and the emoji
                        single_line = f"{BASE_TEXT} {current_emoji}"
                        # Multiply it into a 7-line block structure
                        text_to_send = "\n\n".join([single_line] * 7)
                    else:
                        text_to_send = SIGNATURE
                    
                    await page.focus(textbox_selector)
                    await page.keyboard.insert_text(text_to_send)
                    await asyncio.sleep(0.2) 
                    await page.keyboard.press("Enter")
                    
                    print(f"[BOT] Message block {i+1}/11 sent.")
                    await asyncio.sleep(random.uniform(0.5, 0.8)) 
                
            except Exception as e:
                print(f"[WARNING] Error: {e}. Resetting...")
                await page.reload(wait_until="networkidle")
                await asyncio.sleep(5)

async def main():
    cookie = os.environ.get("INSTA_COOKIE")
    tid = os.environ.get("TARGET_THREAD_ID")
    
    if cookie and tid:
        print("[SYSTEM] Booting Virtual Display...")
        display = Display(visible=0, size=(1920, 1080))
        display.start()
        try:
            await asyncio.gather(run_name_guardian(cookie, tid, SIGNATURE), run_strike(cookie, tid))
        finally:
            display.stop()

if __name__ == "__main__":
    asyncio.run(main())
