from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from income_model import IncomeModel, IncomeParseError, IncomeParser


class TestIncomeParser(unittest.TestCase):
    def test_parse_correct_line(self) -> None:
        income = IncomeParser.parse_line('Доходы 2024.03.28 "Зарплата" 50000')

        self.assertEqual(income.income_date, date(2024, 3, 28))
        self.assertEqual(income.source, "Зарплата")
        self.assertEqual(income.amount, 50000)

    def test_parse_source_with_spaces(self) -> None:
        income = IncomeParser.parse_line(
            'Доходы 2024.04.10 "Подработка в выходные" 7000'
        )

        self.assertEqual(income.source, "Подработка в выходные")
        self.assertEqual(income.amount, 7000)

    def test_parse_invalid_date(self) -> None:
        with self.assertRaises(IncomeParseError):
            IncomeParser.parse_line('Доходы 2024.99.28 "Зарплата" 50000')

    def test_parse_invalid_amount(self) -> None:
        with self.assertRaises(IncomeParseError):
            IncomeParser.parse_line('Доходы 2024.03.28 "Зарплата" пятьсот')

    def test_parse_invalid_format_without_quotes(self) -> None:
        with self.assertRaises(IncomeParseError):
            IncomeParser.parse_line("Доходы 2024.03.28 Зарплата 50000")

    def test_parse_negative_amount(self) -> None:
        with self.assertRaises(IncomeParseError):
            IncomeParser.parse_line('Доходы 2024.03.28 "Зарплата" -500')


class TestIncomeModel(unittest.TestCase):
    def test_add_income(self) -> None:
        model = IncomeModel()

        model.add_income("2024.03.28", "Зарплата", "50000")

        self.assertEqual(len(model.incomes), 1)
        self.assertEqual(model.incomes[0].source, "Зарплата")

    def test_remove_income(self) -> None:
        model = IncomeModel()
        model.add_income("2024.03.28", "Зарплата", "50000")

        model.remove_income(0)

        self.assertEqual(len(model.incomes), 0)

    def test_remove_income_with_wrong_index(self) -> None:
        model = IncomeModel()

        with self.assertRaises(IndexError):
            model.remove_income(0)

    def test_save_to_file(self) -> None:
        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "result.txt"
            model = IncomeModel()

            model.add_income("2024.03.28", "Зарплата", "50000")
            model.save_to_file(file_path)

            text = file_path.read_text(encoding="utf-8")
            self.assertIn('Доходы 2024.03.28 "Зарплата" 50000', text)

    def test_load_from_file_skips_invalid_lines(self) -> None:
        with TemporaryDirectory() as temp_dir:
            data_path = Path(temp_dir) / "data.txt"
            log_path = Path(temp_dir) / "errors.log"

            data_path.write_text(
                'Доходы 2024.03.28 "Зарплата" 50000\n'
                'Доходы 2024.99.28 "Ошибка даты" 1000\n'
                'Доходы 2024.04.10 "Подработка" 7000\n',
                encoding="utf-8",
            )

            model = IncomeModel()
            invalid_count = model.load_from_file(data_path, log_path)

            self.assertEqual(len(model.incomes), 2)
            self.assertEqual(invalid_count, 1)
            self.assertTrue(log_path.exists())
            self.assertIn("Ошибка", log_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()