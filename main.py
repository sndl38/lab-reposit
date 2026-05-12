from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import shlex
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


DATA_FILE = Path(__file__).with_name("data.txt")
DATE_FORMAT = "%Y.%m.%d"


@dataclass
class Income:
    income_date: date
    source: str
    amount: int


def parse_income(line: str) -> Income:
    parts = shlex.split(line)

    income_date = datetime.strptime(parts[1], DATE_FORMAT).date()
    source = parts[2]
    amount = int(parts[3])

    return Income(income_date=income_date, source=source, amount=amount)


def read_incomes_from_file(file_path: Path) -> list[Income]:
    incomes = []

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                incomes.append(parse_income(line))

    return incomes


def income_to_table_row(income: Income) -> tuple[str, str, str]:
    return (
        income.income_date.strftime(DATE_FORMAT),
        income.source,
        str(income.amount),
    )


def create_income_from_fields(date_text: str, source: str, amount_text: str) -> Income:
    income_date = datetime.strptime(date_text, DATE_FORMAT).date()
    amount = int(amount_text)

    return Income(income_date=income_date, source=source, amount=amount)


class IncomeApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.incomes: list[Income] = []

        self.date_entry: ttk.Entry
        self.source_entry: ttk.Entry
        self.amount_entry: ttk.Entry
        self.table: ttk.Treeview

        self.configure_window()
        self.create_widgets()
        self.load_initial_data()

    def configure_window(self) -> None:
        self.root.title("Практическая работа 2 — Доходы")
        self.root.geometry("700x450")
        self.root.resizable(False, False)

    def create_widgets(self) -> None:
        title_label = ttk.Label(
            self.root,
            text="Список доходов",
            font=("Arial", 16),
        )
        title_label.pack(pady=10)

        self.create_table()
        self.create_input_form()
        self.create_buttons()

    def create_table(self) -> None:
        columns = ("date", "source", "amount")

        self.table = ttk.Treeview(
            self.root,
            columns=columns,
            show="headings",
            height=10,
        )

        self.table.heading("date", text="Дата")
        self.table.heading("source", text="Источник")
        self.table.heading("amount", text="Сумма")

        self.table.column("date", width=150, anchor="center")
        self.table.column("source", width=350, anchor="center")
        self.table.column("amount", width=150, anchor="center")

        self.table.pack(pady=10)

    def create_input_form(self) -> None:
        form_frame = ttk.Frame(self.root)
        form_frame.pack(pady=10)

        ttk.Label(form_frame, text="Дата:").grid(row=0, column=0, padx=5)
        self.date_entry = ttk.Entry(form_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5)
        self.date_entry.insert(0, "2024.05.20")

        ttk.Label(form_frame, text="Источник:").grid(row=0, column=2, padx=5)
        self.source_entry = ttk.Entry(form_frame, width=25)
        self.source_entry.grid(row=0, column=3, padx=5)

        ttk.Label(form_frame, text="Сумма:").grid(row=0, column=4, padx=5)
        self.amount_entry = ttk.Entry(form_frame, width=15)
        self.amount_entry.grid(row=0, column=5, padx=5)

    def create_buttons(self) -> None:
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        add_button = ttk.Button(
            button_frame,
            text="Добавить",
            command=self.add_income,
        )
        add_button.grid(row=0, column=0, padx=10)

        delete_button = ttk.Button(
            button_frame,
            text="Удалить выбранный",
            command=self.delete_selected_income,
        )
        delete_button.grid(row=0, column=1, padx=10)

        reload_button = ttk.Button(
            button_frame,
            text="Загрузить из файла",
            command=self.load_initial_data,
        )
        reload_button.grid(row=0, column=2, padx=10)

    def load_initial_data(self) -> None:
        self.incomes = read_incomes_from_file(DATA_FILE)
        self.update_table()

    def update_table(self) -> None:
        for row in self.table.get_children():
            self.table.delete(row)

        for income in self.incomes:
            self.table.insert("", tk.END, values=income_to_table_row(income))

    def add_income(self) -> None:
        date_text = self.date_entry.get()
        source = self.source_entry.get()
        amount_text = self.amount_entry.get()

        if not date_text or not source or not amount_text:
            messagebox.showwarning("Ошибка", "Заполните все поля.")
            return

        try:
            income = create_income_from_fields(date_text, source, amount_text)
        except ValueError:
            messagebox.showwarning(
                "Ошибка",
                "Проверьте формат данных: дата гггг.мм.дд, сумма — целое число.",
            )
            return

        self.incomes.append(income)
        self.update_table()
        self.clear_source_and_amount_fields()

    def delete_selected_income(self) -> None:
        selected_item = self.table.selection()

        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите строку для удаления.")
            return

        selected_index = self.table.index(selected_item[0])
        del self.incomes[selected_index]

        self.update_table()

    def clear_source_and_amount_fields(self) -> None:
        self.source_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)


def main() -> None:
    root = tk.Tk()
    app = IncomeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()