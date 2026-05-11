"""
observer.py — Observer патерн для подієвої системи бібліотеки.

Патерн Observer визначає залежність «один-до-багатьох» між об'єктами,
так що при зміні стану одного об'єкта всі залежні сповіщуються.

Події:
  - book_borrowed: Книга видана
  - book_returned: Книга повернена
  - book_added: Нова книга додана
  - book_overdue: Книга прострочена
  - user_registered: Новий користувач зареєстрований
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable
from enum import Enum


class EventType(str, Enum):
    """Типи подій у бібліотечній системі."""
    BOOK_BORROWED = "book_borrowed"
    BOOK_RETURNED = "book_returned"
    BOOK_ADDED = "book_added"
    BOOK_OVERDUE = "book_overdue"
    USER_REGISTERED = "user_registered"
    PENALTY_CHARGED = "penalty_charged"


@dataclass
class Event:
    """Об'єкт події."""
    type: EventType
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        return f"Event({self.type.value}, data={self.data}, at={self.timestamp:%H:%M:%S})"


class EventListener(ABC):
    """Абстрактний спостерігач (Observer)."""

    @abstractmethod
    def handle(self, event: Event) -> None:
        """Обробити подію.

        Args:
            event: Об'єкт події.
        """
        ...


# =============================================================================
# Конкретні спостерігачі
# =============================================================================

class LoggingListener(EventListener):
    """Записує всі події в лог."""

    def __init__(self, log_file: str = "library_events.log"):
        self._log_file = log_file

    def handle(self, event: Event) -> None:
        log_msg = f"[{event.timestamp:%Y-%m-%d %H:%M:%S}] {event.type.value}: {event.data}"
        print(f"📝 [LOG] {log_msg}")


class EmailNotificationListener(EventListener):
    """Надсилає email-сповіщення при певних подіях."""

    def handle(self, event: Event) -> None:
        if event.type == EventType.BOOK_BORROWED:
            user = event.data.get("user_name", "Unknown")
            book = event.data.get("book_title", "Unknown")
            print(f"📧 [EMAIL] → {user}: Ви отримали книгу «{book}»")

        elif event.type == EventType.BOOK_OVERDUE:
            user = event.data.get("user_name", "Unknown")
            book = event.data.get("book_title", "Unknown")
            days = event.data.get("days_overdue", 0)
            print(f"📧 [EMAIL] → {user}: Книга «{book}» прострочена на {days} днів!")

        elif event.type == EventType.PENALTY_CHARGED:
            user = event.data.get("user_name", "Unknown")
            amount = event.data.get("amount", 0)
            print(f"📧 [EMAIL] → {user}: Нараховано штраф {amount:.2f} грн")


class StatisticsListener(EventListener):
    """Збирає статистику подій."""

    def __init__(self):
        self._stats: dict[str, int] = {}

    def handle(self, event: Event) -> None:
        key = event.type.value
        self._stats[key] = self._stats.get(key, 0) + 1
        print(f"📊 [STATS] {key}: {self._stats[key]} (всього подій)")

    def get_stats(self) -> dict[str, int]:
        """Отримати зібрану статистику."""
        return self._stats.copy()


class InventoryListener(EventListener):
    """Відстежує зміни інвентарю."""

    def handle(self, event: Event) -> None:
        if event.type == EventType.BOOK_BORROWED:
            book = event.data.get("book_title", "Unknown")
            remaining = event.data.get("remaining", "?")
            print(f"📦 [INVENTORY] «{book}» — залишилось {remaining} шт.")

        elif event.type == EventType.BOOK_RETURNED:
            book = event.data.get("book_title", "Unknown")
            remaining = event.data.get("remaining", "?")
            print(f"📦 [INVENTORY] «{book}» повернена — тепер {remaining} шт.")

        elif event.type == EventType.BOOK_ADDED:
            book = event.data.get("book_title", "Unknown")
            qty = event.data.get("quantity", 0)
            print(f"📦 [INVENTORY] Нова книга «{book}» — {qty} шт.")


# =============================================================================
# Менеджер подій (Event Manager / Subject)
# =============================================================================

class EventManager:
    """Менеджер подій — Subject у патерні Observer.

    Підтримує:
      - Підписку на конкретні типи подій.
      - Відписку від подій.
      - Публікацію подій усім підписникам.

    Використання:
        manager = EventManager()
        manager.subscribe(EventType.BOOK_BORROWED, LoggingListener())
        manager.publish(Event(EventType.BOOK_BORROWED, {"book_title": "Кобзар"}))
    """

    def __init__(self):
        self._listeners: dict[EventType, list[EventListener]] = {}

    def subscribe(self, event_type: EventType, listener: EventListener) -> None:
        """Підписатися на подію.

        Args:
            event_type: Тип події.
            listener: Спостерігач.
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)

    def unsubscribe(self, event_type: EventType, listener: EventListener) -> None:
        """Відписатися від події.

        Args:
            event_type: Тип події.
            listener: Спостерігач для видалення.
        """
        if event_type in self._listeners:
            self._listeners[event_type] = [
                l for l in self._listeners[event_type] if l is not listener
            ]

    def publish(self, event: Event) -> None:
        """Опублікувати подію всім підписникам.

        Args:
            event: Об'єкт події.
        """
        listeners = self._listeners.get(event.type, [])
        for listener in listeners:
            listener.handle(event)

    def subscriber_count(self, event_type: EventType) -> int:
        """Кількість підписників для типу події."""
        return len(self._listeners.get(event_type, []))
