from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import sqlite3
from werkzeug.security import check_password_hash
import database
from datetime import datetime
from werkzeug.security import generate_password_hash
import requests # Make sure to pip install requests
import json

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
        # .strip() removes accidental spaces at the start or end
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        print(f"Login Attempt: User='{username}' Pass='{password}'") # Debugging

        conn = get_db()
        # Use COLLATE NOCASE to ignore Capitalization differences
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? COLLATE NOCASE",
            (username,)
        ).fetchone()
        conn.close()

        if user:
            # check_password_hash compares the plain text password to the hashed one
            if check_password_hash(user["password"], password):

                session["user_id"] = user["id"]
                session["role"] = user["role"]
                session["linked_student_id"] = user["linked_student_id"]

                if user["role"] == "nurse":
                    return redirect(url_for("nurse_dashboard"))

                elif user["role"] == "student":
                    return redirect(url_for("student_dashboard"))

            else:
                print("Password mismatch")
                return "Invalid password (Make sure it is your Student Number)"
        else:
            print(f"User '{username}' not found in database")
            return "Invalid username (Make sure it is your exact Full Name)"

    return render_template("login.html")


# ================= NURSE DASHBOARD =================
# ================= NURSE - HOME (GRAPHS) =================
@app.route("/nurse_dashboard")
def nurse_dashboard():
    if session.get("role") != "nurse":
        return redirect(url_for("login"))
    
    conn = get_db()
    
    # 1. Visitation per Day (Last 7 Days)
    visits_per_day = conn.execute("""
        SELECT date(time_in) as date, COUNT(*) as count 
        FROM clinic_visits 
        GROUP BY date(time_in) 
        ORDER BY date DESC LIMIT 7
    """).fetchall()
    
    # 2. Visits per Grade Level
    visits_per_grade = conn.execute("""
        SELECT students.grade, COUNT(*) as count 
        FROM clinic_visits 
        JOIN students ON clinic_visits.student_id = students.id 
        GROUP BY students.grade
    """).fetchall()

    # Statistics for the cards
    today = datetime.now().strftime("%Y-%m-%d")
    total_students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    total_visits_today = conn.execute("SELECT COUNT(*) FROM clinic_visits WHERE time_in LIKE ?", (f"{today}%",)).fetchone()[0]
    students_with_allergies = conn.execute("SELECT COUNT(*) FROM students WHERE allergies != '' AND allergies IS NOT NULL").fetchone()[0]
    students_with_medical_conditions = conn.execute("SELECT COUNT(*) FROM students WHERE medical_condition != '' AND medical_condition IS NOT NULL").fetchone()[0]
    
    nurse_id = session.get("user_id")
    nurse = conn.execute("SELECT * FROM nurses WHERE id=?", (nurse_id,)).fetchone()
    conn.close()

    return render_template(
        "nurse_dashboard.html",
        nurse=nurse,
        total_students=total_students,
        total_visits_today=total_visits_today,
        students_with_allergies=students_with_allergies,
        students_with_medical_conditions=students_with_medical_conditions,
        graph_days=[row['date'] for row in visits_per_day],
        graph_day_counts=[row['count'] for row in visits_per_day],
        graph_grades=[row['grade'] for row in visits_per_grade],
        graph_grade_counts=[row['count'] for row in visits_per_grade]
    )

# ================= MANAGE STUDENTS =================
@app.route("/manage_students")
def manage_students():
    if session.get("role") != "nurse":
        return redirect(url_for("login"))
    conn = get_db()
    students = conn.execute("SELECT id, student_number, full_name, section, grade, rfid_uid FROM students").fetchall()
    nurse_id = session.get("user_id")
    nurse = conn.execute("SELECT * FROM nurses WHERE id=?", (nurse_id,)).fetchone()
    conn.close()
    return render_template("manage_students.html", students=students, nurse=nurse)

