import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the browser session from browser_tools
from src.agent.tools.browser_tools import browser_session, goto_url_helper

async def test_google_login():
    """
    Opens a browser window and navigates to Google for testing login.
    The browser has been configured to bypass security warnings.
    Press Enter in the terminal to close the browser.
    """
    try:
        print("=== Google Login Test ===")
        print("- Browser window will open and navigate to Google")
        print("- Try to log in to your Google account")
        print("- The browser has been configured to bypass security warnings")
        print("- Press Enter in this terminal window when you're done to close the browser")

        # Start the browser session
        await browser_session.start()

        # Navigate to Google
        print("\nNavigating to Google...")
        await goto_url_helper("https://accounts.google.com")

        print("\n=== Browser is ready for testing Google login ===")
        print("Please try to log in to your Google account.")
        print("Press Enter to close the browser when you're done...")

        # Wait for user to press Enter
        await asyncio.get_event_loop().run_in_executor(None, input)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Make sure to close the browser session at the end
        print("\n=== Closing browser session ===")
        await browser_session.close()
        print("Browser session closed. Your login information has been saved.")
        print("Run this script again to reopen the browser with your saved session.")

if __name__ == "__main__":
    asyncio.run(test_google_login())