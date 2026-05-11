"""
penalty_strategy.py — Strategy патерн для розрахунку штрафів.

Патерн Strategy визначає сімейство алгоритмів, інкапсулює кожен
з них і робить їх взаємозамінними.

Стратегії:
  - FixedPenaltyStrategy: Фіксована ставка за день.
  - ProgressivePenaltyStrategy: Зростаюча ставка з часом.
  - FreePenaltyStrategy: Без штрафу (пільговий період).
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional


class PenaltyStrategy(ABC):
    """Абстрактна стратегія розрахунку штрафу."""

    @abstractmethod
    def calculate(self, days_overdue: int) -> float:
        """Розрахувати штраф за кількість прострочених днів.

        Args:
            days_overdue: Кількість днів прострочення.

        Returns:
            Сума штрафу в гривнях.
        """
        ...

    @abstractmethod
    def get_name(self) -> str:
        """Назва стратегії."""
        ...


class FixedPenaltyStrategy(PenaltyStrategy):
    """Фіксована ставка штрафу за кожен день прострочення.

    Приклад: 5.50 грн × кількість днів.
    """

    def __init__(self, daily_rate: float = 5.50):
        self._daily_rate = daily_rate

    def calculate(self, days_overdue: int) -> float:
        if days_overdue <= 0:
            return 0.0
        return days_overdue * self._daily_rate

    def get_name(self) -> str:
        return f"Фіксована ({self._daily_rate} грн/день)"


class ProgressivePenaltyStrategy(PenaltyStrategy):
    """Прогресивна ставка штрафу — зростає з часом.

    - 1-7 днів: базова ставка
    - 8-14 днів: подвійна ставка
    - 15+ днів: потрійна ставка
    """

    def __init__(self, base_rate: float = 3.00):
        self._base_rate = base_rate

    def calculate(self, days_overdue: int) -> float:
        if days_overdue <= 0:
            return 0.0

        total = 0.0
        for day in range(1, days_overdue + 1):
            if day <= 7:
                total += self._base_rate
            elif day <= 14:
                total += self._base_rate * 2
            else:
                total += self._base_rate * 3
        return total

    def get_name(self) -> str:
        return f"Прогресивна (від {self._base_rate} грн/день)"


class FreePenaltyStrategy(PenaltyStrategy):
    """Пільговий період — без штрафу (для студентів, працівників бібліотеки тощо)."""

    def __init__(self, grace_period_days: int = 7):
        self._grace_period = grace_period_days

    def calculate(self, days_overdue: int) -> float:
        if days_overdue <= self._grace_period:
            return 0.0
        # Після пільгового періоду — стандартна ставка
        effective_days = days_overdue - self._grace_period
        return effective_days * 5.50

    def get_name(self) -> str:
        return f"Пільгова ({self._grace_period} днів без штрафу)"


# =============================================================================
# Контекст, що використовує стратегію
# =============================================================================

class PenaltyCalculator:
    """Контекст для обчислення штрафів з використанням стратегії.

    Використання:
        calculator = PenaltyCalculator(FixedPenaltyStrategy(5.50))
        penalty = calculator.compute(due_date=..., return_date=...)

        # Зміна стратегії в runtime:
        calculator.set_strategy(ProgressivePenaltyStrategy())
    """

    def __init__(self, strategy: PenaltyStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: PenaltyStrategy) -> None:
        """Змінити стратегію розрахунку.

        Args:
            strategy: Нова стратегія.
        """
        self._strategy = strategy

    def compute(
        self,
        due_date: datetime,
        return_date: Optional[datetime] = None,
    ) -> float:
        """Обчислити штраф.

        Args:
            due_date: Дата, до якої мала бути повернена книга.
            return_date: Фактична дата повернення (None = зараз).

        Returns:
            Сума штрафу.
        """
        actual_return = return_date or datetime.now()
        if actual_return <= due_date:
            return 0.0

        days_overdue = (actual_return - due_date).days
        return self._strategy.calculate(days_overdue)

    def get_strategy_name(self) -> str:
        """Отримати назву поточної стратегії."""
        return self._strategy.get_name()
