# Ubuntu with VNC + Chromium CDP (via Playwright)
# Build: docker build -t cdp-browser docker/
# Run:   docker run -d -p 127.0.0.1:19222:19222 -p 127.0.0.1:15900:15900 --name browser-cdp cdp-browser
# CDP:   localhost:19222 | VNC: localhost:15900

# Pinned by digest for reproducible builds; Dependabot bumps the digest weekly.
# Move to a newer Ubuntu LTS by hand, with a Playwright version whose install-deps supports it.
FROM ubuntu:22.04@sha256:0a9887931b0e38af2e3487ed39e29436b0535c4f3f52e57745baaf79d1898956

# Pinned so the Chromium build only changes when this is bumped
ARG PLAYWRIGHT_VERSION=1.64.1

ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:99
ENV VNC_PASSWORD=changeme

# Off the usual 9222/5900, so host network mode never collides with a host Chrome
# or a host VNC server. CHROME_CDP_PORT is Chromium's loopback-only port behind socat.
ENV CDP_PORT=19222
ENV CHROME_CDP_PORT=19223
ENV VNC_PORT=15900

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget curl ca-certificates \
    x11vnc xvfb fluxbox \
    python3 python3-pip \
    fonts-liberation fonts-noto-cjk \
    libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 \
    libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 \
    libnspr4 libnss3 libxcomposite1 libxdamage1 libxrandr2 \
    socat \
    xdotool scrot \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright and browsers
# Note: Chromium on ARM64 does NOT support H.264 (proprietary codec)
#       WebKit on ARM64 DOES support H.264
RUN pip3 install "playwright==${PLAYWRIGHT_VERSION}" && playwright install-deps && playwright install chromium webkit

RUN mkdir -p /app/chrome_profile /app/webkit_profile

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Chrome profile for CDP mode, WebKit profile for Playwright persistent context
VOLUME ["/app/chrome_profile", "/app/webkit_profile"]

EXPOSE 15900 19222

CMD ["/entrypoint.sh"]
