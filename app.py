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
# ================= NURSE DASHBOARD =================
@app.route("/nurse_dashboard")
def nurse_dashboard():
    if session.get("role") != "nurse":
        return redirect(url_for("login"))

    conn = get_db()
    # Fetch all students
    students = conn.execute("SELECT * FROM students").fetchall()

    # Fetch summary stats
    total_students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    total_visits_today = conn.execute(
        "SELECT COUNT(*) FROM clinic_visits WHERE date(time_in) = date('now')"
    ).fetchone()[0]
    students_with_allergies = conn.execute(
        "SELECT COUNT(*) FROM students WHERE allergies IS NOT NULL AND allergies != ''"
    ).fetchone()[0]
    students_with_medical_conditions = conn.execute(
        "SELECT COUNT(*) FROM students WHERE medical_condition IS NOT NULL AND medical_condition != ''"
    ).fetchone()[0]
    conn.close()

    return render_template(
        "nurse_dashboard.html",
        students=students,
        total_students=total_students,
        total_visits_today=total_visits_today,
        students_with_allergies=students_with_allergies,
        students_with_medical_conditions=students_with_medical_conditions
    )


# ================= STUDENT DASHBOARD =================
@app.route("/student_dashboard")
def student_dashboard():

    if session.get("role") != "student":
        return redirect(url_for("login"))

    student_id = session.get("linked_student_id")

    conn = get_db()
    # Fetch student info
    student = conn.execute(
        "SELECT * FROM students WHERE id=?",
        (student_id,)
    ).fetchone()

    # Fetch recent visits (last 10)
    visits = conn.execute(
        "SELECT * FROM clinic_visits WHERE student_id=? ORDER BY time_in DESC LIMIT 10",
        (student_id,)
    ).fetchall()
    conn.close()

    # Pass data to template
    return render_template("student_dashboard.html", student=student, visits=visits)




@app.route("/get_student_info/<int:student_id>")
def get_student_info(student_id):
    conn = get_db()
    student = conn.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()
    visits = conn.execute("SELECT * FROM clinic_visits WHERE student_id=? ORDER BY time_in DESC", (student_id,)).fetchall()
    conn.close()

    return {
        "id": student["id"],
        "full_name": student["full_name"],
        "rfid_uid": student["rfid_uid"],
        "address": student["address"],
        "age": student["age"],
        "grade": student["grade"],
        "section": student["section"],
        "allergies": student["allergies"],
        "medical_condition": student["medical_condition"],
        "parent_name": student["parent_name"],
        "parent_contact_number": student["parent_contact_number"],
        "parent_email": student["parent_email"],
        "visits": [dict(v) for v in visits]
    }













# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)