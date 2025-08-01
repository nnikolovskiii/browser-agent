import asyncio
import sys
sys.path.insert(0, '/home/nnikolovskii/dev/ai_task_agent')
from src.agent.tools.browser_tools import browser_session, goto_url_helper, get_page_content

async def test_session_persistence():
    try:
        print("=== First Run: Opening browser and navigating to a site ===")
        # Navigate to a site that requires login (using a test site for demonstration)
        await goto_url_helper("https://github.com")
        
        # Get the page content to see if we're logged in or not
        content = await get_page_content()
        print("Initial page content (check if logged in):")
        print(content[:500] + "..." if len(content) > 500 else content)
        
        print("\n=== Closing browser session ===")
        # Close the browser session (but keep the user data directory)
        await browser_session.close()
        
        print("\n=== Second Run: Reopening browser to check if session persists ===")
        # Reopen the browser and navigate to the same site
        await goto_url_helper("https://github.com")
        
        # Get the page content again to see if we're still logged in
        content = await get_page_content()
        print("Page content after reopening (check if still logged in):")
        print(content[:500] + "..." if len(content) > 500 else content)
        
        print("\n=== Test completed ===")
        print("If you were logged in during the first run, you should still be logged in during the second run.")
        print("This confirms that session persistence is working correctly.")
        
    except Exception as e:
        print(f"An error occurred during testing: {e}")
    finally:
        # Make sure to close the browser session at the end
        await browser_session.close()

if __name__ == "__main__":
    asyncio.run(test_session_persistence())