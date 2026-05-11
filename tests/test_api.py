"""
test_api.py — Інтеграційні тести з in-memory SQLite.

Тестує взаємодію між шарами через реальну (in-memory) БД.
"""

import pytest
import sqlite3
from datetime import datetime, timedelta


# =============================================================================
# Fixture: In-memory SQLite DB
# =============================================================================

@pytest.fixture
def db_connection():
    """Створити in-memory SQLite з усіма таблицями."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT,
            role TEXT NOT NULL DEFAULT 'reader',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE authors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            birth_year INTEGER,
            country TEXT,
            biography TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            isbn TEXT NOT NULL UNIQUE,
            publication_year INTEGER,
            genre TEXT,
            quantity INTEGER NOT NULL DEFAULT 1,
            available_quantity INTEGER NOT NULL DEFAULT 1,
            author_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES authors(id)
        );

        CREATE TABLE borrow_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            borrow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date DATE NOT NULL,
            return_date TIMESTAMP,
            penalty_amount REAL DEFAULT 0.0,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (book_id) REFERENCES books(id)
        );
    """)
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def seeded_db(db_connection):
    """Наповнити БД тестовими даними."""
    cursor = db_connection.cursor()

    # Автори
    cursor.execute(
        "INSERT INTO authors (first_name, last_name, birth_year, country) "
        "VALUES ('Тарас', 'Шевченко', 1814, 'Україна')"
    )
    cursor.execute(
        "INSERT INTO authors (first_name, last_name, birth_year, country) "
        "VALUES ('Леся', 'Українка', 1871, 'Україна')"
    )

    # Книги
    cursor.execute(
        "INSERT INTO books (title, isbn, publication_year, genre, quantity, "
        "available_quantity, author_id) VALUES "
        "('Кобзар', '9789660368002', 1840, 'Поезія', 5, 5, 1)"
    )
    cursor.execute(
        "INSERT INTO books (title, isbn, publication_year, genre, quantity, "
        "available_quantity, author_id) VALUES "
        "('Лісова пісня', '9789660368019', 1911, 'Драма', 3, 3, 2)"
    )

    # Користувачі
    cursor.execute(
        "INSERT INTO users (first_name, last_name, email, role) "
        "VALUES ('Іван', 'Франко', 'ivan@example.com', 'reader')"
    )

    db_connection.commit()
    return db_connection


# =============================================================================
# Інтеграційні тести
# =============================================================================

@pytest.mark.integration
class TestBookIntegration:
    """Інтеграційні тести для книг."""

    def test_insert_and_select_book(self, db_connection):
        cursor = db_connection.cursor()
        cursor.execute(
            "INSERT INTO authors (first_name, last_name) VALUES ('Test', 'Author')"
        )
        author_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO books (title, isbn, quantity, available_quantity, author_id) "
            "VALUES (?, ?, ?, ?, ?)",
            ("Test Book", "1234567890", 3, 3, author_id),
        )
        db_connection.commit()

        cursor.execute("SELECT * FROM books WHERE isbn = '1234567890'")
        book = cursor.fetchone()
        assert book is not None
        assert book["title"] == "Test Book"
        assert book["quantity"] == 3

    def test_unique_isbn_constraint(self, seeded_db):
        cursor = seeded_db.cursor()
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute(
                "INSERT INTO books (title, isbn, quantity, available_quantity, author_id) "
                "VALUES ('Duplicate', '9789660368002', 1, 1, 1)"
            )

    def test_foreign_key_author(self, seeded_db):
        cursor = seeded_db.cursor()
        cursor.execute("SELECT b.title, a.last_name FROM books b "
                        "JOIN authors a ON b.author_id = a.id WHERE b.id = 1")
        row = cursor.fetchone()
        assert row["title"] == "Кобзар"
        assert row["last_name"] == "Шевченко"

    def test_search_books_by_genre(self, seeded_db):
        cursor = seeded_db.cursor()
        cursor.execute("SELECT * FROM books WHERE genre = 'Поезія'")
        books = cursor.fetchall()
        assert len(books) == 1
        assert books[0]["title"] == "Кобзар"


