"""
dirty_code.py — Навмисне порушення принципів SRP та DIP.

Порушення SRP: Клас LibraryManager відповідає одночасно за:
  1. Роботу з базою даних (SQL-запити).
  2. Бізнес-логіку (розрахунок штрафів).
  3. Надсилання сповіщень (email).
  4. Логування.
  5. Валідацію даних.

Порушення DIP: Клас напряму залежить від конкретних реалізацій
  (sqlite3, smtplib), а не від абстракцій.
"""

import sqlite3
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText


class LibraryManager:
    """God-клас, що робить ВСЕ — порушує SRP та DIP."""

    def __init__(self):
        # Порушення DIP: жорстка залежність від конкретної реалізації
        self.conn = sqlite3.connect("library.db")
        self.cursor = self.conn.cursor()

    def add_book(self, title: str, isbn: str, author: str, quantity: int):
        """Додає книгу, валідує, логує, і сповіщує — все в одному місці."""
        # Валідація (відповідальність #1)
        if not title or len(title) < 1:
            print(f"[ERROR] {datetime.now()} - Назва книги не може бути порожньою")
            return None
        if not isbn or len(isbn) not in (10, 13):
            print(f"[ERROR] {datetime.now()} - Невалідний ISBN: {isbn}")
            return None
        if quantity < 0:
            print(f"[ERROR] {datetime.now()} - Кількість не може бути від'ємною")
            return None

        # Робота з БД (відповідальність #2)
        self.cursor.execute(
            "INSERT INTO books (title, isbn, author, quantity) VALUES (?, ?, ?, ?)",
            (title, isbn, author, quantity),
        )
        self.conn.commit()
        book_id = self.cursor.lastrowid

        # Логування (відповідальність #3)
        print(f"[INFO] {datetime.now()} - Книга '{title}' додана з ID={book_id}")

        # Сповіщення (відповідальність #4)
        self._send_email(
            "admin@library.com",
            f"Нова книга: {title}",
            f"Книга '{title}' (ISBN: {isbn}) була додана до бібліотеки.",
        )

        return book_id

    def borrow_book(self, user_id: int, book_id: int):
        """Видача книги — все змішано в одному методі."""
        # Перевірка доступності (БД)
        self.cursor.execute(
            "SELECT quantity FROM books WHERE id = ?", (book_id,)
        )
        result = self.cursor.fetchone()
        if not result or result[0] <= 0:
            print(f"[WARN] {datetime.now()} - Книга {book_id} недоступна")
            return None

        # Оновлення кількості (БД)
        self.cursor.execute(
            "UPDATE books SET quantity = quantity - 1 WHERE id = ?", (book_id,)
        )

        # Створення запису видачі (БД)
        due_date = datetime.now() + timedelta(days=14)
        self.cursor.execute(
            "INSERT INTO borrow_records (user_id, book_id, borrow_date, due_date) "
            "VALUES (?, ?, ?, ?)",
            (user_id, book_id, datetime.now(), due_date),
        )
        self.conn.commit()

        # Логування
        print(f"[INFO] {datetime.now()} - Книга {book_id} видана користувачу {user_id}")

        # Сповіщення
        self._send_email(
            f"user_{user_id}@library.com",
            "Книга видана",
            f"Ви отримали книгу (ID: {book_id}). Поверніть до {due_date}.",
        )

        return True

    def calculate_penalty(self, record_id: int) -> float:
        """Розрахунок штрафу — бізнес-логіка змішана з БД-доступом."""
        self.cursor.execute(
            "SELECT due_date, return_date FROM borrow_records WHERE id = ?",
            (record_id,),
        )
        result = self.cursor.fetchone()
        if not result:
            return 0.0

        due_date = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S.%f")
        return_date = (
            datetime.strptime(result[1], "%Y-%m-%d %H:%M:%S.%f")
            if result[1]
            else datetime.now()
        )

        if return_date > due_date:
            days_overdue = (return_date - due_date).days
            # Magic number: 5.50 грн/день — без пояснення
            penalty = days_overdue * 5.50
            print(f"[INFO] {datetime.now()} - Штраф: {penalty} грн за {days_overdue} днів")
            return penalty

        return 0.0

    def _send_email(self, to: str, subject: str, body: str):
        """Порушення DIP: жорстка залежність від smtplib."""
        try:
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = "noreply@library.com"
            msg["To"] = to

            # Порушення DIP: конкретний SMTP-сервер зашитий у код
            server = smtplib.SMTP("smtp.library.com", 587)
            server.starttls()
            server.login("noreply@library.com", "password123")  # Пароль у коді!
            server.send_message(msg)
            server.quit()
            print(f"[INFO] {datetime.now()} - Email надіслано до {to}")
        except Exception as e:
            print(f"[ERROR] {datetime.now()} - Помилка надсилання email: {e}")
