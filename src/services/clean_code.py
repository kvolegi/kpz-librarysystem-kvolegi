"""
clean_code.py — Рефакторинг dirty_code.py за принципами SOLID.

Зміни:
  SRP: Кожен клас має одну відповідальність.
  OCP: Легко додати нові типи сповіщень без зміни існуючого коду.
  LSP: Всі реалізації інтерфейсів взаємозамінні.
  ISP: Інтерфейси розділені та мінімальні.
  DIP: Залежності інжектуються через конструктор (абстракції, не реалізації).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# Доменні моделі (Model Layer)
# =============================================================================

@dataclass
class Book:
    """Доменна модель книги."""
    id: Optional[int] = None
    title: str = ""
    isbn: str = ""
    author: str = ""
    quantity: int = 0


@dataclass
class BorrowRecord:
    """Доменна модель запису про видачу."""
    id: Optional[int] = None
    user_id: int = 0
    book_id: int = 0
    borrow_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    return_date: Optional[datetime] = None


# =============================================================================
# Абстракції (Interfaces) — DIP: залежимо від абстракцій
# =============================================================================

class BookRepository(ABC):
    """Абстракція для доступу до даних книг (Repository Pattern)."""

    @abstractmethod
    async def add(self, book: Book) -> int:
        """Додати книгу, повернути ID."""
        ...

    @abstractmethod
    async def get_by_id(self, book_id: int) -> Optional[Book]:
        """Отримати книгу за ID."""
        ...

    @abstractmethod
    async def update_quantity(self, book_id: int, delta: int) -> bool:
        """Оновити кількість доступних книг."""
        ...


class BorrowRepository(ABC):
    """Абстракція для доступу до записів видачі."""

    @abstractmethod
    async def create(self, record: BorrowRecord) -> int:
        """Створити запис видачі."""
        ...

    @abstractmethod
    async def get_by_id(self, record_id: int) -> Optional[BorrowRecord]:
        """Отримати запис за ID."""
        ...


class NotificationService(ABC):
    """Абстракція для сповіщень — ISP: тільки один метод."""

    @abstractmethod
    async def send(self, recipient: str, subject: str, message: str) -> bool:
        """Надіслати сповіщення."""
        ...


class Validator(ABC):
    """Абстракція для валідації."""

    @abstractmethod
    def validate(self, data: dict) -> list[str]:
        """Повернути список помилок валідації (порожній = валідно)."""
        ...


# =============================================================================
# Конкретні реалізації (можуть бути замінені)
# =============================================================================

class BookValidator(Validator):
    """SRP: відповідає ТІЛЬКИ за валідацію книг."""

    def validate(self, data: dict) -> list[str]:
        errors = []
        if not data.get("title"):
            errors.append("Назва книги не може бути порожньою")
        isbn = data.get("isbn", "")
        if not isbn or len(isbn) not in (10, 13):
            errors.append(f"Невалідний ISBN: {isbn}")
        if data.get("quantity", 0) < 0:
            errors.append("Кількість не може бути від'ємною")
        return errors


# =============================================================================
# Сервіс для розрахунку штрафів — SRP: ТІЛЬКИ бізнес-логіка
# =============================================================================

class PenaltyCalculator:
    """SRP: відповідає ТІЛЬКИ за розрахунок штрафів."""

    DAILY_PENALTY_RATE = 5.50  # грн/день — іменована константа замість magic number

    def calculate(self, due_date: datetime, return_date: Optional[datetime] = None) -> float:
        """Розрахувати штраф за прострочення.

        Args:
            due_date: Дата, до якої потрібно повернути книгу.
            return_date: Фактична дата повернення (None = сьогодні).

        Returns:
            Сума штрафу в гривнях.
        """
        actual_return = return_date or datetime.now()
        if actual_return <= due_date:
            return 0.0

        days_overdue = (actual_return - due_date).days
        penalty = days_overdue * self.DAILY_PENALTY_RATE
        logger.info("Штраф: %.2f грн за %d днів прострочення", penalty, days_overdue)
        return penalty


# =============================================================================
# Сервіс управління книгами — DIP: залежить від абстракцій через конструктор
# =============================================================================

class BookService:
    """SRP: оркеструє операції з книгами.

    DIP: всі залежності інжектуються через конструктор.
    """

    def __init__(
        self,
        book_repo: BookRepository,
        notification: NotificationService,
        validator: Validator,
    ):
        self._book_repo = book_repo
        self._notification = notification
        self._validator = validator

    async def add_book(self, title: str, isbn: str, author: str, quantity: int) -> Optional[int]:
        """Додати нову книгу до бібліотеки."""
        # Валідація — делегуємо спеціалізованому класу
        errors = self._validator.validate({
            "title": title,
            "isbn": isbn,
            "author": author,
            "quantity": quantity,
        })
        if errors:
            for error in errors:
                logger.error("Помилка валідації: %s", error)
            return None

        # Збереження — делегуємо репозиторію
        book = Book(title=title, isbn=isbn, author=author, quantity=quantity)
        book_id = await self._book_repo.add(book)
        logger.info("Книга '%s' додана з ID=%d", title, book_id)

        # Сповіщення — делегуємо сервісу сповіщень
        await self._notification.send(
            "admin@library.com",
            f"Нова книга: {title}",
            f"Книга '{title}' (ISBN: {isbn}) додана до бібліотеки.",
        )

        return book_id


# =============================================================================
# Сервіс видачі книг — DIP: залежить від абстракцій
# =============================================================================

class BorrowService:
    """SRP: оркеструє процес видачі/повернення книг."""

    LOAN_PERIOD_DAYS = 14  # Іменована константа

    def __init__(
        self,
        book_repo: BookRepository,
        borrow_repo: BorrowRepository,
        notification: NotificationService,
        penalty_calculator: PenaltyCalculator,
    ):
        self._book_repo = book_repo
        self._borrow_repo = borrow_repo
        self._notification = notification
        self._penalty_calculator = penalty_calculator

    async def borrow_book(self, user_id: int, book_id: int) -> bool:
        """Видати книгу користувачу."""
        book = await self._book_repo.get_by_id(book_id)
        if not book or book.quantity <= 0:
            logger.warning("Книга %d недоступна для видачі", book_id)
            return False

        await self._book_repo.update_quantity(book_id, delta=-1)

        now = datetime.now()
        record = BorrowRecord(
            user_id=user_id,
            book_id=book_id,
            borrow_date=now,
            due_date=now + timedelta(days=self.LOAN_PERIOD_DAYS),
        )
        await self._borrow_repo.create(record)

        logger.info("Книга %d видана користувачу %d", book_id, user_id)

        await self._notification.send(
            f"user_{user_id}@library.com",
            "Книга видана",
            f"Ви отримали книгу (ID: {book_id}). Поверніть до {record.due_date}.",
        )

        return True

    async def calculate_penalty(self, record_id: int) -> float:
        """Розрахувати штраф для конкретного запису видачі."""
        record = await self._borrow_repo.get_by_id(record_id)
        if not record or not record.due_date:
            return 0.0
        return self._penalty_calculator.calculate(record.due_date, record.return_date)