@pytest.mark.integration
class TestBorrowIntegration:
    """Інтеграційні тести для видачі книг."""

    def test_borrow_book(self, seeded_db):
        cursor = seeded_db.cursor()
        due = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

        cursor.execute(
            "INSERT INTO borrow_records (user_id, book_id, due_date, status) "
            "VALUES (1, 1, ?, 'active')", (due,)
        )
        cursor.execute(
            "UPDATE books SET available_quantity = available_quantity - 1 WHERE id = 1"
        )
        seeded_db.commit()

        cursor.execute("SELECT available_quantity FROM books WHERE id = 1")
        assert cursor.fetchone()["available_quantity"] == 4

        cursor.execute("SELECT * FROM borrow_records WHERE user_id = 1")
        record = cursor.fetchone()
        assert record["status"] == "active"

    def test_return_book(self, seeded_db):
        cursor = seeded_db.cursor()
        due = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

        # Видача
        cursor.execute(
            "INSERT INTO borrow_records (user_id, book_id, due_date) VALUES (1, 1, ?)",
            (due,),
        )
        borrow_id = cursor.lastrowid
        cursor.execute("UPDATE books SET available_quantity = available_quantity - 1 WHERE id = 1")

        # Повернення
        cursor.execute(
            "UPDATE borrow_records SET return_date = CURRENT_TIMESTAMP, status = 'returned' "
            "WHERE id = ?", (borrow_id,)
        )
        cursor.execute("UPDATE books SET available_quantity = available_quantity + 1 WHERE id = 1")
        seeded_db.commit()

        cursor.execute("SELECT status FROM borrow_records WHERE id = ?", (borrow_id,))
        assert cursor.fetchone()["status"] == "returned"

        cursor.execute("SELECT available_quantity FROM books WHERE id = 1")
        assert cursor.fetchone()["available_quantity"] == 5

    def test_user_borrow_history(self, seeded_db):
        cursor = seeded_db.cursor()
        due = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

        cursor.execute(
            "INSERT INTO borrow_records (user_id, book_id, due_date) VALUES (1, 1, ?)", (due,)
        )
        cursor.execute(
            "INSERT INTO borrow_records (user_id, book_id, due_date) VALUES (1, 2, ?)", (due,)
        )
        seeded_db.commit()

        cursor.execute(
            "SELECT br.*, b.title FROM borrow_records br "
            "JOIN books b ON br.book_id = b.id WHERE br.user_id = 1"
        )
        records = cursor.fetchall()
        assert len(records) == 2


@pytest.mark.integration
class TestUserIntegration:
    """Інтеграційні тести для користувачів."""

    def test_create_user(self, db_connection):
        cursor = db_connection.cursor()
        cursor.execute(
            "INSERT INTO users (first_name, last_name, email) "
            "VALUES ('Нова', 'Особа', 'new@example.com')"
        )
        db_connection.commit()
        cursor.execute("SELECT * FROM users WHERE email = 'new@example.com'")
        user = cursor.fetchone()
        assert user["first_name"] == "Нова"
        assert user["role"] == "reader"

    def test_unique_email(self, seeded_db):
        cursor = seeded_db.cursor()
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute(
                "INSERT INTO users (first_name, last_name, email) "
                "VALUES ('Dup', 'User', 'ivan@example.com')"
            )

    def test_update_user_role(self, seeded_db):
        cursor = seeded_db.cursor()
        cursor.execute("UPDATE users SET role = 'librarian' WHERE id = 1")
        seeded_db.commit()
        cursor.execute("SELECT role FROM users WHERE id = 1")
        assert cursor.fetchone()["role"] == "librarian"
