import playwright.async_api
from langchain_core.tools import tool
import os
import tempfile
import asyncio
from bs4 import BeautifulSoup
import re

# --- Playwright Session Management ---
# This object will hold our browser instance so it persists across tool calls.
# The browser session is configured to persist login information and cookies between runs.
# It uses a persistent user data directory (~/.playwright_user_data) to store session data.
# This means that if you log in to a website during one run, you will remain logged in
# for subsequent runs until you explicitly log out or clear the user data directory.
class BrowserSession:
    def __init__(self):
        self._playwright = None
        self.browser = None
        self.page = None
        self._user_data_dir = None
        self._initialized = False

    async def start(self):
        if not self._initialized:
            # Create a persistent user data directory for Playwright
            # This will store cookies, localStorage, and other session data
            self._user_data_dir = os.path.join(os.path.expanduser("~"), ".playwright_user_data")
            os.makedirs(self._user_data_dir, exist_ok=True)

            # Set the TMPDIR environment variable for Playwright
            os.environ["TMPDIR"] = self._user_data_dir

            self._playwright = await playwright.async_api.async_playwright().start()

            # Launch browser with persistent context using user data directory
            # Add arguments to make the browser appear more like a regular user browser
            # This helps avoid security warnings from sites like Google
            self.browser = await self._playwright.chromium.launch_persistent_context(
                user_data_dir=self._user_data_dir,
                headless=False,  # Start in non-headless to see it work
                ignore_default_args=["--enable-automation"],  # Hide automation
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",  # Set a regular Chrome user agent
                viewport={"width": 1920, "height": 1080},  # Set a common desktop resolution
                accept_downloads=True,  # Accept downloads automatically
                java_script_enabled=True,  # Ensure JavaScript is enabled
                bypass_csp=True,  # Bypass Content Security Policy
                args=[
                    "--disable-blink-features=AutomationControlled",  # Disable automation flags
                    "--no-sandbox",  # Needed in some environments
                    "--disable-web-security",  # Disable CORS and other security features that might block login
                    "--disable-features=IsolateOrigins,site-per-process",  # Disable site isolation
                    "--allow-running-insecure-content",  # Allow running insecure content
                    "--disable-notifications",  # Disable notifications
                    "--disable-popup-blocking",  # Disable popup blocking
                ]
            )

            # Get the first page or create a new one
            if self.browser.pages:
                self.page = self.browser.pages[0]
            else:
                self.page = await self.browser.new_page()

            # Set up automatic handling of dialogs (alerts, confirms, prompts)
            self.page.on("dialog", lambda dialog: asyncio.create_task(dialog.accept()))

            # Set extra HTTP headers that some sites check
            await self.page.set_extra_http_headers({
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Sec-Fetch-Dest": "document",
                "Accept-Encoding": "gzip, deflate, br",
            })

            # Execute script to mask automation
            await self.page.evaluate("""
                // Overwrite the automation-related properties
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false
                });

                // Overwrite user agent if needed
                Object.defineProperty(navigator, 'userAgent', {
                    get: () => window.navigator.userAgent.replace('Headless', '')
                });

                // Add language plugins (regular browsers have these)
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });

                // Add chrome object (regular Chrome has this)
                if (!window.chrome) {
                    window.chrome = {};
                    window.chrome.runtime = {};
                }
            """)

            self._initialized = True

    async def close(self):
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self._playwright:
            await self._playwright.stop()

        # We don't delete the user_data_dir to maintain persistence between sessions
        self._initialized = False

# Create a single instance to be used by all tools
browser_session = BrowserSession()
# We'll initialize it when needed, not at module load time


# --- Browser Tools ---

@tool
async def goto_url(url: str) -> str:
    """Navigates the browser to a specified URL."""
    return await get_page_content(url)


async def goto_url_helper(url: str) -> str:
    """Navigates the browser to a specified URL."""
    try:
        # Ensure browser is started
        await browser_session.start()
        # Navigate to the URL with a longer timeout for slow connections
        await browser_session.page.goto(url, timeout=60000)
        # Wait for the page to be fully loaded and for network to be idle
        # This ensures JavaScript has executed and dynamic content is loaded
        await browser_session.page.wait_for_load_state("networkidle", timeout=10000)
        return f"Successfully navigated to {url}"
    except Exception as e:
        return f"Error navigating to {url}: {e}"

