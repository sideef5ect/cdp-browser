# Security Policy

CDP gives whoever can reach the port full control of the browser, including every logged-in session in its profile. The image ships with no CDP authentication, so treat the endpoint like a root shell into your browser.

## Supported Versions

| Version | Supported |
|---|---|
| Latest `1.x` release | Yes |
| Older releases | No; upgrade to the latest image tag |

## Reporting a Vulnerability

Report privately through [GitHub Security Advisories](https://github.com/sideef5ect/cdp-browser/security/advisories/new). Do not open a public issue for a vulnerability.

Include the image tag or commit, how the container was run (`docker run` flags or Compose file), and steps to reproduce. You can expect a first reply within 7 days. Once a fix is released, the advisory is published with credit unless you ask otherwise.

## In Scope

- The Docker image: `docker/Dockerfile`, `docker/entrypoint.sh`, and the default ports, binds, and passwords they set
- The skill: code in `skills/browser/SKILL.md` that agents paste and run, such as `background_tab()` and `NO_POPUPS`
- The release and build workflows in `.github/workflows/`

## Out of Scope

- Exposure caused by publishing CDP or VNC on a public interface against the documented advice (bind to `127.0.0.1`, change `VNC_PASSWORD`)
- Vulnerabilities in Chromium, WebKit, or Playwright themselves; report those upstream. A release that bumps the pinned version is welcome
