# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [2026-01-11] Fixed Telegram bot async lifecycle (PTB v22)
- Start `Application` before polling to ensure command handlers are active.
- Use async polling via `application.updater.start_polling(...)` within the running event loop.
- Clean shutdown sequence: stop updater, stop application, shutdown.
- Resolves `RuntimeError: This event loop is already running` when running under `asyncio.run(...)`.
- Minor cleanup in `requirements.txt`.

### Impact
- Commands like `/help`, `/start`, `/status` respond reliably.
- Background polling runs concurrently without blocking the main event loop.
- Graceful shutdown avoids dangling tasks.
