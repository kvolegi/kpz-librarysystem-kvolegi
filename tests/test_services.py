"""
test_services.py — Unit-тести з unittest.mock.MagicMock.

Тестує сервіси з mock-залежностями для ізоляції бізнес-логіки.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta

# ── Тести PenaltyCalculator ──

from src.services.penalty_strategy import (
    PenaltyCalculator,
    FixedPenaltyStrategy,
    ProgressivePenaltyStrategy,
    FreePenaltyStrategy,
)


class TestFixedPenaltyStrategy:
    """Тести фіксованої стратегії штрафів."""

    def test_no_penalty_when_on_time(self):
        strategy = FixedPenaltyStrategy(daily_rate=5.50)
        assert strategy.calculate(0) == 0.0

    def test_no_penalty_for_negative_days(self):
        strategy = FixedPenaltyStrategy(daily_rate=5.50)
        assert strategy.calculate(-3) == 0.0

    def test_penalty_for_one_day(self):
        strategy = FixedPenaltyStrategy(daily_rate=5.50)
        assert strategy.calculate(1) == 5.50

    def test_penalty_for_multiple_days(self):
        strategy = FixedPenaltyStrategy(daily_rate=5.50)
        assert strategy.calculate(10) == 55.0

    def test_custom_rate(self):
        strategy = FixedPenaltyStrategy(daily_rate=10.0)
        assert strategy.calculate(3) == 30.0

    def test_strategy_name(self):
        strategy = FixedPenaltyStrategy(daily_rate=5.50)
        assert "5.5" in strategy.get_name()


class TestProgressivePenaltyStrategy:
    """Тести прогресивної стратегії штрафів."""

    def test_first_week(self):
        strategy = ProgressivePenaltyStrategy(base_rate=3.0)
        assert strategy.calculate(7) == 21.0  # 7 × 3.0

    def test_second_week(self):
        strategy = ProgressivePenaltyStrategy(base_rate=3.0)
        # 7 × 3.0 + 3 × 6.0 = 21 + 18 = 39
        assert strategy.calculate(10) == 39.0

    def test_after_two_weeks(self):
        strategy = ProgressivePenaltyStrategy(base_rate=3.0)
        # 7×3 + 7×6 + 1×9 = 21 + 42 + 9 = 72
        assert strategy.calculate(15) == 72.0

    def test_zero_days(self):
        strategy = ProgressivePenaltyStrategy(base_rate=3.0)
        assert strategy.calculate(0) == 0.0


class TestFreePenaltyStrategy:
    """Тести пільгової стратегії."""

    def test_within_grace_period(self):
        strategy = FreePenaltyStrategy(grace_period_days=7)
        assert strategy.calculate(5) == 0.0

    def test_at_grace_boundary(self):
        strategy = FreePenaltyStrategy(grace_period_days=7)
        assert strategy.calculate(7) == 0.0

    def test_after_grace_period(self):
        strategy = FreePenaltyStrategy(grace_period_days=7)
        # 10 - 7 = 3 дні × 5.50 = 16.50
        assert strategy.calculate(10) == 16.50


class TestPenaltyCalculator:
    """Тести калькулятора штрафів з mock-стратегією."""

    def test_compute_uses_strategy(self):
        mock_strategy = MagicMock()
        mock_strategy.calculate.return_value = 42.0

        calc = PenaltyCalculator(mock_strategy)
        due = datetime(2026, 1, 1)
        ret = datetime(2026, 1, 11)

        result = calc.compute(due, ret)
        assert result == 42.0
        mock_strategy.calculate.assert_called_once_with(10)

    def test_no_penalty_when_early(self):
        mock_strategy = MagicMock()
        calc = PenaltyCalculator(mock_strategy)
        due = datetime(2026, 1, 15)
        ret = datetime(2026, 1, 10)

        result = calc.compute(due, ret)
        assert result == 0.0
        mock_strategy.calculate.assert_not_called()

    def test_set_strategy(self):
        old = MagicMock()
        new = MagicMock()
        new.calculate.return_value = 99.0

        calc = PenaltyCalculator(old)
        calc.set_strategy(new)

        due = datetime(2026, 1, 1)
        ret = datetime(2026, 1, 5)
        calc.compute(due, ret)

        new.calculate.assert_called_once()
        old.calculate.assert_not_called()


# ── Тести BookBuilder ──

from src.models.book_builder import BookBuilder, BookDirector


class TestBookBuilder:
    """Тести Builder патерну."""

    def test_build_valid_book(self):
        book = (
            BookBuilder()
            .with_title("Test Book")
            .with_isbn("1234567890")
            .with_author(1, "Author")
            .with_quantity(5)
            .build()
        )
        assert book.title == "Test Book"
        assert book.isbn == "1234567890"
        assert book.quantity == 5
        assert book.available_quantity == 5

    def test_build_without_title_raises(self):
        with pytest.raises(ValueError, match="Назва книги"):
            BookBuilder().with_isbn("1234567890").build()

    def test_build_without_isbn_raises(self):
        with pytest.raises(ValueError, match="ISBN"):
            BookBuilder().with_title("Test").build()

    def test_book_is_available(self):
        book = (
            BookBuilder()
            .with_title("T")
            .with_isbn("1234567890")
            .with_quantity(3)
            .build()
        )
        assert book.is_available()


class TestBookDirector:
    """Тести Director для BookBuilder."""

    def test_create_fiction(self):
        book = BookDirector.create_fiction("Title", "1234567890", 1, "Author")
        assert book.genre == "Художня література"
        assert book.quantity == 5

    def test_create_textbook(self):
        book = BookDirector.create_textbook("Title", "1234567890", 1, "Author")
        assert book.genre == "Навчальна література"
        assert book.quantity == 20

    def test_create_reference(self):
        book = BookDirector.create_reference("Title", "1234567890", 1, "Author")
        assert book.genre == "Довідкова література"
        assert book.quantity == 2


# ── Тести Config Singleton ──

from src.core.config import Config


class TestConfigSingleton:
    """Тести Singleton конфігурації."""

    def setup_method(self):
        Config.reset()

    def test_singleton_same_instance(self):
        c1 = Config()
        c2 = Config()
        assert c1 is c2

    def test_set_and_get(self):
        config = Config()
        config.set("TEST_KEY", "test_value")
        assert config.get("TEST_KEY") == "test_value"

    def test_default_value(self):
        config = Config()
        assert config.get("NONEXISTENT", "default") == "default"

    def test_has_default_settings(self):
        config = Config()
        assert config.get("APP_NAME") == "Library System"


# ── Тести Exceptions ──

from src.core.exceptions import (
    LibraryBaseException,
    BookNotFoundException,
    UserNotFoundException,
    BorrowLimitExceededException,
)


class TestExceptions:
    """Тести ієрархії виключень."""

    def test_base_exception(self):
        exc = LibraryBaseException("test error")
        assert str(exc) == "test error"
        assert exc.code == "LIBRARY_ERROR"

    def test_book_not_found(self):
        exc = BookNotFoundException(42)
        assert exc.code == "BOOK_NOT_FOUND"
        assert exc.details["book_id"] == 42
        assert isinstance(exc, LibraryBaseException)

    def test_user_not_found(self):
        exc = UserNotFoundException(7)
        assert exc.code == "USER_NOT_FOUND"
        assert isinstance(exc, LibraryBaseException)

    def test_borrow_limit(self):
        exc = BorrowLimitExceededException(1, 5, 5)
        assert exc.code == "BORROW_LIMIT_EXCEEDED"
        d = exc.to_dict()
        assert d["details"]["max_allowed"] == 5

    def test_to_dict(self):
        exc = BookNotFoundException(1)
        d = exc.to_dict()
        assert "code" in d
        assert "message" in d
        assert "details" in d


# ── Тести Observer ──

from src.events.observer import EventManager, Event, EventType, LoggingListener


class TestEventManager:
    """Тести подієвої системи."""

    def test_subscribe_and_publish(self):
        manager = EventManager()
        listener = MagicMock()
        listener.handle = MagicMock()

        manager.subscribe(EventType.BOOK_ADDED, listener)
        event = Event(EventType.BOOK_ADDED, {"title": "Test"})
        manager.publish(event)

        listener.handle.assert_called_once_with(event)

    def test_unsubscribe(self):
        manager = EventManager()
        listener = MagicMock()

        manager.subscribe(EventType.BOOK_ADDED, listener)
        manager.unsubscribe(EventType.BOOK_ADDED, listener)
        manager.publish(Event(EventType.BOOK_ADDED))

        listener.handle.assert_not_called()

    def test_subscriber_count(self):
        manager = EventManager()
        manager.subscribe(EventType.BOOK_ADDED, MagicMock())
        manager.subscribe(EventType.BOOK_ADDED, MagicMock())
        assert manager.subscriber_count(EventType.BOOK_ADDED) == 2

    def test_no_listeners_no_error(self):
        manager = EventManager()
        manager.publish(Event(EventType.BOOK_BORROWED))  # Не має кидати помилку
