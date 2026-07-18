import sqlite3
from question_bank.applied_electricity_ii import questions

connection = sqlite3.connect("students.db")
cursor = connection.cursor()

# Optional: Clear existing Applied Electricity II questions
cursor.execute(
    "DELETE FROM questions WHERE course = ?",
    ("Applied Electricity II",)
)

for q in questions:
    cursor.execute("""
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
    """, (
        q["course"],
        q["year"],
        q["question"],
        q["option_a"],
        q["option_b"],
        q["option_c"],
        q["option_d"],
        q["correct_answer"]
    ))

connection.commit()
connection.close()

print(f"✅ {len(questions)} questions inserted successfully!")