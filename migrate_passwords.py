"""One-time, repeat-safe password migration for ExamHub.

Run only after deploying login handlers that use check_password_hash().
Requires a backup of students.db. Never commit the database or backup.
"""
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

DB_PATH = Path(__file__).resolve().parent / 'students.db'
HASH_PREFIXES = ('scrypt:', 'pbkdf2:')


def main():
    if not DB_PATH.is_file():
        raise SystemExit('students.db not found beside this script; no changes made.')
    with sqlite3.connect(DB_PATH) as db:
        db.execute('BEGIN IMMEDIATE')
        for table in ('students', 'admins'):
            rows = db.execute(f'SELECT id, password FROM {table}').fetchall()
            converted = 0
            for account_id, stored in rows:
                if not isinstance(stored, str) or not stored:
                    raise ValueError(f'{table} account {account_id} has an empty/invalid password; rolled back')
                if stored.startswith(HASH_PREFIXES):
                    continue
                db.execute(
                    f'UPDATE {table} SET password = ? WHERE id = ?',
                    (generate_password_hash(stored), account_id),
                )
                converted += 1
            print(f'{table}: {converted} passwords converted, {len(rows)-converted} already hashed')
    print('Migration committed successfully.')


if __name__ == '__main__':
    main()
