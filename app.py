from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from werkzeug.security import check_password_hash
import database

app = Flask(__name__)
app.secret_key = "clinic_secret_key"

# Create DB automatically
database.create_database()

# ================= DATABASE CONNECTION =================
def get_db():
    conn = sqlite3.connect("clinic.db")
    conn.row_factory = sqlite3.Row
    return conn


# ================= LOGIN =================
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["role"] = user["role"]
            session["linked_student_id"] = user["linked_student_id"]

            if user["role"] == "nurse":
                return redirect(url_for("nurse_dashboard"))

            elif user["role"] == "student":
                return redirect(url_for("student_dashboard"))

        else:
            return "Invalid username or password"

    return render_template("login.html")


# ================= NURSE DASHBOARD =================
@app.route("/nurse_dashboard")
def nurse_dashboard():

    if session.get("role") != "nurse":
        return redirect(url_for("login"))

    conn = get_db()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()

    return f"""
    <h2>Nurse Dashboard</h2>
    <p>Total Students: {len(students)}</p>
    <a href='/logout'>Logout</a>
    """


# ================= STUDENT DASHBOARD =================
@app.route("/student_dashboard")
def student_dashboard():

    if session.get("role") != "student":
        return redirect(url_for("login"))

    student_id = session.get("linked_student_id")

    conn = get_db()
    student = conn.execute(
        "SELECT * FROM students WHERE id=?",
        (student_id,)
    ).fetchone()
    conn.close()

    return f"""
    <h2>Student Dashboard</h2>
    <p><strong>Full Name:</strong> {student['full_name']}</p>
    <p><strong>Student Number:</strong> {student['student_number']}</p>
    <p><strong>Grade:</strong> {student['grade']} - {student['section']}</p>
    <p><strong>Allergies:</strong> {student['allergies']}</p>
    <p><strong>Medical Condition:</strong> {student['medical_condition']}</p>
    <a href='/logout'>Logout</a>
    """


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)