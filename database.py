import sqlite3
from werkzeug.security import generate_password_hash

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
    CREATE TABLE IF NOT EXISTS visits (
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

    # ================= INSERT SAMPLE STUDENT =================
    cursor.execute("""
    INSERT OR IGNORE INTO students
    (id, student_number, full_name, address, age, grade, section,
     allergies, medical_condition, parent_name,
     parent_contact_number, parent_email)
    VALUES
    (1, '2024-0001', 'Juan Dela Cruz',
     'Laguna, Philippines',
     18, 'Grade 12', 'STEM-A',
     'Peanuts',
     'Asthma',
     'Maria Dela Cruz',
     '09123456789',
     'maria@gmail.com')
    """)

    # ================= CREATE STUDENT LOGIN =================
    # Username = fullname without space, lowercase
    username = "juandelacruz"
    password = generate_password_hash("2024-0001")

    cursor.execute("""
    INSERT OR IGNORE INTO users
    (id, username, password, role, linked_student_id)
    VALUES
    (2, ?, ?, 'student', 1)
    """, (username, password))

    # ================= CREATE NURSE ACCOUNT =================
    cursor.execute("""
    INSERT OR IGNORE INTO users
    (id, username, password, role, linked_student_id)
    VALUES
    (1, 'nurse1', ?, 'nurse', NULL)
    """, (generate_password_hash("nurse123"),))

    conn.commit()
    conn.close()

    print("Database created successfully.")


if __name__ == "__main__":
    create_database()