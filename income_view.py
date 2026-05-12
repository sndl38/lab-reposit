from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from income_model import DATE_FORMAT, IncomeModel, IncomeParseError


class IncomeView:
    def __init__(
        self,
        root: tk.Tk,
        model: IncomeModel,
        data_path: Path,
        log_path: Path,
    ) -> None:
        self.root = root
        self.model = model
        self.data_path = data_path
        self.log_path = log_path

        self.date_entry: ttk.Entry
        self.source_entry: ttk.Entry
        self.amount_entry: ttk.Entry
        self.table: ttk.Treeview

        self.configure_window()
        self.create_widgets()
        self.load_data()

    def configure_window(self) -> None:
        self.root.title("Практическая работа 3 — Доходы")
        self.root.geometry("750x470")
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

        self.table.column("date", width=160, anchor="center")
        self.table.column("source", width=380, anchor="center")
        self.table.column("amount", width=160, anchor="center")

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

        ttk.Button(
            button_frame,
            text="Добавить",
            command=self.add_income,
        ).grid(row=0, column=0, padx=10)

        ttk.Button(
            button_frame,
            text="Удалить выбранный",
            command=self.delete_selected_income,
        ).grid(row=0, column=1, padx=10)

        ttk.Button(
            button_frame,
            text="Загрузить из файла",
            command=self.load_data,
        ).grid(row=0, column=2, padx=10)

    def load_data(self) -> None:
        invalid_count = self.model.load_from_file(self.data_path, self.log_path)
        self.update_table()

        if invalid_count > 0:
            messagebox.showinfo(
                "Загрузка данных",
                f"Некорректных строк пропущено: {invalid_count}.\n"
                f"Информация записана в файл: {self.log_path.name}",
            )

    def update_table(self) -> None:
        for row in self.table.get_children():
            self.table.delete(row)

        for row in self.model.get_table_rows():
            self.table.insert("", tk.END, values=row)

    def add_income(self) -> None:
        date_text = self.date_entry.get()
        source = self.source_entry.get()
        amount_text = self.amount_entry.get()

        try:
            self.model.add_income(date_text, source, amount_text)
        except IncomeParseError as error:
            messagebox.showwarning("Ошибка", str(error))
            return

        self.update_table()
        self.clear_source_and_amount_fields()

    def delete_selected_income(self) -> None:
        selected_item = self.table.selection()

        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите строку для удаления.")
            return

        selected_index = self.table.index(selected_item[0])

        try:
            self.model.remove_income(selected_index)
        except IndexError as error:
            messagebox.showwarning("Ошибка", str(error))
            return

        self.update_table()

    def clear_source_and_amount_fields(self) -> None:
        self.source_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)