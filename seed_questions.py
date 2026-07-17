import sqlite3

connection = sqlite3.connect("students.db")
cursor = connection.cursor()

questions = [
    (
        "Applied Electricity I",
        2024,
        "What is Ohm's Law?",
        "V = IR",
        "P = IV",
        "I = R²",
        "R = V²",
        "A"
    ),
    (
        "Applied Electricity I",
        2024,
        "The SI unit of electric current is:",
        "Volt",
        "Ampere",
        "Ohm",
        "Watt",
        "B"
    )
]

cursor.executemany("""
INSERT INTO questions (
    course,
    year,
    question,
    option_a,
    option_b,
    option_c,
    option_d,
    correct_answer
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", questions)

connection.commit()

print(f"{cursor.rowcount} questions inserted successfully!")

connection.close()