# Setup: Docker Container

A headed Chromium on a virtual display, with CDP on port 9222 and VNC on 5900. Use it by default: it never touches the user's desktop.

Pre-built image on GHCR (public, no auth needed), built from `image/` in [sideef5ect/cdp-browser](https://github.com/sideef5ect/cdp-browser):

```text
ghcr.io/sideef5ect/cdp-browser:latest
```

## Start

### Host Network (Recommended)

The browser can reach services on the host's `localhost`, such as dev servers:

```bash
docker run -d \
  --network host \
  -v browser-chrome-profile:/app/chrome_profile \
  -v browser-webkit-profile:/app/webkit_profile \
  --shm-size=1g \
  --name browser-cdp \
  ghcr.io/sideef5ect/cdp-browser:latest
```

On Linux this listens on every interface. Firewall port 9222, or use port mapping below.

### Port Mapping

Use this when host network is not available (Docker Desktop without host networking) or causes conflicts:

```bash
docker run -d \
  -p 127.0.0.1:9222:9222 \
  -p 127.0.0.1:15900:5900 \
  -v browser-chrome-profile:/app/chrome_profile \
  -v browser-webkit-profile:/app/webkit_profile \
  --shm-size=1g \
  --name browser-cdp \
  ghcr.io/sideef5ect/cdp-browser:latest
```

With port mapping, the browser reaches host services at `host.docker.internal` instead of `localhost`.

## Ports and Volumes

| Port | Service | Access |
|------|---------|--------|
| 9222 | CDP | `localhost:9222` |
| 5900 | VNC | `localhost:5900` (host network) / `localhost:15900` (port mapping) |

| Volume | Container Path | Purpose |
|--------|----------------|---------|
| Chrome profile | `/app/chrome_profile` | Chromium cookies, sessions, cache |
| WebKit profile | `/app/webkit_profile` | WebKit cookies, sessions, cache |

## Verify

```bash
curl -s http://localhost:9222/json/version
```

The container takes a few seconds to start Xvfb, VNC and Chromium. `docker logs browser-cdp` ends with `Browser environment ready!` once CDP is up.

## VNC Access

Watch what the browser is doing, or log in to a site by hand once so the session is saved in the profile. Default password `changeme`; set another with `-e VNC_PASSWORD=...` on `docker run`.

```bash
open vnc://localhost:5900     # host network
open vnc://localhost:15900    # port mapping
```

## Container Management

```bash
# Status
docker ps -f name=browser-cdp

# Stop / Start / Restart
docker stop browser-cdp
docker start browser-cdp
docker restart browser-cdp

# Remove
docker rm -f browser-cdp

# Fresh start (remove container and volumes, which logs out of every site)
docker rm -f browser-cdp && docker volume rm browser-chrome-profile browser-webkit-profile
```

## Build Locally

```bash
docker build -t cdp-browser image/
```
