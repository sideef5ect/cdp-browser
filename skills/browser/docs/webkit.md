# WebKit Usage Guide

WebKit is Safari's browser engine. Use it when you need H.264 video support on ARM64 Linux (where Chromium lacks proprietary codecs).

## When to Use WebKit

| Scenario | Use |
|----------|-----|
| General browsing, scraping | Chromium (CDP) |
| H.264 video playback testing | WebKit |
| Safari compatibility testing | WebKit |

## Key Differences from Chromium

| Feature | Chromium | WebKit |
|---------|----------|--------|
| CDP support | Yes | No |
| H.264 on ARM64 | No | Yes |
| Persistent session | Yes (auto via CDP) | Yes (via `launch_persistent_context()`) |
| Connection method | `connect_over_cdp()` | `launch()` or `launch_persistent_context()` |

## Usage Examples

### Basic Navigation

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.webkit.launch(headless=True)
    page = browser.new_page()

    page.goto("https://example.com", wait_until="networkidle")
    print(page.title())

    browser.close()
```

### Screenshot

```python
with sync_playwright() as p:
    browser = p.webkit.launch(headless=True)
    page = browser.new_page()

    page.goto("https://example.com", wait_until="networkidle")
    page.screenshot(path="/tmp/screenshot.png", full_page=True)

    browser.close()
```

### Video Playback Testing

```python
with sync_playwright() as p:
    browser = p.webkit.launch(headless=True)
    page = browser.new_page()

    # Check H.264 support
    codecs = page.evaluate('''() => {
        const video = document.createElement("video");
        return {
            h264: video.canPlayType('video/mp4; codecs="avc1.42E01E"'),
            aac: video.canPlayType('audio/mp4; codecs="mp4a.40.2"'),
        }
    }''')
    print(f"Codec support: {codecs}")
    # Output: {'h264': 'probably', 'aac': 'probably'}

    # Test video page
    page.goto("https://your-video-site.com", wait_until="networkidle")

    video_info = page.evaluate('''() => {
        const video = document.querySelector("video");
        if (!video) return { exists: false };
        return {
            exists: true,
            error: video.error ? video.error.message : null,
            readyState: video.readyState,
            duration: video.duration
        };
    }''')
    print(f"Video info: {video_info}")

    browser.close()
```

### Persistent Context (Recommended for Sessions)

Use `launch_persistent_context()` to persist cookies, localStorage, and sessions across runs:

```python
with sync_playwright() as p:
    # Uses /app/webkit_profile volume in container
    context = p.webkit.launch_persistent_context(
        "/app/webkit_profile",
        headless=True
    )
    page = context.pages[0] if context.pages else context.new_page()

    page.goto("https://example.com")
    # Cookies and localStorage persist for next run

    context.close()
```

### With Authentication (Manual Cookies)

For one-off sessions or when you need to set cookies programmatically:

```python
with sync_playwright() as p:
    browser = p.webkit.launch(headless=True)
    context = browser.new_context()

    # Add cookies before navigation
    context.add_cookies([
        {
            "name": "session",
            "value": "your-session-token",
            "domain": ".example.com",
            "path": "/"
        }
    ])

    page = context.new_page()
    page.goto("https://example.com/protected")

    browser.close()
```

### Run Inside Container

Since WebKit doesn't use CDP, run scripts inside the container:

```bash
docker exec browser-cdp python3 << 'EOF'
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # Persistent context - saves cookies/localStorage to volume
    context = p.webkit.launch_persistent_context("/app/webkit_profile", headless=True)
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://example.com")
    page.screenshot(path="/tmp/webkit-screenshot.png")
    context.close()
EOF

# Copy screenshot out
docker cp browser-cdp:/tmp/webkit-screenshot.png ./screenshot.png
```

## Headless vs Headed

```python
# Headless (no GUI, faster)
browser = p.webkit.launch(headless=True)

# Headed (shows window, requires DISPLAY)
browser = p.webkit.launch(headless=False)
```

For headed mode in container, VNC must be running (it is by default).

## Limitations

- No CDP - can't connect remotely like Chromium
- Slower startup than connecting to existing Chromium CDP (launches new browser each time)
- Some sites may detect WebKit as Safari mobile

**Note:** Use `launch_persistent_context()` for session persistence - cookies and localStorage are saved to `/app/webkit_profile` volume.
