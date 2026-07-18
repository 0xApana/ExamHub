import sqlite3

connection = sqlite3.connect("students.db")
cursor = connection.cursor()

# ==========================
# STUDENTS TABLE
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE NOT NULL,
    matric_number TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    password TEXT NOT NULL
)
""")

# ==========================
# QUESTIONS TABLE
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS questions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course TEXT NOT NULL,
    year INTEGER NOT NULL,
    question TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer TEXT NOT NULL
)
""")

connection.commit()

print("Database initialized successfully!")

connection.close()