# cdp-browser — Developer Guide

An agent skill for driving a persistent browser over CDP with Playwright, plus a multi-arch Docker image (Xvfb, VNC, Chromium, WebKit) published to `ghcr.io/sideef5ect/cdp-browser`. Host Chrome with remote debugging is the other backend. The container serves CDP on `localhost:19222` and VNC on `15900` by default; host Chrome keeps `9222`.

## Rules

- Do NOT auto-commit unless explicitly asked.
- Never manually wrap lines in Markdown. One paragraph, list item, or table row is one line.
- This is a public repo. No personal details in files or commits: no real names, personal emails, home paths (`/Users/<name>`), hostnames, or tokens. Commits use the GitHub noreply address set in the local git config.
- `skills/browser/SKILL.md` is usage only: backend choice, ready check, Don't Steal Focus, the `background_tab()` helper, recipes, and the Docs Index. Setup and reference material goes in `skills/browser/docs/`, and every new doc gets a row in the Docs Index saying when to read it.
- The helper stays in `SKILL.md` directly after the line `Paste this helper into every script:`. `test/focus_test.py` extracts that exact code block with a regex, so renaming the line or moving the block breaks the test.
- Any change to `background_tab()` or `NO_POPUPS` is followed by a run of the focus test on macOS before it is committed.
- Examples that publish ports bind to `127.0.0.1`. CDP has no authentication and exposes every logged-in session in the profile.
- The image, `docker run` examples, and `docker/docker-compose.yaml` stay in step: the same container name (`browser-cdp`), volume names (`browser-chrome-profile`, `browser-webkit-profile`), ports, and `--shm-size=1g`.
- Container ports default to `CDP_PORT=19222` and `VNC_PORT=15900` (Chromium itself on loopback `CHROME_CDP_PORT=19223`, exposed by socat). Never move them back to 9222/5900: host network mode would collide with a host Chrome or VNC server. Host Chrome docs keep 9222.
- Playwright is pinned twice: `ARG PLAYWRIGHT_VERSION` in `docker/Dockerfile` and `playwright==` in `pyproject.toml`. Change both in one commit, run `uv lock`, rebuild, and rerun the smoke test; `scripts/check_playwright_version.py` fails CI when they differ.
- `pyproject.toml` is a dev environment only (`package = false`), never a published package. The skill must keep working without it: `SKILL.md` code is pasted into the user's own scripts.

## Dev Environment

- Python:      `uv sync` (Python from `.python-version`, 3.14); lint with `uv run ruff check . && uv run ruff format --check .`
- Build:       `docker build -t cdp-browser docker/`
- Smoke test:  run the image on spare ports (`-e CDP_PORT=29222 -p 127.0.0.1:29222:29222 --name cdp-browser-smoke`), wait for `curl -s http://127.0.0.1:29222/json/version`, connect with the helper from `SKILL.md`, screenshot a page, then `docker rm -f cdp-browser-smoke`
- Focus test:  `uv run skills/browser/test/focus_test.py` against host Chrome started per `docs/setup-host-chrome.md`, with another app in front (macOS only)
- Plugin:      `claude plugin validate .`
- VNC:         `open vnc://localhost:15900` (password `VNC_PASSWORD`, default `changeme`)

## Git

- **`master` is the production branch.** A push to `master` that touches `docker/` or the workflow builds and pushes `latest` and `sha-<commit>`.
- Releases come from release-please (`.github/workflows/release.yaml`, `release-please-config.json`, `.release-please-manifest.json`). Never bump `version` in `.claude-plugin/plugin.json`, edit `CHANGELOG.md`, or push `v*` tags by hand: the release PR does all three. Merging it tags `vX.Y.Z`, creates the GitHub release, and calls `build-image.yaml` to publish `X.Y.Z` and `X.Y`.
- `feat:` bumps minor, `fix:`/`docs:`/`chore:` bump patch, `!` or `BREAKING CHANGE:` bumps minor while `bump-major-for-breaking-change` is false. Force a version with an empty commit whose body has `Release-As: X.Y.Z`.
- The release workflow uses only `GITHUB_TOKEN`; never add a personal access token secret. The release PR is approved and merged by hand. Because it is opened with `GITHUB_TOKEN`, its checks do not run on their own; the content was already checked on `master`.
- Pull requests build both platforms and push nothing.
- Conventional Commits (`feat:`, `fix:`, `docs:`, `ci:`).

## Project Structure

| Path | Purpose |
|------|---------|
| `skills/browser/SKILL.md` | The agent skill: usage, focus rules, helper, recipes, Docs Index |
| `skills/browser/docs/` | Setup docs loaded on demand: `setup-container.md`, `setup-host-chrome.md`, `webkit.md` |
| `skills/browser/test/focus_test.py` | macOS test that the helper never raises Chrome; reads the helper from `SKILL.md` |
| `docker/` | `Dockerfile` (Ubuntu 22.04, Playwright Chromium and WebKit, Xvfb, fluxbox, x11vnc, socat) `entrypoint.sh` (start order, stale lock cleanup, shutdown) and `docker-compose.yaml` (host-network run of the published image) |
| `.claude-plugin/` | `plugin.json` (name, version) and `marketplace.json`, so `/plugin marketplace add sideef5ect/cdp-browser` installs the skill |
| `.github/workflows/build-image.yaml` | Multi-arch build (amd64, arm64), push to GHCR, prune old versions; also called by `release.yaml` with a `version` input |
| `.github/workflows/release.yaml` | release-please: release PR, `vX.Y.Z` tag, GitHub release, then the versioned image build |
| `release-please-config.json`, `.release-please-manifest.json` | release-please settings (changelog sections, `plugin.json` version as an extra file) and the last released version |
| `.github/ISSUE_TEMPLATE/`, `.github/pull_request_template.md` | Bug and feature issue forms (blank issues off, security reports routed to advisories) and the PR checklist |
| `.github/dependabot.yml` | Weekly update PRs for actions (`ci:` prefix) and the `docker/` base image (`build:` prefix); Playwright stays a manual bump |
| `CONTRIBUTING.md`, `SECURITY.md` | Human contributor guide (keep its commands in step with Dev Environment here) and the private vulnerability reporting policy |
| `pyproject.toml`, `uv.lock`, `.python-version` | uv dev environment: the pinned Playwright client and ruff, Python 3.14 locally, `>=3.11` supported |
| `scripts/check_playwright_version.py` | Fails when the `pyproject.toml` and Dockerfile Playwright pins differ; run by `lint.yaml` |
| `.github/workflows/lint.yaml` | On push and PR: `uv sync --locked`, the version check, ruff lint and format |
| `docs/assets/` | README diagrams (each SVG beside the Python generator that draws it) and the two backend screenshots |

## Coding Style

- No emoji in code, docs, or commits.
- Docs are GitHub-flavoured Markdown and must read correctly on github.com: relative links, no Obsidian wikilinks or callouts other than GitHub alerts (`> [!WARNING]`).
- Diagrams are SVG files in `docs/assets/` with their generator `.py` beside them; regenerate rather than hand-edit the SVG. Solid background, no external fonts or scripts.
- Python examples use the sync Playwright API and connect with `connect_over_cdp()`; never `launch()` for the Chromium backend.
- Shell in `entrypoint.sh` stays `bash` with `set -e`; each started process is added to `PIDS` so the trap stops it.

## Bash Tool Usage

- Every Bash command starts with a `# comment` first line.
- Run long jobs (image builds, CI watches) in the background; never pipe output through `tail`/`head`/`grep`. Read the full output file.
