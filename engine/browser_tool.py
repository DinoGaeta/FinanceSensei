
import os
import json
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from .tools import Tool
from typing import Dict, Any

class KitsuneBrowserTool(Tool):
    """
    A KillerSkill tool that allows the Kitsune Agent to navigate the web,
    handle Javascript, and interact with complex DEX pages like GeckoTerminal.
    """
    
    @property
    def name(self):
        return "browse_web"

    @property
    def description(self):
        return (
            "Navigate and interact with websites. "
            "Params: 'action' (visit, click, type, scroll), 'url' (for visit), "
            "'selector' (for click/type), 'text' (for type)."
        )

    def execute(self, params: Dict[str, Any]) -> str:
        action = params.get("action", "visit")
        url = params.get("url")
        selector = params.get("selector")
        text = params.get("text")

        try:
            with sync_playwright() as p:
                # HEADED MODE: Enable visibility so the user can see the agent moving
                browser = p.chromium.launch(headless=False, slow_mo=1000) 
                
                # Set a common user agent and viewport for 'Smart' look
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                    viewport={'width': 1280, 'height': 720}
                )
                page = context.new_page()
                
                if action == "visit":
                    if not url: return "[Error] URL required for 'visit'"
                    page.goto(url, wait_until="networkidle", timeout=60000)
                elif action == "click":
                    if not selector: return "[Error] Selector required for 'click'"
                    # Highlight action for visibility
                    page.locator(selector).highlight()
                    page.click(selector, timeout=10000)
                elif action == "type":
                    if not selector or not text: return "[Error] Selector and text required for 'type'"
                    page.locator(selector).highlight()
                    page.fill(selector, text, timeout=10000)
                    page.keyboard.press("Enter")
                
                # Take screenshot
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                shot_path = f"reports/screenshots/shot_{timestamp}.png"
                os.makedirs("reports/screenshots", exist_ok=True)
                page.screenshot(path=shot_path)

                # After action, extract content
                content = page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Cleanup: remove scripts, styles, etc.
                for script in soup(["script", "style"]):
                    script.extract()
                
                # Get text
                text_content = soup.get_text(separator=' ', strip=True)
                # Truncate to avoid blowing up the LLM context (approx 5000 chars)
                summary = text_content[:5000]
                
                # Look for potential interactive elements to help the agent "see" what to do next
                buttons = [b.get_text() for b in soup.find_all('button') if b.get_text()][:10]
                links = [{"text": a.get_text(), "href": a.get('href')} for a in soup.find_all('a') if a.get_text()][:10]
                
                browser.close()
                
                return json.dumps({
                    "url": page.url,
                    "screenshot": shot_path,
                    "content_summary": summary,
                    "active_elements": {
                        "buttons": buttons,
                        "links": links
                    }
                }, indent=2)

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            return f"""[Error] Browser Action Failed: {str(e)}

--- DEBUG INFO ---
{error_details}

--- POSSIBLE FIXES ---
1. Install Playwright: pip install playwright
2. Install Chromium: playwright install chromium
3. If on Windows, try running as Administrator
4. Check if any antivirus is blocking browser automation
"""
