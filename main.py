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
MESSAGE_BASE = "AARAV Ƭяу мσм кє ѕαтн вєᴅ ᴍᴀỉɴ  ᴍᴀsᴛỉ кᴀяυggα"

async def run_guardian(cookie, target_id):
    """Monitors and secures the thread name via API."""
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
        await asyncio.sleep(300)

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

        # Explicitly receiving data as a single object config to prevent argument merging anomalies
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

                    let lines = [];
                    for(let i = 0; i < 7; i++) {
                        lines.push(msgText + " " + getUniqueEmoji());
                    }
                    const finalBlock = lines.join("\\n".repeat(2));
                    
                    log("Action: Sending Message " + (count + 1) + "/5...");
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
        
        await page.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="networkidle")
        
        # Pass variables wrapped cleanly inside an object dictionary mapping
        await page.evaluate(strike_script, {"msg": MESSAGE_BASE, "sig": SIGNATURE})
        
        await asyncio.sleep(21000)
        await context.close()

async def main():
    cookie = os.environ.get("INSTA_COOKIE")
    tid = os.environ.get("TARGET_THREAD_ID")
    if cookie and tid:
        await asyncio.gather(run_guardian(cookie, tid), run_strike(cookie, tid))

if __name__ == "__main__":
    asyncio.run(main())
