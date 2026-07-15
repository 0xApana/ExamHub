from flask import Flask, render_template,request

app= Flask(__name__)
@app.route("/")
def Home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        matric = request.form["matric"]
        password = request.form["password"]

        return f"Matric: {matric} <br> Password: {password}"
    return render_template("login.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/student/<name>")
def student(name):
    return f"Welcome, {name}!"


if __name__ == "__main__":
    app.run(debug=True)
