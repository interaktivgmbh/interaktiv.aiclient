# Changelog

<!--
   You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst
-->

<!-- towncrier release notes start -->

## 3.0.0 (2026-10-07)


### Breaking changes:

- Replace `langchain-openai` with the `openai` client. Prompts must be OpenAI-style message dicts. @arybakov05 


### New features:

- Added proper uninstall profile. @arybakov05 
- Raise the default `max_concurrent_requests` from 5 to 10. @arybakov05 
- Support Plone 6.2 and Python 3.14. @arybakov05 
- `call` and `batch` pass keyword arguments on to the request. @arybakov05 


### Bug fixes:

- Fix prompts being sent twice due to stale connections. @arybakov05 

## 2.0.1 (2026-04-27)


### Bug fixes:

- Pin `langchain-openai` to version `0.3.35` for compatibility with `typing_extensions<4.13` as requested by Plone `6.0.15` constraints. @arybakov05
- Fixed tests for `helper` file. @arybakov05

## 2.0.0 (2026-02-13)


### Breaking changes:

- Switch to implicit namespaces. @arybakov05

## 1.1.1 (2026-02-02)


### New features:

- Added semaphore to limit concurrent requests in a batch. @arybakov05
- Added caching for model vocabulary. @arybakov05
- Added a session manager that keeps a single event loop alive for a shared connection pool. @arybakov05


### Bug fixes:

- Add retry and timeout for models API call. @arybakov05

## 1.1.0 (2026-01-27)


### New features:

- Added support for batching. @szuev00 @arybakov05 [#4](https://github.com/interaktivgmbh/interaktiv.aiclient/issues/4)


### Bug fixes:

- Avoid unreliable Hyperbolic provider for mistralai models @szuev00 [#4](https://github.com/interaktivgmbh/interaktiv.aiclient/issues/4)


### Internal:

- Added retries and timeout as safety mechanisms for requests. @szuev00 @arybakov05 [#4](https://github.com/interaktivgmbh/interaktiv.aiclient/issues/4)

## 1.0.0 (2025-12-15)


### Internal:

- Initial release. @arybakov05 [#1](https://github.com/interaktivgmbh/interaktiv.aiclient/issues/1)
