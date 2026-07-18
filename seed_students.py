import sqlite3

connection = sqlite3.connect("students.db")
cursor = connection.cursor()

students = [

    ("ST001", "2024/1/95339CP", "Ridwanullahi Apana Ali", "12345"),

    ("ST002", "2024/1/95349CP", "Ibrahim Mikail Opadel", "12345"),

    ("ST003", "2023/1/90228CP", "Abdulbasit Bello", "12345"),

    ("ST004", "2022/1/90237CP", "David John", "12345"),

    ("ST005", "2024/1/96449CP", "Sulyman Yusuf", "12345"),

    ("ST006", "2024/1/89679CP", "Mashood Abdulbasit Ayinde", "12345")

]

cursor.executemany("""
INSERT OR IGNORE INTO students
(student_id, matric_number, full_name, password)
VALUES (?, ?, ?, ?)
""", students)

connection.commit()

print("Students inserted successfully!")

connection.close()