"""
config.py — Singleton патерн для конфігурації додатку.

Патерн Singleton гарантує, що клас має лише один екземпляр,
і надає глобальну точку доступу до нього.

Реалізація через __new__ — потокобезпечна з використанням блокування.
"""

import threading
from typing import Any, Optional


class Config:
    """Singleton конфігурація бібліотечної системи.

    Використання:
        config = Config()
        config.set("DB_HOST", "localhost")
        host = config.get("DB_HOST")
    """

    _instance: Optional["Config"] = None
    _lock: threading.Lock = threading.Lock()
    _initialized: bool = False

    def __new__(cls) -> "Config":
        """Гарантує створення лише одного екземпляра (потокобезпечно)."""
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Ініціалізація виконується лише один раз."""
        if not Config._initialized:
            self._settings: dict[str, Any] = {
                "APP_NAME": "Library System",
                "APP_VERSION": "1.0.0",
                "DB_HOST": "localhost",
                "DB_PORT": 5432,
                "DB_NAME": "library_db",
                "DB_USER": "library_user",
                "DB_PASSWORD": "",
                "LOG_LEVEL": "INFO",
                "LOG_FORMAT": "json",
                "MAX_BORROW_DAYS": 14,
                "DAILY_PENALTY_RATE": 5.50,
                "MAX_BOOKS_PER_USER": 5,
                "SMTP_HOST": "smtp.example.com",
                "SMTP_PORT": 587,
            }
            Config._initialized = True

    def get(self, key: str, default: Any = None) -> Any:
        """Отримати значення налаштування.

        Args:
            key: Ключ налаштування.
            default: Значення за замовчуванням.

        Returns:
            Значення налаштування або default.
        """
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Встановити значення налаштування.

        Args:
            key: Ключ налаштування.
            value: Нове значення.
        """
        self._settings[key] = value

    def get_all(self) -> dict[str, Any]:
        """Отримати всі налаштування (копію).

        Returns:
            Копія словника налаштувань.
        """
        return self._settings.copy()

    def __repr__(self) -> str:
        return f"Config(settings_count={len(self._settings)})"

    @classmethod
    def reset(cls) -> None:
        """Скинути Singleton (для тестів).

        ⚠️ Використовувати лише в тестах!
        """
        with cls._lock:
            cls._instance = None
            cls._initialized = False
