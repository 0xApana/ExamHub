from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from database import get_db_connection
import random
import time
import os
import secrets
from datetime import timedelta
from functools import wraps
from pathlib import Path
from werkzeug.security import check_password_hash


app= Flask(__name__)
# Set EXAMHUB_SECRET_KEY in production. Local development uses a persistent,
# untracked key file so restarting Flask does not invalidate every session.
secret = os.environ.get("EXAMHUB_SECRET_KEY")
if not secret:
    key_file = Path(__file__).resolve().parent / ".examhub_secret_key"
    if key_file.exists():
        secret = key_file.read_text(encoding="utf-8").strip()
    else:
        secret = secrets.token_hex(32)
        key_file.write_text(secret, encoding="utf-8")
app.secret_key = secret
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("EXAMHUB_HTTPS") == "1",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=2),
)


def student_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "student_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "admin_id" not in session:
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped


def active_exam_required(view):
    @wraps(view)
    @student_required
    def wrapped(*args, **kwargs):
        if not session.get("exam_questions") or "exam_start_time" not in session:
            flash("Start an exam from your dashboard.")
            return redirect(url_for("dashboard"))
        return view(*args, **kwargs)
    return wrapped


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
        matric = (request.form.get("matric") or "").strip()
        password = request.form.get("password") or ""
        connection = get_db_connection()
        try:
            student = connection.execute(
                "SELECT id, password FROM students WHERE matric_number = ?", (matric,)
            ).fetchone()
        finally:
            connection.close()
        if student and check_password_hash(student["password"], password):
            session.clear()
            session.permanent = True
            session["student_id"] = student["id"]
            return redirect(url_for("dashboard"))
        flash("Invalid matric number or password.")
        return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/student/<name>")
def student(name):
    return f"Welcome, {name}!"

@app.route("/dashboard")
@student_required
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
              COUNT(*)  AS total_questions
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
@student_required
def start_exam():

    session["selected_course"] = request.form["course"]
    try:
        exam_size = int(request.form.get("exam_size", ""))
    except (ValueError, TypeError):
        abort(400)
    if exam_size < 1:
        abort(400)
    session["exam_size"] = exam_size

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

    session["exam_start_time"] = int(time.time())
    session["exam_duration"] = 20 * 60   # 20 minutes
    

    return redirect(url_for("exam"))

