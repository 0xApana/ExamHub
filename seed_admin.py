import sqlite3

connection = sqlite3.connect("students.db")
cursor = connection.cursor()

cursor.execute("""
INSERT OR IGNORE INTO admins(username, password)
VALUES (?, ?)
""", (
    "admin",
    "admin123"
))

connection.commit()
connection.close()

print("Admin created successfully!")