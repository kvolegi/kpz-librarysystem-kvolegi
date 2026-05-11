"""
discount.py — Функція розрахунку знижки за лояльність.

TDD процес:
  Крок 1 (RED):      Тести написані → вони падають (ImportError).
  Крок 2 (GREEN):    Мінімальний код для проходження тестів.
  Крок 3 (REFACTOR): Фінальна версія з Enum, docstrings, чистим кодом.

Це — фінальна відрефакторена версія (Крок 3).
"""

from enum import Enum


class DiscountTier(Enum):
    """Рівні знижок за лояльність.

    Визначає відсоток знижки залежно від кількості
    позичених книг за весь час.
    """
    NONE = 0.0         # 0-10 книг
    SILVER = 5.0       # 11-100 книг
    GOLD = 10.0        # 101-500 книг
    PLATINUM = 15.0    # 501+ книг


# Конфігурація порогів (відсортовано за спаданням для правильного пріоритету)
_TIER_THRESHOLDS: list[tuple[int, DiscountTier]] = [
    (501, DiscountTier.PLATINUM),
    (101, DiscountTier.GOLD),
    (11,  DiscountTier.SILVER),
]


def calculate_discount(total_borrows: int) -> float:
    """Розрахувати знижку за лояльність користувача.

    Знижка визначається за кількістю позичених книг за весь час:
      - 0–10 книг:   0% (NONE)
      - 11–100 книг:  5% (SILVER)
      - 101–500 книг: 10% (GOLD)
      - 501+ книг:   15% (PLATINUM)

    Args:
        total_borrows: Загальна кількість книг, позичених користувачем.

    Returns:
        Відсоток знижки (0.0, 5.0, 10.0 або 15.0).

    Examples:
        >>> calculate_discount(0)
        0.0
        >>> calculate_discount(50)
        5.0
        >>> calculate_discount(200)
        10.0
        >>> calculate_discount(1000)
        15.0
    """
    if total_borrows < 0:
        return DiscountTier.NONE.value

    for threshold, tier in _TIER_THRESHOLDS:
        if total_borrows >= threshold:
            return tier.value

    return DiscountTier.NONE.value