@app.route("/next")
@active_exam_required
def next_question():

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT COUNT(*) FROM questions
    WHERE course = ?
    """, (session["selected_course"],))

    total_questions = cursor.fetchone()[0]

    connection.close()

    if session["current_question"] < len(session["exam_questions"]) - 1:
        session["current_question"] += 1

    return redirect(url_for("exam"))

@app.route("/previous")
@active_exam_required
def previous_question():

    if session["current_question"] > 0:
        session["current_question"] -= 1

    return redirect(url_for("exam"))

@app.route("/goto_question/<int:index>")
@active_exam_required
def goto_question(index):

    total = len(session["exam_questions"])

    if 0 <= index < total:
        session["current_question"] = index

    return redirect(url_for("exam"))

@app.route("/save_answer", methods=["POST"])
@active_exam_required
def save_answer():

    question_id = request.form.get("question_id")
    answer = request.form.get("answer")

    answers = session.get("answers", {})

    answers[question_id] = answer

    session["answers"] = answers

    total_questions = len(session["exam_questions"])

    if session["current_question"] < len(session["exam_questions"]) - 1:
        session["current_question"] += 1

        return redirect(url_for("exam"))

    return redirect(url_for("submit_exam"))

@app.route("/submit_exam")
@active_exam_required
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

    total_questions = len(session["exam_questions"])

    connection.close()

    return render_template(
        "result.html",
        score=score,
        total=total_questions
    )



@app.route("/exam")
@active_exam_required
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
    
    if not questions:
        connection.close()
        flash("This exam is no longer available.")
        return redirect(url_for("dashboard"))
    session["current_question"] = min(max(session["current_question"], 0), len(questions) - 1)
    question = questions[session["current_question"]]

    connection.close()

    current_time = int(time.time())

    elapsed_time = current_time - session["exam_start_time"]

    remaining_time = session["exam_duration"] - elapsed_time

    if remaining_time <= 0:
       return redirect(url_for("submit_exam"))
    
    total = len(session["exam_questions"])
    question_ids = session["exam_questions"]
    question_ids=question_ids

    answered = len(session.get("answers", {}))

    unanswered = total - answered

    return render_template(
    "exam.html",
    question=question,
    current=session["current_question"] + 1,
    total=len(questions),
    is_last=(session["current_question"] == len(questions) - 1),
    selected_answer=session.get("answers", {}).get(str(question["id"])),
    remaining_time=remaining_time,
    question_numbers=range(total),
    # question_numbers=range(total),
    question_ids=question_ids,
    unanswered=unanswered
)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        connection = get_db_connection()
        try:
            admin = connection.execute(
                "SELECT id, password FROM admins WHERE username = ?", (username,)
            ).fetchone()
        finally:
            connection.close()
        if admin and check_password_hash(admin["password"], password):
            session.clear()
            session.permanent = True
            session["admin_id"] = admin["id"]
            return redirect(url_for("admin_dashboard"))
        flash("Invalid username or password.")
    return render_template("admin_login.html")


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) AS total FROM students")
    total_students = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM questions")
    total_questions = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(DISTINCT course) AS total
        FROM questions
    """)
    total_courses = cursor.fetchone()["total"]

    # We'll create this table later
    total_results = 0

    connection.close()

    return render_template(
        "admin_dashboard.html",
        total_students=total_students,
        total_questions=total_questions,
        total_courses=total_courses,
        total_results=total_results
    )


@app.route("/admin/questions")
@admin_required
def admin_questions():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM questions
        ORDER BY course, year
    """)

    questions = cursor.fetchall()

    connection.close()

    return render_template(
        "admin_questions.html",
        questions=questions
    )

@app.route("/admin/questions/delete/<int:question_id>", methods=["POST"])
@admin_required
def delete_question(question_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM questions WHERE id = ?",
        (question_id,)
    )

    connection.commit()
    connection.close()

    flash("Question deleted successfully.")

    return redirect(url_for("admin_questions"))


@app.route("/admin/questions/add", methods=["GET", "POST"])
@admin_required
def add_question():

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    if request.method == "POST":

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO questions(
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
            request.form["course"],
            request.form["year"],
            request.form["question"],
            request.form["option_a"],
            request.form["option_b"],
            request.form["option_c"],
            request.form["option_d"],
            request.form["correct_answer"]
        ))

        connection.commit()
        connection.close()

        flash("Question added successfully!")

        return redirect(url_for("admin_questions"))

    return render_template(
    "question_form.html",
    question=None
    )

@app.route("/admin/questions/edit/<int:question_id>", methods=["GET", "POST"])
@admin_required
def edit_question(question_id):

    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == "POST":

        cursor.execute("""
            UPDATE questions
            SET
                course=?,
                year=?,
                question=?,
                option_a=?,
                option_b=?,
                option_c=?,
                option_d=?,
                correct_answer=?
            WHERE id=?
        """, (

            request.form["course"],
            request.form["year"],
            request.form["question"],
            request.form["option_a"],
            request.form["option_b"],
            request.form["option_c"],
            request.form["option_d"],
            request.form["correct_answer"],
            question_id

        ))

        connection.commit()
        connection.close()

        flash("Question updated successfully!")

        return redirect(url_for("admin_questions"))

    cursor.execute(
        "SELECT * FROM questions WHERE id=?",
        (question_id,)
    )

    question = cursor.fetchone()

    connection.close()

    return render_template(
        "question_form.html",
        question=question
    )

@app.route("/logout")
def logout():
    session.clear()
    flash("logout successful.")
    return redirect(url_for("login"))
    


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
