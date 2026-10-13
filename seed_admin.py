
"""Provision the first ExamHub administrator for a newly initialized database.

Run after `python init_db.py`.
Never use this script to reset an existing administrator's password.
"""

import getpass
import sqlite3

from database import DATABASE
from werkzeug.security import generate_password_hash


def main():
    if not DATABASE.is_file():
        raise SystemExit("Database not found. Run `python init_db.py` first.")

    with sqlite3.connect(DATABASE) as connection:
        try:
            count = connection.execute(
                "SELECT COUNT(*) FROM admins"
            ).fetchone()[0]
        except sqlite3.OperationalError as exc:
            raise SystemExit(
                "Admins table missing. Run `python init_db.py` first."
            ) from exc

        if count:
            raise SystemExit(
                "An administrator already exists. No changes made."
            )

        username = input("New admin username: ").strip()
        if not username:
            raise SystemExit("Username cannot be empty. No changes made.")

        password = getpass.getpass("New admin password: ")
        confirmation = getpass.getpass("Confirm admin password: ")

        if password != confirmation:
            raise SystemExit("Passwords do not match. No changes made.")

        if len(password) < 12:
            raise SystemExit(
                "Use a password of at least 12 characters. No changes made."
            )

        connection.execute(
            "INSERT INTO admins (username, password) VALUES (?, ?)",
            (username, generate_password_hash(password)),
        )
        connection.commit()

    print(f"Administrator '{username}' created successfully.")


if __name__ == "__main__":
    main()
