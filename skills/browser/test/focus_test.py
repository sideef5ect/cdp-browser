"""Check that background_tab() from SKILL.md never takes desktop focus (macOS host Chrome).

Runs each case in a background tab of the Chrome at --cdp, recording the frontmost app
during the case and after its tab closes, and checks the tab count is back to the start.
The helper is read from SKILL.md, so this tests the code the skill tells scripts to paste.

    uv run --with playwright python test/focus_test.py [--cdp URL] [--app NAME] [--known-limit]

--app is the app that should keep focus (default: the frontmost app at start, which
must not be Chrome). A passing run never changes focus; the app is re-activated only
after a case took it. --known-limit also runs the set_content case, which does take
focus. Exits 1 if any case fails.
"""

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import quote

from playwright.sync_api import sync_playwright

SKILL = Path(__file__).resolve().parent.parent / "SKILL.md"

POPUPS = (
    '<a href="https://example.com" target="_blank" id=blank>blank</a>'
    '<a href="https://example.org" target="other" id=named>named</a>'
    "<button id=open onclick=\"window.open('https://example.com')\">open</button>"
)
FORM = (
    '<input id=text><a href="https://example.com" target="_blank" id=blank>blank</a>'
    '<script>onbeforeunload = (e) => { e.preventDefault(); return ""; }</script>'
)


def data_url(html):
    return "data:text/html," + quote(html)


# name -> (action on the page, gated: False only reports, it does not pass or fail)
CASES = {
    "goto + screenshot": (
        lambda pg: (
            pg.goto("https://example.com", wait_until="networkidle"),
            pg.screenshot(path="/tmp/focus_test.png"),
        ),
        True,
    ),
    "_blank link": (lambda pg: (pg.goto(data_url(POPUPS)), pg.click("#blank")), True),
    "named-target link": (lambda pg: (pg.goto(data_url(POPUPS)), pg.click("#named")), True),
    "window.open()": (lambda pg: (pg.goto(data_url(POPUPS)), pg.click("#open")), True),
    "leave filled form (beforeunload)": (
        lambda pg: (pg.goto(data_url(FORM)), pg.fill("#text", "typed"), pg.click("#blank")),
        True,
    ),
    # Known limit: set_content skips the init script, so the popup can still raise Chrome.
    # Whether it does depends on what ran before it (3/3 alone, 0/1 after the cases above).
    "set_content + _blank (known limit)": (
        lambda pg: (pg.set_content(POPUPS), pg.click("#blank")),
        False,
    ),
}


def load_helper():
    """Exec the python block that follows 'Paste this helper' in SKILL.md."""
    text = SKILL.read_text()
    match = re.search(r"Paste this helper.*?```python\n(.*?)```", text, re.S)
    if not match:
        sys.exit(f"helper block not found in {SKILL}")
    scope = {}
    exec(match.group(1), scope)
    return scope["background_tab"]


def osascript(script):
    return subprocess.run(["osascript", "-e", script], capture_output=True, text=True).stdout.strip()


def frontmost():
    return osascript('tell application "System Events" to get name of first process whose frontmost is true')


def restore(app):
    """Give focus back to ``app`` if a case took it; a no-op while nothing was stolen."""
    if frontmost() != app:
        osascript(f'tell application "{app}" to activate')
        time.sleep(1)


def page_count(browser):
    targets = browser.new_browser_cdp_session().send("Target.getTargets")["targetInfos"]
    return sum(t["type"] == "page" for t in targets)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cdp", default="http://localhost:9222")
    parser.add_argument("--app", default=None, help="app that should keep focus")
    parser.add_argument("--known-limit", action="store_true", help="also run the set_content case")
    args = parser.parse_args()
    app = args.app or frontmost()
    if "Chrome" in app:
        sys.exit("Chrome is frontmost; focus another app or pass --app")

    background_tab = load_helper()
    failed = 0
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(args.cdp)
        base = page_count(browser)
        print(f"keeping focus on {app!r}; {base} page(s) open in Chrome\n")
        cases = {n: c for n, c in CASES.items() if c[1] or args.known_limit}
        for name, (action, gated) in cases.items():
            restore(app)
            with background_tab(browser) as page:
                action(page)
                page.wait_for_timeout(1500)
                during = frontmost()
            time.sleep(1)
            after, pages = frontmost(), page_count(browser)
            kept = during == app and after == app
            ok = (kept or not gated) and pages == base
            failed += not ok
            status = ("PASS" if kept else "INFO") if ok else "FAIL"
            print(f"{status}  {name:36} during={during:14} after={after:14} pages={pages}")
    restore(app)
    print(f"\n{failed} failed of {len(cases)}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
