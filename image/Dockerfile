# Ubuntu with VNC + Chromium CDP (via Playwright)
# Build: docker build -t cdp-browser image/
# Run:   docker run -d -p 9222:9222 --name browser-cdp cdp-browser
# CDP:   localhost:9222 | VNC: 5900

FROM ubuntu:22.04

# Pinned so the Chromium build only changes when this is bumped
ARG PLAYWRIGHT_VERSION=1.64.1

ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:99
ENV VNC_PASSWORD=changeme

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

EXPOSE 5900 9222

CMD ["/entrypoint.sh"]
