from flask import Flask, render_template,request, redirect, url_for,  flash, session
from database import get_db_connection

app= Flask(__name__)
app.secret_key = "examhub_secret_key"

@app.route("/")
def Home():
    return render_template("index.html")

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
            session["student"] = student["full_name"]
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
    
    if "student" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))
    
    return f"Welcome {session['student']}!"

@app.route("/logout")
def logout():
    session.pop("student",None)
    flash("logout successful.")
    return redirect(url_for("login"))
    


if __name__ == "__main__":
    app.run(debug=True)
