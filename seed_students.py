import sqlite3

connection = sqlite3.connect("students.db")
cursor = connection.cursor()

cursor.execute("""
INSERT INTO students(student_id, matric_number, full_name, password)
VALUES (?, ?, ?, ?)
""", (
    "UGE34",
    "2024/1/95339CP",
    "Ridwanullahi Apana",
    "916718"
))

connection.commit()

print("Student inserted successfully!")

connection.close()