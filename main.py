# -*- coding: utf-8 -*-
import asyncio
import os
import re
import sys
import uuid
import time
import requests
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from pyvirtualdisplay import Display

# --- ⚙️ CONFIGURATION ---
sys.stdout.reconfigure(encoding='utf-8')
SIGNATURE = "༺ρ 𝕣 ꪜ 𝕣 अब्बू ☽༻"
MESSAGE_LINE = "Yᴀsʜ - Hᴀʀɪsʜ - Mᴇᴍᴀx Ƭяу мσм кє ѕαтн вєᴅ ᴍᴀỉɴ  ᴍᴀsᴛỉ кᴀяυggᴀ 🌟"

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

# --- 🔥 STRIKE ENGINE (Shield-Bypass) ---
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
        
        try:
            await page.wait_for_selector(textbox_selector, timeout=30000)
            print("[BOT] Chat loaded successfully.")
        except Exception as e:
            print("[CRITICAL] Failed to find chat box.")
            return

        count = 0
        message_block = "\n\n".join([MESSAGE_LINE] * 7)
        last_reload_time = time.time()
        
        # --- THE NATIVE LOOP (Shield-Bypass) ---
        while True:
            try:
                # 2-Minute Forced Reload
                if time.time() - last_reload_time > 120:
                    print("[BOT] 2 Minutes elapsed. Reloading...")
                    await page.reload(wait_until="networkidle")
                    await page.wait_for_selector(textbox_selector, timeout=30000)
                    last_reload_time = time.time()

                # 60s Rest Break after 5 messages (4+1 cycle)
                if count >= 5:
                    print("[BOT] Cycle complete. 60s rest break...")
                    await asyncio.sleep(60)
                    count = 0
                    continue

                text_to_send = message_block if count < 4 else SIGNATURE
                
                # BYPASS SHIELD: Focus then inject text directly via keyboard
                await page.focus(textbox_selector)
                await page.keyboard.insert_text(text_to_send)
                await asyncio.sleep(0.5) 
                await page.keyboard.press("Enter")
                
                print(f"[BOT] Message {count+1}/5 sent successfully.")
                count += 1
                await asyncio.sleep(1.5) 
                
            except Exception as e:
                print(f"[WARNING] UI interrupted, refreshing... Error: {e}")
                await page.reload(wait_until="networkidle")
                await page.wait_for_selector(textbox_selector, timeout=30000)
                last_reload_time = time.time()

async def main():
    cookie = os.environ.get("INSTA_COOKIE")
    tid = os.environ.get("TARGET_THREAD_ID")
    
    if cookie and tid:
        print("[SYSTEM] Booting Virtual Display...")
        display = Display(visible=0, size=(1920, 1080))
        display.start()
        
        try:
            await asyncio.gather(
                run_name_guardian(cookie, tid, SIGNATURE), 
                run_strike(cookie, tid)
            )
        finally:
            print("[SYSTEM] Shutting down Virtual Display...")
            display.stop()

if __name__ == "__main__":
    asyncio.run(main())
