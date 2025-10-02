# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains two main projects:

1. **Wake Word Detector** (`wake_word_vosk.py`) - Offline Russian speech recognition using Vosk
2. **MeetingBot** (`meetingbot/`) - Selenium-based Zoom meeting automation bot

## Running the Projects

### Wake Word Detector
```bash
source venv/bin/activate
python wake_word_vosk.py
```

### MeetingBot
```bash
cd meetingbot
python bot.py
```

Bot will run until manually stopped with Ctrl+C.

### Ubuntu Server Deployment (MeetingBot)
```bash
cd meetingbot
chmod +x setup_ubuntu.sh
./setup_ubuntu.sh
cp .env.example .env
# Edit .env with your settings
python bot.py
```

## Critical Architecture Notes

### MeetingBot Headless vs Non-Headless Behavior

**IMPORTANT**: The bot behaves differently in headless mode vs non-headless mode due to how Zoom's web interface handles automation:

- **Non-headless mode** (`HEADLESS=false`): Standard Selenium methods work normally
  - `element.click()` works
  - `element.send_keys()` works

- **Headless mode** (`HEADLESS=true`): Requires special techniques for iframe interactions
  - **Buttons (Mute/Video/Join)**: MUST use JavaScript `.click()` instead of Selenium WebElement click
  - **Text input**: MUST use CDP `Input.insertText` after iframe context switch
  - Standard Selenium methods (`element.click()`, `send_keys()`) fail silently inside Zoom's iframe

### MeetingBot Click/Input Pattern

All interactions with Zoom UI inside the `#webclient` iframe follow this pattern:

```python
# 1. Switch to iframe
iframe = driver.find_element("id", "webclient")
driver.switch_to.frame(iframe)

# 2. For buttons - use JavaScript click
clicked = driver.execute_script("""
    var elem = document.elementFromPoint(x, y);
    while (elem && elem.tagName !== 'BUTTON') {
        elem = elem.parentElement;
    }
    if (elem) {
        elem.click();
        return {success: true};
    }
    return {success: false};
""")

# 3. For text input - use CDP Input.insertText
driver.execute_script("""
    var input = document.getElementById('input-for-name');
    input.focus();
    input.click();
""")
driver.execute_cdp_cmd('Input.insertText', {'text': BOT_NAME})
```

**Never** use coordinate-based ActionChains or element.send_keys() in headless mode for Zoom iframe - they will fail.

### MeetingBot Session Management

- Each run creates a new session directory: `sessions/YYYYMMDD_HHMMSS/screenshots/`
- Screenshots are numbered sequentially with descriptive names
- Bot continues running after joining meeting until Ctrl+C

## Configuration Files

### meetingbot/.env
Required environment variables:
- `MEETING_URL` - Zoom meeting URL
- `BOT_NAME` - Name to display in meeting
- `HEADLESS` - `true` for server deployment, `false` for debugging
- `WINDOW_WIDTH`, `WINDOW_HEIGHT` - Browser dimensions (1200x800 tested)

## Dependencies

### Wake Word Detector
- `vosk` - Offline speech recognition
- `sounddevice` - Audio capture
- Vosk Russian model in `models/vosk-model-small-ru-0.22/`

### MeetingBot
- `selenium` - Browser automation
- `webdriver-manager` - Automatic ChromeDriver management
- `python-dotenv` - Environment variables
- Google Chrome (installed via `setup_ubuntu.sh` on Ubuntu)
