"""
book_builder.py — Builder патерн для створення об'єктів Book.

Патерн Builder дозволяє створювати складні об'єкти покроково,
надаючи зрозумілий fluent-інтерфейс.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Book:
    """Доменна модель книги."""
    id: Optional[int] = None
    title: str = ""
    isbn: str = ""
    publication_year: Optional[int] = None
    genre: str = ""
    quantity: int = 1
    available_quantity: int = 1
    author_id: Optional[int] = None
    author_name: str = ""
    description: str = ""
    language: str = "uk"
    pages: Optional[int] = None
    tags: list[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_available(self) -> bool:
        """Чи є книга доступною для видачі."""
        return self.available_quantity > 0

    def __str__(self) -> str:
        return f"📖 «{self.title}» — {self.author_name} ({self.publication_year})"


class BookBuilder:
    """Builder для покрокового створення об'єктів Book.

    Використання (fluent-інтерфейс):
        book = (
            BookBuilder()
            .with_title("Кобзар")
            .with_author(1, "Тарас Шевченко")
            .with_isbn("9789660368002")
            .with_year(1840)
            .with_genre("Поезія")
            .with_quantity(10)
            .with_description("Збірка поезій Тараса Шевченка")
            .with_tags(["поезія", "класика", "українська"])
            .build()
        )
    """

    def __init__(self):
        self._book = Book()

    def with_title(self, title: str) -> "BookBuilder":
        """Встановити назву книги."""
        self._book.title = title
        return self

    def with_isbn(self, isbn: str) -> "BookBuilder":
        """Встановити ISBN."""
        self._book.isbn = isbn
        return self

    def with_year(self, year: int) -> "BookBuilder":
        """Встановити рік публікації."""
        self._book.publication_year = year
        return self

    def with_genre(self, genre: str) -> "BookBuilder":
        """Встановити жанр."""
        self._book.genre = genre
        return self

    def with_quantity(self, quantity: int) -> "BookBuilder":
        """Встановити кількість примірників."""
        self._book.quantity = quantity
        self._book.available_quantity = quantity
        return self

    def with_author(self, author_id: int, author_name: str = "") -> "BookBuilder":
        """Встановити автора."""
        self._book.author_id = author_id
        self._book.author_name = author_name
        return self

    def with_description(self, description: str) -> "BookBuilder":
        """Встановити опис книги."""
        self._book.description = description
        return self

    def with_language(self, language: str) -> "BookBuilder":
        """Встановити мову книги."""
        self._book.language = language
        return self

    def with_pages(self, pages: int) -> "BookBuilder":
        """Встановити кількість сторінок."""
        self._book.pages = pages
        return self

    def with_tags(self, tags: list[str]) -> "BookBuilder":
        """Встановити теги."""
        self._book.tags = tags
        return self

    def build(self) -> Book:
        """Побудувати об'єкт Book.

        Returns:
            Готовий об'єкт Book.

        Raises:
            ValueError: Якщо обов'язкові поля не заповнені.
        """
        errors = self._validate()
        if errors:
            raise ValueError(
                "Неможливо створити книгу. Помилки:\n"
                + "\n".join(f"  - {e}" for e in errors)
            )

        now = datetime.now()
        self._book.created_at = now
        self._book.updated_at = now

        book = self._book
        self._book = Book()  # Скидаємо builder для повторного використання
        return book

    def _validate(self) -> list[str]:
        """Валідація обов'язкових полів."""
        errors = []
        if not self._book.title:
            errors.append("Назва книги (title) є обов'язковою")
        if not self._book.isbn:
            errors.append("ISBN є обов'язковим")
        if len(self._book.isbn) not in (0, 10, 13):
            errors.append(f"ISBN має бути 10 або 13 символів, отримано {len(self._book.isbn)}")
        if self._book.quantity < 0:
            errors.append("Кількість не може бути від'ємною")
        return errors


class BookDirector:
    """Director — створює книги за типовими шаблонами.

    Використання:
        director = BookDirector()
        textbook = director.create_textbook("Алгоритми", "978...", 1, "Д. Кнут")
    """

    @staticmethod
    def create_fiction(title: str, isbn: str, author_id: int, author_name: str) -> Book:
        """Створити художню книгу."""
        return (
            BookBuilder()
            .with_title(title)
            .with_isbn(isbn)
            .with_author(author_id, author_name)
            .with_genre("Художня література")
            .with_language("uk")
            .with_quantity(5)
            .build()
        )

    @staticmethod
    def create_textbook(title: str, isbn: str, author_id: int, author_name: str) -> Book:
        """Створити навчальний підручник."""
        return (
            BookBuilder()
            .with_title(title)
            .with_isbn(isbn)
            .with_author(author_id, author_name)
            .with_genre("Навчальна література")
            .with_language("uk")
            .with_quantity(20)
            .with_tags(["навчання", "підручник"])
            .build()
        )

    @staticmethod
    def create_reference(title: str, isbn: str, author_id: int, author_name: str) -> Book:
        """Створити довідник (не видається додому)."""
        return (
            BookBuilder()
            .with_title(title)
            .with_isbn(isbn)
            .with_author(author_id, author_name)
            .with_genre("Довідкова література")
            .with_quantity(2)
            .with_tags(["довідник", "читальна зала"])
            .build()
        )
