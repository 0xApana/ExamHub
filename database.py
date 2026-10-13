import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATABASE = Path(
    os.environ.get(
        "EXAMHUB_DATABASE",
        str(BASE_DIR / "students.db")
    )
).expanduser()


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection