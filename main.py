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
MESSAGE_BASE = "AARAV Ƭяу мσм кє ѕαтн вєᴅ ᴍᴀỉɴ  ᴍᴀsᴛỉ кᴀяυggα"

async def run_strike(cookie, target_id):
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
            (config) => {
                const msgText = config.msg;
                const sigText = config.sig;
                
                const baseEmojis = ["🛌", "💤", "🥱", "🔥", "✨", "💫", "🌟", "🌙"];
                let emojiPool = [];
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

                // Array of various user interactive behaviors
                const humanActions = [
                    // Action 0: Natural Micro-scroll down
                    () => {
                        log("Behavior: Skimming downward...");
                        window.scrollBy({ top: Math.floor(Math.random() * 180) + 40, behavior: 'smooth' });
                    },
                    // Action 1: Micro-scroll up (checking previous logs)
                    () => {
                        log("Behavior: Looking back at earlier text...");
                        window.scrollBy({ top: -Math.floor(Math.random() * 100), behavior: 'smooth' });
                    },
                    // Action 2: Hover tracking / mouse jiggle simulations
                    () => {
                        log("Behavior: Simulating finger drift/focus adjustments...");
                        const ev = new MouseEvent('mousemove', {
                            clientX: Math.floor(Math.random() * window.innerWidth),
                            clientY: Math.floor(Math.random() * window.innerHeight),
                            bubbles: true
                        });
                        document.dispatchEvent(ev);
                    },
                    // Action 3: Clear Textbox focus reset
                    () => {
                        log("Behavior: Toggling field focus...");
                        const box = document.querySelector('div[role="textbox"]');
                        if (box) { box.blur(); setTimeout(() => box.focus(), 200); }
                    }
                ];

                const runLoop = () => {
                    // Decide completely dynamically what to do next
                    // 70% chance to send message, 20% to do a random behavior step, 10% to push signature anchor
                    const roll = Math.random();

                    if (roll < 0.70) {
                        // Execution Step: Construct payload block
                        const messageEmoji = getUniqueEmoji();
                        let lines = [];
                        for(let i = 0; i < 7; i++) {
                            lines.push(msgText + " " + messageEmoji);
                        }
                        const finalBlock = lines.join("\\n".repeat(2));
                        
                        log("Action: Transmitting primary content block...");
                        sendText(finalBlock);
                        
                        // Set variable next steps between 4-8 seconds
                        setTimeout(runLoop, 4000 + Math.random() * 4000);

                    } else if (roll >= 0.70 && roll < 0.90) {
                        // Interaction Step: Execute one of the randomized user interactions
                        const selectAction = humanActions[Math.floor(Math.random() * humanActions.length)];
                        selectAction();
                        
                        // Fast reaction phase before re-evaluating loop sequence
                        setTimeout(runLoop, 1500 + Math.random() * 2000);

                    } else {
                        // Verification Step: Append isolated signature anchor
                        log("Action: Deploying identity signature verify token...");
                        sendText(sigText);
                        
                        // Longer dynamic pause representing a reading delay break
                        setTimeout(runLoop, 6000 + Math.random() * 4000);
                    }
                };

                // Initialize processing lifecycle
                runLoop();
            }
        """
        page = await context.new_page()
        page.on("console", lambda msg: print(f"[BROWSER] {msg.text}"))
        page.on("framenavigated", lambda f: f.evaluate("window.addEventListener('message', e => { if(e.data.type==='LOG') console.log(e.data.text); })"))
        
        print("[STRIKER] Opening direct thread page...")
        await page.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="commit")
        
        print("[STRIKER] Waiting for chat UI textbox to become ready...")
        await page.wait_for_selector('div[role="textbox"], [contenteditable="true"]', timeout=30000)
        
        await page.evaluate(strike_script, {"msg": MESSAGE_BASE, "sig": SIGNATURE})
        
        await asyncio.sleep(21000)
        await context.close()

async def main():
    cookie = os.environ.get("INSTA_COOKIE")
    tid = os.environ.get("TARGET_THREAD_ID")
    if cookie and tid:
        await run_strike(cookie, tid)

if __name__ == "__main__":
    asyncio.run(main())
