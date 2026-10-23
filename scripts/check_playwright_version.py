"""Fail if the Playwright pin in pyproject.toml differs from ARG PLAYWRIGHT_VERSION in docker/Dockerfile."""

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

deps = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["dependencies"]
pinned = next((d.split("==", 1)[1] for d in deps if d.startswith("playwright==")), None)
match = re.search(r"^ARG PLAYWRIGHT_VERSION=(\S+)", (ROOT / "docker/Dockerfile").read_text(), re.M)
image = match.group(1) if match else None

if pinned is None or image is None or pinned != image:
    print(f"Playwright version mismatch: pyproject.toml={pinned} docker/Dockerfile={image}")
    sys.exit(1)
print(f"Playwright {pinned} in both pyproject.toml and docker/Dockerfile")
