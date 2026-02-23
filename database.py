import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

DB_NAME = "clinic.db"

def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # ================= USERS TABLE =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        linked_student_id INTEGER
    )
    """)

    # ================= STUDENTS TABLE =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rfid_uid TEXT UNIQUE,
        student_number TEXT UNIQUE,
        full_name TEXT,
        address TEXT,
        age INTEGER,
        grade TEXT,
        section TEXT,
        allergies TEXT,
        medical_condition TEXT,
        parent_name TEXT,
        parent_contact_number TEXT,
        parent_email TEXT
    )
    """)

    # ================= VISITS TABLE =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clinic_visits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        temperature REAL,
        complaint TEXT,
        diagnosis TEXT,
        medicine TEXT,
        time_in TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id)
    )
    """)

    # ================= SAMPLE STUDENT =================
    cursor.execute("""
    INSERT OR IGNORE INTO students
    (id, rfid_uid, student_number, full_name, address, age, grade, section,
     allergies, medical_condition, parent_name,
     parent_contact_number, parent_email)
    VALUES
    (1, 'RFID123456', '2024-0001', 'Juan Dela Cruz',
     'Laguna, Philippines',
     18, 'Grade 12', 'STEM-A',
     'Peanuts',
     'Asthma',
     'Maria Dela Cruz',
     '09123456789',
     'maria@gmail.com')
    """)

    # ================= STUDENT LOGIN =================
    username = "juandelacruz"
    password = generate_password_hash("2024-0001")

    cursor.execute("""
    INSERT OR IGNORE INTO users
    (id, username, password, role, linked_student_id)
    VALUES
    (2, ?, ?, 'student', 1)
    """, (username, password))

    # ================= NURSE LOGIN =================
    cursor.execute("""
    INSERT OR IGNORE INTO users
    (id, username, password, role, linked_student_id)
    VALUES
    (1, 'nurse1', ?, 'nurse', NULL)
    """, (generate_password_hash("nurse123"),))

    # ================= DUMMY CLINIC VISITS =================
    # Generate 3 sample visits for Juan Dela Cruz
    visits = [
        (1, 37.2, "Headache and mild fever", "Common Cold", "Paracetamol", (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")),
        (1, 36.8, "Asthma attack during PE class", "Asthma", "Inhaler", (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")),
        (1, 37.5, "Allergic reaction to peanuts", "Allergy", "Antihistamine", (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"))
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO clinic_visits
    (student_id, temperature, complaint, diagnosis, medicine, time_in)
    VALUES (?, ?, ?, ?, ?, ?)
    """, visits)

    conn.commit()
    conn.close()
    print("Database updated successfully with RFID field and dummy visits.")

if __name__ == "__main__":
    create_database()