"""
good_service.py — Відрефакторена версія bad_service.py.

Рефакторинг: Extract Function — кожна відповідальність у своєму методі.
Усі Magic Numbers замінені на іменовані константи.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


# Іменовані константи замість Magic Numbers
MAX_BOOKS_PER_USER = 5
LOAN_PERIOD_DAYS = 14
BASE_DEPOSIT_UAH = 50.0
GOLD_TIER_THRESHOLD = 100
SILVER_TIER_THRESHOLD = 10
GOLD_DISCOUNT = 0.10   # 10%
SILVER_DISCOUNT = 0.05  # 5%
MIN_NAME_LENGTH = 2


@dataclass
class BorrowResult:
    """Результат операції видачі."""
    success: bool
    message: str
    user: str = ""
    book: str = ""
    borrow_date: str = ""
    due_date: str = ""
    deposit: float = 0.0
    discount_percent: float = 0.0


class GoodBookService:
    """Відрефакторений сервіс — Extract Function + Named Constants."""

    def process_borrow_request(self, user_data: dict, book_data: dict) -> BorrowResult:
        """Основний метод — оркестратор, делегує підзадачі."""
        # Крок 1: Валідація
        error = self._validate_user(user_data)
        if error:
            return BorrowResult(success=False, message=error)

        error = self._validate_book(book_data)
        if error:
            return BorrowResult(success=False, message=error)

        error = self._check_borrow_limit(user_data)
        if error:
            return BorrowResult(success=False, message=error)

        # Крок 2: Бізнес-логіка
        borrow_date, due_date = self._calculate_dates()
        discount = self._calculate_discount(user_data)
        deposit = self._calculate_deposit(discount)

        # Крок 3: Формування результату
        return self._build_result(user_data, book_data, borrow_date, due_date, deposit, discount)

    # ── Extracted Functions ──

    @staticmethod
    def _validate_user(user_data: dict) -> Optional[str]:
        """Валідація даних користувача."""
        name = user_data.get("name", "")
        email = user_data.get("email", "")
        if not name:
            return "Ім'я користувача обов'язкове"
        if len(name) < MIN_NAME_LENGTH:
            return f"Ім'я має містити мінімум {MIN_NAME_LENGTH} символи"
        if not email or "@" not in email:
            return "Невалідний email"
        return None

    @staticmethod
    def _validate_book(book_data: dict) -> Optional[str]:
        """Валідація даних книги."""
        if not book_data.get("title"):
            return "Назва книги обов'язкова"
        if book_data.get("available", 0) <= 0:
            return "Книга наразі недоступна"
        return None

    @staticmethod
    def _check_borrow_limit(user_data: dict) -> Optional[str]:
        """Перевірка ліміту видачі."""
        current = user_data.get("current_borrows", 0)
        if current >= MAX_BOOKS_PER_USER:
            return f"Досягнуто ліміт: {current}/{MAX_BOOKS_PER_USER} книг"
        return None

    @staticmethod
    def _calculate_dates() -> tuple[datetime, datetime]:
        """Розрахунок дат видачі та повернення."""
        borrow_date = datetime.now()
        due_date = borrow_date + timedelta(days=LOAN_PERIOD_DAYS)
        return borrow_date, due_date

    @staticmethod
    def _calculate_discount(user_data: dict) -> float:
        """Розрахунок знижки за лояльність."""
        total = user_data.get("total_borrows", 0)
        if total > GOLD_TIER_THRESHOLD:
            return GOLD_DISCOUNT
        elif total > SILVER_TIER_THRESHOLD:
            return SILVER_DISCOUNT
        return 0.0

    @staticmethod
    def _calculate_deposit(discount: float) -> float:
        """Розрахунок депозиту зі знижкою."""
        return round(BASE_DEPOSIT_UAH * (1 - discount), 2)

    @staticmethod
    def _build_result(
        user_data: dict, book_data: dict,
        borrow_date: datetime, due_date: datetime,
        deposit: float, discount: float,
    ) -> BorrowResult:
        """Формування результату операції."""
        return BorrowResult(
            success=True,
            message=f"Книга '{book_data['title']}' видана {user_data['name']}",
            user=user_data["name"],
            book=book_data["title"],
            borrow_date=borrow_date.isoformat(),
            due_date=due_date.isoformat(),
            deposit=deposit,
            discount_percent=discount * 100,
        )
