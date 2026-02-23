import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

DB_NAME = "clinic.db"

def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. TABLE CREATION
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

    # 2. INSERT SAMPLE DATA
    # Using REPLACE ensures that if the ID exists, it updates with the correct password/role
    
    # Stefan Salvatore - STEM-A
    cursor.execute("REPLACE INTO students (id, rfid_uid, student_number, full_name, address, age, grade, section, allergies, medical_condition, parent_name, parent_contact_number, parent_email) VALUES (4, 'RFID444', '2024-0004', 'Stefan Salvatore', 'Mystic Falls', 17, 'Grade 11', 'STEM-A', 'None', 'None', 'Giuseppe Salvatore', '09112223334', 'stefan@salvatore.com')")
    cursor.execute("REPLACE INTO users (id, username, password, role, linked_student_id) VALUES (4, 'stefans', ?, 'student', 4)", (generate_password_hash("password123"),))

    # Klaus Mikaelson - ABM-C
    cursor.execute("REPLACE INTO students (id, rfid_uid, student_number, full_name, address, age, grade, section, allergies, medical_condition, parent_name, parent_contact_number, parent_email) VALUES (5, 'RFID555', '2024-0005', 'Klaus Mikaelson', 'New Orleans', 19, 'Grade 12', 'ABM-C', 'Silver', 'None', 'Mikael Mikaelson', '09119998887', 'klaus@mikaelson.com')")
    cursor.execute("REPLACE INTO users (id, username, password, role, linked_student_id) VALUES (5, 'klausm', ?, 'student', 5)", (generate_password_hash("password123"),))

    # Nurse Bonnie Bennett (Login: nurse_bonnie / nurse123)
    # Forced ID 2 for both to ensure session['user_id'] works
    cursor.execute("REPLACE INTO nurses (id, full_name, username) VALUES (2, 'Bonnie Bennett', 'nurse_bonnie')")
    cursor.execute("REPLACE INTO users (id, username, password, role, linked_student_id) VALUES (2, 'nurse_bonnie', ?, 'nurse', NULL)", (generate_password_hash("nurse123"),))

    conn.commit()
    conn.close()
    print("Database updated successfully.")

if __name__ == "__main__":
    create_database()