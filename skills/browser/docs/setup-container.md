# Setup: Docker Container

A headed Chromium on a virtual display, with CDP on port 19222 and VNC on 15900. Use it by default: it never touches the user's desktop. The ports are off Chrome's usual 9222 and VNC's 5900, so the container and a host Chrome run side by side, even on the host network.

Pre-built image on GHCR (public, no auth needed), built from `docker/` in [sideef5ect/cdp-browser](https://github.com/sideef5ect/cdp-browser):

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

On Linux this listens on every interface. Firewall ports 19222 and 15900, or use port mapping below.

### Port Mapping

Use this when host network is not available (Docker Desktop without host networking) or causes conflicts:

```bash
docker run -d \
  -p 127.0.0.1:19222:19222 \
  -p 127.0.0.1:15900:15900 \
  -v browser-chrome-profile:/app/chrome_profile \
  -v browser-webkit-profile:/app/webkit_profile \
  --shm-size=1g \
  --name browser-cdp \
  ghcr.io/sideef5ect/cdp-browser:latest
```

With port mapping, the browser reaches host services at `host.docker.internal` instead of `localhost`.

## Ports and Volumes

| Port | Env var | Service |
|------|---------|---------|
| 19222 | `CDP_PORT` | CDP, forwarded by socat to Chromium's loopback-only port `CHROME_CDP_PORT` (19223) |
| 15900 | `VNC_PORT` | VNC |

To use other ports, set the env vars and publish the same numbers, e.g. `-e CDP_PORT=29222 -p 127.0.0.1:29222:29222`.

| Volume | Container Path | Purpose |
|--------|----------------|---------|
| Chrome profile | `/app/chrome_profile` | Chromium cookies, sessions, cache |
| WebKit profile | `/app/webkit_profile` | WebKit cookies, sessions, cache |

## Verify

```bash
curl -s http://localhost:19222/json/version
```

The container takes a few seconds to start Xvfb, VNC and Chromium. `docker logs browser-cdp` ends with `Browser environment ready!` once CDP is up.

## VNC Access

Watch what the browser is doing, or log in to a site by hand once so the session is saved in the profile. Default password `changeme`; set another with `-e VNC_PASSWORD=...` on `docker run`.

```bash
open vnc://localhost:15900
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
docker build -t cdp-browser docker/
```
