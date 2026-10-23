# Contributing

Thanks for helping. Bug reports, docs fixes, and pull requests are all welcome.

## Before You Start

- For anything larger than a small fix, open an issue first so the approach can be agreed before you write code
- Security problems go through [SECURITY.md](SECURITY.md), not public issues

## Development Setup

Requirements: Docker with Buildx for the image, [uv](https://docs.astral.sh/uv/) for the Python scripts, and macOS with Google Chrome for the focus test.

Set up the Python environment once. uv reads `.python-version` (3.14) and installs the Playwright client pinned in `pyproject.toml`, the same version as the image:

```bash
uv sync
uv run ruff check . && uv run ruff format --check .
```

Build the image and smoke-test it on spare ports, so it does not clash with a container you already run:

```bash
docker build -t cdp-browser:dev docker/
docker run -d --rm -e CDP_PORT=29222 -p 127.0.0.1:29222:29222 --shm-size=1g --name cdp-browser-dev cdp-browser:dev
curl -s http://127.0.0.1:29222/json/version
docker rm -f cdp-browser-dev
```

Building on a Linux host is the closest match to CI. To check both platforms, use `docker buildx build --platform linux/amd64,linux/arm64 docker/`.

## Changing the Skill

- `skills/browser/SKILL.md` holds usage only. Setup and reference material goes in `skills/browser/docs/`, with a row in the Docs Index saying when to read it
- The `background_tab()` helper must stay directly after the line `Paste this helper into every script:`, because the focus test extracts it from there
- After any change to `background_tab()` or `NO_POPUPS`, run the focus test on macOS with host Chrome started as in [setup-host-chrome.md](skills/browser/docs/setup-host-chrome.md) and another app in front:

```bash
uv run skills/browser/test/focus_test.py
```

- To bump Playwright, change `pyproject.toml` and `ARG PLAYWRIGHT_VERSION` in `docker/Dockerfile` together, run `uv lock`, and rebuild; CI fails if the two differ
- Validate the plugin manifest with `claude plugin validate .`

## Commits and Pull Requests

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/), because [release-please](https://github.com/googleapis/release-please-action) reads them to pick the next version and write `CHANGELOG.md`:

| Prefix | Use for | Release |
|---|---|---|
| `feat:` | New behaviour in the image or skill | Minor |
| `fix:` | Bug fixes | Patch |
| `docs:`, `chore:`, `ci:`, `build:` | Docs, maintenance, workflows, image build | Patch |

- Branch from `master` and open the pull request against `master`
- Keep a pull request to one change; CI builds the image for both platforms and must pass
- Do not bump versions, edit `CHANGELOG.md`, or push tags; the release PR does that
- Port defaults (`19222` CDP, `15900` VNC) and the container and volume names stay in step across the Dockerfile, the README, the docs, and `docker/docker-compose.yaml`

## License

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE).
