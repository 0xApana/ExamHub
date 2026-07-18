from flask import Flask, render_template,request, redirect, url_for,  flash, session
from database import get_db_connection
import random

app= Flask(__name__)
app.secret_key = "examhub_secret_key"

@app.route("/")
def home():
    return render_template("index.html")

# @app.route("/home")
# def home():
#     return render_template(url_for("Home"))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        matric = request.form.get("matric")
        password = request.form.get("password")

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
        SELECT *
        FROM students
        WHERE matric_number = ?
        AND password = ?
        """, (matric, password))

        student = cursor.fetchone()

        if student:
            session["student_id"] = student["id"]
            connection.close()
            return redirect(url_for("dashboard"))

        connection.close()
        flash("Invalid Matric Number or Password.")
        return redirect(url_for("login"))
    
    return render_template("login.html")
    

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/student/<name>")
def student(name):
    return f"Welcome, {name}!"

@app.route("/dashboard")
def dashboard():

    if "student_id" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (session["student_id"],)
    )

    student = cursor.fetchone()
    cursor.execute("""
        SELECT 
              course,
              COUNT(*)  AS total_questios
        FROM questions
        GROUP BY course
        ORDER BY course                                         
""")

    courses = cursor.fetchall()

    connection.close()

    return render_template(
        "dashboard.html",
        student=student,
        courses=courses
    )

@app.route("/start_exam", methods=["POST"])
def start_exam():

    session["selected_course"] = request.form["course"]
    session["exam_size"] = int(request.form["exam_size"])

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM questions
        WHERE course = ?
    """, (session["selected_course"],))

    question_ids = [row["id"] for row in cursor.fetchall()]

    connection.close()

    import random

    if session["exam_size"] > len(question_ids):
        session["exam_size"] = len(question_ids)

    session["exam_questions"] = random.sample(
        question_ids,
        session["exam_size"]
    )

    session["current_question"] = 0
    session["answers"] = {}

    return redirect(url_for("exam"))

@app.route("/next")
def next_question():

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT COUNT(*) FROM questions
    WHERE course = ?
    """, (session["selected_course"],))

    total_questions = cursor.fetchone()[0]

    connection.close()

    if session["current_question"] < total_questions - 1:
        session["current_question"] += 1

    return redirect(url_for("exam"))

@app.route("/previous")
def previous_question():

    if session["current_question"] > 0:
        session["current_question"] -= 1

    return redirect(url_for("exam"))

@app.route("/save_answer", methods=["POST"])
def save_answer():

    question_id = request.form.get("question_id")
    answer = request.form.get("answer")

    answers = session.get("answers", {})

    answers[question_id] = answer

    session["answers"] = answers

    total_questions = len(session["exam_questions"])

    if session["current_question"] < total_questions - 1:
        session["current_question"] += 1

        return redirect(url_for("exam"))

    return redirect(url_for("submit_exam"))

@app.route("/submit_exam")
def submit_exam():

    answers = session.get("answers", {})

    connection = get_db_connection()
    cursor = connection.cursor()

    score = 0

    for question_id, student_answer in answers.items():

        cursor.execute("""
        SELECT correct_answer
        FROM questions
        WHERE id = ?
        """, (question_id,))

        question = cursor.fetchone()

        if question and student_answer == question["correct_answer"]:
            score += 1

    total_questions = len(answers)

    connection.close()

    return render_template(
        "result.html",
        score=score,
        total=total_questions
    )



@app.route("/exam")
def exam():

    
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT *
    FROM questions
    WHERE course = ?
    ORDER BY id
    """, (session["selected_course"],))

    all_questions = cursor.fetchall()

    selected_ids = session["exam_questions"]

    questions = [
      q for q in all_questions
      if q["id"] in selected_ids
]

    

    if request.args.get("new") == "1":
        session["current_question"] = 0
        session["answers"] = {}

    if "current_question" not in session:
        session["current_question"] = 0

    if "answers" not in session:
        session["answers"] = {}
    
    question = questions[session["current_question"]]

    connection.close()

    return render_template(
    "exam.html",
    question=question,
    current=session["current_question"] + 1,
    total=len(questions),
    is_last=(session["current_question"] == len(questions) - 1),
    selected_answer=session.get("answers", {}).get(str(question["id"]))
)

@app.route("/logout")
def logout():
    session.pop("student",None)
    flash("logout successful.")
    return redirect(url_for("login"))
    


if __name__ == "__main__":
    app.run(debug=True)
