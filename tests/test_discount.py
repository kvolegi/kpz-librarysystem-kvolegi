"""
test_discount.py — TDD: тести для функції розрахунку знижки.

Крок 1 (RED):  Тести написані ДО реалізації — вони мають падати.
Крок 2 (GREEN): Мінімальний код у src/services/discount.py.
Крок 3 (REFACTOR): Фінальна чиста версія.
"""

import pytest
from src.services.discount import calculate_discount, DiscountTier


class TestCalculateDiscount:
    """Тести для функції розрахунку знижки за лояльність."""

    # ── Базові випадки ──

    def test_no_discount_for_new_user(self):
        """Новий користувач (0 книг) — без знижки."""
        assert calculate_discount(total_borrows=0) == 0.0

    def test_no_discount_below_threshold(self):
        """Менше 10 книг — без знижки."""
        assert calculate_discount(total_borrows=5) == 0.0
        assert calculate_discount(total_borrows=9) == 0.0

    # ── Silver tier ──

    def test_silver_discount(self):
        """11-100 книг — знижка 5%."""
        assert calculate_discount(total_borrows=11) == 5.0
        assert calculate_discount(total_borrows=50) == 5.0
        assert calculate_discount(total_borrows=100) == 5.0

    # ── Gold tier ──

    def test_gold_discount(self):
        """Більше 100 книг — знижка 10%."""
        assert calculate_discount(total_borrows=101) == 10.0
        assert calculate_discount(total_borrows=500) == 10.0

    # ── Platinum tier ──

    def test_platinum_discount(self):
        """Більше 500 книг — знижка 15%."""
        assert calculate_discount(total_borrows=501) == 15.0
        assert calculate_discount(total_borrows=1000) == 15.0

    # ── Граничні значення (Boundary) ──

    def test_boundary_silver(self):
        """Межа Silver: 10 = ні, 11 = так."""
        assert calculate_discount(total_borrows=10) == 0.0
        assert calculate_discount(total_borrows=11) == 5.0

    def test_boundary_gold(self):
        """Межа Gold: 100 = Silver, 101 = Gold."""
        assert calculate_discount(total_borrows=100) == 5.0
        assert calculate_discount(total_borrows=101) == 10.0

    def test_boundary_platinum(self):
        """Межа Platinum: 500 = Gold, 501 = Platinum."""
        assert calculate_discount(total_borrows=500) == 10.0
        assert calculate_discount(total_borrows=501) == 15.0

    # ── Невалідний ввід ──

    def test_negative_borrows_returns_zero(self):
        """Від'ємне значення — 0% знижки."""
        assert calculate_discount(total_borrows=-1) == 0.0

    # ── Перевірка DiscountTier ──

    def test_discount_tier_enum(self):
        """DiscountTier має правильні значення."""
        assert DiscountTier.NONE.value == 0.0
        assert DiscountTier.SILVER.value == 5.0
        assert DiscountTier.GOLD.value == 10.0
        assert DiscountTier.PLATINUM.value == 15.0
