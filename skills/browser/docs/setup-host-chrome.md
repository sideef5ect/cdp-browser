# Setup: Host Chrome

Drive the user's installed Chrome when the task needs their real logins, or Docker is not available. Chrome runs on the user's desktop, so always use `background_tab()` (see [Don't Steal Focus](../SKILL.md#dont-steal-focus)).

## Start

Chrome refuses `--remote-debugging-port` on its default profile, so it needs its own `--user-data-dir`. This starts a separate Chrome instance next to the user's normal one.

### macOS

`open -g` launches it without bringing it to the front. The throttling flags keep background tabs running at full speed while the user works elsewhere:

```bash
open -g -na "Google Chrome" --args \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.cache/chrome-cdp" \
  --no-first-run --no-default-browser-check \
  --disable-background-timer-throttling \
  --disable-renderer-backgrounding \
  --disable-backgrounding-occluded-windows
```

### Linux

```bash
google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.cache/chrome-cdp" \
  --no-first-run --no-default-browser-check \
  --disable-background-timer-throttling \
  --disable-renderer-backgrounding \
  --disable-backgrounding-occluded-windows \
  >/dev/null 2>&1 &
```

## Verify

```bash
curl -s http://localhost:9222/json/version
```

## Rules

- Logins made in this window persist in `~/.cache/chrome-cdp`. The user logs in once by hand; scripts reuse the session
- Never kill or restart a Chrome the user is using without asking
- If port 9222 is already taken by a Chrome the user started, connect to it rather than starting another
