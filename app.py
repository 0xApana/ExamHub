from flask import Flask, render_template,request, redirect, url_for,  flash, session

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

        if matric == "2024/1/95339CP" and password == "12345":

            session["student"] = matric

            return redirect(url_for("dashboard"))
        else:

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
