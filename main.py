from pathlib import Path
import tkinter as tk

from income_model import IncomeModel
from income_view import IncomeView


BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data.txt"
LOG_FILE = BASE_DIR / "errors.log"


def main() -> None:
    root = tk.Tk()
    model = IncomeModel()
    IncomeView(root, model, DATA_FILE, LOG_FILE)
    root.mainloop()


if __name__ == "__main__":
    main()