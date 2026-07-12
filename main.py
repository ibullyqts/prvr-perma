# -*- coding: utf-8 -*-
import asyncio
import os
import re
import sys
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

# --- ⚙️ BOLD PILLAR SETTINGS ---
TABS_PER_MACHINE = 1    # Recommended to keep at 1 for human-like behavior
PULSE_DELAY = 100       
CYCLE_DURATION = 300    # Increased to 5 minutes to allow for slow pacing
SESSION_MAX_SEC = 21000 
sys.stdout.reconfigure(encoding='utf-8')

async def run_strike(node_id, cookie, target_id, target_name):
    async with async_playwright() as p:
        user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
        profile_path = os.path.join(os.getcwd(), f"n_{node_id}")
        
        context = await p.chromium.launch_persistent_context(
            user_data_dir=profile_path,
            headless=True,
            user_agent=user_agent,
            viewport={'width': 375, 'height': 667},
            args=[
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-gpu"
            ]
        )

        await Stealth().apply_stealth_async(context)

        sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
        await context.add_cookies([{
            'name': 'sessionid', 'value': sid.strip(), 
            'domain': '.instagram.com', 'path': '/', 'secure': True, 'httpOnly': True
        }])

        # ⚡ BOLD ALIGNED SCRIPT (SLOW + BROWSING REST + SIGNATURE)
        strike_script = """
            (name, delay) => {
                const flowers = ["🌸", "🌹", "🌺", "🌻", "🌼", "🌷", "💐", "🪷"];
                const signature = "༺ρ 𝕣 ꪜ 𝕣 अब्बू ☽༻";
                let lastFlowerIndex = -1;
                let messageCount = 0;

                const getBlock = () => {
                    let randomIndex;
                    do {
                        randomIndex = Math.floor(Math.random() * flowers.length);
                    } while (randomIndex === lastFlowerIndex && flowers.length > 1);
                    
                    lastFlowerIndex = randomIndex;
                    const randomFlower = flowers[randomIndex];
                    const baseText = "RNK ᴛʀʏ. ᴍᴀ ғʟᴏᴡᴇʀ. " + randomFlower + " ʏᴀ ғɪʀᴇ 🔥??";
                    
                    let text = "";
                    for(let i = 0; i < 3; i++) {
                        text += baseText + "\\n".repeat(15);
                    }
                    return text;
                }

                const sendText = (text) => {
                    const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                    if (box) {
                        const dataTransfer = new DataTransfer();
                        dataTransfer.setData('text/plain', text);
                        const pasteEvent = new ClipboardEvent('paste', { clipboardData: dataTransfer, bubbles: true, cancelable: true });
                        box.focus();
                        box.dispatchEvent(pasteEvent);
                        box.dispatchEvent(new Event('input', { bubbles: true }));
                        
                        setTimeout(() => {
                            const sendBtn = Array.from(document.querySelectorAll('div[role="button"], button')).find(el => 
                                el.textContent === 'Send' || el.innerText === 'Send'
                            );
                            if (sendBtn) sendBtn.click();
                        }, 200);
                    }
                }

                const browseOrScroll = () => {
                    const scrollAmount = Math.floor(Math.random() * 400) - 200;
                    window.scrollBy(0, scrollAmount);
                }

                const pulse = () => {
                    // REST SESSION: After 5 messages, send signature then browse
                    if (messageCount > 0 && messageCount % 5 === 0) {
                        sendText(signature); 
                        
                        const restEnd = Date.now() + (Math.floor(Math.random() * 5000) + 5000);
                        const restLoop = () => {
                            if (Date.now() < restEnd) {
                                browseOrScroll();
                                setTimeout(restLoop, 1500);
                            } else {
                                messageCount = 0;
                                pulse();
                            }
                        };
                        restLoop();
                        return;
                    }

                    sendText(getBlock());
                    messageCount++;

                    // Sending Delay: 1-5 seconds between messages
                    const nextSendDelay = Math.floor(Math.random() * (5000 - 1000 + 1)) + 1000;
                    setTimeout(pulse, nextSendDelay);
                }
                pulse();
            }
        """

        elapsed = 0
        while elapsed < SESSION_MAX_SEC:
            pages = []
            for i in range(TABS_PER_MACHINE):
                pg = await context.new_page()
                await pg.route("**/*.{png,jpg,jpeg,gif,webp,svg,mp4,woff,woff2,ttf}", lambda route: route.abort())
                try:
                    await pg.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="commit", timeout=15000)
                    await pg.evaluate(strike_script, [target_name, PULSE_DELAY])
                    pages.append(pg)
                except: pass
            
            await asyncio.sleep(CYCLE_DURATION)
            for pg in pages: await pg.close()
            elapsed += CYCLE_DURATION

        await context.close()

async def main():
    cookie = os.environ.get("INSTA_COOKIE")
    target_id = os.environ.get("TARGET_THREAD_ID")
    target_name = os.environ.get("TARGET_NAME", "TARGET")
    m_id = os.environ.get("MACHINE_ID", "1")
    if cookie and target_id:
        await run_strike(m_id, cookie, target_id, target_name)

if __name__ == "__main__":
    asyncio.run(main())