@app.route("/delete_students", methods=["POST"])
def delete_students():
    student_ids = request.json.get('ids', [])
    conn = get_db()
    for s_id in student_ids:
        conn.execute("DELETE FROM students WHERE id = ?", (s_id,))
        conn.execute("DELETE FROM users WHERE linked_student_id = ?", (s_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/bulk_import_students", methods=["POST"])
def bulk_import_students():
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "No data received"}), 400
        
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        for row in data:
            # CLEANING DATA: Force strings and remove decimals from numbers
            std_num = str(row.get('student_number', '')).split('.')[0].strip()
            full_name = str(row.get('full_name', '')).strip()
            rfid = str(row.get('rfid_uid', '')).strip()

            # 1. RETAIN ORIGINAL STUDENT IMPORT CODE
            cursor.execute("""
                INSERT OR REPLACE INTO students 
                (rfid_uid, student_number, full_name, address, age, grade, section, 
                 allergies, medical_condition, parent_name, parent_contact_number, parent_email)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rfid, std_num, full_name,
                row.get('address'), row.get('age'), row.get('grade'), row.get('section'),
                row.get('allergies'), row.get('medical_condition'), row.get('parent_name'),
                row.get('parent_contact_number'), row.get('parent_email')
            ))

            # 2. ADD CREDENTIAL FUNCTION (Automated User Creation)
            # Fetch the ID of the student we just inserted/updated
            cursor.execute("SELECT id FROM students WHERE student_number = ?", (std_num,))
            student_res = cursor.fetchone()
            
            if student_res:
                student_id = student_res['id']
                # Password is clean student number string, hashed
                hashed_pass = generate_password_hash(std_num)
                
                # Insert user with 'student' role
                cursor.execute("""
                    INSERT OR REPLACE INTO users (username, password, role, linked_student_id)
                    VALUES (?, ?, ?, ?)
                """, (full_name, hashed_pass, 'student', student_id))

        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        conn.rollback()
        print(f"Import Error: {e}") # This shows in your terminal
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()



@app.route("/save_student", methods=["POST"])
def save_student():
    if session.get("role") != "nurse":
        return redirect(url_for("login"))

    # 1. Collect Form Data
    s_id = request.form.get("id")
    rfid = request.form.get("rfid_uid")
    s_num = request.form.get("student_number").strip()
    name = request.form.get("full_name").strip()
    
    # 2. Database Operation
    conn = get_db()
    cursor = conn.cursor()

    try:
        if s_id:  # --- EDIT EXISTING STUDENT ---
            cursor.execute("""
                UPDATE students SET 
                rfid_uid=?, student_number=?, full_name=?, address=?, age=?, 
                grade=?, section=?, allergies=?, medical_condition=?, 
                parent_name=?, parent_contact_number=?, parent_email=?
                WHERE id=?
            """, (rfid, s_num, name, request.form.get("address"), request.form.get("age"), 
                  request.form.get("grade"), request.form.get("section"), 
                  request.form.get("allergies"), request.form.get("medical_condition"), 
                  request.form.get("parent_name"), request.form.get("parent_contact_number"), 
                  request.form.get("parent_email"), s_id))
            
            # Update credentials username if the name changed
            cursor.execute("UPDATE users SET username=? WHERE linked_student_id=?", (name, s_id))
            
        else:  # --- REGISTER NEW STUDENT ---
            cursor.execute("""
                INSERT INTO students 
                (rfid_uid, student_number, full_name, address, age, grade, section, 
                 allergies, medical_condition, parent_name, parent_contact_number, parent_email)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (rfid, s_num, name, request.form.get("address"), request.form.get("age"), 
                  request.form.get("grade"), request.form.get("section"), 
                  request.form.get("allergies"), request.form.get("medical_condition"), 
                  request.form.get("parent_name"), request.form.get("parent_contact_number"), 
                  request.form.get("parent_email")))
            
            new_student_id = cursor.lastrowid
            
            # --- AUTO-CREATE CREDENTIALS ---
            # Username = Full Name, Password = Student Number (hashed)
            hashed_password = generate_password_hash(s_num)
            cursor.execute("""
                INSERT INTO users (username, password, role, linked_student_id)
                VALUES (?, ?, ?, ?)
            """, (name, hashed_password, 'student', new_student_id))

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error saving student: {e}")
    finally:
        conn.close()

    return redirect(url_for("manage_students"))

