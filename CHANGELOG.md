# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-05-11

### Added

#### Модуль 2 — Проєктування
- ADR-001: обґрунтування вибору шарової архітектури (`docs/adr/001-architecture.md`).
- Шарова структура проєкту: `api/`, `services/`, `repositories/`, `models/`.
- OpenAPI 3.0 специфікація з 13 ендпоінтами (`docs/openapi.yaml`).
- SQL-схема бази даних у 3NF: `users`, `authors`, `books`, `borrow_records` (`src/database/schema.sql`).
- Приклад порушення SRP/DIP (`src/services/dirty_code.py`) та SOLID-рефакторинг (`src/services/clean_code.py`).

#### Модуль 3 — Реалізація
- **Породжуючі патерни:**
  - Singleton для конфігурації (`src/core/config.py`).
  - Factory Method для сповіщень (`src/services/notification_factory.py`).
  - Builder для об'єктів Book (`src/models/book_builder.py`).
  - Демо-скрипт для всіх патернів (`demo/patterns_demo.py`).
- **Поведінкові та структурні патерни:**
  - Strategy для розрахунку штрафів (`src/services/penalty_strategy.py`).
  - Observer для подієвої системи (`src/events/observer.py`).
  - Decorator: `@timer`, `@log` (`src/utils/decorators.py`).
  - Facade для спрощеного інтерфейсу (`src/services/library_facade.py`).
- Ієрархія виключень з `LibraryBaseException` (`src/core/exceptions.py`).
- Структуроване JSON-логування (`src/core/logger.py`).
- Рефакторинг code smells: Magic Numbers, Long Method → Extract Function (`src/services/bad_service.py` → `good_service.py`).
- Async API з `asyncio.gather` та background task (`src/api/books_async.py`).

#### Модуль 4 — Тестування та CI/CD
- Unit-тести з `unittest.mock.MagicMock` (`tests/test_services.py`).
- Інтеграційні тести з in-memory SQLite (`tests/test_api.py`).
- TDD-демонстрація: RED → GREEN → REFACTOR для функції знижок (`tests/test_discount.py`, `src/services/discount.py`).
- `Dockerfile` (Python 3.11-slim).
- `docker-compose.yml` (сервіси `web` та `postgres`).
- `.github/workflows/ci.yml` — GitHub Actions CI (pytest, black, flake8, isort).
- `README.md` з badges, архітектурою та інструкціями.
- Звіт метрик `radon` (`docs/metrics/README.md`).

### Changed
- N/A (перший реліз).

### Deprecated
- N/A.

### Removed
- N/A.

### Fixed
- N/A.

### Security
- Dockerfile працює з непривілейованим користувачем (`appuser`).
- Паролі винесені у змінні середовища (docker-compose).
- CI перевіряє залежності за допомогою `safety`.

[Unreleased]: https://github.com/username/library-system/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/username/library-system/releases/tag/v1.0.0
