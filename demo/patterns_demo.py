"""
patterns_demo.py — Демонстрація роботи всіх трьох породжуючих патернів.

Запуск:
    python -m demo.patterns_demo

Демонструє:
    1. Singleton (Config)
    2. Factory Method (NotificationFactory)
    3. Builder (BookBuilder / BookDirector)
"""

import asyncio
import sys
import os

# Додаємо кореневу директорію проєкту до PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.config import Config
from src.services.notification_factory import NotificationFactory, Notification
from src.models.book_builder import BookBuilder, BookDirector


def print_section(title: str) -> None:
    """Вивести заголовок секції."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def demo_singleton() -> None:
    """Демонстрація патерну Singleton."""
    print_section("🔒 SINGLETON — Config")

    # Створюємо два екземпляри
    config1 = Config()
    config2 = Config()

    # Перевіряємо, що це один і той самий об'єкт
    print(f"\nconfig1 is config2: {config1 is config2}")
    print(f"id(config1): {id(config1)}")
    print(f"id(config2): {id(config2)}")

    # Встановлюємо значення через один екземпляр
    config1.set("DB_HOST", "production-server.com")
    config1.set("DB_PORT", 5433)

    # Читаємо через інший — значення збігаються
    print(f"\nconfig2.get('DB_HOST'): {config2.get('DB_HOST')}")
    print(f"config2.get('DB_PORT'): {config2.get('DB_PORT')}")
    print(f"config2.get('APP_NAME'): {config2.get('APP_NAME')}")

    # Усі налаштування
    print(f"\n📋 Всі налаштування ({len(config1.get_all())} ключів):")
    for key, value in list(config1.get_all().items())[:5]:
        print(f"   {key}: {value}")
    print("   ...")

    print("\n✅ Singleton працює: обидва посилання вказують на один об'єкт!")


async def demo_factory_method() -> None:
    """Демонстрація патерну Factory Method."""
    print_section("🏭 FACTORY METHOD — NotificationFactory")

    # Показуємо доступні типи
    print(f"\nДоступні типи сповіщень: {NotificationFactory.available_types()}")

    # Створюємо різні сповіщення через фабрику
    notification = Notification(
        recipient="reader@library.com",
        subject="Нагадування про повернення",
        message="Будь ласка, поверніть книгу «Кобзар» до 25.05.2026",
    )

    types_to_demo = ["email", "sms", "push", "console"]
    for ntype in types_to_demo:
        print(f"\n--- Тип: {ntype.upper()} ---")
        sender = NotificationFactory.create(ntype)
        await sender.send(notification)
        print(f"   Тип відправника: {sender.get_type()}")

    # Демонстрація помилки при невідомому типі
    print("\n--- Спроба створити невідомий тип ---")
    try:
        NotificationFactory.create("telegram")
    except ValueError as e:
        print(f"   ❌ Помилка: {e}")

    print("\n✅ Factory Method працює: різні реалізації через єдиний інтерфейс!")


def demo_builder() -> None:
    """Демонстрація патерну Builder."""
    print_section("🔨 BUILDER — BookBuilder / BookDirector")

    # 1. Створення через Builder (fluent API)
    print("\n--- Builder (ручне створення) ---")
    book = (
        BookBuilder()
        .with_title("Кобзар")
        .with_isbn("9789660368002")
        .with_author(1, "Тарас Шевченко")
        .with_year(1840)
        .with_genre("Поезія")
        .with_quantity(10)
        .with_description("Збірка поезій великого українського поета")
        .with_language("uk")
        .with_pages(232)
        .with_tags(["поезія", "класика", "українська"])
        .build()
    )
    print(f"   {book}")
    print(f"   ISBN: {book.isbn}")
    print(f"   Жанр: {book.genre}")
    print(f"   Кількість: {book.quantity}")
    print(f"   Доступно: {book.available_quantity}")
    print(f"   Мова: {book.language}")
    print(f"   Теги: {book.tags}")
    print(f"   Доступна: {book.is_available()}")

    # 2. Створення через Director (шаблони)
    print("\n--- Director (шаблонні книги) ---")

    fiction = BookDirector.create_fiction(
        "Тіні забутих предків", "9789660369856", 2, "Михайло Коцюбинський"
    )
    print(f"\n   Художня: {fiction}")
    print(f"   Жанр: {fiction.genre}, Кількість: {fiction.quantity}")

    textbook = BookDirector.create_textbook(
        "Алгоритми та структури даних", "9781234567890", 3, "Дональд Кнут"
    )
    print(f"\n   Підручник: {textbook}")
    print(f"   Жанр: {textbook.genre}, Кількість: {textbook.quantity}")
    print(f"   Теги: {textbook.tags}")

    reference = BookDirector.create_reference(
        "Енциклопедія України", "9789876543210", 4, "Колектив авторів"
    )
    print(f"\n   Довідник: {reference}")
    print(f"   Жанр: {reference.genre}, Кількість: {reference.quantity}")

    # 3. Демонстрація валідації
    print("\n--- Валідація Builder ---")
    try:
        BookBuilder().with_isbn("123").build()  # Немає title + невалідний ISBN
    except ValueError as e:
        print(f"   ❌ Помилка валідації:\n{e}")

    print("\n✅ Builder працює: покрокове створення складних об'єктів!")


async def main() -> None:
    """Головна функція демонстрації."""
    print("\n" + "🏛️" * 25)
    print("  LIBRARY SYSTEM — Демонстрація породжуючих патернів")
    print("🏛️" * 25)

    # 1. Singleton
    demo_singleton()

    # 2. Factory Method
    await demo_factory_method()

    # 3. Builder
    demo_builder()

    print("\n" + "=" * 60)
    print("  🎉 Всі три патерни успішно продемонстровані!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
