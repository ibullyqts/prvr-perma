# -*- coding: utf-8 -*-
import asyncio
import os
import re
import uuid
import random
import requests
from playwright.async_api import async_playwright, Error as PlaywrightError
from playwright_stealth import Stealth
from pyvirtualdisplay import Display

# --- ⚙️ CONFIGURATION ---
SIGNATURE = "༺ρ 𝕣 ꪜ 𝕣 अब्बू ☽༻"
BASE_TEXT = "Yᴀsʜ - Hᴀʀɪsʜ - Mᴇᴍᴀx Ƭяу мσм кє ѕαтн вєᴅ ᴍᴀỉɴ  ᴍᴀsᴛỉ кᴀяυggᴀ"
EMOJIS = ["🔥", "🌟", "✨", "💫", "🚀", "💎", "🌙", "🧿", "🍃", "🦋"]

# --- 🔥 STRIKE ENGINE (HARDENED) ---
async def run_strike(cookie, target_id):
    async with async_playwright() as p:
        # Launch with persistent context to maintain session
        context = await p.chromium.launch_persistent_context(
            user_data_dir="n_1", 
            headless=False, 
            channel="chrome",
            args=[
                "--no-sandbox", 
                "--disable-gpu", 
                "--disable-dev-shm-usage", 
                "--disable-blink-features=AutomationControlled"
            ]
        )
        await Stealth().apply_stealth_async(context)
        
        # Helper to maintain an active page reference
        async def get_active_page():
            if not context.pages:
                return await context.new_page()
            return context.pages[0]

        # Inject session
        sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
        await context.add_cookies([{'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com', 'path': '/'}])

        while True:
            try:
                page = await get_active_page()
                await page.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="domcontentloaded")
                
                # Use locator for better stability than selectors
                textbox = page.locator('div[role="textbox"][contenteditable="true"]')
                await textbox.wait_for(timeout=30000)

                for i in range(11):
                    # Prepare content
                    text = ("\n\n".join([f"{BASE_TEXT} {random.choice(EMOJIS)}"] * 7)) if i < 10 else SIGNATURE
                    
                    # Ensure textbox is focused and clear
                    await textbox.click()
                    await page.keyboard.press("Control+A")
                    await page.keyboard.press("Backspace")
                    
                    # Emulate Human Typing
                    await textbox.type(text, delay=random.uniform(70, 150))
                    await asyncio.sleep(1.2)
                    
                    # Attempt to press Enter
                    await page.keyboard.press("Enter")
                    
                    print(f"[BOT] Block {i+1}/11 sent.")
                    await asyncio.sleep(random.uniform(6.0, 10.0))

            except PlaywrightError as e:
                print(f"[ERROR] Browser/Page issue: {e}. Recovering...")
                await asyncio.sleep(5)
                # Cleanup dead pages
                for page in context.pages:
                    try: await page.close()
                    except: pass
            except Exception as e:
                print(f"[ERROR] General failure: {e}. Retrying...")
                await asyncio.sleep(5)

# --- 🚀 MAIN ---
async def main():
    cookie = os.environ.get("INSTA_COOKIE")
    tid = os.environ.get("TARGET_THREAD_ID")
    
    if not cookie or not tid:
        print("[ERROR] Missing INSTA_COOKIE or TARGET_THREAD_ID")
        return

    display = Display(visible=0, size=(1920, 1080))
    display.start()
    try:
        await run_strike(cookie, tid)
    finally:
        display.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
