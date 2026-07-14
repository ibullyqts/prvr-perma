# -*- coding: utf-8 -*-
import asyncio
import os
import re
import sys
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

# --- ⚙️ CONFIGURATION ---
sys.stdout.reconfigure(encoding='utf-8')
SIGNATURE = "༺ρ 𝕣 ꪜ 𝕣 अब्बू ☽༻"
MESSAGE_BASE = "Yᴀsʜ - Hᴀʀɪsʜ - Mᴇᴍᴀx Ƭяу мσм кє ѕαтн вєᴅ ᴍᴀỉɴ  ᴍᴀsᴛỉ кᴀяυggα"

async def run_strike(cookie, target_id):
    async with async_playwright() as p:
        # 1. HARDENED CONTEXT: Uses Chrome channel and suppresses automation flags
        context = await p.chromium.launch_persistent_context(
            user_data_dir="n_1", 
            headless=True,
            channel="chrome", 
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15",
            viewport={'width': 375, 'height': 667},
            ignore_default_args=["--enable-automation"],
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-gpu",
                "--excludeSwitches=enable-automation"
            ]
        )
        
        # 2. STEALTH LAYER
        await Stealth().apply_stealth_async(context)

        # 3. DEEP HARDWARE MOCKING INJECTION
        stealth_js = """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            
            const getParameter = WebGLRenderingContext.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) return 'Apple Inc.';
                if (parameter === 37446) return 'Apple GPU';
                return getParameter(parameter);
            };
        """
        await context.add_init_script(stealth_js)

        sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
        await context.add_cookies([{'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com', 'path': '/', 'secure': True}])

        strike_script = """
            (config) => {
                const msgText = config.msg;
                const sigText = config.sig;
                
                const baseEmojis = ["🛌", "💤", "🥱", "🔥", "✨", "💫", "🌟", "🌙"];
                let emojiPool = [];
                let messageSequenceCount = 0;
                const log = (txt) => window.parent.postMessage({ type: 'LOG', text: txt }, '*');

                const getUniqueEmoji = () => {
                    if (emojiPool.length === 0) emojiPool = [...baseEmojis];
                    return emojiPool.splice(Math.floor(Math.random() * emojiPool.length), 1)[0];
                };

                const sendText = (text) => {
                    const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                    if (box) {
                        box.innerHTML = '';
                        const dt = new DataTransfer(); dt.setData('text/plain', text);
                        const paste = new ClipboardEvent('paste', {clipboardData: dt, bubbles: true});
                        box.focus(); box.dispatchEvent(paste); box.dispatchEvent(new Event('input', {bubbles: true}));
                        
                        setTimeout(() => {
                            const btn = Array.from(document.querySelectorAll('div[role="button"], button'))
                                .find(el => el.innerText === 'Send' || el.getAttribute('aria-label') === 'Send');
                            if (btn) { btn.click(); log("Action: Sent input string."); }
                            else { box.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true})); log("Action: Dispatched Enter fallback."); }
                        }, 600);
                    }
                };

                const humanActions = [
                    () => { log("Behavior: Skimming downward..."); window.scrollBy({ top: Math.floor(Math.random() * 140) + 40, behavior: 'smooth' }); },
                    () => { log("Behavior: Looking back at earlier text..."); window.scrollBy({ top: -Math.floor(Math.random() * 80), behavior: 'smooth' }); },
                    () => { log("Behavior: Simulating screen interaction..."); const ev = new MouseEvent('mousemove', { clientX: Math.floor(Math.random() * window.innerWidth), clientY: Math.floor(Math.random() * window.innerHeight), bubbles: true }); document.dispatchEvent(ev); }
                ];

                const runLoop = () => {
                    if (messageSequenceCount >= 4) {
                        log("⚠️ Anti-429 Cooldown: Entering extended structural rest break...");
                        messageSequenceCount = 0;
                        humanActions[Math.floor(Math.random() * humanActions.length)]();
                        setTimeout(runLoop, 45000 + Math.random() * 25000);
                        return;
                    }

                    const roll = Math.random();
                    if (roll < 0.60) {
                        const messageEmoji = getUniqueEmoji();
                        let lines = [];
                        for(let i = 0; i < 7; i++) { lines.push(msgText + " " + messageEmoji); }
                        const finalBlock = lines.join("\\n".repeat(2));
                        log("Action: Transmitting primary content block...");
                        sendText(finalBlock);
                        messageSequenceCount++;
                        setTimeout(runLoop, 12000 + Math.random() * 10000);
                    } else if (roll >= 0.60 && roll < 0.85) {
                        humanActions[Math.floor(Math.random() * humanActions.length)]();
                        setTimeout(runLoop, 4000 + Math.random() * 4000);
                    } else {
                        log("Action: Deploying identity signature verify token...");
                        sendText(sigText);
                        messageSequenceCount++;
                        setTimeout(runLoop, 15000 + Math.random() * 10000);
                    }
                };
                runLoop();
            }
        """
        page = await context.new_page()
        page.on("console", lambda msg: print(f"[BROWSER] {msg.text}"))
        page.on("framenavigated", lambda f: f.evaluate("window.addEventListener('message', e => { if(e.data.type==='LOG') console.log(e.data.text); })"))
        
        print("[STRIKER] Opening direct thread page...")
        await page.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="commit")
        await page.wait_for_selector('div[role="textbox"], [contenteditable="true"]', timeout=30000)
        await page.evaluate(strike_script, {"msg": MESSAGE_BASE, "sig": SIGNATURE})
        
        await asyncio.sleep(45000)
        await context.close()

async def main():
    cookie = os.environ.get("INSTA_COOKIE")
    tid = os.environ.get("TARGET_THREAD_ID")
    if cookie and tid:
        await run_strike(cookie, tid)

if __name__ == "__main__":
    asyncio.run(main())
