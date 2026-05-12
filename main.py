from dataclasses import dataclass
from datetime import datetime
import shlex


@dataclass
class Income:
    date: datetime.date
    source: str
    amount: int


def parse_income(line: str) -> Income:
    parts = shlex.split(line)

    object_type = parts[0]
    date_text = parts[1]
    source = parts[2]
    amount_text = parts[3]

    date = datetime.strptime(date_text, "%Y.%m.%d").date()
    amount = int(amount_text)

    return Income(date=date, source=source, amount=amount)


def print_income(income: Income) -> None:
    print("Сформирован объект:")
    print(f"Дата: {income.date}")
    print(f"Источник: {income.source}")
    print(f"Сумма: {income.amount}")


def main() -> None:
    line = input("Введите данные о доходе: ")

    income = parse_income(line)

    print_income(income)


if __name__ == "__main__":
    main()