@tool
async def click_element(selector: str, description: str) -> str:
    """Clicks on a web element found by a CSS selector."""
    """Use this to click on buttons, links, or other interactive elements.
    The 'description' should be a brief text explaining what you are clicking on, for example 'the login button'."""
    try:
        # Ensure browser is started
        await browser_session.start()
        # Click only the first matching element
        await browser_session.page.locator(selector).first.click()
        # Wait for the page to be fully loaded and for network to be idle after clicking
        # This ensures JavaScript has executed and dynamic content is loaded
        await browser_session.page.wait_for_load_state("networkidle", timeout=10000)
        return f"Successfully clicked on first element with selector '{selector}'."
    except Exception as e:
        return f"Error clicking element '{selector}': {e}"

@tool
async def fill_text(selector: str, text: str) -> str:
    """Fills a text input field with the given text."""
    """Use this for login forms, search bars, etc."""
    try:
        # Ensure browser is started
        await browser_session.start()
        await browser_session.page.locator(selector).fill(text)
        # Wait for any auto-suggest or dynamic content to load after filling text
        # This is especially important for search boxes that show suggestions
        await browser_session.page.wait_for_load_state("networkidle", timeout=5000)
        return f"Successfully filled '{text}' into element '{selector}'."
    except Exception as e:
        return f"Error filling element '{selector}': {e}"


async def get_page_content(dummy: str = "") -> str:
    """Returns the cleaned text content and interactive elements of the current web page."""
    try:
        # Ensure browser is started
        await browser_session.start()

        # Make sure we have the latest content
        await smart_wait_for_page(browser_session.page, timeout=5000)

        # Get the raw HTML content
        html_content = await browser_session.page.content()

        # If content is suspiciously short, try to wait more
        if len(html_content) < 1000:
            print("Warning: Page content seems too short, waiting for more content...")
            await asyncio.sleep(2)
            html_content = await browser_session.page.content()

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Get page title and URL
        title = soup.title.string if soup.title else "No title"
        current_url = browser_session.page.url

        # Remove clutter elements
        for element in soup(["script", "style", "meta", "noscript", "link"]):
            element.decompose()

        # Extract main content text
        text_content = extract_main_content(soup, current_url)

        # Extract interactive elements
        elements_info = await extract_interactive_elements(browser_session.page, soup)

        # Format the output
        result = f"PAGE TITLE: {title}\nURL: {current_url}\n\n"
        result += elements_info + "\n"
        result += f"PAGE CONTENT:\n{text_content}"

        return result
    except Exception as e:
        return f"Error getting page content: {e}"


def extract_main_content(soup: BeautifulSoup, url: str) -> str:
    """Extract main content text from the page."""
    # Try to find main content areas
    main_selectors = [
        'main', 'article', '[role="main"]', '.main-content', '#main',
        '#content', '.content', '.results', '#search', '.search-results'
    ]

    main_content = None
    for selector in main_selectors:
        elements = soup.select(selector)
        if elements:
            main_content = elements[0]
            break

    # If no main content found, use body
    if not main_content:
        main_content = soup.body if soup.body else soup

    # Extract text
    text_lines = []
    for element in main_content.find_all(text=True):
        text = element.strip()
        if text and len(text) > 1:  # Skip single characters
            parent = element.parent
            if parent and parent.name not in ['script', 'style', 'meta', 'title']:
                text_lines.append(text)

    # Join and clean up
    text_content = '\n'.join(text_lines)

    # Remove excessive whitespace
    text_content = re.sub(r'\n\s*\n', '\n\n', text_content)
    text_content = re.sub(r' +', ' ', text_content)

    # Truncate if too long
    max_length = 8000
    if len(text_content) > max_length:
        text_content = text_content[:max_length] + "\n[Content truncated due to length...]"

    return text_content


