from flask import render_template, request, flash, redirect, url_for, session
from flask import send_file
import os

from app.quiz_questions import QUIZ_QUESTIONS


from datetime import datetime
import uuid
import os
from werkzeug.security import generate_password_hash, check_password_hash
from database.database import (
    add_student,
    get_student_by_email,
    get_student_by_phone,
    save_quiz_result,
    get_leaderboard,
    get_student_rank
)

from app import app
from database.database import (
    add_student,
    get_student_by_email,
    get_student_by_phone,
    save_quiz_result,
    get_leaderboard
)



# Home Page
@app.route("/")
def home():
    return render_template("index.html")


# ============================
# Notes Section
# ============================


# Notes -> Branch Selection
@app.route("/notes")
def notes():
    return render_template("branches.html")



# Branch -> Semester Selection
@app.route("/notes/<branch>")
def semesters(branch):

    return render_template(
        "semester.html",
        branch=branch
    )



# Semester -> Subject Selection
@app.route("/notes/<branch>/<semester>")
def subject_notes(branch, semester):

    return render_template(
        "subject_notes.html",
        branch=branch,
        semester=semester
    )




# Previous Papers
@app.route("/paper_branches")
def paper_branches():
    return render_template("paper_branches.html")


@app.route("/papers/<branch>")
def papers(branch):
    return render_template(
        "papers.html",
        branch=branch
    )


# Quiz
@app.route("/quiz")
def quiz():
    return render_template("quiz.html")
# CME Quiz Selection
@app.route("/cme-quiz")
def cme_quiz():

    return render_template(
        "cme_quiz.html"
    )

@app.route("/quiz/<branch>")
def start_quiz(branch):

    if branch not in QUIZ_QUESTIONS:
        flash("Quiz for this branch will be added soon.", "info")
        return redirect(url_for("quiz"))

    questions = QUIZ_QUESTIONS[branch]

    return render_template(
        "quiz_questions.html",
        branch=branch,
        questions=questions
    )
@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():

    branch = request.form["branch"]
    questions = QUIZ_QUESTIONS[branch]

    score = 0

    for i in range(len(questions)):
        selected = request.form.get(f"q{i+1}")

        if selected == questions[i]["answer"]:
            score += 1

    email = session["student_email"]

    save_quiz_result(
        email,
        branch,
        score
    )

    # Calculate percentage
    percentage = (score / len(questions)) * 100

    # Save quiz details in session
    session["quiz_score"] = score
    session["quiz_total"] = len(questions)
    session["quiz_percentage"] = round(
        percentage,
        2
    )
    session["quiz_branch"] = branch

    # Get student's rank
    rank = get_student_rank(
        session["student_email"]
    )

    return render_template(
        "quiz_result.html",
        score=score,
        total=len(questions),
        percentage=round(percentage, 2),
        rank=rank
    )
    # Leaderboard
# ==========================
@app.route("/leaderboard")
def leaderboard():

    students = get_leaderboard()

    print([dict(x) for x in students])

    return render_template(
        "leaderboard.html",
        students=students
    )
# Results
@app.route("/results")
def results():
    return render_template("results.html")


# Contact
@app.route("/contact")
def contact():
    return render_template("contact.html")


# Admin
@app.route("/admin")
def admin():
    return render_template("admin.html")

def add_background(canvas, doc):

    bg_path = os.path.join(
        app.root_path,
        "..",
        "static",
        "images",
        "certi.png"
    )

    bg_path = os.path.abspath(bg_path)

    print(bg_path)
    print(os.path.exists(bg_path))

    if os.path.exists(bg_path):
        canvas.drawImage(
            bg_path,
            0,
            0,
            width=595,
            height=842
        )

# Register
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        # Check if email or phone already exists
        student = get_student_by_email(email)
        phone_student = get_student_by_phone(phone)

        if student:
            flash("Email already registered!", "error")
            return redirect(url_for("register"))

        if phone_student:
            flash("Phone number already registered!", "error")
            return redirect(url_for("register"))

        # Save student
        add_student(name, email, phone, hashed_password)

        flash("Registration Successful!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        student = get_student_by_email(email)

        if student and check_password_hash(
                student["password"], password):

            session["student_name"] = student["name"]
            session["student_email"] = student["email"]
            session["student_phone"] = student["phone"]

            flash("Login Successful!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password!", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


# Dashboard
@app.route("/dashboard")
def dashboard():

    if "student_name" not in session:
        return redirect(url_for("login"))


    return render_template(
        "dashboard.html",
        username=session["student_name"]
    )

@app.route('/pdf/<path:pdf_path>')
def view_pdf(pdf_path):
    return render_template(
        'pdf_viewer.html',
        pdf_path=pdf_path
    )


# Logout
@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully!", "success")

    return redirect(url_for("login"))
