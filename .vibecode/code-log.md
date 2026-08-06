# Code Log

## 2026-08-06: WS-02

- Reconciled schema names with the current SQLAlchemy models and added real ORM serialization tests.
- Replaced persistent/stateful tests with per-test in-memory SQLite fixtures and dependency overrides.
- Replaced mock Contact, Conversation, and Message routers with authenticated implementations.
- Added typed EventBus and FastAPI lifespan dispatcher.
- Added WebSocket persistence/broadcast path and browser reconnect hook.
- Fixed JWT subject decoding to convert the token `sub` string to UUID before repository lookup.
- Added REST, service, EventBus, WebSocket, and WS-01 integration tests.

Verification recorded in `results-ws02.md`.
