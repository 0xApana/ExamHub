import sqlite3

from question_bank.applied_electricity_ii import questions as ae_questions
from question_bank.engineering_math_ii import questions as em_questions

connection = sqlite3.connect("students.db")
cursor = connection.cursor()


cursor.execute("DELETE FROM questions")

connection.commit()


all_questions = ae_questions + em_questions


for q in all_questions:

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

print(f"✅ {len(all_questions)} questions inserted successfully!")