## What and Why

<!-- What this changes and the problem it solves. Link the issue: Closes #123 -->

## Checks

- [ ] The pull request title follows Conventional Commits (`feat:`, `fix:`, `docs:`, ...)
- [ ] Image changes: built and smoke-tested (`curl /json/version`, a page loaded over CDP)
- [ ] Helper changes (`background_tab()`, `NO_POPUPS`): focus test passed on macOS
- [ ] Ports, container and volume names still match across the Dockerfile, README, docs, and `docker/docker-compose.yaml`
- [ ] Docs updated; new skill docs have a row in the `SKILL.md` Docs Index
