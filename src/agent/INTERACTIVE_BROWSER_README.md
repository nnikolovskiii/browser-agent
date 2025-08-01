# Interactive Browser

This script provides a simple way to open a browser window that you can interact with manually. The browser session will persist between runs, so login information will be saved.

## Features

- Opens a browser window that you can interact with manually
- Persists login information between runs using a persistent user data directory
- Simple interface: just press Enter in the terminal to close the browser when you're done

## Usage

To use the interactive browser, run the following command from the project root:

```bash
python src/agent/interactive_browser.py
```

By default, the browser will open to Google. If you want to start at a different website, you can specify a URL:

```bash
python src/agent/interactive_browser.py --url https://github.com
```

## How it works

1. The script opens a browser window using Playwright
2. It navigates to the specified URL (defaults to Google if none is provided)
3. You can then manually interact with the browser, navigate to any website, log in, etc.
4. When you're done, press Enter in the terminal window to close the browser
5. Your login information and browser state will be saved for the next time you run the script

## Session Persistence

The browser session is configured to persist login information and cookies between runs. This means that if you log in to a website during one run, you will remain logged in for subsequent runs until you explicitly log out or clear the user data directory.

### How session persistence works

- The browser session uses a persistent user data directory located at `~/.playwright_user_data`
- This directory stores cookies, localStorage, sessionStorage, and other browser state
- When you restart the script, it will reuse this data, maintaining your login sessions

### Clearing session data

If you need to clear the session data and start fresh:

```bash
rm -rf ~/.playwright_user_data
```

This will remove all saved login information and cookies, requiring you to log in again on the next run.

## Browser Security Configuration

The browser is configured with enhanced security settings to ensure you can log in to websites like Google without encountering "browser not secure" warnings. The configuration includes:

- Setting a realistic user agent string
- Disabling automation flags
- Setting a common desktop viewport size
- Bypassing Content Security Policy
- Handling JavaScript dialogs automatically
- Setting appropriate HTTP headers
- Using JavaScript to mask automation indicators

These configurations help ensure that you can log in to most websites without encountering security warnings or being blocked as an automated browser.
