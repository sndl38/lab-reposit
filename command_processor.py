import csv
import re
from datetime import datetime
from pathlib import Path

from income_model import DATE_FORMAT, Income, IncomeModel, IncomeParser


class CommandError(Exception):
    """Ошибка обработки команды."""


class CommandProcessor:
    CONDITION_PATTERN = re.compile(
        r"^(date|дата|source|источник|amount|сумма|sum)\s*"
        r"(<=|>=|==|!=|<|>)\s*(.+)$"
    )

    FIELD_NAMES = {
        "date": "date",
        "дата": "date",
        "source": "source",
        "источник": "source",
        "amount": "amount",
        "сумма": "amount",
        "sum": "amount",
    }

    def __init__(self, model: IncomeModel, base_dir: Path) -> None:
        self.model = model
        self.base_dir = base_dir

    def execute_file(self, command_path: Path) -> list[str]:
        messages = []

        with open(command_path, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()

                if not line:
                    continue

                try:
                    message = self.execute_line(line)
                except (CommandError, ValueError) as error:
                    messages.append(f"Строка {line_number}: ошибка — {error}")
                else:
                    messages.append(f"Строка {line_number}: {message}")

        return messages

    def execute_line(self, line: str) -> str:
        if line.startswith("ADD "):
            return self._execute_add(line[4:].strip())

        if line.startswith("REM "):
            return self._execute_rem(line[4:].strip())

        if line.startswith("SAVE "):
            return self._execute_save(line[5:].strip())

        raise CommandError("Неизвестная команда.")

    def _execute_add(self, data_text: str) -> str:
        fields = self._parse_csv(data_text)

        if len(fields) == 4:
            object_type, date_text, source, amount_text = fields

            if object_type.lower() not in ("доходы", "income"):
                raise CommandError("Команда ADD поддерживает только объект Доходы.")

        elif len(fields) == 3:
            date_text, source, amount_text = fields

        else:
            raise CommandError(
                "ADD должен иметь формат: ADD Доходы;дата;источник;сумма."
            )

        income = IncomeParser.create_income(date_text, source, amount_text)
        self.model.add_income_object(income)

        return "объект добавлен"

    def _execute_rem(self, condition_text: str) -> str:
        condition = self._create_condition(condition_text)
        removed_count = self.model.remove_by_condition(condition)

        return f"удалено объектов: {removed_count}"

    def _execute_save(self, filename: str) -> str:
        if not filename:
            raise CommandError("Не указано имя файла для сохранения.")

        file_path = Path(filename)

        if not file_path.is_absolute():
            file_path = self.base_dir / file_path

        self.model.save_to_file(file_path)

        return f"данные сохранены в файл {file_path.name}"

    @staticmethod
    def _parse_csv(text: str) -> list[str]:
        reader = csv.reader([text], delimiter=";", skipinitialspace=True)
        return [item.strip() for item in next(reader)]

    def _create_condition(self, condition_text: str):
        match = self.CONDITION_PATTERN.match(condition_text.strip())

        if not match:
            raise CommandError(
                "Условие должно иметь формат: поле оператор значение."
            )

        field_name, operator, value_text = match.groups()
        field = self.FIELD_NAMES[field_name]
        value_text = self._clean_value(value_text)

        def condition(income: Income) -> bool:
            left_value, right_value = self._get_values_for_compare(
                income,
                field,
                value_text,
            )
            return self._compare(left_value, operator, right_value)

        return condition

    @staticmethod
    def _clean_value(value_text: str) -> str:
        value_text = value_text.strip()

        if len(value_text) >= 2 and value_text[0] == '"' and value_text[-1] == '"':
            return value_text[1:-1]

        return value_text

    @staticmethod
    def _get_values_for_compare(
        income: Income,
        field: str,
        value_text: str,
    ):
        if field == "amount":
            return income.amount, int(value_text)

        if field == "date":
            right_date = datetime.strptime(value_text, DATE_FORMAT).date()
            return income.income_date, right_date

        if field == "source":
            return income.source, value_text

        raise CommandError("Неизвестное поле условия.")

    @staticmethod
    def _compare(left_value, operator: str, right_value) -> bool:
        if operator == "==":
            return left_value == right_value

        if operator == "!=":
            return left_value != right_value

        if operator == "<":
            return left_value < right_value

        if operator == ">":
            return left_value > right_value

        if operator == "<=":
            return left_value <= right_value

        if operator == ">=":
            return left_value >= right_value

        raise CommandError("Неизвестный оператор сравнения.")