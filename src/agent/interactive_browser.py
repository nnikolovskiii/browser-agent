import asyncio
import sys
import os
import argparse

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the browser session from browser_tools
from src.agent.tools.browser_tools import browser_session, goto_url_helper

async def interactive_browser(start_url="https://www.google.com"):
    """
    Opens a browser window that the user can interact with manually.
    The browser session will persist between runs, so login information will be saved.
    Press Enter in the terminal to close the browser.

    Args:
        start_url (str): The URL to navigate to when the browser opens. Defaults to Google.
    """
    try:
        print("=== Starting Interactive Browser Session ===")
        print("- Browser window will open automatically")
        print("- You can manually interact with the browser")
        print("- Login information will be saved for future sessions")
        print("- Press Enter in this terminal window when you're done to close the browser")

        # Start the browser session
        await browser_session.start()

        # Navigate to the start page
        print(f"\nNavigating to {start_url}...")
        await goto_url_helper(start_url)

        print("\n=== Browser is ready for interaction ===")
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
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Open an interactive browser window.')
    parser.add_argument('--url', type=str, default="https://www.google.com",
                        help='The URL to navigate to when the browser opens. Defaults to Google.')
    args = parser.parse_args()

    # Run the interactive browser with the specified URL
    asyncio.run(interactive_browser(args.url))
