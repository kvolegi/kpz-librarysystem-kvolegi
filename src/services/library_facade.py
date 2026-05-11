"""
library_facade.py — Facade патерн для спрощення інтерфейсу бібліотеки.

Патерн Facade надає уніфікований інтерфейс до складної підсистеми,
приховуючи внутрішню складність від клієнтів.
"""

from datetime import datetime, timedelta
from typing import Optional, Any

from src.services.penalty_strategy import PenaltyCalculator, PenaltyStrategy, FixedPenaltyStrategy
from src.events.observer import EventManager, Event, EventType


class LibraryFacade:
    """Фасад бібліотечної системи.

    Спрощує взаємодію з підсистемами:
    - Управління книгами
    - Управління користувачами
    - Видача/повернення книг
    - Розрахунок штрафів
    - Подієва система
    """

    def __init__(
        self,
        event_manager: Optional[EventManager] = None,
        penalty_strategy: Optional[PenaltyStrategy] = None,
    ):
        self._event_manager = event_manager or EventManager()
        self._penalty_calc = PenaltyCalculator(
            penalty_strategy or FixedPenaltyStrategy()
        )
        # In-memory сховища для демонстрації
        self._books: dict[int, dict] = {}
        self._users: dict[int, dict] = {}
        self._borrows: dict[int, dict] = {}
        self._next_book_id = 1
        self._next_user_id = 1
        self._next_borrow_id = 1

    # ── Книги ──

    def add_book(self, title: str, isbn: str, author: str, quantity: int = 1) -> int:
        """Додати книгу до бібліотеки."""
        book_id = self._next_book_id
        self._next_book_id += 1
        self._books[book_id] = {
            "id": book_id, "title": title, "isbn": isbn,
            "author": author, "quantity": quantity, "available": quantity,
        }
        self._event_manager.publish(Event(
            EventType.BOOK_ADDED,
            {"book_title": title, "quantity": quantity},
        ))
        return book_id

    def get_book(self, book_id: int) -> Optional[dict]:
        """Отримати інформацію про книгу."""
        return self._books.get(book_id)

    def search_books(self, query: str) -> list[dict]:
        """Пошук книг за назвою або автором."""
        q = query.lower()
        return [
            b for b in self._books.values()
            if q in b["title"].lower() or q in b["author"].lower()
        ]

    # ── Користувачі ──

    def register_user(self, name: str, email: str) -> int:
        """Зареєструвати користувача."""
        uid = self._next_user_id
        self._next_user_id += 1
        self._users[uid] = {"id": uid, "name": name, "email": email}
        self._event_manager.publish(Event(
            EventType.USER_REGISTERED, {"user_name": name},
        ))
        return uid

    # ── Видача / Повернення ──

    def borrow_book(self, user_id: int, book_id: int) -> Optional[int]:
        """Видати книгу користувачу (спрощений інтерфейс)."""
        book = self._books.get(book_id)
        user = self._users.get(user_id)
        if not book or not user or book["available"] <= 0:
            return None
        book["available"] -= 1
        bid = self._next_borrow_id
        self._next_borrow_id += 1
        self._borrows[bid] = {
            "id": bid, "user_id": user_id, "book_id": book_id,
            "borrow_date": datetime.now(),
            "due_date": datetime.now() + timedelta(days=14),
            "return_date": None,
        }
        self._event_manager.publish(Event(
            EventType.BOOK_BORROWED,
            {"user_name": user["name"], "book_title": book["title"],
             "remaining": book["available"]},
        ))
        return bid

    def return_book(self, borrow_id: int) -> float:
        """Повернути книгу та обчислити штраф."""
        record = self._borrows.get(borrow_id)
        if not record or record["return_date"]:
            return 0.0
        record["return_date"] = datetime.now()
        book = self._books.get(record["book_id"])
        if book:
            book["available"] += 1
        penalty = self._penalty_calc.compute(
            record["due_date"], record["return_date"]
        )
        user = self._users.get(record["user_id"])
        user_name = user["name"] if user else "Unknown"
        book_title = book["title"] if book else "Unknown"
        self._event_manager.publish(Event(
            EventType.BOOK_RETURNED,
            {"user_name": user_name, "book_title": book_title,
             "remaining": book["available"] if book else 0},
        ))
        if penalty > 0:
            self._event_manager.publish(Event(
                EventType.PENALTY_CHARGED,
                {"user_name": user_name, "amount": penalty},
            ))
        return penalty
