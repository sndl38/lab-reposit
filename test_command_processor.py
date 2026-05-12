from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from command_processor import CommandError, CommandProcessor
from income_model import IncomeModel


class TestCommandProcessor(unittest.TestCase):
    def test_add_command(self) -> None:
        model = IncomeModel()
        processor = CommandProcessor(model, Path("."))

        processor.execute_line("ADD Доходы;2024.06.01;Подарок;3000")

        self.assertEqual(len(model.incomes), 1)
        self.assertEqual(model.incomes[0].source, "Подарок")
        self.assertEqual(model.incomes[0].amount, 3000)

    def test_add_command_without_object_type(self) -> None:
        model = IncomeModel()
        processor = CommandProcessor(model, Path("."))

        processor.execute_line("ADD 2024.06.01;Подарок;3000")

        self.assertEqual(len(model.incomes), 1)
        self.assertEqual(model.incomes[0].source, "Подарок")

    def test_remove_by_amount_condition(self) -> None:
        model = IncomeModel()
        model.add_income("2024.03.28", "Зарплата", "50000")
        model.add_income("2024.04.15", "Стипендия", "3500")

        processor = CommandProcessor(model, Path("."))
        processor.execute_line("REM amount < 5000")

        self.assertEqual(len(model.incomes), 1)
        self.assertEqual(model.incomes[0].source, "Зарплата")

    def test_remove_by_source_condition(self) -> None:
        model = IncomeModel()
        model.add_income("2024.03.28", "Зарплата", "50000")
        model.add_income("2024.04.15", "Стипендия", "3500")

        processor = CommandProcessor(model, Path("."))
        processor.execute_line('REM source == "Стипендия"')

        self.assertEqual(len(model.incomes), 1)
        self.assertEqual(model.incomes[0].source, "Зарплата")

    def test_remove_by_date_condition(self) -> None:
        model = IncomeModel()
        model.add_income("2024.03.28", "Зарплата", "50000")
        model.add_income("2024.05.01", "Премия", "12000")

        processor = CommandProcessor(model, Path("."))
        processor.execute_line("REM date < 2024.04.01")

        self.assertEqual(len(model.incomes), 1)
        self.assertEqual(model.incomes[0].source, "Премия")

    def test_save_command(self) -> None:
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            model = IncomeModel()
            model.add_income("2024.03.28", "Зарплата", "50000")

            processor = CommandProcessor(model, base_dir)
            processor.execute_line("SAVE result.txt")

            result_path = base_dir / "result.txt"
            self.assertTrue(result_path.exists())
            self.assertIn("Зарплата", result_path.read_text(encoding="utf-8"))

    def test_execute_file(self) -> None:
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            command_path = base_dir / "commands.txt"

            command_path.write_text(
                "ADD Доходы;2024.06.01;Подарок;3000\n"
                "ADD Доходы;2024.06.05;Фриланс;18000\n"
                "REM amount < 5000\n"
                "SAVE result.txt\n",
                encoding="utf-8",
            )

            model = IncomeModel()
            processor = CommandProcessor(model, base_dir)
            messages = processor.execute_file(command_path)

            self.assertEqual(len(model.incomes), 1)
            self.assertEqual(model.incomes[0].source, "Фриланс")
            self.assertTrue((base_dir / "result.txt").exists())
            self.assertEqual(len(messages), 4)

    def test_unknown_command(self) -> None:
        model = IncomeModel()
        processor = CommandProcessor(model, Path("."))

        with self.assertRaises(CommandError):
            processor.execute_line("EDIT something")


if __name__ == "__main__":
    unittest.main()