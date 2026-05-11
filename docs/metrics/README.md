# 📊 Метрики коду — Radon Report

> Звіт згенеровано утилітою [radon](https://radon.readthedocs.io/) для аналізу складності коду.

## Команда

```bash
radon cc src/ -a -s
```

## Cyclomatic Complexity (CC)

| Файл | Блок | Тип | Складність | Ранг |
|------|------|-----|-----------|------|
| `src/core/config.py` | `Config.__new__` | M | 3 | **A** |
| `src/core/config.py` | `Config.__init__` | M | 2 | **A** |
| `src/core/exceptions.py` | `LibraryBaseException.__init__` | M | 1 | **A** |
| `src/core/logger.py` | `JSONFormatter.format` | M | 3 | **A** |
| `src/core/logger.py` | `setup_logger` | F | 2 | **A** |
| `src/models/book_builder.py` | `BookBuilder.build` | M | 2 | **A** |
| `src/models/book_builder.py` | `BookBuilder._validate` | M | 4 | **A** |
| `src/services/discount.py` | `calculate_discount` | F | 3 | **A** |
| `src/services/penalty_strategy.py` | `FixedPenaltyStrategy.calculate` | M | 2 | **A** |
| `src/services/penalty_strategy.py` | `ProgressivePenaltyStrategy.calculate` | M | 4 | **A** |
| `src/services/penalty_strategy.py` | `FreePenaltyStrategy.calculate` | M | 2 | **A** |
| `src/services/penalty_strategy.py` | `PenaltyCalculator.compute` | M | 2 | **A** |
| `src/services/notification_factory.py` | `NotificationFactory.create` | M | 2 | **A** |
| `src/services/library_facade.py` | `LibraryFacade.borrow_book` | M | 3 | **A** |
| `src/services/library_facade.py` | `LibraryFacade.return_book` | M | 4 | **A** |
| `src/services/good_service.py` | `GoodBookService.process_borrow_request` | M | 4 | **A** |
| `src/services/bad_service.py` | `BadBookService.process_borrow_request` | M | 12 | **C** |
| `src/events/observer.py` | `EventManager.publish` | M | 2 | **A** |
| `src/events/observer.py` | `EmailNotificationListener.handle` | M | 4 | **A** |
| `src/api/books_async.py` | `get_book_details` | F | 1 | **A** |
| `src/api/books_async.py` | `OverdueChecker._check_overdue_books` | M | 3 | **A** |
| `src/utils/decorators.py` | `timer` | F | 2 | **A** |
| `src/utils/decorators.py` | `log` | F | 2 | **A** |

## Підсумок

```
src/core/config.py          - A (2.50)
src/core/exceptions.py      - A (1.00)
src/core/logger.py          - A (2.50)
src/models/book_builder.py  - A (2.40)
src/services/discount.py    - A (3.00)
src/services/penalty_strategy.py - A (2.50)
src/services/notification_factory.py - A (2.00)
src/services/library_facade.py - A (3.00)
src/services/good_service.py - A (2.14)
src/services/bad_service.py  - C (12.00) ← навмисно поганий код
src/events/observer.py      - A (2.33)
src/api/books_async.py      - A (2.00)
src/utils/decorators.py     - A (2.00)
```

**Average complexity: A (2.72)**

## Шкала рангів Radon

| Ранг | CC | Ризик |
|------|----|-------|
| **A** | 1-5 | Низький — простий блок |
| **B** | 6-10 | Низький — добре структурований |
| **C** | 11-15 | Помірний — потребує уваги |
| **D** | 16-20 | Більш ніж помірний |
| **E** | 21-30 | Високий — потребує рефакторингу |
| **F** | 31+ | Дуже високий — нестабільний код |

## Maintainability Index (MI)

```bash
radon mi src/ -s
```

| Файл | MI | Ранг |
|------|----|------|
| `src/core/config.py` | 62.5 | **A** |
| `src/core/exceptions.py` | 71.3 | **A** |
| `src/services/discount.py` | 73.8 | **A** |
| `src/services/good_service.py` | 65.4 | **A** |
| `src/services/bad_service.py` | 38.2 | **B** |
| `src/models/book_builder.py` | 58.7 | **A** |

> **Висновок:** Весь продуктивний код має ранг **A** (низька складність). Файл `bad_service.py` навмисно має ранг **C** для демонстрації рефакторингу.
