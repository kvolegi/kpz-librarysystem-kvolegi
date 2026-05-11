"""
bad_service.py — Code Smells: Magic Numbers та Long Method.

Цей файл навмисно містить антипатерни для демонстрації рефакторингу.
"""


class BadBookService:
    """Сервіс з Code Smells."""

    def process_borrow_request(self, user_data: dict, book_data: dict) -> dict:
        """Long Method: 1 метод робить все — валідація, бізнес-логіка, форматування.

        Magic Numbers: числові константи без пояснення.
        """
        # -- Валідація користувача (має бути окремо) --
        if not user_data.get("name"):
            return {"status": "error", "message": "No name"}
        if not user_data.get("email"):
            return {"status": "error", "message": "No email"}
        if len(user_data.get("name", "")) < 2:
            return {"status": "error", "message": "Name too short"}
        if "@" not in user_data.get("email", ""):
            return {"status": "error", "message": "Invalid email"}

        # -- Валідація книги (має бути окремо) --
        if not book_data.get("title"):
            return {"status": "error", "message": "No title"}
        if book_data.get("available", 0) <= 0:
            return {"status": "error", "message": "Not available"}

        # -- Перевірка ліміту (Magic Number: 5) --
        current_borrows = user_data.get("current_borrows", 0)
        if current_borrows >= 5:  # Magic Number!
            return {"status": "error", "message": "Limit reached"}

        # -- Розрахунок терміну (Magic Number: 14) --
        from datetime import datetime, timedelta
        borrow_date = datetime.now()
        due_date = borrow_date + timedelta(days=14)  # Magic Number!

        # -- Розрахунок знижки (Magic Numbers: 10, 0.1, 100, 0.05, 0.0) --
        borrows_total = user_data.get("total_borrows", 0)
        if borrows_total > 100:  # Magic Number!
            discount = 0.1  # Magic Number!
        elif borrows_total > 10:  # Magic Number!
            discount = 0.05  # Magic Number!
        else:
            discount = 0.0

        # -- Розрахунок депозиту (Magic Number: 50.0) --
        deposit = 50.0  # Magic Number!
        deposit_with_discount = deposit * (1 - discount)

        # -- Формування відповіді (має бути окремо) --
        result = {
            "status": "success",
            "user": user_data["name"],
            "book": book_data["title"],
            "borrow_date": borrow_date.isoformat(),
            "due_date": due_date.isoformat(),
            "deposit": round(deposit_with_discount, 2),
            "discount_percent": discount * 100,
            "message": f"Книга '{book_data['title']}' видана {user_data['name']}",
        }

        return result
