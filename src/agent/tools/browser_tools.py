import playwright.async_api
from langchain_core.tools import tool
import os
import tempfile
import asyncio
from bs4 import BeautifulSoup

# --- Playwright Session Management ---
# This object will hold our browser instance so it persists across tool calls.
class BrowserSession:
    def __init__(self):
        self._playwright = None
        self.browser = None
        self.page = None
        self._temp_dir = None
        self._initialized = False

    async def start(self):
        if not self._initialized:
            # Create a temporary directory for Playwright artifacts
            self._temp_dir = tempfile.mkdtemp()
            # Set the TMPDIR environment variable for Playwright
            os.environ["TMPDIR"] = self._temp_dir

            self._playwright = await playwright.async_api.async_playwright().start()
            self.browser = await self._playwright.chromium.launch(headless=False) # Start in non-headless to see it work
            self.page = await self.browser.new_page()
            self._initialized = True

    async def close(self):
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self._playwright:
            await self._playwright.stop()

        # Clean up the temporary directory if it exists
        if self._temp_dir and os.path.exists(self._temp_dir):
            import shutil
            try:
                shutil.rmtree(self._temp_dir)
                self._temp_dir = None
            except Exception as e:
                print(f"Error cleaning up temporary directory: {e}")
        self._initialized = False

# Create a single instance to be used by all tools
browser_session = BrowserSession()
# We'll initialize it when needed, not at module load time


# --- Browser Tools ---

@tool
async def goto_url(url: str) -> str:
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
        await browser_session.page.locator(selector).click()
        # Wait for the page to be fully loaded and for network to be idle after clicking
        # This ensures JavaScript has executed and dynamic content is loaded
        await browser_session.page.wait_for_load_state("networkidle", timeout=10000)
        return f"Successfully clicked on element with selector '{selector}'."
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

