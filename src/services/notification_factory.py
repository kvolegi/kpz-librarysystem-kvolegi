"""
notification_factory.py — Factory Method патерн для сповіщень.

Патерн Factory Method визначає інтерфейс для створення об'єктів,
дозволяючи підкласам змінювати тип створюваних об'єктів.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


# =============================================================================
# Продукт (абстракція)
# =============================================================================

@dataclass
class Notification:
    """Базова модель сповіщення."""
    recipient: str
    subject: str
    message: str
    sent_at: Optional[datetime] = None
    status: str = "pending"


class NotificationSender(ABC):
    """Абстрактний відправник сповіщень (Product)."""

    @abstractmethod
    async def send(self, notification: Notification) -> bool:
        """Надіслати сповіщення."""
        ...

    @abstractmethod
    def get_type(self) -> str:
        """Повернути тип сповіщення."""
        ...


# =============================================================================
# Конкретні продукти
# =============================================================================

class EmailNotificationSender(NotificationSender):
    """Відправник email-сповіщень."""

    def __init__(self, smtp_host: str = "smtp.example.com", smtp_port: int = 587):
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port

    async def send(self, notification: Notification) -> bool:
        """Надіслати email."""
        # Імітація надсилання email
        print(f"📧 [EMAIL] To: {notification.recipient}")
        print(f"   Subject: {notification.subject}")
        print(f"   Message: {notification.message}")
        notification.sent_at = datetime.now()
        notification.status = "sent"
        return True

    def get_type(self) -> str:
        return "email"


class SMSNotificationSender(NotificationSender):
    """Відправник SMS-сповіщень."""

    def __init__(self, api_key: str = "demo-key"):
        self._api_key = api_key

    async def send(self, notification: Notification) -> bool:
        """Надіслати SMS."""
        print(f"📱 [SMS] To: {notification.recipient}")
        print(f"   Message: {notification.message[:160]}")
        notification.sent_at = datetime.now()
        notification.status = "sent"
        return True

    def get_type(self) -> str:
        return "sms"


class PushNotificationSender(NotificationSender):
    """Відправник push-сповіщень."""

    async def send(self, notification: Notification) -> bool:
        """Надіслати push-сповіщення."""
        print(f"🔔 [PUSH] To: {notification.recipient}")
        print(f"   Title: {notification.subject}")
        print(f"   Body: {notification.message[:200]}")
        notification.sent_at = datetime.now()
        notification.status = "sent"
        return True

    def get_type(self) -> str:
        return "push"


class ConsoleNotificationSender(NotificationSender):
    """Відправник сповіщень у консоль (для розробки/тестів)."""

    async def send(self, notification: Notification) -> bool:
        """Вивести сповіщення у консоль."""
        print(f"🖥️  [CONSOLE] To: {notification.recipient}")
        print(f"   Subject: {notification.subject}")
        print(f"   Message: {notification.message}")
        notification.sent_at = datetime.now()
        notification.status = "sent"
        return True

    def get_type(self) -> str:
        return "console"


# =============================================================================
# Фабрика (Factory Method)
# =============================================================================

class NotificationFactory:
    """Фабрика для створення сервісів сповіщень.

    Використання:
        sender = NotificationFactory.create("email")
        await sender.send(notification)
    """

    _registry: dict[str, type[NotificationSender]] = {
        "email": EmailNotificationSender,
        "sms": SMSNotificationSender,
        "push": PushNotificationSender,
        "console": ConsoleNotificationSender,
    }

    @classmethod
    def create(cls, notification_type: str, **kwargs) -> NotificationSender:
        """Створити відправник сповіщень за типом.

        Args:
            notification_type: Тип сповіщення ("email", "sms", "push", "console").
            **kwargs: Додаткові аргументи для конструктора.

        Returns:
            Екземпляр NotificationSender.

        Raises:
            ValueError: Якщо тип сповіщення не підтримується.
        """
        sender_class = cls._registry.get(notification_type.lower())
        if not sender_class:
            available = ", ".join(cls._registry.keys())
            raise ValueError(
                f"Невідомий тип сповіщення: '{notification_type}'. "
                f"Доступні: {available}"
            )
        return sender_class(**kwargs)

    @classmethod
    def register(cls, notification_type: str, sender_class: type[NotificationSender]) -> None:
        """Зареєструвати новий тип сповіщень (OCP — розширення без модифікації).

        Args:
            notification_type: Назва типу.
            sender_class: Клас-відправник.
        """
        cls._registry[notification_type.lower()] = sender_class

    @classmethod
    def available_types(cls) -> list[str]:
        """Отримати список доступних типів сповіщень."""
        return list(cls._registry.keys())
