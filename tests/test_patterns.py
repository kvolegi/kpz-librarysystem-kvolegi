"""
test_patterns.py — Додаткові тести для підвищення покриття.

Тестує: Facade, NotificationFactory, Decorators, Logger, Observer listeners.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

# ── Facade ──
from src.services.library_facade import LibraryFacade
from src.events.observer import (
    EventManager, Event, EventType,
    LoggingListener, EmailNotificationListener,
    StatisticsListener, InventoryListener,
)


class TestLibraryFacade:
    """Тести Facade патерну."""

    def test_add_book(self):
        facade = LibraryFacade()
        book_id = facade.add_book("Кобзар", "978", "Шевченко", 5)
        assert book_id == 1

    def test_get_book(self):
        facade = LibraryFacade()
        facade.add_book("Кобзар", "978", "Шевченко", 5)
        book = facade.get_book(1)
        assert book["title"] == "Кобзар"

    def test_get_nonexistent_book(self):
        facade = LibraryFacade()
        assert facade.get_book(999) is None

    def test_search_books(self):
        facade = LibraryFacade()
        facade.add_book("Кобзар", "978", "Шевченко", 5)
        facade.add_book("Лісова пісня", "979", "Українка", 3)
        results = facade.search_books("Кобзар")
        assert len(results) == 1

    def test_register_user(self):
        facade = LibraryFacade()
        uid = facade.register_user("Іван", "ivan@mail.com")
        assert uid == 1

    def test_borrow_book(self):
        facade = LibraryFacade()
        facade.add_book("Кобзар", "978", "Шевченко", 5)
        facade.register_user("Іван", "ivan@mail.com")
        borrow_id = facade.borrow_book(1, 1)
        assert borrow_id == 1
        # Кількість зменшилась
        book = facade.get_book(1)
        assert book["available"] == 4

    def test_borrow_unavailable_book(self):
        facade = LibraryFacade()
        facade.add_book("Рідкісна", "978", "Автор", 0)
        facade.register_user("Іван", "ivan@mail.com")
        assert facade.borrow_book(1, 1) is None

    def test_borrow_nonexistent_user(self):
        facade = LibraryFacade()
        facade.add_book("Книга", "978", "Автор", 1)
        assert facade.borrow_book(999, 1) is None

    def test_return_book(self):
        facade = LibraryFacade()
        facade.add_book("Кобзар", "978", "Шевченко", 5)
        facade.register_user("Іван", "ivan@mail.com")
        borrow_id = facade.borrow_book(1, 1)
        penalty = facade.return_book(borrow_id)
        assert penalty == 0.0
        book = facade.get_book(1)
        assert book["available"] == 5

    def test_return_nonexistent_record(self):
        facade = LibraryFacade()
        assert facade.return_book(999) == 0.0


# ── Notification Factory ──
from src.services.notification_factory import (
    NotificationFactory, Notification,
    EmailNotificationSender, SMSNotificationSender,
    PushNotificationSender, ConsoleNotificationSender,
)


class TestNotificationFactory:
    """Тести Factory Method."""

    def test_create_email(self):
        sender = NotificationFactory.create("email")
        assert sender.get_type() == "email"

    def test_create_sms(self):
        sender = NotificationFactory.create("sms")
        assert sender.get_type() == "sms"

    def test_create_push(self):
        sender = NotificationFactory.create("push")
        assert sender.get_type() == "push"

    def test_create_console(self):
        sender = NotificationFactory.create("console")
        assert sender.get_type() == "console"

    def test_create_unknown_raises(self):
        with pytest.raises(ValueError, match="Невідомий тип"):
            NotificationFactory.create("telegram")

    def test_available_types(self):
        types = NotificationFactory.available_types()
        assert "email" in types
        assert "sms" in types

    def test_send_email(self):
        sender = EmailNotificationSender()
        notification = Notification("to@test.com", "Test", "Body")
        result = asyncio.get_event_loop().run_until_complete(sender.send(notification))
        assert result is True
        assert notification.status == "sent"

    def test_send_sms(self):
        sender = SMSNotificationSender()
        notification = Notification("to@test.com", "Test", "Body")
        result = asyncio.get_event_loop().run_until_complete(sender.send(notification))
        assert result is True

    def test_send_push(self):
        sender = PushNotificationSender()
        notification = Notification("to@test.com", "Test", "Body")
        result = asyncio.get_event_loop().run_until_complete(sender.send(notification))
        assert result is True

    def test_send_console(self):
        sender = ConsoleNotificationSender()
        notification = Notification("to@test.com", "Test", "Body")
        result = asyncio.get_event_loop().run_until_complete(sender.send(notification))
        assert result is True


# ── Observer Listeners ──

class TestObserverListeners:
    """Тести конкретних спостерігачів."""

    def test_logging_listener(self, capsys):
        listener = LoggingListener()
        event = Event(EventType.BOOK_ADDED, {"title": "Test"})
        listener.handle(event)
        captured = capsys.readouterr()
        assert "LOG" in captured.out

    def test_email_listener_borrowed(self, capsys):
        listener = EmailNotificationListener()
        event = Event(EventType.BOOK_BORROWED, {"user_name": "Іван", "book_title": "Кобзар"})
        listener.handle(event)
        captured = capsys.readouterr()
        assert "Іван" in captured.out

    def test_email_listener_overdue(self, capsys):
        listener = EmailNotificationListener()
        event = Event(EventType.BOOK_OVERDUE, {"user_name": "Іван", "book_title": "Кобзар", "days_overdue": 5})
        listener.handle(event)
        captured = capsys.readouterr()
        assert "прострочена" in captured.out

    def test_email_listener_penalty(self, capsys):
        listener = EmailNotificationListener()
        event = Event(EventType.PENALTY_CHARGED, {"user_name": "Іван", "amount": 55.0})
        listener.handle(event)
        captured = capsys.readouterr()
        assert "штраф" in captured.out

    def test_statistics_listener(self):
        listener = StatisticsListener()
        listener.handle(Event(EventType.BOOK_ADDED))
        listener.handle(Event(EventType.BOOK_ADDED))
        stats = listener.get_stats()
        assert stats["book_added"] == 2

    def test_inventory_listener_added(self, capsys):
        listener = InventoryListener()
        event = Event(EventType.BOOK_ADDED, {"book_title": "Кобзар", "quantity": 5})
        listener.handle(event)
        captured = capsys.readouterr()
        assert "Кобзар" in captured.out

    def test_inventory_listener_borrowed(self, capsys):
        listener = InventoryListener()
        event = Event(EventType.BOOK_BORROWED, {"book_title": "Кобзар", "remaining": 4})
        listener.handle(event)
        captured = capsys.readouterr()
        assert "4" in captured.out

    def test_inventory_listener_returned(self, capsys):
        listener = InventoryListener()
        event = Event(EventType.BOOK_RETURNED, {"book_title": "Кобзар", "remaining": 5})
        listener.handle(event)
        captured = capsys.readouterr()
        assert "повернена" in captured.out


# ── Decorators ──
from src.utils.decorators import timer, log


class TestDecorators:
    """Тести декораторів."""

    def test_timer_sync(self, capsys):
        @timer
        def slow_func():
            return 42
        result = slow_func()
        assert result == 42
        captured = capsys.readouterr()
        assert "⏱️" in captured.out

    def test_log_sync(self, capsys):
        @log
        def add(a, b):
            return a + b
        result = add(1, 2)
        assert result == 3
        captured = capsys.readouterr()
        assert "CALL" in captured.out
        assert "RETURN" in captured.out

    def test_log_error(self, capsys):
        @log
        def failing():
            raise ValueError("test error")
        with pytest.raises(ValueError):
            failing()
        captured = capsys.readouterr()
        assert "ERROR" in captured.out


# ── Good / Bad Service ──
from src.services.good_service import GoodBookService
from src.services.bad_service import BadBookService


class TestGoodService:
    """Тести відрефакторованого сервісу."""

    def _user(self, **overrides):
        data = {"name": "Іван", "email": "ivan@test.com", "current_borrows": 0, "total_borrows": 0}
        data.update(overrides)
        return data

    def _book(self, **overrides):
        data = {"title": "Кобзар", "available": 5}
        data.update(overrides)
        return data

    def test_successful_borrow(self):
        svc = GoodBookService()
        result = svc.process_borrow_request(self._user(), self._book())
        assert result.success is True
        assert result.book == "Кобзар"

    def test_no_name(self):
        result = GoodBookService().process_borrow_request(self._user(name=""), self._book())
        assert result.success is False

    def test_short_name(self):
        result = GoodBookService().process_borrow_request(self._user(name="A"), self._book())
        assert result.success is False

    def test_invalid_email(self):
        result = GoodBookService().process_borrow_request(self._user(email="bad"), self._book())
        assert result.success is False

    def test_no_book_title(self):
        result = GoodBookService().process_borrow_request(self._user(), self._book(title=""))
        assert result.success is False

    def test_book_unavailable(self):
        result = GoodBookService().process_borrow_request(self._user(), self._book(available=0))
        assert result.success is False

    def test_borrow_limit(self):
        result = GoodBookService().process_borrow_request(self._user(current_borrows=5), self._book())
        assert result.success is False

    def test_silver_discount(self):
        result = GoodBookService().process_borrow_request(self._user(total_borrows=50), self._book())
        assert result.discount_percent == 5.0

    def test_gold_discount(self):
        result = GoodBookService().process_borrow_request(self._user(total_borrows=200), self._book())
        assert result.discount_percent == 10.0


class TestBadService:
    """Тести поганого сервісу (для покриття)."""

    def test_successful_borrow(self):
        svc = BadBookService()
        result = svc.process_borrow_request(
            {"name": "Іван", "email": "ivan@test.com", "current_borrows": 0, "total_borrows": 0},
            {"title": "Кобзар", "available": 5},
        )
        assert result["status"] == "success"

    def test_no_name(self):
        svc = BadBookService()
        result = svc.process_borrow_request({"name": "", "email": "a@b.com"}, {"title": "T", "available": 1})
        assert result["status"] == "error"

    def test_limit_reached(self):
        svc = BadBookService()
        result = svc.process_borrow_request(
            {"name": "Іван", "email": "a@b.com", "current_borrows": 5},
            {"title": "T", "available": 1},
        )
        assert result["status"] == "error"


# ── Logger ──
from src.core.logger import setup_logger, get_logger, JSONFormatter


class TestLogger:
    """Тести логера."""

    def test_setup_logger(self):
        logger = setup_logger("test_logger", log_file=None)
        assert logger.name == "test_logger"
        assert len(logger.handlers) > 0

    def test_get_logger(self):
        logger = get_logger("test_get")
        assert logger is not None

    def test_json_formatter(self):
        import logging
        formatter = JSONFormatter()
        record = logging.LogRecord("test", logging.INFO, "test.py", 1, "hello", (), None)
        output = formatter.format(record)
        import json
        data = json.loads(output)
        assert data["message"] == "hello"
        assert data["level"] == "INFO"
