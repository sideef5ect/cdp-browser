---
name: browser
description: "Use this skill to control a browser. Trigger on: 'browser', 'fetch page', 'scrape', 'screenshot', when WebFetch tool fails, or when user wants to automate browser tasks."
---

# Browser Automation

Control a persistent browser via CDP using Playwright. Two backends, same CDP URL (`http://localhost:9222`):

| Backend | When | Focus risk | Setup |
|---------|------|------------|-------|
| Docker container | Default; devcontainers, scraping | None (virtual display) | [docs/setup-container.md](docs/setup-container.md) |
| Host Chrome | Need the user's real logins, or no Docker | **High**: Chrome is on the user's desktop | [docs/setup-host-chrome.md](docs/setup-host-chrome.md) |

## Check First

```bash
curl -s http://localhost:9222/json/version
```

If it answers, connect. If not, start a backend from its setup doc. Never kill or restart a Chrome the user is using without asking.

## Don't Steal Focus

Always drive pages through `background_tab()` (below). It costs nothing in the container and is what keeps host Chrome from jumping in front of the user.

Playwright input over CDP (`click`, `fill`, `press`, `set_input_files`) goes to the page, not the OS, so the physical mouse and keyboard are never touched. What raises Chrome is a *window-level* action. Avoid:

| Steals focus | Do instead |
|--------------|------------|
| `context.new_page()`, `window.open()`, a foreground tab | `Target.createTarget` with `background: True, focus: False` |
| `page.bring_to_front()` | Nothing; background pages render and accept input |
| Navigating away from a filled form (native "Leave this page?" dialog) | Stop the page's `beforeunload` handlers before they run (done by `background_tab()`); close tabs with `Target.closeTarget`, which skips `beforeunload` |
| A native `alert`/`confirm` left open | `page.on("dialog", ...)` to answer it immediately |
| A native file picker (`click` on `<input type=file>`) | `page.set_input_files(selector, path)` |
| A `target=_blank` link or `window.open()`: Chrome raises the popup's window | Load them in the same tab instead (done by `background_tab()`; `page.go_back()` returns). Only for documents loaded with `goto`: for your own HTML use `page.goto("data:text/html," + quote(html))`, not `set_content` |

Paste this helper into every script:

```python
import time
from contextlib import contextmanager

from playwright.sync_api import Error as PlaywrightError, sync_playwright

CDP_URL = "http://localhost:9222"

# A popup or a "Leave this page?" dialog raises Chrome even from a background tab, and
# answering or closing it after is too late. So _blank links and window.open() load in
# this tab instead (page.go_back() returns), and the page's beforeunload handlers never
# run: this listener is registered before the page's scripts and stops the rest.
NO_POPUPS = """
window.addEventListener("beforeunload", (e) => e.stopImmediatePropagation(), true);
window.open = (url) => { if (url) location.assign(url); return null; };
document.addEventListener("click", (e) => {
  const a = e.target.closest && e.target.closest("a[target]");
  if (a && a.href && (a.target === "_blank" || !a.target.startsWith("_"))) {
    e.preventDefault();
    location.assign(a.href);
  }
}, true);
"""


def _target_id(context, page):
    session = context.new_cdp_session(page)
    try:
        return session.send("Target.getTargetInfo")["targetInfo"]["targetId"]
    finally:
        session.detach()


@contextmanager
def background_tab(browser):
    """A new tab that never takes focus, popups kept in it; it is closed on exit."""
    context = browser.contexts[0]
    session = browser.new_browser_cdp_session()
    blank = {"url": "about:blank", "background": True, "focus": False}
    target = session.send("Target.createTarget", blank)["targetId"]
    page = None
    for _ in range(50):
        for candidate in context.pages:
            try:
                if _target_id(context, candidate) == target:
                    page = candidate
                    break
            except PlaywrightError:  # a tab closing while it is read
                continue
        if page:
            break
        time.sleep(0.1)
    if page is None:
        raise RuntimeError(f"Chrome opened tab {target} but it never showed as a page")
    page.on("dialog", lambda d: d.dismiss())  # alert/confirm left open would raise Chrome
    page.add_init_script(NO_POPUPS)  # every document loaded from here on; not set_content
    try:
        yield page
    finally:
        for info in session.send("Target.getTargets")["targetInfos"]:
            if target in (info["targetId"], info.get("openerId")):
                session.send("Target.closeTarget", {"targetId": info["targetId"]})
```

Each recipe below assumes it.

## Recipes

### Fetch Text Content

```python
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(CDP_URL)
    with background_tab(browser) as page:
        page.goto("https://example.com", wait_until="networkidle")
        print(page.inner_text("article"))  # or "body", "main"
```

### Fetch HTML

```python
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(CDP_URL)
    with background_tab(browser) as page:
        page.goto("https://example.com", wait_until="networkidle")
        html = page.content()
```

For complex parsing, use [JustHTML](https://github.com/nicois/justhtml): `from justhtml import parse; doc = parse(html)`.

### Screenshot

Works on a background tab; no need to bring it forward.

```python
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(CDP_URL)
    with background_tab(browser) as page:
        page.goto("https://example.com", wait_until="networkidle")
        page.screenshot(path="screenshot.png", full_page=True)
```

### Fill a Form and Upload a File

```python
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(CDP_URL)
    with background_tab(browser) as page:
        page.goto("https://example.com/upload")
        page.fill("input[name=title]", "Report")
        page.set_input_files("input[type=file]", "/path/to/file.png")  # no native picker
```

## Docs Index

| Doc | Read when |
|-----|-----------|
| [docs/setup-container.md](docs/setup-container.md) | CDP is not answering and Docker is available; ports, volumes, VNC, container management |
| [docs/setup-host-chrome.md](docs/setup-host-chrome.md) | The task needs the user's real logins, or there is no Docker |
| [docs/webkit.md](docs/webkit.md) | H.264 video on ARM64, or Safari compatibility; WebKit has no CDP and runs inside the container |