@tool
async def get_page_content(dummy: str = "") -> str:
    """Returns the cleaned text content of the current web page, removing clutter."""
    """Use this to 'see' the current state of the page and decide the next action."""
    try:
        # Ensure browser is started
        await browser_session.start()

        # Wait for the page to be fully loaded and for network to be idle
        # This ensures JavaScript has executed and dynamic content is loaded
        await browser_session.page.wait_for_load_state("networkidle", timeout=10000)

        # Get the raw HTML content
        html_content = await browser_session.page.content()

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Get page title and URL
        title = soup.title.string if soup.title else "No title"
        current_url = browser_session.page.url

        # Create a copy of the soup for element extraction
        elements_soup = BeautifulSoup(html_content, 'html.parser')

        # Remove elements that typically contain clutter
        for element_to_remove in soup(["script", "style", "meta", "noscript", "svg", "path", 
                                      "footer", "header", "nav", "aside", "iframe"]):
            element_to_remove.extract()

        # Try to remove common ad containers and non-content elements
        for element in soup.find_all(class_=lambda c: c and any(ad_term in c.lower() 
                                    for ad_term in ['ad', 'banner', 'cookie', 'popup', 'menu', 'sidebar', 'footer', 'header', 'nav'])):
            element.extract()

        # Extract main content (if available)
        main_content = None
        for tag in ['main', 'article', 'div[role="main"]', '.main-content', '#content', '#main']:
            main_element = soup.select_one(tag)
            if main_element:
                main_content = main_element
                break

        # If we found a main content area, use that; otherwise use the whole body
        if main_content:
            content_soup = main_content
        else:
            content_soup = soup.body if soup.body else soup

        # Extract text from the content
        text_content = content_soup.get_text(separator='\n', strip=True)

        # Clean up excessive whitespace and empty lines
        lines = [line.strip() for line in text_content.splitlines() if line.strip()]
        clean_text = '\n'.join(lines)

        # Truncate if too long (to avoid overwhelming the model)
        max_length = 6000  # Reduced to make room for element information
        if len(clean_text) > max_length:
            clean_text = clean_text[:max_length] + "\n[Content truncated due to length...]"

        # Extract interactive elements
        interactive_elements = []

        # Extract buttons
        buttons = []
        for button in elements_soup.find_all(['button', 'input']):
            if button.name == 'input' and button.get('type') not in ['submit', 'button', 'reset']:
                continue

            button_id = button.get('id', '')
            button_class = ' '.join(button.get('class', []))
            button_text = button.get_text(strip=True) or button.get('value', '')

            # Create a CSS selector for this button
            selector = f"#{button_id}" if button_id else ""
            if not selector and button_class:
                selector = f".{button_class.replace(' ', '.')}"
            if not selector:
                # Fallback to more complex selector
                if button.name == 'button':
                    selector = f"button:contains('{button_text}')" if button_text else ""
                else:
                    selector = f"input[type='{button.get('type', '')}'][value='{button_text}']" if button_text else ""

            if selector:
                buttons.append({
                    'type': 'button',
                    'text': button_text,
                    'selector': selector
                })

        # Extract links
        links = []
        for link in elements_soup.find_all('a'):
            link_id = link.get('id', '')
            link_class = ' '.join(link.get('class', []))
            link_text = link.get_text(strip=True)
            link_href = link.get('href', '')

            # Create a CSS selector for this link
            selector = f"#{link_id}" if link_id else ""
            if not selector and link_class:
                selector = f".{link_class.replace(' ', '.')}"
            if not selector and link_text:
                selector = f"a:contains('{link_text}')"

            if selector:
                links.append({
                    'type': 'link',
                    'text': link_text,
                    'href': link_href,
                    'selector': selector
                })

        # Extract form inputs
        inputs = []
        for input_elem in elements_soup.find_all(['input', 'textarea', 'select']):
            if input_elem.name == 'input' and input_elem.get('type') in ['submit', 'button', 'reset']:
                continue  # Already handled in buttons

            input_id = input_elem.get('id', '')
            input_name = input_elem.get('name', '')
            input_type = input_elem.get('type', '') if input_elem.name == 'input' else input_elem.name
            input_placeholder = input_elem.get('placeholder', '')

            # Create a CSS selector for this input
            selector = f"#{input_id}" if input_id else ""
            if not selector and input_name:
                selector = f"[name='{input_name}']"
            if not selector:
                selector = f"{input_elem.name}[type='{input_type}']" if input_type else input_elem.name

            if selector:
                inputs.append({
                    'type': input_type,
                    'name': input_name,
                    'placeholder': input_placeholder,
                    'selector': selector
                })

        # Format the interactive elements
        elements_text = "INTERACTIVE ELEMENTS:\n"

        if buttons:
            elements_text += "\nButtons:\n"
            for i, button in enumerate(buttons[:10], 1):  # Limit to 10 buttons
                elements_text += f"{i}. Text: '{button['text']}', Selector: '{button['selector']}'\n"
            if len(buttons) > 10:
                elements_text += f"... and {len(buttons) - 10} more buttons\n"

        if links:
            elements_text += "\nLinks:\n"
            for i, link in enumerate(links[:10], 1):  # Limit to 10 links
                elements_text += f"{i}. Text: '{link['text']}', Href: '{link['href']}', Selector: '{link['selector']}'\n"
            if len(links) > 10:
                elements_text += f"... and {len(links) - 10} more links\n"

        if inputs:
            elements_text += "\nForm Inputs:\n"
            for i, input_elem in enumerate(inputs[:10], 1):  # Limit to 10 inputs
                elements_text += f"{i}. Type: '{input_elem['type']}', Name: '{input_elem['name']}', "
                elements_text += f"Placeholder: '{input_elem['placeholder']}', Selector: '{input_elem['selector']}'\n"
            if len(inputs) > 10:
                elements_text += f"... and {len(inputs) - 10} more inputs\n"

        # Format the output with structured information
        result = f"PAGE TITLE: {title}\nURL: {current_url}\n\n{elements_text}\nPAGE CONTENT:\n{clean_text}"

        return result
    except Exception as e:
        return f"Error getting page content: {e}"

# Bind these tools for the LLM, just like you did in llm_tools.py
web_tools = [goto_url, click_element, fill_text, get_page_content]
web_tools_by_name = {tool.name: tool for tool in web_tools}

# You would then bind these to your LLM
# llm_with_web_tools = kimi_llm.bind_tools(web_tools)
