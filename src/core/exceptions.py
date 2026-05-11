"""
exceptions.py — Ієрархія виключень для Library System.

Базовий клас: LibraryBaseException
Спадкоємці:
  - BookNotFoundException
  - UserNotFoundException
  - BorrowLimitExceededException
"""


class LibraryBaseException(Exception):
    """Базовий виняток бібліотечної системи."""

    def __init__(self, message: str, code: str = "LIBRARY_ERROR", details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def to_dict(self) -> dict:
        """Серіалізація для API-відповіді."""
        return {"code": self.code, "message": self.message, "details": self.details}


class BookNotFoundException(LibraryBaseException):
    """Книга не знайдена."""

    def __init__(self, book_id: int):
        super().__init__(
            message=f"Книга з ID={book_id} не знайдена",
            code="BOOK_NOT_FOUND",
            details={"book_id": book_id},
        )


class UserNotFoundException(LibraryBaseException):
    """Користувач не знайдений."""

    def __init__(self, user_id: int):
        super().__init__(
            message=f"Користувач з ID={user_id} не знайдений",
            code="USER_NOT_FOUND",
            details={"user_id": user_id},
        )


class BorrowLimitExceededException(LibraryBaseException):
    """Перевищено ліміт видачі книг."""

    def __init__(self, user_id: int, current: int, limit: int):
        super().__init__(
            message=f"Користувач {user_id} досяг ліміту: {current}/{limit} книг",
            code="BORROW_LIMIT_EXCEEDED",
            details={"user_id": user_id, "current_borrows": current, "max_allowed": limit},
        )


class BookNotAvailableException(LibraryBaseException):
    """Книга недоступна для видачі."""

    def __init__(self, book_id: int):
        super().__init__(
            message=f"Книга з ID={book_id} наразі недоступна",
            code="BOOK_NOT_AVAILABLE",
            details={"book_id": book_id},
        )
