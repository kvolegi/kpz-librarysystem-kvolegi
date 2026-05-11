"""
books_async.py — Async API ендпоінти для книг.

Використовує asyncio.gather для паралельного виконання задач
та background task для фонових операцій.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class BookDTO:
    """DTO для книги."""
    id: int
    title: str
    author: str
    available: bool


# =============================================================================
# Імітація async-операцій (заміна реальних I/O)
# =============================================================================

async def _fetch_book_from_db(book_id: int) -> dict:
    """Імітація запиту до БД."""
    await asyncio.sleep(0.1)  # Імітація I/O
    return {"id": book_id, "title": f"Книга #{book_id}", "author": "Автор", "available": True}


async def _fetch_book_reviews(book_id: int) -> list[dict]:
    """Імітація запиту відгуків."""
    await asyncio.sleep(0.15)
    return [
        {"user": "reader1", "rating": 5, "text": "Чудова книга!"},
        {"user": "reader2", "rating": 4, "text": "Рекомендую."},
    ]


async def _fetch_book_availability(book_id: int) -> dict:
    """Імітація перевірки наявності в інших бібліотеках."""
    await asyncio.sleep(0.12)
    return {"library_count": 3, "nearest": "Бібліотека ім. Лесі Українки"}


async def _fetch_author_info(author_id: int) -> dict:
    """Імітація запиту інформації про автора."""
    await asyncio.sleep(0.08)
    return {"id": author_id, "name": "Тарас Шевченко", "books_count": 42}


# =============================================================================
# Головний async-ендпоінт з asyncio.gather
# =============================================================================

async def get_book_details(book_id: int) -> dict[str, Any]:
    """Отримати повну інформацію про книгу (паралельні запити).

    Використовує asyncio.gather для одночасного виконання 4 задач:
    1. Дані книги з БД
    2. Відгуки
    3. Наявність в інших бібліотеках
    4. Інформація про автора
    """
    book_data, reviews, availability, author_info = await asyncio.gather(
        _fetch_book_from_db(book_id),
        _fetch_book_reviews(book_id),
        _fetch_book_availability(book_id),
        _fetch_author_info(1),
    )

    return {
        "book": book_data,
        "reviews": reviews,
        "reviews_count": len(reviews),
        "availability": availability,
        "author": author_info,
        "fetched_at": datetime.now().isoformat(),
    }


async def search_books_parallel(queries: list[str]) -> list[dict]:
    """Паралельний пошук книг за кількома запитами."""

    async def _search_single(query: str) -> dict:
        await asyncio.sleep(0.1)
        return {"query": query, "results_count": len(query) * 2, "results": []}

    tasks = [_search_single(q) for q in queries]
    return await asyncio.gather(*tasks)


async def batch_update_books(updates: list[dict]) -> list[dict]:
    """Паралельне оновлення кількох книг."""

    async def _update_single(update: dict) -> dict:
        await asyncio.sleep(0.05)
        return {"book_id": update["id"], "status": "updated"}

    tasks = [_update_single(u) for u in updates]
    return await asyncio.gather(*tasks)


# =============================================================================
# Background Task — фонова задача
# =============================================================================

class OverdueChecker:
    """Фонова задача для перевірки прострочених книг."""

    def __init__(self, check_interval: float = 60.0):
        self._interval = check_interval
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._checks_performed = 0

    async def _check_overdue_books(self) -> None:
        """Основний цикл фонової задачі."""
        self._running = True
        print("🔄 [Background] Фонова задача перевірки прострочень запущена")
        while self._running:
            try:
                self._checks_performed += 1
                overdue_count = await self._scan_for_overdue()
                print(
                    f"🔄 [Background] Перевірка #{self._checks_performed}: "
                    f"знайдено {overdue_count} прострочених книг"
                )
                await asyncio.sleep(self._interval)
            except asyncio.CancelledError:
                print("🔄 [Background] Фонова задача зупинена")
                break

    async def _scan_for_overdue(self) -> int:
        """Імітація сканування БД на прострочені книги."""
        await asyncio.sleep(0.05)
        return self._checks_performed % 3  # Імітація різних результатів

    def start(self) -> None:
        """Запустити фонову задачу."""
        if not self._task or self._task.done():
            self._task = asyncio.create_task(self._check_overdue_books())

    def stop(self) -> None:
        """Зупинити фонову задачу."""
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()

    @property
    def is_running(self) -> bool:
        return self._running


# =============================================================================
# Демонстрація
# =============================================================================

async def main():
    """Демонстрація async-функціоналу."""
    print("=" * 50)
    print("  📚 Async Books API — Демонстрація")
    print("=" * 50)

    # 1. Паралельне отримання деталей книги
    print("\n--- asyncio.gather: деталі книги ---")
    import time
    start = time.perf_counter()
    details = await get_book_details(42)
    elapsed = time.perf_counter() - start
    print(f"Книга: {details['book']['title']}")
    print(f"Відгуків: {details['reviews_count']}")
    print(f"Доступна в: {details['availability']['library_count']} бібліотеках")
    print(f"⏱️  Час: {elapsed:.3f} сек. (замість ~0.45 послідовно)")

    # 2. Паралельний пошук
    print("\n--- asyncio.gather: паралельний пошук ---")
    start = time.perf_counter()
    results = await search_books_parallel(["Python", "Алгоритми", "Кобзар"])
    elapsed = time.perf_counter() - start
    for r in results:
        print(f"  Запит '{r['query']}': {r['results_count']} результатів")
    print(f"⏱️  Час: {elapsed:.3f} сек. (замість ~0.30 послідовно)")

    # 3. Background task
    print("\n--- Background Task: перевірка прострочень ---")
    checker = OverdueChecker(check_interval=0.5)
    checker.start()
    await asyncio.sleep(1.5)  # Даємо фоновій задачі попрацювати
    checker.stop()
    await asyncio.sleep(0.1)
    print(f"Фонова задача виконала {checker._checks_performed} перевірок")

    print("\n✅ Async-демонстрація завершена!")


if __name__ == "__main__":
    asyncio.run(main())