# ================= VISIT HISTORY =================
@app.route("/visit_history")
def visit_history():
    if session.get("role") != "nurse":
        return redirect(url_for("login"))
    
    conn = get_db()
    visits = conn.execute("""
        SELECT clinic_visits.*, students.full_name, students.student_number, nurses.full_name as nurse_name 
        FROM clinic_visits 
        JOIN students ON clinic_visits.student_id = students.id
        LEFT JOIN nurses ON clinic_visits.nurse_id = nurses.id
        ORDER BY time_in DESC
    """).fetchall()
    
    nurse_id = session.get("user_id")
    nurse = conn.execute("SELECT * FROM nurses WHERE id=?", (nurse_id,)).fetchone()
    conn.close()
    
    return render_template("visit_history.html", visits=visits, nurse=nurse)

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
    # Joined with nurses table to show who encoded the record
    visits = conn.execute("""
        SELECT clinic_visits.*, nurses.full_name as nurse_name 
        FROM clinic_visits 
        LEFT JOIN nurses ON clinic_visits.nurse_id = nurses.id 
        WHERE student_id=? ORDER BY time_in DESC
    """, (student_id,)).fetchall()
    conn.close()

    return {
        "id": student["id"],
        "full_name": student["full_name"],
        "student_number": student["student_number"],
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

# Search by RFID for the scanner
@app.route("/get_student_by_rfid/<rfid_uid>")
def get_student_by_rfid(rfid_uid):
    conn = get_db()
    student = conn.execute("SELECT * FROM students WHERE rfid_uid=?", (rfid_uid,)).fetchone()
    if student:
        conn.close()
        return get_student_info(student["id"])
    conn.close()
    return {"error": "RFID not found"}, 404

# NEW: Search by Student Number
@app.route("/get_student_by_number/<student_num>")
def get_student_by_number(student_num):
    conn = get_db()
    student = conn.execute("SELECT * FROM students WHERE student_number=?", (student_num,)).fetchone()
    if student:
        conn.close()
        return get_student_info(student["id"])
    conn.close()
    return {"error": "Student Number not found"}, 404


# ================= EMAIL SENDER FUNCTION =================
def send_clinic_email(visit_id):
    conn = get_db()
    query = """
        SELECT 
            s.parent_name, s.parent_email, s.full_name, s.student_number,
            v.time_in, v.temperature, v.complaint, v.medicine, v.diagnosis,
            n.full_name AS nurse_name
        FROM clinic_visits v
        JOIN students s ON v.student_id = s.id
        JOIN nurses n ON v.nurse_id = n.id
        WHERE v.id = ?
    """
    row = conn.execute(query, (visit_id,)).fetchone()
    conn.close()

    if not row:
        print(f"DEBUG: No visit found for ID {visit_id}")
        return False

    url = "https://api.emailjs.com/api/v1.0/email/send"
    
    payload = {
        'service_id': 'service_lqw2xin',
        'template_id': 'template_gex6jti',
        'user_id': 'Yxm_edy2UUe3pY067',
        'accessToken': 'WMmWiAgOH83IFkhXCN2iE',  # <--- ADD THIS LINE
        'template_params': {
            'parent_email': row['parent_email'],
            'parent_name': row['parent_name'],
            'full_name': row['full_name'],
            'student_number': row['student_number'],
            'time_in': row['time_in'],
            'temperature': row['temperature'],
            'complaint': row['complaint'],
            'medicine': row['medicine'],
            'diagnosis': row['diagnosis'],
            'nurse_name': row['nurse_name']
        }
    }

    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            print("DEBUG: Email sent successfully!")
            return True
        else:
            print(f"DEBUG: EmailJS Error: {response.text}")
            return False
    except Exception as e:
        print(f"DEBUG: Connection Error: {e}")
        return False

# ================= UPDATED ADD VISIT ROUTE =================
@app.route("/add_visit", methods=["POST"])
def add_visit():
    if session.get("role") != "nurse":
        return redirect(url_for("login"))

    student_id = request.form["student_id"]
    temperature = request.form["temperature"]
    complaint = request.form["complaint"]
    diagnosis = request.form["diagnosis"]
    medicine = request.form["medicine"]
    nurse_id = session.get("user_id")
    time_in = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO clinic_visits
        (student_id, nurse_id, temperature, complaint, diagnosis, medicine, time_in)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (student_id, nurse_id, temperature, complaint, diagnosis, medicine, time_in))
    
    # Capture the ID of the visit we just saved
    new_visit_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Trigger the Email sending
    if new_visit_id:
        send_clinic_email(new_visit_id)

    return redirect(url_for("nurse_dashboard"))


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)