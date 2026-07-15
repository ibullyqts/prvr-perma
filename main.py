# -*- coding: utf-8 -*-
import asyncio
import os
import re
import random
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from pyvirtualdisplay import Display

# --- ⚙️ CONFIGURATION ---
SIGNATURE = "༺ρ 𝕣 ꪜ 𝕣 अब्बू ☽༻"
BASE_TEXT = "Yᴀsʜ - Hᴀʀɪsʜ - Mᴇᴍᴀx Ƭяу мσм кє ѕαтн вєᴅ ᴍᴀỉɴ  ᴍᴀsᴛỉ кᴀяυggᴀ"
EMOJIS = ["🔥", "🌟", "✨", "💫", "🚀", "💎", "🌙", "🧿", "🍃", "🦋"]
MACHINE_ID = os.environ.get("MACHINE_ID", "1")

# --- 🔥 STRIKE ENGINE (Bypass Interceptors) ---
async def run_strike(cookie, target_id):
    while True:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=False, 
                    args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-blink-features=AutomationControlled"]
                )
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
                )
                page = await context.new_page()
                await Stealth().apply_stealth_async(page)
                
                sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
                await context.add_cookies([{'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com', 'path': '/'}])
                
                print(f"[M{MACHINE_ID}] Engine starting...")
                await page.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="domcontentloaded")
                
                # JavaScript to bypass DOM overlays
                textbox_js = "document.querySelector('div[role=\"textbox\"][contenteditable=\"true\"]')"
                
                while True:
                    # Ensure textbox exists
                    is_ready = await page.evaluate(f"{textbox_js} !== null")
                    if not is_ready:
                        await asyncio.sleep(2)
                        continue

                    for i in range(11):
                        text = ("\n\n".join([f"{BASE_TEXT} {random.choice(EMOJIS)}"] * 7)) if i < 10 else SIGNATURE
                        
                        # Use raw JS to clear and focus, bypassing Playwright click/pointer constraints
                        await page.evaluate(f"""
                            const el = {textbox_js};
                            el.focus();
                            el.innerHTML = '';
                        """)
                        
                        # Use keyboard typing to simulate human input
                        await page.keyboard.type(text, delay=random.uniform(50, 100))
                        await asyncio.sleep(0.5)
                        await page.keyboard.press("Enter")
                        
                        print(f"[M{MACHINE_ID}] Block {i+1}/11 sent.")
                        await asyncio.sleep(random.uniform(7.0, 11.0))
        
        except Exception as e:
            print(f"[CRITICAL] {e}. Relaunching in 10s...")
            await asyncio.sleep(10)

# --- 🚀 MAIN ---
async def main():
    cookie = os.environ.get("INSTA_COOKIE")
    tid = os.environ.get("TARGET_THREAD_ID")
    
    if not cookie or not tid:
        print("[ERROR] Credentials missing.")
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
