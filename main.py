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
MESSAGE_BASE = "ᴘʀᴀᴛɪᴋ-ᴠᴇᴇʀ-ꜱᴜʀᴀᴊ-ɴᴇᴍᴇꜱɪꜱ Ƭяу мσм кє ѕαтн вєᴅ ᴍᴀỉɴ  ᴍᴀsᴛỉ кᴀяυggα"

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
                let count = 0;
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
                            if (btn) { btn.click(); log("Action: Button clicked."); }
                            else { box.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true})); log("Action: Used Enter key."); }
                        }, 600);
                    }
                };

                const pulse = () => {
                    if (count > 0 && count % 5 === 0) {
                        log("Action: Sending Signature & Resting...");
                        sendText(sigText);
                        const end = Date.now() + 8000;
                        const rest = () => {
                            if (Date.now() < end) { window.scrollBy(0, 200); setTimeout(rest, 1000); }
                            else { count = 0; pulse(); }
                        };
                        rest(); return;
                    }

                    const messageEmoji = getUniqueEmoji();
                    
                    let lines = [];
                    for(let i = 0; i < 7; i++) {
                        lines.push(msgText + " " + messageEmoji);
                    }
                    const finalBlock = lines.join("\\n".repeat(2));
                    
                    log("Action: Sending Message " + (count + 1) + "/5 (Emoji: " + messageEmoji + ")...");
                    sendText(finalBlock);
                    count++;
                    setTimeout(pulse, 5000 + Math.random() * 2000);
                }
                pulse();
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