async def extract_interactive_elements(page, soup: BeautifulSoup) -> str:
    """Extract interactive elements using Playwright's capabilities."""
    elements_text = "INTERACTIVE ELEMENTS:\n"

    try:
        # Extract visible links
        links = await page.locator('a:visible').all()
        if links:
            elements_text += "\nLinks:\n"
            for i, link in enumerate(links):
                try:
                    text = await link.text_content()
                    href = await link.get_attribute('href')
                    if text and text.strip():
                        elements_text += f"{i}. Text: '{text.strip()}'"
                        if href:
                            elements_text += f", Href: '{href}'"
                        elements_text += "\n"
                except:
                    continue


        # Extract visible buttons
        buttons = await page.locator('button:visible, input[type="button"]:visible, input[type="submit"]:visible').all()
        if buttons:
            elements_text += "\nButtons:\n"
            for i, button in enumerate(buttons):
                try:
                    text = await button.text_content()
                    if not text:
                        text = await button.get_attribute('value')
                    if not text:
                        text = await button.get_attribute('aria-label')
                    if text and text.strip():
                        elements_text += f"{i}. Text: '{text.strip()}'\n"
                except:
                    continue

        # Extract visible input fields
        inputs = await page.locator(
            'input:visible:not([type="hidden"]):not([type="button"]):not([type="submit"]), textarea:visible, select:visible').all()
        if inputs:
            elements_text += "\nForm Inputs:\n"
            for i, input_elem in enumerate(inputs):
                try:
                    input_type = await input_elem.get_attribute('type') or 'text'
                    placeholder = await input_elem.get_attribute('placeholder')
                    name = await input_elem.get_attribute('name')
                    aria_label = await input_elem.get_attribute('aria-label')

                    desc_parts = [f"Type: '{input_type}'"]
                    if name:
                        desc_parts.append(f"Name: '{name}'")
                    if placeholder:
                        desc_parts.append(f"Placeholder: '{placeholder}'")
                    if aria_label:
                        desc_parts.append(f"Label: '{aria_label}'")

                    elements_text += f"{i}. {', '.join(desc_parts)}\n"
                except:
                    continue


    except Exception as e:
        elements_text += f"\nError extracting elements: {e}\n"

    return elements_text

# Bind these tools for the LLM, just like you did in llm_tools.py
web_tools = [click_element, fill_text, goto_url]
web_tools_by_name = {tool.name: tool for tool in web_tools}

# You would then bind these to your LLM
# llm_with_web_tools = kimi_llm.bind_tools(web_tools)

async def wait_for_content_stability(page, timeout=5000):
    """Wait for the page content to stabilize (no more changes)."""
    last_html = ""
    stable_count = 0
    check_interval = 500  # ms

    start_time = asyncio.get_event_loop().time()

    while (asyncio.get_event_loop().time() - start_time) * 1000 < timeout:
        current_html = await page.content()
        if current_html == last_html:
            stable_count += 1
            if stable_count >= 2:  # Content stable for 2 checks
                break
        else:
            stable_count = 0
        last_html = current_html
        await asyncio.sleep(check_interval / 1000)


async def smart_wait_for_page(page, timeout=30000):
    """Smart waiting that handles different page loading scenarios."""
    try:
        # First, wait for basic load
        await page.wait_for_load_state("load", timeout=timeout)

        # Check if it's a search page or dynamic content page
        current_url = page.url

        if "duckduckgo.com" in current_url and ("q=" in current_url or "?t=" in current_url):
            # DuckDuckGo search results
            try:
                # Wait for search results container
                await page.wait_for_selector('.results', timeout=10000)
                # Wait a bit more for all results to load
                await asyncio.sleep(1)
            except:
                # If specific selector fails, wait for network idle
                await page.wait_for_load_state("networkidle", timeout=10000)

        elif "google.com/search" in current_url:
            # Google search results
            try:
                await page.wait_for_selector('#search', timeout=10000)
                await asyncio.sleep(1)
            except:
                await page.wait_for_load_state("networkidle", timeout=10000)

        elif any(pattern in current_url for pattern in ['github.com', 'stackoverflow.com', 'reddit.com']):
            # Sites with known dynamic content
            await page.wait_for_load_state("networkidle", timeout=10000)
            await wait_for_content_stability(page, timeout=3000)

        else:
            # Default: wait for network idle with shorter timeout
            await page.wait_for_load_state("networkidle", timeout=10000)

        # Final check: ensure we have meaningful content
        content = await page.content()
        if len(content) < 500:  # Suspiciously short
            await asyncio.sleep(2)  # Give it more time

    except Exception as e:
        print(f"Warning during page wait: {e}")
        # Even if waiting fails, continue - we might have partial content

async def main_task():
    try:
        # Step 1: Use the goto_url tool to navigate to the desired page.
        url_to_visit = "https://duckduckgo.com/?t=h_&q=langchain+agents&ia=web"
        print(f"--- Navigating to {url_to_visit} ---")
        navigation_status = await goto_url_helper(url_to_visit)
        print(navigation_status)

        # If navigation was successful, the browser is now on the correct page.

        # Step 2: Now that you are on the page, use get_page_content to "see" it.
        print("\n--- Getting page content ---")
        page_content = await get_page_content()
        print(page_content)

    except Exception as e:
        print(f"An error occurred during the main task: {e}")
    finally:
        # This block is GUARANTEED to run, even if an error happens above.
        print("\n--- Cleaning up browser session ---")
        await browser_session.close()

# Replace your old lol() call with this one
# asyncio.run(main_task())
