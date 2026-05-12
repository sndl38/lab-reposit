from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import re


DATE_FORMAT = "%Y.%m.%d"


class IncomeParseError(Exception):
    """Ошибка разбора строки с данными о доходе."""


@dataclass(frozen=True)
class Income:
    income_date: date
    source: str
    amount: int

    def to_row(self) -> tuple[str, str, str]:
        return (
            self.income_date.strftime(DATE_FORMAT),
            self.source,
            str(self.amount),
        )

    def to_file_line(self) -> str:
        safe_source = self.source.replace('"', "'")
        return (
            f'Доходы {self.income_date.strftime(DATE_FORMAT)} '
            f'"{safe_source}" {self.amount}'
        )


class IncomeParser:
    LINE_PATTERN = re.compile(
        r'^Доходы\s+(\d{4}\.\d{2}\.\d{2})\s+"([^"]+)"\s+(\S+)\s*$'
    )

    @classmethod
    def parse_line(cls, line: str) -> Income:
        line = line.strip()

        if not line:
            raise IncomeParseError("Пустая строка.")

        match = cls.LINE_PATTERN.match(line)

        if not match:
            raise IncomeParseError(
                'Строка должна иметь формат: Доходы гггг.мм.дд "источник" сумма.'
            )

        date_text, source, amount_text = match.groups()
        return cls.create_income(date_text, source, amount_text)

    @staticmethod
    def create_income(date_text: str, source: str, amount_text: str) -> Income:
        if not source.strip():
            raise IncomeParseError("Источник дохода не может быть пустым.")

        try:
            income_date = datetime.strptime(date_text, DATE_FORMAT).date()
        except ValueError as error:
            raise IncomeParseError(
                "Дата должна быть указана в формате гггг.мм.дд."
            ) from error

        try:
            amount = int(amount_text)
        except ValueError as error:
            raise IncomeParseError("Сумма должна быть целым числом.") from error

        if amount < 0:
            raise IncomeParseError("Сумма не может быть отрицательной.")

        return Income(
            income_date=income_date,
            source=source,
            amount=amount,
        )


class IncomeModel:
    def __init__(self) -> None:
        self._incomes: list[Income] = []

    @property
    def incomes(self) -> list[Income]:
        return self._incomes.copy()

    def load_from_file(self, file_path: Path, log_path: Path) -> int:
        self._incomes.clear()
        invalid_count = 0

        with open(file_path, "r", encoding="utf-8") as input_file, open(
            log_path,
            "w",
            encoding="utf-8",
        ) as log_file:
            for line_number, line in enumerate(input_file, start=1):
                try:
                    income = IncomeParser.parse_line(line)
                except IncomeParseError as error:
                    invalid_count += 1
                    log_file.write(
                        f"Строка {line_number}: {line.strip()} | Ошибка: {error}\n"
                    )
                else:
                    self._incomes.append(income)

        return invalid_count

    def add_income(self, date_text: str, source: str, amount_text: str) -> None:
        income = IncomeParser.create_income(date_text, source, amount_text)
        self._incomes.append(income)

    def add_income_object(self, income: Income) -> None:
        self._incomes.append(income)

    def remove_income(self, index: int) -> None:
        if index < 0 or index >= len(self._incomes):
            raise IndexError("Некорректный индекс удаляемого объекта.")

        del self._incomes[index]

    def remove_by_condition(self, condition) -> int:
        old_count = len(self._incomes)
        self._incomes = [
            income for income in self._incomes if not condition(income)
        ]
        return old_count - len(self._incomes)

    def save_to_file(self, file_path: Path) -> None:
        with open(file_path, "w", encoding="utf-8") as file:
            for income in self._incomes:
                file.write(income.to_file_line() + "\n")

    def get_table_rows(self) -> list[tuple[str, str, str]]:
        return [income.to_row() for income in self._incomes]