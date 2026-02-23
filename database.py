import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

DB_NAME = "clinic.db"

def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        linked_student_id INTEGER
    )
    """)

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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clinic_visits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        nurse_id INTEGER,
        temperature REAL,
        complaint TEXT,
        diagnosis TEXT,
        medicine TEXT,
        time_in TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id),
        FOREIGN KEY(nurse_id) REFERENCES nurses(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nurses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        address TEXT,
        contact_number TEXT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # --- New Sample Data ---

    # Damon Salvatore - HUMSS-B
    cursor.execute("INSERT OR IGNORE INTO students (id, rfid_uid, student_number, full_name, address, age, grade, section, allergies, medical_condition, parent_name, parent_contact_number, parent_email) VALUES (2, 'RFID222', '2024-0002', 'Damon Salvatore', 'Mystic Falls', 18, 'Grade 12', 'HUMSS-B', 'None', 'None', 'Giuseppe Salvatore', '09112223334', 'damon@salvatore.com')")
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role, linked_student_id) VALUES ('damons', ?, 'student', 2)", (generate_password_hash("password123"),))

    # Elena Gilbert - STEM-B
    cursor.execute("INSERT OR IGNORE INTO students (id, rfid_uid, student_number, full_name, address, age, grade, section, allergies, medical_condition, parent_name, parent_contact_number, parent_email) VALUES (3, 'RFID333', '2024-0003', 'Elena Gilbert', 'Gilbert House', 17, 'Grade 11', 'STEM-B', 'None', 'None', 'Miranda Gilbert', '09998887776', 'elena@gilbert.com')")
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role, linked_student_id) VALUES ('elenag', ?, 'student', 3)", (generate_password_hash("password123"),))

    # Nurse Bonnie Bennett
    # Use ID 2 for BOTH tables so they link correctly
    cursor.execute("INSERT OR IGNORE INTO nurses (id, full_name, username) VALUES (2, 'Bonnie Bennett', 'nurse_bonnie')")
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password, role) VALUES (2, 'nurse_bonnie', ?, 'nurse')", (generate_password_hash("nurse123"),))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()