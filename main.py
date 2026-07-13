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

# The core automation script running inside the browser
STRIKE_SCRIPT = """
    (config) => {
        const msgText = config.msg;
        const sigText = config.sig;
        const targets = config.targetIds;
        
        const baseEmojis = ["🛌", "💤", "🥱", "🔥", "✨", "💫", "🌟", "🌙"];
        let emojiPool = [];
        let messageSequenceCount = 0;
        let currentTargetIndex = 0;
        
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
            () => { window.scrollBy({ top: Math.floor(Math.random() * 140) + 40, behavior: 'smooth' }); },
            () => { window.scrollBy({ top: -Math.floor(Math.random() * 80), behavior: 'smooth' }); },
            () => {
                const ev = new MouseEvent('mousemove', {
                    clientX: Math.floor(Math.random() * window.innerWidth),
                    clientY: Math.floor(Math.random() * window.innerHeight),
                    bubbles: true
                });
                document.dispatchEvent(ev);
            }
        ];

        const runLoop = () => {
            // After sending 4 messages, drop message activity and switch Group Chats
            if (messageSequenceCount >= 4) {
                messageSequenceCount = 0;
                
                // Check if there's another group chat to switch to
                if (currentTargetIndex < targets.length - 1) {
                    currentTargetIndex++;
                    const nextId = targets[currentTargetIndex];
                    log("🔄 Switching Group Chat: Shifting to Group ID -> " + nextId);
                    
                    // Navigate to the next group chat URL
                    window.location.href = "https://www.instagram.com/direct/t/" + nextId + "/";
                    return; // Stop this loop, page navigation triggers re-evaluation
                } else {
                    log("✅ Finished all assigned group chats for this account.");
                    window.parent.postMessage({ type: 'STATUS', text: 'ACCOUNT_DONE' }, '*');
                    return;
                }
            }

            const roll = Math.random();

            if (roll < 0.60) {
                const messageEmoji = getUniqueEmoji();
                let lines = [];
                for(let i = 0; i < 7; i++) {
                    lines.push(msgText + " " + messageEmoji);
                }
                const finalBlock = lines.join("\\n".repeat(2));
                
                log("Action: Transmitting primary content block...");
                sendText(finalBlock);
                messageSequenceCount++;
                setTimeout(runLoop, 12000 + Math.random() * 8000);

            } else if (roll >= 0.60 && roll < 0.85) {
                humanActions[Math.floor(Math.random() * humanActions.length)]();
                setTimeout(runLoop, 4000 + Math.random() * 4000);

            } else {
                log("Action: Deploying identity signature verify token...");
                sendText(sigText);
                messageSequenceCount++;
                setTimeout(runLoop, 15000 + Math.random() * 8000);
            }
        };

        runLoop();
    }
"""

async def process_account(account_index, session_cookie, thread_list):
    """Runs a single account through all group chats sequentially."""
    print(f"\n[ACCOUNT-{account_index}] Starting lifecycle loop...")
    
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=f"n_profile_seq_{account_index}", 
            headless=True,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15",
            viewport={'width': 375, 'height': 667},
            args=["--no-sandbox", "--disable-gpu"]
        )
        await Stealth().apply_stealth_async(context)
        
        sid = re.search(r'sessionid=([^;]+)', session_cookie).group(1) if 'sessionid=' in session_cookie else session_cookie
        await context.add_cookies([{'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com', 'path': '/', 'secure': True}])

        page = await context.new_page()
        
        # Flag to keep track of when the browser script completes its work
        account_completed = asyncio.Event()

        # Handle log capture and check for the completion status token
        async def handle_message(msg):
            data = msg.args[0].json_value() if msg.args else {}
            if isinstance(data, dict):
                if data.get('type') == 'LOG':
                    print(f"[BROWSER-ACC-{account_index}] {data.get('text')}")
                elif data.get('type') == 'STATUS' and data.get('text') == 'ACCOUNT_DONE':
                    account_completed.set()

        # Listen to messages routed out of the browser frames
        page.on("console", lambda msg: print(f"[BROWSER-CONSOLE] {msg.text}") if "Action" not in msg.text else None)
        
        # When moving from one GC page to another GC page, re-inject the automation script automatically
        async def on_frame_navigated(frame):
            if "direct/t/" in frame.url:
                await asyncio.sleep(5) # Give the layout framework structural time to assemble
                try:
                    await page.wait_for_selector('div[role="textbox"], [contenteditable="true"]', timeout=30000)
                    await page.evaluate(STRIKE_SCRIPT, {
                        "msg": MESSAGE_BASE, 
                        "sig": SIGNATURE,
                        "targetIds": thread_list
                    })
                except Exception as e:
                    print(f"[ERROR] Selector loading error on page navigation adjustment: {e}")

        page.on("framenavigated", lambda f: asyncio.create_task(on_frame_navigated(f)))
        
        # Inject custom cross-window message listeners before page loads
        await page.add_init_script("window.addEventListener('message', e => { if(e.data && e.data.type) console.log(JSON.stringify(e.data)); })")
        page.on("console", lambda msg: asyncio.create_task(handle_message(msg)) if ("LOG" in msg.text or "STATUS" in msg.text) else None)

        # Access the first target to fire up the system chain execution loop
        first_target = thread_list[0]
        print(f"[ACCOUNT-{account_index}] Navigating to initial room: {first_target}")
        await page.goto(f"https://www.instagram.com/direct/t/{first_target}/", wait_until="commit")
        
        # Wait until the browser signals that it went through all elements on the targets list
        try:
            await asyncio.wait_for(account_completed.wait(), timeout=600)
        except asyncio.TimeoutError:
            print(f"[ACCOUNT-{account_index}] Notice: Task reached max runtime execution buffer ceiling.")
            
        await context.close()
        print(f"[ACCOUNT-{account_index}] Context closed cleanly. Moving down queue list...")

async def main():
    raw_cookies = os.environ.get("INSTA_COOKIES", "")
    raw_threads = os.environ.get("TARGET_THREAD_IDS", "")
    
    if not raw_cookies or not raw_threads:
        print("❌ Missing Runtime Configuration: Ensure INSTA_COOKIES and TARGET_THREAD_IDS are defined.")
        return

    cookie_list = [c.strip() for c in raw_cookies.split(",") if c.strip()]
    thread_list = [t.strip() for t in raw_threads.split(",") if t.strip()]

    print(f"🚀 Starting Sequential Engine: Processing {len(cookie_list)} accounts step-by-step.")
    
    # Process each account completely one after the other
    for index, cookie in enumerate(cookie_list):
        await process_account(index + 1, cookie, thread_list)
        # Add a 15-second pause between different accounts logging in
        await asyncio.sleep(15)

    print("🏁 Sequence complete! All accounts processed.")

if __name__ == "__main__":
    asyncio.run(main())
