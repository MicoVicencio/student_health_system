import sqlite3
import random
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

DB_NAME = "clinic.db"

def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. TABLE CREATION
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT, linked_student_id INTEGER)")
    cursor.execute("CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, rfid_uid TEXT UNIQUE, student_number TEXT UNIQUE, full_name TEXT, address TEXT, age INTEGER, grade TEXT, section TEXT, allergies TEXT, medical_condition TEXT, parent_name TEXT, parent_contact_number TEXT, parent_email TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS clinic_visits (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, nurse_id INTEGER, temperature REAL, complaint TEXT, diagnosis TEXT, medicine TEXT, time_in TEXT, FOREIGN KEY(student_id) REFERENCES students(id), FOREIGN KEY(nurse_id) REFERENCES nurses(id))")
    cursor.execute("CREATE TABLE IF NOT EXISTS nurses (id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT, address TEXT, contact_number TEXT, username TEXT UNIQUE, password TEXT)")

    # 2. SETUP NURSE
    cursor.execute("REPLACE INTO nurses (id, full_name, username) VALUES (2, 'Bonnie Bennett', 'nurse_bonnie')")
    cursor.execute("REPLACE INTO users (id, username, password, role, linked_student_id) VALUES (2, 'nurse_bonnie', ?, 'nurse', NULL)", (generate_password_hash("nurse123"),))

    # 3. GENERATE 20 DUMMY STUDENTS (To populate Grades 1-12)
    grades = [f"Grade {i}" for i in range(1, 13)]
    complaints = ["Headache", "Fever", "Stomach Ache", "Cough", "Dizziness", "Sprain", "Toothache", "Allergy"]
    medicines = ["Paracetamol", "Bioflu", "Kremil-S", "Cetirizine", "Ibuprofen", "None", "Amoxicillin"]
    
    # Clear existing students and visits for a clean test
    cursor.execute("DELETE FROM students")
    cursor.execute("DELETE FROM users WHERE role='student'")
    cursor.execute("DELETE FROM clinic_visits")

    student_ids = []
    for i in range(1, 21):
        std_num = f"2026-{1000 + i}"
        full_name = f"Student Name {i}"
        grade = random.choice(grades)
        
        cursor.execute("""
            INSERT INTO students (student_number, rfid_uid, full_name, grade, section)
            VALUES (?, ?, ?, ?, ?)
        """, (std_num, f"RFID_TAG_{i}", full_name, grade, "Section-A"))
        
        student_id = cursor.lastrowid
        student_ids.append(student_id)
        
        # Create user account for the student
        cursor.execute("""
            INSERT INTO users (username, password, role, linked_student_id)
            VALUES (?, ?, ?, ?)
        """, (full_name, generate_password_hash(std_num), 'student', student_id))

    # 4. GENERATE 100 VISITS (Jan 10, 2026 - Present)
    start_date = datetime(2026, 1, 10)
    end_date = datetime.now()
    delta_days = (end_date - start_date).days

    for _ in range(100):
        random_days = random.randint(0, delta_days)
        random_hour = random.randint(7, 16) # School hours 7am - 4pm
        random_minute = random.randint(0, 59)
        
        visit_time = (start_date + timedelta(days=random_days)).replace(hour=random_hour, minute=random_minute)
        visit_str = visit_time.strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT INTO clinic_visits (student_id, nurse_id, temperature, complaint, diagnosis, medicine, time_in)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            random.choice(student_ids),
            2, # Nurse Bonnie
            round(random.uniform(36.2, 39.5), 1),
            random.choice(complaints),
            "General Consultation",
            random.choice(medicines),
            visit_str
        ))

    conn.commit()
    conn.close()
    print("Successfully generated 20 students and 100 clinic visit records.")

if __name__ == "__main__":
    create_database()