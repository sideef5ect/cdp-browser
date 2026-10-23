# Changelog

## [1.0.2](https://github.com/sideef5ect/cdp-browser/compare/v1.0.1...v1.0.2) (2026-10-23)


### Bug Fixes

* **ci:** tag the image from the resolved commit, not a detached HEAD ([406bcf3](https://github.com/sideef5ect/cdp-browser/commit/406bcf3d8a6027aae6b65554cb62325642445865))


### Documentation

* drop the License section from the README ([9569ba1](https://github.com/sideef5ect/cdp-browser/commit/9569ba1a15a4a054ec4bd157a9749b6174ba72d6))
* refresh the license badge and host Chrome screenshot ([a6a4088](https://github.com/sideef5ect/cdp-browser/commit/a6a4088ae757ebd9606f6e3c169df99fe4bbd314))


### Continuous Integration

* remove the lint workflow and Python Dependabot updates ([e242e52](https://github.com/sideef5ect/cdp-browser/commit/e242e52a96186ca94559460ae9cf511b2367d758))

## [1.0.1](https://github.com/sideef5ect/cdp-browser/compare/v1.0.0...v1.0.1) (2026-10-23)


### Build System

* pin the ubuntu base image by digest ([67ba69e](https://github.com/sideef5ect/cdp-browser/commit/67ba69e731cdc10e178f11f278749b33ebd366ad))


### Continuous Integration

* build the image from its own workflow after a release tag ([e46f835](https://github.com/sideef5ect/cdp-browser/commit/e46f8356eacc9970049eb2666f92a27272d99fd7))
* bump the actions group across 1 directory with 8 updates ([#3](https://github.com/sideef5ect/cdp-browser/issues/3)) ([0b4a5fb](https://github.com/sideef5ect/cdp-browser/commit/0b4a5fbc6aa99adee91235bb4022e046811e1256))

## 1.0.0 (2026-10-23)


### Features

* **docker:** move image to docker/ and use ports 19222/15900 ([20c1d2a](https://github.com/sideef5ect/cdp-browser/commit/20c1d2a7b7f8f28a0dc8644ce8266ddf18a5d374))
* initial release of cdp-browser skill and image ([ecb7657](https://github.com/sideef5ect/cdp-browser/commit/ecb76574d2722f8fc821eb9ef07c061d0a7959c8))


### Documentation

* update README and skill docs for new ports ([2abff87](https://github.com/sideef5ect/cdp-browser/commit/2abff87b167c3a5eca00908681dfddee8937d61b))


### Miscellaneous

* add contributing guide, security policy and templates ([3925608](https://github.com/sideef5ect/cdp-browser/commit/3925608b9764d75eb98102f2327d0e26da1fca70))
* release 1.0.0 ([65950d7](https://github.com/sideef5ect/cdp-browser/commit/65950d73c592504f2541f9d731b0daff5924fff5))


### Build System

* add uv project, playwright version check and lint ([b94e714](https://github.com/sideef5ect/cdp-browser/commit/b94e714e13908433b9a0ca0175573a1eac5272ba))


### Continuous Integration

* add release-please and rework image build ([0623833](https://github.com/sideef5ect/cdp-browser/commit/062383341737f56e454495bf3961021a40746ed3))
* release with GITHUB_TOKEN only and manual PR approval ([6a24fdb](https://github.com/sideef5ect/cdp-browser/commit/6a24fdb0e1fb756d3378082d6dff0cc715415d65))
