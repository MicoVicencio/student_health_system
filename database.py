import sqlite3
from werkzeug.security import generate_password_hash

DB_NAME = "clinic.db"

def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. CREATE TABLES (Only if they don't exist)
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT, linked_student_id INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, rfid_uid TEXT UNIQUE, student_number TEXT UNIQUE, full_name TEXT, address TEXT, age INTEGER, grade TEXT, section TEXT, allergies TEXT, medical_condition TEXT, parent_name TEXT, parent_contact_number TEXT, parent_email TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS clinic_visits (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, nurse_id INTEGER, temperature REAL, complaint TEXT, diagnosis TEXT, medicine TEXT, time_in TEXT, FOREIGN KEY(student_id) REFERENCES students(id), FOREIGN KEY(nurse_id) REFERENCES nurses(id))")
    cursor.execute("CREATE TABLE IF NOT EXISTS nurses (id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT, address TEXT, contact_number TEXT, username TEXT UNIQUE, password TEXT)")

    # 2. SETUP NURSE (Using OR IGNORE so it never overwrites existing data)
    cursor.execute("""
        INSERT OR IGNORE INTO nurses (id, full_name, username) 
        VALUES (2, 'Bonnie Bennett', 'nurse_bonnie')
    """)
    
    # Only add the nurse to users if they aren't already there
    cursor.execute("SELECT id FROM users WHERE username='nurse_bonnie'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO users (id, username, password, role, linked_student_id) 
            VALUES (2, 'nurse_bonnie', ?, 'nurse', NULL)
        """, (generate_password_hash("nurse123"),))

    conn.commit()
    conn.close()
    print("Database is ready and persistent. No data was deleted.")

if __name__ == "__main__":
    create_database()